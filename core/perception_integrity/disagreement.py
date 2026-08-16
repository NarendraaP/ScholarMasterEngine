"""
Disagreement Engine Module
==========================
Quantifies divergence across concurrent predictors, redundant features,
and temporal observations.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .contracts import SensorInputPacket


class DisagreementEngine:
    """
    Quantifies disagreement score across multi-modal sensor inputs and model features.
    """

    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self._confidence_history: List[float] = []

    def compute(self, input_packet: SensorInputPacket) -> float:
        """
        Computes disagreement score in [0.0, 1.0].
        
        Evaluates:
        1. Spatial/Presence predictor disagreement (Face vs. Pose keypoints)
        2. Multi-face embedding ambiguity
        3. Temporal confidence shift / volatility
        """
        disagreements = []

        # 1. Face vs. Keypoints spatial/presence disagreement
        face_count = len(input_packet.face_confidences)
        pose_count = len(input_packet.keypoints)

        if face_count > 0 and pose_count > 0:
            # Match ratio difference
            diff = abs(face_count - pose_count) / max(face_count, pose_count)
            disagreements.append(diff * 0.5)
        elif (face_count > 0 and pose_count == 0) or (face_count == 0 and pose_count > 0):
            # One sensor detects entity while other does not
            disagreements.append(0.3)
        else:
            disagreements.append(0.0)

        # 2. Embedding ambiguity across faces if multiple embeddings present
        if len(input_packet.face_embeddings) >= 2:
            try:
                embs = [e.flatten() / (np.linalg.norm(e) + 1e-9) for e in input_packet.face_embeddings]
                sims = []
                for i in range(len(embs)):
                    for j in range(i + 1, len(embs)):
                        sims.append(np.dot(embs[i], embs[j]))
                max_sim = max(sims) if sims else 0.0
                # If embeddings of two detections in same frame are very similar -> high ambiguity / overlap
                if max_sim > 0.85:
                    disagreements.append(0.6)
            except Exception:
                pass

        # 3. Temporal volatility check
        curr_conf = max(input_packet.face_confidences) if input_packet.face_confidences else 0.0
        self._confidence_history.append(curr_conf)
        if len(self._confidence_history) > self.history_size:
            self._confidence_history.pop(0)

        if len(self._confidence_history) >= 3:
            conf_std = float(np.std(self._confidence_history))
            # Sudden high variance in confidence across frames indicates disagreement/flicker
            volatility_disagreement = float(np.clip(conf_std * 2.0, 0.0, 1.0))
            disagreements.append(volatility_disagreement)

        if not disagreements:
            return 0.0

        return float(np.clip(np.mean(disagreements), 0.0, 1.0))

    def reset_history(self) -> None:
        """Clear temporal history buffer."""
        self._confidence_history.clear()
