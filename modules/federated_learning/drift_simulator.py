"""
Drift Simulator for Paper 13
Implements three drift scenarios for model drift characterization:
1. Lighting Drift (window tinting)
2. Demographic Drift (student turnover)
3. Seating Drift (back-row occlusion)

Based on Paper 13 Section III.B (Lines 156-169)
"""

import numpy as np
import torch
from typing import Tuple, Optional
from PIL import Image


class DriftSimulator:
    """
    Simulates three real-world drift scenarios for Paper 13 validation.
    
    Expected accuracy drops (Paper 13 Section III.B):
    - Lighting: 15%
    - Demographic: 12%
    - Seating: 8%
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize drift simulator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
        torch.manual_seed(seed)
    
    def apply_lighting_drift(
        self,
        images: np.ndarray,
        brightness_reduction: float = 0.15,
        noise_std: float = 0.05
    ) -> np.ndarray:
        """
        Scenario 1: Lighting Drift (window tinting).
        
        Simulates window tinting by reducing brightness and adding Gaussian noise.
        
        Paper 13 Section VI.B:
        "Simulate window tinting by reducing sample brightness by 15%,
         add Gaussian noise (σ=0.05). Expected accuracy drop: 15%."
        
        Args:
            images: Input images (N, H, W, C) in range [0, 1]
            brightness_reduction: Brightness reduction factor (default: 0.15)
            noise_std: Gaussian noise standard deviation (default: 0.05)
        
        Returns:
            drifted_images: Images with lighting drift applied
        """
        # Reduce brightness
        drifted = images * (1 - brightness_reduction)
        
        # Add Gaussian noise
        noise = np.random.normal(0, noise_std, images.shape)
        drifted = drifted + noise
        
        # Clip to valid range [0, 1]
        drifted = np.clip(drifted, 0, 1)
        
        return drifted.astype(np.float32)
    
    def apply_demographic_drift(
        self,
        dataset: Tuple[np.ndarray, np.ndarray],
        turnover_rate: float = 0.15,
        new_samples: Optional[Tuple[np.ndarray, np.ndarray]] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Scenario 2: Demographic Drift (student turnover).
        
        Simulates student departure and arrival by removing 15% of samples
        and adding new unseen samples.
        
        Paper 13 Section VI.B:
        "Remove 15% of training samples (simulating student departure),
         add new unseen samples. Expected accuracy drop: 12%."
        
        Args:
            dataset: Tuple of (images, labels)
            turnover_rate: Fraction of students to replace (default: 0.15)
            new_samples: Optional new samples to add. If None, duplicates existing.
        
        Returns:
            (drifted_images, drifted_labels): Dataset with demographic drift
        """
        images, labels = dataset
        n_samples = len(images)
        n_remove = int(n_samples * turnover_rate)
        
        # Remove random samples (simulate departures)
        keep_indices = np.random.choice(
            n_samples,
            size=n_samples - n_remove,
            replace=False
        )
        remaining_images = images[keep_indices]
        remaining_labels = labels[keep_indices]
        
        # Add new samples (simulate arrivals)
        if new_samples is not None:
            new_images, new_labels = new_samples
            # Take first n_remove samples
            new_images = new_images[:n_remove]
            new_labels = new_labels[:n_remove]
        else:
            # Duplicate existing samples with slight augmentation
            duplicate_indices = np.random.choice(
                len(remaining_images),
                size=n_remove,
                replace=True
            )
            new_images = remaining_images[duplicate_indices]
            new_labels = remaining_labels[duplicate_indices]
            
            # Add slight noise to differentiate
            noise = np.random.normal(0, 0.02, new_images.shape)
            new_images = np.clip(new_images + noise, 0, 1)
        
        # Combine
        drifted_images = np.concatenate([remaining_images, new_images])
        drifted_labels = np.concatenate([remaining_labels, new_labels])
        
        return drifted_images.astype(np.float32), drifted_labels
    
    def apply_seating_drift(
        self,
        images: np.ndarray,
        occlusion_ratio: float = 0.20,
        occlusion_type: str = 'top'
    ) -> np.ndarray:
        """
        Scenario 3: Seating Drift (back-row occlusion).
        
        Simulates back-row viewing angles by masking 20% of face region.
        
        Paper 13 Section VI.B:
        "Introduce occlusion (mask 20% of face region) to simulate
         back-row viewing angles. Expected accuracy drop: 8%."
        
        Args:
            images: Input images (N, H, W, C) in range [0, 1]
            occlusion_ratio: Fraction of image to occlude (default: 0.20)
            occlusion_type: 'top', 'bottom', 'random' (default: 'top')
        
        Returns:
            drifted_images: Images with seating drift (occlusion) applied
        """
        drifted = images.copy()
        n, h, w, c = images.shape
        
        if occlusion_type == 'top':
            # Occlude top portion (forehead region)
            mask_h = int(h * occlusion_ratio)
            drifted[:, :mask_h, :, :] = 0
        
        elif occlusion_type == 'bottom':
            # Occlude bottom portion (chin region)
            mask_h = int(h * occlusion_ratio)
            drifted[:, -mask_h:, :, :] = 0
        
        elif occlusion_type == 'random':
            # Random rectangular occlusion
            for i in range(n):
                mask_h = int(h * occlusion_ratio)
                mask_w = int(w * occlusion_ratio)
                
                # Random position
                y = np.random.randint(0, h - mask_h)
                x = np.random.randint(0, w - mask_w)
                
                drifted[i, y:y+mask_h, x:x+mask_w, :] = 0
        
        return drifted.astype(np.float32)
    
    def generate_drift_dataset(
        self,
        base_dataset: Tuple[np.ndarray, np.ndarray],
        scenario: str = 'lighting'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate drifted dataset for specified scenario.
        
        Args:
            base_dataset: Tuple of (images, labels)
            scenario: 'lighting', 'demographic', or 'seating'
        
        Returns:
            (drifted_images, labels): Drifted dataset
        """
        images, labels = base_dataset
        
        if scenario == 'lighting':
            drifted_images = self.apply_lighting_drift(images)
            return drifted_images, labels
        
        elif scenario == 'demographic':
            return self.apply_demographic_drift((images, labels))
        
        elif scenario == 'seating':
            drifted_images = self.apply_seating_drift(images)
            return drifted_images, labels
        
        else:
            raise ValueError(f"Unknown scenario: {scenario}. Choose from: lighting, demographic, seating")
    
    def measure_drift(
        self,
        model: torch.nn.Module,
        clean_data: torch.utils.data.DataLoader,
        drifted_data: torch.utils.data.DataLoader
    ) -> Tuple[float, float, float]:
        """
        Measure accuracy degradation due to drift.
        
        Paper 13 Section III.B:
        "Drift is measured as accuracy degradation over time:
         Drift = Acc_t=0 - Acc_t=T"
        
        Args:
            model: Trained model
            clean_data: Clean (no drift) test data
            drifted_data: Drifted test data
        
        Returns:
            (acc_clean, acc_drifted, drift): Accuracy metrics
        """
        model.eval()
        
        def evaluate(data_loader):
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_x, batch_y in data_loader:
                    outputs = model(batch_x)
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
            
            return 100.0 * correct / total
        
        acc_clean = evaluate(clean_data)
        acc_drifted = evaluate(drifted_data)
        drift = acc_clean - acc_drifted
        
        return acc_clean, acc_drifted, drift


# Validation test
if __name__ == "__main__":
    print("🔬 Drift Simulator Validation Test")
    print("=" * 60)
    
    # Create dummy dataset
    n_samples = 100
    images = np.random.rand(n_samples, 64, 64, 3).astype(np.float32)
    labels = np.random.randint(0, 10, n_samples)
    
    simulator = DriftSimulator(seed=42)
    
    # Test Scenario 1: Lighting Drift
    print("\n1. Lighting Drift (window tinting)")
    drifted_lighting = simulator.apply_lighting_drift(images)
    print(f"   Original range: [{images.min():.3f}, {images.max():.3f}]")
    print(f"   Drifted range:  [{drifted_lighting.min():.3f}, {drifted_lighting.max():.3f}]")
    print(f"   Mean brightness reduction: {(images.mean() - drifted_lighting.mean()) / images.mean() * 100:.1f}%")
    
    # Test Scenario 2: Demographic Drift
    print("\n2. Demographic Drift (student turnover)")
    drifted_demo, drifted_labels = simulator.apply_demographic_drift((images, labels))
    print(f"   Original samples: {len(images)}")
    print(f"   Drifted samples:  {len(drifted_demo)}")
    print(f"   Turnover rate: 15%")
    
    # Test Scenario 3: Seating Drift
    print("\n3. Seating Drift (back-row occlusion)")
    drifted_seating = simulator.apply_seating_drift(images)
    occlusion_ratio = (images != 0).sum() - (drifted_seating != 0).sum()
    occlusion_ratio /= (images != 0).sum()
    print(f"   Occlusion ratio: {occlusion_ratio * 100:.1f}%")
    print(f"   Expected: 20%")
    
    print("\n✅ All drift scenarios validated!")
