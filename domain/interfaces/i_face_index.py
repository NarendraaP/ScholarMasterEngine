"""
Domain Layer - Face Index Interface

Abstract interface for face vector storage and retrieval.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import numpy as np


class IFaceIndex(ABC):
    """
    Interface for face embedding storage and similarity search.
    
    Implementations might use FAISS, Annoy, Milvus, etc.
    """
    
    @abstractmethod
    def add_embedding(self, student_id: str, embedding: np.ndarray) -> bool:
        """
        Add a face embedding to the index.
        
        Args:
            student_id: Unique identifier for the student
            embedding: 512-dimensional face embedding vector
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def search(self, embedding: np.ndarray, threshold: float = 0.6) -> Tuple[bool, Optional[str]]:
        """
        Search for the closest match to an embedding.
        
        Args:
            embedding: Query embedding vector
            threshold: Similarity threshold (0-1)
            
        Returns:
            (found, student_id) tuple
        """
        pass
    
    @abstractmethod
    def remove_embedding(self, student_id: str) -> bool:
        """Remove an embedding from the index"""
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        """Get total number of indexed faces"""
        pass
