import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import DATABASE_URL, SQLITE_FALLBACK_URL

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    try:
        if DATABASE_URL.startswith("postgresql"):
            test_engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3}
            )
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database.")
            return test_engine
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        )
    except Exception as e:
        logger.warning(
            f"Could not connect to configured database ({DATABASE_URL}): {e}. "
            f"Falling back to local SQLite database at {SQLITE_FALLBACK_URL}."
        )
        return create_engine(
            SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
