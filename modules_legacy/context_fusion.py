"""
Context-Aware Engagement Fusion Module (Paper 2)
================================================
This module implements the context-aware engagement inference logic
with semantic keyword detection and affect re-weighting.

Status: Experimental validation - ready for soft-integration
"""

import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ContextFusionConfig:
    """Configuration for context fusion"""
    enable_fusion: bool = False  # Feature flag
    stem_keywords: list = None
    threshold_mu: float = 0.5
    steepness_k: float = 5.0
    alpha: float = 0.6  # Visual weight
    beta: float = 0.4   # Context weight
    
    def __post_init__(self):
        if self.stem_keywords is None:
            self.stem_keywords = [
                "integral", "derivative", "matrix", "algorithm",
                "calculus", "differential", "computation", "proof",
                "theorem", "equation", "function", "variable"
            ]

class ContextFusionEngine:
    """
    Implements Algorithm 1 from Paper 2:
    Context-Aware Affect Re-weighting
    """
    
    def __init__(self, config: Optional[ContextFusionConfig] = None):
        self.config = config or ContextFusionConfig()
        self.logger = logging.getLogger(__name__)
        
    def calculate_semantic_density(self, transcript: str) -> float:
        """
        Calculate semantic density (C_load) from transcript.
        
        Args:
            transcript: Text from audio transcription
            
        Returns:
            C_load: Semantic density score [0, 1]
        """
        if not transcript:
            return 0.0
            
        words = transcript.lower().split()
        if not words:
            return 0.0
            
        # Count STEM keywords
        keyword_count = sum(1 for word in words if word in self.config.stem_keywords)
        
        # Calculate density
        c_load = keyword_count / len(words)
        
        return min(c_load, 1.0)  # Clamp to [0, 1]
    
    def apply_sigmoid_reweighting(self, c_load: float) -> float:
        """
        Apply sigmoid activation for smooth mode switching.
        
        Args:
            c_load: Semantic density
            
        Returns:
            Sigmoid output [0, 1]
        """
        import math
        
        # Equation from Paper 2:
        # sigmoid = 1 / (1 + exp(-k(C_load - mu)))
        exponent = -self.config.steepness_k * (c_load - self.config.threshold_mu)
        return 1.0 / (1.0 + math.exp(exponent))
    
    def compute_engagement_score(
        self,
        v_neg: float,
        transcript: str,
        subject_type: str = "STEM"
    ) -> Tuple[float, Dict]:
        """
        Main fusion function - implements Algorithm 1.
        
        Args:
            v_neg: Probability of negative valence [0, 1]
            transcript: Audio transcription text
            subject_type: Subject type ("STEM" or "ARTS")
            
        Returns:
            Tuple of (engagement_score, debug_info)
        """
        # Step 1: Calculate semantic density
        c_load = self.calculate_semantic_density(transcript)
        
        # Step 2: Determine if re-weighting should apply
        should_reweight = (subject_type == "STEM" and c_load > 0)
        
        # Step 3: Calculate engagement score
        if should_reweight:
            # Apply context-aware re-weighting (Equation 3 from Paper 2)
            # E(t) = α(1 - V_neg) + β * sigmoid(C_load)
            
            sigmoid_term = self.apply_sigmoid_reweighting(c_load)
            engagement = (
                self.config.alpha * (1 - v_neg) + 
                self.config.beta * sigmoid_term
            )
            
            baseline_engagement = 1 - v_neg  # What it would be without context
            
        else:
            # Standard visual-only inference
            engagement = 1 - v_neg
            baseline_engagement = engagement
            sigmoid_term = 0.0
        
        # Clamp to [0, 1]
        engagement = max(0.0, min(1.0, engagement))
        
        # Debug info for logging/visualization
        debug_info = {
            "v_neg": v_neg,
            "c_load": c_load,
            "sigmoid": sigmoid_term,
            "baseline_engagement": baseline_engagement,
            "final_engagement": engagement,
            "reweighted": should_reweight,
            "transcript_preview": transcript[:50] if transcript else ""
        }
        
        return engagement, debug_info


def demo_context_fusion(
    v_neg: float,
    transcript: str,
    subject_type: str = "STEM",
    verbose: bool = True
) -> float:
    """
    Convenience function for demo/testing purposes.
    
    This is the function called by both:
    - scripts/demo_paper2_context_fusion.py (for validation)
    - modules_legacy/master_engine.py (when flag enabled)
    
    Args:
        v_neg: Negative valence probability
        transcript: Audio transcript
        subject_type: Subject category
        verbose: Print debug logs
        
    Returns:
        Final engagement score
    """
    config = ContextFusionConfig(enable_fusion=True)
    engine = ContextFusionEngine(config)
    
    engagement, debug_info = engine.compute_engagement_score(
        v_neg, transcript, subject_type
    )
    
    if verbose:
        print(f"[FUSION] Context-Aware Engagement Inference:")
        print(f"  V_neg: {v_neg:.2f}")
        print(f"  C_load: {debug_info['c_load']:.2f}")
        print(f"  Baseline: {debug_info['baseline_engagement']:.2f}")
        print(f"  Re-weighted: {engagement:.2f}")
        if debug_info['reweighted']:
            print(f"  ✓ Productive struggle adjustment applied")
    
    return engagement


# Example usage
if __name__ == "__main__":
    print("Testing Context Fusion Engine\n" + "="*50)
    
    # Test Case 1: High cognitive load (should boost score)
    print("\nTest Case 1: Negative expression during calculus discussion")
    score = demo_context_fusion(
        v_neg=0.72,  # Frowning
        transcript="Today we will discuss the integral of this complex function",
        subject_type="STEM"
    )
    print(f"Final Score: {score:.2f}\n")
    
    # Test Case 2: No context (standard inference)
    print("\nTest Case 2: Negative expression during casual chat")
    score = demo_context_fusion(
        v_neg=0.72,
        transcript="Let's take a break now",
        subject_type="STEM"
    )
    print(f"Final Score: {score:.2f}\n")
    
    # Test Case 3: Non-STEM subject
    print("\nTest Case 3: Arts class (no STEM keywords)")
    score = demo_context_fusion(
        v_neg=0.72,
        transcript="Discuss the artistic movements of the renaissance period",
        subject_type="ARTS"
    )
    print(f"Final Score: {score:.2f}")
