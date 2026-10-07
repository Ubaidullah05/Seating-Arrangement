import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import Floor, Classroom, Student, Exam

def seed_database():
    print("Checking and creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if floors exist
        existing_floors = db.query(Floor).all()
        if not existing_floors:
            print("Seeding 3 floors and 24 classrooms (M001 to M008, M101 to M108, M201 to M208)...")
            
            floors_spec = [
                (0, "Ground Floor", ["M001", "M002", "M003", "M004", "M005", "M006", "M007", "M008"]),
                (1, "First Floor", ["M101", "M102", "M103", "M104", "M105", "M106", "M107", "M108"]),
                (2, "Second Floor", ["M201", "M202", "M203", "M204", "M205", "M206", "M207", "M208"]),
            ]

            for floor_num, floor_name, room_names in floors_spec:
                floor = Floor(name=floor_name, floor_number=floor_num)
                db.add(floor)
                db.flush() # get floor.id

                for r_name in room_names:
                    # Capacity 28 (4 columns x 7 rows)
                    room = Classroom(
                        floor_id=floor.id,
                        name=r_name,
                        columns=4,
                        rows_per_column=7,
                        is_active=True
                    )
                    db.add(room)

            db.commit()
            print("Successfully created 3 floors with 8 classrooms each (24 rooms total, 672 capacity).")
        else:
            print("Floors and classrooms already exist. Skipping room creation.")

        # Seed sample students if database has 0 students
        student_count = db.query(Student).count()
        if student_count == 0:
            print("Seeding sample students with 16-digit register numbers...")
            sample_branches = [
                ("B.E. Computer Science and Engineering", ["JCS2002", "JCS2501", "JCS2502"]),
                ("B.Tech. Artificial Intelligence and Data Science", ["JAI2001", "JAI2502", "JAI2503"]),
                ("B.E. Electronics and Communication Engineering", ["JEC2001", "JEC2501", "JEC2502"]),
                ("B.Tech. Information Technology", ["JIT2001", "JIT2501", "JIT2502"]),
                ("B.E. Electrical and Electronics Engineering", ["JEE2001", "JEE2501", "JEE2502"])
            ]
            
            students = []
            base_reg = 2403310910421000
            names = [
                "Rasin Karthick S", "Aarav Sharma", "Diya Patel", "Aditya Krishnan", "Ananya Sundaram",
                "Kavya Subramanian", "Rahul Nair", "Priya Menon", "Siddharth Rajan", "Sneha Balaji",
                "Vikram Raman", "Meera Chandran", "Harish Kumar", "Rithika Venkatesh", "Gautam Pillai",
                "Swetha Natarajan", "Arjun Varma", "Deepika Srinivasan", "Karthik Raja", "Pooja Vijay",
                "Naveen Prasath", "Keerthana Murugan", "Dinesh K", "Sanjay Prakash", "Lavanya R",
                "Ashwin S", "Divya M", "Manojkumar B", "Shalini T", "Vignesh G"
            ]

            for i in range(160): # 160 students (~6 rooms worth)
                reg_num_str = str(base_reg + i)
                b_idx = i % len(sample_branches)
                branch_name, sub_codes = sample_branches[b_idx]
                name = names[i % len(names)] + (f" ({i+1})" if i >= len(names) else "")
                sub = sub_codes[i % len(sub_codes)]

                students.append(
                    Student(
                        register_no=reg_num_str,
                        name=name,
                        branch=branch_name,
                        semester=5,
                        subject_code=sub
                    )
                )

            db.add_all(students)
            db.commit()
            print(f"Successfully seeded {len(students)} sample students.")
        else:
            print(f"Database already has {student_count} students.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
