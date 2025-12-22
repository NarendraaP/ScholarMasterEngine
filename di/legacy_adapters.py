"""
Compatibility Adapter

Provides a backward-compatible interface for existing code
while using Clean Architecture under the hood.

This allows gradual migration without breaking existing functionality.
"""
from typing import Tuple, Optional
import numpy as np

from di.container import get_container


class LegacyFaceRegistry:
    """
    Compatibility adapter for old FaceRegistry API.
    
    Wraps Clean Architecture use cases to provide the same interface
    as the legacy modules/face_registry.py
    """
    
    def __init__(self):
        self._container = get_container()
    
    def register_face(self, image_array, user_id, name, role, dept=None, user_role=None) -> Tuple[bool, str]:
        """
        Legacy API: register_face
        
        Delegates to RegisterStudentUseCase under the hood.
        """
        # Parse department info (legacy format)
        if dept:
            parts = dept.split('-')
            if len(parts) >= 4:
                department = parts[0]
                program = parts[1]
                year = int(parts[2])
                section = parts[3]
            else:
                department = dept
                program = "UG"
                year = 1
                section = "A"
        else:
            department = "CS"
            program = "UG"
            year = 1
            section = "A"
        
        # Call new use case
        return self._container.register_student.execute(
            image=image_array,
            student_id=user_id,
            name=name,
            role=role,
            department=department,
            program=program,
            year=year,
            section=section
        )
    
    def search_face(self, embedding: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Legacy API: search_face
        
        Delegates to face index.
        """
        return self._container.face_index.search(embedding, threshold=0.6)


class LegacyAttendanceManager:
    """
    Compatibility adapter for old AttendanceManager API.
    """
    
    def __init__(self):
        self._container = get_container()
    
    def mark_present(self, student_id: str, context_data: dict, user_role: Optional[str] = None) -> str:
        """
        Legacy API: mark_present
        
        Delegates to MarkAttendanceUseCase.
        """
        subject = context_data.get("subject", "Unknown")
        room = context_data.get("room", "Unknown")
        
        success, message = self._container.mark_attendance.execute(
            student_id=student_id,
            subject=subject,
            room=room,
            is_truant=False
        )
        
        if success:
            return "Marked Present"
        else:
            return message


class LegacyContextEngine:
    """
    Compatibility adapter for old ContextEngine API.
    """
    
    def __init__(self):
        self._container = get_container()
    
    def check_compliance(self, student_id: str, current_location: str, day: str = None, check_time=None):
        """
        Legacy API: check_compliance
        
        Delegates to DetectTruancyUseCase.
        """
        import datetime
        if day is None:
            day = datetime.datetime.now().strftime("%a")[:3]
        
        is_compliant, message, session_data = self._container.detect_truancy.execute(
            student_id=student_id,
            current_location=current_location,
            day=day,
            check_time=check_time
        )
        
        return session_data if is_compliant else None


# For easy import compatibility
class FaceRegistry(LegacyFaceRegistry):
    pass


class AttendanceManager(LegacyAttendanceManager):
    pass


class ContextEngine(LegacyContextEngine):
    pass
