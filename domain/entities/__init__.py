"""Domain entities module"""
from domain.entities.student import Student
from domain.entities.attendance import AttendanceRecord, AttendanceStatus
from domain.entities.schedule import ScheduleEntry, TimeSlot

__all__ = [
    'Student',
    'AttendanceRecord',
    'AttendanceStatus',
    'ScheduleEntry',
    'TimeSlot'
]
