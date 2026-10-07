import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    register_no = Column(String(16), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=True)
    branch = Column(String(100), nullable=True, index=True)
    semester = Column(Integer, nullable=True)
    subject_code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    allocations = relationship("Allocation", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "length(register_no) = 16",
            name="check_register_no_16_digits"
        ),
    )


class Floor(Base):
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False) # e.g. "Ground Floor", "First Floor", "Second Floor", "Third Floor"
    floor_number = Column(Integer, nullable=False, unique=True) # 0, 1, 2, 3
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classrooms = relationship("Classroom", back_populates="floor", cascade="all, delete-orphan", order_by="Classroom.name")


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True) # e.g. M001..M008, M101..M108
    columns = Column(Integer, default=4, nullable=False) # Always 4 (A, B, C, D)
    rows_per_column = Column(Integer, default=7, nullable=False) # 6 or 7 rows
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    floor = relationship("Floor", back_populates="classrooms")
    allocations = relationship("Allocation", back_populates="classroom", cascade="all, delete-orphan")

    @property
    def capacity(self) -> int:
        return self.columns * self.rows_per_column


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False) # "END SEMESTER EXAMINATIONS - OCT/NOV 2026"
    exam_date = Column(String(50), nullable=False) # "2026-10-15"
    session = Column(String(10), nullable=False) # "FN" or "AN"
    seed = Column(Integer, nullable=True) # Random seed for reproducibility
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    allocations = relationship("Allocation", back_populates="exam", cascade="all, delete-orphan")


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_label = Column(String(10), nullable=False) # e.g. "A1", "B4", "D7"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exam = relationship("Exam", back_populates="allocations")
    student = relationship("Student", back_populates="allocations")
    classroom = relationship("Classroom", back_populates="allocations")

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_student"),
        UniqueConstraint("exam_id", "classroom_id", "seat_label", name="uq_exam_classroom_seat"),
        Index("idx_alloc_exam_classroom", "exam_id", "classroom_id"),
    )
