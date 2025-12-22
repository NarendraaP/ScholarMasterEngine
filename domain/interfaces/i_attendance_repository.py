"""
Domain Layer - Attendance Repository Interface

Abstract interface for attendance data persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from domain.entities import AttendanceRecord


class IAttendanceRepository(ABC):
    """
    Interface for attendance data storage operations.
    
    Implementations might use CSV, SQL, NoSQL, etc.
    """
    
    @abstractmethod
    def mark_present(self, record: AttendanceRecord) -> bool:
        """
        Record an attendance entry.
        
        Args:
            record: AttendanceRecord entity
            
        Returns:
            True if successfully recorded, False if duplicate
        """
        pass
    
    @abstractmethod
    def get_attendance(self, 
                      student_id: Optional[str] = None, 
                      date: Optional[str] = None,
                      subject: Optional[str] = None) -> List[AttendanceRecord]:
        """
        Query attendance records with optional filters.
        
        Args:
            student_id: Filter by student
            date: Filter by date (YYYY-MM-DD)
            subject: Filter by subject
            
        Returns:
            List of matching attendance records
        """
        pass
    
    @abstractmethod
    def is_already_marked(self, student_id: str, date: str, subject: str) -> bool:
        """
        Check if attendance is already marked (de-duplication).
        
        Args:
            student_id: Student identifier
            date: Date string (YYYY-MM-DD)
            subject: Subject name
            
        Returns:
            True if already marked
        """
        pass
