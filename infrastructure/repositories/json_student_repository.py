"""
Infrastructure Layer - JSON Student Repository

Implements IStudentRepository using JSON file storage.
"""
from typing import List, Optional
import json
import os

from domain.entities import Student
from domain.interfaces import IStudentRepository


class JsonStudentRepository(IStudentRepository):
    """
    JSON file-based student repository.
    
    Persists student data to data/students.json
    """
    
    def __init__(self, data_file: str = "data/students.json"):
        """
        Initialize repository.
        
        Args:
            data_file: Path to JSON file
        """
        self.data_file = data_file
        self._students = self._load()
    
    def get_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        data = self._students.get(student_id)
        if data is None:
            return None
        
        return self._dict_to_entity(data)
    
    def get_all(self) -> List[Student]:
        """Get all students"""
        return [self._dict_to_entity(data) for data in self._students.values()]
    
    def save(self, student: Student) -> bool:
        """Save student entity"""
        try:
            self._students[student.id] = self._entity_to_dict(student)
            self._persist()
            return True
        except Exception as e:
            print(f"Failed to save student: {e}")
            return False
    
    def delete(self, student_id: str) -> bool:
        """Delete student"""
        try:
            if student_id in self._students:
                del self._students[student_id]
                self._persist()
                return True
            return False
        except Exception as e:
            print(f"Failed to delete student: {e}")
            return False
    
    def find_by_class(self, department: str, program: str, year: int, section: str) -> List[Student]:
        """Find students in a specific class"""
        results = []
        for student in self.get_all():
            if (student.department == department and
                student.program == program and
                student.year == year and
                student.section == section):
                results.append(student)
        return results
    
    def _load(self) -> dict:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _persist(self):
        """Save data to JSON file"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self._students, f, indent=4)
    
    def _dict_to_entity(self, data: dict) -> Student:
        """Convert dictionary to Student entity"""
        return Student(
            id=data["id"],
            name=data["name"],
            role=data.get("role", "Student"),
            department=data["dept"],
            program=data["program"],
            year=data["year"],
            section=data["section"],
            privacy_hash=data.get("privacy_hash")
        )
    
    def _entity_to_dict(self, student: Student) -> dict:
        """Convert Student entity to dictionary"""
        return {
            "id": student.id,
            "name": student.name,
            "role": student.role,
            "dept": student.department,
            "program": student.program,
            "year": student.year,
            "section": student.section,
            "privacy_hash": student.privacy_hash
        }
