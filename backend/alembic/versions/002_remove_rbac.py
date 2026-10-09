"""Remove RBAC leftovers and enforce exam date/session uniqueness

Revision ID: 002_remove_rbac
Revises: 001_initial_schema
Create Date: 2026-10-09 00:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_remove_rbac'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Drop leftover faculty_users table from removed RBAC feature
    if "faculty_users" in inspector.get_table_names():
        op.drop_index("ix_faculty_users_email", table_name="faculty_users", if_exists=True)
        op.drop_index("ix_faculty_users_id", table_name="faculty_users", if_exists=True)
        op.drop_table("faculty_users")

    # 2. Drop leftover students.dob column from removed RBAC feature
    student_cols = [c["name"] for c in inspector.get_columns("students")]
    if "dob" in student_cols:
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("students") as batch_op:
                batch_op.drop_column("dob")
        else:
            op.drop_column("students", "dob")

    # 3. Remove duplicate exams (keep lowest id per date+session)
    exams = bind.execute(
        sa.text("SELECT id, exam_date, session FROM exams ORDER BY id")
    ).fetchall()
    seen = {}
    drop_ids = []
    for eid, exam_date, session in exams:
        key = (exam_date, session)
        if key in seen:
            drop_ids.append(eid)
        else:
            seen[key] = eid
    for eid in drop_ids:
        bind.execute(sa.text("DELETE FROM allocations WHERE exam_id = :id"), {"id": eid})
        bind.execute(sa.text("DELETE FROM exams WHERE id = :id"), {"id": eid})

    # 4. Restore any classroom whose rows_per_column is below allocated seat rows.
    #    (GLOB is SQLite-only syntax — skip on PostgreSQL, where data is loaded
    #     separately from an already-repaired SQLite source.)
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("""
        UPDATE classrooms
        SET rows_per_column = (
            SELECT MAX(CAST(SUBSTR(a.seat_label, 2) AS INTEGER))
            FROM allocations a
            WHERE a.classroom_id = classrooms.id
              AND a.seat_label GLOB '[A-D][0-9]*'
        )
        WHERE EXISTS (
            SELECT 1 FROM allocations a
            WHERE a.classroom_id = classrooms.id
              AND CAST(SUBSTR(a.seat_label, 2) AS INTEGER) > classrooms.rows_per_column
        )
        AND (
            SELECT MAX(CAST(SUBSTR(a.seat_label, 2) AS INTEGER))
            FROM allocations a
            WHERE a.classroom_id = classrooms.id
              AND a.seat_label GLOB '[A-D][0-9]*'
        ) BETWEEN 1 AND 8
    """))

    # 5. Enforce unique (exam_date, session) matching models.Exam
    existing_unique = False
    for idx in inspector.get_indexes("exams"):
        if idx.get("unique") and set(idx.get("column_names", [])) == {"exam_date", "session"}:
            existing_unique = True
            break
    if not existing_unique:
        if bind.dialect.name == "sqlite":
            op.create_table(
                "exams_uq_tmp",
                sa.Column("id", sa.Integer(), nullable=False),
                sa.Column("name", sa.String(length=150), nullable=False),
                sa.Column("exam_date", sa.String(length=50), nullable=False),
                sa.Column("session", sa.String(length=10), nullable=False),
                sa.Column("seed", sa.Integer(), nullable=True),
                sa.Column("created_at", sa.DateTime(), nullable=True),
                sa.PrimaryKeyConstraint("id"),
                sa.UniqueConstraint("exam_date", "session", name="uq_exam_date_session"),
            )
            bind.execute(sa.text("""
                INSERT INTO exams_uq_tmp (id, name, exam_date, session, seed, created_at)
                SELECT id, name, exam_date, session, seed, created_at FROM exams
            """))
            op.drop_table("exams")
            op.rename_table("exams_uq_tmp", "exams")
            op.create_index("ix_exams_id", "exams", ["id"], unique=False)
        else:
            op.create_unique_constraint("uq_exam_date_session", "exams", ["exam_date", "session"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Re-add dob column
    student_cols = [c["name"] for c in inspector.get_columns("students")]
    if "dob" not in student_cols:
        op.add_column("students", sa.Column("dob", sa.String(length=10), nullable=True))

    # Re-create faculty_users
    if "faculty_users" not in inspector.get_table_names():
        op.create_table(
            "faculty_users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=120), nullable=False),
            sa.Column("name", sa.String(length=150), nullable=True),
            sa.Column("department", sa.String(length=100), nullable=True),
            sa.Column("role", sa.String(length=20), nullable=False, server_default="faculty"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_faculty_users_id", "faculty_users", ["id"], unique=False)
        op.create_index("ix_faculty_users_email", "faculty_users", ["email"], unique=True)

    # Drop unique constraint on exams if present
    for idx in inspector.get_indexes("exams"):
        if idx.get("unique") and set(idx.get("column_names", [])) == {"exam_date", "session"}:
            op.drop_index(idx["name"], table_name="exams")
            break
