import io
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas
from backend.app.models import Allocation, Exam, Classroom

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that adds a faint diagonal watermark and page footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_watermark_and_footer(num_pages)
            super().showPage()
        super().save()

    def draw_watermark_and_footer(self, page_count):
        self.saveState()
        # Watermark
        self.setFont("Helvetica-Bold", 38)
        self.setFillColor(colors.HexColor("#002f66"), alpha=0.04)
        self.translate(297.5, 421) # Center of A4
        self.rotate(35)
        self.drawCentredString(0, 0, "JERUSALEM COLLEGE OF ENGG")
        self.drawCentredString(0, -50, "OCT / NOV 2026")
        self.restoreState()

        # Footer
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawString(30 * mm, 12 * mm, "Office of the Controller of Examinations - JCE Chennai")
        self.drawRightString(180 * mm, 12 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_seating_pdf(allocations: List[Allocation], exam: Exam) -> io.BytesIO:
    """
    Generates a high-quality multi-page PDF with 1 page per classroom
    matching Jerusalem College of Engineering's official document style.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    college_title_style = ParagraphStyle(
        "CollegeTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.HexColor("#002f66")
    )
    
    sub_title_style = ParagraphStyle(
        "SubTitle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#444444")
    )

    coe_style = ParagraphStyle(
        "COETitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#b8892b") # Gold
    )

    exam_title_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=10.5,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#111111")
    )

    doc_name_style = ParagraphStyle(
        "DocName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#0050b3")
    )

    cell_mono_style = ParagraphStyle(
        "CellMono",
        parent=styles["Normal"],
        fontName="Courier-Bold",
        fontSize=8,
        leading=10,
        alignment=1
    )

    cell_text_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=10,
        alignment=0
    )

    cell_center_style = ParagraphStyle(
        "CellCenter",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=10,
        alignment=1
    )

    story = []

    # Group allocations by classroom
    rooms_dict: Dict[int, List[Allocation]] = {}
    for a in allocations:
        rooms_dict.setdefault(a.classroom_id, []).append(a)

    room_ids_sorted = sorted(rooms_dict.keys())

    for idx, r_id in enumerate(room_ids_sorted):
        room_allocs = rooms_dict[r_id]
        first_alloc = room_allocs[0]
        room = first_alloc.classroom
        floor_name = room.floor.name if (room and room.floor) else "Ground Floor"
        room_name = room.name if room else f"Room {r_id}"

        # Header Block
        story.append(Paragraph("JERUSALEM COLLEGE OF ENGINEERING, Chennai - 600100", college_title_style))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("(An Autonomous Institution Affiliated to Anna University, Chennai)", sub_title_style))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATIONS", coe_style))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"{exam.name}", exam_title_style))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("SEATING ARRANGEMENT", doc_name_style))
        story.append(Spacer(1, 3 * mm))

        # Thin blue dividing line
        line_table = Table([[""]], colWidths=[180 * mm], rowHeights=[1.5])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0050b3")),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 3 * mm))

        # 4-Column Info Box
        info_data = [
            [
                Paragraph("<b>EXAM DATE:</b>", cell_text_style),
                Paragraph(f"{exam.exam_date}", cell_text_style),
                Paragraph("<b>FLOOR:</b>", cell_text_style),
                Paragraph(f"{floor_name}", cell_text_style),
            ],
            [
                Paragraph("<b>SESSION:</b>", cell_text_style),
                Paragraph(f"{exam.session}", cell_text_style),
                Paragraph("<b>HALL NO:</b>", cell_text_style),
                Paragraph(f"<b>{room_name}</b>", cell_text_style),
            ],
            [
                Paragraph("<b>TOTAL STUDENTS:</b>", cell_text_style),
                Paragraph(f"<b>{len(room_allocs)}</b>", cell_text_style),
                Paragraph("<b>CAPACITY:</b>", cell_text_style),
                Paragraph(f"{room.capacity if room else 28} seats", cell_text_style),
            ],
        ]
        info_table = Table(info_data, colWidths=[35 * mm, 55 * mm, 35 * mm, 55 * mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f7f9fc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#0050b3")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 4 * mm))

        # Allocations Table for this room
        # Sorted by seat label
        sorted_room_allocs = sorted(room_allocs, key=lambda x: (x.seat_label[0], int(x.seat_label[1:])))

        table_data = [
            [
                Paragraph("<b>Seat</b>", cell_center_style),
                Paragraph("<b>Register Number (16 Digits)</b>", cell_center_style),
                Paragraph("<b>Student Name</b>", cell_text_style),
                Paragraph("<b>Branch / Dept</b>", cell_text_style),
            ]
        ]

        for a in sorted_room_allocs:
            st = a.student
            table_data.append([
                Paragraph(f"<b>{a.seat_label}</b>", cell_center_style),
                Paragraph(f"<b>{st.register_no if st else ''}</b>", cell_mono_style),
                Paragraph(f"{st.name if (st and st.name) else '-'}", cell_text_style),
                Paragraph(f"{st.branch if (st and st.branch) else '-'}", cell_text_style),
            ])

        col_w = [18 * mm, 58 * mm, 60 * mm, 44 * mm]
        seats_table = Table(table_data, colWidths=col_w, repeatRows=1)
        seats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eef2f8")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(seats_table)

        # Page break if not the last room
        if idx < len(room_ids_sorted) - 1:
            story.append(PageBreak())

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
