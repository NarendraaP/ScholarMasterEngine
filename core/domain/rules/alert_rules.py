"""
Domain Rules - Alert Rules

Business logic for alert triggering and escalation.
"""
from enum import Enum
from typing import Dict


class AlertSeverity(Enum):
    """Alert severity levels"""
    SECURITY = "Security"  # Spoof attempts, unauthorized access
    WARNING = "Warning"    # Truancy, noise violations
    CRITICAL = "Critical"  # Violence, screams, sustained loud noise
    GROOMING = "Grooming"  # Uniform violations


class AlertRules:
    """
    Alert triggering rules.
    
    Determines when and with what severity to trigger alerts.
    """
    
    # Context-aware noise thresholds (dB normalized to 0-1)
    LECTURE_MODE_THRESHOLD = 40 / 100  # 40 dB in lecture mode (strict)
    BREAK_MODE_THRESHOLD = 80 / 100     # 80 dB in break mode (relaxed)
    
    SCREAM_THRESHOLD = 0.85  # 85 dB = scream/violence
    
    @staticmethod
    def should_trigger_noise_alert(
        db_level: float,
        is_lecture_mode: bool
    ) -> bool:
        """
        Determine if noise level warrants alert.
        
        Context-aware thresholds from Paper 6.
        
        Args:
            db_level: Normalized dB level (0-1)
            is_lecture_mode: True if class in session
            
        Returns:
            True if alert should be triggered
        """
        threshold = (AlertRules.LECTURE_MODE_THRESHOLD if is_lecture_mode 
                    else AlertRules.BREAK_MODE_THRESHOLD)
        
        return db_level > threshold
    
    @staticmethod
    def get_noise_alert_severity(db_level: float) -> AlertSeverity:
        """
        Determine alert severity based on noise level.
        
        Args:
            db_level: Normalized dB level (0-1)
            
        Returns:
            AlertSeverity
        """
        if db_level > AlertRules.SCREAM_THRESHOLD:
            return AlertSeverity.CRITICAL  # Possible violence/emergency
        else:
            return AlertSeverity.WARNING  # Loud noise
    
    @staticmethod
    def get_role_routing(severity: AlertSeverity) -> str:
        """
        Determine which role should receive alert.
        
        Role hierarchy from RBAC (7 roles).
        
        Args:
            severity: Alert severity
            
        Returns:
            Target role for notification routing
        """
        routing = {
            AlertSeverity.SECURITY: "Security",
            AlertSeverity.WARNING: "Faculty",
            AlertSeverity.CRITICAL: "Dean",
            AlertSeverity.GROOMING: "Disciplinary Committee"
        }
        return routing.get(severity, "Admin")
    
    @staticmethod
    def should_debounce(recent_alert_count: int, window_minutes: int = 5) -> bool:
        """
        Check if alert should be suppressed due to recent duplicates.
        
        Prevents alert spam.
        
        Args:
            recent_alert_count: Number of alerts in window
            window_minutes: Time window for debouncing
            
        Returns:
            True if alert should be suppressed
        """
        # Allow max 1 alert per 5 minutes for same condition
        return recent_alert_count > 0
