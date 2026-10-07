"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-07 22:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Students Table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('register_no', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=True),
        sa.Column('branch', sa.String(length=100), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('subject_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("length(register_no) = 16", name='check_register_no_16_digits'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('register_no')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    op.create_index(op.f('ix_students_register_no'), 'students', ['register_no'], unique=True)
    op.create_index(op.f('ix_students_branch'), 'students', ['branch'], unique=False)

    # 2. Floors Table
    op.create_table(
        'floors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('floor_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('floor_number')
    )
    op.create_index(op.f('ix_floors_id'), 'floors', ['id'], unique=False)

    # 3. Classrooms Table
    op.create_table(
        'classrooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('floor_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('columns', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('rows_per_column', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['floor_id'], ['floors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_classrooms_id'), 'classrooms', ['id'], unique=False)
    op.create_index(op.f('ix_classrooms_name'), 'classrooms', ['name'], unique=True)
    op.create_index(op.f('ix_classrooms_floor_id'), 'classrooms', ['floor_id'], unique=False)

    # 4. Exams Table
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('exam_date', sa.String(length=50), nullable=False),
        sa.Column('session', sa.String(length=10), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exams_id'), 'exams', ['id'], unique=False)

    # 5. Allocations Table
    op.create_table(
        'allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('seat_label', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'student_id', name='uq_exam_student'),
        sa.UniqueConstraint('exam_id', 'classroom_id', 'seat_label', name='uq_exam_classroom_seat')
    )
    op.create_index(op.f('ix_allocations_id'), 'allocations', ['id'], unique=False)
    op.create_index('idx_alloc_exam_classroom', 'allocations', ['exam_id', 'classroom_id'], unique=False)


def downgrade() -> None:
    op.drop_table('allocations')
    op.drop_table('exams')
    op.drop_table('classrooms')
    op.drop_table('floors')
    op.drop_table('students')
