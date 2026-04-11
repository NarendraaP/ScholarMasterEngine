#!/usr/bin/env python3
"""
Failure Semantics Implementation
================================
Implements fail-safe behavior as defined in ARCHITECTURE_CANONICAL.md Section 7.

Privacy must be preserved during failure. Fail-safe defaults apply.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque

logger = logging.getLogger(__name__)


# =============================================================================
# FAILURE STATES
# =============================================================================

class SystemState(Enum):
    """System operational states."""
    NORMAL = auto()
    DEGRADED = auto()
    MQTT_FAILURE = auto()
    GOVERNANCE_FAILURE = auto()
    STORAGE_FAILURE = auto()
    RECOVERING = auto()
    HALTED = auto()


class PrivacyMode(Enum):
    """Privacy LED states (from ARCHITECTURE_CANONICAL.md 6.1)."""
    OFF = auto()      # System inactive
    PRIVACY = auto()  # Pose-only mode (anonymous) - GREEN
    ACTIVE = auto()   # Face recognition enabled - RED


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker for downstream systems.
    
    Prevents cascading failures and enables graceful degradation.
    """
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        reset_timeout: float = 60.0
    ):
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._is_open = False
        self._name = "default"
    
    def set_name(self, name: str) -> None:
        """Set circuit breaker name for logging."""
        self._name = name
    
    def record_success(self) -> None:
        """Record successful operation."""
        self._failure_count = 0
        if self._is_open:
            self._is_open = False
            logger.info(f"CircuitBreaker[{self._name}]: Closed after success")
    
    def record_failure(self) -> None:
        """Record failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self._failure_threshold:
            self._is_open = True
            logger.warning(
                f"CircuitBreaker[{self._name}]: Opened after "
                f"{self._failure_count} failures"
            )
    
    def is_available(self) -> bool:
        """Check if circuit is available for operations."""
        if not self._is_open:
            return True
        
        # Check if reset timeout has elapsed
        elapsed = time.time() - self._last_failure_time
        if elapsed >= self._reset_timeout:
            logger.info(f"CircuitBreaker[{self._name}]: Reset timeout elapsed, allowing retry")
            return True  # Allow retry
        
        return False


# =============================================================================
# EPHEMERAL EVENT BUFFER (MQTT FALLBACK)
# =============================================================================

class EphemeralEventBuffer:
    """
    RAM-only event buffer for MQTT failure fallback.
    
    No persistent queue writes allowed.
    Buffer overflow drops oldest events.
    """
    
    def __init__(self, max_size: int = 1000):
        self._buffer: deque = deque(maxlen=max_size)
        self._overflow_count = 0
        logger.info(f"EphemeralEventBuffer initialized (max_size={max_size})")
    
    def add(self, event: Dict[str, Any]) -> None:
        """
        Add event to buffer.
        
        Oldest events dropped on overflow.
        """
        if len(self._buffer) >= self._buffer.maxlen:
            self._overflow_count += 1
            logger.debug("EphemeralEventBuffer: Overflow, dropping oldest")
        
        self._buffer.append({
            "event": event,
            "timestamp": time.time()
        })
    
    def drain(self) -> List[Dict[str, Any]]:
        """
        Drain all events from buffer.
        
        Returns:
            List of buffered events.
        """
        events = list(self._buffer)
        self._buffer.clear()
        logger.info(f"EphemeralEventBuffer: Drained {len(events)} events")
        return [e["event"] for e in events]
    
    def size(self) -> int:
        """Get current buffer size."""
        return len(self._buffer)
    
    def get_overflow_count(self) -> int:
        """Get total overflow count."""
        return self._overflow_count


# =============================================================================
# FAILURE HANDLER
# =============================================================================

class FailureHandler:
    """
    Central failure handling with privacy preservation.
    
    Implements failure semantics from ARCHITECTURE_CANONICAL.md Section 7.
    """
    
    def __init__(self):
        self._state = SystemState.NORMAL
        self._privacy_mode = PrivacyMode.OFF
        self._mqtt_circuit = CircuitBreaker()
        self._mqtt_circuit.set_name("MQTT")
        self._governance_circuit = CircuitBreaker()
        self._governance_circuit.set_name("Governance")
        self._storage_circuit = CircuitBreaker()
        self._storage_circuit.set_name("Storage")
        self._event_buffer = EphemeralEventBuffer()
        self._state_history: List[Dict] = []
        self._led_set_at_boot = False
        logger.info("FailureHandler initialized")
    
    # --- 7.1 MQTT Failure ---
    
    def handle_mqtt_failure(self, event: Dict[str, Any]) -> None:
        """
        Handle MQTT failure: buffer events locally (RAM-only).
        
        No persistent queue writes allowed.
        """
        self._mqtt_circuit.record_failure()
        self._event_buffer.add(event)
        
        if self._state != SystemState.MQTT_FAILURE:
            self._transition_state(SystemState.MQTT_FAILURE)
            logger.warning("FailureHandler: MQTT failure detected, buffering events")
    
    def mqtt_available(self) -> bool:
        """Check if MQTT is available."""
        return self._mqtt_circuit.is_available()
    
    def drain_mqtt_buffer(self) -> List[Dict[str, Any]]:
        """Drain MQTT event buffer after recovery."""
        self._mqtt_circuit.record_success()
        if self._state == SystemState.MQTT_FAILURE:
            self._transition_state(SystemState.NORMAL)
        return self._event_buffer.drain()
    
    # --- 7.2 Governance Failure ---
    
    def handle_governance_failure(self) -> None:
        """
        Handle governance failure: block all L4→L6 traffic.
        
        No inference output may bypass governance during failure.
        """
        self._governance_circuit.record_failure()
        
        if self._state != SystemState.GOVERNANCE_FAILURE:
            self._transition_state(SystemState.GOVERNANCE_FAILURE)
            logger.error(
                "FailureHandler: GOVERNANCE FAILURE - "
                "All L4→L6 traffic blocked"
            )
    
    def governance_available(self) -> bool:
        """Check if governance is available."""
        return self._governance_circuit.is_available()
    
    def can_pass_to_human_interface(self) -> bool:
        """
        Check if data can pass to L6 (human interface).
        
        Returns False if governance has failed.
        """
        if self._state == SystemState.GOVERNANCE_FAILURE:
            logger.warning("FailureHandler: L6 access blocked due to governance failure")
            return False
        return True
    
    # --- 7.3 Storage Failure ---
    
    def handle_storage_failure(self) -> None:
        """
        Handle storage failure: continue with ephemeral operation.
        
        Session data loss is acceptable; privacy violation is not.
        """
        self._storage_circuit.record_failure()
        
        if self._state != SystemState.STORAGE_FAILURE:
            self._transition_state(SystemState.DEGRADED)
            logger.warning(
                "FailureHandler: Storage failure - "
                "Continuing in ephemeral mode"
            )
    
    def storage_available(self) -> bool:
        """Check if storage is available."""
        return self._storage_circuit.is_available()
    
    # --- 7.4 Crash Recovery ---
    
    def recover_from_crash(self) -> bool:
        """
        Recover from crash.
        
        - Assume all volatile data destroyed
        - Initialize to PRIVACY mode
        - Require operator acknowledgment before ACTIVE mode
        
        Returns:
            True if recovery successful.
        """
        self._transition_state(SystemState.RECOVERING)
        
        # Assume all volatile data destroyed
        self._event_buffer = EphemeralEventBuffer()
        
        # Initialize to PRIVACY mode (fail-safe)
        self._privacy_mode = PrivacyMode.PRIVACY
        
        logger.info(
            "FailureHandler: Crash recovery - "
            "Initialized to PRIVACY mode, operator ack required for ACTIVE"
        )
        
        self._transition_state(SystemState.NORMAL)
        return True
    
    def request_active_mode(self, operator_ack: bool) -> bool:
        """
        Request transition to ACTIVE mode.
        
        Requires operator acknowledgment.
        
        Returns:
            True if transition allowed.
        """
        if not operator_ack:
            logger.warning(
                "FailureHandler: ACTIVE mode request denied - "
                "Operator acknowledgment required"
            )
            return False
        
        self._privacy_mode = PrivacyMode.ACTIVE
        logger.info("FailureHandler: Transitioned to ACTIVE mode with operator ack")
        return True
    
    # --- 7.5 Partial Subsystem Availability ---
    
    def is_degraded(self) -> bool:
        """Check if system is in degraded mode."""
        return self._state in {
            SystemState.DEGRADED,
            SystemState.MQTT_FAILURE,
            SystemState.STORAGE_FAILURE
        }
    
    def get_available_subsystems(self) -> Dict[str, bool]:
        """Get availability of all subsystems."""
        return {
            "mqtt": self._mqtt_circuit.is_available(),
            "governance": self._governance_circuit.is_available(),
            "storage": self._storage_circuit.is_available(),
            "l4_to_l6": self.can_pass_to_human_interface()
        }
    
    # --- Privacy LED (6.1) ---
    
    def set_boot_privacy_led(self, state: PrivacyMode) -> bool:
        """
        Set privacy LED state at boot.
        
        MANDATORY: Must be called at system boot.
        Failure to set LED must halt system.
        
        Returns:
            True if LED set successfully.
        """
        # Simulate LED hardware
        try:
            self._privacy_mode = state
            self._led_set_at_boot = True
            logger.info(f"FailureHandler: Privacy LED set to {state.name} at boot")
            return True
        except Exception as e:
            logger.error(f"FailureHandler: CRITICAL - Cannot set Privacy LED: {e}")
            self._transition_state(SystemState.HALTED)
            return False
    
    def verify_boot_led(self) -> bool:
        """
        Verify Privacy LED was set at boot.
        
        System must halt if LED was not set.
        
        Returns:
            True if LED was properly set at boot.
        """
        if not self._led_set_at_boot:
            logger.error(
                "FailureHandler: CRITICAL - Privacy LED not set at boot. "
                "System must halt."
            )
            self._transition_state(SystemState.HALTED)
            return False
        return True
    
    def get_privacy_mode(self) -> PrivacyMode:
        """Get current privacy mode."""
        return self._privacy_mode
    
    # --- State Management ---
    
    def _transition_state(self, new_state: SystemState) -> None:
        """Record state transition."""
        old_state = self._state
        self._state = new_state
        self._state_history.append({
            "from": old_state.name,
            "to": new_state.name,
            "timestamp": time.time()
        })
        logger.info(f"FailureHandler: {old_state.name} → {new_state.name}")
    
    def get_state(self) -> SystemState:
        """Get current system state."""
        return self._state
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete failure handler status."""
        return {
            "state": self._state.name,
            "privacy_mode": self._privacy_mode.name,
            "led_set_at_boot": self._led_set_at_boot,
            "subsystems": self.get_available_subsystems(),
            "mqtt_buffer_size": self._event_buffer.size(),
            "mqtt_overflow_count": self._event_buffer.get_overflow_count()
        }


