"""
Governance Filter Tests

ARCHITECTURE_CANONICAL.md 4.0 COMPLIANCE:
- All L4 inference outputs must pass L5 governance filter
- Four paths: ALLOW, DROP, TRANSFORM, ESCALATE
- No output reaches L6 without governance approval
"""
import pytest
from enum import Enum, auto
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
import time

from core.canonical_layers import GovernanceFilter, GovernanceState, GovernanceDecision


# =============================================================================
# GOVERNANCE DECISION ENUM
# =============================================================================

class GovernanceAction(Enum):
    """Governance filter decision actions."""
    ALLOW = auto()      # Pass through to L6
    DROP = auto()       # Block from reaching L6
    TRANSFORM = auto()  # Modify (anonymize/redact) before L6
    ESCALATE = auto()   # Require operator acknowledgment


# =============================================================================
# EXTENDED GOVERNANCE FILTER
# =============================================================================

class ExtendedGovernanceFilter(GovernanceFilter):
    """
    Extended governance filter with ALLOW/DROP/TRANSFORM/ESCALATE paths.
    
    Per ARCHITECTURE_CANONICAL.md 4.0:
    - ALLOW: Valid event passes to L6
    - DROP: Forbidden/invalid event blocked
    - TRANSFORM: PII redacted before L6
    - ESCALATE: High-severity requires operator ack
    """
    
    # Extended allowlist
    ALLOWED_FIELDS = {
        "zone_id", "timestamp", "event_type", "severity",
        "skeleton_keypoints", "audio_class", "event_id",
        "source_paper", "is_valid", "reason",
        # Operational fields
        "alert_type", "message", "student_count",
        "engagement_score", "check_type", "metric_type"
    }
    
    # Fields requiring transformation (PII)
    PII_FIELDS = {"student_id", "face_id", "person_name", "email"}
    
    # Severity threshold for escalation
    ESCALATION_THRESHOLD = 0.8
    
    def __init__(self):
        super().__init__()
        self._escalated_events: Dict[str, Dict] = {}
        self._operator_acks: Dict[str, bool] = {}
        self._transformations: Dict[str, List[str]] = {}
    
    def process_inference_output(
        self, 
        event_id: str, 
        payload: Dict[str, Any]
    ) -> tuple[GovernanceAction, Dict[str, Any]]:
        """
        Process L4 inference output through governance filter.
        
        Returns:
            (action, processed_payload)
        """
        # Check for DROP conditions first (before any processing)
        drop_action = self._check_drop_conditions(event_id, payload)
        if drop_action:
            return GovernanceAction.DROP, {}
        
        # Check for TRANSFORM conditions - apply PII redaction
        transformed_payload, transforms = self._apply_transforms(payload)
        if transforms:
            self._transformations[event_id] = transforms
        
        # Remove PII fields from transformed payload for compliance
        compliance_payload = {k: v for k, v in transformed_payload.items() 
                              if k not in self.PII_FIELDS}
        
        # Stage 1: Receive inference with cleaned payload
        self.receive_inference_complete(event_id, compliance_payload)
        
        # Check for ESCALATE conditions
        if self._requires_escalation(payload):
            self._escalated_events[event_id] = transformed_payload
            return GovernanceAction.ESCALATE, transformed_payload
        
        # Stage 2: Compliance check
        if not self.compliance_check(event_id):
            return GovernanceAction.DROP, {}
        
        # Stage 3: Approve
        approved = self.approve_for_output(event_id)
        if approved:
            return GovernanceAction.ALLOW, transformed_payload
        
        return GovernanceAction.DROP, {}
    
    def _check_drop_conditions(
        self, 
        event_id: str, 
        payload: Dict[str, Any]
    ) -> bool:
        """Check if event should be dropped."""
        # Check for forbidden fields (not in allowlist, not PII)
        payload_keys = set(payload.keys())
        forbidden = payload_keys - self.ALLOWED_FIELDS - self.PII_FIELDS
        
        if forbidden:
            self._decisions[event_id] = GovernanceDecision(
                event_id=event_id,
                state=GovernanceState.REJECTED,
                reason=f"Forbidden fields: {forbidden}"
            )
            return True
        
        # Check for invalid event marker
        if payload.get("is_valid") is False:
            self._decisions[event_id] = GovernanceDecision(
                event_id=event_id,
                state=GovernanceState.REJECTED,
                reason="Event marked as invalid"
            )
            return True
        
        return False
    
    def _apply_transforms(
        self, 
        payload: Dict[str, Any]
    ) -> tuple[Dict[str, Any], List[str]]:
        """Apply transformations (PII redaction)."""
        transformed = payload.copy()
        transforms = []
        
        for pii_field in self.PII_FIELDS:
            if pii_field in transformed:
                # Anonymize: hash or redact
                original = transformed[pii_field]
                transformed[pii_field] = f"[REDACTED:{hash(str(original)) % 10000}]"
                transforms.append(f"redacted:{pii_field}")
        
        return transformed, transforms
    
    def _requires_escalation(self, payload: Dict[str, Any]) -> bool:
        """Check if event requires operator escalation."""
        severity = payload.get("severity", 0.0)
        return severity >= self.ESCALATION_THRESHOLD
    
    def acknowledge_escalation(self, event_id: str, operator_id: str) -> bool:
        """
        Operator acknowledges escalated event.
        
        Per ARCHITECTURE_CANONICAL.md 6.4:
        - Human acknowledgment required for high-severity
        """
        if event_id not in self._escalated_events:
            return False
        
        self._operator_acks[event_id] = True
        
        # Now allow through governance
        self.compliance_check(event_id)
        self.approve_for_output(event_id)
        
        return True
    
    def is_escalation_acknowledged(self, event_id: str) -> bool:
        """Check if escalation was acknowledged."""
        return self._operator_acks.get(event_id, False)
    
    def get_transformations(self, event_id: str) -> List[str]:
        """Get list of transformations applied."""
        return self._transformations.get(event_id, [])


