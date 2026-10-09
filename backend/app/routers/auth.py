"""Authentication endpoints: student (register no + DOB) and faculty (email + password)."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import crud
from backend.app.models import FacultyUser, Student, Allocation
from backend.app.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    FacultyLoginRequest,
    StudentLoginRequest,
    StudentResponse,
    StudentSeatResponse,
)
from backend.app.security import (
    DEFAULT_FACULTY_EMAIL,
    DEFAULT_FACULTY_PASSWORD,
    create_token,
    decode_token,
    hash_password,
    is_faculty_email,
    is_strict_ddmmyyyy,
    is_valid_register_no,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_current_principal(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Validate the bearer token and return the current principal (student/faculty)."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated. Please sign in.")
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")
    role = payload.get("role")
    user_id = payload.get("sub")
    if role not in ("student", "faculty") or not isinstance(user_id, int):
        raise HTTPException(status_code=401, detail="Invalid session token.")
    return {"role": role, "id": user_id, "payload": payload}


def get_current_student(principal: dict = Depends(get_current_principal)) -> dict:
    if principal["role"] != "student":
        raise HTTPException(status_code=403, detail="Student account required.")
    return principal


def get_current_faculty(principal: dict = Depends(get_current_principal)) -> dict:
    if principal["role"] != "faculty":
        raise HTTPException(status_code=403, detail="Faculty account required.")
    return principal


# ---------------------------------------------------------------------------
# Bootstrap: make sure the ACOE faculty account exists
# ---------------------------------------------------------------------------
def bootstrap_faculty_user(db: Session) -> FacultyUser:
    """Create the default ACOE account if it does not exist yet."""
    user = db.query(FacultyUser).filter(FacultyUser.email == DEFAULT_FACULTY_EMAIL).first()
    if user is None:
        user = FacultyUser(
            email=DEFAULT_FACULTY_EMAIL,
            name="ACOE - Controller of Examinations",
            hashed_password=hash_password(DEFAULT_FACULTY_PASSWORD),
            must_change_password=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Student login: register number + DOB (DD/MM/YYYY)
# ---------------------------------------------------------------------------
@router.post("/student/login", response_model=AuthResponse)
def student_login(payload: StudentLoginRequest, db: Session = Depends(get_db)):
    register_no = (payload.register_no or "").strip().lstrip("'")
    password = (payload.password or "").strip()

    if not is_valid_register_no(register_no):
        raise HTTPException(
            status_code=400,
            detail="Register number must be exactly 13 or 16 numeric digits.",
        )
    if not is_strict_ddmmyyyy(password):
        raise HTTPException(
            status_code=400,
            detail="Date of birth must be in DD/MM/YYYY format (e.g. 15/08/2005). No other formats are accepted.",
        )

    student = db.query(Student).filter(Student.register_no == register_no).first()
    if student is None or student.dob is None or student.dob.strip() != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid register number or date of birth.",
        )

    token = create_token({"role": "student", "sub": student.id, "reg": student.register_no})
    return AuthResponse(
        access_token=token,
        role="student",
        must_change_password=False,
        student=StudentResponse.model_validate(student),
    )


# ---------------------------------------------------------------------------
# Faculty login: institutional email + password (default acoe@123)
# ---------------------------------------------------------------------------
@router.post("/faculty/login", response_model=AuthResponse)
def faculty_login(payload: FacultyLoginRequest, db: Session = Depends(get_db)):
    email = (payload.email or "").strip().lower()
    password = payload.password or ""

    if not is_faculty_email(email):
        raise HTTPException(
            status_code=400,
            detail="Please use your institutional email (e.g. acoe@jerusalemengg.ac.in).",
        )

    user = db.query(FacultyUser).filter(FacultyUser.email == email).first()
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_token({"role": "faculty", "sub": user.id, "email": user.email})
    return AuthResponse(
        access_token=token,
        role="faculty",
        must_change_password=bool(user.must_change_password),
        email=user.email,
    )


# ---------------------------------------------------------------------------
# Change password (faculty, after login)
# ---------------------------------------------------------------------------
@router.post("/faculty/change-password")
def change_password(
    payload: ChangePasswordRequest,
    principal: dict = Depends(get_current_faculty),
    db: Session = Depends(get_db),
):
    user = db.query(FacultyUser).filter(FacultyUser.id == principal["id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Account not found.")

    if not verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    if new_password == payload.old_password:
        raise HTTPException(status_code=400, detail="New password must be different from the current password.")

    user.hashed_password = hash_password(new_password)
    user.must_change_password = False
    db.commit()
    return {"message": "Password changed successfully."}


# ---------------------------------------------------------------------------
# Current session info
# ---------------------------------------------------------------------------
@router.get("/me")
def read_me(principal: dict = Depends(get_current_principal), db: Session = Depends(get_db)):
    if principal["role"] == "student":
        student = db.query(Student).filter(Student.id == principal["id"]).first()
        if student is None:
            raise HTTPException(status_code=401, detail="Student account not found.")
        return {
            "role": "student",
            "student": StudentResponse.model_validate(student).model_dump(),
        }
    user = db.query(FacultyUser).filter(FacultyUser.id == principal["id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Faculty account not found.")
    return {
        "role": "faculty",
        "email": user.email,
        "name": user.name,
        "must_change_password": bool(user.must_change_password),
    }


# ---------------------------------------------------------------------------
# Student portal: view only my exam hall / seat
# ---------------------------------------------------------------------------
@router.get("/student/seats", response_model=list[StudentSeatResponse])
def my_seats(principal: dict = Depends(get_current_student), db: Session = Depends(get_db)):
    rows = (
        db.query(Allocation)
        .filter(Allocation.student_id == principal["id"])
        .join(Allocation.exam, isouter=True)
        .join(Allocation.classroom, isouter=True)
        .all()
    )
    seats: list[StudentSeatResponse] = []
    for alloc in rows:
        classroom = alloc.classroom
        floor = classroom.floor if classroom else None
        exam = alloc.exam
        seats.append(
            StudentSeatResponse(
                exam_id=exam.id if exam else 0,
                exam_name=exam.name if exam else "Examination",
                exam_date=exam.exam_date if exam else "",
                session=exam.session if exam else "",
                floor_name=floor.name if floor else "Ground Floor",
                classroom_name=classroom.name if classroom else "—",
                seat_label=alloc.seat_label,
            )
        )
    return seats
