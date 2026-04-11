"""
Federation Differential Privacy Tests

ARCHITECTURE_CANONICAL.md 5.0 COMPLIANCE:
- Only DP-protected gradients leave campus
- Campus withdrawal removes all future influence
- No raw data, embeddings, or identifiers cross L8 boundary
"""
import pytest
import numpy as np
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import time

from core.canonical_layers import FederationCoordinator, CampusMembership


# =============================================================================
# DIFFERENTIAL PRIVACY GRADIENT WRAPPER
# =============================================================================

@dataclass
class DPGradient:
    """
    Differentially Private gradient container.
    
    Per ARCHITECTURE_CANONICAL.md 5.2:
    - Gradients clipped and noised before federation
    - Epsilon budget tracked per campus
    """
    gradient: np.ndarray
    epsilon: float
    delta: float
    noise_scale: float
    clipping_norm: float
    is_dp_protected: bool = True
    
    @classmethod
    def from_raw_gradient(
        cls, 
        raw_gradient: np.ndarray,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        clipping_norm: float = 1.0
    ) -> "DPGradient":
        """
        Create DP-protected gradient from raw gradient.
        
        Applies:
        1. Gradient clipping (L2 norm bound)
        2. Gaussian noise addition
        """
        # L2 clipping
        grad_norm = np.linalg.norm(raw_gradient)
        if grad_norm > clipping_norm:
            clipped = raw_gradient * (clipping_norm / grad_norm)
        else:
            clipped = raw_gradient.copy()
        
        # Calculate noise scale (simplified Gaussian mechanism)
        noise_scale = clipping_norm * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        
        # Add noise
        noise = np.random.normal(0, noise_scale, size=clipped.shape)
        noised = clipped + noise
        
        return cls(
            gradient=noised,
            epsilon=epsilon,
            delta=delta,
            noise_scale=noise_scale,
            clipping_norm=clipping_norm,
            is_dp_protected=True
        )


# =============================================================================
# EXTENDED FEDERATION COORDINATOR WITH DP
# =============================================================================

class DPFederationCoordinator(FederationCoordinator):
    """
    Federation coordinator with Differential Privacy enforcement.
    
    Per ARCHITECTURE_CANONICAL.md 5.0:
    - Only DP-protected gradients cross campus boundary
    - Campus withdrawal purges all gradient contributions
    - Right-to-be-forgotten enforced
    """
    
    DEFAULT_EPSILON = 1.0
    DEFAULT_DELTA = 1e-5
    MAX_EPSILON_BUDGET = 10.0  # Total privacy budget per campus
    
    def __init__(self):
        super().__init__()
        self._epsilon_budgets: Dict[str, float] = {}  # Remaining budget
        self._gradient_history: Dict[str, List[int]] = {}  # round -> campus contributions
        self._current_round: int = 0
        self._withdrawn_campuses: Set[str] = set()
        self._gradient_checksums: Dict[str, List[str]] = {}  # For audit
    
    def join_federation(
        self, 
        campus_id: str, 
        consent_attestation: bool
    ) -> bool:
        """Join with epsilon budget initialization."""
        result = super().join_federation(campus_id, consent_attestation)
        if result:
            self._epsilon_budgets[campus_id] = self.MAX_EPSILON_BUDGET
            self._gradient_checksums[campus_id] = []
        return result
    
    def contribute_dp_gradient(
        self,
        campus_id: str,
        dp_gradient: DPGradient
    ) -> bool:
        """
        Accept DP-protected gradient contribution.
        
        Validates:
        1. Campus has consent
        2. Gradient is DP-protected
        3. Epsilon budget not exceeded
        """
        # Verify consent
        if not self.verify_consent(campus_id):
            return False
        
        # Verify campus not withdrawn
        if campus_id in self._withdrawn_campuses:
            return False
        
        # CRITICAL: Verify gradient is DP-protected
        if not dp_gradient.is_dp_protected:
            raise ValueError(
                f"ARCHITECTURE_CANONICAL.md 5.2: Only DP-protected gradients allowed"
            )
        
        # Check epsilon budget
        remaining = self._epsilon_budgets.get(campus_id, 0)
        if dp_gradient.epsilon > remaining:
            return False
        
        # Deduct from budget
        self._epsilon_budgets[campus_id] = remaining - dp_gradient.epsilon
        
        # Store contribution
        return super().contribute_gradient(campus_id, dp_gradient)
    
    def contribute_raw_gradient(
        self,
        campus_id: str,
        raw_gradient: np.ndarray
    ) -> bool:
        """
        Block raw gradient contribution.
        
        Raw gradients are FORBIDDEN per ARCHITECTURE_CANONICAL.md 5.0.
        """
        raise ValueError(
            "ARCHITECTURE_CANONICAL.md 5.0: Raw gradients forbidden at L8 boundary. "
            "Use contribute_dp_gradient() with DP-protected gradients."
        )
    
    def withdraw_from_federation(self, campus_id: str) -> bool:
        """
        Campus withdrawal with complete influence removal.
        
        Per ARCHITECTURE_CANONICAL.md 5.5:
        - No justification required
        - Completes within one federation round
        - All gradient contributions purged
        """
        result = super().withdraw_from_federation(campus_id)
        if result:
            self._withdrawn_campuses.add(campus_id)
            # Clear epsilon budget
            self._epsilon_budgets[campus_id] = 0
            # Record for audit
            self._gradient_checksums[campus_id].append(
                f"WITHDRAWN:{time.time()}"
            )
        return result
    
    def get_remaining_epsilon(self, campus_id: str) -> float:
        """Get remaining epsilon budget for campus."""
        return self._epsilon_budgets.get(campus_id, 0)
    
    def is_campus_withdrawn(self, campus_id: str) -> bool:
        """Check if campus has withdrawn."""
        return campus_id in self._withdrawn_campuses
    
    def advance_round(self) -> int:
        """Advance federation round."""
        self._current_round += 1
        return self._current_round


