#!/usr/bin/env python3
"""
Canonical Architecture Compliance Tests
========================================
Tests that verify implementation matches ARCHITECTURE_CANONICAL.md.

These tests serve as enforcement checkpoints for CI systems.
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Import canonical layers
from core.canonical_layers import (
    PhysicalSubstrate,
    SensorAcquisition,
    EdgeAbstraction,
    FrameDestructionError,
    GovernanceFilter,
    GovernanceState,
    EphemeralMemoryZone,
    FederationCoordinator,
    CanonicalRuntimeEngine,
)

# Import failure semantics
from core.failure_semantics import (
    SystemState,
    PrivacyMode,
    CircuitBreaker,
    EphemeralEventBuffer,
    FailureHandler,
    HealthCheckProtocol,
    OperatorAcknowledgmentLoop,
)


# =============================================================================
# L1: PHYSICAL SUBSTRATE TESTS
# =============================================================================

class TestL1PhysicalSubstrate:
    """Tests for L1 Physical Substrate layer."""
    
    def test_initialization(self):
        """L1 must initialize with volatile memory verification."""
        l1 = PhysicalSubstrate()
        assert not l1._operational
        assert not l1._volatile_memory_verified
    
    def test_verify_volatile_memory(self):
        """L1 must verify volatile memory support."""
        l1 = PhysicalSubstrate()
        assert l1.verify_volatile_memory_support()
        assert l1._volatile_memory_verified
    
    def test_start_requires_volatile_verification(self):
        """L1 start must verify volatile memory if not done."""
        l1 = PhysicalSubstrate()
        result = l1.start()
        assert result
        assert l1._volatile_memory_verified
        assert l1._operational
    
    def test_operational_status(self):
        """L1 must provide operational status signals."""
        l1 = PhysicalSubstrate()
        l1.start()
        status = l1.get_operational_status()
        assert status["operational"]
        assert "uptime_seconds" in status
        assert status["volatile_memory_verified"]


# =============================================================================
# L3: EDGE ABSTRACTION TESTS (IRREVERSIBILITY)
# =============================================================================

class TestL3EdgeAbstraction:
    """Tests for L3 Edge Abstraction (Irreversible Boundary)."""
    
    @pytest.fixture
    def l3_setup(self):
        """Setup L2 and L3 layers."""
        l1 = PhysicalSubstrate()
        l1.start()
        l2 = SensorAcquisition(l1)
        l3 = EdgeAbstraction(l2)
        return l3
    
    def test_frame_ttl_constant(self, l3_setup):
        """Frame TTL must be 33ms per ARCHITECTURE_CANONICAL.md."""
        assert l3_setup.FRAME_TTL_MS == 33
    
    def test_audio_ttl_constant(self, l3_setup):
        """Audio TTL must be 3 seconds per ARCHITECTURE_CANONICAL.md."""
        assert l3_setup.AUDIO_TTL_SECONDS == 3
    
    def test_max_skeleton_dimensions(self, l3_setup):
        """Skeleton must have max 34 dimensions per ARCHITECTURE_CANONICAL.md."""
        assert l3_setup.MAX_SKELETON_DIMS == 34
    
    def test_min_compression_ratio(self, l3_setup):
        """Compression ratio must be at least 1000:1."""
        assert l3_setup.MIN_COMPRESSION_RATIO == 1000
    
    def test_frame_destruction(self, l3_setup):
        """Frame must be destroyed after skeleton extraction."""
        mock_frame = Mock()
        mock_frame.nbytes = 1920 * 1080 * 3
        
        skeleton = [0.5] * 34  # Valid 34-dim skeleton
        extractor = Mock(return_value=skeleton)
        
        result = l3_setup.transform_frame_to_skeleton(mock_frame, extractor)
        
        assert result["original_destroyed"]
        assert result["transform_type"] == "irreversible"
    
    def test_oversized_skeleton_rejected(self, l3_setup):
        """Skeleton with >34 dimensions must be rejected."""
        mock_frame = Mock()
        mock_frame.nbytes = 1920 * 1080 * 3
        
        oversized_skeleton = [0.5] * 100  # Too many dimensions
        extractor = Mock(return_value=oversized_skeleton)
        
        with pytest.raises(ValueError, match="max allowed is 34"):
            l3_setup.transform_frame_to_skeleton(mock_frame, extractor)
    
    def test_destruction_callback(self, l3_setup):
        """Destruction callbacks must be invoked."""
        callback_invoked = []
        
        def callback(frame_id, elapsed_ms):
            callback_invoked.append((frame_id, elapsed_ms))
        
        l3_setup.add_destruction_callback(callback)
        
        mock_frame = Mock()
        mock_frame.nbytes = 1000
        extractor = Mock(return_value=[0.5] * 34)
        
        l3_setup.transform_frame_to_skeleton(mock_frame, extractor)
        
        assert len(callback_invoked) == 1
        assert callback_invoked[0][1] < 33  # Within TTL


# =============================================================================
# L5: GOVERNANCE FILTER TESTS
# =============================================================================

class TestL5GovernanceFilter:
    """Tests for L5 Governance & Compliance Filter."""
    
    @pytest.fixture
    def l5(self):
        """Create governance filter."""
        return GovernanceFilter()
    
    def test_allowlist_only(self, l5):
        """L5 must use allowlist, not denylist."""
        assert hasattr(l5, 'ALLOWED_FIELDS')
        assert "zone_id" in l5.ALLOWED_FIELDS
        assert "raw_frame" not in l5.ALLOWED_FIELDS
    
    def test_event_ordering_enforced(self, l5):
        """Event ordering must be: INFERENCE_COMPLETE → COMPLIANCE_CHECKED → APPROVED."""
        event_id = "test_001"
        payload = {"zone_id": "Zone_1", "timestamp": time.time()}
        
        # Stage 1: Inference complete
        l5.receive_inference_complete(event_id, payload)
        stages = l5.get_event_stages(event_id)
        assert stages == ["INFERENCE_COMPLETE"]
        
        # Stage 2: Compliance check
        l5.compliance_check(event_id)
        stages = l5.get_event_stages(event_id)
        assert stages == ["INFERENCE_COMPLETE", "COMPLIANCE_CHECKED"]
        
        # Stage 3: Approve for output
        l5.approve_for_output(event_id)
        stages = l5.get_event_stages(event_id)
        assert stages == ["INFERENCE_COMPLETE", "COMPLIANCE_CHECKED", "APPROVED_FOR_OUTPUT"]
    
    def test_bypass_prevention_compliance_before_inference(self, l5):
        """Compliance check without inference complete must fail."""
        event_id = "test_002"
        result = l5.compliance_check(event_id)
        assert result is False
    
    def test_bypass_prevention_approve_before_compliance(self, l5):
        """Approve without compliance check must fail."""
        event_id = "test_003"
        payload = {"zone_id": "Zone_1"}
        
        l5.receive_inference_complete(event_id, payload)
        # Skip compliance check
        result = l5.approve_for_output(event_id)
        assert result is None  # Must fail
    
    def test_unknown_fields_rejected(self, l5):
        """Unknown fields must be rejected (not ignored)."""
        event_id = "test_004"
        payload = {
            "zone_id": "Zone_1",
            "unknown_field": "should_fail"  # Not in allowlist
        }
        
        l5.receive_inference_complete(event_id, payload)
        result = l5.compliance_check(event_id)
        
        assert result is False
        decision = l5.get_decision(event_id)
        assert decision.state == GovernanceState.REJECTED
        assert "Forbidden fields" in decision.reason


# =============================================================================
# L7: EPHEMERAL MEMORY ZONE TESTS
# =============================================================================

class TestL7EphemeralMemoryZone:
    """Tests for L7 Ephemeral Memory Zone."""
    
    def test_ram_only_storage(self):
        """L7 must store in RAM only (ephemeral)."""
        l7 = EphemeralMemoryZone(session_ttl_seconds=3600)
        
        event = {"zone_id": "Zone_1", "event_type": "POSE_DETECTED"}
        result = l7.store_event("evt_001", event)
        
        assert result
        assert l7.get_event("evt_001") == event
    
    def test_session_ttl(self):
        """Events must be cleared on session expiry."""
        l7 = EphemeralMemoryZone(session_ttl_seconds=0.1)  # 100ms TTL
        
        event = {"zone_id": "Zone_1"}
        l7.store_event("evt_001", event)
        
        time.sleep(0.2)  # Wait for TTL
        
        result = l7.get_event("evt_001")
        assert result is None  # Expired
    
    def test_memory_zeroed_on_session_end(self):
        """Memory must be zeroed on session end."""
        l7 = EphemeralMemoryZone()
        
        l7.store_event("evt_001", {"zone_id": "Zone_1"})
        l7.store_event("evt_002", {"zone_id": "Zone_2"})
        
        l7.end_session()
        
        assert l7.get_event("evt_001") is None
        assert l7.get_event("evt_002") is None
        assert l7.get_event_stream() == []


# =============================================================================
# L8: FEDERATION COORDINATOR TESTS
# =============================================================================

class TestL8FederationCoordinator:
    """Tests for L8 Federated Adaptation & Coordination."""
    
    @pytest.fixture
    def l8(self):
        """Create federation coordinator."""
        return FederationCoordinator()
    
    def test_join_requires_consent(self, l8):
        """Campus join must require explicit consent."""
        # Without consent
        result = l8.join_federation("campus_1", consent_attestation=False)
        assert result is False
        
        # With consent
        result = l8.join_federation("campus_1", consent_attestation=True)
        assert result is True
    
    def test_withdrawal_no_justification(self, l8):
        """Campus withdrawal must not require justification."""
        l8.join_federation("campus_1", consent_attestation=True)
        
        # Withdraw without justification
        result = l8.withdraw_from_federation("campus_1")
        assert result is True
    
    def test_withdrawal_purges_gradients(self, l8):
        """Withdrawal must purge campus gradients."""
        l8.join_federation("campus_1", consent_attestation=True)
        l8.contribute_gradient("campus_1", {"gradient": [0.1, 0.2]})
        
        l8.withdraw_from_federation("campus_1")
        
        assert "campus_1" not in l8._gradient_contributions
    
    def test_withdrawal_revokes_consent(self, l8):
        """Withdrawal must revoke consent."""
        l8.join_federation("campus_1", consent_attestation=True)
        assert l8.verify_consent("campus_1")
        
        l8.withdraw_from_federation("campus_1")
        assert not l8.verify_consent("campus_1")
    
    def test_gradient_requires_consent(self, l8):
        """Gradient contribution must require verified consent."""
        l8.join_federation("campus_1", consent_attestation=True)
        l8.revoke_consent("campus_1")
        
        result = l8.contribute_gradient("campus_1", {"gradient": [0.1]})
        assert result is False


# =============================================================================
# FAILURE SEMANTICS TESTS
# =============================================================================

class TestFailureSemantics:
    """Tests for failure handling per ARCHITECTURE_CANONICAL.md Section 7."""
    
    @pytest.fixture
    def handler(self):
        """Create failure handler."""
        return FailureHandler()
    
    def test_mqtt_failure_buffers_locally(self, handler):
        """MQTT failure must buffer events in RAM."""
        event = {"zone_id": "Zone_1", "event_type": "ALERT"}
        
        handler.handle_mqtt_failure(event)
        
        assert handler._event_buffer.size() == 1
        assert handler.get_state() == SystemState.MQTT_FAILURE
    
    def test_governance_failure_blocks_l6(self, handler):
        """Governance failure must block all L4→L6 traffic."""
        handler.handle_governance_failure()
        
        assert not handler.can_pass_to_human_interface()
        assert handler.get_state() == SystemState.GOVERNANCE_FAILURE
    
    def test_crash_recovery_privacy_mode(self, handler):
        """Crash recovery must initialize to PRIVACY mode."""
        handler._privacy_mode = PrivacyMode.ACTIVE
        
        handler.recover_from_crash()
        
        assert handler.get_privacy_mode() == PrivacyMode.PRIVACY
    
    def test_active_mode_requires_operator_ack(self, handler):
        """ACTIVE mode requires operator acknowledgment."""
        handler.recover_from_crash()
        
        # Without ack
        result = handler.request_active_mode(operator_ack=False)
        assert result is False
        assert handler.get_privacy_mode() == PrivacyMode.PRIVACY
        
        # With ack
        result = handler.request_active_mode(operator_ack=True)
        assert result is True
        assert handler.get_privacy_mode() == PrivacyMode.ACTIVE
    
    def test_boot_led_required(self, handler):
        """Privacy LED must be set at boot."""
        # LED not set
        assert not handler.verify_boot_led()
        assert handler.get_state() == SystemState.HALTED
    
    def test_boot_led_set(self, handler):
        """Boot with LED set must succeed."""
        handler.set_boot_privacy_led(PrivacyMode.PRIVACY)
        assert handler.verify_boot_led()


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""
    
    def test_opens_after_threshold(self):
        """Circuit must open after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.is_available()
        
        breaker.record_failure()
        assert not breaker.is_available()
    
    def test_resets_on_success(self):
        """Circuit must reset on success."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_success()
        
        assert breaker._failure_count == 0


class TestOperatorAcknowledgment:
    """Tests for operator acknowledgment loop."""
    
    def test_alert_requires_ack(self):
        """Critical alerts must require acknowledgment."""
        loop = OperatorAcknowledgmentLoop()
        
        loop.require_acknowledgment("alert_001")
        assert not loop.is_acknowledged("alert_001")
        assert loop.get_pending_count() == 1
    
    def test_ack_recorded(self):
        """Acknowledgment must be logged."""
        loop = OperatorAcknowledgmentLoop()
        
        loop.require_acknowledgment("alert_001")
        loop.acknowledge("alert_001", operator_id="op_123")
        
        assert loop.is_acknowledged("alert_001")
        assert loop.get_pending_count() == 0


# =============================================================================
# CANONICAL RUNTIME ENGINE TESTS
# =============================================================================

class TestCanonicalRuntimeEngine:
    """Tests for complete canonical runtime."""
    
    def test_start_stop(self):
        """Engine must start and stop cleanly."""
        engine = CanonicalRuntimeEngine()
        
        assert engine.start()
        assert engine._running
        
        engine.stop()
        assert not engine._running
    
    def test_process_frame_through_layers(self):
        """Frame must pass through L2→L3→L5→L7."""
        engine = CanonicalRuntimeEngine()
        engine.start()
        
        mock_frame = Mock()
        mock_frame.nbytes = 1920 * 1080 * 3
        
        skeleton = [0.5] * 34
        extractor = Mock(return_value=skeleton)
        
        result = engine.process_frame(mock_frame, extractor)
        
        assert result is not None
        assert "skeleton_keypoints" in result
        
        engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
