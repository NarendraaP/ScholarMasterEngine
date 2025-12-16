import sys
import os
import json
import pandas as pd
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import SessionLocal, User, Student, Schedule, init_db

def migrate_data():
    print("🚀 Starting Data Migration to SQL...")
    
    db = SessionLocal()
    
    # 1. Migrate Users
    users_file = "data/users.json"
    if os.path.exists(users_file):
        print(f"📦 Migrating Users from {users_file}...")
        with open(users_file, "r") as f:
            users_data = json.load(f)
            
        for username, data in users_data.items():
            # Check if exists
            exists = db.query(User).filter(User.username == username).first()
            if not exists:
                user = User(
                    username=username,
                    password_hash=data.get("password"), # Note: In production, ensure this is hashed
                    role=data.get("role"),
                    name=data.get("name")
                )
                db.add(user)
        print(f"✅ Users migrated.")
    else:
        print("⚠️ users.json not found.")

    # 2. Migrate Students
    students_file = "data/students.json"
    if os.path.exists(students_file):
        print(f"📦 Migrating Students from {students_file}...")
        with open(students_file, "r") as f:
            students_data = json.load(f)
            
        for s_id, data in students_data.items():
            exists = db.query(Student).filter(Student.id == s_id).first()
            if not exists:
                student = Student(
                    id=s_id,
                    name=data.get("name"),
                    dept=data.get("dept"),
                    section=data.get("section"),
                    privacy_hash=data.get("privacy_hash")
                )
                db.add(student)
        print(f"✅ Students migrated.")
    else:
        print("⚠️ students.json not found.")

    # 3. Migrate Timetable
    timetable_file = "data/timetable.csv"
    if os.path.exists(timetable_file):
        print(f"📦 Migrating Schedule from {timetable_file}...")
        df = pd.read_csv(timetable_file)
        
        # Clean headers just in case
        df.columns = df.columns.str.strip().str.lower()
        
        for _, row in df.iterrows():
            # Basic mapping
            schedule = Schedule(
                day=row.get('day'),
                start_time=row.get('start'),
                end_time=row.get('end'),
                subject=row.get('subject'),
                teacher=row.get('teacher'),
                room=row.get('room')
            )
            db.add(schedule)
        print(f"✅ Schedule migrated.")
    else:
        print("⚠️ timetable.csv not found.")

    # Commit all changes
    try:
        db.commit()
        print("🎉 Migration Complete: Data moved to SQL.")
    except Exception as e:
        db.rollback()
        print(f"❌ Migration Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    migrate_data()
