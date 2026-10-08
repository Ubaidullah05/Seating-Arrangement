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
        # Sorted by seat label safely
        def seat_sort_key(a: Allocation):
            if not a.seat_label:
                return ("", 0)
            import re
            m = re.match(r"^([A-Za-z]+)(\d+)$", a.seat_label.strip())
            if m:
                return (m.group(1).upper(), int(m.group(2)))
            return (a.seat_label, 0)

        sorted_room_allocs = sorted(room_allocs, key=seat_sort_key)

        table_data = [
            [
                Paragraph("<b>S.No</b>", cell_center_style),
                Paragraph("<b>Register Number</b>", cell_center_style),
                Paragraph("<b>Name</b>", cell_text_style),
                Paragraph("<b>Seat No</b>", cell_center_style),
                Paragraph("<b>Candidate Signature</b>", cell_center_style),
            ]
        ]

        for s_idx, a in enumerate(sorted_room_allocs, start=1):
            st = a.student
            table_data.append([
                Paragraph(f"{s_idx}", cell_center_style),
                Paragraph(f"<b>{st.register_no if st else ''}</b>", cell_mono_style),
                Paragraph(f"{st.name if (st and st.name) else '-'}", cell_text_style),
                Paragraph(f"<b>{a.seat_label}</b>", cell_center_style),
                Paragraph("", cell_text_style),
            ])

        col_w = [14 * mm, 46 * mm, 54 * mm, 24 * mm, 42 * mm]
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


def generate_notice_board_pdf(allocations: List[Allocation], exam: Exam) -> io.BytesIO:
    """
    Generates a Notice Board Seating Summary PDF with room-wise register number ranges.
    Designed for printing and posting on notice boards.
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

    college_title_style = ParagraphStyle(
        "NBCollegeTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#002f66")
    )

    sub_title_style = ParagraphStyle(
        "NBSubTitle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#444444")
    )

    coe_style = ParagraphStyle(
        "NBCOETitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#b8892b")
    )

    exam_title_style = ParagraphStyle(
        "NBExamTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#111111")
    )

    doc_name_style = ParagraphStyle(
        "NBDocName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#0050b3")
    )

    cell_mono_style = ParagraphStyle(
        "NBCellMono",
        parent=styles["Normal"],
        fontName="Courier-Bold",
        fontSize=8.5,
        leading=11,
        alignment=1
    )

    cell_text_style = ParagraphStyle(
        "NBCellText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11,
        alignment=0
    )

    cell_center_style = ParagraphStyle(
        "NBCellCenter",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11,
        alignment=1
    )

    story = []

    # Header
    story.append(Paragraph("JERUSALEM COLLEGE OF ENGINEERING, Chennai - 600100", college_title_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("(An Autonomous Institution Affiliated to Anna University, Chennai)", sub_title_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATIONS", coe_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"{exam.name}", exam_title_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("NOTICE BOARD SEATING SUMMARY", doc_name_style))
    story.append(Spacer(1, 3 * mm))

    # Dividing line
    line_table = Table([[""]], colWidths=[180 * mm], rowHeights=[1.5])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0050b3")),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 3 * mm))

    # Room grouping
    room_groups = {}
    for a in allocations:
        room_name = a.classroom.name if a.classroom else "Unknown"
        floor_name = a.classroom.floor.name if (a.classroom and a.classroom.floor) else "Ground Floor"
        floor_num = a.classroom.floor.floor_number if (a.classroom and a.classroom.floor) else 0
        reg = a.student.register_no if a.student else ""
        key = (floor_num, floor_name, room_name)
        room_groups.setdefault(key, []).append(reg)

    total_candidates = len(allocations)
    total_halls = len(room_groups)

    # Info table
    info_data = [
        [
            Paragraph("<b>EXAM DATE:</b>", cell_text_style),
            Paragraph(f"{exam.exam_date}", cell_text_style),
            Paragraph("<b>SESSION:</b>", cell_text_style),
            Paragraph(f"{exam.session}", cell_text_style),
        ],
        [
            Paragraph("<b>TOTAL CANDIDATES:</b>", cell_text_style),
            Paragraph(f"<b>{total_candidates} Students</b>", cell_text_style),
            Paragraph("<b>TOTAL HALLS ALLOCATED:</b>", cell_text_style),
            Paragraph(f"<b>{total_halls} Halls</b>", cell_text_style),
        ],
    ]
    info_table = Table(info_data, colWidths=[40 * mm, 50 * mm, 45 * mm, 45 * mm])
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

    # Table of room ranges
    table_data = [
        [
            Paragraph("<b>S.No</b>", cell_center_style),
            Paragraph("<b>Floor Level</b>", cell_center_style),
            Paragraph("<b>Hall / Room</b>", cell_center_style),
            Paragraph("<b>Total Seats</b>", cell_center_style),
            Paragraph("<b>Starting Register No</b>", cell_center_style),
            Paragraph("<b>Ending Register No</b>", cell_center_style),
        ]
    ]

    sno = 1
    for (f_num, f_name, r_name), regs in sorted(room_groups.items()):
        sorted_regs = sorted(regs)
        min_r = sorted_regs[0] if sorted_regs else "-"
        max_r = sorted_regs[-1] if sorted_regs else "-"

        table_data.append([
            Paragraph(str(sno), cell_center_style),
            Paragraph(f_name, cell_center_style),
            Paragraph(f"<b>{r_name}</b>", cell_center_style),
            Paragraph(f"<b>{len(regs)}</b>", cell_center_style),
            Paragraph(f"<b>{min_r}</b>", cell_mono_style),
            Paragraph(f"<b>{max_r}</b>", cell_mono_style),
        ])
        sno += 1

    col_w = [12 * mm, 32 * mm, 28 * mm, 24 * mm, 42 * mm, 42 * mm]
    summary_table = Table(table_data, colWidths=col_w, repeatRows=1)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#002f66")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    # Set header font color to white for headers
    for i in range(6):
        summary_table.setStyle(TableStyle([
            ('TEXTCOLOR', (i, 0), (i, 0), colors.white)
        ]))

    story.append(summary_table)

    # Note at bottom
    story.append(Spacer(1, 8 * mm))
    note_style = ParagraphStyle(
        "NBNote",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        alignment=0,
        textColor=colors.HexColor("#555555")
    )
    story.append(Paragraph("Note: Candidates are instructed to verify their register number and occupy their assigned seats in the corresponding examination hall 15 minutes before the commencement of the exam.", note_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

