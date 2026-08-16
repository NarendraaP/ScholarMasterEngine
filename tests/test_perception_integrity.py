"""
Unit and Integration Tests for Perception Integrity Layer
==========================================================
Verifies uncertainty estimation, disagreement engine, consistency checker,
risk calibration, and adaptive cascade routing without breaking downstream APIs.
"""

import pytest
import numpy as np
import time

from core.perception_integrity import (
    SensorInputPacket,
    IntegrityMetrics,
    CascadeDecision,
    PerceptionPacket,
    UncertaintyEstimator,
    DisagreementEngine,
    ConsistencyChecker,
    RiskCalibrator,
    AdaptiveCascade,
    PerceptionIntegrityGate,
)


def test_sensor_input_packet_defaults():
    packet = SensorInputPacket()
    assert packet.frame is None
    assert packet.audio_db == 0.0
    assert packet.keypoints == []
    assert packet.face_embeddings == []
    assert packet.face_confidences == []


def test_uncertainty_estimator_clean_input():
    estimator = UncertaintyEstimator()
    # Create clean artificial frame (uniform texture / mild pattern)
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    packet = SensorInputPacket(
        frame=frame,
        face_confidences=[0.95],
        keypoints=[np.zeros((17, 3))],
    )

    epistemic, aleatoric = estimator.estimate(packet)
    assert 0.0 <= epistemic <= 1.0
    assert 0.0 <= aleatoric <= 1.0
    assert epistemic < 0.2  # High confidence face -> low epistemic uncertainty


def test_uncertainty_estimator_blurry_input():
    estimator = UncertaintyEstimator(blur_threshold=100.0)
    # Uniform constant frame has zero Laplacian variance (maximum blur)
    blurry_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    packet = SensorInputPacket(frame=blurry_frame)

    epistemic, aleatoric = estimator.estimate(packet)
    assert aleatoric > 0.4  # Zero Laplacian variance indicates high aleatoric uncertainty


def test_disagreement_engine():
    engine = DisagreementEngine()
    # Mismatched predictor count (1 face vs 3 pose keypoint skeletons)
    packet = SensorInputPacket(
        face_confidences=[0.9],
        keypoints=[np.zeros((17, 3)), np.zeros((17, 3)), np.zeros((17, 3))],
    )

    disagreement = engine.compute(packet)
    assert 0.0 <= disagreement <= 1.0
    assert disagreement > 0.0  # Divergence between face and pose predictors


def test_consistency_checker():
    checker = ConsistencyChecker()
    # Acoustic anomaly: high audio (90dB) with no visual presence
    packet = SensorInputPacket(
        audio_db=95.0,
        frame=None,
        keypoints=[],
    )

    consistency = checker.check(packet)
    assert 0.0 <= consistency <= 1.0
    assert consistency < 0.6  # Audio energy without visual presence is anomalous


def test_risk_calibrator():
    calibrator = RiskCalibrator()

    # Low risk inputs
    low_risk = calibrator.calibrate(
        epistemic=0.05,
        aleatoric=0.05,
        disagreement=0.0,
        consistency=1.0,
    )

    # High risk inputs
    high_risk = calibrator.calibrate(
        epistemic=0.9,
        aleatoric=0.9,
        disagreement=0.8,
        consistency=0.2,
    )

    assert 0.0 <= low_risk <= 1.0
    assert 0.0 <= high_risk <= 1.0
    assert high_risk > low_risk


def test_adaptive_cascade_decisions():
    cascade = AdaptiveCascade(
        tau_accept=0.45,
        tau_degrade=0.70,
        tau_delegate=0.85,
    )

    packet = SensorInputPacket()

    # Test ACCEPT
    metrics_accept = IntegrityMetrics(calibrated_risk=0.2)
    assert cascade.route(metrics_accept, packet) == CascadeDecision.ACCEPT

    # Test DEGRADE
    metrics_degrade = IntegrityMetrics(calibrated_risk=0.6)
    assert cascade.route(metrics_degrade, packet) == CascadeDecision.DEGRADE

    # Test DELEGATE
    metrics_delegate = IntegrityMetrics(calibrated_risk=0.8)
    assert cascade.route(metrics_delegate, packet) == CascadeDecision.DELEGATE

    # Test HALT
    metrics_halt = IntegrityMetrics(calibrated_risk=0.95)
    assert cascade.route(metrics_halt, packet) == CascadeDecision.HALT


def test_perception_integrity_gate_facade():
    gate = PerceptionIntegrityGate()

    frame = np.full((128, 128, 3), 150, dtype=np.uint8)
    result = gate.process_frame(
        frame=frame,
        keypoints=[np.zeros((17, 3))],
        face_confidences=[0.92],
        audio_db=55.0,
        zone_id="Zone_01",
    )

    assert isinstance(result, PerceptionPacket)
    assert result.decision in CascadeDecision
    assert 0.0 <= result.metrics.calibrated_risk <= 1.0
    assert result.packet_id.startswith("pi_")

    stats = gate.get_system_metrics()
    assert stats["total_evaluated"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