# =============================================================================
# ALLOW PATH TESTS
# =============================================================================

class TestAllowPath:
    """Tests for ALLOW governance path."""
    
    def test_valid_event_allowed(self):
        """Valid inference output is ALLOWED through."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_001",
            "event_type": "HAND_RAISE",
            "zone_id": "classroom_A",
            "timestamp": time.time(),
            "severity": 0.3
        }
        
        action, result = gov.process_inference_output("evt_001", payload)
        
        assert action == GovernanceAction.ALLOW
        assert result["event_type"] == "HAND_RAISE"
    
    def test_governance_attestation_attached(self):
        """Approved event has governance attestation."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_002",
            "event_type": "ATTENTION_LOW",
            "zone_id": "lab_B",
            "timestamp": time.time(),
            "severity": 0.2
        }
        
        action, _ = gov.process_inference_output("evt_002", payload)
        
        assert action == GovernanceAction.ALLOW
        
        # Check governance decision
        decision = gov.get_decision("evt_002")
        assert decision is not None
        assert decision.approved_for_output is True
    
    def test_allowlist_fields_pass(self):
        """All allowlisted fields pass through."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "zone_id": "zone_1",
            "timestamp": 12345.0,
            "event_type": "SAFETY_ALERT",
            "severity": 0.5,
            "skeleton_keypoints": [1, 2, 3],
            "audio_class": "speech",
            "event_id": "evt_003"
        }
        
        action, result = gov.process_inference_output("evt_003", payload)
        
        assert action == GovernanceAction.ALLOW


# =============================================================================
# DROP PATH TESTS
# =============================================================================

class TestDropPath:
    """Tests for DROP governance path."""
    
    def test_forbidden_fields_dropped(self):
        """Events with forbidden fields are DROPPED."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_drop_1",
            "event_type": "FACE_MATCH",
            "zone_id": "door_entry",
            "face_embedding": [0.1, 0.2, 0.3],  # FORBIDDEN
            "biometric_vector": [0.5, 0.6]  # FORBIDDEN
        }
        
        action, result = gov.process_inference_output("evt_drop_1", payload)
        
        assert action == GovernanceAction.DROP
        assert result == {}
    
    def test_invalid_event_dropped(self):
        """Events marked invalid are DROPPED."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_drop_2",
            "event_type": "ATTENTION",
            "zone_id": "room_1",
            "is_valid": False,
            "reason": "Low confidence"
        }
        
        action, result = gov.process_inference_output("evt_drop_2", payload)
        
        assert action == GovernanceAction.DROP
    
    def test_unapproved_event_dropped(self):
        """Events that fail compliance check are DROPPED."""
        gov = ExtendedGovernanceFilter()
        
        # Set a validator that rejects
        gov.set_validator(lambda p: (False, "Rejected by ST-CSF"))
        
        payload = {
            "event_id": "evt_drop_3",
            "event_type": "ANOMALY",
            "zone_id": "corridor"
        }
        
        # Manually trigger stages without full processing
        gov.receive_inference_complete("evt_drop_3", payload)
        result = gov.compliance_check("evt_drop_3")
        
        assert result is False
        
        decision = gov.get_decision("evt_drop_3")
        assert decision.state == GovernanceState.REJECTED
    
    def test_drop_reason_logged(self):
        """Dropped events have reason logged."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_drop_4",
            "raw_frame_data": b"bytes",  # FORBIDDEN
        }
        
        action, _ = gov.process_inference_output("evt_drop_4", payload)
        
        assert action == GovernanceAction.DROP
        
        decision = gov.get_decision("evt_drop_4")
        assert "Forbidden fields" in decision.reason


