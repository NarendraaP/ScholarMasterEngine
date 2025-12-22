"""
Domain Layer - Schedule Entity

Pure Python dataclass representing schedule/timetable entries.
"""
from dataclasses import dataclass
from datetime import time
from typing import Optional


@dataclass(frozen=True)
class TimeSlot:
    """Value object representing a time slot"""
    start: time
    end: time
    
    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")
    
    def contains(self, check_time: time) -> bool:
        """Check if a time falls within this slot"""
        return self.start <= check_time < self.end
    
    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"


@dataclass(frozen=True)
class ScheduleEntry:
    """
    Core business entity representing a scheduled class.
    
    Immutable to prevent schedule corruption.
    """
    day: str  # "Mon", "Tue", etc.
    time_slot: TimeSlot
    faculty: str
    department: str
    program: str  # "UG", "PG"
    year: int
    section: str
    subject: str
    teacher: str
    room: str
    
    def __post_init__(self):
        """Validate business rules"""
        valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        if self.day not in valid_days:
            raise ValueError(f"Invalid day: {self.day}")
        if not self.room:
            raise ValueError("Room cannot be empty")
        if not self.subject:
            raise ValueError("Subject cannot be empty")
    
    def matches_student(self, student) -> bool:
        """Check if this schedule entry applies to a student"""
        return (
            self.department == student.department and
            self.program == student.program and
            self.year == student.year and
            self.section == student.section
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for persistence"""
        return {
            "day": self.day,
            "start": self.time_slot.start.strftime("%H:%M"),
            "end": self.time_slot.end.strftime("%H:%M"),
            "faculty": self.faculty,
            "dept": self.department,
            "program": self.program,
            "year": self.year,
            "section": self.section,
            "subject": self.subject,
            "teacher": self.teacher,
            "room": self.room
        }
