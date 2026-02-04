"""
Application Layer - Mark Attendance Use Case

Orchestrates attendance marking logic with de-duplication and validation.
"""
from datetime import datetime
from typing import Tuple

from domain.entities import AttendanceRecord, AttendanceStatus
from domain.interfaces import IAttendanceRepository, IStudentRepository


class MarkAttendanceUseCase:
    """
    Use case for marking student attendance.
    
    Handles business rules:
    - De-duplication (can't mark twice for same subject/day)
    - Validates student exists
    - Records with proper status
    """
    
    def __init__(self,
                 attendance_repo: IAttendanceRepository,
                 student_repo: IStudentRepository):
        self._attendance_repo = attendance_repo
        self._student_repo = student_repo
    
    def execute(self,
                student_id: str,
                subject: str,
                room: str,
                is_truant: bool = False) -> Tuple[bool, str]:
        """
        Mark attendance for a student.
        
        Args:
            student_id: Student identifier
            subject: Subject name
            room: Room/location
            is_truant: True if student is in wrong location
            
        Returns:
            (success, message) tuple
        """
        try:
            # 1. Verify student exists
            student = self._student_repo.get_by_id(student_id)
            if not student:
                return False, f"Student {student_id} not found"
            
            # 2. Check for duplicates
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            
            if self._attendance_repo.is_already_marked(student_id, date_str, subject):
                return False, f"Attendance already marked for {student.name} in {subject} today"
            
            # 3. Determine status
            status = AttendanceStatus.TRUANT if is_truant else AttendanceStatus.PRESENT
            
            # 4. Create attendance record (domain entity)
            record = AttendanceRecord(
                timestamp=now,
                student_id=student_id,
                student_name=student.name,
                subject=subject,
                room=room,
                status=status,
                date=date_str
            )
            
            # 5. Persist
            success = self._attendance_repo.mark_present(record)
            
            if success:
                status_msg = "Truancy recorded" if is_truant else "Present"
                return True, f"Attendance marked: {student.name} - {status_msg}"
            else:
                return False, "Failed to save attendance record"
                
        except ValueError as e:
            return False, f"Validation error: {str(e)}"
        except Exception as e:
            return False, f"Attendance marking failed: {str(e)}"