# =============================================================================
# TRANSFORM PATH TESTS
# =============================================================================

class TestTransformPath:
    """Tests for TRANSFORM governance path."""
    
    def test_pii_redacted(self):
        """PII fields are redacted before output."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_transform_1",
            "event_type": "ATTENDANCE",
            "zone_id": "entrance",
            "student_id": "STU_12345",  # PII - will be redacted
            "timestamp": time.time()
        }
        
        action, result = gov.process_inference_output("evt_transform_1", payload)
        
        assert action == GovernanceAction.ALLOW
        assert result["student_id"].startswith("[REDACTED:")
        assert "STU_12345" not in result["student_id"]
    
    def test_multiple_pii_redacted(self):
        """Multiple PII fields are all redacted."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_transform_2",
            "event_type": "PROFILE_UPDATE",
            "zone_id": "admin",
            "student_id": "STU_999",
            "person_name": "John Doe",
            "email": "john@school.edu",
            "timestamp": time.time()
        }
        
        action, result = gov.process_inference_output("evt_transform_2", payload)
        
        # All PII should be redacted
        assert "[REDACTED:" in result["student_id"]
        assert "[REDACTED:" in result["person_name"]
        assert "[REDACTED:" in result["email"]
    
    def test_transformations_tracked(self):
        """Applied transformations are tracked."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_transform_3",
            "event_type": "ALERT",
            "zone_id": "room_1",
            "face_id": "face_abc123",
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_transform_3", payload)
        
        transforms = gov.get_transformations("evt_transform_3")
        assert "redacted:face_id" in transforms
    
    def test_identifier_anonymized(self):
        """Identifiers are anonymized consistently."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_transform_4",
            "event_type": "TRACKING",
            "zone_id": "hall",
            "student_id": "STU_SAME",
            "timestamp": time.time()
        }
        
        action, result1 = gov.process_inference_output("evt_transform_4", payload)
        
        # Same student_id should produce same hash
        gov2 = ExtendedGovernanceFilter()
        payload2 = {
            "event_id": "evt_transform_5",
            "event_type": "TRACKING",
            "zone_id": "hall",
            "student_id": "STU_SAME",
            "timestamp": time.time()
        }
        _, result2 = gov2.process_inference_output("evt_transform_5", payload2)
        
        # Anonymization should be consistent (same hash)
        assert result1["student_id"] == result2["student_id"]


# =============================================================================
# ESCALATE PATH TESTS
# =============================================================================

