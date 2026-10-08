from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from backend.app.models import Student, Floor, Classroom, Exam, Allocation
from backend.app.schemas import StudentCreate, ClassroomUpdate, ExamCreate, ClassroomCreate, FloorCreate

def get_floors(db: Session) -> List[Floor]:
    return db.query(Floor).order_by(Floor.floor_number).all()

def create_floor(db: Session, floor_in: FloorCreate) -> Floor:
    if floor_in.floor_number is None:
        max_num = db.query(func.max(Floor.floor_number)).scalar()
        floor_number = (max_num + 1) if max_num is not None else 0
    else:
        floor_number = floor_in.floor_number
    floor = Floor(name=floor_in.name, floor_number=floor_number)
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor

def create_classroom(db: Session, room_in: ClassroomCreate) -> Classroom:
    room = Classroom(
        floor_id=room_in.floor_id,
        name=room_in.name,
        columns=room_in.columns,
        rows_per_column=room_in.rows_per_column,
        is_active=room_in.is_active
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def get_classrooms(db: Session, active_only: bool = False) -> List[Classroom]:
    q = db.query(Classroom).options(joinedload(Classroom.floor)).order_by(Classroom.name)
    if active_only:
        q = q.filter(Classroom.is_active == True)
    return q.all()

def get_classroom_by_id(db: Session, classroom_id: int) -> Optional[Classroom]:
    return db.query(Classroom).filter(Classroom.id == classroom_id).first()

def update_classroom(db: Session, classroom_id: int, update_data: ClassroomUpdate) -> Optional[Classroom]:
    room = get_classroom_by_id(db, classroom_id)
    if not room:
        return None
    if update_data.rows_per_column is not None:
        room.rows_per_column = update_data.rows_per_column
    if update_data.is_active is not None:
        room.is_active = update_data.is_active
    db.commit()
    db.refresh(room)
    return room

def get_students(db: Session, skip: int = 0, limit: int = 2000) -> List[Student]:
    return db.query(Student).order_by(Student.register_no).offset(skip).limit(limit).all()

def get_total_students_count(db: Session) -> int:
    return db.query(func.count(Student.id)).scalar() or 0

def get_student_by_register_no(db: Session, register_no: str) -> Optional[Student]:
    return db.query(Student).filter(Student.register_no == register_no).first()

def search_student(db: Session, query: str, exam_id: Optional[int] = None) -> List[Tuple[Student, Optional[Allocation]]]:
    clean_query = query.strip()
    if not clean_query:
        return []
    
    # Exact 16 digits match or partial match (e.g. last 3-4 digits or contains)
    stmt = db.query(Student).filter(
        or_(
            Student.register_no == clean_query,
            Student.register_no.like(f"%{clean_query}%"),
            Student.name.ilike(f"%{clean_query}%")
        )
    ).limit(25)
    
    students = stmt.all()
    results = []
    for s in students:
        alloc_query = db.query(Allocation).options(
            joinedload(Allocation.classroom).joinedload(Classroom.floor),
            joinedload(Allocation.exam)
        ).filter(Allocation.student_id == s.id)
        
        if exam_id:
            alloc_query = alloc_query.filter(Allocation.exam_id == exam_id)
        else:
            alloc_query = alloc_query.order_by(Allocation.id.desc())
            
        alloc = alloc_query.first()
        results.append((s, alloc))
    return results

def bulk_import_students(db: Session, students_data: List[StudentCreate]) -> int:
    # Filter out existing register numbers
    existing_reg_nos = set(
        r[0] for r in db.query(Student.register_no).all()
    )
    new_objs = []
    for s in students_data:
        if s.register_no not in existing_reg_nos:
            new_objs.append(
                Student(
                    register_no=s.register_no,
                    name=s.name,
                    branch=s.branch,
                    semester=s.semester,
                    subject_code=s.subject_code
                )
            )
            existing_reg_nos.add(s.register_no)
    
    if new_objs:
        db.add_all(new_objs)
        db.commit()
    return len(new_objs)

def clear_all_students(db: Session) -> int:
    count = db.query(Student).delete()
    db.commit()
    return count

def get_exams(db: Session) -> List[Exam]:
    return db.query(Exam).order_by(Exam.id.desc()).all()

def get_exam_by_id(db: Session, exam_id: int) -> Optional[Exam]:
    return db.query(Exam).filter(Exam.id == exam_id).first()

def get_latest_exam(db: Session) -> Optional[Exam]:
    return db.query(Exam).order_by(Exam.id.desc()).first()

def create_exam(db: Session, exam_data: ExamCreate) -> Exam:
    exam = Exam(
        name=exam_data.name,
        exam_date=exam_data.exam_date,
        session=exam_data.session,
        seed=exam_data.seed
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

def get_allocations_for_room(db: Session, exam_id: int, classroom_id: int) -> List[Allocation]:
    return db.query(Allocation).options(
        joinedload(Allocation.student),
        joinedload(Allocation.classroom).joinedload(Classroom.floor)
    ).filter(
        Allocation.exam_id == exam_id,
        Allocation.classroom_id == classroom_id
    ).order_by(Allocation.seat_label).all()

def get_all_allocations_for_exam(db: Session, exam_id: int) -> List[Allocation]:
    return db.query(Allocation).options(
        joinedload(Allocation.student),
        joinedload(Allocation.classroom).joinedload(Classroom.floor)
    ).filter(
        Allocation.exam_id == exam_id
    ).order_by(Allocation.classroom_id, Allocation.seat_label).all()

def get_dashboard_stats(db: Session) -> dict:
    total_students = get_total_students_count(db)
    active_rooms = db.query(Classroom).filter(Classroom.is_active == True).all()
    inactive_count = db.query(func.count(Classroom.id)).filter(Classroom.is_active == False).scalar() or 0
    total_capacity = sum(r.capacity for r in active_rooms)
    
    latest_exam = get_latest_exam(db)
    total_allocated = 0
    active_exam_id = None
    active_exam_name = None
    active_exam_date = None
    active_exam_session = None
    
    if latest_exam:
        active_exam_id = latest_exam.id
        active_exam_name = latest_exam.name
        active_exam_date = latest_exam.exam_date
        active_exam_session = latest_exam.session
        total_allocated = db.query(func.count(Allocation.id)).filter(
            Allocation.exam_id == latest_exam.id
        ).scalar() or 0

    total_unallocated = max(0, total_students - total_allocated)

    return {
        "total_students": total_students,
        "total_active_rooms": len(active_rooms),
        "total_inactive_rooms": inactive_count,
        "total_capacity": total_capacity,
        "total_allocated": total_allocated,
        "total_unallocated": total_unallocated,
        "active_exam_id": active_exam_id,
        "active_exam_name": active_exam_name,
        "active_exam_date": active_exam_date,
        "active_exam_session": active_exam_session,
    }
