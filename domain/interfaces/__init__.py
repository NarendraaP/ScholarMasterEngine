"""Domain interfaces module"""
from domain.interfaces.i_face_recognizer import IFaceRecognizer, Face
from domain.interfaces.i_face_index import IFaceIndex
from domain.interfaces.i_student_repository import IStudentRepository
from domain.interfaces.i_attendance_repository import IAttendanceRepository
from domain.interfaces.i_schedule_repository import IScheduleRepository

__all__ = [
    'IFaceRecognizer',
    'Face',
    'IFaceIndex',
    'IStudentRepository',
    'IAttendanceRepository',
    'IScheduleRepository'
]
