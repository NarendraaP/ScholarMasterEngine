"""
DP-FedAvg Trainer for Paper 13
Implements Differentially Private Federated Averaging with:
- Gradient clipping (C=1.0)
- Gaussian noise injection (σ=0.5)
- Privacy accounting via moments accountant

Based on Algorithm 1 from Paper 13 (Lines 191-212)
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Tuple, Optional
from .privacy_accountant import PrivacyAccountant


class DPFedAvgTrainer:
    """
    Differentially Private Federated Averaging Trainer.
    
    Implements Paper 13's DP-FedAvg algorithm with:
    - Client-side local SGD training
    - Gradient clipping for bounded sensitivity
    - Gaussian noise injection for (ε, δ)-DP
    - Moments accountant for privacy tracking
    """
    
    def __init__(
        self,
        model: nn.Module,
        num_clients: int = 5,
        sigma: float = 0.5,
        clipping_norm: float = 1.0,
        delta: float = 1e-5,
        local_epochs: int = 5,
        learning_rate: float = 0.001
    ):
        """
        Initialize DP-FedAvg trainer.
        
        Args:
            model: Global PyTorch model
            num_clients: Number of federated clients (default: 5 classrooms)
            sigma: Noise multiplier (default: 0.5 from Paper 13)
            clipping_norm: Gradient clipping norm C (default: 1.0)
            delta: Failure probability (default: 10^-5)
            local_epochs: Local training epochs per round (default: 5)
            learning_rate: Local SGD learning rate (default: 0.001)
        """
        self.global_model = model
        self.num_clients = num_clients
        self.sigma = sigma
        self.clipping_norm = clipping_norm
        self.local_epochs = local_epochs
        self.learning_rate = learning_rate
        
        # Initialize privacy accountant
        self.privacy_accountant = PrivacyAccountant(delta=delta)
        
        # Training history
        self.history = {
            'rounds': [],
            'global_loss': [],
            'epsilon': [],
            'communication_mb': []
        }
    
    def _clip_gradient(self, gradient: Dict[str, torch.Tensor], C: float) -> Dict[str, torch.Tensor]:
        """
        Clip gradient to bounded L2 norm.
        
        Formula (Paper 13, Algorithm 1, Line 8):
            Δw_i ← min(1, C/||Δw_i||_2) · Δw_i
        
        Args:
            gradient: Dictionary of parameter gradients
            C: Clipping norm
        
        Returns:
            clipped_gradient: Gradient with bounded L2 norm
        """
        # Compute L2 norm of gradient
        grad_norm = torch.sqrt(sum(torch.sum(g ** 2) for g in gradient.values()))
        
        # Compute clipping factor
        clip_factor = min(1.0, C / (grad_norm.item() + 1e-10))
        
        # Apply clipping
        clipped_gradient = {
            name: grad * clip_factor
            for name, grad in gradient.items()
        }
        
        return clipped_gradient
    
    def _add_gaussian_noise(
        self,
        gradient: Dict[str, torch.Tensor],
        sigma: float,
        C: float
    ) -> Dict[str, torch.Tensor]:
        """
        Add Gaussian noise for differential privacy.
        
        Formula (Paper 13, Algorithm 1, Line 11):
            Δw_avg ← Δw_avg + N(0, σ²C²I)
        
        Args:
            gradient: Aggregated gradient
            sigma: Noise multiplier
            C: Clipping norm
        
        Returns:
            noisy_gradient: DP-protected gradient
        """
        noisy_gradient = {}
        
        for name, grad in gradient.items():
            # Generate Gaussian noise: N(0, σ²C²I)
            noise = torch.randn_like(grad) * (sigma * C)
            noisy_gradient[name] = grad + noise
        
        return noisy_gradient
    
    def _local_sgd(
        self,
        client_data: torch.utils.data.DataLoader,
        initial_weights: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Perform local SGD training on client data.
        
        Args:
            client_data: Client's local dataset
            initial_weights: Global model weights
        
        Returns:
            gradient: Weight update (Δw_i = w_i - w_t)
        """
        # Create local model copy
        local_model = type(self.global_model)()
        local_model.load_state_dict(initial_weights)
        local_model.train()
        
        # Optimizer
        optimizer = torch.optim.SGD(
            local_model.parameters(),
            lr=self.learning_rate
        )
        criterion = nn.CrossEntropyLoss()
        
        # Local training
        for epoch in range(self.local_epochs):
            for batch_x, batch_y in client_data:
                optimizer.zero_grad()
                outputs = local_model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        # Compute gradient: Δw_i = w_i - w_t
        gradient = {}
        for name, param in local_model.named_parameters():
            gradient[name] = param.data - initial_weights[name]
        
        return gradient
    
    def _aggregate_gradients(
        self,
        gradients: List[Dict[str, torch.Tensor]]
    ) -> Dict[str, torch.Tensor]:
        """
        Aggregate client gradients (simple averaging).
        
        Formula (Paper 13, Algorithm 1, Line 10):
            Δw_avg = (1/N) Σ Δw_i
        
        Args:
            gradients: List of client gradients
        
        Returns:
            avg_gradient: Averaged gradient
        """
        avg_gradient = {}
        
        # Get parameter names from first gradient
        param_names = gradients[0].keys()
        
        for name in param_names:
            # Average across clients
            avg_gradient[name] = torch.stack([
                grad[name] for grad in gradients
            ]).mean(dim=0)
        
        return avg_gradient
    
    def _measure_communication(self, gradient: Dict[str, torch.Tensor]) -> float:
        """
        Measure gradient size in MB.
        
        Args:
            gradient: Gradient dictionary
        
        Returns:
            size_mb: Gradient size in megabytes
        """
        total_params = sum(g.numel() for g in gradient.values())
        size_bytes = total_params * 4  # float32 = 4 bytes
        size_mb = size_bytes / (1024 ** 2)
        
        return size_mb
    
    def federated_round(
        self,
        client_datasets: List[torch.utils.data.DataLoader]
    ) -> Tuple[float, float]:
        """
        Execute one round of DP-FedAvg.
        
        Implements Paper 13 Algorithm 1 (Lines 191-212):
        1. Broadcast global model to clients
        2. Clients train locally and compute gradients
        3. Clip gradients for bounded sensitivity
        4. Aggregate and add Gaussian noise
        5. Update global model
        6. Track privacy budget
        
        Args:
            client_datasets: List of client data loaders
        
        Returns:
            (global_loss, epsilon): Loss and cumulative privacy budget
        """
        # Get current global weights
        global_weights = {
            name: param.data.clone()
            for name, param in self.global_model.named_parameters()
        }
        
        # Step 1-2: Local training on each client
        client_gradients = []
        for client_data in client_datasets:
            gradient = self._local_sgd(client_data, global_weights)
            client_gradients.append(gradient)
        
        # Step 3: Clip gradients
        clipped_gradients = [
            self._clip_gradient(grad, self.clipping_norm)
            for grad in client_gradients
        ]
        
        # Step 4: Aggregate
        avg_gradient = self._aggregate_gradients(clipped_gradients)
        
        # Step 5: Add Gaussian noise
        noisy_gradient = self._add_gaussian_noise(
            avg_gradient,
            self.sigma,
            self.clipping_norm
        )
        
        # Step 6: Update global model
        with torch.no_grad():
            for name, param in self.global_model.named_parameters():
                param.data += noisy_gradient[name]
        
        # Step 7: Privacy accounting
        epsilon = self.privacy_accountant.update_budget(
            sigma=self.sigma,
            q=1.0  # All clients participate (q=1.0)
        )
        
        # Measure communication
        comm_mb = self._measure_communication(noisy_gradient) * self.num_clients
        
        # Compute global loss (for monitoring)
        self.global_model.eval()
        total_loss = 0.0
        total_samples = 0
        criterion = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for client_data in client_datasets:
                for batch_x, batch_y in client_data:
                    outputs = self.global_model(batch_x)
                    loss = criterion(outputs, batch_y)
                    total_loss += loss.item() * len(batch_y)
                    total_samples += len(batch_y)
        
        global_loss = total_loss / total_samples
        
        # Record history
        self.history['rounds'].append(len(self.history['rounds']) + 1)
        self.history['global_loss'].append(global_loss)
        self.history['epsilon'].append(epsilon)
        self.history['communication_mb'].append(comm_mb)
        
        return global_loss, epsilon
    
    def train(
        self,
        client_datasets: List[torch.utils.data.DataLoader],
        num_rounds: int = 10
    ) -> Dict:
        """
        Execute full DP-FedAvg training.
        
        Args:
            client_datasets: List of client data loaders
            num_rounds: Number of federated rounds (default: 10 from Paper 13)
        
        Returns:
            results: Training results and privacy report
        """
        print(f"🔐 Starting DP-FedAvg Training")
        print(f"   Clients: {self.num_clients}")
        print(f"   Rounds: {num_rounds}")
        print(f"   Noise (σ): {self.sigma}")
        print(f"   Clipping (C): {self.clipping_norm}")
        print("=" * 60)
        
        for round_num in range(1, num_rounds + 1):
            loss, epsilon = self.federated_round(client_datasets)
            comm_mb = self.history['communication_mb'][-1]
            
            print(f"Round {round_num:2d} | Loss: {loss:.4f} | ε: {epsilon:6.2f} | Comm: {comm_mb:5.1f} MB")
        
        # Final privacy validation
        is_valid, message = self.privacy_accountant.validate_budget(target_epsilon=95.97)
        print("=" * 60)
        print(message)
        
        # Communication budget validation
        total_comm_mb = sum(self.history['communication_mb'])
        if total_comm_mb <= 500:
            print(f"✅ Communication budget validated: {total_comm_mb:.1f} MB (target: ≤500 MB)")
        else:
            print(f"❌ Communication budget exceeded: {total_comm_mb:.1f} MB (target: ≤500 MB)")
        
        return {
            'history': self.history,
            'privacy_report': self.privacy_accountant.get_report(),
            'final_epsilon': epsilon,
            'total_communication_mb': total_comm_mb
        }


# Validation test
if __name__ == "__main__":
    print("🧪 DP-FedAvg Trainer Validation Test")
    print("=" * 60)
    
    # Create dummy model and data
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(10, 2)
        
        def forward(self, x):
            return self.fc(x)
    
    model = SimpleModel()
    
    # Create dummy client datasets (5 classrooms)
    client_datasets = []
    for i in range(5):
        X = torch.randn(100, 10)
        y = torch.randint(0, 2, (100,))
        dataset = torch.utils.data.TensorDataset(X, y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=32)
        client_datasets.append(loader)
    
    # Initialize trainer
    trainer = DPFedAvgTrainer(
        model=model,
        num_clients=5,
        sigma=0.5,
        clipping_norm=1.0,
        delta=1e-5
    )
    
    # Run 10 rounds
    results = trainer.train(client_datasets, num_rounds=10)
    
    print(f"\n📊 Final Results:")
    print(f"   Final ε: {results['final_epsilon']:.2f}")
    print(f"   Total Communication: {results['total_communication_mb']:.1f} MB")
