"""Add student DOB (portal password) and faculty_users table

Revision ID: 003_add_auth
Revises: 002_remove_rbac
Create Date: 2026-10-09 00:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_add_auth'
down_revision: Union[str, None] = '002_remove_rbac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. students.dob — date of birth in DD/MM/YYYY, used as the student portal password
    student_cols = [c["name"] for c in inspector.get_columns("students")]
    if "dob" not in student_cols:
        op.add_column("students", sa.Column("dob", sa.String(length=10), nullable=True))

    # 2. faculty_users table for staff logins
    if "faculty_users" not in inspector.get_table_names():
        op.create_table(
            "faculty_users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=120), nullable=False),
            sa.Column("name", sa.String(length=150), nullable=True),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_faculty_users_id", "faculty_users", ["id"], unique=False)
        op.create_index("ix_faculty_users_email", "faculty_users", ["email"], unique=True)

    # 3. Seed the default ACOE account if missing
    from backend.app.security import (
        DEFAULT_FACULTY_EMAIL,
        DEFAULT_FACULTY_PASSWORD,
        hash_password,
    )

    existing = bind.execute(
        sa.text("SELECT id FROM faculty_users WHERE email = :email"),
        {"email": DEFAULT_FACULTY_EMAIL},
    ).fetchone()
    if existing is None:
        bind.execute(
            sa.text(
                "INSERT INTO faculty_users (email, name, hashed_password, must_change_password, is_active) "
                "VALUES (:email, :name, :pwd, 1, 1)"
            ),
            {
                "email": DEFAULT_FACULTY_EMAIL,
                "name": "ACOE - Controller of Examinations",
                "pwd": hash_password(DEFAULT_FACULTY_PASSWORD),
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "faculty_users" in inspector.get_table_names():
        op.drop_index("ix_faculty_users_email", table_name="faculty_users")
        op.drop_index("ix_faculty_users_id", table_name="faculty_users")
        op.drop_table("faculty_users")

    student_cols = [c["name"] for c in inspector.get_columns("students")]
    if "dob" in student_cols:
        op.drop_column("students", "dob")
