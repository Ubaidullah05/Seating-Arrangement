from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import (
    GenerateAllocationRequest, RoomSeatingPlanResponse, SeatGridCell,
    AllocationItemResponse, NoticeBoardResponse, NoticeBoardRoomRange,
    ExamResponse, DashboardStats
)
from backend.app import crud
from backend.app.allocation import run_seating_allocation
from backend.app.models import Classroom, Exam, Allocation

router = APIRouter(prefix="/api/v1/allocations", tags=["allocations"])

@router.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@router.post("/generate")
def generate_allocations(
    request: GenerateAllocationRequest,
    db: Session = Depends(get_db)
):
    try:
        exam, count = run_seating_allocation(db, request)
        return {
            "message": f"Successfully generated seating arrangement for {count} students.",
            "exam_id": exam.id,
            "exam_name": exam.name,
            "allocated_count": count,
            "seed": exam.seed
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")

@router.get("/room-plan", response_model=RoomSeatingPlanResponse)
def get_room_seating_plan(
    exam_id: int = Query(...),
    classroom_id: int = Query(...),
    db: Session = Depends(get_db)
):
    room = crud.get_classroom_by_id(db, classroom_id)
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    allocations = crud.get_allocations_for_room(db, exam_id, classroom_id)
    
    # Map allocations by seat_label
    seat_map: Dict[str, AllocationItemResponse] = {}
    reg_numbers: List[str] = []
    
    for a in allocations:
        st = a.student
        item = AllocationItemResponse(
            id=a.id,
            student_id=a.student_id,
            register_no=st.register_no if st else "",
            student_name=st.name if st else None,
            branch=st.branch if st else None,
            semester=st.semester if st else None,
            subject_code=st.subject_code if st else None,
            floor_name=room.floor.name if room.floor else "Ground Floor",
            classroom_id=room.id,
            classroom_name=room.name,
            seat_label=a.seat_label
        )
        seat_map[a.seat_label] = item
        if st and st.register_no:
            reg_numbers.append(st.register_no)

    # Build 2D grid: rows x columns
    # Columns are A, B, C, D
    cols = ["A", "B", "C", "D"][:room.columns]
    grid: List[List[SeatGridCell]] = []

    for r in range(1, room.rows_per_column + 1):
        row_cells: List[SeatGridCell] = []
        for c in cols:
            label = f"{c}{r}"
            cell = SeatGridCell(
                seat_label=label,
                column=c,
                row=r,
                allocation=seat_map.get(label, None)
            )
            row_cells.append(cell)
        grid.append(row_cells)

    sorted_regs = sorted(reg_numbers)
    min_reg = sorted_regs[0] if sorted_regs else None
    max_reg = sorted_regs[-1] if sorted_regs else None

    return RoomSeatingPlanResponse(
        classroom_id=room.id,
        classroom_name=room.name,
        floor_name=room.floor.name if room.floor else "Ground Floor",
        floor_id=room.floor_id,
        columns=room.columns,
        rows_per_column=room.rows_per_column,
        capacity=room.capacity,
        allocated_count=len(allocations),
        grid=grid,
        min_register_no=min_reg,
        max_register_no=max_reg
    )

@router.get("/notice-board", response_model=NoticeBoardResponse)
def get_notice_board(
    exam_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    allocations = crud.get_all_allocations_for_exam(db, exam_id)
    
    # Group by room
    room_dict: Dict[int, List[Allocation]] = {}
    for a in allocations:
        room_dict.setdefault(a.classroom_id, []).append(a)

    room_ranges: List[NoticeBoardRoomRange] = []
    
    for r_id, allocs in sorted(room_dict.items(), key=lambda x: x[1][0].classroom.name if x[1] and x[1][0].classroom else ""):
        first_alloc = allocs[0]
        room = first_alloc.classroom
        floor_name = room.floor.name if (room and room.floor) else "Ground Floor"
        room_name = room.name if room else f"Room {r_id}"

        reg_nos = [a.student.register_no for a in allocs if a.student and a.student.register_no]
        sorted_regs = sorted(reg_nos)
        
        min_r = sorted_regs[0] if sorted_regs else None
        max_r = sorted_regs[-1] if sorted_regs else None
        
        summary = f"{min_r} to {max_r}" if (min_r and max_r and min_r != max_r) else (min_r or "None")

        room_ranges.append(
            NoticeBoardRoomRange(
                classroom_name=room_name,
                floor_name=floor_name,
                student_count=len(allocs),
                min_register_no=min_r,
                max_register_no=max_r,
                ranges_summary=summary
            )
        )

    exam_dto = ExamResponse.model_validate(exam)
    exam_dto.total_allocated = len(allocations)

    return NoticeBoardResponse(
        exam=exam_dto,
        total_students=len(allocations),
        rooms=room_ranges
    )
