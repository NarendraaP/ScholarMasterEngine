"""
Privacy Accountant for DP-FedAvg
Implements moments accountant for privacy budget tracking.

Paper 13 Contract Requirements:
- Track cumulative epsilon over FL rounds
- Validate ε=95.97 for 10 rounds (σ=0.5, q=1.0, δ=10^-5)
"""

import numpy as np
from typing import Tuple


class PrivacyAccountant:
    """
    Moments accountant for differential privacy tracking in federated learning.
    
    Based on Abadi et al. 2016 "Deep Learning with Differential Privacy"
    """
    
    def __init__(self, delta: float = 1e-5):
        """
        Initialize privacy accountant.
        
        Args:
            delta: Failure probability (default: 10^-5)
        """
        self.delta = delta
        self.epsilon_cumulative = 0.0
        self.rounds = 0
        self.history = []
    
    def compute_epsilon(self, sigma: float, q: float, T: int) -> float:
        """
        Compute privacy budget using moments accountant.
        
        Formula (from Paper 13, Equation 4):
            ε ≈ (q · T · √(2 ln(1/δ))) / σ
        
        Args:
            sigma: Noise multiplier
            q: Sampling ratio (fraction of clients per round)
            T: Number of rounds
        
        Returns:
            epsilon: Privacy budget
        """
        epsilon = (q * T * np.sqrt(2 * np.log(1 / self.delta))) / sigma
        return epsilon
    
    def update_budget(self, sigma: float, q: float = 1.0) -> float:
        """
        Update cumulative privacy budget after each round.
        
        Args:
            sigma: Noise multiplier for this round
            q: Sampling ratio (default: 1.0 = all clients)
        
        Returns:
            epsilon_cumulative: Total privacy budget consumed
        """
        self.rounds += 1
        
        # Compute epsilon for this round
        delta_epsilon = self.compute_epsilon(sigma, q, T=1)
        self.epsilon_cumulative += delta_epsilon
        
        # Record history
        self.history.append({
            'round': self.rounds,
            'sigma': sigma,
            'q': q,
            'delta_epsilon': delta_epsilon,
            'epsilon_cumulative': self.epsilon_cumulative
        })
        
        return self.epsilon_cumulative
    
    def validate_budget(self, target_epsilon: float = 95.97, tolerance: float = 1.0) -> Tuple[bool, str]:
        """
        Validate that cumulative epsilon matches Paper 13 target.
        
        Args:
            target_epsilon: Target privacy budget (default: 95.97 from Paper 13)
            tolerance: Acceptable deviation (default: ±1.0)
        
        Returns:
            (is_valid, message): Validation result and description
        """
        diff = abs(self.epsilon_cumulative - target_epsilon)
        
        if diff <= tolerance:
            return True, f"✅ Privacy budget validated: ε={self.epsilon_cumulative:.2f} (target: {target_epsilon:.2f})"
        else:
            return False, f"❌ Privacy budget mismatch: ε={self.epsilon_cumulative:.2f} (target: {target_epsilon:.2f}, diff: {diff:.2f})"
    
    def get_report(self) -> dict:
        """
        Generate privacy accounting report.
        
        Returns:
            report: Dictionary with privacy metrics
        """
        return {
            'total_rounds': self.rounds,
            'epsilon_cumulative': self.epsilon_cumulative,
            'delta': self.delta,
            'history': self.history
        }
    
    def reset(self):
        """Reset privacy accountant to initial state."""
        self.epsilon_cumulative = 0.0
        self.rounds = 0
        self.history = []


# Validation test
if __name__ == "__main__":
    print("🔐 Privacy Accountant Validation Test")
    print("=" * 50)
    
    # Paper 13 parameters: σ=0.5, q=1.0, T=10, δ=10^-5
    accountant = PrivacyAccountant(delta=1e-5)
    
    print(f"\nSimulating 10 FL rounds with σ=0.5, q=1.0...")
    for round_num in range(1, 11):
        epsilon = accountant.update_budget(sigma=0.5, q=1.0)
        print(f"  Round {round_num}: ε_cumulative = {epsilon:.2f}")
    
    # Validate against Paper 13 target
    is_valid, message = accountant.validate_budget(target_epsilon=95.97)
    print(f"\n{message}")
    
    # Generate report
    report = accountant.get_report()
    print(f"\nFinal Report:")
    print(f"  Total Rounds: {report['total_rounds']}")
    print(f"  Cumulative ε: {report['epsilon_cumulative']:.2f}")
    print(f"  Delta (δ): {report['delta']}")