# =============================================================================
# HEALTH CHECK PROTOCOL
# =============================================================================

class HealthCheckProtocol:
    """
    Health check protocol for edge nodes.
    
    Monitors subsystem health and triggers failure handling.
    """
    
    def __init__(self, failure_handler: FailureHandler):
        self._failure_handler = failure_handler
        self._check_interval = 5.0  # seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._health_checks: Dict[str, Callable[[], bool]] = {}
        logger.info("HealthCheckProtocol initialized")
    
    def register_check(self, name: str, check_fn: Callable[[], bool]) -> None:
        """Register a health check function."""
        self._health_checks[name] = check_fn
        logger.debug(f"HealthCheckProtocol: Registered check '{name}'")
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all registered health checks."""
        results = {}
        for name, check_fn in self._health_checks.items():
            try:
                results[name] = check_fn()
            except Exception as e:
                logger.error(f"HealthCheckProtocol: Check '{name}' failed: {e}")
                results[name] = False
        return results
    
    def start(self) -> None:
        """Start periodic health check thread."""
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        logger.info("HealthCheckProtocol: Started periodic checks")
    
    def stop(self) -> None:
        """Stop health check thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("HealthCheckProtocol: Stopped")
    
    def _check_loop(self) -> None:
        """Periodic health check loop."""
        while self._running:
            results = self.run_all_checks()
            
            for name, healthy in results.items():
                if not healthy:
                    logger.warning(f"HealthCheckProtocol: Unhealthy - {name}")
            
            time.sleep(self._check_interval)


