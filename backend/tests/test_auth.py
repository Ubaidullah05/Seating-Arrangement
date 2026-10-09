"""Tests for the RBAC authentication endpoints (student DOB login + faculty email login)."""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models import Student, Floor, Classroom, Exam, Allocation
from backend.app.routers.auth import bootstrap_faculty_user
from conftest import test_session as _test_db

client = TestClient(app)

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
bootstrap_faculty_user(_test_db)

STUDENT_REG = "2403310910421777"
STUDENT_DOB = "15/08/2005"

_student = Student(register_no=STUDENT_REG, name="Auth Test Student", dob=STUDENT_DOB)
_test_db.add(_student)
_test_db.commit()
_test_db.refresh(_student)


# ---------------------------------------------------------------------------
# Student login
# ---------------------------------------------------------------------------
def test_student_login_success():
    res = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": STUDENT_DOB},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "student"
    assert data["access_token"]
    assert data["student"]["register_no"] == STUDENT_REG
    # DOB must never leak in the response
    assert "dob" not in (data["student"] or {})


def test_student_login_rejects_non_strict_dob_formats():
    wrong_formats = [
        "2005-08-15",   # YYYY-MM-DD
        "15-08-2005",   # DD-MM-YYYY
        "15.08.2005",   # dots
        "15/8/2005",    # single-digit month
        "1/5/2005",     # single digit day/month
        "15/08/05",     # 2-digit year
        "08/15/2005",   # MM/DD/YYYY
    ]
    for bad in wrong_formats:
        res = client.post(
            "/api/v1/auth/student/login",
            json={"register_no": STUDENT_REG, "password": bad},
        )
        assert res.status_code in (400, 401), f"Accepted bad DOB format: {bad}"


def test_student_login_rejects_impossible_date():
    # 31/02/2005 matches the pattern but is not a real date
    res = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": "31/02/2005"},
    )
    assert res.status_code in (400, 401)


def test_student_login_wrong_dob():
    res = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": "16/08/2005"},
    )
    assert res.status_code == 401


def test_student_login_unknown_register():
    res = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": "9999999999999999", "password": STUDENT_DOB},
    )
    assert res.status_code == 401


def test_student_login_invalid_register_length():
    res = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": "12345", "password": STUDENT_DOB},
    )
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Faculty login
# ---------------------------------------------------------------------------
def test_faculty_login_default_credentials():
    res = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "acoe@123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "faculty"
    assert data["email"] == "acoe@jerusalemengg.ac.in"
    assert data["must_change_password"] is True
    assert data["access_token"]


def test_faculty_login_rejects_non_institutional_email():
    bad_emails = [
        "acoe@gmail.com",
        "acoe@jerusalemengg.ac",      # wrong TLD
        "not-an-email",
        "acoe@@jerusalemengg.ac.in",
        "acoe @jerusalemengg.ac.in",
        "someone@othersite.com",
    ]
    for bad in bad_emails:
        res = client.post(
            "/api/v1/auth/faculty/login",
            json={"email": bad, "password": "acoe@123"},
        )
        assert res.status_code in (400, 401), f"Accepted bad email: {bad}"


def test_faculty_login_wrong_password():
    res = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "wrongpass"},
    )
    assert res.status_code == 401


def test_faculty_login_unknown_institutional_email():
    # Format is valid but no account exists
    res = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "other@jerusalemengg.ac.in", "password": "acoe@123"},
    )
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Session info & student seats
# ---------------------------------------------------------------------------
def test_me_endpoint_student():
    token = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": STUDENT_DOB},
    ).json()["access_token"]
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["role"] == "student"


def test_me_endpoint_requires_token():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_student_seats_shows_only_my_hall():
    # Give the seeded student an allocation
    floor = Floor(name="Ground Floor", floor_number=0)
    _test_db.add(floor)
    _test_db.commit()
    room = Classroom(floor_id=floor.id, name="TEST101", columns=4, rows_per_column=7)
    _test_db.add(room)
    _test_db.commit()
    exam = Exam(name="UNIT TEST EXAM", exam_date="15-10-2026", session="FN")
    _test_db.add(exam)
    _test_db.commit()
    _test_db.add(
        Allocation(
            exam_id=exam.id,
            student_id=_student.id,
            classroom_id=room.id,
            seat_label="B3",
        )
    )
    _test_db.commit()

    token = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": STUDENT_DOB},
    ).json()["access_token"]

    res = client.get(
        "/api/v1/auth/student/seats", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    seats = res.json()
    assert len(seats) == 1
    assert seats[0]["classroom_name"] == "TEST101"
    assert seats[0]["seat_label"] == "B3"
    assert seats[0]["floor_name"] == "Ground Floor"
    assert seats[0]["exam_name"] == "UNIT TEST EXAM"


def test_student_seats_forbidden_for_faculty():
    token = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "acoe@123"},
    ).json()["access_token"]
    res = client.get(
        "/api/v1/auth/student/seats", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Change password (run last: restores the default password afterwards)
# ---------------------------------------------------------------------------
def test_change_password_flow():
    login = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "acoe@123"},
    ).json()
    token = login["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Wrong current password
    res = client.post(
        "/api/v1/auth/faculty/change-password",
        json={"old_password": "not-the-password", "new_password": "newsecret1"},
        headers=headers,
    )
    assert res.status_code == 400

    # Too-short new password
    res = client.post(
        "/api/v1/auth/faculty/change-password",
        json={"old_password": "acoe@123", "new_password": "abc"},
        headers=headers,
    )
    assert res.status_code == 422

    # Successful change
    res = client.post(
        "/api/v1/auth/faculty/change-password",
        json={"old_password": "acoe@123", "new_password": "newsecret1"},
        headers=headers,
    )
    assert res.status_code == 200

    # Old password no longer works, new one does
    res = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "acoe@123"},
    )
    assert res.status_code == 401
    res = client.post(
        "/api/v1/auth/faculty/login",
        json={"email": "acoe@jerusalemengg.ac.in", "password": "newsecret1"},
    )
    assert res.status_code == 200
    assert res.json()["must_change_password"] is False

    # Restore the default password so other tests keep working
    new_token = res.json()["access_token"]
    res = client.post(
        "/api/v1/auth/faculty/change-password",
        json={"old_password": "newsecret1", "new_password": "acoe@123"},
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert res.status_code == 200


def test_change_password_requires_faculty_role():
    token = client.post(
        "/api/v1/auth/student/login",
        json={"register_no": STUDENT_REG, "password": STUDENT_DOB},
    ).json()["access_token"]
    res = client.post(
        "/api/v1/auth/faculty/change-password",
        json={"old_password": "x", "new_password": "yyyyyy"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
