import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import Floor, Classroom, Student, Exam, Allocation

def seed_database(target_students: int = 924, force: bool = False):
    print("Checking and creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        floors_spec = [
            (0, "Ground Floor", ["M001", "M002", "M003", "M004", "M005", "M006", "M007", "M008"]),
            (1, "First Floor", ["M101", "M102", "M103", "M104", "M105", "M106", "M107", "M108"]),
            (2, "Second Floor", ["M201", "M202", "M203", "M204", "M205", "M206", "M207", "M208"]),
            (3, "Third Floor", ["M301", "M302", "M303", "M304", "M305"]),
            (4, "LS", ["LS-1"]),
            (5, "VH", ["VH-1", "VH-2", "VH-3"]),
        ]

        for floor_num, floor_name, room_names in floors_spec:
            floor = db.query(Floor).filter(Floor.floor_number == floor_num).first()
            if not floor:
                floor = Floor(name=floor_name, floor_number=floor_num)
                db.add(floor)
                db.flush()
                print(f"Created floor: {floor_name}")

            for r_name in room_names:
                existing_room = db.query(Classroom).filter(Classroom.name == r_name).first()
                if not existing_room:
                    room = Classroom(
                        floor_id=floor.id,
                        name=r_name,
                        columns=4,
                        rows_per_column=7,
                        is_active=True
                    )
                    db.add(room)
                    print(f"Created classroom: {r_name} in {floor.name}")

        db.commit()

        # Seed sample students (target: 924 students = 33 classrooms x 28 capacity)
        student_count = db.query(Student).count()
        if student_count != target_students or force:
            print(f"Clearing previous allocations and students to seed exactly {target_students} students...")
            db.query(Allocation).delete()
            db.query(Student).delete()
            db.commit()

            print(f"Seeding {target_students} students with 16-digit register numbers...")
            sample_branches = [
                ("B.E. Computer Science and Engineering", ["CS3301", "CS3351", "CS3352"]),
                ("B.Tech. Artificial Intelligence and Data Science", ["AD3301", "AD3351", "AD3391"]),
                ("B.E. Electronics and Communication Engineering", ["EC3301", "EC3351", "EC3354"]),
                ("B.Tech. Information Technology", ["IT3301", "IT3351", "IT3381"]),
                ("B.E. Electrical and Electronics Engineering", ["EE3301", "EE3351", "EE3392"]),
                ("B.E. Mechanical Engineering", ["ME3301", "ME3351", "ME3391"]),
                ("B.E. Civil Engineering", ["CE3301", "CE3351", "CE3391"]),
                ("B.Tech. Computer Science and Business Systems", ["CB3301", "CB3351", "CB3381"]),
            ]

            first_names = [
                "Aarav", "Aditya", "Akash", "Ananya", "Anirudh", "Archana", "Arjun", "Ashwin", "Bhavana", "Deepak",
                "Deepika", "Dinesh", "Divya", "Gayathri", "Gautam", "Gokul", "Hari", "Harish", "Harini", "Janani",
                "Karthik", "Kavya", "Keerthana", "Lavanya", "Madhavan", "Manojkumar", "Meera", "Mithun", "Naveen", "Nisha",
                "Nithya", "Pavithra", "Pooja", "Pranav", "Prashanth", "Praveen", "Priya", "Rahul", "Rajesh", "Rakshita",
                "Rasin", "Rithika", "Rohit", "Sai", "Sanjay", "Santhosh", "Saravanan", "Shalini", "Shravan", "Siddharth",
                "Sneha", "Srikanth", "Srinath", "Subhash", "Suresh", "Surya", "Swetha", "Tejas", "Varun", "Vignesh",
                "Vijay", "Vikram", "Vinoth", "Vishal", "Yogesh"
            ]

            last_names = [
                "Sharma", "Patel", "Krishnan", "Sundaram", "Subramanian", "Nair", "Menon", "Rajan", "Balaji", "Raman",
                "Chandran", "Kumar", "Venkatesh", "Pillai", "Natarajan", "Varma", "Srinivasan", "Raja", "Vijay", "Prasath",
                "Murugan", "Prakash", "Karthick", "Swaminathan", "Ramachandran", "Anand", "Iyer", "Mani", "Selvam",
                "Pandian", "Reddy", "Chowdhury", "Das", "Bose", "Banerjee", "Gupta", "Malhotra", "Joshi", "Bhat", "Verma"
            ]

            students = []
            for i in range(target_students):
                # 16-digit register number: 2403310910420001 to 2403310910420924
                reg_num_str = f"240331091042{i+1:04d}"
                
                # Assign branch and subject code round-robin
                b_idx = i % len(sample_branches)
                branch_name, sub_codes = sample_branches[b_idx]
                sub = sub_codes[(i // len(sample_branches)) % len(sub_codes)]

                # Generate distinct realistic names
                fn = first_names[i % len(first_names)]
                ln = last_names[(i // len(first_names)) % len(last_names)]
                suffix = f" {chr(65 + (i % 26))}." if (i // (len(first_names) * len(last_names))) > 0 else ""
                full_name = f"{fn} {ln}{suffix}"

                students.append(
                    Student(
                        register_no=reg_num_str,
                        name=full_name,
                        branch=branch_name,
                        semester=5,
                        subject_code=sub
                    )
                )

            db.add_all(students)
            db.commit()
            print(f"Successfully seeded {len(students)} students into the database.")
        else:
            print(f"Database already has {student_count} students.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    force_run = "--force" in sys.argv
    count = 924
    for arg in sys.argv[1:]:
        if arg.isdigit():
            count = int(arg)
    seed_database(target_students=count, force=force_run)
