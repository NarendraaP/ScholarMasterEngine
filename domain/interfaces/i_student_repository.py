"""
Domain Layer - Student Repository Interface

Abstract interface for student data persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Student


class IStudentRepository(ABC):
    """
    Interface for student data storage operations.
    
    Implementations might use JSON, SQL, NoSQL, etc.
    """
    
    @abstractmethod
    def get_by_id(self, student_id: str) -> Optional[Student]:
        """
        Retrieve a student by ID.
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            Student entity or None if not found
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Student]:
        """Get all students"""
        pass
    
    @abstractmethod
    def save(self, student: Student) -> bool:
        """
        Persist a student entity.
        
        Args:
            student: Student entity to save
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def delete(self, student_id: str) -> bool:
        """Delete a student by ID"""
        pass
    
    @abstractmethod
    def find_by_class(self, department: str, program: str, year: int, section: str) -> List[Student]:
        """Find all students in a specific class"""
        pass
