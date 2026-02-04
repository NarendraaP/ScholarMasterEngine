"""
Schedule Repository Interface (Port)

Abstracts timetable data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import time
from dataclasses import dataclass


@dataclass
class ScheduleEntry:
    """Single timetable entry"""
    day: str  # "Mon", "Tue", etc.
    start_time: time
    end_time: time
    subject: str
    teacher: str
    room: str
    dept: str
    program: str  # "UG", "PG"
    year: int  # 1-4
    section: str  # "A", "B", "C"
    
    def is_active_at(self, day: str, check_time: time) -> bool:
        """Check if this entry is active at given time"""
        return (self.day == day and 
                self.start_time <= check_time < self.end_time)


class IScheduleRepository(ABC):
    """
    Port for schedule data access.
    
    Implementations: CSV, Database
    """
    
    @abstractmethod
    def get_entry_at_time(
        self,
        dept: str,
        program: str,
        year: int,
        section: str,
        day: str,
        check_time: time
    ) -> Optional[ScheduleEntry]:
        """
        Get schedule entry for class at given time.
        
        Args:
            dept: Department (e.g., "Computer Science")
            program: Program (e.g., "UG", "PG")
            year: Year (1-4)
            section: Section ("A", "B", "C")
            day: Day of week
            check_time: Time to check
            
        Returns:
            ScheduleEntry if class scheduled, None if free period
        """
        pass
    
    @abstractmethod
    def get_all_for_day(self, day: str) -> List[ScheduleEntry]:
        """Get all schedule entries for a day"""
        pass
    
    @abstractmethod
    def is_lecture_mode(self, room: str, day: str, check_time: time) -> bool:
        """
        Check if room is in lecture mode.
        
        Returns:
            True if class is active in room
        """
        pass
