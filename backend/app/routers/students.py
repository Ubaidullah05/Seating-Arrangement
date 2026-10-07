import io
import re
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import (
    StudentBase, StudentCreate, StudentResponse, 
    UploadPreviewResponse, UploadCommitRequest, UploadCommitResponse,
    InvalidRow, DuplicateRow, StudentSearchResult, AllocationItemResponse
)
from backend.app import crud

router = APIRouter(prefix="/api/v1/students", tags=["students"])

REGISTER_NO_SYNONYMS = [
    "register number", "register_no", "reg no", "reg_no", "regno",
    "registration number", "register no", "student register number", "register"
]
NAME_SYNONYMS = ["name", "student name", "student_name", "candidate name"]
BRANCH_SYNONYMS = ["branch", "dept", "department", "course", "program"]
SEM_SYNONYMS = ["sem", "semester", "current semester"]
SUBJECT_SYNONYMS = ["subject", "subject code", "subject_code", "course code", "course_code"]

def find_column(df_columns, synonyms):
    col_map = {str(c).strip().lower(): c for c in df_columns}
    for syn in synonyms:
        if syn in col_map:
            return col_map[syn]
    return None

@router.post("/upload-preview", response_model=UploadPreviewResponse)
async def upload_preview(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Parses uploaded CSV or XLSX file using pandas with dtype=str.
    Validates 16-digit register numbers, detects Excel scientific notation / float corruption,
    checks duplicates, and returns a detailed preview.
    """
    filename = file.filename or "upload"
    content = await file.read()
    
    if not (filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .csv or .xlsx file."
        )

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
        else:
            # Excel file
            df = pd.read_excel(io.BytesIO(content), dtype=str, keep_default_na=False)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}. Please check format."
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    # Match register number column
    reg_col = find_column(df.columns, REGISTER_NO_SYNONYMS)
    if not reg_col:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Missing required register number column. Found columns: {list(df.columns)}. "
                "Accepted headers include: 'Register Number', 'Reg No', 'register_no'."
            )
        )

    name_col = find_column(df.columns, NAME_SYNONYMS)
    branch_col = find_column(df.columns, BRANCH_SYNONYMS)
    sem_col = find_column(df.columns, SEM_SYNONYMS)
    sub_col = find_column(df.columns, SUBJECT_SYNONYMS)

    # Fetch existing register numbers in DB
    existing_in_db = set(
        r[0] for r in db.query(crud.Student.register_no).all()
    )

    seen_in_file = set()
    invalid_rows: List[InvalidRow] = []
    duplicate_rows: List[DuplicateRow] = []
    valid_students: List[StudentBase] = []

    for index, row in df.iterrows():
        row_num = index + 2  # 1-indexed Excel row (header is row 1)
        raw_val = str(row[reg_col]).strip()

        # Check blank
        if not raw_val or raw_val.lower() == "nan":
            continue

        # Strip leading apostrophe often used in Excel for text numbers
        cleaned_val = raw_val.lstrip("'").strip()

        # 1. Excel float / scientific notation check
        if "." in cleaned_val or "e" in cleaned_val.lower():
            invalid_rows.append(
                InvalidRow(
                    row_number=row_num,
                    raw_value=raw_val,
                    reason="Scientific notation or float detected from Excel precision loss. Format cell as Text."
                )
            )
            continue

        # 2. Exact 16 numeric digits check
        if not re.match(r"^\d{16}$", cleaned_val):
            invalid_rows.append(
                InvalidRow(
                    row_number=row_num,
                    raw_value=raw_val,
                    reason=f"Must be exactly 16 numeric digits (found {len(cleaned_val)} characters: '{cleaned_val}')."
                )
            )
            continue

        # 3. Duplicate check within file
        if cleaned_val in seen_in_file:
            duplicate_rows.append(
                DuplicateRow(
                    row_number=row_num,
                    register_no=cleaned_val,
                    reason="Duplicate register number within this uploaded file."
                )
            )
            continue

        # 4. Duplicate check against database
        if cleaned_val in existing_in_db:
            duplicate_rows.append(
                DuplicateRow(
                    row_number=row_num,
                    register_no=cleaned_val,
                    reason="Register number already exists in the database."
                )
            )
            continue

        seen_in_file.add(cleaned_val)

        name_val = str(row[name_col]).strip() if name_col and row[name_col] else None
        branch_val = str(row[branch_col]).strip() if branch_col and row[branch_col] else None
        sem_raw = str(row[sem_col]).strip() if sem_col and row[sem_col] else None
        sem_val = int(sem_raw) if (sem_raw and sem_raw.isdigit()) else None
        sub_val = str(row[sub_col]).strip() if sub_col and row[sub_col] else None

        valid_students.append(
            StudentBase(
                register_no=cleaned_val,
                name=name_val,
                branch=branch_val,
                semester=sem_val,
                subject_code=sub_val
            )
        )

    return UploadPreviewResponse(
        filename=filename,
        total_rows=len(df),
        valid_count=len(valid_students),
        invalid_count=len(invalid_rows),
        duplicate_count=len(duplicate_rows),
        invalid_rows=invalid_rows,
        duplicate_rows=duplicate_rows,
        valid_preview=valid_students[:25]
    )


@router.post("/commit-upload", response_model=UploadCommitResponse)
def commit_upload(
    payload: UploadCommitRequest,
    db: Session = Depends(get_db)
):
    if not payload.students:
        raise HTTPException(status_code=400, detail="No student data to import.")

    imported = crud.bulk_import_students(db, payload.students)
    return UploadCommitResponse(
        message=f"Successfully imported {imported} student records.",
        imported_count=imported
    )


@router.get("", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    return crud.get_students(db, skip=skip, limit=limit)


@router.delete("/all")
def clear_students(db: Session = Depends(get_db)):
    deleted = crud.clear_all_students(db)
    return {"message": f"Cleared {deleted} student records from database."}


@router.get("/search", response_model=List[StudentSearchResult])
def search_student(
    q: str = Query(..., min_length=2, description="Register number (full or last 3-4 digits) or name"),
    exam_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    results = crud.search_student(db, query=q, exam_id=exam_id)
    response_list = []
    for st, alloc in results:
        alloc_dto = None
        exam_name = None
        if alloc:
            floor_name = alloc.classroom.floor.name if (alloc.classroom and alloc.classroom.floor) else "Ground Floor"
            classroom_name = alloc.classroom.name if alloc.classroom else "Unknown"
            exam_name = alloc.exam.name if alloc.exam else None
            alloc_dto = AllocationItemResponse(
                id=alloc.id,
                student_id=alloc.student_id,
                register_no=st.register_no,
                student_name=st.name,
                branch=st.branch,
                semester=st.semester,
                subject_code=st.subject_code,
                floor_name=floor_name,
                classroom_id=alloc.classroom_id,
                classroom_name=classroom_name,
                seat_label=alloc.seat_label
            )

        response_list.append(
            StudentSearchResult(
                found=True,
                student=StudentResponse.model_validate(st),
                allocation=alloc_dto,
                exam_name=exam_name
            )
        )
    return response_list
