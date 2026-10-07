import random
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models import Student, Classroom, Exam, Allocation
from backend.app.schemas import GenerateAllocationRequest

def generate_seat_labels(rows_per_column: int, columns: int = 4) -> List[str]:
    """
    Generate seat labels in 4 columns (A, B, C, D) and rows (1..rows_per_column).
    Ordered in snake or column-first order.
    Columns are ['A', 'B', 'C', 'D'].
    For example: A1, A2, A3... A7, B1..B7, C1..C7, D1..D7
    """
    col_names = ["A", "B", "C", "D"][:columns]
    seats = []
    # Interleaving across columns for better exam supervision spacing:
    # Row 1: A1, B1, C1, D1
    # Row 2: A2, B2, C2, D2 ...
    for r in range(1, rows_per_column + 1):
        for c in col_names:
            seats.append(f"{c}{r}")
    return seats

def run_seating_allocation(
    db: Session,
    request: GenerateAllocationRequest
) -> Tuple[Exam, int]:
    """
    Executes student seating allocation inside a single transaction.
    1. Fetches all registered students.
    2. Fetches active classrooms ordered by floor number and room name.
    3. Checks capacity constraints.
    4. Shuffles students randomly using the provided/generated seed.
    5. Balances students evenly across classrooms (25-27 students per room).
    6. Interleaves branches/subjects to avoid adjacent duplicates.
    7. Creates or updates the Exam and saves Allocations.
    """
    students: List[Student] = db.query(Student).order_by(Student.register_no).all()
    if not students:
        raise ValueError("No students found in the database. Please upload students first.")

    active_rooms: List[Classroom] = (
        db.query(Classroom)
        .filter(Classroom.is_active == True)
        .join(Classroom.floor)
        .order_by(Classroom.floor_id, Classroom.name)
        .all()
    )
    if not active_rooms:
        raise ValueError("No active classrooms found. Please enable classrooms in Room Configuration.")

    total_students = len(students)
    total_capacity = sum(r.capacity for r in active_rooms)

    if total_students > total_capacity:
        raise ValueError(
            f"Insufficient seating capacity: {total_students} students to allocate, "
            f"but active rooms have only {total_capacity} total seats. "
            f"Please activate more classrooms in Room Configuration."
        )

    # Determine seed
    seed = request.seed
    if seed is None:
        seed = random.randint(100000, 999999)

    rng = random.Random(seed)

    # Calculate rooms needed and balanced counts per room
    # We want to fill rooms evenly with ~25-27 students each
    # First find minimum number of rooms needed:
    rooms_needed = 0
    cap_accum = 0
    for r in active_rooms:
        rooms_needed += 1
        cap_accum += r.capacity
        if cap_accum >= total_students:
            break

    selected_rooms = active_rooms[:rooms_needed]

    # Distribute students evenly among selected rooms
    # Each room receives at least base_count students, remainder receives +1
    base_count = total_students // len(selected_rooms)
    remainder = total_students % len(selected_rooms)

    room_targets = {}
    for idx, r in enumerate(selected_rooms):
        target = base_count + (1 if idx < remainder else 0)
        if target > r.capacity:
            raise ValueError(
                f"Even distribution assigned {target} students to room {r.name}, "
                f"which exceeds its capacity of {r.capacity}."
            )
        room_targets[r.id] = target

    # Shuffle students
    # Group students by branch/subject if present for diversity interleaving
    students_copy = list(students)
    rng.shuffle(students_copy)

    # Optional: Branch interleaving to minimize adjacent same-branch students
    # Separate students by branch
    branches: Dict[str, List[Student]] = {}
    for s in students_copy:
        b = s.branch or "General"
        branches.setdefault(b, []).append(s)

    # Round-robin merge across branches
    interleaved_students: List[Student] = []
    branch_keys = list(branches.keys())
    rng.shuffle(branch_keys)
    max_branch_len = max(len(b_list) for b_list in branches.values()) if branches else 0

    for i in range(max_branch_len):
        for b in branch_keys:
            if i < len(branches[b]):
                interleaved_students.append(branches[b][i])

    # In case any student was missed (safety fallback)
    if len(interleaved_students) != total_students:
        interleaved_students = students_copy

    # Find existing or create new Exam record
    # Check if an exam with this name, date and session exists
    exam = (
        db.query(Exam)
        .filter(
            Exam.name == request.name,
            Exam.exam_date == request.exam_date,
            Exam.session == request.session
        )
        .first()
    )

    if not exam:
        exam = Exam(
            name=request.name,
            exam_date=request.exam_date,
            session=request.session,
            seed=seed
        )
        db.add(exam)
        db.flush()
    else:
        exam.seed = seed
        # Clear existing allocations for this exam
        db.query(Allocation).filter(Allocation.exam_id == exam.id).delete()
        db.flush()

    # Allocate students to rooms and seats
    allocations_to_add: List[Allocation] = []
    student_idx = 0

    for r in selected_rooms:
        count_for_this_room = room_targets[r.id]
        seat_labels = generate_seat_labels(r.rows_per_column, r.columns)
        
        # Take seats for this room
        assigned_seats = seat_labels[:count_for_this_room]

        for seat in assigned_seats:
            st = interleaved_students[student_idx]
            alloc = Allocation(
                exam_id=exam.id,
                student_id=st.id,
                classroom_id=r.id,
                seat_label=seat
            )
            allocations_to_add.append(alloc)
            student_idx += 1

    # Commit all allocations in single transaction
    db.add_all(allocations_to_add)
    db.commit()
    db.refresh(exam)

    return exam, len(allocations_to_add)
