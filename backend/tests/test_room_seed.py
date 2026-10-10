from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models import Classroom, Floor, Student
from backend.app.room_seed import FLOORS_SPEC, ensure_rooms

SPEC_ROOM_COUNT = sum(len(rooms) for _, _, rooms in FLOORS_SPEC)


def _fresh_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False)()


def test_ensure_rooms_creates_full_spec():
    db = _fresh_session()
    try:
        created = ensure_rooms(db)
        assert created == len(FLOORS_SPEC) + SPEC_ROOM_COUNT
        assert db.query(Floor).count() == len(FLOORS_SPEC)
        assert db.query(Classroom).count() == SPEC_ROOM_COUNT
        for floor_number, _, room_names in FLOORS_SPEC:
            floor = db.query(Floor).filter(Floor.floor_number == floor_number).one()
            names = {
                r.name
                for r in db.query(Classroom).filter(Classroom.floor_id == floor.id)
            }
            assert names == set(room_names)
        vh_floor = db.query(Floor).filter(Floor.name == "VH").one()
        vh_rooms = sorted(
            r.name
            for r in db.query(Classroom).filter(Classroom.floor_id == vh_floor.id)
        )
        assert vh_rooms == ["VH1", "VH2", "VH3"]
        m001 = db.query(Classroom).filter(Classroom.name == "M001").one()
        assert (m001.columns, m001.rows_per_column, m001.is_active) == (4, 7, True)
    finally:
        db.close()


def test_ensure_rooms_is_idempotent_and_preserves_students():
    db = _fresh_session()
    try:
        db.add(Student(
            register_no="2403310910421001",
            name="Test Student",
            branch="B.E. Computer Science and Engineering",
            semester=5,
            subject_code="CS3301",
        ))
        db.commit()
        first = ensure_rooms(db)
        second = ensure_rooms(db)
        assert first > 0
        assert second == 0
        assert db.query(Student).count() == 1
        assert db.query(Classroom).count() == SPEC_ROOM_COUNT
        assert db.query(Floor).count() == len(FLOORS_SPEC)
    finally:
        db.close()


def test_ensure_rooms_fills_only_missing_and_never_edits_existing():
    db = _fresh_session()
    try:
        floor = Floor(name="Ground Floor", floor_number=0)
        db.add(floor)
        db.flush()
        db.add(Classroom(
            floor_id=floor.id,
            name="M001",
            columns=99,
            rows_per_column=7,
            is_active=False,
        ))
        db.commit()
        ensure_rooms(db)
        assert db.query(Floor).count() == len(FLOORS_SPEC)
        assert db.query(Classroom).count() == SPEC_ROOM_COUNT
        m001 = db.query(Classroom).filter(Classroom.name == "M001").one()
        assert (m001.columns, m001.is_active) == (99, False)
        assert not db.query(Student).count()
    finally:
        db.close()
