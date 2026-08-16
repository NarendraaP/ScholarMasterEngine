"""
Consistency Checker Module
==========================
Evaluates cross-modal consistency across visual, acoustic, pose, and spatial signals.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from .contracts import SensorInputPacket


class ConsistencyChecker:
    """
    Evaluates cross-modal consistency score in [0.0, 1.0].
    Higher score indicates higher cross-modal agreement.
    """

    def __init__(self, max_timestamp_skew_sec: float = 1.0):
        self.max_timestamp_skew_sec = max_timestamp_skew_sec

    def check(self, input_packet: SensorInputPacket) -> float:
        """
        Computes consistency score in [0.0, 1.0].
        1.0 = Perfect cross-modal agreement
        0.0 = Complete contradiction / anomaly
        """
        scores = []

        # 1. Timestamp skew check
        now = time.time()
        skew = abs(now - input_packet.timestamp)
        if skew > self.max_timestamp_skew_sec:
            skew_score = max(0.0, 1.0 - (skew / (self.max_timestamp_skew_sec * 5.0)))
            scores.append(skew_score)
        else:
            scores.append(1.0)

        # 2. Audio-Visual Activity Consistency
        # High audio level (> 85dB) but 0 pose keypoints and 0 faces -> anomaly / skew
        audio_db = input_packet.audio_db
        has_visuals = (input_packet.frame is not None and input_packet.frame.size > 0) or len(input_packet.keypoints) > 0

        if audio_db > 85.0 and not has_visuals:
            scores.append(0.1)  # Audio anomaly without visual presence
        elif audio_db < 30.0 and len(input_packet.keypoints) > 5:
            # Active classroom/people but near zero audio (mic muted or disconnected)
            scores.append(0.5)
        else:
            scores.append(1.0)

        # 3. Spatial Zone Sanity Check
        zone = input_packet.zone_id
        if not zone or not isinstance(zone, str):
            scores.append(0.5)
        else:
            scores.append(1.0)

        if not scores:
            return 1.0

        min_score = min(scores)
        mean_score = float(np.mean(scores))
        # Combine min and mean so a single severe anomaly meaningfully lowers consistency
        final_consistency = 0.5 * min_score + 0.5 * mean_score
        return float(np.clip(final_consistency, 0.0, 1.0))
