"""
Application Layer - Recognize Student Use Case

Identifies a student from face image using biometric matching.
"""
from typing import Tuple, Optional
import numpy as np

from domain.interfaces import IFaceRecognizer, IFaceIndex, IStudentRepository


class RecognizeStudentUseCase:
    """
    Use case for identifying a student from face image.
    
    Combines face detection, embedding extraction, and index search.
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
                threshold: float = 0.6) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Recognize student from image.
        
        Args:
            image: Image containing face
            threshold: Matching threshold (0-1)
            
        Returns:
            (found, student_id, student_data) tuple
        """
        try:
            # 1. Detect faces
            faces = self._face_recognizer.detect_faces(image)
            
            if len(faces) == 0:
                return False, None, None
            
            # Use first detected face
            face = faces[0]
            
            # 2. Search index
            found, student_id = self._face_index.search(face.embedding, threshold)
            
            if not found or student_id is None:
                return False, None, None
            
            # 3. Get student details
            student = self._student_repo.get_by_id(student_id)
            
            if student is None:
                # Inconsistency: in index but not in repository
                return False, student_id, None
            
            student_data = {
                "id": student.id,
                "name": student.name,
                "department": student.department,
                "program": student.program,
                "year": student.year,
                "section": student.section,
                "class": student.get_class_identifier()
            }
            
            return True, student_id, student_data
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return False, None, None
