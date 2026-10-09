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


def test_upload_existing_without_dob_is_duplicate():
    _seed_student("01/01/2000")
    csv_bytes = _csv_bytes(
        "Register Number,Student Name,Branch,Semester,Course Code",
        f"{EXISTING_REG},DOB Overwrite Test,B.E. Computer Science and Engineering,5,JCS2501",
    )

    response = _preview(csv_bytes)
    assert response.status_code == 200
    data = response.json()
    assert data["valid_count"] == 0
    assert data["duplicate_count"] == 1
    assert data["duplicate_rows"][0]["register_no"] == EXISTING_REG


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
