"""
Domain Layer - Student Entity

Pure Python dataclass with no external dependencies.
Represents a student in the Scholar Master system.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Student:
    """
    Core business entity representing a student.
    
    Immutable to ensure data integrity across the system.
    """
    id: str
    name: str
    role: str  # "Student", "Faculty", etc.
    department: str
    program: str  # "UG", "PG"
    year: int
    section: str  # "A", "B", "C"
    privacy_hash: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.id:
            raise ValueError("Student ID cannot be empty")
        if not self.name:
            raise ValueError("Student name cannot be empty")
        if self.year not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid year: {self.year}. Must be 1-4")
        if self.section not in ["A", "B", "C"]:
            raise ValueError(f"Invalid section: {self.section}")
    
    def get_class_identifier(self) -> str:
        """Returns unique class identifier: DEPT-PROGRAM-YEAR-SECTION"""
        return f"{self.department}-{self.program}-{self.year}-{self.section}"
