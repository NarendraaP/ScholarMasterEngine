"""
Domain Rules - Compliance Checking

Pure business logic extracted from ContextEngine.
ZERO infrastructure dependencies.
"""
from typing import Optional, Tuple
from datetime import time


class ComplianceRules:
    """
    ST-CSF Compliance Rules (Paper 4)
    
    Determines if student is in correct location based on schedule.
    """
    
    @staticmethod
    def is_in_expected_location(
        current_zone: str,
        expected_zone: Optional[str]
    ) -> bool:
        """
        Check if student is where they should be.
        
        Args:
            current_zone: Where student currently is
            expected_zone: Where student should be (None = free period)
            
        Returns:
            True if compliant (in correct location or free period)
        """
        if expected_zone is None:
            # No class scheduled - student is free
            return True
        
        # Direct string comparison (case-insensitive)
        return current_zone.strip().lower() == expected_zone.strip().lower()
    
    @staticmethod
    def get_compliance_message(
        is_compliant: bool,
        expected_zone: Optional[str],
        subject: Optional[str] = None
    ) -> str:
        """
        Generate human-readable compliance message.
        
        Args:
            is_compliant: Compliance status
            expected_zone: Expected location
            subject: Subject name (if scheduled)
            
        Returns:
            Human-readable message
        """
        if expected_zone is None:
            return "Free Period"
        
        if is_compliant:
            return "Compliant"
        else:
            subject_str = f" for {subject}" if subject else ""
            return f"TRUANCY: Expected in {expected_zone}{subject_str}"
    
    @staticmethod
    def requires_debounce(violation_count: int, threshold: int = 30) -> bool:
        """
        Check if violation should be reported based on persistence.
        
        Prevents false positives from transient detections.
        
        Args:
            violation_count: Number of consecutive violations
            threshold: Required persistence (frames/seconds)
            
        Returns:
            True if violation is persistent enough to report
        """
        return violation_count >= threshold
