"""
Domain Layer - Attendance Entity

Pure Python dataclass representing attendance records.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from domain.entities.student import Student


class AttendanceStatus(Enum):
    """Attendance status enumeration"""
    PRESENT = "Present"
    ABSENT = "Absent"
    TRUANT = "Truant"  # Present but in wrong location
    LATE = "Late"


@dataclass(frozen=True)
class AttendanceRecord:
    """
    Core business entity representing an attendance record.
    
    Immutable to maintain audit trail integrity.
    """
    timestamp: datetime
    student_id: str
    student_name: str
    subject: str
    room: str
    status: AttendanceStatus
    date: str  # YYYY-MM-DD format
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.student_id:
            raise ValueError("Student ID cannot be empty")
        if not self.subject:
            raise ValueError("Subject cannot be empty")
        
    def is_compliant(self) -> bool:
        """Check if attendance is compliant (present in correct location)"""
        return self.status == AttendanceStatus.PRESENT
    
    def to_dict(self) -> dict:
        """Convert to dictionary for persistence"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "student_id": self.student_id,
            "student_name": self.student_name,
            "subject": self.subject,
            "room": self.room,
            "status": self.status.value,
            "date": self.date
        }
