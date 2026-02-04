"""
Face Recognizer Interface (Port)

Abstracts face detection and recognition infrastructure.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class Face:
    """Face detection result"""
    bbox: np.ndarray  # [x1, y1, x2, y2]
    embedding: np.ndarray  # 512-dim vector
    confidence: float
    landmarks: Optional[np.ndarray] = None


class IFaceRecognizer(ABC):
    """
    Port for face recognition infrastructure.
    
    Implementations: InsightFace + FAISS (Paper 1)
    """
    
    @abstractmethod
    def detect_faces(self, frame: np.ndarray) -> List[Face]:
        """
        Detect all faces in frame.
        
        Args:
            frame: RGB image (H x W x 3)
            
        Returns:
            List of detected faces with embeddings
        """
        pass
    
    @abstractmethod
    def search_face(self, embedding: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Search for face in gallery.
        
        Args:
            embedding: 512-dim face vector
            
        Returns:
            (found, student_id) tuple
            - found: True if match found (above adaptive threshold)
            - student_id: Matched student ID or None
        """
        pass
    
    @abstractmethod
    def enroll_face(self, student_id: str, embedding: np.ndarray) -> bool:
        """
        Add face to gallery.
        
        Args:
            student_id: Unique student identifier
            embedding: 512-dim face vector
            
        Returns:
            True if enrolled successfully
        """
        pass
    
    @abstractmethod
    def get_gallery_size(self) -> int:
        """Get number of enrolled faces"""
        pass
