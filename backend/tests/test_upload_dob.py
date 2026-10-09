import io

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models import Student
from backend.scripts.backfill_dob import sample_dob, TEMPLATE_DOBS
from conftest import test_session as _test_db

client = TestClient(app)

EXISTING_REG = "7777000011112222"


def _seed_student(dob: str = "01/01/2000") -> None:
    existing = _test_db.query(Student).filter(Student.register_no == EXISTING_REG).first()
    if existing is None:
        existing = Student(register_no=EXISTING_REG, name="DOB Overwrite Test")
        _test_db.add(existing)
    existing.dob = dob
    _test_db.commit()


def _csv_bytes(header: str, row: str) -> bytes:
    return f"{header}\n{row}\n".encode("utf-8")


def _preview(csv_bytes: bytes):
    return client.post(
        "/api/v1/students/upload-preview",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )


def test_upload_existing_with_dob_is_valid_and_overwrites():
    _seed_student("01/01/2000")
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code,Date of Birth",
        f"{EXISTING_REG},DOB Overwrite Test,B.E. Computer Science and Engineering,5,JCS2501,15/09/2004",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["valid_count"] == 1
    assert data["duplicate_count"] == 0
    assert data["invalid_count"] == 0

    commit = client.post(
        "/api/v1/students/commit-upload",
        json={"students": data["all_valid"]},
    )
    assert commit.status_code == 200
    assert commit.json()["imported_count"] == 1

    refreshed = _test_db.query(Student).filter(Student.register_no == EXISTING_REG).first()
    _test_db.refresh(refreshed)
    assert refreshed.dob == "15/09/2004"


def test_upload_missing_dob_column_rejected():
    _seed_student("01/01/2000")
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code",
        f"{EXISTING_REG},DOB Overwrite Test,B.E. Computer Science and Engineering,5,JCS2501",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 400
    body = response.json()
    message = body.get("message") or body.get("detail") or ""
    assert "date of birth" in message.lower()


def test_upload_blank_dob_cell_is_invalid():
    _seed_student("01/01/2000")
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code,Date of Birth",
        "7777000011112223,Blank DOB Student,B.E. Computer Science and Engineering,5,JCS2501,",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["invalid_count"] == 1
    assert data["valid_count"] == 0
    assert "required" in data["invalid_rows"][0]["reason"].lower()


def test_upload_accepts_13_digit_register_with_dob():
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code,Date of Birth",
        "2403310910421,Thirteen Digit Student,B.E. Computer Science and Engineering,5,JCS2501,15/08/2005",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["valid_count"] == 1
    assert data["invalid_count"] == 0
    assert data["all_valid"][0]["register_no"] == "2403310910421"

    commit = client.post(
        "/api/v1/students/commit-upload",
        json={"students": data["all_valid"]},
    )
    assert commit.status_code == 200

    created = _test_db.query(Student).filter(Student.register_no == "2403310910421").first()
    assert created is not None
    assert created.dob == "15/08/2005"
    _test_db.delete(created)
    _test_db.commit()


def test_upload_rejects_12_digit_register():
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code,Date of Birth",
        "240331091042,Twelve Digit,B.E. Computer Science and Engineering,5,JCS2501,15/08/2005",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["invalid_count"] == 1
    assert "13 or 16" in data["invalid_rows"][0]["reason"]


def test_dob_template_download():
    response = client.get("/api/v1/students/dob-template")
    assert response.status_code == 200
    assert "dob_template.xlsx" in response.headers.get("content-disposition", "")

    import io
    import pandas as pd
    df = pd.read_excel(io.BytesIO(response.content), dtype=str)
    assert list(df.columns) == ["Register Number", "Date of Birth"]
    for dob in df["Date of Birth"]:
        assert len(str(dob).strip()) == 10
        assert str(dob).strip()[2] == "/" and str(dob).strip()[5] == "/"


def test_upload_invalid_dob_format_rejected():
    _seed_student("01/01/2000")
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code,Date of Birth",
        f"{EXISTING_REG},DOB Overwrite Test,B.E. Computer Science and Engineering,5,JCS2501,15-09-2004",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["invalid_count"] == 1
    assert "date of birth" in data["invalid_rows"][0]["reason"].lower()

    # DOB must be untouched after the failed import attempt
    refreshed = _test_db.query(Student).filter(Student.register_no == EXISTING_REG).first()
    _test_db.refresh(refreshed)
    assert refreshed.dob == "01/01/2000"


def test_sample_dob_deterministic_and_valid():
    from backend.app.security import is_strict_ddmmyyyy

    # Template registers keep the shipped sample dates
    for reg, dob in TEMPLATE_DOBS.items():
        assert sample_dob(reg) == dob
        assert is_strict_ddmmyyyy(dob)

    # Derived dates are deterministic and always valid DD/MM/YYYY
    for i in range(30):
        reg = f"2403310910421{i:03d}"
        first = sample_dob(reg)
        assert first == sample_dob(reg)
        assert is_strict_ddmmyyyy(first)
        year = int(first.split("/")[2])
        assert 2004 <= year <= 2006
