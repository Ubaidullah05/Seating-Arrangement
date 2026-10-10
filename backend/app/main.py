import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import inspect, text

from backend.app.config import CORS_ORIGINS
from backend.app.database import engine, Base, SessionLocal
from backend.app.room_seed import ensure_rooms
from backend.app.routers import students, classrooms, exams, allocations, export, auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exam_seating_planner")

# Ensure database tables exist
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.warning(f"Database table auto-initialization note: {e}")

# Self-heal: add students.dob to pre-auth databases created before this feature
try:
    _inspector = inspect(engine)
    _student_cols = [c["name"] for c in _inspector.get_columns("students")]
    if "dob" not in _student_cols:
        with engine.begin() as _conn:
            _conn.execute(text("ALTER TABLE students ADD COLUMN dob VARCHAR(10)"))
        logger.info("Added missing students.dob column.")
except Exception as e:
    logger.warning(f"Schema self-heal note: {e}")

# Self-seed default floors & classrooms on a fresh database (e.g. first deploy)
try:
    _rooms_db = SessionLocal()
    try:
        _created_rooms = ensure_rooms(_rooms_db)
        if _created_rooms:
            logger.info(f"Room self-seed created {_created_rooms} floor/classroom records.")
    finally:
        _rooms_db.close()
except Exception as e:
    logger.warning(f"Room self-seed note: {e}")

# Bootstrap the default ACOE faculty account (acoe@jerusalemengg.ac.in / acoe@123)
try:
    _bootstrap_db = SessionLocal()
    try:
        auth.bootstrap_faculty_user(_bootstrap_db)
    finally:
        _bootstrap_db.close()
except Exception as e:
    logger.warning(f"Faculty bootstrap note: {e}")

app = FastAPI(
    title="Exam Seating Planner API",
    description="Office of the Controller of Examinations - Jerusalem College of Engineering, Chennai",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Global error handlers for consistent responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc not in ["body", "query", "path"])
        errors.append({
            "field": field or "body",
            "message": err["msg"],
            "type": err["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": errors
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Failed",
            "message": str(exc.detail)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc)
        }
    )

# Include API routers under /api/v1
app.include_router(students.router)
app.include_router(classrooms.router)
app.include_router(exams.router)
app.include_router(allocations.router)
app.include_router(export.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "institution": "Jerusalem College of Engineering, Chennai - 600100",
        "office": "Office of the Controller of Examinations",
        "application": "Exam Seating Planner",
        "version": "1.0.0",
        "status": "Online",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "institution": "Jerusalem College of Engineering"}
