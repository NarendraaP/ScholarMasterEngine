"""
Domain Layer - Face Recognizer Interface

Abstract interface for face recognition capabilities.
No implementation details - pure abstraction.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class Face:
    """Simple data structure for face information"""
    def __init__(self, bbox: Tuple[int, int, int, int], embedding: np.ndarray, confidence: float = 1.0):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.embedding = embedding
        self.confidence = confidence


class IFaceRecognizer(ABC):
    """
    Interface for face recognition operations.
    
    Implementations might use InsightFace, FaceNet, etc.
    Domain layer doesn't care about the implementation.
    """
    
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> List[Face]:
        """
        Detect all faces in an image.
        
        Args:
            image: NumPy array in BGR format
            
        Returns:
            List of Face objects with bounding boxes and embeddings
        """
        pass
    
    @abstractmethod
    def extract_embedding(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract face embedding from a specific region.
        
        Args:
            image: NumPy array in BGR format
            bbox: Bounding box (x1, y1, x2, y2)
            
        Returns:
            512-dimensional embedding vector
        """
        pass
