# Exam Seating Planner — Jerusalem College of Engineering, Chennai
## Comprehensive Development & Change Log (`rasin.md`)

**Target Institution**: Jerusalem College of Engineering (Autonomous), Chennai - 600100  
**Department**: Office of the Controller of Examinations (COE)  
**Target Examination**: End Semester Examinations (OCT/NOV 2026)  
**Target Audience**: College Staff Only (Exam Coordinators & Invigilators). No authentication, no logins, no student-facing interface.

---

## 1. Executive Summary of Changes

A complete full-stack web application called **"Exam Seating Planner"** was designed and implemented to generate, balance, visualize, and export examination seating arrangements. The design precisely replicates the college's existing **"Single Window Portal"** (Office of the Controller of Examinations).

### Core Accomplishments
1. **Single Window Portal User Interface**:
   - Deep navy vertical gradient sidebar (`#004a99` to `#002f66`) with the serif header `"Single Window Portal"`, collapsible hamburger button, and gold active indicator border (`#b8892b`).
   - Top Header Bar with Jerusalem College of Engineering crest emblem on a white square badge, bold serif institution heading, Anna University affiliation line, gold COE title (`#e5a93c`), and static `"STAFF"` indicator.
   - Main content featuring a 2px blue underline title row, gold `"PRINT"` action button, and centered printable **Official Document Paper Cards** with faint repeating watermarks (`JERUSALEM COLLEGE OF ENGG - OCT / NOV 2026`).
2. **Classroom & Floor Topology**:
   - **Ground Floor**: Rooms **`M001` through `M008`** (8 halls).
   - **First Floor**: Rooms **`M101` through `M108`** (8 halls).
   - **Second Floor**: Rooms **`M201` through `M208`** (8 halls).
   - **Third Floor**: Rooms **`M301` through `M305`** (5 halls).
   - 4 seat columns (`A`, `B`, `C`, `D`) with configurable 6 or 7 rows (24 to 28 seats).
3. **16-Digit Register Number Text & Excel Precision Safeguard**:
   - Database: `VARCHAR(16)` with `CHECK (length(register_no) = 16)` and regex pattern `^[0-9]{16}$`.
   - Excel reading: `pandas.read_excel(..., dtype=str)` preserves all 16 digits. Scientific notation floats (`2.4033E+15`) or precision-loss values are flagged with row numbers and exact reasons.
   - Excel exports: Explicitly written as text cells (`data_type='s'`, `number_format='@'`) to prevent Excel from corrupting digits when opened by staff.
   - Display: Compact monospace bold font everywhere (`font-mono`).
   - Search: Supports exact 16-digit matches, partial suffix matches (last 3-4 digits), or student names.
4. **Balanced Allocation Engine**:
   - Even load balancing across active halls (**~25 to 27 students per room**), eliminating nearly empty rooms.
   - Random shuffling with reproducible integer seeds and **"Re-shuffle with New Seed"** support.
   - Academic branch interleaving to ensure adjacent students do not belong to the same department.
   - Atomic database transactions.
5. **PDF & Excel Exports**:
   - Multi-page ReportLab PDF (1 classroom per page in official document card format with watermarks).
   - Hall-wise XLSX export with text register numbers.
   - Notice Board summary roster with string-sorted register number ranges per room.

---

## 2. Directory Structure & Files Created

