from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import crud
from backend.app.export_xlsx import generate_allocations_xlsx, generate_notice_board_xlsx
from backend.app.export_pdf import generate_seating_pdf

router = APIRouter(prefix="/api/v1/export", tags=["export"])

@router.get("/pdf")
def export_pdf(
    exam_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    allocations = crud.get_all_allocations_for_exam(db, exam_id)
    if not allocations:
        raise HTTPException(status_code=400, detail="No seating allocations found for this exam.")

    pdf_buffer = generate_seating_pdf(allocations, exam)
    clean_name = exam.name.replace(" ", "_").replace("/", "-")
    filename = f"Seating_Plan_{clean_name}_{exam.exam_date}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/xlsx")
def export_xlsx(
    exam_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    allocations = crud.get_all_allocations_for_exam(db, exam_id)
    if not allocations:
        raise HTTPException(status_code=400, detail="No seating allocations found for this exam.")

    xlsx_buffer = generate_allocations_xlsx(allocations, exam)
    clean_name = exam.name.replace(" ", "_").replace("/", "-")
    filename = f"Seating_Plan_{clean_name}_{exam.exam_date}.xlsx"

    return StreamingResponse(
        xlsx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/notice-board-xlsx")
def export_notice_board_xlsx(
    exam_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    allocations = crud.get_all_allocations_for_exam(db, exam_id)
    if not allocations:
        raise HTTPException(status_code=400, detail="No seating allocations found for this exam.")

    xlsx_buffer = generate_notice_board_xlsx(allocations, exam)
    clean_name = exam.name.replace(" ", "_").replace("/", "-")
    filename = f"Notice_Board_{clean_name}_{exam.exam_date}.xlsx"

    return StreamingResponse(
        xlsx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
