"""
Uncertainty Estimator Module
============================
Estimates epistemic and aleatoric uncertainty from multi-modal sensor streams
and model outputs without fabricating missing modalities.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
from .contracts import SensorInputPacket


class UncertaintyEstimator:
    """
    Estimates epistemic and aleatoric uncertainty for incoming sensor input.
    """

    def __init__(self, blur_threshold: float = 50.0):
        self.blur_threshold = blur_threshold

    def estimate(self, input_packet: SensorInputPacket) -> Tuple[float, float]:
        """
        Computes (epistemic_uncertainty, aleatoric_uncertainty) for input packet.
        
        Returns:
            Tuple[float, float] bounded in [0.0, 1.0]
        """
        aleatoric = self._estimate_aleatoric(input_packet)
        epistemic = self._estimate_epistemic(input_packet)

        return float(np.clip(epistemic, 0.0, 1.0)), float(np.clip(aleatoric, 0.0, 1.0))

    def _estimate_aleatoric(self, packet: SensorInputPacket) -> float:
        """
        Aleatoric uncertainty derived from physical noise/quality factors:
        - Image blur (variance of Laplacian)
        - Illumination extremes (over/under-exposure)
        - Audio clipping / low signal
        """
        noise_factors = []

        if packet.frame is not None and packet.frame.size > 0:
            # 1. Blur and Noise estimation via Laplacian variance
            try:
                gray = cv2.cvtColor(packet.frame, cv2.COLOR_BGR2GRAY) if len(packet.frame.shape) == 3 else packet.frame
                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

                if lap_var < self.blur_threshold:
                    # Blurry frame
                    blur_factor = max(0.0, 1.0 - (lap_var / self.blur_threshold))
                elif lap_var > 800.0:
                    # Heavy Gaussian / high-frequency noise
                    blur_factor = min(1.0, (lap_var - 800.0) / 1000.0)
                else:
                    # Normal texture
                    blur_factor = 0.05

                noise_factors.append(blur_factor)

                # 2. Illumination extreme check
                mean_intensity = np.mean(gray)
                if mean_intensity < 25 or mean_intensity > 230:
                    noise_factors.append(0.8)
                else:
                    noise_factors.append(0.1)
            except Exception:
                noise_factors.append(0.5)

        if packet.audio_buffer is not None and packet.audio_buffer.size > 0:
            # Audio clip check
            max_amp = np.max(np.abs(packet.audio_buffer))
            if max_amp > 0.95:  # Audio clipping
                noise_factors.append(0.7)
            elif max_amp < 0.01:  # Silent / no audio signal
                noise_factors.append(0.3)
            else:
                noise_factors.append(0.1)

        if not noise_factors:
            return 0.5  # Default baseline if no raw streams attached

        return float(np.mean(noise_factors))

    def _estimate_epistemic(self, packet: SensorInputPacket) -> float:
        """
        Epistemic uncertainty derived from model output distributions:
        - Detection confidence margin / entropy
        - Embedding dispersion
        - Modality availability gaps
        """
        if not packet.face_confidences:
            # If face confidences are absent
            if packet.frame is not None and len(packet.keypoints) > 0:
                # Keypoints present but no face detected -> mild epistemic uncertainty
                return 0.35
            elif packet.frame is not None:
                # Frame present but zero face/pose detections -> uncertainty in detection
                return 0.45
            return 0.2  # Normal default state when no frame is present

        confidences = packet.face_confidences
        max_conf = max(confidences)

        # High confidence -> low epistemic uncertainty
        # Low confidence (e.g. 0.4) -> high epistemic uncertainty (0.6)
        confidence_uncertainty = 1.0 - max_conf

        # Entropy / variance across detections if multiple faces present
        if len(confidences) > 1:
            p = np.array(confidences) / np.sum(confidences)
            entropy = -np.sum(p * np.log(p + 1e-9)) / np.log(len(confidences) + 1e-9)
            epistemic = 0.6 * confidence_uncertainty + 0.4 * float(entropy)
        else:
            epistemic = confidence_uncertainty

        return float(epistemic)