```
Seating-Arrangement/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 001_initial_schema.py    # Database migration for all tables & constraints
│   │   ├── env.py                       # Alembic environment configured with app engine
│   │   └── script.py.mako               # Migration template
│   ├── app/
│   │   ├── routers/
│   │   │   ├── allocations.py           # Allocation generation, room plan, notice board, stats
│   │   │   ├── classrooms.py            # Floor & classroom CRUD, active/capacity toggle
│   │   │   ├── exams.py                 # Exam session listings & creation
│   │   │   ├── export.py                # PDF and XLSX export streaming endpoints
│   │   │   └── students.py              # File upload preview, validation, import & search
│   │   ├── allocation.py                # Balanced allocation algorithm & seat mapping
│   │   ├── config.py                    # Environment settings with fallback logic
│   │   ├── crud.py                      # Database query helpers
│   │   ├── database.py                  # SQLAlchemy engine & session factory
│   │   ├── export_pdf.py                # ReportLab multi-page A4 classroom PDF generator
│   │   ├── export_xlsx.py               # OpenPyXL export generator with text format enforcement
│   │   ├── main.py                      # FastAPI app entry with CORS & error handlers
│   │   ├── models.py                    # SQLAlchemy ORM models (Student, Floor, Classroom, Exam, Allocation)
│   │   └── schemas.py                   # Pydantic v2 schemas and validation models
│   ├── tests/
│   │   ├── test_allocation.py           # Pytest tests for capacity, even distribution & uniqueness
│   │   └── test_validation.py           # Pytest tests for 16-digit register number text validation
│   ├── .env.example                     # Environment template
│   ├── alembic.ini                      # Alembic CLI configuration
│   ├── exam_seating.db                  # Local active SQLite database
│   ├── requirements.txt                 # Backend Python package requirements
│   └── seed_data.py                     # Initial seed for floors, rooms M001..M208, and sample students
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   └── logo.svg                 # Jerusalem College of Engineering vector crest logo
│   │   ├── components/
│   │   │   ├── DocumentCard.tsx         # Official printable card with college header & watermark
│   │   │   ├── SeatGrid.tsx             # 4-column classroom seat layout (A1 to D7)
│   │   │   ├── Sidebar.tsx              # Deep blue Single Window Portal navigation sidebar
│   │   │   └── TopHeader.tsx            # Header bar with JCE emblem, COE title & staff badge
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx        # Overview stats, active exam banner & floor cards
│   │   │   ├── GeneratePage.tsx         # Exam parameter setup, shuffle engine & seed controls
│   │   │   ├── RoomsPage.tsx            # Classroom capacity & active hall toggle (M001..M208)
│   │   │   ├── SearchPage.tsx           # Full/partial register number hall & seat locator
│   │   │   ├── SeatingPlansPage.tsx     # Visual seat grid, attendance list, notice board, exports
│   │   │   └── UploadPage.tsx           # CSV/XLSX validator with 16-digit precision report
│   │   ├── api/
│   │   │   └── client.ts                # Typed API client
│   │   ├── types/
│   │   │   └── index.ts                 # TypeScript interfaces synced with Pydantic schemas
│   │   ├── App.tsx                      # Application router and QueryClient provider
│   │   ├── index.css                    # Single Window Portal styling tokens & @media print rules
│   │   └── main.tsx                     # React root mount
│   ├── index.html                       # HTML document with JCE branding & favicon
│   ├── package.json                     # Frontend dependencies
│   ├── tsconfig.json                    # TypeScript compiler configuration
│   └── vite.config.ts                   # Vite build tool configuration
├── samples/
│   ├── sample_students.csv              # 150 clean 16-digit student records
│   └── sample_students_with_errors.xlsx # Test file containing deliberate validation errors
├── .env.example                         # Root environment template
└── README.md                            # Complete setup and user guide
```

---

## 3. Database Schema Design

### Tables & Relationships
1. **`students`**:
   - `id`: Integer Primary Key
   - `register_no`: VARCHAR(16) UNIQUE, NOT NULL, Indexed, with `CHECK (length(register_no) = 16)`
   - `name`: VARCHAR(150), Nullable
   - `branch`: VARCHAR(100), Nullable
   - `semester`: Integer, Nullable
   - `subject_code`: VARCHAR(50), Nullable
   - `created_at`: DateTime
2. **`floors`**:
   - `id`: Integer Primary Key
   - `name`: VARCHAR(50) (`"Ground Floor"`, `"First Floor"`, `"Second Floor"`, `"Third Floor"`)
   - `floor_number`: Integer UNIQUE (`0`, `1`, `2`, `3`)
   - `created_at`: DateTime
