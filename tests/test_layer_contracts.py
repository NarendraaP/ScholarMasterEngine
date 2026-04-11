"""
Tests for Layer Boundary Contracts

ARCHITECTURE_CANONICAL.md Section 2 Compliance:
- Data flows unidirectionally from L1 to L8
- Bypass of any layer is prohibited
- No module may access upstream raw data
"""
import pytest
import numpy as np
from core.layer_contracts import (
    Layer, LayerBoundaryEnforcer, LayerBoundaryViolation,
    L2Output, L3Output, L4Output, L5Output,
    layer_guard, forbid_upstream_data, require_governance_approval,
    FORBIDDEN_OUTPUTS, UPSTREAM_FORBIDDEN,
    get_enforcer, reset_enforcer
)


# =============================================================================
# FIXTURE
# =============================================================================

@pytest.fixture(autouse=True)
def reset():
    """Reset enforcer before each test."""
    reset_enforcer()


# =============================================================================
# L3 OUTPUT TESTS
# =============================================================================

class TestL3Output:
    """Tests for L3 Edge Abstraction output constraints."""
    
    def test_skeleton_max_34_dims(self):
        """Skeleton must not exceed 34 dimensions."""
        # Valid: 34 dimensions
        output = L3Output(skeleton_keypoints=tuple(range(34)))
        assert len(output.skeleton_keypoints) == 34
    
    def test_skeleton_exceeds_34_rejected(self):
        """Skeleton > 34 dimensions is rejected."""
        with pytest.raises(ValueError, match="max 34 dims"):
            L3Output(skeleton_keypoints=tuple(range(50)))
    
    def test_layer_source_is_l3(self):
        """Output is tagged with L3 source."""
        output = L3Output()
        assert output._layer_source == Layer.L3_EDGE


class TestL4Output:
    """Tests for L4 Local Inference output constraints."""
    
    def test_must_be_anonymous(self):
        """L4 output must be anonymous."""
        output = L4Output(event_type="HAND_RAISE", is_anonymous=True)
        assert output.is_anonymous
    
    def test_non_anonymous_rejected(self):
        """Non-anonymous output is rejected."""
        with pytest.raises(ValueError, match="must be anonymous"):
            L4Output(event_type="FACE_ID", is_anonymous=False)


class TestL5Output:
    """Tests for L5 Governance output constraints."""
    
    def test_must_be_approved(self):
        """L5 output must be governance-approved."""
        output = L5Output(
            event_type="ALERT", 
            governance_approved=True,
            compliance_attestation="ST-CSF-PASS"
        )
        assert output.governance_approved
    
    def test_unapproved_rejected(self):
        """Unapproved output is rejected."""
        with pytest.raises(ValueError, match="must be governance-approved"):
            L5Output(event_type="ALERT", governance_approved=False)


# =============================================================================
# LAYER BOUNDARY ENFORCER TESTS
# =============================================================================

class TestLayerBoundaryEnforcer:
    """Tests for runtime layer boundary enforcement."""
    
    def test_forward_flow_allowed(self):
        """Forward flow L3 → L4 is allowed."""
        enforcer = LayerBoundaryEnforcer()
        result = enforcer.validate_transition(
            Layer.L3_EDGE, Layer.L4_INFERENCE, {"skeleton"}
        )
        assert result is True
    
    def test_backward_flow_blocked(self):
        """Backward flow L4 → L3 is blocked."""
        enforcer = LayerBoundaryEnforcer()
        with pytest.raises(LayerBoundaryViolation, match="Backward flow"):
            enforcer.validate_transition(
                Layer.L4_INFERENCE, Layer.L3_EDGE, {"data"}
            )
    
    def test_layer_bypass_blocked(self):
        """Layer bypass L3 → L5 is blocked."""
        enforcer = LayerBoundaryEnforcer()
        with pytest.raises(LayerBoundaryViolation, match="bypass"):
            enforcer.validate_transition(
                Layer.L3_EDGE, Layer.L5_GOVERNANCE, {"skeleton"}
            )
    
    def test_l5_to_l7_allowed(self):
        """L5 → L7 is explicitly allowed."""
        enforcer = LayerBoundaryEnforcer()
        result = enforcer.validate_transition(
            Layer.L5_GOVERNANCE, Layer.L7_EPHEMERAL, {"approved_event"}
        )
        assert result is True
    
    def test_l5_to_l8_allowed(self):
        """L5 → L8 is explicitly allowed."""
        enforcer = LayerBoundaryEnforcer()
        result = enforcer.validate_transition(
            Layer.L5_GOVERNANCE, Layer.L8_FEDERATION, {"gradient"}
        )
        assert result is True
    
    def test_raw_frame_blocked_at_l4(self):
        """Raw frame cannot enter L4."""
        enforcer = LayerBoundaryEnforcer()
        with pytest.raises(LayerBoundaryViolation, match="Forbidden data"):
            enforcer.validate_transition(
                Layer.L3_EDGE, Layer.L4_INFERENCE, {"raw_frame"}
            )
    
    def test_embedding_blocked_at_l5(self):
        """Face embedding cannot enter L5."""
        enforcer = LayerBoundaryEnforcer()
        with pytest.raises(LayerBoundaryViolation, match="Forbidden data"):
            enforcer.validate_transition(
                Layer.L4_INFERENCE, Layer.L5_GOVERNANCE, {"face_embedding"}
            )
    
    def test_violations_logged(self):
        """Violations are logged for audit."""
        enforcer = LayerBoundaryEnforcer()
        try:
            enforcer.validate_transition(
                Layer.L4_INFERENCE, Layer.L3_EDGE, {"data"}
            )
        except LayerBoundaryViolation:
            pass
        
        violations = enforcer.get_violations()
        assert len(violations) == 1
        assert violations[0]["type"] == "BACKWARD_FLOW"
    
    def test_output_forbidden_fields(self):
        """Output cannot contain forbidden fields."""
        enforcer = LayerBoundaryEnforcer()
        with pytest.raises(LayerBoundaryViolation):
            enforcer.check_output_constraints(
                Layer.L3_EDGE, {"raw_frame", "skeleton"}
            )


