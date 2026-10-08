from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.schemas import ExamResponse, ExamCreate
from backend.app.models import Exam, Allocation
from backend.app import crud

router = APIRouter(prefix="/api/v1/exams", tags=["exams"])

@router.get("", response_model=List[ExamResponse])
def list_exams(db: Session = Depends(get_db)):
    exams = crud.get_exams(db)
    result = []
    for ex in exams:
        count = db.query(func.count(Allocation.id)).filter(Allocation.exam_id == ex.id).scalar() or 0
        resp = ExamResponse.model_validate(ex)
        resp.total_allocated = count
        result.append(resp)
    return result

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    count = db.query(func.count(Allocation.id)).filter(Allocation.exam_id == exam.id).scalar() or 0
    resp = ExamResponse.model_validate(exam)
    resp.total_allocated = count
    return resp

@router.post("", response_model=ExamResponse)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_exam(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
