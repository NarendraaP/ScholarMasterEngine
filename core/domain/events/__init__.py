"""
Domain Events Package
"""
from .domain_events import (
    DomainEvent,
    FaceDetectedEvent,
    ViolationDetectedEvent,
    AttendanceMarkedEvent,
    NoiseAlertEvent,
    SafetyAlertEvent
)

__all__ = [
    'DomainEvent',
    'FaceDetectedEvent',
    'ViolationDetectedEvent',
    'AttendanceMarkedEvent',
    'NoiseAlertEvent',
    'SafetyAlertEvent'
]
