"""
Manifest & State Machine Engine
===============================
Manages machine-readable experiment manifests, state machine transitions,
and hardware capability auditing.
"""

import os
import sys
import json
import time
import psutil
import platform
import hashlib
from typing import Dict, Any, Optional


class ExperimentStateMachine:
    """
    State machine tracking experiment lifecycle:
    PLANNED -> CONFIGURED -> CALIBRATED -> EXECUTED -> VALIDATED -> LOGGED -> COMPLETED / BLOCKED / FAILED
    """

    VALID_STATES = [
        "PLANNED",
        "CONFIGURED",
        "CALIBRATED",
        "EXECUTED",
        "VALIDATED",
        "LOGGED",
        "COMPLETED",
        "BLOCKED",
        "FAILED",
        "INVALIDATED",
    ]

    def __init__(self, experiment_id: str, paper_id: str, name: str):
        self.experiment_id = experiment_id
        self.paper_id = paper_id
        self.name = name
        self.current_state = "PLANNED"
        self.history: List[Dict[str, Any]] = []
        self._record_transition("PLANNED", "Initialization")

    def transition_to(self, new_state: str, reason: str = ""):
        if new_state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {new_state}")
        old_state = self.current_state
        self.current_state = new_state
        self._record_transition(new_state, reason)

    def _record_transition(self, state: str, reason: str):
        self.history.append({
            "state": state,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason,
        })


class HardwareAuditor:
    """
    Audits execution environment hardware capabilities.
    Enforces strict truthfulness: does NOT claim Jetson AGX Orin / CUDA if absent.
    """

    @staticmethod
    def audit() -> Dict[str, Any]:
        has_cuda = False
        has_jetson = False
        has_mps = False

        # System info
        os_info = platform.system()
        cpu_arch = platform.machine()

        # Check PyTorch / CUDA / MPS if available
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        except ImportError:
            pass

        # Check Jetson hardware markers (/etc/nv_tegra_release or jtop)
        if os.path.exists("/etc/nv_tegra_release"):
            has_jetson = True

        status_tag = "HOST_CPU_TELEMETRY_ACTIVE"
        jetson_status = "BLOCKED (Jetson AGX Orin Hardware Unavailable)" if not has_jetson else "AVAILABLE"

        return {
            "os": os_info,
            "architecture": cpu_arch,
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "cuda_available": has_cuda,
            "mps_available": has_mps,
            "jetson_agx_orin": jetson_status,
            "telemetry_status": status_tag,
        }


def generate_experiment_manifest(
    experiment_id: str,
    paper_id: str,
    experiment_name: str,
    dataset: str,
    model: str,
    parameter_hash: str,
    threshold: float,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Generates a standardized machine-readable experiment manifest.
    """
    hw_info = HardwareAuditor.audit()

    manifest = {
        "experiment_id": experiment_id,
        "paper_id": paper_id,
        "experiment_name": experiment_name,
        "dataset": dataset,
        "dataset_version": "v1.0-synthetic-canonical",
        "dataset_split": "test",
        "model": model,
        "model_version": "2.1.0",
        "model_family": "YOLO-Pose + InsightFace + PerceptionIntegrityGate",
        "calibration_state": "LOCKED",
        "parameter_hash": parameter_hash,
        "threshold": threshold,
        "random_seed": seed,
        "software_version": "Python " + platform.python_version(),
        "hardware": hw_info,
        "precision": "FP32",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return manifest
