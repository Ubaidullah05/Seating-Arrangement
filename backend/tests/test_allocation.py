import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import Student, Floor, Classroom, Exam, Allocation
from backend.app.schemas import GenerateAllocationRequest
from backend.app.allocation import run_seating_allocation

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create 1 floor with 3 rooms (each room has 4 cols x 7 rows = 28 capacity)
    floor = Floor(name="Ground Floor", floor_number=0)
    db.add(floor)
    db.flush()

    rooms = [
        Classroom(floor_id=floor.id, name=f"M00{i}", columns=4, rows_per_column=7, is_active=True)
        for i in range(1, 4) # 3 rooms -> total capacity 84
    ]
    db.add_all(rooms)
    db.commit()

    yield db
    db.close()

def test_allocation_even_distribution(test_db):
    # Insert 75 students (should distribute 25, 25, 25 across 3 rooms)
    students = [
        Student(
            register_no=f"240331091042{i:04d}",
            name=f"Student {i}",
            branch="CSE" if i % 2 == 0 else "ECE"
        )
        for i in range(1, 76)
    ]
    test_db.add_all(students)
    test_db.commit()

    req = GenerateAllocationRequest(
        name="TEST EXAM",
        exam_date="2026-10-15",
        session="FN",
        seed=42
    )

    exam, count = run_seating_allocation(test_db, req)
    assert count == 75

    # Check distribution across rooms
    allocs = test_db.query(Allocation).filter(Allocation.exam_id == exam.id).all()
    assert len(allocs) == 75

    # Group by room
    room_counts = {}
    for a in allocs:
        room_counts[a.classroom_id] = room_counts.get(a.classroom_id, 0) + 1

    assert len(room_counts) == 3
    for room_id, r_count in room_counts.items():
        assert r_count == 25, f"Expected 25 students in room {room_id}, got {r_count}"

def test_allocation_no_duplicate_seats_or_students(test_db):
    students = [
        Student(register_no=f"240331091042{i:04d}", name=f"Student {i}")
        for i in range(1, 55)
    ]
    test_db.add_all(students)
    test_db.commit()

    req = GenerateAllocationRequest(
        name="DUP CHECK EXAM",
        exam_date="2026-10-15",
        session="AN",
        seed=123
    )

    exam, count = run_seating_allocation(test_db, req)
    allocs = test_db.query(Allocation).filter(Allocation.exam_id == exam.id).all()
    
    # Check student uniqueness
    allocated_students = set(a.student_id for a in allocs)
    assert len(allocated_students) == 54

    # Check (room, seat) uniqueness
    room_seats = set((a.classroom_id, a.seat_label) for a in allocs)
    assert len(room_seats) == 54

def test_allocation_capacity_exceeded_error(test_db):
    # Total capacity is 84, insert 90 students
    students = [
        Student(register_no=f"240331091042{i:04d}", name=f"Student {i}")
        for i in range(1, 91)
    ]
    test_db.add_all(students)
    test_db.commit()

    req = GenerateAllocationRequest(name="OVERFLOW EXAM", exam_date="2026-10-15", session="FN")
    with pytest.raises(ValueError) as excinfo:
        run_seating_allocation(test_db, req)
    assert "Insufficient seating capacity" in str(excinfo.value)
