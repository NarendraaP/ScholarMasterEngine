"""
Test for Debounce Logic in DetectTruancyUseCase

Verifies that the sanitization/debounce mechanism filters transient
violations as described in Paper 4, Algorithm 1.
"""
import pytest
from datetime import time
from application.use_cases import DetectTruancyUseCase
from domain.entities import Student, ScheduleEntry, TimeSlot
from infrastructure.repositories import JsonStudentRepository, CsvScheduleRepository


class TestDebounceLogic:
    """Test debounce/sanitization filtering"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.student_repo = JsonStudentRepository("data/students.json")
        self.schedule_repo = CsvScheduleRepository("data/timetable.csv")
        self.use_case = DetectTruancyUseCase(
            self.student_repo,
            self.schedule_repo,
            debounce_threshold=5  # Lower threshold for faster testing
        )
    
    def test_transient_violation_ignored(self):
        """Test that brief violations don't trigger alerts"""
        student_id = "CSE001"
        wrong_location = "Canteen"
        day = "Mon"
        check_time = time(10, 30)  # Should be in class
        
        # First 4 detections in wrong location
        for i in range(4):
            is_compliant, message, _ = self.use_case.execute(
                student_id, wrong_location, day, check_time
            )
            # Should NOT trigger alert yet
            assert is_compliant is True, f"Iteration {i+1}: Should not alert before threshold"
            assert "Potential mismatch" in message
            assert f"({i+1}/5)" in message
    
    def test_persistent_violation_triggers_alert(self):
        """Test that sustained violations trigger alerts"""
        student_id = "CSE001"
        wrong_location = "Canteen"
        day = "Mon"
        check_time = time(10, 30)
        
        # 5th detection should trigger alert
        for i in range(5):
            is_compliant, message, _ = self.use_case.execute(
                student_id, wrong_location, day, check_time
            )
            
            if i < 4:
                assert is_compliant is True
            else:
                # 5th check should trigger
                assert is_compliant is False
                assert "PERSISTENT TRUANCY" in message
                assert "(verified 5+ times)" in message
    
    def test_compliance_resets_counter(self):
        """Test that returning to correct location resets counter"""
        student_id = "CSE001"
        wrong_location = "Canteen"
        correct_location = "CSE Lab A"  # Assuming this is scheduled
        day = "Mon"
        check_time = time(10, 30)
        
        # Build up violations
        for _ in range(3):
            self.use_case.execute(student_id, wrong_location, day, check_time)
        
        # Return to compliance - should reset
        is_compliant, message, _ = self.use_case.execute(
            student_id, correct_location, day, check_time
        )
        assert is_compliant is True
        assert message == "Compliant"
        
        # Now violations should start from 0 again
        is_compliant, message, _ = self.use_case.execute(
            student_id, wrong_location, day, check_time
        )
        assert "(1/5)" in message  # Counter reset
    
    def test_different_students_independent_counters(self):
        """Test that each student has independent violation tracking"""
        student1 = "CSE001"
        student2 = "CSE002"
        wrong_location = "Canteen"
        day = "Mon"
        check_time = time(10, 30)
        
        # Student 1: 3 violations
        for _ in range(3):
            self.use_case.execute(student1, wrong_location, day, check_time)
        
        # Student 2: 1 violation
        _, msg, _ = self.use_case.execute(student2, wrong_location, day, check_time)
        
        # Student 2 should be at (1/5), not (4/5)
        assert "(1/5)" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
