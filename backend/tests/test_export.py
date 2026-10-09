import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import Student, Floor, Classroom, Exam, Allocation
from backend.app.schemas import GenerateAllocationRequest
from backend.app.allocation import run_seating_allocation

@pytest.fixture
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    # Create floor and classroom
    floor = Floor(name="Ground Floor", floor_number=0)
    db.add(floor)
    db.flush()

    room = Classroom(floor_id=floor.id, name="M001", columns=4, rows_per_column=7, is_active=True)
    db.add(room)
    db.flush()

    # Add 10 students with valid 16-digit register numbers
    students = [
        Student(register_no=f"240331091042{i:04d}", name=f"Student {i}", branch="CSE")
        for i in range(1, 11)
    ]
    db.add_all(students)
    db.commit()

    # Generate allocations
    req = GenerateAllocationRequest(name="Midterm Exam", exam_date="15-10-2026", session="FN", seed=42)
    exam, _ = run_seating_allocation(db, req)

    # Empty exam without allocations
    empty_exam = Exam(name="Empty Exam", exam_date="16-10-2026", session="AN")
    db.add(empty_exam)
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client, exam.id, empty_exam.id, db

    app.dependency_overrides.clear()
    db.close()


def test_export_pdf_success(client_with_db):
    client, exam_id, _, _ = client_with_db
    response = client.get(f"/api/v1/export/pdf?exam_id={exam_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000


def test_export_xlsx_success(client_with_db):
    client, exam_id, _, _ = client_with_db
    response = client.get(f"/api/v1/export/xlsx?exam_id={exam_id}")
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert len(response.content) > 1000


def test_export_notice_board_xlsx_success(client_with_db):
    client, exam_id, _, _ = client_with_db
    response = client.get(f"/api/v1/export/notice-board-xlsx?exam_id={exam_id}")
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert len(response.content) > 1000


def test_export_notice_board_pdf_success(client_with_db):
    client, exam_id, _, _ = client_with_db
    response = client.get(f"/api/v1/export/notice-board-pdf?exam_id={exam_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000


def test_export_no_allocations_returns_400(client_with_db):
    client, _, empty_exam_id, _ = client_with_db
    res_pdf = client.get(f"/api/v1/export/pdf?exam_id={empty_exam_id}")
    assert res_pdf.status_code == 400
    assert "No seating allocations" in res_pdf.json()["message"]

    res_xlsx = client.get(f"/api/v1/export/xlsx?exam_id={empty_exam_id}")
    assert res_xlsx.status_code == 400

    res_nb_xlsx = client.get(f"/api/v1/export/notice-board-xlsx?exam_id={empty_exam_id}")
    assert res_nb_xlsx.status_code == 400

    res_nb_pdf = client.get(f"/api/v1/export/notice-board-pdf?exam_id={empty_exam_id}")
    assert res_nb_pdf.status_code == 400


def test_export_with_em_dash_in_exam_name(client_with_db):
    """
    Verifies that exams with unicode em-dash '\u2014' (e.g. 'END SEMESTER EXAMINATIONS — OCT/NOV 2026')
    do NOT fail with UnicodeEncodeError: 'latin-1' codec can't encode character '\u2014'.
    """
    client, exam_id, _, db = client_with_db
    from backend.app.models import Exam

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    exam.name = "END SEMESTER EXAMINATIONS \u2014 OCT/NOV 2026"
    db.commit()


    # 1. PDF
    res_pdf = client.get(f"/api/v1/export/pdf?exam_id={exam_id}")
    assert res_pdf.status_code == 200
    cd = res_pdf.headers["content-disposition"]
    cd.encode("latin-1")  # Must not raise UnicodeEncodeError

    # 2. XLSX
    res_xlsx = client.get(f"/api/v1/export/xlsx?exam_id={exam_id}")
    assert res_xlsx.status_code == 200
    res_xlsx.headers["content-disposition"].encode("latin-1")

    # 3. Notice Board XLSX
    res_nb_xlsx = client.get(f"/api/v1/export/notice-board-xlsx?exam_id={exam_id}")
    assert res_nb_xlsx.status_code == 200
    res_nb_xlsx.headers["content-disposition"].encode("latin-1")

    # 4. Notice Board PDF
    res_nb_pdf = client.get(f"/api/v1/export/notice-board-pdf?exam_id={exam_id}")
    assert res_nb_pdf.status_code == 200
    res_nb_pdf.headers["content-disposition"].encode("latin-1")


