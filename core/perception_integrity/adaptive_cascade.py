"""
Adaptive Cascade Module
======================
Determines dynamic cascade routing decisions based on calibrated risk thresholds.
"""

from typing import Dict, Any
from .contracts import CascadeDecision, IntegrityMetrics, SensorInputPacket


class AdaptiveCascade:
    """
    Evaluates calibrated risk against operational policy thresholds
    to return dynamic routing decisions: ACCEPT, DEGRADE, DELEGATE, HALT.
    """

    def __init__(
        self,
        tau_accept: float = 0.45,
        tau_degrade: float = 0.70,
        tau_delegate: float = 0.85,
    ):
        self.tau_accept = tau_accept
        self.tau_degrade = tau_degrade
        self.tau_delegate = tau_delegate

        # Routing counters
        self.counts: Dict[CascadeDecision, int] = {
            CascadeDecision.ACCEPT: 0,
            CascadeDecision.DEGRADE: 0,
            CascadeDecision.DELEGATE: 0,
            CascadeDecision.HALT: 0,
        }

    def route(self, metrics: IntegrityMetrics, packet: SensorInputPacket) -> CascadeDecision:
        """
        Determines the CascadeDecision for the input packet based on calibrated risk.
        """
        risk = metrics.calibrated_risk

        # Hard sanity check: if frame is corrupted / size == 0 when frame expected -> HALT
        if packet.frame is not None and packet.frame.size == 0:
            decision = CascadeDecision.HALT
        elif risk <= self.tau_accept:
            decision = CascadeDecision.ACCEPT
        elif risk <= self.tau_degrade:
            decision = CascadeDecision.DEGRADE
        elif risk <= self.tau_delegate:
            decision = CascadeDecision.DELEGATE
        else:
            decision = CascadeDecision.HALT

        self.counts[decision] += 1
        return decision

    def get_statistics(self) -> Dict[str, Any]:
        """
        Returns summary of cascade routing decisions.
        """
        total = sum(self.counts.values())
        return {
            "total_evaluated": total,
            "accept_count": self.counts[CascadeDecision.ACCEPT],
            "degrade_count": self.counts[CascadeDecision.DEGRADE],
            "delegate_count": self.counts[CascadeDecision.DELEGATE],
            "halt_count": self.counts[CascadeDecision.HALT],
            "degrade_rate": self.counts[CascadeDecision.DEGRADE] / total if total > 0 else 0.0,
            "halt_rate": self.counts[CascadeDecision.HALT] / total if total > 0 else 0.0,
        }
