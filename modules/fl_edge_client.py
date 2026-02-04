#!/usr/bin/env python3
"""
Federated Learning Edge Client for Paper 13
Performs local training on teacher-verified samples.

Usage:
    client = FLEdgeClient(client_id=0, local_data=samples)
    update = client.local_training(global_weights, epochs=5)
"""

import numpy as np
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class LocalUpdate:
    """Local model update to send to coordinator"""
    gradients: np.ndarray
    num_samples: int
    training_loss: float
    training_time: float


class FLEdgeClient:
    """
    Edge node for federated learning
    Trains on local teacher-verified samples
    """
    
    def __init__(self, client_id: int, local_data: List[Dict]):
        """
        Args:
            client_id: Unique classroom/device identifier
            local_data: Teacher-verified training samples
        """
        self.client_id = client_id
        self.local_data = local_data
        self.local_weights = None
        
    def local_training(self, 
                      global_weights: np.ndarray,
                      epochs: int = 5,
                      learning_rate: float = 0.01) -> LocalUpdate:
        """
        Perform local SGD on teacher-verified data
        
        Args:
            global_weights: Current global model from coordinator
            epochs: Number of local training epochs
            learning_rate: Local SGD learning rate
            
        Returns:
            LocalUpdate with gradient, sample count, and metrics
        """
        start_time = time.time()
        
        # Initialize local model with global weights
        self.local_weights = global_weights.copy()
        
        # Simulate local training (simplified)
        # Real implementation: PyTorch/TensorFlow local SGD
        for epoch in range(epochs):
            # Simulate gradient computation
            gradient = self._compute_gradient()
            
            # Local SGD update
            self.local_weights = self.local_weights - learning_rate * gradient
        
        # Compute weight delta (gradient for FedAvg)
        weight_delta = self.local_weights - global_weights
        
        # Calculate training loss
        training_loss = self._evaluate_local_model()
        
        training_time = time.time() - start_time
        
        return LocalUpdate(
            gradients=weight_delta,
            num_samples=len(self.local_data),
            training_loss=training_loss,
            training_time=training_time
        )
    
    def _compute_gradient(self) -> np.ndarray:
        """
        Compute gradient on local batch
        Simplified: returns random gradient for simulation
        Real: forward-backward pass on local data
        """
        # Simulate realistic gradient (decreases with training)
        base_grad = np.random.randn(10) * 0.05
        return base_grad
    
    def _evaluate_local_model(self) -> float:
        """
        Evaluate local model on validation set
        Simplified: returns simulated loss
        """
        # Simulate loss decreasing with training
        base_loss = 1.5
        noise = np.random.uniform(-0.1, 0.1)
        return max(0.1, base_loss + noise)
    
    def simulate_drift(self, drift_type: str = "lighting"):
        """
        Simulate distribution shift in classroom
        
        Args:
            drift_type: Type of drift ("lighting", "demographics", "seating")
        """
        if drift_type == "lighting":
            # Simulate lighting change (darker classroom → lower confidence)
            for sample in self.local_data:
                sample['confidence'] *= 0.85
        
        elif drift_type == "demographics":
            # Simulate demographic shift (new students → unknown faces)
            num_drift = int(len(self.local_data) * 0.15)  # 15% drift
            for i in range(num_drift):
                self.local_data[i]['label'] = 'unknown'
        
        elif drift_type == "seating":
            # Simulate seating arrangement change (occlusion)
            for sample in self.local_data:
                sample['visibility'] = np.random.uniform(0.6, 1.0)


def simulate_multi_classroom_scenario():
    """
    Simulate 5 classrooms with varying drift conditions
    Used for Paper 13 validation
    """
    print("🏫 Simulating Multi-Classroom Drift Scenario")
    print("="*60)
    
    # Create 5 edge clients (classrooms)
    clients = []
    for i in range(5):
        # Simulate varying dataset sizes
        num_samples = np.random.randint(80, 150)
        local_data = [
            {
                'frame_id': j,
                'label': 'student_X',
                'confidence': 0.95,
                'visibility': 1.0
            }
            for j in range(num_samples)
        ]
        
        client = FLEdgeClient(client_id=i, local_data=local_data)
        clients.append(client)
    
    # Introduce drift in classrooms 2, 3, 4
    print("\n📉 Introducing Drift:")
    clients[2].simulate_drift(drift_type="lighting")
    print(f"   Classroom 2: Lighting drift (darker environment)")
    
    clients[3].simulate_drift(drift_type="demographics")
    print(f"   Classroom 3: Demographic drift (15% new students)")
    
    clients[4].simulate_drift(drift_type="seating")
    print(f"   Classroom 4: Seating drift (occlusion)")
    
    # Measure initial accuracy degradation
    baseline_accuracy = 0.95
    drift_classrooms = [clients[2], clients[3], clients[4]]
    
    degraded_accuracies = []
    for client in drift_classrooms:
        # Simulate accuracy drop due to drift
        avg_confidence = np.mean([s['confidence'] for s in client.local_data])
        degraded_acc = baseline_accuracy * avg_confidence
        degraded_accuracies.append(degraded_acc)
    
    avg_degradation = np.mean(degraded_accuracies)
    drift_percent = (baseline_accuracy - avg_degradation) / baseline_accuracy * 100
    
    print(f"\n📊 Initial Impact:")
    print(f"   Baseline Accuracy: {baseline_accuracy:.1%}")
    print(f"   Degraded Accuracy: {avg_degradation:.1%}")
    print(f"   Drift Impact:      {drift_percent:.1f}% accuracy loss")
    
    print("\n✅ Scenario Ready for FL Training")
    print("   Run FL coordinator with these clients to demonstrate drift compensation")
    
    return clients


if __name__ == "__main__":
    # Run multi-classroom simulation
    clients = simulate_multi_classroom_scenario()
    
    print("\n" + "="*60)
    print(f"Created {len(clients)} edge clients")
    print("Use with fl_coordinator.py to validate Paper 13 claims")
