from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import (
    FloorResponse, FloorCreate, ClassroomResponse, ClassroomCreate, ClassroomUpdate
)
from backend.app import crud

router = APIRouter(prefix="/api/v1/classrooms", tags=["classrooms"])

@router.get("/floors", response_model=List[FloorResponse])
def get_floors_with_rooms(db: Session = Depends(get_db)):
    """
    Returns all floors with their associated classrooms (e.g. Ground, First, Second, Third floor: M001..M305, LS: LS-1, VH: VH-1..VH-3).
    """
    floors = crud.get_floors(db)
    return floors

@router.post("/floors", response_model=FloorResponse)
def create_floor(payload: FloorCreate, db: Session = Depends(get_db)):
    return crud.create_floor(db, payload)

@router.get("", response_model=List[ClassroomResponse])
def get_all_classrooms(active_only: bool = False, db: Session = Depends(get_db)):
    rooms = crud.get_classrooms(db, active_only=active_only)
    return rooms

@router.post("", response_model=ClassroomResponse)
def create_classroom(payload: ClassroomCreate, db: Session = Depends(get_db)):
    return crud.create_classroom(db, payload)

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
