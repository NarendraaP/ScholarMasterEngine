"""
Event Handlers - Application Layer

Handles domain events and triggers appropriate actions.
These are the "subscribers" in the event-driven architecture.
"""
from typing import Dict, Any
from datetime import datetime

from core.infrastructure.events.event_bus import Event, EventType
from core.interfaces.i_alert_service import IAlertService, Alert, AlertSeverity
from core.domain.rules.alert_rules import AlertRules


class EventHandlers:
    """
    Application-level event handlers.
    
    These handle events published by sensors and trigger side effects.
    """
    
    def __init__(self, alert_service: IAlertService, event_bus):
        self.alert_service = alert_service
        self.event_bus = event_bus
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.VIOLATION_DETECTED, self.on_violation_detected)
        self.event_bus.subscribe(EventType.AUDIO_ALERT, self.on_audio_alert)
        self.event_bus.subscribe(EventType.SAFETY_CONCERN, self.on_safety_concern)
        
        print("✅ Event handlers registered")
    
    def on_violation_detected(self, event: Event):
        """
        Handle compliance violation.
        
        Triggered when student is in wrong location.
        """
        payload = event.payload
        
        # Check debounce
        recent_alerts = self.alert_service.get_recent_alerts(
            zone=payload.get('zone'),
            minutes=5
        )
        
        if AlertRules.should_debounce(len(recent_alerts), window_minutes=5):
            return  # Suppress duplicate
        
        # Trigger alert
        alert = Alert(
            timestamp=datetime.now(),
            severity=AlertSeverity.WARNING,
            message=payload.get('message', 'Violation detected'),
            zone=payload.get('zone', 'Unknown'),
            metadata=payload
        )
        
        self.alert_service.trigger(alert)
        
        # Publish alert triggered event (for audit)
        self.event_bus.publish(Event(
            type=EventType.ALERT_TRIGGERED,
            payload={'alert': alert.__dict__}
        ))
    
    def on_audio_alert(self, event: Event):
        """
        Handle audio alert.
        
        Triggered when loud noise detected.
        """
        payload = event.payload
        db_level = payload.get('db_level', 0.0)
        zone = payload.get('zone', 'Unknown')
        
        # Determine severity using domain rules
        severity = AlertRules.get_noise_alert_severity(db_level)
        
        # Check debounce
        recent_alerts = self.alert_service.get_recent_alerts(zone=zone, minutes=1)
        if AlertRules.should_debounce(len(recent_alerts), window_minutes=1):
            return
        
        # Trigger alert
        alert = Alert(
            timestamp=datetime.now(),
            severity=severity,
            message=f"Loud noise detected ({db_level:.2f} dB)",
            zone=zone,
            metadata=payload
        )
        
        self.alert_service.trigger(alert)
    
    def on_safety_concern(self, event: Event):
        """
        Handle safety concern.
        
        Triggered by safety detection (violence, sleep, etc.)
        """
        payload = event.payload
        
        alert = Alert(
            timestamp=datetime.now(),
            severity=AlertSeverity.CRITICAL,
            message=payload.get('message', 'Safety concern detected'),
            zone=payload.get('zone', 'Unknown'),
            metadata=payload
        )
        
        self.alert_service.trigger(alert)
