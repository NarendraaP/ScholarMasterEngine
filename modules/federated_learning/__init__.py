"""
Federated Learning Module for Paper 13
Privacy-Preserving Model Drift Compensation

This module implements DP-FedAvg with:
- Gradient clipping (C=1.0)
- Gaussian noise injection (σ=0.5)
- Moments accountant privacy tracking
"""

__all__ = [
    'DPFedAvgTrainer',
    'PrivacyAccountant',
    'DriftSimulator',
    'ActiveLearningSelector',
    'MQTTGradientBuffer',
    'FlashAwareCheckpointer'
]

