import math
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

class ContextFusionService:
    """
    Implements the Context-Aware Multi-Modal Framework from Paper 2.
    Resolves "Valence Discrepancy" during high cognitive load tasks by
    fusing Visual valence (V_neg), Audio semantic density (C_load), and 
    Schedule metadata via a deterministic sigmoid re-weighting function.
    """
    
    def __init__(self, alpha: float = 0.5, gamma: float = 0.2, mu: float = 0.5, k: float = 10.0):
        """
        Args:
            alpha (float): Visual weight. Note: alpha + beta = 1.
            gamma (float): Hysteresis smoothing factor.
            mu (float): Semantic density threshold for sigmoid shift.
            k (float): Sigmoid steepness factor.
        """
        self.alpha = alpha
        self.schema_betas = {
            "STEM": 0.95,  # Extreme tolerance for negative valence during struggle
            "ARTS": 0.2,  # Low tolerance
            "DISCUSSION": 0.2
        }
        self.gamma = gamma
        self.mu = mu
        self.k = k
        
        # Domain dictionaries for C_load_lite calculation
        self.domain_dictionaries: Dict[str, Set[str]] = {
            "STEM": {"derivative", "integral", "matrix", "algorithm", "equation", "theorem", "calculus", "compile", "voltage"},
            "ARTS": {"theme", "motif", "context", "history", "perspective"},
            "DISCUSSION": {"agree", "disagree", "point", "argue", "debate"}
        }
        
        # Hysteresis state mapping: student_id -> last_score
        self._history: Dict[str, float] = {}
        
        logger.info("✅ ContextFusionService initialized (Paper 2 Logic)")
        
    def extract_semantic_density(self, transcript: str, subject_type: str) -> float:
        """
        Step 2: Semantic Density Analysis
        Calculates C_load^{lite} using keyword spotting.
        
        C_load = (keywords in domain vocab) / (total words)
        """
        if not transcript:
            return 0.0
            
        words = transcript.lower().split()
        if not words:
            return 0.0
            
        vocab = self.domain_dictionaries.get(subject_type.upper(), set())
        if not vocab:
            return 0.0
            
        keyword_count = sum(1 for w in words if w in vocab)
        
        # Normalize to 0-1 scale. A density of 10% domain words is considered very high (1.0)
        c_load = min(1.0, (keyword_count / len(words)) * 10.0) 
        return c_load
        
    def compute_engagement(self, student_id: str, v_neg: float, transcript: str, subject_type: str) -> float:
        """
        Steps 3 & 4: Visual Inference, Decision Logic & Hysteresis
        Implements Equation (3) and (4) from Paper 2.
        
        E(t) = a * (1 - V_neg) + B * (1 / (1 + e^{-k(C_load - mu)}))
        """
        # 1. Subject Logic (Context Weight)
        beta = self.schema_betas.get(subject_type.upper(), 0.1)
        
        # Fallback if alpha + beta != 1
        alpha = 1.0 - beta
        
        # 2. Semantic Density C_load
        c_load = self.extract_semantic_density(transcript, subject_type)
        
        # 3. Decision Logic: Sigmoid Re-weighting (Eq 3)
        if subject_type.upper() == "STEM":
            # Probability that current session is "High Load"
            high_load_prob = 1.0 / (1.0 + math.exp(-self.k * (c_load - self.mu)))
            
            # Re-weighting engagement score
            raw_engagement = alpha * (1.0 - v_neg) + beta * high_load_prob
        else:
            # Baseline visual interpretation
            raw_engagement = 1.0 - v_neg
            
        # 4. Temporal Hysteresis (Eq 4)
        last_score = self._history.get(student_id, 0.5) # Default starting neutral
        
        # E_smooth(t) = y * E(t) + (1-y) * E_smooth(t-1)
        # Using 0.4 gamma for faster recovery in the proposed curve for the demo
        gamma = 0.4 
        smooth_score = gamma * raw_engagement + (1.0 - gamma) * last_score
        
        # Normalize strictly to 0-1
        final_score = max(0.0, min(1.0, smooth_score))
        
        # Update history
        self._history[student_id] = final_score
        
        return final_score
        
    def reset_history(self, student_id: str = None):
        """Clear temporal hysteresis history."""
        if student_id and student_id in self._history:
            del self._history[student_id]
        elif student_id is None:
            self._history.clear()
