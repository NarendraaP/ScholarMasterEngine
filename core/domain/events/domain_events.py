"""
Domain Events

Events that domain logic can publish.
These represent things that HAVE HAPPENED.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class DomainEvent:
    """Base class for domain events"""
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class FaceDetectedEvent(DomainEvent):
    """Face was detected and recognized"""
    student_id: str
    zone: str
    confidence: float
    timestamp: datetime = None


@dataclass
class ViolationDetectedEvent(DomainEvent):
    """Compliance violation detected"""
    student_id: str
    violation_type: str  # "truancy", "noise", "violence", "grooming"
    zone: str
    severity: str  # "Security", "Warning", "Critical"
    metadata: Dict[str, Any]
    timestamp: datetime = None


@dataclass
class AttendanceMarkedEvent(DomainEvent):
    """Attendance was successfully marked"""
    student_id: str
    subject: str
    zone: str
    teacher: Optional[str] = None
    timestamp: datetime = None


@dataclass
class NoiseAlertEvent(DomainEvent):
    """Loud noise detected"""
    zone: str
    db_level: float
    is_lecture_mode: bool
    severity: str  # "Warning", "Critical"
    timestamp: datetime = None


@dataclass
class SafetyAlertEvent(DomainEvent):
    """Safety concern detected (violence, sleep, etc.)"""
    zone: str
    alert_type: str  # "violence", "prolonged_sleep", etc.
    severity: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
