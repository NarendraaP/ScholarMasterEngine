"""
Fail-Safe Dropout Tests

ARCHITECTURE_CANONICAL.md 6.0 COMPLIANCE:
- System fails safe on edge/network/campus dropout
- No backlog replay after recovery
- Privacy mode on component isolation
"""
import pytest
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque


# =============================================================================
# FAILURE MODE DEFINITIONS
# =============================================================================

class FailureType(Enum):
    """Types of system failures."""
    EDGE_CAMERA = auto()      # Camera/sensor failure
    EDGE_PROCESSOR = auto()   # Pose/audio extractor failure
    NETWORK_MQTT = auto()     # MQTT broker unreachable
    NETWORK_API = auto()      # REST API failure
    CAMPUS_FEDERATION = auto() # Federation disconnect
    CAMPUS_ISOLATION = auto()  # Complete campus isolation


class FailSafeAction(Enum):
    """Actions taken on failure."""
    DROP_CURRENT = auto()     # Drop current data, continue
    ENTER_PRIVACY = auto()    # Enter privacy mode
    HALT_PROCESSING = auto()  # Stop processing pipeline
    BUFFER_LOCAL = auto()     # Buffer locally (limited)
    DISCARD_BUFFER = auto()   # Discard buffer on recovery


# =============================================================================
# FAIL-SAFE CONTROLLER
# =============================================================================

@dataclass
class FailureEvent:
    """Record of a failure event."""
    failure_type: FailureType
    timestamp: float
    action_taken: FailSafeAction
    data_dropped: int = 0
    recovered_at: Optional[float] = None


class FailSafeController:
    """
    Manages fail-safe behavior across system components.
    
    Per ARCHITECTURE_CANONICAL.md 6.0:
    - No backlog replay after recovery
    - Privacy mode on component failure
    - Stale data discarded
    """
    
    # Maximum buffer size before forced drop
    MAX_BUFFER_SIZE = 100
    
    # Maximum age of buffered data (seconds)
    MAX_BUFFER_AGE_SECONDS = 5.0
    
    # Components requiring privacy mode on failure
    PRIVACY_CRITICAL = {
        FailureType.EDGE_CAMERA,
        FailureType.EDGE_PROCESSOR,
        FailureType.CAMPUS_ISOLATION
    }
    
    def __init__(self):
        self._failures: List[FailureEvent] = []
        self._active_failures: Dict[FailureType, FailureEvent] = {}
        self._buffers: Dict[str, deque] = {}
        self._buffer_timestamps: Dict[str, float] = {}
        self._in_privacy_mode = False
        self._backlog_replay_enabled = False  # ALWAYS False per spec
    
    def report_failure(
        self, 
        failure_type: FailureType,
        context: Optional[Dict[str, Any]] = None
    ) -> FailSafeAction:
        """
        Report a component failure.
        
        Returns:
            Action to take in response.
        """
        action = self._determine_action(failure_type)
        
        event = FailureEvent(
            failure_type=failure_type,
            timestamp=time.time(),
            action_taken=action
        )
        
        self._failures.append(event)
        self._active_failures[failure_type] = event
        
        # Execute action
        self._execute_action(action, failure_type)
        
        return action
    
    def _determine_action(self, failure_type: FailureType) -> FailSafeAction:
        """Determine fail-safe action for failure type."""
        if failure_type in self.PRIVACY_CRITICAL:
            return FailSafeAction.ENTER_PRIVACY
        elif failure_type == FailureType.NETWORK_MQTT:
            return FailSafeAction.BUFFER_LOCAL
        elif failure_type == FailureType.CAMPUS_FEDERATION:
            return FailSafeAction.DROP_CURRENT
        else:
            return FailSafeAction.DROP_CURRENT
    
    def _execute_action(
        self, 
        action: FailSafeAction, 
        failure_type: FailureType
    ) -> None:
        """Execute the fail-safe action."""
        if action == FailSafeAction.ENTER_PRIVACY:
            self._in_privacy_mode = True
        elif action == FailSafeAction.BUFFER_LOCAL:
            self._init_buffer(str(failure_type))
    
    def _init_buffer(self, buffer_name: str) -> None:
        """Initialize a local buffer for failure mode."""
        if buffer_name not in self._buffers:
            self._buffers[buffer_name] = deque(maxlen=self.MAX_BUFFER_SIZE)
            self._buffer_timestamps[buffer_name] = time.time()
    
    def buffer_event(
        self, 
        buffer_name: str, 
        event: Dict[str, Any]
    ) -> bool:
        """
        Buffer an event during failure.
        
        Returns:
            True if buffered, False if dropped.
        """
        if buffer_name not in self._buffers:
            return False
        
        # Check buffer age
        age = time.time() - self._buffer_timestamps.get(buffer_name, 0)
        if age > self.MAX_BUFFER_AGE_SECONDS:
            # Buffer too old, discard
            self._buffers[buffer_name].clear()
            return False
        
        self._buffers[buffer_name].append(event)
        return True
    
    def report_recovery(self, failure_type: FailureType) -> int:
        """
        Report component recovery.
        
        CRITICAL: No backlog replay. All buffered data is discarded.
        
        Returns:
            Number of events discarded.
        """
        buffer_name = str(failure_type)
        discarded = 0
        
        # Discard buffer - NO REPLAY per ARCHITECTURE_CANONICAL.md 6.3
        if buffer_name in self._buffers:
            discarded = len(self._buffers[buffer_name])
            self._buffers[buffer_name].clear()
            del self._buffers[buffer_name]
        
        if buffer_name in self._buffer_timestamps:
            del self._buffer_timestamps[buffer_name]
        
        # Update failure record
        if failure_type in self._active_failures:
            self._active_failures[failure_type].recovered_at = time.time()
            self._active_failures[failure_type].data_dropped = discarded
            del self._active_failures[failure_type]
        
        # Exit privacy mode if no privacy-critical failures active
        active_privacy = any(
            ft in self.PRIVACY_CRITICAL 
            for ft in self._active_failures.keys()
        )
        if not active_privacy:
            self._in_privacy_mode = False
        
        return discarded
    
    def is_in_privacy_mode(self) -> bool:
        """Check if system is in privacy mode."""
        return self._in_privacy_mode
    
    def is_backlog_replay_enabled(self) -> bool:
        """Check if backlog replay is enabled (ALWAYS False)."""
        return self._backlog_replay_enabled
    
    def get_active_failures(self) -> List[FailureType]:
        """Get list of active failures."""
        return list(self._active_failures.keys())
    
    def get_buffer_size(self, buffer_name: str) -> int:
        """Get size of a buffer."""
        if buffer_name in self._buffers:
            return len(self._buffers[buffer_name])
        return 0


