"""
Privacy LED Enforcement

ARCHITECTURE_CANONICAL.md 6.1 COMPLIANCE:
- Privacy LED must indicate system state at boot
- LED failure must halt system
- LED state must be accurate

This module provides runtime enforcement of Privacy LED requirements.
"""
import time
import logging
from typing import Optional, Callable
from enum import Enum, auto
from dataclasses import dataclass


logger = logging.getLogger(__name__)


# =============================================================================
# LED STATE DEFINITIONS
# =============================================================================

class LEDState(Enum):
    """Privacy LED states per ARCHITECTURE_CANONICAL.md 6.1."""
    OFF = auto()       # System inactive
    PRIVACY = auto()   # Pose-only mode (anonymous) - GREEN
    ACTIVE = auto()    # Face recognition enabled - RED


class LEDFailure(Exception):
    """Raised when Privacy LED cannot be set."""
    pass


class SystemHaltRequired(Exception):
    """Raised when system must halt due to LED failure."""
    pass


# =============================================================================
# PRIVACY LED CONTROLLER
# =============================================================================

@dataclass
class LEDStateRecord:
    """Record of LED state change for audit."""
    timestamp: float
    previous_state: Optional[LEDState]
    new_state: LEDState
    reason: str


class PrivacyLEDController:
    """
    Privacy LED Controller with boot enforcement.
    
    Per ARCHITECTURE_CANONICAL.md 6.1:
    - Privacy LED must be set at system boot
    - Failure to set LED must halt system
    - LED state must be accurate
    """
    
    # Hardware simulation (in production, this interfaces with GPIO)
    _hardware_available: bool = True
    
    def __init__(self, hardware_interface: Optional[Callable] = None):
        """
        Initialize LED controller.
        
        Args:
            hardware_interface: Optional callable for hardware LED control.
                               If None, uses software simulation.
        """
        self._current_state: Optional[LEDState] = None
        self._boot_completed: bool = False
        self._hardware_interface = hardware_interface
        self._state_history: list[LEDStateRecord] = []
        self._halted: bool = False
    
    def boot(self, initial_state: LEDState = LEDState.PRIVACY) -> bool:
        """
        Boot LED controller with mandatory state setting.
        
        Per ARCHITECTURE_CANONICAL.md 6.1:
        - LED MUST be set at boot
        - Failure halts system
        
        Args:
            initial_state: Initial LED state (default: PRIVACY mode)
            
        Returns:
            True if boot successful
            
        Raises:
            SystemHaltRequired: If LED cannot be set
        """
        try:
            self._set_hardware_led(initial_state)
            self._current_state = initial_state
            self._boot_completed = True
            
            self._log_state_change(None, initial_state, "System boot")
            
            logger.info(f"Privacy LED boot: {initial_state.name}")
            return True
            
        except LEDFailure as e:
            # ARCHITECTURE_CANONICAL.md 6.1: Failure to set LED must halt system
            self._halted = True
            logger.critical(f"LED failure at boot - SYSTEM HALT REQUIRED: {e}")
            raise SystemHaltRequired(
                "ARCHITECTURE_CANONICAL.md 6.1: LED failure requires system halt"
            ) from e
    
    def set_state(self, new_state: LEDState, reason: str = "") -> bool:
        """
        Set LED state with validation.
        
        Args:
            new_state: New LED state
            reason: Reason for state change (for audit)
            
        Returns:
            True if state changed successfully
            
        Raises:
            SystemHaltRequired: If LED cannot be set
        """
        if self._halted:
            raise SystemHaltRequired("System is halted due to LED failure")
        
        if not self._boot_completed:
            raise LEDFailure("LED controller not booted - call boot() first")
        
        previous_state = self._current_state
        
        try:
            self._set_hardware_led(new_state)
            self._current_state = new_state
            self._log_state_change(previous_state, new_state, reason)
            
            logger.info(f"Privacy LED: {previous_state.name} → {new_state.name}")
            return True
            
        except LEDFailure as e:
            # ARCHITECTURE_CANONICAL.md 6.1: LED failure halts system
            self._halted = True
            logger.critical(f"LED failure - SYSTEM HALT REQUIRED: {e}")
            raise SystemHaltRequired(
                "ARCHITECTURE_CANONICAL.md 6.1: LED failure requires system halt"
            ) from e
    
    def _set_hardware_led(self, state: LEDState) -> None:
        """
        Set physical LED hardware.
        
        Raises:
            LEDFailure: If hardware cannot be controlled
        """
        if self._hardware_interface is not None:
            try:
                self._hardware_interface(state)
            except Exception as e:
                raise LEDFailure(f"Hardware LED control failed: {e}")
        elif not self._hardware_available:
            raise LEDFailure("LED hardware not available")
        # else: software simulation (always succeeds)
    
    def _log_state_change(
        self, 
        previous: Optional[LEDState], 
        new: LEDState, 
        reason: str
    ) -> None:
        """Log state change for audit trail."""
        record = LEDStateRecord(
            timestamp=time.time(),
            previous_state=previous,
            new_state=new,
            reason=reason
        )
        self._state_history.append(record)
    
    @property
    def current_state(self) -> Optional[LEDState]:
        """Get current LED state."""
        return self._current_state
    
    @property
    def is_booted(self) -> bool:
        """Check if LED controller has booted."""
        return self._boot_completed
    
    @property
    def is_halted(self) -> bool:
        """Check if system is halted due to LED failure."""
        return self._halted
    
    def get_state_history(self) -> list[LEDStateRecord]:
        """Get LED state change history for audit."""
        return self._state_history.copy()
    
    def require_operator_ack_for_active(self) -> bool:
        """
        Transition to ACTIVE mode requires operator acknowledgment.
        
        Per ARCHITECTURE_CANONICAL.md 7.4:
        - On restart: Require operator acknowledgment before ACTIVE mode
        
        Returns:
            True if operator acknowledgment is required
        """
        return self._current_state == LEDState.PRIVACY
    
    @classmethod
    def simulate_hardware_failure(cls) -> None:
        """Simulate hardware failure for testing."""
        cls._hardware_available = False
    
    @classmethod
    def restore_hardware(cls) -> None:
        """Restore hardware availability for testing."""
        cls._hardware_available = True
