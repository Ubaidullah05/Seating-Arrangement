import os
from pathlib import Path

# Base directory of the backend
BASE_DIR = Path(__file__).resolve().parent.parent

def load_dotenv_simple(env_path: Path):
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value

# Check .env in backend dir or parent dir
load_dotenv_simple(BASE_DIR / ".env")
load_dotenv_simple(BASE_DIR.parent / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/exam_seating_db"
)

# SQLite fallback URL if PostgreSQL cannot connect or if configured to sqlite
SQLITE_FALLBACK_URL = f"sqlite:///{BASE_DIR / 'exam_seating.db'}"

CORS_ORIGINS_RAW = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
)
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_RAW.split(",") if origin.strip()]
