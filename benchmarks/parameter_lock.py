"""
Parameter Lock & No-Leakage Protocol Module
============================================
Calibrates perception gate parameters, serializes artifact, computes SHA-256 hash,
and enforces parameter freeze during zero-shot Family-B evaluation.
"""

import os
import json
import hashlib
from typing import Dict, Any, Tuple
from core.perception_integrity import PerceptionIntegrityGate


class ParameterLockManager:
    """
    Manages parameter calibration, freeze, SHA-256 manifest registration,
    and zero-shot evaluation protocol enforcement.
    """

    def __init__(
        self,
        artifact_path: str = "data/calibration_artifact.json",
        manifest_path: str = "data/experiment_manifest.json",
    ):
        self.artifact_path = artifact_path
        self.manifest_path = manifest_path
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)

    def calibrate_and_lock(self, gate: PerceptionIntegrityGate) -> Tuple[Dict[str, Any], str]:
        """
        Extracts calibration parameters from gate, serializes them,
        computes SHA-256 hash, and freezes the calibration state.
        """
        params = {
            "tau_accept": gate.adaptive_cascade.tau_accept,
            "tau_degrade": gate.adaptive_cascade.tau_degrade,
            "tau_delegate": gate.adaptive_cascade.tau_delegate,
            "w_epistemic": gate.risk_calibrator.w_epistemic,
            "w_aleatoric": gate.risk_calibrator.w_aleatoric,
            "w_disagreement": gate.risk_calibrator.w_disagreement,
            "w_inconsistency": gate.risk_calibrator.w_inconsistency,
            "temperature": gate.risk_calibrator.temperature,
            "bias_offset": gate.risk_calibrator.bias_offset,
            "blur_threshold": gate.uncertainty_estimator.blur_threshold,
            "model_family_a": "YOLO-Pose + InsightFace + SpectralAudio",
            "model_family_b_zero_shot": "MediaPipe-Pose + FAISS-HNSW",
        }

        # Serialize calibration artifact deterministically
        param_json = json.dumps(params, indent=2, sort_keys=True)
        with open(self.artifact_path, "w") as f:
            f.write(param_json)

        # Calculate cryptographic SHA-256 digest
        sha256_hash = hashlib.sha256(param_json.encode("utf-8")).hexdigest()

        # Write experiment manifest
        manifest = {
            "status": "PARAMETER_LOCKED",
            "sha256_hash": sha256_hash,
            "artifact_path": self.artifact_path,
            "frozen_parameters": params,
            "protocol": "STRICT_PARAMETER_LOCK_NO_LEAKAGE",
        }
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"[PARAM_LOCK] Calibration serialized to {self.artifact_path}")
        print(f"[PARAM_LOCK] Cryptographic SHA-256 Hash: {sha256_hash}")
        print(f"[PARAM_LOCK] Parameters frozen for Zero-Shot Family-B evaluation.")

        return params, sha256_hash

    def verify_lock(self) -> bool:
        """
        Verifies that serialized calibration artifact matches manifest SHA-256 hash.
        """
        if not os.path.exists(self.artifact_path) or not os.path.exists(self.manifest_path):
            return False

        with open(self.artifact_path, "r") as f:
            artifact_content = f.read()

        with open(self.manifest_path, "r") as f:
            manifest = json.load(f)

        computed_hash = hashlib.sha256(artifact_content.encode("utf-8")).hexdigest()
        expected_hash = manifest.get("sha256_hash")

        is_valid = (computed_hash == expected_hash)
        if not is_valid:
            print(f"[PARAM_LOCK] ❌ WARNING: Parameter tampering detected! Hash mismatch.")
        else:
            print(f"[PARAM_LOCK] ✅ Lock Verified: SHA-256 hash intact ({computed_hash[:16]}...)")
        return is_valid
