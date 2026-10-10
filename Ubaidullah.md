# Ubaidullah.md — Change Log

Track of all changes made to the Exam Seating Planner (Jerusalem College of Engineering — Office of the Controller of Examinations).

---

## 2026-10-10 — Deploy Fix: Automatic Room Seeding & New Hall VH3

### Overview

The first Vercel + Neon deployment came up with **empty floors/classrooms** (faculty login and student upload worked — they only touch `faculty_users`/`students` — but the Rooms page showed nothing and generating a plan for the 510 uploaded students failed with *insufficient seating capacity*). Root cause: a fresh database only ever receives `create_all` + the faculty bootstrap at startup — **nothing seeded the rooms**. Fixed with startup self-seeding plus the requested **VH3** hall.

### 1. Diagnosis (deployed site)

| Observation | Meaning |
|---|---|
| Faculty login works on the live site | Backend function + `DATABASE_URL` reach Neon; ACOE account is auto-bootstrapped at import |
| 510 students import fine | `students` table works |
| Rooms page empty, generate → *insufficient seating capacity* | `floors`/`classrooms` tables were **empty** — never seeded (local rooms came from a one-time historical seed, not from app startup) |

### 2. Fix — startup room self-seed

| Item | Details |
|---|---|
| New `backend/app/room_seed.py` | `FLOORS_SPEC` (single source of truth: 6 floors, **33 rooms** × 4 cols × 7 rows = **924 seats**) + `ensure_rooms(db)` — creates only *missing* floors/rooms, never touches students/exams/allocations, never edits existing rows, one transaction (all-or-nothing), idempotent |
| `backend/app/main.py` | Runs `ensure_rooms` at import after `create_all`, before faculty bootstrap — a **fresh database self-heals on first cold start** (guarded by try/except; unique keys on `floor_number`/`name` make concurrent cold starts safe) |
| `backend/seed_data.py` | Now imports `FLOORS_SPEC` / `ROOM_COLUMNS` / `ROOM_ROWS_PER_COLUMN` instead of duplicating the layout (its destructive demo-student path is untouched and was **not** used for the deploy — it would wipe live students) |

### 3. New hall VH3

- Spec now `(5, "VH", ["VH1", "VH2", "VH3"])` → **VH floor has VH1, VH2, VH3** (each 4×7, 28 seats).
- Inserted into the local **PostgreSQL** and the **SQLite backup** (both now: 6 floors, 33 rooms — the `924 students = 33 classrooms x 28` comment in `seed_data.py` is now actually true).
- Totals: **33 rooms / 924 seats** → the 510-student deploy fits with room to spare.

### 4. Testing (this round)

