"""
Five-Regime Benchmark Suite Module
==================================
Evaluates system behavior under 5 operational regimes:
Regime 1: Clean ID Control
Regime 2: Benign OOD / Environmental Shift
Regime 3: Physical Sensor Degradation
Regime 4: Targeted Physical / Adversarial Perturbation
Regime 5: Combined Adversarial + Environmental Degradation
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

from core.perception_integrity import (
    PerceptionIntegrityGate,
    CascadeDecision,
)
from benchmarks.trust_metrics import compute_auroc_fpr95, compute_ece, compute_brier_score


class FiveRegimeEvaluator:
    """
    Executes the 5-regime benchmark suite on Perception Integrity Gate.
    """

    def __init__(self, gate: PerceptionIntegrityGate):
        self.gate = gate

    def generate_synthetic_frame(self, regime_id: int) -> Tuple[np.ndarray, float, List[np.ndarray], bool]:
        """
        Generates frame, audio_db, keypoints, and ground-truth anomaly label for regime.
        
        Returns:
            (frame, audio_db, keypoints, is_anomalous)
        """
        base = np.full((480, 640, 3), 128, dtype=np.uint8)

        if regime_id == 1:
            # Regime 1: Clean ID Control
            frame = base
            audio_db = 55.0
            keypoints = [np.zeros((17, 3))]
            is_anomalous = False

        elif regime_id == 2:
            # Regime 2: Benign OOD / Low Light & Blur
            frame = (base * 0.15).astype(np.uint8)  # Low illumination (<20 intensity)
            audio_db = 45.0
            keypoints = [np.zeros((17, 3))]
            is_anomalous = True

        elif regime_id == 3:
            # Regime 3: Physical Sensor Degradation / Heavy Gaussian Noise
            noise = np.random.normal(0, 45, base.shape).astype(np.int16)
            frame = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            audio_db = 60.0
            keypoints = []
            is_anomalous = True

        elif regime_id == 4:
            # Regime 4: Targeted Adversarial Patch Simulation
            frame = base.copy()
            # Draw synthetic adversarial patch in top-left region
            cv2.rectangle(frame, (20, 20), (120, 120), (255, 0, 255), -1)
            cv2.putText(frame, "ADV_PATCH", (25, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            audio_db = 50.0
            keypoints = [np.zeros((17, 3))]
            is_anomalous = True

        else:
            # Regime 5: Combined Adversarial + Environmental Degradation
            frame = (base * 0.2).astype(np.uint8)
            noise = np.random.normal(0, 30, base.shape).astype(np.int16)
            frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            cv2.rectangle(frame, (20, 20), (120, 120), (255, 0, 255), -1)
            audio_db = 95.0  # Mismatched scream audio
            keypoints = []
            is_anomalous = True

        return frame, audio_db, keypoints, is_anomalous

    def evaluate_regime(self, regime_id: int, num_samples: int = 200) -> Dict[str, Any]:
        """
        Runs evaluation for a specific regime.
        """
        regime_names = {
            1: "Regime 1: Clean ID Control",
            2: "Regime 2: Benign OOD / Environmental Shift",
            3: "Regime 3: Physical Sensor Degradation",
            4: "Regime 4: Targeted Adversarial Perturbation",
            5: "Regime 5: Combined Adversarial + Environmental",
        }
        name = regime_names.get(regime_id, f"Regime {regime_id}")

        latencies = []
        risks = []
        labels = []
        decisions = {d: 0 for d in CascadeDecision}

        for _ in range(num_samples):
            frame, audio_db, kps, is_anomalous = self.generate_synthetic_frame(regime_id)

            t0 = time.perf_counter()
            packet = self.gate.process_frame(
                frame=frame,
                audio_db=audio_db,
                keypoints=kps,
                zone_id="Regime_Zone",
            )
            t1 = time.perf_counter()

            latencies.append((t1 - t0) * 1000.0)
            risks.append(packet.metrics.calibrated_risk)
            labels.append(1 if is_anomalous else 0)
            decisions[packet.decision] += 1

        risks_arr = np.array(risks)
        labels_arr = np.array(labels)

        mean_lat = float(np.mean(latencies))
        p95_lat = float(np.percentile(latencies, 95))
        p99_lat = float(np.percentile(latencies, 99))
        accept_rate = float(decisions[CascadeDecision.ACCEPT] / num_samples)
        degrade_rate = float(decisions[CascadeDecision.DEGRADE] / num_samples)
        halt_rate = float(decisions[CascadeDecision.HALT] / num_samples)

        ece = compute_ece(risks_arr, labels_arr)
        brier = compute_brier_score(risks_arr, labels_arr)

        res = {
            "regime_id": regime_id,
            "regime_name": name,
            "num_samples": num_samples,
            "mean_latency_ms": round(mean_lat, 3),
            "p95_latency_ms": round(p95_lat, 3),
            "p99_latency_ms": round(p99_lat, 3),
            "accept_rate": round(accept_rate, 4),
            "degrade_rate": round(degrade_rate, 4),
            "halt_rate": round(halt_rate, 4),
            "mean_risk": round(float(np.mean(risks_arr)), 4),
            "ece": round(ece, 4),
            "brier_score": round(brier, 4),
        }

        print(f"[{name}] Mean Risk={res['mean_risk']:.3f} | AcceptRate={res['accept_rate']*100:.1f}% | Latency={mean_lat:.2f}ms")
        return res

    def run_all_regimes(self, samples_per_regime: int = 200) -> Dict[str, Any]:
        """
        Runs all 5 regimes and returns summary report.
        """
        print("\n" + "=" * 80)
        print("EXECUTING FIVE-REGIME BENCHMARK SUITE")
        print("=" * 80)

        regime_results = {}
        for r_id in range(1, 6):
            regime_results[f"regime_{r_id}"] = self.evaluate_regime(r_id, samples_per_regime)

        return regime_results
