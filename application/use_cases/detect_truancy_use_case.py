"""
Application Layer - Detect Truancy Use Case

Checks if a student is in the correct location based on schedule.
"""
from datetime import datetime, time
from typing import Tuple, Optional

from domain.entities import Student
from domain.interfaces import IStudentRepository, IScheduleRepository


class DetectTruancyUseCase:
    """
    Use case for detecting truancy (wrong location).
    
    Compares student's current location against their schedule.
    """
    
    def __init__(self,
                 student_repo: IStudentRepository,
                 schedule_repo: IScheduleRepository,
                 debounce_threshold: int = 30):
        self._student_repo = student_repo
        self._schedule_repo = schedule_repo
        self._violation_counters = {}  # {student_id: consecutive_violation_count}
        self._debounce_threshold = debounce_threshold  # 30 frames = ~30s at 1Hz
    
    def execute(self,
                student_id: str,
                current_location: str,
                day: str,
                check_time: Optional[time] = None) -> Tuple[bool, str, Optional[dict]]:
        """
        Check if student is in correct location.
        
        Args:
            student_id: Student identifier
            current_location: Where student currently is
            day: Day of week ("Mon", "Tue", etc.)
            check_time: Time to check (defaults to now)
            
        Returns:
            (is_compliant, message, session_data) tuple
        """
        try:
            # 1. Get student
            student = self._student_repo.get_by_id(student_id)
            if not student:
                return False, f"Student {student_id} not found", None
            
            # 2. Get expected schedule
            if check_time is None:
                check_time = datetime.now().time()
            
            expected_entry = self._schedule_repo.get_entry_at_time(student, day, check_time)
            
            if expected_entry is None:
                # No class scheduled - free period
                return True, "Free Period", None
            
            # 3. Check location compliance
            expected_room = expected_entry.room
            
            session_data = {
                "subject": expected_entry.subject,
                "room": expected_room,
                "teacher": expected_entry.teacher,
                "time": str(expected_entry.time_slot)
            }
            
            if current_location == expected_room:
                # Reset violation counter on compliance
                self._violation_counters[student_id] = 0
                return True, "Compliant", session_data
            else:
                # Increment violation counter
                self._violation_counters[student_id] = self._violation_counters.get(student_id, 0) + 1
                
                # Only trigger alert if violation persists beyond threshold (debounce)
                if self._violation_counters[student_id] >= self._debounce_threshold:
                    message = f"PERSISTENT TRUANCY: Expected in {expected_room} for {expected_entry.subject}, found in {current_location} (verified {self._debounce_threshold}+ times)"
                    return False, message, session_data
                else:
                    # Transient violation - still counting
                    transient_msg = f"Potential mismatch detected ({self._violation_counters[student_id]}/{self._debounce_threshold})"
                    return True, transient_msg, session_data  # Return True to avoid premature alerts
                
        except Exception as e:
            return False, f"Truancy check failed: {str(e)}", None