# =============================================================================
# EDGE DROPOUT TESTS
# =============================================================================

class TestEdgeDropout:
    """Tests for edge component failure handling."""
    
    def test_camera_failure_fails_safe(self):
        """Camera failure enters privacy mode."""
        ctrl = FailSafeController()
        
        action = ctrl.report_failure(FailureType.EDGE_CAMERA)
        
        assert action == FailSafeAction.ENTER_PRIVACY
        assert ctrl.is_in_privacy_mode()
    
    def test_pose_extractor_failure_fails_safe(self):
        """Pose extractor failure enters privacy mode."""
        ctrl = FailSafeController()
        
        action = ctrl.report_failure(FailureType.EDGE_PROCESSOR)
        
        assert action == FailSafeAction.ENTER_PRIVACY
        assert ctrl.is_in_privacy_mode()
    
    def test_no_stale_frames_replayed(self):
        """Stale frames are never replayed after recovery."""
        ctrl = FailSafeController()
        
        # Simulate failure
        ctrl.report_failure(FailureType.EDGE_CAMERA)
        
        # Recovery should not enable replay
        ctrl.report_recovery(FailureType.EDGE_CAMERA)
        
        assert not ctrl.is_backlog_replay_enabled()
    
    def test_edge_recovery_exits_privacy(self):
        """Edge recovery exits privacy mode."""
        ctrl = FailSafeController()
        
        ctrl.report_failure(FailureType.EDGE_CAMERA)
        assert ctrl.is_in_privacy_mode()
        
        ctrl.report_recovery(FailureType.EDGE_CAMERA)
        assert not ctrl.is_in_privacy_mode()


# =============================================================================
# NETWORK DROPOUT TESTS
# =============================================================================

class TestNetworkDropout:
    """Tests for network failure handling."""
    
    def test_mqtt_failure_buffers_locally(self):
        """MQTT failure enables local buffering."""
        ctrl = FailSafeController()
        
        action = ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        assert action == FailSafeAction.BUFFER_LOCAL
    
    def test_buffer_accepts_events(self):
        """Events can be buffered during MQTT failure."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        buffer_name = str(FailureType.NETWORK_MQTT)
        
        result = ctrl.buffer_event(buffer_name, {"event": "test"})
        
        assert result is True
        assert ctrl.get_buffer_size(buffer_name) == 1
    
    def test_reconnect_discards_stale_buffer(self):
        """Reconnection discards stale buffer data."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        buffer_name = str(FailureType.NETWORK_MQTT)
        
        # Buffer some events
        for i in range(5):
            ctrl.buffer_event(buffer_name, {"event": i})
        
        assert ctrl.get_buffer_size(buffer_name) == 5
        
        # Recovery discards all
        discarded = ctrl.report_recovery(FailureType.NETWORK_MQTT)
        
        assert discarded == 5
        assert ctrl.get_buffer_size(buffer_name) == 0
    
    def test_no_backlog_replay_after_recovery(self):
        """No backlog replay after network recovery."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        # Buffer events
        buffer_name = str(FailureType.NETWORK_MQTT)
        for i in range(10):
            ctrl.buffer_event(buffer_name, {"event": i})
        
        # Recovery
        ctrl.report_recovery(FailureType.NETWORK_MQTT)
        
        # Backlog replay must NEVER be enabled
        assert not ctrl.is_backlog_replay_enabled()
    
    def test_buffer_has_max_size(self):
        """Buffer has maximum size limit."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        buffer_name = str(FailureType.NETWORK_MQTT)
        
        # Try to buffer more than max
        for i in range(ctrl.MAX_BUFFER_SIZE + 50):
            ctrl.buffer_event(buffer_name, {"event": i})
        
        # Should be capped at MAX_BUFFER_SIZE
        assert ctrl.get_buffer_size(buffer_name) == ctrl.MAX_BUFFER_SIZE
    
    def test_network_dropout_not_privacy_mode(self):
        """Network dropout alone doesn't enter privacy mode."""
        ctrl = FailSafeController()
        
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        # Network failure doesn't require privacy mode
        assert not ctrl.is_in_privacy_mode()


