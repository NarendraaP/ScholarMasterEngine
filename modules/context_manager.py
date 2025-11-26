import json
import pandas as pd
import os
from datetime import datetime

class ContextEngine:
    def __init__(self, students_file="data/students.json", timetable_file="data/timetable.csv"):
        self.students = self._load_students(students_file)
        self.timetable = self._load_timetable(timetable_file)

    def _load_students(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return {}

    def _load_timetable(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            # Lowercase headers for consistency
            df.columns = [c.lower() for c in df.columns]
            return df
        return pd.DataFrame()

    def get_student_info(self, student_id):
        """Returns student details or None."""
        return self.students.get(student_id)

    def _get_class_row(self, student_id, current_day, current_time):
        """Helper to find the specific timetable row for a student at a given time."""
        student = self.get_student_info(student_id)
        if not student or self.timetable.empty:
            return None

        # Filter by student's academic details
        mask = (
            (self.timetable['program'] == student['program']) &
            (self.timetable['year'] == student['year']) &
            (self.timetable['section'] == student['section']) &
            (self.timetable['day'] == current_day)
        )
        
        day_schedule = self.timetable[mask]
        
        # Check time range
        # Assuming format "H:MM" or "HH:MM"
        current_dt = datetime.strptime(current_time, "%H:%M")
        
        for _, row in day_schedule.iterrows():
            start_dt = datetime.strptime(row['start'], "%H:%M")
            end_dt = datetime.strptime(row['end'], "%H:%M")
            
            if start_dt <= current_dt < end_dt:
                return row
                
        return None

    def check_truancy(self, student_id, current_room, current_day, current_time):
        """
        Checks if a student is truant.
        Returns (is_truant, status_message)
        """
        row = self._get_class_row(student_id, current_day, current_time)
        
        if row is None:
            return False, "Free Period"
            
        expected_room = row['room']
        subject = row['subject']
        
        if current_room == expected_room:
            return False, "On Time"
        else:
            return True, f"TRUANCY: Expected in {expected_room} for {subject}"

    def get_class_subject(self, student_id, current_day, current_time):
        """Returns the subject name for the current class, or None."""
        row = self._get_class_row(student_id, current_day, current_time)
        if row is not None:
            return row['subject']
        return None
