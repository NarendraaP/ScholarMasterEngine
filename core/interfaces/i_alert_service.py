"""
Alert Service Interface (Port)

Abstracts alert notification infrastructure.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any


class AlertSeverity(Enum):
    """Alert severity levels"""
    SECURITY = "Security"
    WARNING = "Warning"
    CRITICAL = "Critical"
    GROOMING = "Grooming"


@dataclass
class Alert:
    """Alert entity"""
    timestamp: datetime
    severity: AlertSeverity
    message: str
    zone: str
    metadata: Dict[str, Any]
    
    def requires_immediate_action(self) -> bool:
        """Check if alert needs immediate response"""
        return self.severity in [AlertSeverity.SECURITY, AlertSeverity.CRITICAL]


class IAlertService(ABC):
    """
    Port for alert notification infrastructure.
    
    Implementations: JSON file, Email/SMS, Push notifications
    """
    
    @abstractmethod
    def trigger(self, alert: Alert) -> None:
        """
        Trigger alert (irreversible action).
        
        Args:
            alert: Alert to trigger
        """
        pass
    
    @abstractmethod
    def get_recent_alerts(self, zone: Optional[str] = None, minutes: int = 60) -> List[Alert]:
        """
        Get recent alerts for debouncing.
        
        Args:
            zone: Filter by zone (None for all)
            minutes: Time window in minutes
            
        Returns:
            List of recent alerts
        """
        pass