# =============================================================================
# OPERATOR ACKNOWLEDGMENT
# =============================================================================

@dataclass
class AcknowledgmentRecord:
    """Record of operator acknowledgment."""
    alert_id: str
    acknowledged: bool
    operator_id: Optional[str]
    timestamp: float = field(default_factory=time.time)


class OperatorAcknowledgmentLoop:
    """
    Operator acknowledgment loop for critical alerts.
    
    - Critical alerts require operator acknowledgment
    - Acknowledgment is logged
    - Unacknowledged alerts escalate
    """
    
    def __init__(self, escalation_timeout: float = 300.0):
        self._escalation_timeout = escalation_timeout
        self._pending_alerts: Dict[str, float] = {}  # alert_id -> sent_time
        self._acknowledgments: Dict[str, AcknowledgmentRecord] = {}
        self._escalation_callback: Optional[Callable] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        logger.info(f"OperatorAcknowledgmentLoop initialized (timeout={escalation_timeout}s)")
    
    def set_escalation_callback(self, callback: Callable) -> None:
        """Set callback for escalations."""
        self._escalation_callback = callback
    
    def require_acknowledgment(self, alert_id: str) -> None:
        """Mark alert as requiring acknowledgment."""
        self._pending_alerts[alert_id] = time.time()
        logger.info(f"OperatorAcknowledgmentLoop: Alert {alert_id} requires ack")
    
    def acknowledge(self, alert_id: str, operator_id: Optional[str] = None) -> bool:
        """
        Record operator acknowledgment.
        
        Returns:
            True if acknowledgment recorded.
        """
        if alert_id not in self._pending_alerts:
            logger.warning(f"OperatorAcknowledgmentLoop: Unknown alert {alert_id}")
            return False
        
        self._acknowledgments[alert_id] = AcknowledgmentRecord(
            alert_id=alert_id,
            acknowledged=True,
            operator_id=operator_id
        )
        
        del self._pending_alerts[alert_id]
        logger.info(f"OperatorAcknowledgmentLoop: Alert {alert_id} acknowledged by {operator_id}")
        return True
    
    def is_acknowledged(self, alert_id: str) -> bool:
        """Check if alert is acknowledged."""
        record = self._acknowledgments.get(alert_id)
        return record is not None and record.acknowledged
    
    def get_pending_count(self) -> int:
        """Get count of pending alerts."""
        return len(self._pending_alerts)
    
    def start(self) -> None:
        """Start escalation monitoring."""
        self._running = True
        self._thread = threading.Thread(target=self._escalation_loop, daemon=True)
        self._thread.start()
        logger.info("OperatorAcknowledgmentLoop: Started escalation monitoring")
    
    def stop(self) -> None:
        """Stop escalation monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _escalation_loop(self) -> None:
        """Check for alerts needing escalation."""
        while self._running:
            now = time.time()
            for alert_id, sent_time in list(self._pending_alerts.items()):
                if now - sent_time > self._escalation_timeout:
                    logger.warning(
                        f"OperatorAcknowledgmentLoop: Escalating alert {alert_id}"
                    )
                    if self._escalation_callback:
                        self._escalation_callback(alert_id)
                    # Mark as escalated (not removing from pending)
            
            time.sleep(10)  # Check every 10 seconds


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "SystemState",
    "PrivacyMode",
    "CircuitBreaker",
    "EphemeralEventBuffer",
    "FailureHandler",
    "HealthCheckProtocol",
    "OperatorAcknowledgmentLoop",
    "AcknowledgmentRecord",
]
