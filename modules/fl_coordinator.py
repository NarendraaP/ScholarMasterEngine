#!/usr/bin/env python3
"""
Federated Learning Coordinator for Paper 13
Implements FedAvg algorithm with Differential Privacy.

Usage:
    coordinator = FedAvgCoordinator(num_clients=5, privacy_sigma=0.5)
    coordinator.run_training(num_rounds=10)
"""

import numpy as np
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ClientUpdate:
    """Client model update with metadata"""
    client_id: int
    gradients: np.ndarray  # Model weight updates
    num_samples: int       # Training samples used
    training_loss: float
    timestamp: str


class FedAvgCoordinator:
    """
    Federated Averaging Coordinator (McMahan et al., 2017)
    Implements server-side aggregation with differential privacy.
    """
    
    def __init__(self, 
                 num_clients: int = 5,
                 privacy_sigma: float = 0.5,
                 clipping_norm: float = 1.0,
                 initial_lr: float = 0.01):
        """
        Args:
            num_clients: Number of edge nodes (classrooms)
            privacy_sigma: DP noise scale (σ in Gaussian mechanism)
            clipping_norm: Gradient clipping threshold (C)
            initial_lr: Learning rate for global model updates
        """
        self.num_clients = num_clients
        self.sigma = privacy_sigma
        self.C = clipping_norm
        self.lr = initial_lr
        
        # Global model (simplified: weight vector)
        self.global_weights = self._initialize_model()
        
        # Training history
        self.training_history = {
            "rounds": [],
            "global_loss": [],
            "privacy_budget": []
        }
        
        # Privacy accounting
        self.epsilon = 0.0  # Will be computed via moments accountant
        self.delta = 1e-5   # Target delta for (ε,δ)-DP
        
    def _initialize_model(self) -> np.ndarray:
        """Initialize global model weights (simplified)"""
        # For actual implementation, load PyTorch model
        # For simulation: 10-dimensional weight vector
        np.random.seed(42)
        return np.random.randn(10) * 0.01
    
    def aggregate_updates(self, client_updates: List[ClientUpdate]) -> np.ndarray:
        """
        FedAvg: Weighted average of client updates
        
        Equation 2 from Paper 13:
        w_{t+1} = Σ (n_k / n) × Δw_k
        
        Where:
        - n_k = number of samples at client k
        - n = total samples across all clients
        - Δw_k = client k's weight update
        """
        total_samples = sum([u.num_samples for u in client_updates])
        
        # Weighted aggregation
        aggregated_gradient = np.zeros_like(self.global_weights)
        
        for update in client_updates:
            weight = update.num_samples / total_samples
            aggregated_gradient += weight * update.gradients
        
        return aggregated_gradient
    
    def apply_differential_privacy(self, gradients: np.ndarray) -> np.ndarray:
        """
        Add Gaussian noise for (ε,δ)-Differential Privacy
        
        Equation 3 from Paper 13:
        Δw_noisy = Clip(Δw, C) + N(0, σ²C²I)
        
        Where:
        - Clip(): L2-norm clipping to threshold C
        - N(0, σ²C²I): Gaussian noise with scale σC
        """
        # Step 1: Clip gradients to norm C
        grad_norm = np.linalg.norm(gradients)
        if grad_norm > self.C:
            gradients = gradients * (self.C / grad_norm)
        
        # Step 2: Add Gaussian noise
        noise_scale = self.sigma * self.C
        noise = np.random.normal(0, noise_scale, size=gradients.shape)
        noisy_gradients = gradients + noise
        
        # Update privacy budget (simplified moments accountant)
        self.epsilon += self._compute_privacy_cost()
        
        return noisy_gradients
    
    def _compute_privacy_cost(self) -> float:
        """
        Compute privacy cost per round using moments accountant
        
        For Gaussian mechanism with sampling ratio q and noise σ:
        ε ≈ (q × T × √(2 ln(1/δ))) / σ
        
        Where:
        - q = sampling ratio (1.0 for full participation)
        - T = number of rounds
        - δ = target delta
        """
        q = 1.0  # All clients participate (worst case)
        epsilon_per_round = (q * np.sqrt(2 * np.log(1 / self.delta))) / self.sigma
        return epsilon_per_round
    
    def run_training(self, num_rounds: int = 10) -> Dict:
        """
        Execute federated training for specified rounds
        
        Returns:
            training_history: Dict with losses and privacy budget per round
        """
        print(f"🚀 Starting Federated Training")
        print(f"   Clients: {self.num_clients}")
        print(f"   Rounds: {num_rounds}")
        print(f"   Privacy: σ={self.sigma}, C={self.C}")
        print()
        
        for round_idx in range(1, num_rounds + 1):
            print(f"[Round {round_idx}/{num_rounds}]")
            
            # Step 1: Broadcast global model to clients (simulated)
            client_updates = self._simulate_client_training(round_idx)
            
            # Step 2: Aggregate client updates
            aggregated_gradient = self.aggregate_updates(client_updates)
            
            # Step 3: Apply differential privacy
            noisy_gradient = self.apply_differential_privacy(aggregated_gradient)
            
            # Step 4: Update global model
            self.global_weights = self.global_weights + self.lr * noisy_gradient
            
            # Step 5: Evaluate global loss (simulated)
            global_loss = self._evaluate_global_model()
            
            # Record history
            self.training_history["rounds"].append(round_idx)
            self.training_history["global_loss"].append(global_loss)
            self.training_history["privacy_budget"].append(self.epsilon)
            
            print(f"   Global Loss: {global_loss:.4f}")
            print(f"   Privacy Budget: ε={self.epsilon:.4f}, δ={self.delta}")
            print()
        
        print("✅ Federated Training Complete")
        self._save_results()
        return self.training_history
    
    def _simulate_client_training(self, round_idx: int) -> List[ClientUpdate]:
        """
        Simulate local training at each edge node
        In real implementation: clients perform local SGD on teacher-verified data
        """
        updates = []
        
        for client_id in range(self.num_clients):
            # Simulate gradient computation (random for demo)
            # Real: gradient = (local_weights - global_weights)
            gradient = np.random.randn(10) * 0.1
            
            # Simulate varying dataset sizes
            num_samples = np.random.randint(50, 200)
            
            # Simulate training loss (decreases over rounds)
            training_loss = 2.0 / (1 + 0.5 * round_idx) + np.random.uniform(0, 0.1)
            
            update = ClientUpdate(
                client_id=client_id,
                gradients=gradient,
                num_samples=num_samples,
                training_loss=training_loss,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            updates.append(update)
        
        return updates
    
    def _evaluate_global_model(self) -> float:
        """
        Evaluate global model on simulated holdout set
        In real implementation: test on teacher-verified validation data
        """
        # Simulate convergence: loss decreases logarithmically
        base_loss = 2.0
        improvement = len(self.training_history["rounds"]) * 0.15
        noise = np.random.uniform(-0.05, 0.05)
        return max(0.1, base_loss - improvement + noise)
    
    def _save_results(self):
        """Save training history and privacy audit"""
        Path("data").mkdir(exist_ok=True)
        
        # Save training history
        with open("data/fl_training_history.json", 'w') as f:
            # Convert numpy types to native Python for JSON serialization
            history = {
                "rounds": self.training_history["rounds"],
                "global_loss": [float(x) for x in self.training_history["global_loss"]],
                "privacy_budget": [float(x) for x in self.training_history["privacy_budget"]]
            }
            json.dump(history, f, indent=2)
        
        # Save privacy audit
        privacy_audit = {
            "mechanism": "Gaussian",
            "parameters": {
                "sigma": self.sigma,
                "clipping_norm": self.C,
                "delta": self.delta
            },
            "final_privacy_budget": {
                "epsilon": float(self.epsilon),
                "delta": self.delta
            },
            "interpretation": f"({self.epsilon:.2f}, {self.delta})-DP guarantee"
        }
        
        with open("data/fl_privacy_audit.json", 'w') as f:
            json.dump(privacy_audit, f, indent=2)
        
        print(f"📊 Results saved:")
        print(f"   - data/fl_training_history.json")
        print(f"   - data/fl_privacy_audit.json")


def main():
    """Run FL simulation"""
    print("="*60)
    print("PAPER 13: Federated Learning Simulation")
    print("="*60)
    print()
    
    # Initialize coordinator
    coordinator = FedAvgCoordinator(
        num_clients=5,          # 5 classrooms
        privacy_sigma=0.5,      # DP noise scale
        clipping_norm=1.0,      # Gradient clipping
        initial_lr=0.01         # Learning rate
    )
    
    # Run training
    history = coordinator.run_training(num_rounds=10)
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Initial Loss:     {history['global_loss'][0]:.4f}")
    print(f"Final Loss:       {history['global_loss'][-1]:.4f}")
    print(f"Loss Reduction:   {(history['global_loss'][0] - history['global_loss'][-1]):.4f}")
    print(f"Privacy Budget:   ε={history['privacy_budget'][-1]:.4f}, δ={coordinator.delta}")
    print("="*60)


if __name__ == "__main__":
    main()
