"""
Copy all application data from the local SQLite database into PostgreSQL.

The target must be the database in DATABASE_URL (PostgreSQL). The SQLite file
is left untouched and remains usable as an emergency fallback.

Usage:
  python backend/scripts/migrate_sqlite_to_postgres.py           # abort if target already has data
  python backend/scripts/migrate_sqlite_to_postgres.py --force   # wipe target app tables first, then copy
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import MetaData, create_engine, inspect, select, text

from backend.app.config import DATABASE_URL, BASE_DIR

SOURCE_SQLITE = BASE_DIR / "exam_seating.db"

# Parent tables before children (PostgreSQL checks FKs immediately)
TABLE_ORDER = [
    "floors",
    "classrooms",
    "students",
    "exams",
    "faculty_users",
    "allocations",
]


def convert_value(column, value):
    if value is None:
        return None
    from sqlalchemy import Boolean, DateTime

    if isinstance(column.type, Boolean) and not isinstance(value, bool):
        return bool(value)
    if isinstance(column.type, DateTime) and isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy SQLite data into PostgreSQL")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Truncate target application tables before copying",
    )
    args = parser.parse_args()

    if not SOURCE_SQLITE.exists():
        raise SystemExit(f"Source SQLite database not found: {SOURCE_SQLITE}")
    if not DATABASE_URL.startswith("postgresql"):
        raise SystemExit(
            f"DATABASE_URL must point at PostgreSQL (got: {DATABASE_URL.split('@')[-1]})"
        )

    src_engine = create_engine(f"sqlite:///{SOURCE_SQLITE.as_posix()}")
    dst_engine = create_engine(DATABASE_URL)

    src_meta = MetaData()
    src_meta.reflect(bind=src_engine)

    missing = [t for t in TABLE_ORDER if t not in src_meta.tables]
    if missing:
        raise SystemExit(f"Source database is missing tables: {missing}")

    with src_engine.connect() as src_conn, dst_engine.begin() as dst_conn:
        target_tables = set(inspect(dst_conn).get_table_names())
        absent = [t for t in TABLE_ORDER if t not in target_tables]
        if absent:
            raise SystemExit(
                f"Target PostgreSQL schema is incomplete (missing {absent}). "
                "Run: alembic -c backend/alembic.ini upgrade head"
            )

        existing_students = dst_conn.execute(
            text("SELECT COUNT(*) FROM students")
        ).scalar()
        if existing_students and not args.force:
            raise SystemExit(
                f"Target already contains {existing_students} students. "
                "Re-run with --force to wipe and replace."
            )

        if args.force:
            dst_conn.execute(
                text(
                    "TRUNCATE allocations, faculty_users, exams, students, "
                    "classrooms, floors RESTART IDENTITY CASCADE"
                )
            )
            print("Target truncated (--force).")

        # The ACOE row seeded by migration 003 is replaced by the source row
        # (preserves any password change made before the migration).
        dst_conn.execute(text("DELETE FROM faculty_users"))

        summary = []
        for name in TABLE_ORDER:
            table = src_meta.tables[name]
            columns = list(table.columns)
            keys = [str(c.key) for c in columns]
            rows = [
                dict(
                    zip(
                        keys,
                        (
                            convert_value(c, v)
                            for c, v in zip(columns, tuple(row))
                        ),
                    )
                )
                for row in src_conn.execute(select(table))
            ]
            if rows:
                dst_conn.execute(table.insert(), rows)

            src_count = len(rows)
            dst_count = dst_conn.execute(
                text(f"SELECT COUNT(*) FROM {name}")
            ).scalar()
            summary.append((name, src_count, dst_count))

            # Explicit IDs above do not advance PostgreSQL sequences
            dst_conn.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {name}), 0) + 1, false)"
                )
            )

    print(f"{'table':<15} {'sqlite':>8} {'postgres':>9}")
    ok = True
    for name, src_count, dst_count in summary:
        flag = "" if src_count == dst_count else "   <-- MISMATCH"
        if src_count != dst_count:
            ok = False
        print(f"{name:<15} {src_count:>8} {dst_count:>9}{flag}")
    print("Migration OK." if ok else "Migration FAILED (count mismatch).")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
