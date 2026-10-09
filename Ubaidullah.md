# Ubaidullah.md — Change Log

Track of all changes made to the Exam Seating Planner (Jerusalem College of Engineering — Office of the Controller of Examinations).

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

### How to test manually

1. **Faculty:** open `/login` → *Faculty & Staff* tab → `acoe@jerusalemengg.ac.in` / `acoe@123` → you are prompted (amber *Set Password* button) to change the password.
2. **Student:** all 160 students already have sample DOBs (backfilled) — `/login` → *Student* tab → e.g. `2403310910421001` + `15/08/2005` → shows only their exam hall/seat. When real dates arrive, re-upload the register with the Date of Birth column (existing DOBs are overwritten) or run `backend/scripts/backfill_dob.py --input real_dobs.csv`.
3. Try a wrong DOB format (`2005-08-15`, `15-08-2005`) or a non-institutional email — both are rejected.
