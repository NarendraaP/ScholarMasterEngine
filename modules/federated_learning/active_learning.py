"""
Active Learning Selector for Paper 13
Implements teacher-in-the-loop active learning for label-efficient retraining.

Based on Paper 13 Algorithm 2 (Lines 225-244) and Section V.A
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Optional


class ActiveLearningSelector:
    """
    Teacher-in-the-loop active learning for label-efficient retraining.
    
    Reduces teacher labeling burden from 3000 frames/month to 450 (85% reduction)
    by selecting only high-uncertainty samples for verification.
    
    Paper 13 Section V.A:
    "Rather than asking teachers to label random frames, the system selects
     samples with the highest model uncertainty (Entropy)."
    """
    
    def __init__(
        self,
        entropy_threshold: float = 0.7,
        monthly_budget: int = 100
    ):
        """
        Initialize active learning selector.
        
        Args:
            entropy_threshold: Minimum entropy for teacher verification (default: 0.7)
            monthly_budget: Teacher labeling budget per classroom/month (default: 100)
        """
        self.entropy_threshold = entropy_threshold
        self.monthly_budget = monthly_budget
        self.selection_history = []
    
    def compute_entropy(self, predictions: np.ndarray) -> np.ndarray:
        """
        Compute prediction entropy for uncertainty estimation.
        
        Formula (Paper 13 Algorithm 2, Line 5):
            Entropy(x_t) = -Σ P(y_i) log P(y_i)
        
        Args:
            predictions: Model predictions (softmax probabilities) shape (N, num_classes)
        
        Returns:
            entropy: Entropy values shape (N,)
        """
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        entropy = -np.sum(predictions * np.log(predictions + epsilon), axis=1)
        
        return entropy
    
    def select_uncertain_samples(
        self,
        predictions: np.ndarray,
        threshold: Optional[float] = None
    ) -> np.ndarray:
        """
        Select samples with high entropy (low confidence) for teacher verification.
        
        Paper 13 Algorithm 2 (Lines 6-10):
        IF Entropy(x_t) > H_min:
            // Low confidence: needs verification
            B_train.add(x_t)
        ELSE:
            // High confidence: auto-label
            D_auto.add(x_t, argmax(P))
        
        Args:
            predictions: Model predictions (softmax probabilities)
            threshold: Entropy threshold (default: use self.entropy_threshold)
        
        Returns:
            uncertain_indices: Indices of samples requiring verification
        """
        if threshold is None:
            threshold = self.entropy_threshold
        
        # Compute entropy
        entropy = self.compute_entropy(predictions)
        
        # Select high-entropy samples
        uncertain_indices = np.where(entropy > threshold)[0]
        
        return uncertain_indices
    
    def reduce_labeling_burden(
        self,
        model: nn.Module,
        unlabeled_data: torch.utils.data.DataLoader,
        budget: Optional[int] = None
    ) -> Tuple[List[int], np.ndarray]:
        """
        Reduce teacher labeling from 3000 frames/month to 450 (85% reduction).
        
        Paper 13 Section V.A:
        "This process reduces labelling from 3,000 frames/month (naive retraining)
         to 450 frames/month (85% reduction)."
        
        Args:
            model: Trained model for uncertainty estimation
            unlabeled_data: Unlabeled samples
            budget: Teacher labeling budget (default: use self.monthly_budget)
        
        Returns:
            (selected_indices, entropy_scores): Indices to label and their entropy scores
        """
        if budget is None:
            budget = self.monthly_budget
        
        model.eval()
        
        # Collect predictions for all unlabeled samples
        all_predictions = []
        all_indices = []
        
        with torch.no_grad():
            for batch_idx, (batch_x, _) in enumerate(unlabeled_data):
                outputs = model(batch_x)
                probs = torch.softmax(outputs, dim=1)
                all_predictions.append(probs.cpu().numpy())
                
                # Track original indices
                batch_size = len(batch_x)
                batch_indices = list(range(
                    batch_idx * batch_size,
                    batch_idx * batch_size + batch_size
                ))
                all_indices.extend(batch_indices)
        
        # Concatenate all predictions
        predictions = np.vstack(all_predictions)
        
        # Compute entropy
        entropy = self.compute_entropy(predictions)
        
        # Select top-k uncertain samples (limited by budget)
        uncertain_indices = self.select_uncertain_samples(predictions)
        
        # Sort by entropy (descending) and take top budget samples
        sorted_indices = uncertain_indices[np.argsort(-entropy[uncertain_indices])]
        selected_indices = sorted_indices[:budget].tolist()
        
        # Record selection
        self.selection_history.append({
            'total_samples': len(predictions),
            'uncertain_samples': len(uncertain_indices),
            'selected_samples': len(selected_indices),
            'reduction_rate': 1 - (len(selected_indices) / len(predictions))
        })
        
        return selected_indices, entropy[selected_indices]
    
    def validate_reduction(self, naive_labeling: int = 3000) -> Tuple[bool, str]:
        """
        Validate 85% labeling reduction.
        
        Args:
            naive_labeling: Naive retraining labeling requirement (default: 3000)
        
        Returns:
            (is_valid, message): Validation result
        """
        if not self.selection_history:
            return False, "❌ No selection history available"
        
        # Calculate average selected samples
        avg_selected = np.mean([
            h['selected_samples'] for h in self.selection_history
        ])
        
        # Calculate reduction rate
        reduction_rate = 1 - (avg_selected / naive_labeling)
        
        if reduction_rate >= 0.85:
            return True, f"✅ Labeling reduction validated: {reduction_rate*100:.1f}% (target: ≥85%)"
        else:
            return False, f"❌ Insufficient reduction: {reduction_rate*100:.1f}% (target: ≥85%)"
    
    def get_report(self) -> dict:
        """
        Generate active learning report.
        
        Returns:
            report: Dictionary with selection metrics
        """
        if not self.selection_history:
            return {'status': 'No selections made'}
        
        total_samples = sum(h['total_samples'] for h in self.selection_history)
        total_selected = sum(h['selected_samples'] for h in self.selection_history)
        avg_reduction = np.mean([h['reduction_rate'] for h in self.selection_history])
        
        return {
            'total_samples_processed': total_samples,
            'total_samples_selected': total_selected,
            'average_reduction_rate': avg_reduction,
            'target_reduction_rate': 0.85,
            'selection_history': self.selection_history
        }


# Validation test
if __name__ == "__main__":
    print("🎯 Active Learning Selector Validation Test")
    print("=" * 60)
    
    # Create dummy model and data
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(10, 5)
        
        def forward(self, x):
            return self.fc(x)
    
    model = SimpleModel()
    
    # Create dummy unlabeled data (3000 samples = naive labeling requirement)
    X = torch.randn(3000, 10)
    y = torch.randint(0, 5, (3000,))
    dataset = torch.utils.data.TensorDataset(X, y)
    loader = torch.utils.data.DataLoader(dataset, batch_size=100)
    
    # Initialize selector
    selector = ActiveLearningSelector(
        entropy_threshold=0.7,
        monthly_budget=450  # Target: 85% reduction from 3000
    )
    
    # Select uncertain samples
    print("\nSelecting uncertain samples for teacher verification...")
    selected_indices, entropy_scores = selector.reduce_labeling_burden(
        model=model,
        unlabeled_data=loader,
        budget=450
    )
    
    print(f"   Total samples: 3000")
    print(f"   Selected for labeling: {len(selected_indices)}")
    print(f"   Reduction: {(1 - len(selected_indices)/3000)*100:.1f}%")
    print(f"   Mean entropy of selected: {entropy_scores.mean():.3f}")
    
    # Validate reduction
    is_valid, message = selector.validate_reduction(naive_labeling=3000)
    print(f"\n{message}")
    
    # Generate report
    report = selector.get_report()
    print(f"\n📊 Active Learning Report:")
    print(f"   Total processed: {report['total_samples_processed']}")
    print(f"   Total selected: {report['total_samples_selected']}")
    print(f"   Average reduction: {report['average_reduction_rate']*100:.1f}%")
