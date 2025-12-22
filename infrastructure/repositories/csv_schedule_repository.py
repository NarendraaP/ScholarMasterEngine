"""
Infrastructure Layer - CSV Schedule Repository

Implements IScheduleRepository using CSV file storage.
"""
from typing import List, Optional
from datetime import time, datetime
import pandas as pd
import os

from domain.entities import ScheduleEntry, TimeSlot, Student
from domain.interfaces import IScheduleRepository


class CsvScheduleRepository(IScheduleRepository):
    """
    CSV-based schedule repository.
    """
    
    def __init__(self, data_file: str = "data/timetable.csv"):
        self.data_file = data_file
        self._schedule = self._load()
    
    def get_schedule_for_student(self, student: Student, day: str) -> List[ScheduleEntry]:
        """Get student's schedule for a day"""
        results = []
        for entry in self._schedule:
            if entry.day == day and entry.matches_student(student):
                results.append(entry)
        return results
    
    def get_entry_at_time(self, student: Student, day: str, check_time: time) -> Optional[ScheduleEntry]:
        """Get schedule entry at specific time"""
        schedule = self.get_schedule_for_student(student, day)
        
        for entry in schedule:
            if entry.time_slot.contains(check_time):
                return entry
        
        return None
    
    def save_entry(self, entry: ScheduleEntry) -> bool:
        """Save schedule entry"""
        try:
            self._schedule.append(entry)
            self._persist()
            return True
        except Exception as e:
            print(f"Failed to save entry: {e}")
            return False
    
    def get_all(self) -> List[ScheduleEntry]:
        """Get all entries"""
        return self._schedule.copy()
    
    def delete_entry(self, day: str, time_start: time, room: str) -> bool:
        """Delete specific entry"""
        try:
            self._schedule = [
                entry for entry in self._schedule
                if not (entry.day == day and 
                       entry.time_slot.start == time_start and 
                       entry.room == room)
            ]
            self._persist()
            return True
        except Exception as e:
            print(f"Failed to delete entry: {e}")
            return False
    
    def _load(self) -> List[ScheduleEntry]:
        """Load from CSV"""
        if not os.path.exists(self.data_file):
            return []
        
        try:
            df = pd.read_csv(self.data_file)
            entries = []
            
            for _, row in df.iterrows():
                entry = self._row_to_entity(row)
                entries.append(entry)
            
            return entries
        except Exception as e:
            print(f"Failed to load schedule: {e}")
            return []
    
    def _persist(self):
        """Save to CSV"""
        try:
            data = [entry.to_dict() for entry in self._schedule]
            df = pd.DataFrame(data)
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            df.to_csv(self.data_file, index=False)
        except Exception as e:
            print(f"Failed to persist schedule: {e}")
    
    def _row_to_entity(self, row) -> ScheduleEntry:
        """Convert row to entity"""
        start_time = datetime.strptime(row["start"], "%H:%M").time()
        end_time = datetime.strptime(row["end"], "%H:%M").time()
        
        return ScheduleEntry(
            day=row["day"],
            time_slot=TimeSlot(start=start_time, end=end_time),
            faculty=row["faculty"],
            department=row["dept"],
            program=row["program"],
            year=int(row["year"]),
            section=row["section"],
            subject=row["subject"],
            teacher=row["teacher"],
            room=row["room"]
        )
