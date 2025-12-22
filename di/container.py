"""
Dependency Injection Container

Wires all dependencies together following Clean Architecture.
This is the composition root of the application.
"""
from infrastructure.face_recognition import InsightFaceAdapter
from infrastructure.indexing import FaissFaceIndex
from infrastructure.repositories import (
    JsonStudentRepository,
    CsvAttendanceRepository,
    CsvScheduleRepository
)
from application.use_cases import (
    RegisterStudentUseCase,
    MarkAttendanceUseCase,
    DetectTruancyUseCase,
    RecognizeStudentUseCase
)


class DIContainer:
    """
    Dependency Injection Container.
    
    This is where all the magic happens:
    1. Instantiates infrastructure implementations
    2. Injects them into use cases
    3. Provides a clean API for the presentation layer
    
    Following Dependency Inversion Principle:
    - High-level modules (use cases) don't depend on low-level modules (infrastructure)
    - Both depend on abstractions (domain interfaces)
    - This container does the wiring
    """
    
    def __init__(self):
        """Initialize all dependencies"""
        # Infrastructure Layer (Outer)
        self._init_infrastructure()
        
        # Application Layer (Middle)
        self._init_application()
    
    def _init_infrastructure(self):
        """Initialize infrastructure implementations"""
        # Face recognition
        self.face_recognizer = InsightFaceAdapter(det_size=(640, 640))
        
        # Face index
        self.face_index = FaissFaceIndex(
            index_file="data/faiss_index.bin",
            identity_map_file="data/identity_map.json"
        )
        
        # Repositories
        self.student_repo = JsonStudentRepository("data/students.json")
        self.attendance_repo = CsvAttendanceRepository("data/attendance.csv")
        self.schedule_repo = CsvScheduleRepository("data/timetable.csv")
    
    def _init_application(self):
        """Initialize application use cases with injected dependencies"""
        # Register student use case
        self.register_student = RegisterStudentUseCase(
            face_recognizer=self.face_recognizer,
            face_index=self.face_index,
            student_repo=self.student_repo
        )
        
        # Mark attendance use case
        self.mark_attendance = MarkAttendanceUseCase(
            attendance_repo=self.attendance_repo,
            student_repo=self.student_repo
        )
        
        # Detect truancy use case
        self.detect_truancy = DetectTruancyUseCase(
            student_repo=self.student_repo,
            schedule_repo=self.schedule_repo
        )
        
        # Recognize student use case
        self.recognize_student = RecognizeStudentUseCase(
            face_recognizer=self.face_recognizer,
            face_index=self.face_index,
            student_repo=self.student_repo
        )
    
    # Convenience methods for direct access
    def get_face_recognition_service(self):
        """Get face recognition infrastructure"""
        return self.face_recognizer
    
    def get_student_repository(self):
        """Get student repository"""
        return self.student_repo
    
    def get_attendance_repository(self):
        """Get attendance repository"""
        return self.attendance_repo
    
    def get_schedule_repository(self):
        """Get schedule repository"""
        return self.schedule_repo


# Global singleton instance
# In production, you might use a proper DI framework like dependency-injector
_container: DIContainer = None


def get_container() -> DIContainer:
    """
    Get or create the global DI container.
    
    Returns:
        DIContainer instance
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container():
    """Reset the container (useful for testing)"""
    global _container
    _container = None
