"""
Backfill / correct student date-of-birth values (the student portal password).

DOBs must be strict DD/MM/YYYY. Examples:

  # Fill only students that have no DOB yet (safe, re-runnable)
  python backend/scripts/backfill_dob.py

  # Regenerate the sample DOBs over existing values (resets to samples)
  python backend/scripts/backfill_dob.py --overwrite

  # Apply real DOBs from a CSV (register_no,date_of_birth columns)
  python backend/scripts/backfill_dob.py --input real_dobs.csv
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text

from backend.app.config import DATABASE_URL
from backend.app.security import is_strict_ddmmyyyy

# The 10 register numbers shipped in the Excel template, with their sample DOBs
TEMPLATE_DOBS = {
    "2403310910421001": "15/08/2005",
    "2403310910421002": "02/11/2005",
    "2403310910421003": "27/01/2005",
    "2403310910421004": "09/03/2005",
    "2403310910421005": "21/07/2005",
    "2403310910421006": "30/12/2004",
    "2403310910421007": "14/06/2005",
    "2403310910421008": "05/09/2005",
    "2403310910421009": "18/02/2005",
    "2403310910421010": "23/10/2004",
}


def sample_dob(register_no: str) -> str:
    """Deterministic sample DOB derived from the register number.

    Same register always maps to the same date; always a real calendar date
    between 2004-2006 (day is capped at 28 so every month is valid).
    """
    if register_no in TEMPLATE_DOBS:
        return TEMPLATE_DOBS[register_no]
    digits = register_no[-8:] if len(register_no) >= 8 else register_no.zfill(8)
    n = int(digits)
    year = 2004 + (n // 13) % 3
    month = (n // 7) % 12 + 1
    day = n % 28 + 1
    return f"{day:02d}/{month:02d}/{year:04d}"


def load_real_dobs(csv_path: Path) -> dict:
    """Read a CSV/TSV with register number + DOB columns into {register: dob}."""
    register_keys = {"register number", "register_no", "reg no", "regno", "register"}
    dob_keys = {"date of birth", "dob", "birth date", "date_of_birth"}

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        if not reader.fieldnames:
            raise SystemExit(f"CSV has no header row: {csv_path}")

        norm = {str(h).strip().lower(): h for h in reader.fieldnames if h}
        reg_col = next((norm[k] for k in norm if k in register_keys), None)
        dob_col = next((norm[k] for k in norm if k in dob_keys), None)
        if reg_col is None or dob_col is None:
            raise SystemExit(
                f"CSV must have register number and date of birth columns. Found: {list(reader.fieldnames)}"
            )

        mapping = {}
        for idx, row in enumerate(reader, start=2):
            reg = str(row.get(reg_col) or "").strip().lstrip("'")
            dob = str(row.get(dob_col) or "").strip()
            if not reg:
                continue
            if not is_strict_ddmmyyyy(dob):
                raise SystemExit(
                    f"Row {idx}: DOB '{dob}' for register {reg} is not a valid DD/MM/YYYY date."
                )
            mapping[reg] = dob
        return mapping


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill student DOBs (portal passwords)")
    parser.add_argument("--input", type=Path, help="CSV with real DOBs (register_no,date_of_birth)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate sample DOBs even where a DOB already exists (ignored with --input)",
    )
    args = parser.parse_args()

    real_dobs = load_real_dobs(args.input) if args.input else None

    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, register_no, dob FROM students ORDER BY register_no")
        ).fetchall()

        filled = 0
        overwritten = 0
        skipped = 0
        missing_regs = set(real_dobs) if real_dobs else set()

        for sid, reg, current_dob in rows:
            if real_dobs is not None:
                new_dob = real_dobs.get(reg)
                if new_dob is None:
                    skipped += 1
                    continue
                missing_regs.discard(reg)
                if new_dob == current_dob:
                    skipped += 1
                    continue
                conn.execute(
                    text("UPDATE students SET dob = :dob WHERE id = :id"),
                    {"dob": new_dob, "id": sid},
                )
                overwritten += 1
            else:
                if current_dob and not args.overwrite:
                    skipped += 1
                    continue
                new_dob = sample_dob(reg)
                if new_dob == current_dob:
                    skipped += 1
                    continue
                conn.execute(
                    text("UPDATE students SET dob = :dob WHERE id = :id"),
                    {"dob": new_dob, "id": sid},
                )
                if current_dob:
                    overwritten += 1
                else:
                    filled += 1

        remaining_null = conn.execute(
            text("SELECT COUNT(*) FROM students WHERE dob IS NULL OR dob = ''")
        ).scalar()

    print(f"Students updated: {filled} filled (were empty), {overwritten} overwritten, {skipped} skipped")
    print(f"Students still without a DOB: {remaining_null}")
    if real_dobs and missing_regs:
        print(f"WARNING: {len(missing_regs)} register number(s) from the CSV not found in DB: {sorted(missing_regs)[:10]}")


if __name__ == "__main__":
    main()