class TestEscalatePath:
    """Tests for ESCALATE governance path."""
    
    def test_high_severity_escalated(self):
        """High severity events are ESCALATED."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_escalate_1",
            "event_type": "VIOLENCE_DETECTED",
            "zone_id": "playground",
            "severity": 0.95,  # Above threshold
            "timestamp": time.time()
        }
        
        action, result = gov.process_inference_output("evt_escalate_1", payload)
        
        assert action == GovernanceAction.ESCALATE
    
    def test_escalation_requires_ack(self):
        """Escalated events require operator acknowledgment."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_escalate_2",
            "event_type": "EMERGENCY",
            "zone_id": "lab",
            "severity": 0.9,
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_escalate_2", payload)
        
        assert action == GovernanceAction.ESCALATE
        assert not gov.is_escalation_acknowledged("evt_escalate_2")
    
    def test_ack_allows_output(self):
        """Acknowledged escalation allows output."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_escalate_3",
            "event_type": "CRITICAL_ALERT",
            "zone_id": "server_room",
            "severity": 0.85,
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_escalate_3", payload)
        assert action == GovernanceAction.ESCALATE
        
        # Operator acknowledges
        ack_result = gov.acknowledge_escalation("evt_escalate_3", "operator_1")
        assert ack_result is True
        assert gov.is_escalation_acknowledged("evt_escalate_3")
        
        # Now should be approved
        assert gov.is_approved("evt_escalate_3")
    
    def test_unacked_event_not_approved(self):
        """Unacknowledged escalation is not approved."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_escalate_4",
            "event_type": "SECURITY_BREACH",
            "zone_id": "entrance",
            "severity": 0.99,
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_escalate_4", payload)
        
        assert action == GovernanceAction.ESCALATE
        assert not gov.is_approved("evt_escalate_4")
    
    def test_severity_threshold_boundary(self):
        """Events at exactly threshold are escalated."""
        gov = ExtendedGovernanceFilter()
        
        # Exactly at threshold
        payload = {
            "event_id": "evt_escalate_5",
            "event_type": "ALERT",
            "zone_id": "room",
            "severity": 0.8,  # Exactly at threshold
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_escalate_5", payload)
        
        assert action == GovernanceAction.ESCALATE
    
    def test_below_threshold_not_escalated(self):
        """Events below threshold are not escalated."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_no_escalate",
            "event_type": "INFO",
            "zone_id": "room",
            "severity": 0.79,  # Below threshold
            "timestamp": time.time()
        }
        
        action, _ = gov.process_inference_output("evt_no_escalate", payload)
        
        assert action == GovernanceAction.ALLOW


# =============================================================================
# EVENT ORDERING TESTS
# =============================================================================

class TestEventOrdering:
    """Tests for mandatory event ordering (INFERENCE→COMPLIANCE→APPROVED)."""
    
    def test_stages_in_order(self):
        """Events pass through stages in correct order."""
        gov = ExtendedGovernanceFilter()
        
        payload = {
            "event_id": "evt_order_1",
            "event_type": "TEST",
            "zone_id": "test",
            "timestamp": time.time()
        }
        
        gov.process_inference_output("evt_order_1", payload)
        
        stages = gov.get_event_stages("evt_order_1")
        
        assert "INFERENCE_COMPLETE" in stages
        assert "COMPLIANCE_CHECKED" in stages
        assert "APPROVED_FOR_OUTPUT" in stages
        
        # Check order
        assert stages.index("INFERENCE_COMPLETE") < stages.index("COMPLIANCE_CHECKED")
        assert stages.index("COMPLIANCE_CHECKED") < stages.index("APPROVED_FOR_OUTPUT")
    
    def test_compliance_before_inference_fails(self):
        """Compliance check before inference fails."""
        gov = ExtendedGovernanceFilter()
        
        # Try compliance without inference
        result = gov.compliance_check("unknown_event")
        
        assert result is False
    
    def test_approve_before_compliance_fails(self):
        """Approve before compliance fails."""
        gov = ExtendedGovernanceFilter()
        
        gov.receive_inference_complete("evt_order_2", {"event_type": "TEST"})
        
        # Skip compliance, try approve
        result = gov.approve_for_output("evt_order_2")
        
        assert result is None
