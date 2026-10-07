# Exam Seating Planner — Jerusalem College of Engineering, Chennai

An enterprise examination seating arrangement portal designed for the **Office of the Controller of Examinations (COE)** at **Jerusalem College of Engineering (Autonomous), Chennai - 600100**.

Built exclusively for examination staff and coordinators to automate the generation, balancing, visualization, and export of seating plans for End Semester Examinations (e.g. OCT/NOV 2026). The user interface faithfully mirrors the college's official **Single Window Portal**.

---

## 🏛️ System Highlights & UI Design

- **Single Window Portal Aesthetic**:
  - **Fixed Deep Blue Left Sidebar** (`#004a99` to `#002f66`) with the `"Single Window Portal"` title, hamburger toggle, uppercase menu items, and active gold left border indicator (`#b8892b`).
  - **Top Header Bar**: Jerusalem College of Engineering crest emblem, bold uppercase serif heading, autonomous Anna University affiliation subtext, gold `"OFFICE OF THE CONTROLLER OF EXAMINATIONS"`, and static `"STAFF"` indicator (no authentication, no student logins).
  - **Main Content**: Blue underline headers, gold/mustard `"PRINT"` action button, and centered printable **Official Document Paper Cards** featuring watermark patterns, 4-column examination info boxes, and monospace register numbers.
- **Classroom Topology**:
  - **3 Floors**:
    - **Ground Floor**: Rooms **`M001` to `M008`** (8 halls)
    - **First Floor**: Rooms **`M101` to `M108`** (8 halls)
    - **Second Floor**: Rooms **`M201` to `M208`** (8 halls)
  - 4 seat columns per hall (`A`, `B`, `C`, `D`), configurable with 6 or 7 rows (24 to 28 capacity, allocating ~25-27 students per room).
- **16-Digit Register Number Strict Text Handling**:
  - Every register number is treated as pure **TEXT** everywhere (`VARCHAR(16)`, `CHECK (length(register_no) = 16)` / `register_no ~ '^[0-9]{16}$'`).
  - **Excel Precision Protection**: Excel stores numeric cells with only 15 significant digits. The upload parser reads all cells as string (`dtype=str`), trims apostrophes, and automatically catches and flags scientific notation (`2.4033E+15`) or float corruption before committing.
  - Exported Excel files explicitly set the register number cell type as string (`data_type='s'`, `number_format='@'`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Database** | PostgreSQL with SQLAlchemy 2.0 ORM, Alembic migrations, psycopg3 driver (with seamless development SQLite fallback) |
| **Backend API** | Python 3.10+ / 3.14, FastAPI, Pydantic v2 schemas |
| **File Parsing** | pandas + openpyxl (Excel `.xlsx`), pandas / csv (CSV) with `dtype=str` |
| **Document Export** | ReportLab (multi-page A4 classroom PDF with watermark) & openpyxl (XLSX) |
| **Frontend** | React 19 + TypeScript (Vite), React Router v7, TanStack Query v5, Lucide Icons |
| **Styling** | Vanilla CSS Design System with `@media print` layout |

---

## ⚙️ Local Setup Instructions

### Prerequisites
- Python 3.10+ (or Python 3.14)
- Node.js v18+ and npm
- PostgreSQL (optional for local testing; SQLite fallback is built-in if PostgreSQL is not running)

### 1. Backend Setup

```bash
# Navigate to project directory
cd Seating-Arrangement

# Optional: Create and activate a virtual environment
python -m venv backend/venv
# On Windows PowerShell:
.\backend\venv\Scripts\Activate.ps1
# On Linux/macOS:
source backend/venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure .env (optional if using default PostgreSQL or SQLite fallback)
cp backend/.env.example backend/.env

# Run database migrations
python -m alembic -c backend/alembic.ini upgrade head

# Seed floors (M001..M208) and 160 sample students
python backend/seed_data.py

# Start FastAPI backend server (runs on http://127.0.0.1:8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger documentation will be available at:
👉 **`http://127.0.0.1:8000/docs`**

---

### 2. Frontend Setup

```bash
# Open a new terminal in the frontend directory
cd Seating-Arrangement/frontend

# Install npm packages
npm install

# Start Vite development server (runs on http://127.0.0.1:5173)
npm run dev
```

Open your browser at:
👉 **`http://127.0.0.1:5173`**

---

## 🧮 Allocation Engine Algorithm

The seating allocation engine (`backend/app/allocation.py`) operates as follows:
1. **Capacity Validation**: Calculates total candidates $N$ against active classrooms capacity. Rejects with an informative error if total students exceed available seats.
2. **Even Load Balancing**: Instead of filling rooms to 100% and leaving the last hall almost empty, the engine calculates the required active halls and computes:
   $$\text{target\_per\_hall} = \lfloor N / R \rfloor$$
   Distributing the remainder $+1$ to initial halls so every room has **25 to 27 candidates**.
3. **Randomized Shuffling & Interleaving**:
   - Randomizes candidates using Python's `random.Random(seed)`.
   - Groups candidates by academic branch/subject and round-robin interleaves them to avoid adjacent students from the same department.
4. **Reproducible Seeding**: If a seed is specified (or generated), it is saved in the `exams` table. Staff can re-shuffle or re-generate with identical results anytime.
5. **Atomic DB Transaction**: Executes all room allocations inside a single database transaction.

---

## 🧪 Automated Testing

Run the automated test suite with pytest:

```bash
# Run all tests
python -m pytest backend/tests -v
```

### Test Coverage:
- `backend/tests/test_validation.py`:
  - 16-digit numeric register number validation.
  - Preservation of leading zeros (e.g. `'0003310910421108'`).
  - Leading apostrophe stripping (`'2403310910421108'`).
  - Rejection of 15-digit numbers, 17-digit numbers, letters, and scientific notation floats.
- `backend/tests/test_allocation.py`:
  - Even distribution across rooms (e.g. 75 students $\rightarrow$ 25 in each room).
  - Uniqueness: No student assigned to multiple seats; no duplicate seat labels in a room.
  - Insufficient capacity error handling.

---

## 📁 Sample Test Files Provided

- **`samples/sample_students.csv`**: 150 valid 16-digit student registers across 5 branches.
- **`samples/sample_students_with_errors.xlsx`**: Excel file containing intentional errors to test validation:
  - Row 3: 15 digits (short)
  - Row 4: Scientific notation float (`2.40331E+15`)
  - Row 5: Alphanumeric characters
  - Row 6: Duplicate register number
  - Row 7: 18 digits (too long)
  - Rows 8+: Valid candidates

---

## 📄 License & Attribution
Designed for **Jerusalem College of Engineering (Autonomous), Chennai**, affiliated with Anna University. Single Window Portal UI format &copy; Controller of Examinations.