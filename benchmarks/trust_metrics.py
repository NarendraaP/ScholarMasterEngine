"""
Trustworthiness and Calibration Metrics Module
=============================================
Computes ECE (Expected Calibration Error), Brier Score, AUROC, AUPRC, FPR95,
and Selective Risk vs Coverage curves.
"""

import numpy as np
from typing import Dict, Any, List, Tuple


def compute_ece(confidences: np.ndarray, labels: np.ndarray, num_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE).
    """
    if len(confidences) == 0:
        return 0.0

    bins = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0
    total_samples = len(confidences)

    for i in range(num_bins):
        bin_lower = bins[i]
        bin_upper = bins[i + 1]

        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        bin_size = np.sum(in_bin)

        if bin_size > 0:
            bin_acc = np.mean(labels[in_bin])
            bin_conf = np.mean(confidences[in_bin])
            ece += (bin_size / total_samples) * abs(bin_acc - bin_conf)

    return float(ece)


def compute_brier_score(confidences: np.ndarray, labels: np.ndarray) -> float:
    """
    Computes Brier Score (mean squared error of probability predictions).
    """
    if len(confidences) == 0:
        return 0.0
    return float(np.mean((confidences - labels) ** 2))


def compute_auroc_fpr95(risk_scores: np.ndarray, is_anomalous: np.ndarray) -> Tuple[float, float]:
    """
    Computes AUROC and FPR95 (False Positive Rate at 95% True Positive Rate).
    
    Args:
        risk_scores: Predicted risk scores (higher = more anomalous)
        is_anomalous: Binary array (1 = anomalous/corrupted, 0 = clean)
        
    Returns:
        (auroc, fpr95)
    """
    if len(risk_scores) == 0 or len(np.unique(is_anomalous)) < 2:
        return 0.5, 0.0

    # Sort thresholds
    sorted_indices = np.argsort(risk_scores)[::-1]
    sorted_scores = risk_scores[sorted_indices]
    sorted_labels = is_anomalous[sorted_indices]

    num_positives = np.sum(is_anomalous == 1)
    num_negatives = np.sum(is_anomalous == 0)

    if num_positives == 0 or num_negatives == 0:
        return 0.5, 0.0

    tpr_list = []
    fpr_list = []

    tp = 0
    fp = 0

    for label in sorted_labels:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / num_positives)
        fpr_list.append(fp / num_negatives)

    tpr_arr = np.array(tpr_list)
    fpr_arr = np.array(fpr_list)

    # Trapezoidal rule for AUROC
    auroc = float(np.trapz(tpr_arr, fpr_arr))

    # FPR at 95% TPR
    idx_95 = np.searchsorted(tpr_arr, 0.95)
    fpr95 = float(fpr_arr[idx_95]) if idx_95 < len(fpr_arr) else 1.0

    return float(np.clip(auroc, 0.0, 1.0)), float(np.clip(fpr95, 0.0, 1.0))


def compute_selective_risk_coverage(
    risk_scores: np.ndarray,
    task_errors: np.ndarray,
    steps: int = 10
) -> List[Dict[str, float]]:
    """
    Computes Task Error as coverage varies from 100% to 10%.
    """
    if len(risk_scores) == 0:
        return []

    sorted_idx = np.argsort(risk_scores)  # Lowest risk first
    sorted_errors = task_errors[sorted_idx]
    n = len(risk_scores)

    results = []
    coverages = np.linspace(1.0, 0.1, steps)

    for cov in coverages:
        k = max(1, int(cov * n))
        accepted_errors = sorted_errors[:k]
        selective_risk = float(np.mean(accepted_errors))
        results.append({
            "coverage": float(round(cov, 2)),
            "accepted_count": k,
            "selective_risk": float(round(selective_risk, 4)),
        })

    return results
