"""Application use cases module"""
from application.use_cases.register_student_use_case import RegisterStudentUseCase
from application.use_cases.mark_attendance_use_case import MarkAttendanceUseCase
from application.use_cases.detect_truancy_use_case import DetectTruancyUseCase
from application.use_cases.recognize_student_use_case import RecognizeStudentUseCase

__all__ = [
    'RegisterStudentUseCase',
    'MarkAttendanceUseCase',
    'DetectTruancyUseCase',
    'RecognizeStudentUseCase'
]
