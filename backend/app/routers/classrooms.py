from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import FloorResponse, ClassroomResponse, ClassroomUpdate
from backend.app import crud

router = APIRouter(prefix="/api/v1/classrooms", tags=["classrooms"])

@router.get("/floors", response_model=List[FloorResponse])
def get_floors_with_rooms(db: Session = Depends(get_db)):
    """
    Returns all 3 floors with their associated classrooms (e.g. M001..M008, M101..M108, M201..M208).
    """
    floors = crud.get_floors(db)
    return floors

@router.get("", response_model=List[ClassroomResponse])
def get_all_classrooms(active_only: bool = False, db: Session = Depends(get_db)):
    rooms = crud.get_classrooms(db, active_only=active_only)
    return rooms

@router.patch("/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(
    classroom_id: int,
    payload: ClassroomUpdate,
    db: Session = Depends(get_db)
):
    room = crud.update_classroom(db, classroom_id, payload)
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return room
