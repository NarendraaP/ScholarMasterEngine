#!/usr/bin/env python3
"""
Hierarchical Federated Averaging (H-FedAvg) Global Coordinator
Paper 14: Cross-Campus Federated Intelligence

This module implements the Tier 3 (Global Federation) server that:
1. Receives aggregated updates from multiple campus aggregators
2. Applies staleness-aware weighting to asynchronous updates
3. Broadcasts updated global model back to campuses
"""

import numpy as np
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from datetime import datetime

@dataclass
class CampusUpdate:
    """Represents an update from a single campus aggregator"""
    campus_id: str
    weights: np.ndarray
    num_samples: int
    base_epoch: int  # Epoch on which this update was computed
    timestamp: float
    
@dataclass
class GlobalState:
    """Global model state"""
    global_weights: np.ndarray
    current_epoch: int
    total_samples: int
    participating_campuses: List[str]
    
class HierarchicalFedAvgCoordinator:
    """
    Global Federation Server implementing Hierarchical FedAvg
    
    Key Features:
    - Staleness-aware asynchronous aggregation
    - Campus-weighted averaging (by total sample count)
    - Convergence tracking and history logging
    """
    
    def __init__(self, 
                 model_dim: int = 1000,
                 global_lr: float = 1.0,
                 staleness_gamma: float = 0.5,
                 output_dir: str = "data/h_fedavg"):
        """
        Initialize H-FedAvg coordinator
        
        Args:
            model_dim: Dimension of model weight vector
            global_lr: Global learning rate (η in paper)
            staleness_gamma: Staleness decay parameter (γ in paper)
            output_dir: Directory for saving logs and checkpoints
        """
        self.model_dim = model_dim
        self.global_lr = global_lr
        self.staleness_gamma = staleness_gamma
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize global model
        self.global_weights = np.random.randn(model_dim) * 0.01
        self.current_epoch = 0
        self.total_samples = 0
        
        # Training history
        self.history = {
            'epochs': [],
            'global_loss': [],
            'num_campuses': [],
            'staleness_values': [],
            'campus_contributions': []
        }
        
        # Campus registry
        self.campus_registry: Dict[str, int] = {}  # campus_id -> num_samples
        
        print(f"🌐 H-FedAvg Coordinator Initialized")
        print(f"   Model Dimension: {model_dim}")
        print(f"   Staleness γ: {staleness_gamma}")
        
    def register_campus(self, campus_id: str, num_samples: int):
        """Register a new campus in the federation"""
        self.campus_registry[campus_id] = num_samples
        self.total_samples += num_samples
        print(f"✅ Registered Campus '{campus_id}' with {num_samples} samples")
        
    def compute_staleness_weight(self, staleness: int) -> float:
        """
        Compute dampening factor for stale updates
        
        α(τ) = 1 / (1 + τ)^γ
        
        Args:
            staleness: τ = current_epoch - base_epoch
            
        Returns:
            Dampening weight in [0, 1]
        """
        return 1.0 / ((1 + staleness) ** self.staleness_gamma)
    
    def aggregate_campus_updates(self, campus_updates: List[CampusUpdate]) -> np.ndarray:
        """
        Aggregate updates from multiple campuses with staleness-aware weighting
        
        Algorithm:
        1. For each campus update:
            - Compute staleness τ = current_epoch - base_epoch
            - Apply dampening α(τ)
            - Weight by campus sample count
        2. Normalize and aggregate
        
        Args:
            campus_updates: List of updates from campuses
            
        Returns:
            Aggregated gradient update
        """
        if not campus_updates:
            return np.zeros_like(self.global_weights)
        
        aggregated_delta = np.zeros_like(self.global_weights)
        total_weight = 0.0
        staleness_vals = []
        
        for update in campus_updates:
            # Compute staleness
            staleness = self.current_epoch - update.base_epoch
            staleness_vals.append(staleness)
            
            # Apply staleness dampening
            alpha = self.compute_staleness_weight(staleness)
            
            # Weight by campus size (number of samples)
            campus_weight = update.num_samples / self.total_samples
            
            # Combined weight
            combined_weight = alpha * campus_weight
            
            # Compute gradient (delta from global model)
            delta = update.weights - self.global_weights
            
            # Accumulate weighted update
            aggregated_delta += combined_weight * delta
            total_weight += combined_weight
            
            print(f"   Campus {update.campus_id}: staleness={staleness}, α={alpha:.3f}, weight={combined_weight:.3f}")
        
        # Normalize by total weight
        if total_weight > 0:
            aggregated_delta /= total_weight
        
        # Record staleness statistics
        self.history['staleness_values'].append(staleness_vals)
        
        return aggregated_delta
    
    def update_global_model(self, campus_updates: List[CampusUpdate]) -> Tuple[np.ndarray, float]:
        """
        Update global model with campus aggregations
        
        w_new = w_current + η * Σ[α(τ) * weight_c * Δw_c]
        
        Args:
            campus_updates: Updates from participating campuses
            
        Returns:
            (updated_weights, global_loss_estimate)
        """
        # Aggregate campus updates
        aggregated_delta = self.aggregate_campus_updates(campus_updates)
        
        # Update global model
        self.global_weights += self.global_lr * aggregated_delta
        
        # Increment epoch
        self.current_epoch += 1
        
        # Estimate global loss (simplified: L2 norm of delta as proxy)
        global_loss = np.linalg.norm(aggregated_delta)
        
        # Record history
        self.history['epochs'].append(self.current_epoch)
        self.history['global_loss'].append(global_loss)
        self.history['num_campuses'].append(len(campus_updates))
        self.history['campus_contributions'].append([u.campus_id for u in campus_updates])
        
        print(f"\n📊 Global Update (Epoch {self.current_epoch})")
        print(f"   Global Loss: {global_loss:.4f}")
        print(f"   Participating Campuses: {len(campus_updates)}")
        
        return self.global_weights.copy(), global_loss
    
    def simulate_training_round(self, 
                                 num_campuses: int = 5,
                                 dropout_rate: float = 0.0) -> Dict:
        """
        Simulate a training round with multiple campuses
        
        Args:
            num_campuses: Number of campuses in federation
            dropout_rate: Probability of campus dropout
            
        Returns:
            Round statistics
        """
        # Simulate campus updates (some may drop out)
        campus_updates = []
        
        for i in range(num_campuses):
            campus_id = f"Campus_{chr(65+i)}"  # A, B, C, ...
            
            # Simulate dropout
            if np.random.rand() < dropout_rate:
                print(f"⚠️  {campus_id} dropped (network issue)")
                continue
            
            # Register if first round
            if campus_id not in self.campus_registry:
                num_samples = np.random.randint(5000, 15000)  # Random campus size
                self.register_campus(campus_id, num_samples)
            
            # Simulate local training (random gradient for demo)
            local_weights = self.global_weights + np.random.randn(self.model_dim) * 0.1
            
            # Simulate variable staleness (some campuses slower)
            staleness_delay = np.random.randint(0, 3)  # 0-2 epochs behind
            base_epoch = max(0, self.current_epoch - staleness_delay)
            
            update = CampusUpdate(
                campus_id=campus_id,
                weights=local_weights,
                num_samples=self.campus_registry[campus_id],
                base_epoch=base_epoch,
                timestamp=time.time()
            )
            campus_updates.append(update)
        
        # Aggregate and update
        new_weights, loss = self.update_global_model(campus_updates)
        
        return {
            'epoch': self.current_epoch,
            'loss': loss,
            'participating_campuses': len(campus_updates),
            'total_campuses': num_campuses
        }
    
    def save_history(self):
        """Save training history to JSON"""
        history_file = self.output_dir / "h_fedavg_training_history.json"
        
        # Convert numpy arrays to lists for JSON serialization
        json_history = {
            'epochs': self.history['epochs'],
            'global_loss': self.history['global_loss'],
            'num_campuses': self.history['num_campuses'],
            'staleness_values': self.history['staleness_values'],
            'campus_contributions': self.history['campus_contributions']
        }
        
        with open(history_file, 'w') as f:
            json.dump(json_history, f, indent=2)
        
        print(f"\n💾 Training history saved to {history_file}")
    
    def get_summary(self) -> Dict:
        """Get training summary statistics"""
        if not self.history['epochs']:
            return {}
        
        return {
            'total_epochs': self.current_epoch,
            'initial_loss': self.history['global_loss'][0] if self.history['global_loss'] else 0,
            'final_loss': self.history['global_loss'][-1] if self.history['global_loss'] else 0,
            'total_campuses': len(self.campus_registry),
            'avg_participation': np.mean(self.history['num_campuses']) if self.history['num_campuses'] else 0
        }


