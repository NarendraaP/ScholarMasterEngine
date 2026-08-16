"""
Perception Integrity Package
=============================
Upstream integrity gatekeeper for ScholarMaster.
Evaluates epistemic uncertainty, model disagreement, cross-modal consistency,
calibrated risk, and dynamic cascade routing decisions before downstream inference.
"""

from .contracts import (
    SensorInputPacket,
    IntegrityMetrics,
    CascadeDecision,
    PerceptionPacket,
)
from .uncertainty import UncertaintyEstimator
from .disagreement import DisagreementEngine
from .consistency import ConsistencyChecker
from .risk_calibrator import RiskCalibrator
from .adaptive_cascade import AdaptiveCascade
from .gate import PerceptionIntegrityGate

__all__ = [
    "SensorInputPacket",
    "IntegrityMetrics",
    "CascadeDecision",
    "PerceptionPacket",
    "UncertaintyEstimator",
    "DisagreementEngine",
    "ConsistencyChecker",
    "RiskCalibrator",
    "AdaptiveCascade",
    "PerceptionIntegrityGate",
]
