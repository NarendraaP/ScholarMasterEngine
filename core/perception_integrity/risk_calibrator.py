"""
Risk Calibrator Module
======================
Fuses uncertainty, disagreement, and consistency into a calibrated risk score
using calibrated temperature scaling.
"""

import numpy as np
from typing import Dict, Any
from .contracts import IntegrityMetrics


class RiskCalibrator:
    """
    Fuses raw perception metrics into a normalized, calibrated risk score [0.0, 1.0].
    """

    def __init__(
        self,
        w_epistemic: float = 0.35,
        w_aleatoric: float = 0.20,
        w_disagreement: float = 0.25,
        w_inconsistency: float = 0.20,
        temperature: float = 0.5,
        bias_offset: float = 0.30,
    ):
        self.w_epistemic = w_epistemic
        self.w_aleatoric = w_aleatoric
        self.w_disagreement = w_disagreement
        self.w_inconsistency = w_inconsistency
        self.temperature = max(1e-3, temperature)
        self.bias_offset = bias_offset

    def calibrate(
        self,
        epistemic: float,
        aleatoric: float,
        disagreement: float,
        consistency: float,
    ) -> float:
        """
        Calculates calibrated risk score in [0.0, 1.0].
        
        Args:
            epistemic: Epistemic uncertainty [0, 1]
            aleatoric: Aleatoric uncertainty [0, 1]
            disagreement: Disagreement score [0, 1]
            consistency: Cross-modal consistency [0, 1] (1 = perfect)
            
        Returns:
            Calibrated risk score in [0.0, 1.0]
        """
        inconsistency = 1.0 - np.clip(consistency, 0.0, 1.0)

        # Weighted linear combination
        raw_risk = (
            self.w_epistemic * np.clip(epistemic, 0.0, 1.0)
            + self.w_aleatoric * np.clip(aleatoric, 0.0, 1.0)
            + self.w_disagreement * np.clip(disagreement, 0.0, 1.0)
            + self.w_inconsistency * inconsistency
        )

        # Temperature-scaled Sigmoidal Calibration around bias offset
        scaled = (raw_risk - self.bias_offset) / self.temperature
        calibrated_risk = 1.0 / (1.0 + np.exp(-scaled))

        return float(np.clip(calibrated_risk, 0.0, 1.0))

    def calibrate_metrics(self, metrics: IntegrityMetrics) -> IntegrityMetrics:
        """
        Updates IntegrityMetrics in-place with calibrated risk score.
        """
        metrics.calibrated_risk = self.calibrate(
            epistemic=metrics.epistemic_uncertainty,
            aleatoric=metrics.aleatoric_uncertainty,
            disagreement=metrics.disagreement_score,
            consistency=metrics.cross_modal_consistency,
        )
        return metrics
