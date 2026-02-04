"""
Event Bus - Infrastructure for Event-Driven Architecture

Enables decoupling between components:
- Sensors publish events (NO decision making)
- Use cases subscribe to events (decision logic)
- Side effects triggered by events (alerts, logging)

Aligns with Papers 9 & 10 (Orchestration, System Effects)
"""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import threading


class EventType(Enum):
    """Event types for the system"""
    # Sensing events
    FACE_DETECTED = "face_detected"
    AUDIO_ALERT = "audio_alert"
    POSE_DETECTED = "pose_detected"
    
    # Decision events
    VIOLATION_DETECTED = "violation_detected"
    COMPLIANCE_VERIFIED = "compliance_verified"
    
    # Action events
    ALERT_TRIGGERED = "alert_triggered"
    ATTENDANCE_MARKED = "attendance_marked"
    
    # System events
    SAFETY_CONCERN = "safety_concern"


@dataclass
class Event:
    """Base event class"""
    type: EventType
    payload: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class EventBus:
    """
    Lightweight event bus for decoupling components.
    
    Thread-safe implementation for multi-threaded orchestration.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._lock = threading.Lock()
        print("✅ Event bus initialized")
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: Type of event to listen for
            handler: Function to call when event occurs
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            print(f"📡 Subscribed handler to {event_type.value}")
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        with self._lock:
            handlers = self._handlers.get(event.type, [])
        
        # Execute handlers (outside lock to prevent deadlock)
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"⚠️  Event handler error for {event.type.value}: {e}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Remove a handler subscription"""
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type].remove(handler)
    
    def clear_all(self):
        """Clear all subscriptions (for cleanup)"""
        with self._lock:
            self._handlers.clear()
