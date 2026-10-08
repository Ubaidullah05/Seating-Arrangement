# Commands Reference — Exam Seating Planner

This guide contains the exact commands to run the **Database**, **Backend**, and **Frontend** services on Windows (PowerShell / Command Prompt) or macOS/Linux.

---

## 📌 Quick Start (3 Separate Terminals)

Always open terminals starting from the project root:
```
c:\Users\rasin\Desktop\Project\Seating plan\Seating-Arrangement
```

---

### Terminal 1: Database (DB)

The project is configured by default to use **SQLite** (file: `backend/exam_seating.db`). SQLite runs embedded with the backend, so no external server process needs to be kept open.

#### 1. Setup & Run Database Migrations
Run from the **project root directory**:
```powershell
# Run database migrations with Alembic
python -m alembic -c backend/alembic.ini upgrade head
```

#### 2. Seed Initial Data (Floors M001–M305 & 160 Sample Students)
```powershell
python backend/seed_data.py
```

> **Using PostgreSQL instead of SQLite?**
> If you wish to use PostgreSQL:
> 1. Make sure PostgreSQL service is running (`Get-Service *postgres* | Start-Service`).
> 2. Create the database:
>    ```sql
>    CREATE DATABASE exam_seating_db;
>    ```
> 3. Update `DATABASE_URL` in `.env`:
>    ```env
>    DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/exam_seating_db
>    ```
> 4. Run `python -m alembic -c backend/alembic.ini upgrade head` and `python backend/seed_data.py`.

---

### Terminal 2: Backend (FastAPI API)

Run from the **project root directory**:

```powershell
# 1. (Optional) Activate Virtual Environment if created
.\backend\venv\Scripts\Activate.ps1

# 2. Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# 3. Start the FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend API URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/v1/health`

> ⚠️ **Important**: Do **not** run `python -m uvicorn backend.app.main:app` from inside the `backend` folder. Always run it from the root `Seating-Arrangement` folder so Python can resolve the `backend` package.

---

### Terminal 3: Frontend (React 19 + Vite)

Run from the `frontend` directory:

```powershell
# 1. Navigate to frontend folder
cd frontend

# 2. Install dependencies (first time only)
npm install

# 3. Start Vite dev server
npm run dev
```

- **Frontend App URL**: `http://localhost:5173`

---

## 🛠️ Verification & Troubleshooting Commands

### Check if Ports are Listening
```powershell
netstat -ano | findstr "8000 5173"
```

### Test Backend Connectivity
```powershell
curl http://127.0.0.1:8000/api/v1/health
```

### Stop Running Processes on Specific Ports (if stuck)
```powershell
# Find PID on port 8000
netstat -ano | findstr ":8000"

# Kill process by PID (replace <PID> with number from last column)
taskkill /PID <PID> /F
```

---

## 📋 Summary Table

| Service | Working Directory | Command | URL |
| :--- | :--- | :--- | :--- |
| **Database Seed** | `Seating-Arrangement` | `python backend/seed_data.py` | `backend/exam_seating.db` |
| **Backend API** | `Seating-Arrangement` | `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload` | `http://127.0.0.1:8000` |
| **Frontend UI** | `Seating-Arrangement\frontend` | `npm run dev` | `http://localhost:5173` |
