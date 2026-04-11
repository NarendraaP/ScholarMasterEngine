"""
Cross-Paper Domain Events
==========================
Additional domain events for cross-paper communication.

These extend the base domain_events.py with events that flow
between paper boundaries (P8↔P13↔P15).

INVARIANT: All events must be serializable and contain
NO raw biometric data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class DomainEvent:
    """Base class for domain events."""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# =============================================================================
# FEDERATED LEARNING EVENTS (Papers 12-14)
# =============================================================================

@dataclass
class FLGradientReadyEvent(DomainEvent):
    """
    Local gradient computation complete, ready for aggregation.
    
    Triggered by: Local FL trainer after processing batch
    Consumed by: FL aggregator (P14 cross-campus sync)
    """
    node_id: str                    # Local node identifier
    gradient_hash: str              # SHA-256 of compressed gradient
    batch_size: int                 # Number of samples in batch
    privacy_budget_used: float      # Epsilon consumed this round
    timestamp: datetime = None


@dataclass
class ModelDriftDetectedEvent(DomainEvent):
    """
    Significant model drift detected, retraining may be needed.
    
    Triggered by: Drift detector in P13
    Consumed by: P8 (audit), P15 (AR alert)
    """
    drift_score: float              # KL divergence or similar metric
    drift_type: str                 # "temporal", "distribution", "concept"
    affected_classes: List[str]     # Which output classes affected
    recommended_action: str         # "retrain", "alert", "monitor"
    timestamp: datetime = None


@dataclass  
class PrivacyBudgetExceededEvent(DomainEvent):
    """
    Privacy budget (epsilon) exhausted, FL must pause.
    
    Triggered by: Privacy accountant in P13
    Consumed by: P8 (audit), P15 (critical alert)
    
    CRITICAL: This event MUST stop further FL updates.
    """
    current_epsilon: float          # Current cumulative epsilon
    max_epsilon: float              # Configured limit
    rounds_completed: int           # How many FL rounds finished
    timestamp: datetime = None


@dataclass
class ModelUpdateEvent(DomainEvent):
    """
    New aggregated model available from FL.
    
    Triggered by: FL aggregator after successful round
    Consumed by: Local nodes, P8 (audit)
    """
    model_version: str              # Semantic version
    model_hash: str                 # SHA-256 of model weights
    participating_nodes: int        # How many nodes contributed
    aggregation_method: str         # "fedavg", "fedprox", etc.
    timestamp: datetime = None


# =============================================================================
# GOVERNANCE EVENTS (Papers 7-11)
# =============================================================================

@dataclass
class AuditLoggedEvent(DomainEvent):
    """
    Event logged to blockchain audit trail.
    
    Triggered by: TrustLogger after successful append
    Consumed by: P15 (AR dashboard update)
    """
    log_hash: str                   # Merkle root/event hash
    original_event_type: str        # What event was logged
    chain_length: int               # Current audit chain length
    timestamp: datetime = None


@dataclass
class CryptoShredExecutedEvent(DomainEvent):
    """
    Cryptographic shredding executed for GDPR compliance.
    
    Triggered by: KeyManagementService.crypto_shred()
    Consumed by: P8 (audit), P16 (trust signal - agency)
    
    NOTE: This is a POSITIVE trust signal for Paper 16.
    """
    subject_id_hash: str            # Hashed ID (not actual ID)
    keys_destroyed: int             # Number of keys shredded
    data_categories: List[str]      # ["attendance", "pose", etc.]
    timestamp: datetime = None


@dataclass
class PrivacyLEDStateEvent(DomainEvent):
    """
    Privacy LED state changed.
    
    Triggered by: GPIO controller or simulation
    Consumed by: P16 (ambient trust measurement)
    """
    zone_id: str
    led_color: str                  # "red", "green", "off"
    previous_color: str
    camera_active: bool
    timestamp: datetime = None


# =============================================================================
# PRESENTATION EVENTS (Paper 15)
# =============================================================================

@dataclass
class ARAlertRenderedEvent(DomainEvent):
    """
    AR alert was rendered to operator display.
    
    Triggered by: AR client after successful render
    Consumed by: P16 (response time measurement)
    """
    alert_id: str
    render_latency_ms: float        # Time from event to render
    lod_level: int                  # Level of detail used
    timestamp: datetime = None


@dataclass
class OperatorAcknowledgedEvent(DomainEvent):
    """
    Operator acknowledged an AR alert.
    
    Triggered by: Operator interaction
    Consumed by: P8 (audit), P16 (agency measurement)
    """
    alert_id: str
    acknowledgment_latency_ms: float  # Time from render to ack
    action_taken: str               # "dismiss", "investigate", "escalate"
    timestamp: datetime = None


# =============================================================================
# SYSTEM INTEGRATION EVENTS
# =============================================================================

@dataclass
class SystemHealthEvent(DomainEvent):
    """
    Periodic system health check.
    
    Consumed by: All layers for self-monitoring
    """
    component: str                  # "sensing", "governance", "FL", "AR"
    status: str                     # "healthy", "degraded", "critical"
    metrics: Dict[str, float]       # CPU, memory, latency, etc.
    timestamp: datetime = None


@dataclass
class VisiblePrivacyArtifactEvent(DomainEvent):
    """
    A visible privacy artifact was displayed to user.
    
    This is the KEY event for Paper 16's sociological analysis.
    
    Triggered by: Any system showing privacy-preserving view
    Consumed by: Paper 16 (trust measurement)
    """
    artifact_type: str              # "skeleton_view", "audit_dashboard", "led"
    zone_id: str
    exposure_duration_ms: float     # How long artifact was visible
    user_interaction: bool          # Did user interact with it?
    timestamp: datetime = None


# =============================================================================
# EVENT TYPE REGISTRY
# =============================================================================

# All cross-paper events for easy discovery
CROSS_PAPER_EVENTS = [
    FLGradientReadyEvent,
    ModelDriftDetectedEvent,
    PrivacyBudgetExceededEvent,
    ModelUpdateEvent,
    AuditLoggedEvent,
    CryptoShredExecutedEvent,
    PrivacyLEDStateEvent,
    ARAlertRenderedEvent,
    OperatorAcknowledgedEvent,
    SystemHealthEvent,
    VisiblePrivacyArtifactEvent,
]
