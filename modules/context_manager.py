import json
import pandas as pd
import os
import datetime
from filelock import FileLock

class ContextEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.students_path = os.path.join(data_dir, "students.json")
        self.timetable_path = os.path.join(data_dir, "timetable.csv")
        self.log_path = os.path.join(data_dir, "session_log.csv")
        
        self._load_data()
        
    def _load_data(self):
        # Load students
        if os.path.exists(self.students_path):
            with open(self.students_path, "r") as f:
                self.students = json.load(f)
        else:
            self.students = {}
            
        # Load timetable
        if os.path.exists(self.timetable_path):
            self.timetable = pd.read_csv(self.timetable_path)
            # Normalize headers: strip whitespace and lowercase
            self.timetable.columns = self.timetable.columns.str.strip().str.lower()
        else:
            self.timetable = pd.DataFrame()
            
    def get_student_info(self, student_id):
        """Returns the student's dict (Section, Dept, Privacy Hash)."""
        return self.students.get(student_id)

    def get_expected_location(self, student_id, day, time_str):
        """
        Looks up the student's Section/Year/Dept.
        Filters the Timetable DataFrame for that specific class at that time.
        Returns a dict with `room`, `subject`, `start`, `end` if a class exists, or `None`.
        """
        student = self.get_student_info(student_id)
        if not student:
            return None
            
        program = student.get("program")
        year = student.get("year")
        section = student.get("section")
        dept = student.get("dept")
        
        if self.timetable.empty:
            return None
            
        # Filter for the student's class
        # Assuming timetable columns are: day, start, end, faculty, dept, program, year, section, subject, teacher, room
        # We need to match day, program, year, section, dept
        
        # Note: Ensure types match (e.g., year is int in json, check csv type)
        # Timetable year might be int or str. Let's try to match flexibly or ensure type.
        
        student_classes = self.timetable[
            (self.timetable["day"] == day) &
            (self.timetable["program"] == program) &
            (self.timetable["year"] == year) &
            (self.timetable["section"] == section) &
            (self.timetable["dept"] == dept)
        ]
        
        for _, row in student_classes.iterrows():
            start_time = row["start"] # e.g. "9:00"
            end_time = row["end"]     # e.g. "10:00"
            
            try:
                t_check = datetime.datetime.strptime(time_str, "%H:%M").time()
                t_start = datetime.datetime.strptime(start_time, "%H:%M").time()
                t_end = datetime.datetime.strptime(end_time, "%H:%M").time()
                
                if t_start <= t_check < t_end:
                    return {
                        "room": row["room"],
                        "subject": row["subject"],
                        "start": row["start"],
                        "end": row["end"],
                        "teacher": row["teacher"]
                    }
            except ValueError:
                continue
                
        return None

    def get_class_context(self, zone, day, time_str):
        """
        Checks if a class is currently active in the given zone.
        Returns: True (Class Active) or False (Break/Free).
        """
        if self.timetable.empty:
            return False
            
        # Filter for the room
        room_classes = self.timetable[
            (self.timetable["day"] == day) &
            (self.timetable["room"] == zone)
        ]
        
        for _, row in room_classes.iterrows():
            start_time = row["start"]
            end_time = row["end"]
            
            try:
                t_check = datetime.datetime.strptime(time_str, "%H:%M").time()
                t_start = datetime.datetime.strptime(start_time, "%H:%M").time()
                t_end = datetime.datetime.strptime(end_time, "%H:%M").time()
                
                if t_start <= t_check < t_end:
                    return True # Class is active
            except ValueError:
                continue
                
        return False

    def check_compliance(self, student_id, current_zone, day, time_str):
        """
        Uses `get_expected_location`.
        If no class is scheduled: Return `(True, "Free Period", None)`.
        If class is scheduled AND `current_zone == expected_room`: Return `(True, "Compliant", expected_data)`.
        If class is scheduled AND `current_zone != expected_room`: Return `(False, f"TRUANCY...", expected_data)`.
        """
        expected = self.get_expected_location(student_id, day, time_str)
        
        if expected is None:
            return True, "Free Period", None
            
        expected_room = expected["room"]
        subject = expected["subject"]
        
        if current_zone == expected_room:
            return True, "Compliant", expected
        else:
            return False, f"TRUANCY: Expected in {expected_room} for {subject}", expected

    def get_anon_id(self, real_id):
        """Returns the privacy_hash for a given student ID."""
        student = self.students.get(real_id)
        if student:
            return student.get("privacy_hash")
        return None

    def log_event(self, real_id, emotion, context):
        """Logs an event anonymously using RCU pattern."""
        anon_id = self.get_anon_id(real_id)
        if not anon_id:
            print(f"Cannot log event: Unknown student ID {real_id}")
            return
            
        timestamp = datetime.datetime.now().isoformat()
        
        new_entry = {
            "timestamp": timestamp,
            "anon_id": anon_id,
            "emotion": emotion,
            "context": context
        }
        
        # Load existing log or create new DataFrame
        if os.path.exists(self.log_path):
            try:
                df = pd.read_csv(self.log_path)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame(columns=["timestamp", "anon_id", "emotion", "context"])
        else:
            df = pd.DataFrame(columns=["timestamp", "anon_id", "emotion", "context"])
            
        # Append new entry
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        
        # RCU Save with FileLock
        log_lock = FileLock(f"{self.log_path}.lock")
        with log_lock:
            temp_path = f"{self.log_path}.tmp"
            df.to_csv(temp_path, index=False)
            os.replace(temp_path, self.log_path)

if __name__ == "__main__":
    # Quick test
    engine = ContextEngine()
    
    # Create a dummy timetable entry for testing if not exists or just rely on existing
    # For S101: UG, 1, A, Computer Science
    # Let's assume there is a class at Mon 10:00 in Lab 1
    
    # We need to make sure the timetable has data for this test to be meaningful
    # Or we can mock it by adding a row to self.timetable in memory
    
    print("Testing Compliance for S101 at Mon 10:00 (Location: Canteen)...")
    
    # Inject test data into memory for robust testing without depending on external file state
    test_row = {
        "day": "Mon",
        "start": "10:00",
        "end": "11:00",
        "faculty": "Technology",
        "dept": "Computer Science",
        "program": "UG",
        "year": 1,
        "section": "A",
        "subject": "Data Structures",
        "teacher": "Ms. Davis",
        "room": "Lab 1"
    }
    engine.timetable = pd.concat([engine.timetable, pd.DataFrame([test_row])], ignore_index=True)
    
    is_compliant, message, data = engine.check_compliance("S101", "Canteen", "Mon", "10:00")
    print(f"Result: {is_compliant}, Message: {message}, Data: {data}")
    
    print("\nTesting Compliance for S101 at Mon 10:00 (Location: Lab 1)...")
    is_compliant, message, data = engine.check_compliance("S101", "Lab 1", "Mon", "10:00")
    print(f"Result: {is_compliant}, Message: {message}, Data: {data}")
