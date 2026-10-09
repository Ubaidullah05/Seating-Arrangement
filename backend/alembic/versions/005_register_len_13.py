"""Allow 13- or 16-digit register numbers (was 12 or 16)

Revision ID: 005_register_len_13
Revises: 004_register_len
Create Date: 2026-10-09 00:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_register_len_13'
down_revision: Union[str, None] = '004_register_len'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_CLAUSE = "length(register_no) IN (12, 16)"
NEW_CLAUSE = "length(register_no) IN (13, 16)"
OLD_NAME = "check_register_no_len"
LEGACY_NAME = "check_register_no_16_digits"
NEW_NAME = "check_register_no_len"


def _sqlite_rebuild(bind, old_clause: str, new_clause: str) -> None:
    """SQLite cannot ALTER a CHECK constraint — rebuild the students table.

    Only runs when the source table actually contains the old clause.
    Foreign-key enforcement is off by default in SQLite (SQLAlchemy does not
    enable it), so dropping/renaming the table is safe here.
    """
    row = bind.execute(
        sa.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
    ).fetchone()
    if row is None or not row[0] or old_clause not in row[0]:
        return

    table_sql = row[0]
    index_rows = bind.execute(
        sa.text(
            "SELECT sql FROM sqlite_master WHERE type='index' "
            "AND tbl_name='students' AND sql IS NOT NULL"
        )
    ).fetchall()
    columns = [
        r[1]
        for r in bind.execute(sa.text("PRAGMA table_info(students)")).fetchall()
    ]

    new_table_sql = table_sql.replace("students", "students_new", 1).replace(
        old_clause, new_clause
    )
    bind.execute(sa.text(new_table_sql))
    col_list = ", ".join(f'"{c}"' for c in columns)
    bind.execute(
        sa.text(f"INSERT INTO students_new ({col_list}) SELECT {col_list} FROM students")
    )
    bind.execute(sa.text("DROP TABLE students"))
    bind.execute(sa.text('ALTER TABLE students_new RENAME TO "students"'))
    for (idx_sql,) in index_rows:
        bind.execute(sa.text(idx_sql))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(f"ALTER TABLE students DROP CONSTRAINT IF EXISTS {OLD_NAME}")
        op.execute(f"ALTER TABLE students DROP CONSTRAINT IF EXISTS {LEGACY_NAME}")
        op.execute(f"ALTER TABLE students ADD CONSTRAINT {NEW_NAME} CHECK ({NEW_CLAUSE})")
    elif bind.dialect.name == "sqlite":
        _sqlite_rebuild(bind, OLD_CLAUSE, NEW_CLAUSE)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(f"ALTER TABLE students DROP CONSTRAINT IF EXISTS {NEW_NAME}")
        op.execute(f"ALTER TABLE students ADD CONSTRAINT {OLD_NAME} CHECK ({OLD_CLAUSE})")
    elif bind.dialect.name == "sqlite":
        _sqlite_rebuild(bind, NEW_CLAUSE, OLD_CLAUSE)
