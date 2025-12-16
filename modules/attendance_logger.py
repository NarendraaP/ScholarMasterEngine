import pandas as pd
import os
import datetime
import json

class AttendanceManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.attendance_path = os.path.join(data_dir, "attendance.csv")
        self.students_path = os.path.join(data_dir, "students.json")
        self.marked_sessions = set() # Cache: "StudentID_Date_Subject"
        self._load_cache()
        self.students = self._load_students()

    def _load_students(self):
        if os.path.exists(self.students_path):
            with open(self.students_path, "r") as f:
                return json.load(f)
        return {}

    def _load_cache(self):
        """Loads existing attendance to memory to prevent duplicates."""
        if os.path.exists(self.attendance_path):
            try:
                df = pd.read_csv(self.attendance_path)
                # Ensure columns exist
                required_cols = ["timestamp", "date", "student_id", "name", "subject", "room", "status"]
                if not set(required_cols).issubset(df.columns):
                    # Recreate if schema mismatch
                    df = pd.DataFrame(columns=required_cols)
                    df.to_csv(self.attendance_path, index=False)
                    return

                for _, row in df.iterrows():
                    # Key: StudentID_Date_Subject
                    key = f"{row['student_id']}_{row['date']}_{row['subject']}"
                    self.marked_sessions.add(key)
            except Exception as e:
                print(f"⚠️ Failed to load attendance cache: {e}")
        else:
            # Create file with headers
            df = pd.DataFrame(columns=["timestamp", "date", "student_id", "name", "subject", "room", "status"])
            df.to_csv(self.attendance_path, index=False)

    def mark_present(self, student_id, context_data, user_role=None):
        """
        Marks attendance if not already marked for this subject on this date.
        
        RBAC Protection: Only Admin and Faculty can modify attendance.
        
        Args:
            student_id: Student ID to mark present
            context_data: dict with 'subject', 'room', etc.
            user_role: Current user's role (if None, fetches from session_state)
        
        Returns: 
            str: "Marked Present", "Already Logged", or "Error"
        
        Raises:
            PermissionError: If user doesn't have Admin or Faculty role
        """
        # RBAC Backend Protection
        from modules.auth import validate_role
        validate_role(['Admin', 'Faculty'], user_role)
        
        subject = context_data.get("subject", "Unknown")
        room = context_data.get("room", "Unknown")
        
        # Get Date
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        
        # Construct Key
        key = f"{student_id}_{date_str}_{subject}"
        
        if key in self.marked_sessions:
            return "Already Logged"
        
        # Get Student Name
        student_name = self.students.get(student_id, {}).get("name", "Unknown")
        
        # Log to CSV
        timestamp = now.isoformat()
        new_entry = {
            "timestamp": timestamp,
            "date": date_str,
            "student_id": student_id,
            "name": student_name,
            "subject": subject,
            "room": room,
            "status": "Present"
        }
        
        try:
            # Atomic Append
            if os.path.exists(self.attendance_path):
                df = pd.read_csv(self.attendance_path)
            else:
                df = pd.DataFrame(columns=["timestamp", "date", "student_id", "name", "subject", "room", "status"])
                
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            
            # RCU Save
            temp_path = self.attendance_path + ".tmp"
            df.to_csv(temp_path, index=False)
            os.replace(temp_path, self.attendance_path)
            
            # Update Cache
            self.marked_sessions.add(key)
            print(f"✅ Attendance Marked: {student_name} ({student_id}) for {subject}")
            return "Marked Present"
            
        except Exception as e:
            print(f"❌ Failed to mark attendance: {e}")
            return "Error"

    def get_attendance(self, subject=None):
        """Returns attendance dataframe, optionally filtered by subject."""
        if os.path.exists(self.attendance_path):
            df = pd.read_csv(self.attendance_path)
            if subject:
                df = df[df["subject"] == subject]
            return df
        return pd.DataFrame()
