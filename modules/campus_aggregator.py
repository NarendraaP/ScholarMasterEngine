#!/usr/bin/env python3
"""
Campus Aggregator (Tier 2)
Paper 14: Cross-Campus Federated Intelligence

This module implements the campus-level aggregator that:
1. Collects updates from classroom edge nodes within a single institution
2. Aggregates using weighted average (FedAvg)
3. Adds hierarchical differential privacy noise
4. Submits aggregated update to global coordinator
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import time

@dataclass
class EdgeUpdate:
    """Update from a single classroom edge node"""
    node_id: str
    weights: np.ndarray
    num_samples: int
    timestamp: float

class CampusAggregator:
    """
    Tier 2: Campus-level aggregator
    
    Provides institutional firewall - no individual classroom data
    leaves the campus network
    """
    
    def __init__(self,
                 campus_id: str,
                 model_dim: int = 1000,
                 dp_sigma: float = 0.3,
                 output_dir: str = "data/campus_aggregators"):
        """
        Initialize campus aggregator
        
        Args:
            campus_id: Unique campus identifier
            model_dim: Model weight dimension
            dp_sigma: DP noise scale for campus-level privacy
            output_dir: Output directory
        """
        self.campus_id = campus_id
        self.model_dim = model_dim
        self.dp_sigma = dp_sigma
        self.output_dir = Path(output_dir) / campus_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Current campus model
        self.campus_weights = np.random.randn(model_dim) * 0.01
        
        # Registry of edge nodes
        self.edge_registry: Dict[str, int] = {}  # node_id -> num_samples
        
        print(f"🏛️  Campus Aggregator '{campus_id}' initialized")
        print(f"   DP Noise σ: {dp_sigma}")
        
    def register_edge_node(self, node_id: str, num_samples: int):
        """Register an edge node (classroom) in this campus"""
        self.edge_registry[node_id] = num_samples
        print(f"   ✅ Registered {node_id} ({num_samples} samples)")
        
    def aggregate_edge_updates(self, edge_updates: List[EdgeUpdate]) -> np.ndarray:
        """
        Aggregate updates from classroom nodes using weighted FedAvg
        
        w_campus = Σ (n_k / N_campus) * w_k
        
        Args:
            edge_updates: Updates from edge nodes
            
        Returns:
            Aggregated campus weights
        """
        if not edge_updates:
            return self.campus_weights
        
        # Calculate total samples
        total_samples = sum(u.num_samples for u in edge_updates)
        
        # Weighted average
        aggregated = np.zeros_like(self.campus_weights)
        for update in edge_updates:
            weight = update.num_samples / total_samples
            aggregated += weight * update.weights
        
        return aggregated
    
    def add_dp_noise(self, weights: np.ndarray) -> np.ndarray:
        """
        Add campus-level differential privacy noise
        
        Hierarchical DP: Edge nodes already added noise, this is second layer
        
        Args:
            weights: Aggregated campus weights
            
        Returns:
            Noisy weights
        """
        noise = np.random.normal(0, self.dp_sigma, size=weights.shape)
        return weights + noise
    
    def process_round(self, edge_updates: List[EdgeUpdate]) -> Dict:
        """
        Process one aggregation round
        
        1. Aggregate edge updates (FedAvg)
        2. Add DP noise (campus-level privacy)
        3. Prepare for transmission to global coordinator
        
        Args:
            edge_updates: Updates from participating classrooms
            
        Returns:
            Campus update package
        """
        print(f"\n🔄 {self.campus_id} Aggregation Round")
        print(f"   Participating Nodes: {len(edge_updates)}")
        
        # Aggregate
        aggregated_weights = self.aggregate_edge_updates(edge_updates)
        
        # Add DP noise
        noisy_weights = self.add_dp_noise(aggregated_weights)
        
        # Update local campus model
        self.campus_weights = noisy_weights
        
        # Calculate total samples
        total_samples = sum(u.num_samples for u in edge_updates)
        
        return {
            'campus_id': self.campus_id,
            'weights': noisy_weights,
            'num_samples': total_samples,
            'num_nodes': len(edge_updates),
            'timestamp': time.time()
        }


if __name__ == "__main__":
    """
    Demo: Simulate campus aggregation with 10 classroom nodes
    """
    print("="*60)
    print("CAMPUS AGGREGATOR SIMULATION")
    print("="*60)
    
    # Create campus aggregator
    campus = CampusAggregator(
        campus_id="Campus_A",
        model_dim=1000,
        dp_sigma=0.3
    )
    
    # Register 10 classroom nodes
    num_classrooms = 10
    for i in range(num_classrooms):
        node_id = f"Classroom_{i+1}"
        num_samples = np.random.randint(80, 150)  # Variable class sizes
        campus.register_edge_node(node_id, num_samples)
    
    # Simulate edge updates
    print(f"\n📡 Simulating edge updates from {num_classrooms} classrooms...")
    edge_updates = []
    for node_id, num_samples in campus.edge_registry.items():
        # Simulate local training (random weights for demo)
        weights = np.random.randn(1000) * 0.1
        
        update = EdgeUpdate(
            node_id=node_id,
            weights=weights,
            num_samples=num_samples,
            timestamp=time.time()
        )
        edge_updates.append(update)
    
    # Process aggregation round
    campus_update = campus.process_round(edge_updates)
    
    print(f"\n📊 Campus Update Summary:")
    print(f"   Campus ID: {campus_update['campus_id']}")
    print(f"   Total Samples: {campus_update['num_samples']}")
    print(f"   Participating Nodes: {campus_update['num_nodes']}")
    print(f"   Weight Vector Norm: {np.linalg.norm(campus_update['weights']):.4f}")
    
    print("\n✅ Campus aggregation complete!")
