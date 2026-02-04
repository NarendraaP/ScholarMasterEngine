"""
Schedule Repository - Infrastructure Adapter

Implements IScheduleRepository using CSV storage.
"""
from typing import List, Optional
from datetime import time, datetime
import pandas as pd
import os

from core.interfaces.i_schedule_repository import IScheduleRepository, ScheduleEntry


class CSVScheduleRepository(IScheduleRepository):
    """
    CSV-based schedule repository.
    
    Loads timetable from data/timetable.csv
    """
    
    def __init__(self, timetable_path="data/timetable.csv"):
        """Load timetable from CSV"""
        self.timetable_path = timetable_path
        
        if os.path.exists(timetable_path):
            self.timetable = pd.read_csv(timetable_path)
            
            # Normalize column names
            self.timetable.columns = self.timetable.columns.str.strip().str.lower()
            
            print(f"✅ Loaded timetable with {len(self.timetable)} entries")
        else:
            self.timetable = pd.DataFrame()
            print(f"⚠️  Timetable not found at {timetable_path}")
    
    def get_entry_at_time(
        self,
        dept: str,
        program: str,
        year: int,
        section: str,
        day: str,
        check_time: time
    ) -> Optional[ScheduleEntry]:
        """Get schedule entry for class at given time"""
        if self.timetable.empty:
            return None
        
        # Filter by class (dept, program, year, section)
        filtered = self.timetable[
            (self.timetable['dept'] == dept) &
            (self.timetable['program'] == program) &
            (self.timetable['year'] == year) &
            (self.timetable['section'] == section) &
            (self.timetable['day'] == day)
        ]
        
        # Check if any entry is active at check_time
        for _, row in filtered.iterrows():
            try:
                start_time = datetime.strptime(row['start'], "%H:%M").time()
                end_time = datetime.strptime(row['end'], "%H:%M").time()
                
                if start_time <= check_time < end_time:
                    # Found active entry
                    return ScheduleEntry(
                        day=row['day'],
                        start_time=start_time,
                        end_time=end_time,
                        subject=row['subject'],
                        teacher=row['teacher'],
                        room=row['room'],
                        dept=row['dept'],
                        program=row['program'],
                        year=row['year'],
                        section=row['section']
                    )
            except (ValueError, KeyError):
                continue
        
        return None  # Free period
    
    def get_all_for_day(self, day: str) -> List[ScheduleEntry]:
        """Get all schedule entries for a day"""
        if self.timetable.empty:
            return []
        
        filtered = self.timetable[self.timetable['day'] == day]
        
        entries = []
        for _, row in filtered.iterrows():
            try:
                entry = ScheduleEntry(
                    day=row['day'],
                    start_time=datetime.strptime(row['start'], "%H:%M").time(),
                    end_time=datetime.strptime(row['end'], "%H:%M").time(),
                    subject=row['subject'],
                    teacher=row['teacher'],
                    room=row['room'],
                    dept=row['dept'],
                    program=row['program'],
                    year=row['year'],
                    section=row['section']
                )
                entries.append(entry)
            except (ValueError, KeyError):
                continue
        
        return entries
    
    def is_lecture_mode(self, room: str, day: str, check_time: time) -> bool:
        """Check if room is in lecture mode"""
        if self.timetable.empty:
            return False
        
        # Filter by room and day
        room_schedule = self.timetable[
            (self.timetable['room'] == room) &
            (self.timetable['day'] == day)
        ]
        
        # Check if any class is active
        for _, row in room_schedule.iterrows():
            try:
                start_time = datetime.strptime(row['start'], "%H:%M").time()
                end_time = datetime.strptime(row['end'], "%H:%M").time()
                
                if start_time <= check_time < end_time:
                    return True  # Class is active
            except (ValueError, KeyError):
                continue
        
        return False  # Break time
