"""
Alert Service - Infrastructure Adapter

Implements IAlertService using JSON file storage.
"""
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os

from core.interfaces.i_alert_service import IAlertService, Alert, AlertSeverity


class JSONAlertService(IAlertService):
    """
    JSON-based alert service.
    
    Persists alerts to data/alerts.json with atomic writes.
    """
    
    def __init__(self, alerts_path="data/alerts.json"):
        """Initialize alert service"""
        self.alerts_path = alerts_path
        print(f"✅ Alert service initialized (path: {alerts_path})")
    
    def trigger(self, alert: Alert) -> None:
        """
        Trigger alert (irreversible action).
        
        Uses atomic write (RCU pattern) to prevent corruption.
        """
        # Convert alert to dict
        alert_dict = {
            "timestamp": alert.timestamp.isoformat(),
            "type": alert.severity.value,
            "msg": alert.message,
            "zone": alert.zone,
            "metadata": alert.metadata
        }
        
        try:
            # Read existing alerts
            if os.path.exists(self.alerts_path):
                with open(self.alerts_path, "r") as f:
                    try:
                        alerts = json.load(f)
                    except json.JSONDecodeError:
                        alerts = []
            else:
                alerts = []
            
            # Append new alert
            alerts.append(alert_dict)
            
            # Keep only last 100 alerts to prevent bloat
            if len(alerts) > 100:
                alerts = alerts[-100:]
            
            # Atomic write (RCU pattern from Paper 4)
            temp_file = self.alerts_path + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(alerts, f, indent=4)
            os.replace(temp_file, self.alerts_path)  # Atomic
            
            print(f"🚨 Alert triggered: [{alert.severity.value}] {alert.message}")
            
        except Exception as e:
            print(f"❌ Failed to log alert: {e}")
    
    def get_recent_alerts(self, zone: Optional[str] = None, minutes: int = 60) -> List[Alert]:
        """
        Get recent alerts for debouncing.
        
        Args:
            zone: Filter by zone (None for all)
            minutes: Time window in minutes
            
        Returns:
            List of recent alerts
        """
        if not os.path.exists(self.alerts_path):
            return []
        
        try:
            with open(self.alerts_path, "r") as f:
                alerts_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_alerts = []
        for alert_dict in alerts_data:
            try:
                alert_time = datetime.fromisoformat(alert_dict["timestamp"])
                
                if alert_time < cutoff_time:
                    continue  # Too old
                
                # Filter by zone if specified
                if zone is not None and alert_dict.get("zone") != zone:
                    continue
                
                # Convert to Alert entity
                alert = Alert(
                    timestamp=alert_time,
                    severity=AlertSeverity(alert_dict["type"]),
                    message=alert_dict["msg"],
                    zone=alert_dict["zone"],
                    metadata=alert_dict.get("metadata", {})
                )
                recent_alerts.append(alert)
                
            except (KeyError, ValueError):
                continue
        
        return recent_alerts
