import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List
from backend.app.models import Allocation, Exam

def generate_allocations_xlsx(allocations: List[Allocation], exam: Exam) -> io.BytesIO:
    """
    Generates an Excel workbook with allocations.
    Ensures register numbers are written EXPLICITLY as string/text cells
    with number_format='@' to prevent Excel 15-digit precision truncation.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Seating Allocation"

    # Header styling (matching Jerusalem College of Engineering navy blue theme)
    header_fill = PatternFill(start_color="002F66", end_color="002F66", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    sub_fill = PatternFill(start_color="004A99", end_color="004A99", fill_type="solid")
    sub_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    
    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )
    
    mono_font = Font(name="Consolas", size=10, bold=True)
    body_font = Font(name="Segoe UI", size=10)

    # Title rows
    ws.merge_cells("A1:G1")
    ws["A1"] = "JERUSALEM COLLEGE OF ENGINEERING, CHENNAI - 600100"
    ws["A1"].font = Font(name="Georgia", size=14, bold=True, color="002F66")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 25

    ws.merge_cells("A2:G2")
    ws["A2"] = f"OFFICE OF THE CONTROLLER OF EXAMINATIONS | {exam.name}"
    ws["A2"].font = Font(name="Segoe UI", size=11, bold=True, color="B8892B")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    ws.merge_cells("A3:G3")
    ws["A3"] = f"Date: {exam.exam_date} | Session: {exam.session} | Total Allocated: {len(allocations)}"
    ws["A3"].font = Font(name="Segoe UI", size=10, italic=True, color="555555")
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 18

    # Blank row
    ws.row_dimensions[4].height = 10

    # Column Headers
    headers = [
        "S.No",
        "Register Number",
        "Student Name",
        "Branch",
        "Floor",
        "Room No",
        "Seat"
    ]
    
    row_idx = 5
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.fill = sub_fill
        cell.font = sub_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[row_idx].height = 26

    # Sort allocations by floor, room, seat
    sorted_allocs = sorted(
        allocations, 
        key=lambda a: (
            a.classroom.floor.floor_number if a.classroom and a.classroom.floor else 0,
            a.classroom.name if a.classroom else "",
            a.seat_label
        )
    )

    row_idx = 6
    for idx, a in enumerate(sorted_allocs, start=1):
        st = a.student
        room = a.classroom
        floor_name = room.floor.name if (room and room.floor) else "Ground Floor"
        room_name = room.name if room else ""

        # 1. S.No
        c1 = ws.cell(row=row_idx, column=1, value=idx)
        c1.alignment = Alignment(horizontal="center")
        c1.font = body_font
        c1.border = thin_border

        # 2. Register Number (CRITICAL: String data_type and '@' text format)
        reg_no_str = str(st.register_no) if st else ""
        c2 = ws.cell(row=row_idx, column=2)
        c2.value = reg_no_str
        c2.data_type = 's'  # Explicit string type in OpenPyXL
        c2.number_format = '@' # Plain text format
        c2.font = mono_font
        c2.alignment = Alignment(horizontal="center")
        c2.border = thin_border

        # 3. Student Name
        c3 = ws.cell(row=row_idx, column=3, value=st.name if st and st.name else "-")
        c3.font = body_font
        c3.border = thin_border

        # 4. Branch
        c4 = ws.cell(row=row_idx, column=4, value=st.branch if st and st.branch else "-")
        c4.font = body_font
        c4.alignment = Alignment(horizontal="center")
        c4.border = thin_border

        # 5. Floor
        c5 = ws.cell(row=row_idx, column=5, value=floor_name)
        c5.font = body_font
        c5.alignment = Alignment(horizontal="center")
        c5.border = thin_border

        # 6. Room No (e.g. M001..M008)
        c6 = ws.cell(row=row_idx, column=6, value=room_name)
        c6.font = mono_font
        c6.alignment = Alignment(horizontal="center")
        c6.border = thin_border

        # 7. Seat (e.g. A1..D7)
        c7 = ws.cell(row=row_idx, column=7, value=a.seat_label)
        c7.font = mono_font
        c7.alignment = Alignment(horizontal="center")
        c7.border = thin_border

        ws.row_dimensions[row_idx].height = 20
        row_idx += 1

    # Auto-fit column widths
    column_widths = {
        "A": 8,   # S.No
        "B": 24,  # Register Number (16 digits + space)
        "C": 30,  # Student Name
        "D": 22,  # Branch
        "E": 18,  # Floor
        "F": 14,  # Room No
        "G": 10   # Seat
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_notice_board_xlsx(allocations: List[Allocation], exam: Exam) -> io.BytesIO:
    """
    Generates a Notice Board Summary sheet in Excel with room-wise register number ranges.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notice Board Summary"

    # Header styling
    sub_fill = PatternFill(start_color="002F66", end_color="002F66", fill_type="solid")
    sub_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    mono_font = Font(name="Consolas", size=10, bold=True)
    body_font = Font(name="Segoe UI", size=10)
    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    ws.merge_cells("A1:F1")
    ws["A1"] = "JERUSALEM COLLEGE OF ENGINEERING, CHENNAI - 600100"
    ws["A1"].font = Font(name="Georgia", size=14, bold=True, color="002F66")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:F2")
    ws["A2"] = f"EXAM SEATING NOTICE BOARD | {exam.name} | Date: {exam.exam_date} ({exam.session})"
    ws["A2"].font = Font(name="Segoe UI", size=11, bold=True, color="B8892B")
    ws["A2"].alignment = Alignment(horizontal="center")

    headers = ["S.No", "Floor", "Hall / Room", "Total Count", "Starting Reg No", "Ending Reg No"]
    ws.row_dimensions[4].height = 24
    for c_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=c_idx, value=h)
        c.fill = sub_fill
        c.font = sub_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

    # Group by room
    room_groups = {}
    for a in allocations:
        room_name = a.classroom.name if a.classroom else "Unknown"
        floor_name = a.classroom.floor.name if (a.classroom and a.classroom.floor) else "Ground Floor"
        floor_num = a.classroom.floor.floor_number if (a.classroom and a.classroom.floor) else 0
        reg = a.student.register_no if a.student else ""
        key = (floor_num, floor_name, room_name)
        room_groups.setdefault(key, []).append(reg)

    row_idx = 5
    sno = 1
    for (f_num, f_name, r_name), regs in sorted(room_groups.items()):
        sorted_regs = sorted(regs) # Equal length string sort = numeric order
        min_r = sorted_regs[0] if sorted_regs else "-"
        max_r = sorted_regs[-1] if sorted_regs else "-"

        ws.cell(row=row_idx, column=1, value=sno).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=2, value=f_name).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=3, value=r_name).font = mono_font
        ws.cell(row=row_idx, column=3).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=4, value=len(regs)).alignment = Alignment(horizontal="center")
        
        c5 = ws.cell(row=row_idx, column=5, value=min_r)
        c5.data_type = 's'
        c5.number_format = '@'
        c5.font = mono_font
        c5.alignment = Alignment(horizontal="center")

        c6 = ws.cell(row=row_idx, column=6, value=max_r)
        c6.data_type = 's'
        c6.number_format = '@'
        c6.font = mono_font
        c6.alignment = Alignment(horizontal="center")

        for col in range(1, 7):
            ws.cell(row=row_idx, column=col).border = thin_border

        ws.row_dimensions[row_idx].height = 20
        row_idx += 1
        sno += 1

    widths = {"A": 8, "B": 18, "C": 16, "D": 14, "E": 24, "F": 24}
    for c_let, w in widths.items():
        ws.column_dimensions[c_let].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
