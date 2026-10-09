import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app

# Shared in-memory database for all HTTP-level tests. Kept alive for the whole
# session (StaticPool + :memory: => one connection, one database).
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=test_engine)
_TestingSession = sessionmaker(bind=test_engine, autoflush=False)
test_session = _TestingSession()


def _override_get_db():
    yield test_session


@pytest.fixture(autouse=True)
def db_override():
    """Make sure every test uses the shared in-memory session, even after a
    test module clears or replaces the dependency override."""
    app.dependency_overrides[get_db] = _override_get_db
    yield