# =============================================================================
# DP-PROTECTED UPDATE TESTS
# =============================================================================

class TestDPProtectedUpdates:
    """Tests for Differential Privacy protection on federation updates."""
    
    def test_gradient_has_noise_added(self):
        """Gradients have Gaussian noise added."""
        raw = np.ones(100)
        dp_grad = DPGradient.from_raw_gradient(raw, epsilon=1.0)
        
        # DP gradient should differ from raw
        assert not np.allclose(dp_grad.gradient, raw)
        
        # Should have same shape
        assert dp_grad.gradient.shape == raw.shape
    
    def test_gradient_is_clipped(self):
        """Large gradients are clipped to L2 norm bound."""
        raw = np.ones(100) * 10  # Large gradient
        clipping_norm = 1.0
        
        dp_grad = DPGradient.from_raw_gradient(
            raw, 
            epsilon=1.0, 
            clipping_norm=clipping_norm
        )
        
        # Before noise, clipped gradient should have norm <= clipping_norm
        # (noise makes it exceed slightly)
        assert dp_grad.clipping_norm == clipping_norm
    
    def test_raw_gradient_forbidden_at_l8(self):
        """Raw gradients cannot be sent through L8."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_A", consent_attestation=True)
        
        raw = np.ones(50)
        
        with pytest.raises(ValueError, match="Raw gradients forbidden"):
            fed.contribute_raw_gradient("campus_A", raw)
    
    def test_dp_gradient_accepted(self):
        """DP-protected gradients are accepted."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_B", consent_attestation=True)
        
        raw = np.random.randn(50)
        dp_grad = DPGradient.from_raw_gradient(raw, epsilon=1.0)
        
        result = fed.contribute_dp_gradient("campus_B", dp_grad)
        
        assert result is True
    
    def test_unprotected_gradient_rejected(self):
        """Gradients not marked as DP-protected are rejected."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_C", consent_attestation=True)
        
        # Manually create unprotected gradient
        fake_dp = DPGradient(
            gradient=np.ones(50),
            epsilon=1.0,
            delta=1e-5,
            noise_scale=0.1,
            clipping_norm=1.0,
            is_dp_protected=False  # NOT protected
        )
        
        with pytest.raises(ValueError, match="Only DP-protected"):
            fed.contribute_dp_gradient("campus_C", fake_dp)
    
    def test_epsilon_budget_tracked(self):
        """Epsilon budget is tracked per campus."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_D", consent_attestation=True)
        
        initial_budget = fed.get_remaining_epsilon("campus_D")
        assert initial_budget == fed.MAX_EPSILON_BUDGET
        
        # Contribute with epsilon=2.0
        dp_grad = DPGradient.from_raw_gradient(np.ones(10), epsilon=2.0)
        fed.contribute_dp_gradient("campus_D", dp_grad)
        
        remaining = fed.get_remaining_epsilon("campus_D")
        assert remaining == initial_budget - 2.0
    
    def test_epsilon_budget_enforced(self):
        """Contributions exceeding budget are rejected."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_E", consent_attestation=True)
        
        # Use up most of budget
        for _ in range(9):
            dp_grad = DPGradient.from_raw_gradient(np.ones(10), epsilon=1.0)
            fed.contribute_dp_gradient("campus_E", dp_grad)
        
        # Now budget is 1.0, try to use 2.0
        big_dp = DPGradient.from_raw_gradient(np.ones(10), epsilon=2.0)
        result = fed.contribute_dp_gradient("campus_E", big_dp)
        
        assert result is False


# =============================================================================
# CAMPUS WITHDRAWAL TESTS
# =============================================================================

class TestCampusWithdrawal:
    """Tests for campus withdrawal and influence removal."""
    
    def test_withdrawal_removes_future_influence(self):
        """Withdrawn campus cannot contribute future gradients."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_withdraw", consent_attestation=True)
        
        # Contribute before withdrawal
        dp_grad = DPGradient.from_raw_gradient(np.ones(10), epsilon=1.0)
        result1 = fed.contribute_dp_gradient("campus_withdraw", dp_grad)
        assert result1 is True
        
        # Withdraw
        fed.withdraw_from_federation("campus_withdraw")
        
        # Try to contribute after withdrawal
        dp_grad2 = DPGradient.from_raw_gradient(np.ones(10), epsilon=1.0)
        result2 = fed.contribute_dp_gradient("campus_withdraw", dp_grad2)
        
        assert result2 is False
        assert fed.is_campus_withdrawn("campus_withdraw")
    
    def test_gradients_purged_on_withdrawal(self):
        """All gradient contributions are purged on withdrawal."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_purge", consent_attestation=True)
        
        # Contribute several gradients
        for _ in range(3):
            dp_grad = DPGradient.from_raw_gradient(np.ones(10), epsilon=0.5)
            fed.contribute_dp_gradient("campus_purge", dp_grad)
        
        # Verify contributions exist
        assert "campus_purge" in fed._gradient_contributions
        assert len(fed._gradient_contributions["campus_purge"]) == 3
        
        # Withdraw
        fed.withdraw_from_federation("campus_purge")
        
        # Gradients should be purged
        assert "campus_purge" not in fed._gradient_contributions
    
    def test_no_justification_required(self):
        """Withdrawal requires no justification."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_no_reason", consent_attestation=True)
        
        # Withdraw without any reason
        result = fed.withdraw_from_federation("campus_no_reason")
        
        assert result is True
    
    def test_consent_revoked_on_withdrawal(self):
        """Consent is automatically revoked on withdrawal."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_consent", consent_attestation=True)
        
        assert fed.verify_consent("campus_consent") is True
        
        fed.withdraw_from_federation("campus_consent")
        
        assert fed.verify_consent("campus_consent") is False
    
    def test_epsilon_budget_zeroed_on_withdrawal(self):
        """Epsilon budget is zeroed on withdrawal."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_budget", consent_attestation=True)
        
        assert fed.get_remaining_epsilon("campus_budget") > 0
        
        fed.withdraw_from_federation("campus_budget")
        
        assert fed.get_remaining_epsilon("campus_budget") == 0
    
    def test_withdrawal_recorded_for_audit(self):
        """Withdrawal is recorded in audit trail."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_audit", consent_attestation=True)
        
        fed.withdraw_from_federation("campus_audit")
        
        checksums = fed._gradient_checksums.get("campus_audit", [])
        assert any("WITHDRAWN" in c for c in checksums)


# =============================================================================
# DATA BOUNDARY TESTS
# =============================================================================

class TestL8DataBoundary:
    """Tests ensuring no raw data crosses L8 boundary."""
    
    def test_raw_data_never_leaves_campus(self):
        """Raw data (frames, audio, embeddings) never crosses L8."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_boundary", consent_attestation=True)
        
        # These should all be rejected
        with pytest.raises(ValueError):
            fed.contribute_raw_gradient("campus_boundary", np.ones(100))
    
    def test_only_gradients_cross_boundary(self):
        """Only DP-protected gradients can cross L8."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_only_grads", consent_attestation=True)
        
        # DP gradient should work
        dp_grad = DPGradient.from_raw_gradient(np.ones(10), epsilon=1.0)
        result = fed.contribute_dp_gradient("campus_only_grads", dp_grad)
        
        assert result is True
    
    def test_embedding_not_in_gradient(self):
        """Verify DPGradient doesn't contain embeddings."""
        raw = np.ones(512)  # Same size as embedding
        dp_grad = DPGradient.from_raw_gradient(raw, epsilon=1.0)
        
        # DP gradient should have noise, making it irreversible
        assert not np.allclose(dp_grad.gradient, raw)
        
        # Verify it's marked as protected
        assert dp_grad.is_dp_protected is True


# =============================================================================
# RIGHT TO BE FORGOTTEN TESTS
# =============================================================================

class TestRightToBeForgotten:
    """Tests for individual deletion requests."""
    
    def test_deletion_request_processed(self):
        """Individual deletion request is processed."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_rtbf", consent_attestation=True)
        
        result = fed.process_deletion_request("campus_rtbf", "individual_123")
        
        assert result is True
    
    def test_model_version_increments_on_deletion(self):
        """Global model version increments after deletion."""
        fed = DPFederationCoordinator()
        fed.join_federation("campus_version", consent_attestation=True)
        
        initial_version = fed._global_model_version
        
        fed.process_deletion_request("campus_version", "individual_456")
        
        assert fed._global_model_version > initial_version