# =============================================================================
# DECORATOR TESTS
# =============================================================================

class TestLayerGuardDecorator:
    """Tests for @layer_guard decorator."""
    
    def test_valid_transition(self):
        """Valid transition passes through."""
        @layer_guard(Layer.L3_EDGE, Layer.L4_INFERENCE)
        def process_skeleton(data: L3Output) -> str:
            return "processed"
        
        output = L3Output(skeleton_keypoints=(1.0, 2.0))
        result = process_skeleton(output)
        assert result == "processed"
    
    def test_invalid_backward_blocked(self):
        """Backward transition is blocked."""
        @layer_guard(Layer.L4_INFERENCE, Layer.L3_EDGE)
        def invalid_function(data):
            return "should not reach"
        
        with pytest.raises(LayerBoundaryViolation, match="Backward flow"):
            invalid_function(L4Output(event_type="TEST", is_anonymous=True))


class TestForbidUpstreamDecorator:
    """Tests for @forbid_upstream_data decorator."""
    
    def test_forbidden_kwarg_blocked(self):
        """Forbidden kwarg is blocked."""
        @forbid_upstream_data("raw_frame", "embedding")
        def process_data(**kwargs):
            return kwargs
        
        with pytest.raises(LayerBoundaryViolation, match="Forbidden data"):
            process_data(raw_frame=b"bytes")
    
    def test_allowed_kwarg_passes(self):
        """Allowed kwarg passes through."""
        @forbid_upstream_data("raw_frame", "embedding")
        def process_data(**kwargs):
            return kwargs
        
        result = process_data(skeleton=[(1, 2), (3, 4)])
        assert "skeleton" in result
    
    def test_l2_output_blocked(self):
        """L2Output (raw frame) is blocked."""
        @forbid_upstream_data("raw_frame")
        def process_data(data):
            return data
        
        l2_data = L2Output(frame_buffer=b"raw_bytes")
        with pytest.raises(LayerBoundaryViolation, match="L2Output"):
            process_data(l2_data)


class TestRequireGovernanceApproval:
    """Tests for @require_governance_approval decorator."""
    
    def test_approved_passes(self):
        """Approved L5Output passes."""
        @require_governance_approval
        def display_alert(event: L5Output):
            return "displayed"
        
        approved = L5Output(
            event_type="ALERT",
            governance_approved=True,
            compliance_attestation="PASS"
        )
        result = display_alert(approved)
        assert result == "displayed"
    
    def test_no_approval_blocked(self):
        """Function without approved L5Output is blocked."""
        @require_governance_approval
        def display_alert(data: dict):
            return "displayed"
        
        with pytest.raises(LayerBoundaryViolation, match="governance approval"):
            display_alert({"event": "test"})


# =============================================================================
# FORBIDDEN DATA PATTERNS TESTS
# =============================================================================

class TestForbiddenPatterns:
    """Tests for forbidden data pattern definitions."""
    
    def test_l3_forbids_raw_frame(self):
        """L3 forbids raw_frame output."""
        assert "raw_frame" in FORBIDDEN_OUTPUTS[Layer.L3_EDGE]
    
    def test_l3_forbids_embedding(self):
        """L3 forbids embedding output."""
        assert "embedding" in FORBIDDEN_OUTPUTS[Layer.L3_EDGE]
    
    def test_l4_forbids_biometric_vector(self):
        """L4 forbids biometric_vector output."""
        assert "biometric_vector" in FORBIDDEN_OUTPUTS[Layer.L4_INFERENCE]
    
    def test_l8_forbids_raw_data(self):
        """L8 forbids raw_data output."""
        assert "raw_data" in FORBIDDEN_OUTPUTS[Layer.L8_FEDERATION]
    
    def test_upstream_l4_forbids_raw_frame(self):
        """L4 upstream forbids raw_frame."""
        assert "raw_frame" in UPSTREAM_FORBIDDEN[Layer.L4_INFERENCE]
    
    def test_upstream_l6_forbids_embedding(self):
        """L6 upstream forbids embedding."""
        assert "embedding" in UPSTREAM_FORBIDDEN[Layer.L6_HUMAN_INTERFACE]
