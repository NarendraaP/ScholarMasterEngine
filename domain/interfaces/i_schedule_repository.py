"""
Domain Layer - Schedule Repository Interface

Abstract interface for schedule/timetable data persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import time
from domain.entities import ScheduleEntry, Student


class IScheduleRepository(ABC):
    """
    Interface for schedule data storage operations.
    
    Implementations might use CSV, SQL, iCal, etc.
    """
    
    @abstractmethod
    def get_schedule_for_student(self, student: Student, day: str) -> List[ScheduleEntry]:
        """
        Get all scheduled classes for a student on a specific day.
        
        Args:
            student: Student entity
            day: Day of week ("Mon", "Tue", etc.)
            
        Returns:
            List of ScheduleEntry objects for that day
        """
        pass
    
    @abstractmethod
    def get_entry_at_time(self, student: Student, day: str, check_time: time) -> Optional[ScheduleEntry]:
        """
        Get the scheduled class for a student at a specific time.
        
        Args:
            student: Student entity
            day: Day of week
            check_time: Time to check
            
        Returns:
            ScheduleEntry if found, None if no class at that time
        """
        pass
    
    @abstractmethod
    def save_entry(self, entry: ScheduleEntry) -> bool:
        """Save a schedule entry"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[ScheduleEntry]:
        """Get all schedule entries"""
        pass
    
    @abstractmethod
    def delete_entry(self, day: str, time_start: time, room: str) -> bool:
        """Delete a specific schedule entry"""
        pass
