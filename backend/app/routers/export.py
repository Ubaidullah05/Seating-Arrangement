import re
import unicodedata
import urllib.parse
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import crud
from backend.app.export_xlsx import generate_allocations_xlsx, generate_notice_board_xlsx
from backend.app.export_pdf import generate_seating_pdf, generate_notice_board_pdf

router = APIRouter(prefix="/api/v1/export", tags=["export"])

def build_content_disposition(prefix: str, exam_name: str, exam_date: str, extension: str) -> dict:
    """
    Builds RFC 6266 / RFC 5987 compliant Content-Disposition header.
    Starlette strictly encodes HTTP response headers as 'latin-1'.
    If exam.name contains unicode characters such as '—' (em-dash \u2014) or non-latin-1 characters,
    putting it raw in filename="..." causes UnicodeEncodeError.
    This helper guarantees a safe ASCII fallback filename for latin-1 HTTP headers,
    while also supplying the UTF-8 percent-encoded filename* for modern browsers.
    """
    # Normalize unicode (e.g. em-dash '—' \u2014 to '-', en-dash '–' to '-')
    normalized = unicodedata.normalize("NFKD", exam_name)
    normalized = (
        normalized.replace("—", "-")
        .replace("–", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "_")
    )
    # Strip any remaining non-ASCII characters for the ASCII parameter
    ascii_clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "", normalized).strip("._-") or "Exam"
    ascii_filename = f"{prefix}_{ascii_clean}_{exam_date}.{extension}"

    # UTF-8 encoded filename for modern browsers supporting filename*
    full_clean = exam_name.replace("/", "-").replace("\\", "-").replace(" ", "_")
    utf8_filename = f"{prefix}_{full_clean}_{exam_date}.{extension}"
    encoded_utf8 = urllib.parse.quote(utf8_filename, encoding="utf-8")

    return {
        "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_utf8}'
    }

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
    headers = build_content_disposition("Seating_Plan", exam.name, str(exam.exam_date), "pdf")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers
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
    headers = build_content_disposition("Seating_Plan", exam.name, str(exam.exam_date), "xlsx")

    return StreamingResponse(
        xlsx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
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
    headers = build_content_disposition("Notice_Board", exam.name, str(exam.exam_date), "xlsx")

    return StreamingResponse(
        xlsx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@router.get("/notice-board-pdf")
def export_notice_board_pdf(
    exam_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exam = crud.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    allocations = crud.get_all_allocations_for_exam(db, exam_id)
    if not allocations:
        raise HTTPException(status_code=400, detail="No seating allocations found for this exam.")

    pdf_buffer = generate_notice_board_pdf(allocations, exam)
    headers = build_content_disposition("Notice_Board", exam.name, str(exam.exam_date), "pdf")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers
    )