# =============================================================================
# CAMPUS DROPOUT TESTS
# =============================================================================

class TestCampusDropout:
    """Tests for campus/federation failure handling."""
    
    def test_federation_disconnect_handled(self):
        """Federation disconnect drops current data."""
        ctrl = FailSafeController()
        
        action = ctrl.report_failure(FailureType.CAMPUS_FEDERATION)
        
        assert action == FailSafeAction.DROP_CURRENT
    
    def test_gradients_not_queued_for_replay(self):
        """Gradients are not queued for later replay."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.CAMPUS_FEDERATION)
        
        # Federation failures use DROP, not BUFFER
        buffer_name = str(FailureType.CAMPUS_FEDERATION)
        
        # Should fail - no buffer created
        result = ctrl.buffer_event(buffer_name, {"gradient": [1, 2, 3]})
        
        assert result is False
    
    def test_privacy_mode_on_campus_isolation(self):
        """Campus isolation enters privacy mode."""
        ctrl = FailSafeController()
        
        action = ctrl.report_failure(FailureType.CAMPUS_ISOLATION)
        
        assert action == FailSafeAction.ENTER_PRIVACY
        assert ctrl.is_in_privacy_mode()
    
    def test_isolation_recovery_requires_all_components(self):
        """Privacy mode only exits when all critical components recover."""
        ctrl = FailSafeController()
        
        # Multiple failures
        ctrl.report_failure(FailureType.CAMPUS_ISOLATION)
        ctrl.report_failure(FailureType.EDGE_CAMERA)
        
        assert ctrl.is_in_privacy_mode()
        
        # Recover one
        ctrl.report_recovery(FailureType.CAMPUS_ISOLATION)
        
        # Still in privacy mode due to camera failure
        assert ctrl.is_in_privacy_mode()
        
        # Recover camera
        ctrl.report_recovery(FailureType.EDGE_CAMERA)
        
        # Now exits privacy mode
        assert not ctrl.is_in_privacy_mode()


# =============================================================================
# FAIL-SAFE INVARIANTS
# =============================================================================

class TestFailSafeInvariants:
    """Tests for critical fail-safe invariants."""
    
    def test_backlog_replay_never_enabled(self):
        """Backlog replay is NEVER enabled, regardless of state."""
        ctrl = FailSafeController()
        
        # Initial state
        assert not ctrl.is_backlog_replay_enabled()
        
        # During failure
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        assert not ctrl.is_backlog_replay_enabled()
        
        # After recovery
        ctrl.report_recovery(FailureType.NETWORK_MQTT)
        assert not ctrl.is_backlog_replay_enabled()
        
        # After multiple cycles
        for _ in range(5):
            ctrl.report_failure(FailureType.NETWORK_MQTT)
            ctrl.report_recovery(FailureType.NETWORK_MQTT)
        
        assert not ctrl.is_backlog_replay_enabled()
    
    def test_failure_events_logged(self):
        """All failure events are logged for audit."""
        ctrl = FailSafeController()
        
        ctrl.report_failure(FailureType.EDGE_CAMERA)
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        assert len(ctrl._failures) == 2
    
    def test_recovery_records_discarded_count(self):
        """Recovery records how much data was discarded."""
        ctrl = FailSafeController()
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        
        buffer_name = str(FailureType.NETWORK_MQTT)
        for i in range(7):
            ctrl.buffer_event(buffer_name, {"event": i})
        
        discarded = ctrl.report_recovery(FailureType.NETWORK_MQTT)
        
        assert discarded == 7
        
        # Check failure record updated
        for event in ctrl._failures:
            if event.failure_type == FailureType.NETWORK_MQTT:
                assert event.data_dropped == 7
                assert event.recovered_at is not None
    
    def test_concurrent_failures_handled(self):
        """Multiple concurrent failures are all tracked."""
        ctrl = FailSafeController()
        
        ctrl.report_failure(FailureType.EDGE_CAMERA)
        ctrl.report_failure(FailureType.NETWORK_MQTT)
        ctrl.report_failure(FailureType.CAMPUS_FEDERATION)
        
        active = ctrl.get_active_failures()
        
        assert len(active) == 3
        assert FailureType.EDGE_CAMERA in active
        assert FailureType.NETWORK_MQTT in active
        assert FailureType.CAMPUS_FEDERATION in active
