from backend.app.models import Floor, Classroom

ROOM_COLUMNS = 4
ROOM_ROWS_PER_COLUMN = 7

FLOORS_SPEC = [
    (0, "Ground Floor", ["M001", "M002", "M003", "M004", "M005", "M006", "M007", "M008"]),
    (1, "First Floor", ["M101", "M102", "M103", "M104", "M105", "M106", "M107", "M108"]),
    (2, "Second Floor", ["M201", "M202", "M203", "M204", "M205", "M206", "M207", "M208"]),
    (3, "Third Floor", ["M301", "M302", "M303", "M304", "M305"]),
    (4, "LS", ["LS1"]),
    (5, "VH", ["VH1", "VH2", "VH3"]),
]


def ensure_rooms(db) -> int:
    created = 0
    for floor_number, floor_name, room_names in FLOORS_SPEC:
        floor = db.query(Floor).filter(Floor.floor_number == floor_number).first()
        if floor is None:
            floor = Floor(name=floor_name, floor_number=floor_number)
            db.add(floor)
            db.flush()
            created += 1
        for room_name in room_names:
            existing = db.query(Classroom).filter(Classroom.name == room_name).first()
            if existing is None:
                db.add(Classroom(
                    floor_id=floor.id,
                    name=room_name,
                    columns=ROOM_COLUMNS,
                    rows_per_column=ROOM_ROWS_PER_COLUMN,
                    is_active=True,
                ))
                created += 1
    db.commit()
    return created
