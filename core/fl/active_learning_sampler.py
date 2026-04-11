import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class ActiveLearningSampler:
    """
    Paper 13: Algorithm 2 (Active Learning Selection for Edge Nodes)
    Evaluates predictive entropy to determine if a generic inferred action 
    is ambiguous enough to require a Teacher's manual label verification.
    """
    def __init__(self, entropy_threshold: float = 0.8):
        self.H_min = entropy_threshold
        # Simulating a K=3 class problem (e.g. Raising Hand, Writing, Idle)
        self.num_classes = 3 
        
    def calculate_entropy(self, probabilities: np.ndarray) -> float:
        """ Eq (7): H(x) = -Sum(P * logP) """
        # Add small epsilon to prevent log(0)
        eps = 1e-9
        p = np.clip(probabilities, eps, 1.0)
        entropy = -np.sum(p * np.log(p))
        return entropy

    def process_inference_stream(self, num_samples: int = 1000):
        print("================================================================")
        print("Paper 13 MLOps: Teacher-in-the-Loop Active Learning")
        print(f"Entropy Threshold (H_min): {self.H_min}")
        print("================================================================\n")
        
        b_train = [] # Sent for Teacher Verification
        d_auto = []  # Auto-labeled (High Confidence)
        
        for _ in range(num_samples):
            # Simulate ML classification output probabilities
            raw_logits = np.random.randn(self.num_classes)
            # Softmax to get probabilities
            exp_logits = np.exp(raw_logits - np.max(raw_logits))
            probs = exp_logits / exp_logits.sum()
            
            # 1. Evaluate Predictive Entropy
            entropy = self.calculate_entropy(probs)
            
            # 2. Decision Logic
            predicted_class = np.argmax(probs)
            if entropy > self.H_min:
                # Ambiguous: e.g. [0.4, 0.35, 0.25] -> High Entropy
                b_train.append((probs, entropy))
            else:
                # Certain: e.g. [0.9, 0.05, 0.05] -> Low Entropy
                d_auto.append((probs, predicted_class))
                
        # 3. Output Efficacy Metrics
        total = len(b_train) + len(d_auto)
        reduction_pct = 100 * (1.0 - (len(b_train) / total))
        
        print(f"Processed {total} incoming abstractions.")
        print(f" -> Auto-Labeled (High Confidence):   {len(d_auto):>4} frames")
        print(f" -> Flagged for Teacher Verification: {len(b_train):>4} frames")
        print("-" * 64)
        print(f"Labeling Reduction Efficiency: {reduction_pct:.1f}%")
        
        if reduction_pct >= 80.0:
            print("Status: SUCCESS (Achieved > 80% labeling reduction target)")
        else:
            print("Status: WARNING (Entropy threshold may need tuning)")
        
        print("\n================================================================")
        return b_train, d_auto
        
if __name__ == "__main__":
    # Simulate a stream of 3000 inference events
    # Max entropy for 3 classes is ~1.098. To flag only the ~15% MOST uncertain, 
    # we need a very high threshold (e.g. 1.04)
    sampler = ActiveLearningSampler(entropy_threshold=1.04)
    sampler.process_inference_stream(num_samples=3000)
