"""
Unit tests for Clean Architecture use cases.

Demonstrates:
- Proper mocking of dependencies
- Testing business logic in isolation
- Benefits of dependency injection
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from datetime import datetime

from domain.entities import Student, AttendanceRecord, AttendanceStatus
from domain.interfaces import IFaceRecognizer, IFaceIndex, IStudentRepository, IAttendanceRepository
from application.use_cases import (
    RegisterStudentUseCase,
    MarkAttendanceUseCase,
    RecognizeStudentUseCase
)


class TestRegisterStudentUseCase:
    """Test student registration use case"""
    
    def setup_method(self):
        """Setup mocks before each test"""
        self.mock_recognizer = Mock(spec=IFaceRecognizer)
        self.mock_index = Mock(spec=IFaceIndex)
        self.mock_repo = Mock(spec=IStudentRepository)
        
        self.use_case = RegisterStudentUseCase(
            self.mock_recognizer,
            self.mock_index,
            self.mock_repo
        )
    
    def test_register_student_success(self):
        """Test successful student registration"""
        # Arrange
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        embedding = np.random.rand(512).astype('float32')
        
        # Mock face detection - return one face
        from domain.interfaces.i_face_recognizer import Face
        mock_face = Face(bbox=(10, 10, 100, 100), embedding=embedding)
        self.mock_recognizer.detect_faces.return_value = [mock_face]
        
        # Mock successful index addition
        self.mock_index.add_embedding.return_value = True
        
        # Mock successful save
        self.mock_repo.save.return_value = True
        
        # Act
        success, message = self.use_case.execute(
            image=image,
            student_id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=1,
            section="A"
        )
        
        # Assert
        assert success is True
        assert "Successfully registered" in message
        self.mock_recognizer.detect_faces.assert_called_once()
        self.mock_index.add_embedding.assert_called_once()
        self.mock_repo.save.assert_called_once()
    
    def test_register_student_no_face_detected(self):
        """Test registration failure when no face detected"""
        # Arrange
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        self.mock_recognizer.detect_faces.return_value = []
        
        # Act
        success, message = self.use_case.execute(
            image=image,
            student_id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=1,
            section="A"
        )
        
        # Assert
        assert success is False
        assert "No face detected" in message
        self.mock_index.add_embedding.assert_not_called()
    
    def test_register_student_invalid_year(self):
        """Test validation: invalid year should fail"""
        # Arrange
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        
        # Act
        success, message = self.use_case.execute(
            image=image,
            student_id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=5,  # Invalid!
            section="A"
        )
        
        # Assert
        assert success is False
        assert "Validation error" in message


class TestMarkAttendanceUseCase:
    """Test attendance marking use case"""
    
    def setup_method(self):
        """Setup mocks before each test"""
        self.mock_attendance_repo = Mock(spec=IAttendanceRepository)
        self.mock_student_repo = Mock(spec=IStudentRepository)
        
        self.use_case = MarkAttendanceUseCase(
            self.mock_attendance_repo,
            self.mock_student_repo
        )
    
    def test_mark_attendance_success(self):
        """Test successful attendance marking"""
        # Arrange
        student = Student(
            id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=1,
            section="A"
        )
        
        self.mock_student_repo.get_by_id.return_value = student
        self.mock_attendance_repo.is_already_marked.return_value = False
        self.mock_attendance_repo.mark_present.return_value = True
        
        # Act
        success, message = self.use_case.execute(
            student_id="S101",
            subject="Math",
            room="Room-101"
        )
        
        # Assert
        assert success is True
        assert "Attendance marked" in message
        self.mock_attendance_repo.mark_present.assert_called_once()
    
    def test_mark_attendance_student_not_found(self):
        """Test failure when student doesn't exist"""
        # Arrange
        self.mock_student_repo.get_by_id.return_value = None
        
        # Act
        success, message = self.use_case.execute(
            student_id="S999",
            subject="Math",
            room="Room-101"
        )
        
        # Assert
        assert success is False
        assert "not found" in message
    
    def test_mark_attendance_duplicate(self):
        """Test de-duplication: already marked"""
        # Arrange
        student = Student(
            id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=1,
            section="A"
        )
        
        self.mock_student_repo.get_by_id.return_value = student
        self.mock_attendance_repo.is_already_marked.return_value = True
        
        # Act
        success, message = self.use_case.execute(
            student_id="S101",
            subject="Math",
            room="Room-101"
        )
        
        # Assert
        assert success is False
        assert "already marked" in message.lower()


class TestRecognizeStudentUseCase:
    """Test student recognition use case"""
    
    def setup_method(self):
        """Setup mocks before each test"""
        self.mock_recognizer = Mock(spec=IFaceRecognizer)
        self.mock_index = Mock(spec=IFaceIndex)
        self.mock_student_repo = Mock(spec=IStudentRepository)
        
        self.use_case = RecognizeStudentUseCase(
            self.mock_recognizer,
            self.mock_index,
            self.mock_student_repo
        )
    
    def test_recognize_student_success(self):
        """Test successful student recognition"""
        # Arrange
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        embedding = np.random.rand(512).astype('float32')
        
        from domain.interfaces.i_face_recognizer import Face
        mock_face = Face(bbox=(10, 10, 100, 100), embedding=embedding)
        self.mock_recognizer.detect_faces.return_value = [mock_face]
        
        # Mock successful search
        self.mock_index.search.return_value = (True, "S101")
        
        # Mock student data
        student = Student(
            id="S101",
            name="John Doe",
            role="Student",
            department="CS",
            program="UG",
            year=1,
            section="A"
        )
        self.mock_student_repo.get_by_id.return_value = student
        
        # Act
        found, student_id, student_data = self.use_case.execute(image)
        
        # Assert
        assert found is True
        assert student_id == "S101"
        assert student_data["name"] == "John Doe"
    
    def test_recognize_student_not_found(self):
        """Test when student not in index"""
        # Arrange
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        embedding = np.random.rand(512).astype('float32')
        
        from domain.interfaces.i_face_recognizer import Face
        mock_face = Face(bbox=(10, 10, 100, 100), embedding=embedding)
        self.mock_recognizer.detect_faces.return_value = [mock_face]
        
        # Mock search failure
        self.mock_index.search.return_value = (False, None)
        
        # Act
        found, student_id, student_data = self.use_case.execute(image)
        
        # Assert
        assert found is False
        assert student_id is None
        assert student_data is None
