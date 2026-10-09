from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class StudentBase(BaseModel):
    register_no: str = Field(..., description="Exact 16-digit numeric register number")
    name: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    subject_code: Optional[str] = None
    dob: Optional[str] = Field(
        None,
        description="Date of birth in strict DD/MM/YYYY format (used as login password)",
    )

    @field_validator("register_no")
    @classmethod
    def validate_register_no(cls, v: str) -> str:
        s = str(v).strip().lstrip("'")
        if not re.match(r"^\d{16}$", s):
            raise ValueError(f"Register number must be exactly 16 numeric digits, received: '{s}'")
        return s

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        from datetime import datetime
        if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$", s):
            raise ValueError(
                f"Date of birth must be in DD/MM/YYYY format, received: '{s}'"
            )
        try:
            datetime.strptime(s, "%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Date of birth is not a valid calendar date: '{s}'")
        return s

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    # DOB is the student's portal password — never serialize it in API responses
    dob: Optional[str] = Field(None, exclude=True)

    model_config = ConfigDict(from_attributes=True)


class InvalidRow(BaseModel):
    row_number: int
    raw_value: Optional[str] = None
    reason: str

class DuplicateRow(BaseModel):
    row_number: int
    register_no: str
    reason: str

class UploadPreviewResponse(BaseModel):
    filename: str
    total_rows: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    invalid_rows: List[InvalidRow]
    duplicate_rows: List[DuplicateRow]
    valid_preview: List[StudentBase]
    all_valid: Optional[List[StudentBase]] = None

class UploadCommitRequest(BaseModel):
    students: List[StudentCreate]

class UploadCommitResponse(BaseModel):
    message: str
    imported_count: int


class ClassroomBase(BaseModel):
    name: str
    columns: int = 4
    rows_per_column: int = 7
    is_active: bool = True

class ClassroomCreate(ClassroomBase):
    floor_id: int

class ClassroomUpdate(BaseModel):
    rows_per_column: Optional[int] = Field(None, ge=5, le=8)
    is_active: Optional[bool] = None

class ClassroomResponse(ClassroomBase):
    id: int
    floor_id: int
    capacity: int

    model_config = ConfigDict(from_attributes=True)

class FloorCreate(BaseModel):
    name: str
    floor_number: Optional[int] = None

class FloorResponse(BaseModel):
    id: int
    name: str
    floor_number: int
    classrooms: List[ClassroomResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ExamBase(BaseModel):
    name: str
    exam_date: str
    session: str # "FN" or "AN"
    seed: Optional[int] = None

class ExamCreate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: int
    created_at: Any
    total_allocated: int = 0

    model_config = ConfigDict(from_attributes=True)


class GenerateAllocationRequest(BaseModel):
    name: str = "END SEMESTER EXAMINATIONS - OCT/NOV 2026"
    exam_date: str = "2026-10-15"
    session: str = "FN"
    seed: Optional[int] = None
    reshuffle: bool = False


class AllocationItemResponse(BaseModel):
    id: int
    student_id: int
    register_no: str
    student_name: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    subject_code: Optional[str] = None
    floor_name: str
    classroom_id: int
    classroom_name: str
    seat_label: str

    model_config = ConfigDict(from_attributes=True)


class SeatGridCell(BaseModel):
    seat_label: str # e.g. "A1"
    column: str # "A"
    row: int # 1
    allocation: Optional[AllocationItemResponse] = None


class RoomSeatingPlanResponse(BaseModel):
    classroom_id: int
    classroom_name: str
    floor_name: str
    floor_id: int
    columns: int
    rows_per_column: int
    capacity: int
    allocated_count: int
    grid: List[List[SeatGridCell]] # 2D array: rows x columns
    min_register_no: Optional[str] = None
    max_register_no: Optional[str] = None


class NoticeBoardRoomRange(BaseModel):
    classroom_name: str
    floor_name: str
    student_count: int
    min_register_no: Optional[str] = None
    max_register_no: Optional[str] = None
    ranges_summary: str


class NoticeBoardResponse(BaseModel):
    exam: ExamResponse
    total_students: int
    rooms: List[NoticeBoardRoomRange]


class StudentSearchResult(BaseModel):
    found: bool
    student: Optional[StudentResponse] = None
    allocation: Optional[AllocationItemResponse] = None
    exam_name: Optional[str] = None


class DashboardStats(BaseModel):
    total_students: int
    total_active_rooms: int
    total_inactive_rooms: int
    total_capacity: int
    total_allocated: int
    total_unallocated: int
    active_exam_id: Optional[int] = None
    active_exam_name: Optional[str] = None
    active_exam_date: Optional[str] = None
    active_exam_session: Optional[str] = None


# ---------------------------------------------------------------------------
# Authentication schemas
# ---------------------------------------------------------------------------
class StudentLoginRequest(BaseModel):
    register_no: str = Field(..., description="16-digit register number")
    password: str = Field(..., description="Date of birth in DD/MM/YYYY format")


class FacultyLoginRequest(BaseModel):
    email: str = Field(..., description="Institutional email ending @jerusalemengg.ac.in")
    password: str = Field(..., description="Faculty password (default: acoe@123)")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str  # "student" | "faculty"
    must_change_password: bool = False
    student: Optional[StudentResponse] = None
    email: Optional[str] = None


class StudentSeatResponse(BaseModel):
    exam_id: int
    exam_name: str
    exam_date: str
    session: str
    floor_name: str
    classroom_name: str
    seat_label: str