3. **`classrooms`**:
   - `id`: Integer Primary Key
   - `floor_id`: Integer ForeignKey(`floors.id`, ondelete='CASCADE')
   - `name`: VARCHAR(50) UNIQUE (`"M001"`–`"M008"`, `"M101"`–`"M108"`, `"M201"`–`"M208"`, `"M301"`–`"M305"`)
   - `columns`: Integer (Default: 4 for A, B, C, D)
   - `rows_per_column`: Integer (6 or 7 rows)
   - `is_active`: Boolean (Default: True)
   - `created_at`: DateTime
4. **`exams`**:
   - `id`: Integer Primary Key
   - `name`: VARCHAR(150) (`"END SEMESTER EXAMINATIONS — OCT/NOV 2026"`)
   - `exam_date`: VARCHAR(50)
   - `session`: VARCHAR(10) (`"FN"` or `"AN"`)
   - `seed`: Integer, Nullable (Reproducibility seed)
   - `created_at`: DateTime
5. **`allocations`**:
   - `id`: Integer Primary Key
   - `exam_id`: Integer ForeignKey(`exams.id`, ondelete='CASCADE')
   - `student_id`: Integer ForeignKey(`students.id`, ondelete='CASCADE')
   - `classroom_id`: Integer ForeignKey(`classrooms.id`, ondelete='CASCADE')
   - `seat_label`: VARCHAR(10) (`"A1"`, `"B3"`, `"D7"`, etc.)
   - `created_at`: DateTime
   - Constraints:
     - `UNIQUE(exam_id, student_id)`: Student assigned to at most 1 seat per exam
     - `UNIQUE(exam_id, classroom_id, seat_label)`: Seat assigned to at most 1 student

---

## 4. API Endpoints (`/api/v1`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status check |
| `GET` | `/api/v1/allocations/dashboard-stats` | Aggregated dashboard metric totals |
| `POST` | `/api/v1/students/upload-preview` | Parses & validates CSV/XLSX file, returns validation report |
| `POST` | `/api/v1/students/commit-upload` | Imports valid student records into database |
| `GET` | `/api/v1/students` | Lists registered candidates |
| `DELETE` | `/api/v1/students/all` | Clears all registered candidates |
| `GET` | `/api/v1/students/search` | Searches candidate by full/partial register number or name |
| `GET` | `/api/v1/classrooms/floors` | Lists 4 floors and 29 classrooms |
| `GET` | `/api/v1/classrooms` | Lists all classrooms |
| `PATCH` | `/api/v1/classrooms/{id}` | Updates room row count (6/7) or toggles active status |
| `GET` | `/api/v1/exams` | Lists all examination sessions |
| `POST` | `/api/v1/allocations/generate` | Executes randomized balanced allocation |
| `GET` | `/api/v1/allocations/room-plan` | Returns 2D grid matrix of room seats (`A1`–`D7`) |
| `GET` | `/api/v1/allocations/notice-board` | Returns room-wise register number ranges |
| `GET` | `/api/v1/export/pdf` | Streams ReportLab multi-page A4 classroom PDF |
| `GET` | `/api/v1/export/xlsx` | Streams OpenPyXL hall allocation spreadsheet |
| `GET` | `/api/v1/export/notice-board-xlsx` | Streams notice board summary spreadsheet |

---

## 5. Automated Tests Summary

Run tests with `python -m pytest backend/tests -v`.

```
backend/tests/test_allocation.py::test_allocation_even_distribution PASSED
backend/tests/test_allocation.py::test_allocation_no_duplicate_seats_or_students PASSED
backend/tests/test_allocation.py::test_allocation_capacity_exceeded_error PASSED
backend/tests/test_validation.py::test_valid_16_digit_register_no PASSED
backend/tests/test_validation.py::test_preserve_leading_zeros PASSED
backend/tests/test_validation.py::test_leading_apostrophe_stripped PASSED
backend/tests/test_validation.py::test_reject_15_digits PASSED
backend/tests/test_validation.py::test_reject_17_digits PASSED
backend/tests/test_validation.py::test_reject_letters PASSED
backend/tests/test_validation.py::test_reject_scientific_notation PASSED
backend/tests/test_validation.py::test_reject_float_string PASSED
====================== 11 passed in 8.10s =======================
```

---

## 6. How to Run Locally

### 1. Backend Server
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Development Server
```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- Portal URL: `http://127.0.0.1:5173`
