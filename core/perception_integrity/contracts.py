"""
Perception Integrity Data Contracts
===================================
Defines canonical data structures for sensor input packets, integrity metrics,
cascade decisions, and the validated perception output packet.
"""

import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np


class CascadeDecision(Enum):
    """
    Cascade routing decisions determined by Perception Integrity layer.
    """
    ACCEPT = auto()   # Full confidence: proceed with face identity & downstream pipeline
    DEGRADE = auto()  # High uncertainty/disagreement: anonymous pose-only privacy mode
    DELEGATE = auto() # Ambiguous: request secondary verification or low-priority alert
    HALT = auto()     # Critical corruption/anomaly: halt processing for this frame


@dataclass
class SensorInputPacket:
    """
    Container for multi-modal sensor inputs arriving at the perception gate.
    """
    timestamp: float = field(default_factory=time.time)
    frame: Optional[np.ndarray] = None
    audio_buffer: Optional[np.ndarray] = None
    audio_db: float = 0.0
    keypoints: List[np.ndarray] = field(default_factory=list)
    face_embeddings: List[np.ndarray] = field(default_factory=list)
    face_confidences: List[float] = field(default_factory=list)
    zone_id: str = "Main Hall"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrityMetrics:
    """
    Integrity metrics evaluated upstream before downstream inference.
    """
    epistemic_uncertainty: float = 0.0  # [0.0, 1.0] Model knowledge uncertainty
    aleatoric_uncertainty: float = 0.0  # [0.0, 1.0] Sensor noise uncertainty
    disagreement_score: float = 0.0     # [0.0, 1.0] Multi-predictor divergence
    cross_modal_consistency: float = 1.0 # [0.0, 1.0] Agreement across modalities (1.0 = perfect)
    calibrated_risk: float = 0.0        # [0.0, 1.0] Unified calibrated risk score
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerceptionPacket:
    """
    Validated packet produced by Perception Integrity Gate.
    """
    packet_id: str
    timestamp: float
    input_packet: SensorInputPacket
    metrics: IntegrityMetrics
    decision: CascadeDecision
    is_valid: bool
    status_message: str = "OK"