| Check | Result |
|---|---|
| `backend` → `pytest` | **62 passed** (59 old + 3 new in `tests/test_room_seed.py`: full-spec creation incl. VH3, idempotency + student rows untouched, missing-only fill with existing rows never edited) |
| Local API | `GET /api/v1/classrooms/floors` → 6 floors; `floor 5 VH: VH1,VH2,VH3` |
| Deploy path | Importing `backend.app.main` (what Vercel's function does) already self-seeded the local PG — same code path runs on Neon at next deploy/cold start |

> The deployed Neon DB needs **no manual migration** — the pushed startup seed creates the floors/rooms (and VH3) on the function's next cold start after Vercel finishes the redeploy.

---

## 2026-10-09 (later) — PostgreSQL, Required DOB Uploads, 13/16-Digit Registers & New Halls

### Overview

The whole database moved from SQLite to **PostgreSQL**, uploads now **require a DOB** (the student's portal password) with two downloadable templates, register numbers accept **13 or 16 digits**, and three new exam halls (**LS1, VH1, VH2**) were added on dedicated LS/VH floors.

---

### 1. PostgreSQL (primary database)

| Item | Details |
|---|---|
| Database | `exam_seating_db` on `localhost:5432` (user `postgres`, password `postgres`, driver `psycopg`) |
| Config | `backend/.env` + root `.env` → `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/exam_seating_db` (files stay gitignored) |
| Fallback | `database.py` still falls back to the local SQLite file if PostgreSQL is unreachable — SQLite (`backend/exam_seating.db`) is kept as an untouched backup/source |
| Migration chain | `001 → 002 → 003 → 004` run against PostgreSQL; head = `004_register_len` |
| Fixes applied for PG | `002_remove_rbac` step 4 (SQLite-only `GLOB` SQL) now dialect-gated; `003_add_auth` ACOE seed uses `TRUE` booleans (PG rejects integer→boolean) |
| New migration | `backend/alembic/versions/004_register_len.py` — drops `check_register_no_16_digits`, adds `check_register_no_len CHECK (length(register_no) IN (12, 16))` (SQLite branch rebuilds the table only if the old check exists) |
| New migration | `backend/alembic/versions/005_register_len_13.py` — tightens the check to **`IN (13, 16)`** (12-digit registers later disallowed at the user's request); PG drop/re-add, SQLite rebuild-if-present |
| Data copy | New `backend/scripts/migrate_sqlite_to_postgres.py` — copies floors(4), classrooms, students(160), exams(1), faculty_users(1), allocations(160) with preserved IDs, bumps PG sequences, verifies counts; `--force` to wipe+redo |
| Verified | Counts match SQLite; sequences correct; all logins served from PG; after `005`: 13-digit insert accepted / 14-digit `CheckViolation` rejected |

```bash
# Re-run data copy (aborts if target already has students; --force to wipe first)
backend\venv\Scripts\python.exe backend\scripts\migrate_sqlite_to_postgres.py
```

> Note: the server must be **stopped** during `alembic upgrade` + data copy, then restarted — a `uvicorn --reload` worker respawning mid-migration will auto-`create_all` on startup and race the migrations.

---

### 2. Upload section — DOB required + two template buttons

**Backend (`backend/app/routers/students.py`)**

- Missing **Date of Birth** column in an uploaded file → **400** with an explanatory message (previously the file was accepted without DOBs).
- A row with a blank DOB cell → **invalid row** (`Date of birth is required — it is the student's portal login password…`). Format rules unchanged: strict `DD/MM/YYYY` + real calendar date.
- Existing register **with** a DOB in the file → still valid (overwrites stored DOB); existing register without a DOB in the file → duplicate (as before).
- New endpoint **`GET /api/v1/students/dob-template`** → `dob_template.xlsx` — exactly **two columns: Register Number (Text-formatted) + Date of Birth**, with header comments and two harmless sample rows.

**Frontend (`frontend/src/pages/UploadPage.tsx`, `frontend/src/api/client.ts`)**

- Columns-guide table gained a **Date of Birth — REQUIRED (*)** row (aliases, `DD/MM/YYYY` rule, login-password explanation).
- Valid-preview table now shows a **Date of Birth** column.
- Two new buttons in the template card: **⬇ DOB Template** (2-column file) and **⬇ Full Template** (all columns) — the latter wires the previously unused `/students/template` download. Failures surface in the status banner instead of failing silently.
- The **full template now starts with an `S.no` column** (serial number for the coordinator's reference, auto-numbered 1–10 on the sample rows). The upload parser ignores it entirely (unknown headers are skipped), the guidelines sheet and the UploadPage columns guide both document it as *Ignored*, and the Excel advisory now correctly says register numbers live in **Column B**.

---

### 3. Register numbers accept 13 or 16 digits (exactly; 12, 14, 15 rejected)

| Layer | Change |
|---|---|
| `backend/app/security.py` | `REGISTER_NO_RE = ^(?:\d{13}|\d{16})$` |
| `backend/app/schemas.py` | Pydantic validator + field descriptions |
| `backend/app/routers/students.py` | Upload preview check + error text (`Must be exactly 13 or 16 numeric digits…`) |
| `backend/app/routers/auth.py` | Login rejection message |
| `backend/app/models.py` + migrations `004`/`005` | DB CHECK `length(register_no) IN (13, 16)` (PG + SQLite branches) |
| `backend/app/template_generator.py` | Template header comments, guidelines and advisory text |
| `LoginPage.tsx` | Client regex + error message (input still capped at 16) |
| `UploadPage.tsx` | Guide/advisory/badges/loading copy → "13 or 16 digits" |
| `DashboardPage` / `SearchPage` / `SeatingPlansPage` / `types` | Labels & hints updated |

Search (exact + suffix matching), exports, allocation, backfill script and seed data already treat registers as generic strings — no changes needed.

---

### 4. New exam halls — LS1, VH1, VH2

- Added as **three separate classrooms** on dedicated floors (same structure `seed_data.py` already modelled):
  - Floor **LS** (floor_number 4) → **LS1**
  - Floor **VH** (floor_number 5) → **VH1**, **VH2**
- Each: **4 columns × 7 rows = seats A1–D7, capacity 28**, active — identical to the M-series halls.
- Inserted into **both** PostgreSQL (primary) and the SQLite backup file; `seed_data.py` spec aligned (`LS1` / `VH1` / `VH2`, dropped the old hyphenated `LS-1`/`VH-1`/`VH-3` names).
- Classroom count: **29 → 32**. New halls participate in allocation automatically (ordered after the M-series rooms).

---

### 5. Examination date format — DD-MM-YYYY

Exam dates changed from ISO `YYYY-MM-DD` to **`DD-MM-YYYY`** (e.g. `15-10-2026`) end-to-end — the value is stored as-is in `exams.exam_date` (string column) and displayed unchanged everywhere.

| Layer | Change |
|---|---|
| `backend/app/schemas.py` | `_validate_exam_date_format()` — strict `DD-MM-YYYY` + real calendar date; applied to `ExamBase` (create/response) and `GenerateAllocationRequest` (default `15-10-2026`). Old ISO dates, slashes, single-digit parts, `32-10-2026`, `31-02-2026` etc. → **422** with a clear message |
| Existing data | All exam rows converted in **both** databases (`2026-10-15` → `15-10-2026`, etc.) |
| `GeneratePage.tsx` | Native date picker replaced with a **DD-MM-YYYY text input** (mono font, placeholder, helper line) + client-side format/calendar validation before submit |
| `StudentPortalPage.tsx` | `formatExamDate()` now parses `DD-MM-YYYY` (was `YYYY-MM-DD`) |
| `DashboardPage.tsx` | Fallback date placeholder updated |
| Display & exports | Dashboard, Seating Plans list/summary, student portal, PDF/XLSX notice-board & seating headers, and download filenames pick up the new format automatically (they echo `exam.exam_date`) |

Ordering/exams lists sort by `id`, never by the date string, so the non-sortable format is safe. Duplicate detection (`exam_date` + `session`) keeps working since both sides use the same canonical format.

---

### 6. Testing (this round)

| Suite | Result |
|---|---|
| Backend unit/API tests (`pytest`) | **59 passed** — includes new/updated tests: 13-digit schema accept + 12/14/15-digit reject, DOB column required (400), blank-DOB invalid, 13-digit upload end-to-end, DOB-template download shape, DOB overwrite/invalid-format, backfill determinism, exam-date `DD-MM-YYYY` accept + 8 rejected bad formats (ISO, slashes, short parts, impossible dates) |
| Live E2E on PostgreSQL (`e2e_pg.py` + follow-ups) | **21/21 passed** — faculty + student logins, 3 bad DOB formats rejected, both template downloads (2-column shape verified), missing-DOB 400, upload→commit→login→cleanup round-trip, overwrite-path valid, LS1/VH1/VH2 + LS/VH floors via API, 401/403 guards; exam-date round: exams/dashboard return `DD-MM-YYYY`, ISO & impossible dates → **422**, valid `DD-MM-YYYY` passes schema validation; seats view + export (200, `…_15-10-2026.xlsx` filename) verified after regeneration; register-length round (post-`005`): 12-digit login → **400 "13 or 16"**, 13-digit login → 401 (format ok, unknown student), 14-digit → 400, 16-digit → 200, upload accepts 13 / rejects 12 & 14, PG CHECK: 13-digit insert OK, 14-digit `CheckViolation` |
| Frontend lint (`oxlint`) | **0 warnings, 0 errors** |
| Frontend build (`tsc -b && vite build`) | **Passes** |

> **Note — seating regenerated with new seeds (2026-10-09).** `allocations.student_id` has `ON DELETE CASCADE`, so a *Clear All Students* wiped all seating (re-importing students does not restore it). All exams were re-generated via reshuffle with **fresh random seeds** (`seed: null` → server auto-generates 6-digit seed): current state = **5 exams × 10 students = 50 allocations**, all in room M001 (10 students need only one room; first room fills first). The roster at review time was the 10 sample students (`2403310910421001`–`…1010`); restore the full 160-student file by re-uploading it and re-generating if needed.

---

## 2026-10-09 — RBAC Authentication, Student Exam-Hall Portal & Mobile-Friendly UI

### Overview

Role-based login (RBAC) was added to the portal with two roles — **Student** and **Faculty & Staff** — along with a student-facing exam-hall view, a redesigned login page, and full mobile responsiveness.

---

### 1. Authentication (Backend)

| Item | Details |
|---|---|
| New file | `backend/app/security.py` — PBKDF2-HMAC-SHA256 password hashing, HMAC-SHA256 signed session tokens (12 h TTL), strict credential format validators |
| New file | `backend/app/routers/auth.py` — all auth endpoints + ACOE bootstrap |
| New model | `FacultyUser` (`faculty_users` table) — email, hashed password, `must_change_password`, `is_active` |
| Re-added column | `students.dob` — date of birth in **strict DD/MM/YYYY**, used as the student's portal password |
| New migration | `backend/alembic/versions/003_add_auth.py` — adds `students.dob`, creates `faculty_users`, seeds the ACOE account |
| Schema self-heal | `backend/app/main.py` auto-adds `students.dob` on startup for older databases |

**Endpoints**

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/student/login` | Register number (exactly 16 digits) + DOB password (strict `DD/MM/YYYY` — any other format is rejected with 400) |
| POST | `/api/v1/auth/faculty/login` | Institutional email (must match `*@jerusalemengg.ac.in`, e.g. `acoe@jerusalemengg.ac.in`) + password (default `acoe@123`) |
| POST | `/api/v1/auth/faculty/change-password` | Faculty-only; verifies old password, requires ≥ 6 chars and different from old |
| GET | `/api/v1/auth/me` | Current session info (student or faculty) |
| GET | `/api/v1/auth/student/seats` | Student-only: lists **my** exam hall(s), floor, seat and exam details |

**Security rules enforced**

- Student DOB must be exactly `DD/MM/YYYY` (two-digit day/month, four-digit year, slashes, real calendar date). `YYYY-MM-DD`, `DD-MM-YYYY`, `MM/DD/YYYY`, `1/7/2005` etc. are all rejected.
- Faculty email must be in the institutional format `name@jerusalemengg.ac.in`; no other domains accepted.
- The student DOB (login password) is **never** returned by any API response (`StudentResponse` excludes `dob`).
- Passwords stored only as PBKDF2 hashes; sessions are signed tokens that expire after 12 hours.
- Default ACOE account is bootstrapped automatically on app startup (`acoe@jerusalemengg.ac.in` / `acoe@123`, flagged `must_change_password`).

---

### 2. Student Upload Template (DOB column)

- `backend/app/template_generator.py` — template now includes a **Date of Birth** column (F) with `DD/MM/YYYY` sample data, header comment, and a guidelines row.
- `backend/app/routers/students.py` — upload parsing accepts DOB (`date of birth`, `dob`, … synonyms); invalid DOB formats are reported per-row; a file that supplies a DOB for an existing register is **valid, not a duplicate** — the commit **overwrites** the stored DOB (fills blanks *and* corrects sample/real dates). Existing registers without a DOB in the file stay duplicates.
- `backend/app/crud.py` — `bulk_import_students` stores `dob`, fills blanks, and updates DOBs that changed.
- `backend/app/schemas.py` — `StudentBase.dob` validated strictly (`DD/MM/YYYY` + real date).

### 2a. DOB Backfill Script (sample DOBs)

New file: `backend/scripts/backfill_dob.py` — all **160 students now have a DOB** (previously 0), so students can sign in immediately.

```bash
# Fill only students with no DOB (safe, re-runnable)
backend\venv\Scripts\python.exe backend\scripts\backfill_dob.py

# Regenerate sample DOBs over existing values
backend\venv\Scripts\python.exe backend\scripts\backfill_dob.py --overwrite

# Apply real DOBs from a CSV (columns: register_no, date_of_birth)
backend\venv\Scripts\python.exe backend\scripts\backfill_dob.py --input real_dobs.csv
```

- The 10 template register numbers get their exact template DOBs (`2403310910421001` → `15/08/2005`, …); the other 150 get **deterministic** sample DOBs derived from the register number (valid calendar dates in 2004–2006, same input → same date).
- `--input` validates every date strictly (`DD/MM/YYYY`) and aborts on the first invalid one; it also reports CSV registers missing from the DB.
- Real data can also be loaded through the regular upload flow (the overwrite behavior in §2).

---

### 3. Login Page (Frontend) — matches the provided design

New file: `frontend/src/pages/LoginPage.tsx`

- Full-screen campus-blue background with the white card, gold top border, college crest, **"Jerusalem College of Engineering"** serif heading and **"SINGLE WINDOW PORTAL"** subtitle.
- Two tabs: **STUDENT** and **FACULTY & STAFF** (cream/gold active tab styling like the design).
- **Student tab:** Register Number (16 digits, digits-only input) + Date of Birth (`DD/MM/YYYY` placeholder) → Sign In.
- **Faculty tab:** Institutional Email + Password with show/hide eye toggle → Sign In.
- Client-side validation mirrors the server rules; clear error messages for wrong formats/credentials.
- Footer: © Jerusalem College of Engineering.

---

### 4. Student Portal — view only my exam hall

New file: `frontend/src/pages/StudentPortalPage.tsx`

- After student login, students land on **My Exam Hall** — nothing else.
- Shows per exam: exam name, date + session, **examination hall (room) name, floor and seat number**.
- Empty state when no allocation is published yet.
- Own compact header (logo, college name, Logout). No admin/faculty pages are reachable for student sessions (route guards return them to `/student`).

---

### 5. Faculty Portal Integration

- `frontend/src/App.tsx` — role-based routing: `/login` (public), `/student` (students only), all staff pages wrapped in a `FacultyLayout` guard (faculty only). Unauthenticated users are sent to `/login`.
- `frontend/src/components/TopHeader.tsx` — signed-in ACOE chip, **Change Password** button (plus an amber "Set Password" prompt while the default password is active) and **Logout**.
- New file: `frontend/src/components/ChangePasswordModal.tsx` — current/new/confirm password modal with validation and success feedback.
- Session stored in `localStorage`; expired/invalid tokens are cleared and the user is redirected to `/login` (`frontend/src/api/client.ts` attaches `Authorization: Bearer …` automatically).

---

### 6. Mobile-Friendly UI

`frontend/src/index.css` (new responsive section) + component updates:

- **Sidebar** becomes an off-canvas drawer (hamburger toggle + backdrop) below 900 px.
- **Top header** compacts to 60 px, hides subtitle lines, keeps icon actions.
- **Login page** adapts down to 480 px (smaller card/typography, comfortable touch targets).
- **Student portal** stacks hall cards; hall/seat values scale down; metadata wraps to one column on phones.
- Dashboard info grids collapse 4 → 2 → 1 columns; document cards use compact padding.

---

### 7. Testing

| Suite | Result |
|---|---|
| Backend unit/API tests (`pytest`, `backend/tests`) | **43 passed** — `tests/test_auth.py` (16 auth tests: strict DOB formats, email enforcement, login, `/me`, seats, access control, change-password) + `tests/test_upload_dob.py` (4: upload overwrite, no-DOB duplicate, invalid DOB rejection, backfill determinism) + existing suites |
| Live E2E smoke test against running server | **34/34 passed** (faculty login, format rejections, student login, seat view, 403/401 guards, password change + restore) |
| Frontend lint (`oxlint`) | **0 warnings, 0 errors** |
| Frontend build (`tsc -b && vite build`) | **Passes** |

Test infrastructure: `backend/tests/conftest.py` now owns a shared in-memory DB + `get_db` override so test modules no longer stomp each other.

---

### 8. Repo Hygiene (same session)

- Empty `.gitignore` replaced with a real one (`.env`, `__pycache__`, `venv`, `node_modules`, local `.db`, `.freebuff/`).
- Untracked machine-specific `.env`, `*.pyc`/`__pycache__` and `exam_seating.db` from git (files kept locally).
- `backend/.env` / root `.env` now use portable `sqlite:///exam_seating.db` instead of an absolute path from another machine; `config.py` resolves relative SQLite paths against the backend directory.
- Dead frontend files removed (`App.css`, unused icons/assets); dead backend imports cleaned up.

---

### How to test manually (current)

> Server must run against PostgreSQL: `backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` (confirm startup log shows the PG engine, no SQLite fallback).

1. **Faculty:** `/login` → *Faculty & Staff* tab → `acoe@jerusalemengg.ac.in` / `acoe@123` → amber *Set Password* prompt appears.
2. **Student (16-digit):** `/login` → *Student* tab → `2403310910421001` + `15/08/2005` → My Exam Hall with seat. Try wrong formats (`2005-08-15`, `15-08-2005`) or a 12-digit register — rejected with clear messages.
3. **Student (13-digit):** works the same way once a 13-digit register exists (upload one via the preview→commit flow; test round confirmed upload → login → logout end-to-end). 12- and 14-digit registers are rejected at login, upload and DB level.
4. **Upload page:** columns guide shows Date of Birth as **REQUIRED**; download both **DOB Template** and **Full Template** buttons (xlsx opens; DOB template has exactly 2 columns; full template starts with an ignored `S.no` column). Uploading a file *without* a DOB column → error; a row with blank DOB → invalid row with reason.
5. **Exam date:** Generate page → date field accepts **DD-MM-YYYY only** (e.g. `15-10-2026`) — `2026-10-15` or `31-02-2026` show a validation error; dashboard, Seating Plans list, student portal and export filenames all display `DD-MM-YYYY`.
6. **Rooms page:** `LS` floor has **LS1**, `VH` floor has **VH1/VH2** — each A1–D7 (28 seats); generate a seating plan and confirm new halls fill after the M-series rooms.
7. Backups: `backend/exam_seating.db` (SQLite) still holds the full pre-migration copy — untouched.
