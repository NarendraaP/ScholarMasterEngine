"""
Perception Integrity Gate (Master Adapter)
==========================================
Unified upstream gatekeeper facade integrating uncertainty estimation,
disagreement quantification, consistency checking, risk calibration,
and adaptive cascade routing.
"""

import time
import uuid
import numpy as np
from typing import List, Dict, Any, Optional

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


class PerceptionIntegrityGate:
    """
    Upstream gatekeeper for ScholarMaster perception pipeline.
    Ensures every downstream inference is paired with an integrity assessment.
    """

    def __init__(
        self,
        blur_threshold: float = 50.0,
        tau_accept: float = 0.45,
        tau_degrade: float = 0.70,
        tau_delegate: float = 0.85,
    ):
        self.uncertainty_estimator = UncertaintyEstimator(blur_threshold=blur_threshold)
        self.disagreement_engine = DisagreementEngine()
        self.consistency_checker = ConsistencyChecker()
        self.risk_calibrator = RiskCalibrator()
        self.adaptive_cascade = AdaptiveCascade(
            tau_accept=tau_accept,
            tau_degrade=tau_degrade,
            tau_delegate=tau_delegate,
        )

    def process(self, input_packet: SensorInputPacket) -> PerceptionPacket:
        """
        Processes sensor input packet through the 5-stage Perception Integrity pipeline.
        
        Returns:
            PerceptionPacket containing integrity metrics and routing decision.
        """
        # 1. Epistemic & Aleatoric Uncertainty Estimation
        epistemic, aleatoric = self.uncertainty_estimator.estimate(input_packet)

        # 2. Multi-Predictor / Temporal Disagreement Quantification
        disagreement = self.disagreement_engine.compute(input_packet)

        # 3. Cross-Modal Consistency Verification
        consistency = self.consistency_checker.check(input_packet)

        # 4. Calibrated Risk Fusion
        metrics = IntegrityMetrics(
            epistemic_uncertainty=epistemic,
            aleatoric_uncertainty=aleatoric,
            disagreement_score=disagreement,
            cross_modal_consistency=consistency,
        )
        self.risk_calibrator.calibrate_metrics(metrics)

        # 5. Adaptive Cascade Decision Routing
        decision = self.adaptive_cascade.route(metrics, input_packet)

        # Construct Output Packet
        packet_id = f"pi_{uuid.uuid4().hex[:12]}"
        is_valid = (decision != CascadeDecision.HALT)
        status_msg = f"Decision={decision.name}, CalibratedRisk={metrics.calibrated_risk:.3f}"

        return PerceptionPacket(
            packet_id=packet_id,
            timestamp=input_packet.timestamp,
            input_packet=input_packet,
            metrics=metrics,
            decision=decision,
            is_valid=is_valid,
            status_message=status_msg,
        )

    def process_frame(
        self,
        frame: Optional[np.ndarray] = None,
        keypoints: Optional[List[np.ndarray]] = None,
        face_confidences: Optional[List[float]] = None,
        face_embeddings: Optional[List[np.ndarray]] = None,
        audio_db: float = 0.0,
        zone_id: str = "Main Hall",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PerceptionPacket:
        """
        Convenience wrapper method for frame-by-frame pipeline processing.
        """
        input_packet = SensorInputPacket(
            timestamp=time.time(),
            frame=frame,
            audio_db=audio_db,
            keypoints=keypoints or [],
            face_embeddings=face_embeddings or [],
            face_confidences=face_confidences or [],
            zone_id=zone_id,
            metadata=metadata or {},
        )
        return self.process(input_packet)

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Returns perception integrity metrics summary for telemetry/audit.
        """
        return self.adaptive_cascade.get_statistics()
