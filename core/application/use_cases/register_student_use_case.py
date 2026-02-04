"""
Application Layer - Register Student Use Case

Orchestrates the business logic for registering a new student.
"""
from typing import Tuple
import numpy as np

from domain.entities import Student
from domain.interfaces import IFaceRecognizer, IFaceIndex, IStudentRepository


class RegisterStudentUseCase:
    """
    Use case for registering a student with biometric data.
    
    Follows Single Responsibility Principle - only handles registration logic.
    Dependencies are injected as interfaces.
    """
    
    def __init__(self,
                 face_recognizer: IFaceRecognizer,
                 face_index: IFaceIndex,
                 student_repo: IStudentRepository):
        self._face_recognizer = face_recognizer
        self._face_index = face_index
        self._student_repo = student_repo
    
    def execute(self, 
                image: np.ndarray,
                student_id: str,
                name: str,
                role: str,
                department: str,
                program: str,
                year: int,
                section: str) -> Tuple[bool, str]:
        """
        Register a student with face biometric.
        
        Args:
            image: Image containing student's face
            student_id: Unique identifier
            name: Student name
            role: Role (e.g., "Student")
            department: Department code
            program: "UG" or "PG"
            year: Year (1-4)
            section: Section ("A", "B", "C")
            
        Returns:
            (success, message) tuple
        """
        try:
            # 1. Validate business rules via domain entity
            student = Student(
                id=student_id,
                name=name,
                role=role,
                department=department,
                program=program,
                year=year,
                section=section
            )
            
            # 2. Detect face in image
            faces = self._face_recognizer.detect_faces(image)
            
            if len(faces) == 0:
                return False, "No face detected in the image"
            
            if len(faces) > 1:
                return False, "Multiple faces detected. Please provide image with single face"
            
            face = faces[0]
            
            # 3. Add embedding to index
            success = self._face_index.add_embedding(student_id, face.embedding)
            
            if not success:
                return False, "Failed to index face embedding"
            
            # 4. Persist student data
            saved = self._student_repo.save(student)
            
            if not saved:
                # Rollback face index
                self._face_index.remove_embedding(student_id)
                return False, "Failed to save student data"
            
            return True, f"Successfully registered {name} (ID: {student_id})"
            
        except ValueError as e:
            # Domain validation failed
            return False, f"Validation error: {str(e)}"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