if __name__ == "__main__":
    """
    Demo: Simulate 10 rounds of hierarchical federated learning
    with 5 campuses and 20% dropout rate
    """
    print("="*60)
    print("HIERARCHICAL FEDAVG SIMULATION")
    print("Paper 14: Cross-Campus Federated Intelligence")
    print("="*60)
    
    # Initialize coordinator
    coordinator = HierarchicalFedAvgCoordinator(
        model_dim=1000,
        global_lr=1.0,
        staleness_gamma=0.5
    )
    
    # Run 10 training rounds
    num_rounds = 10
    num_campuses = 5
    dropout_rate = 0.2  # 20% chance of campus dropout per round
    
    print(f"\n🚀 Starting {num_rounds} rounds with {num_campuses} campuses")
    print(f"   Dropout rate: {dropout_rate*100:.0f}%\n")
    
    for round_num in range(1, num_rounds + 1):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}/{num_rounds}")
        print('='*60)
        
        stats = coordinator.simulate_training_round(
            num_campuses=num_campuses,
            dropout_rate=dropout_rate
        )
    
    # Save results
    coordinator.save_history()
    
    # Print summary
    summary = coordinator.get_summary()
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Total Rounds:        {summary['total_epochs']}")
    print(f"Initial Loss:        {summary['initial_loss']:.4f}")
    print(f"Final Loss:          {summary['final_loss']:.4f}")
    print(f"Loss Reduction:      {summary['initial_loss'] - summary['final_loss']:.4f}")
    print(f"Total Campuses:      {summary['total_campuses']}")
    print(f"Avg Participation:   {summary['avg_participation']:.1f}/{num_campuses}")
    print("="*60)
    
    print("\n✅ H-FedAvg simulation complete!")
