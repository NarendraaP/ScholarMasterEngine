"""
Infrastructure Layer - CSV Attendance Repository

Implements IAttendanceRepository using CSV file storage.
"""
from typing import List, Optional
import pandas as pd
import os
from datetime import datetime
from filelock import FileLock

from domain.entities import AttendanceRecord, AttendanceStatus
from domain.interfaces import IAttendanceRepository


class CsvAttendanceRepository(IAttendanceRepository):
    """
    CSV-based attendance repository with atomic writes.
    """
    
    def __init__(self, data_file: str = "data/attendance.csv"):
        self.data_file = data_file
        self._lock = FileLock(f"{data_file}.lock")
        self._ensure_file_exists()
    
    def mark_present(self, record: AttendanceRecord) -> bool:
        """Mark attendance with de-duplication"""
        try:
            # Check duplicate
            if self.is_already_marked(record.student_id, record.date, record.subject):
                return False
            
            with self._lock:
                # Load existing
                df = pd.read_csv(self.data_file)
                
                # Append new record
                new_row = record.to_dict()
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Atomic write
                temp_file = f"{self.data_file}.tmp"
                df.to_csv(temp_file, index=False)
                os.replace(temp_file, self.data_file)
            
            return True
        except Exception as e:
            print(f"Failed to mark attendance: {e}")
            return False
    
    def get_attendance(self, student_id: Optional[str] = None, 
                      date: Optional[str] = None, 
                      subject: Optional[str] = None) -> List[AttendanceRecord]:
        """Query attendance with filters"""
        try:
            df = pd.read_csv(self.data_file)
            
            # Apply filters
            if student_id:
                df = df[df["student_id"] == student_id]
            if date:
                df = df[df["date"] == date]
            if subject:
                df = df[df["subject"] == subject]
            
            # Convert to entities
            records = []
            for _, row in df.iterrows():
                record = self._row_to_entity(row)
                records.append(record)
            
            return records
        except Exception as e:
            print(f"Failed to get attendance: {e}")
            return []
    
    def is_already_marked(self, student_id: str, date: str, subject: str) -> bool:
        """Check for duplicate"""
        try:
            df = pd.read_csv(self.data_file)
            existing = df[
                (df["student_id"] == student_id) &
                (df["date"] == date) &
                (df["subject"] == subject)
            ]
            return not existing.empty
        except Exception:
            return False
    
    def _ensure_file_exists(self):
        """Create file with headers if not exists"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            columns = ["timestamp", "student_id", "student_name", "subject", "room", "status", "date"]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.data_file, index=False)
    
    def _row_to_entity(self, row) -> AttendanceRecord:
        """Convert DataFrame row to entity"""
        return AttendanceRecord(
            timestamp=datetime.fromisoformat(row["timestamp"]),
            student_id=row["student_id"],
            student_name=row["student_name"],
            subject=row["subject"],
            room=row["room"],
            status=AttendanceStatus(row["status"]),
            date=row["date"]
        )
