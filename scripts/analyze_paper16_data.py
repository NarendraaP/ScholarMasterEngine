#!/usr/bin/env python3
"""
Paper 16: Statistical Analysis Script
======================================
Analyzes anonymized Likert datasets to reproduce paper statistics.

This script:
- Loads Phase 1 (Black Box) and Phase 2 (Glass Box) datasets
- Computes mean differences and standard deviations
- Calculates Pearson correlation coefficient
- Performs paired t-test for statistical significance
- Outputs LaTeX-formatted tables

SCOPE BOUNDARY: This script performs analysis ONLY on pre-collected,
anonymized datasets. It does NOT:
- Collect new data
- Access any PII
- Import any ML modules from the ScholarMaster core
"""

import json
import math
import os
from pathlib import Path
from typing import Dict, List, Tuple

# =============================================================================
# DATA LOADING
# =============================================================================

def load_dataset(filepath: str) -> Dict:
    """Load a Likert dataset JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_data_dir() -> Path:
    """Get the Paper 16 data directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "data" / "paper16"


# =============================================================================
# STATISTICAL FUNCTIONS (No External Dependencies)
# =============================================================================

def mean(values: List[float]) -> float:
    """Calculate arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def std_dev(values: List[float]) -> float:
    """Calculate sample standard deviation."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def pearson_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.
    
    r = Σ[(xi - x̄)(yi - ȳ)] / √[Σ(xi - x̄)² × Σ(yi - ȳ)²]
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    mean_x = mean(x)
    mean_y = mean(y)
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    
    sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def paired_t_test(before: List[float], after: List[float]) -> Tuple[float, str]:
    """
    Perform paired samples t-test.
    
    Returns (t-statistic, p-value significance level).
    Note: p-value is approximated as a significance threshold, not exact.
    """
    if len(before) != len(after) or len(before) < 2:
        return 0.0, "n/a"
    
    n = len(before)
    differences = [a - b for a, b in zip(after, before)]
    
    mean_diff = mean(differences)
    std_diff = std_dev(differences)
    
    if std_diff == 0:
        return float('inf'), "< 0.001"
    
    t_stat = mean_diff / (std_diff / math.sqrt(n))
    
    # Approximate p-value thresholds for two-tailed test
    # Using critical values for df ≈ 50
    abs_t = abs(t_stat)
    if abs_t > 3.5:
        p_level = "< 0.001"
    elif abs_t > 2.68:
        p_level = "< 0.01"
    elif abs_t > 2.01:
        p_level = "< 0.05"
    else:
        p_level = "> 0.05"
    
    return t_stat, p_level


def cohens_d(before: List[float], after: List[float]) -> float:
    """
    Calculate Cohen's d effect size for paired samples.
    
    d = mean_difference / pooled_std
    """
    if len(before) != len(after) or len(before) < 2:
        return 0.0
    
    mean_before = mean(before)
    mean_after = mean(after)
    mean_diff = mean_after - mean_before
    
    # Pooled standard deviation
    var_before = sum((x - mean_before) ** 2 for x in before) / (len(before) - 1)
    var_after = sum((x - mean_after) ** 2 for x in after) / (len(after) - 1)
    pooled_std = math.sqrt((var_before + var_after) / 2)
    
    if pooled_std == 0:
        return 0.0
    
    return mean_diff / pooled_std


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def extract_scores(responses: List[Dict], metric: str) -> List[float]:
    """Extract a specific metric from all responses."""
    return [r[metric] for r in responses if metric in r]


def analyze_phase_comparison(phase1_data: Dict, phase2_data: Dict) -> Dict:
    """
    Compare Phase 1 and Phase 2 datasets.
    
    Returns a dictionary of statistical results.
    """
    results = {}
    
    metrics = [
        ("trust_score", "Trust in System"),
        ("anxiety_score", "Anxiety Level"),
        ("utility_score", "Perceived Utility"),
        ("understanding_score", "Understanding of Data")
    ]
    
    for metric_key, metric_name in metrics:
        p1_scores = extract_scores(phase1_data["responses"], metric_key)
        p2_scores = extract_scores(phase2_data["responses"], metric_key)
        
        # Ensure paired samples (matching participant IDs)
        p1_by_id = {r["participant_id"]: r[metric_key] for r in phase1_data["responses"]}
        p2_by_id = {r["participant_id"]: r[metric_key] for r in phase2_data["responses"]}
        
        common_ids = set(p1_by_id.keys()) & set(p2_by_id.keys())
        paired_p1 = [p1_by_id[pid] for pid in sorted(common_ids)]
        paired_p2 = [p2_by_id[pid] for pid in sorted(common_ids)]
        
        t_stat, p_level = paired_t_test(paired_p1, paired_p2)
        d = cohens_d(paired_p1, paired_p2)
        
        results[metric_key] = {
            "name": metric_name,
            "phase1_mean": mean(p1_scores),
            "phase1_std": std_dev(p1_scores),
            "phase2_mean": mean(p2_scores),
            "phase2_std": std_dev(p2_scores),
            "delta": mean(p2_scores) - mean(p1_scores),
            "t_statistic": t_stat,
            "p_level": p_level,
            "cohens_d": d
        }
    
    return results


def analyze_attribution(phase2_data: Dict) -> Dict:
    """Analyze trust factor attribution from Phase 2."""
    if "responses" not in phase2_data:
        return {}
    
    attributions = {}
    total = 0
    
    for response in phase2_data["responses"]:
        if "trust_factor_attribution" in response:
            factor = response["trust_factor_attribution"]
            attributions[factor] = attributions.get(factor, 0) + 1
            total += 1
    
    # Convert to percentages
    return {
        factor: round((count / total) * 100, 1) if total > 0 else 0
        for factor, count in attributions.items()
    }


def calculate_visibility_correlation(phase2_data: Dict) -> float:
    """
    Calculate correlation between visibility (skeleton view usage) and trust.
    
    Uses binary visibility indicator: 1 if skeleton_view, 0 otherwise.
    """
    visibility_scores = []
    trust_scores = []
    
    for response in phase2_data["responses"]:
        if "trust_factor_attribution" in response and "trust_score" in response:
            visibility = 1.0 if response["trust_factor_attribution"] == "skeleton_view" else 0.0
            visibility_scores.append(visibility)
            trust_scores.append(response["trust_score"])
    
    return pearson_correlation(visibility_scores, trust_scores)


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def print_results_table(results: Dict):
    """Print results in a formatted table."""
    print("\n" + "=" * 80)
    print("PAPER 16 STATISTICAL ANALYSIS RESULTS")
    print("=" * 80)
    
    print("\n--- Phase Comparison ---")
    print(f"{'Metric':<25} {'Phase 1':<12} {'Phase 2':<12} {'Delta':<10} {'t-stat':<10} {'p':<10}")
    print("-" * 80)
    
    for metric_key, data in results.items():
        p1 = f"{data['phase1_mean']:.2f} ± {data['phase1_std']:.2f}"
        p2 = f"{data['phase2_mean']:.2f} ± {data['phase2_std']:.2f}"
        delta = f"{data['delta']:+.2f}"
        t = f"{data['t_statistic']:.2f}"
        p = data['p_level']
        
        print(f"{data['name']:<25} {p1:<12} {p2:<12} {delta:<10} {t:<10} {p:<10}")
    
    print()


def print_attribution(attribution: Dict):
    """Print attribution analysis."""
    print("\n--- Trust Factor Attribution (Phase 2) ---")
    print(f"{'Factor':<20} {'Percentage':<10}")
    print("-" * 30)
    
    # Sort by percentage descending
    for factor, pct in sorted(attribution.items(), key=lambda x: -x[1]):
        print(f"{factor:<20} {pct:.1f}%")


def print_latex_table(results: Dict):
    """Output LaTeX-formatted table for paper."""
    print("\n--- LaTeX Table (Copy for Paper) ---")
    print(r"\begin{table}[htbp]")
    print(r"\caption{Mean Student Sentiment Scores (1=Negative, 5=Positive)}")
    print(r"\begin{center}")
    print(r"\begin{tabular}{lccc}")
    print(r"\toprule")
    print(r"\textbf{Metric} & \textbf{Phase 1} & \textbf{Phase 2} & \textbf{Delta ($\Delta$)} \\")
    print(r"\midrule")
    
    for data in results.values():
        p1 = f"{data['phase1_mean']:.1f} $\\pm$ {data['phase1_std']:.1f}"
        p2 = f"\\textbf{{{data['phase2_mean']:.1f} $\\pm$ {data['phase2_std']:.1f}}}"
        delta = f"{data['delta']:+.1f}"
        print(f"{data['name']} & {p1} & {p2} & {delta} \\\\")
    
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{center}")
    print(r"\end{table}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run the complete analysis pipeline."""
    data_dir = get_data_dir()
    
    # Load datasets
    print("Loading datasets...")
    try:
        phase1 = load_dataset(data_dir / "likert_dataset_phase1.json")
        phase2 = load_dataset(data_dir / "likert_dataset_phase2.json")
    except FileNotFoundError as e:
        print(f"ERROR: Dataset not found: {e}")
        print(f"Expected location: {data_dir}")
        return 1
    
    print(f"Phase 1 responses: {len(phase1.get('responses', []))}")
    print(f"Phase 2 responses: {len(phase2.get('responses', []))}")
    
    # Run analysis
    results = analyze_phase_comparison(phase1, phase2)
    attribution = analyze_attribution(phase2)
    visibility_r = calculate_visibility_correlation(phase2)
    
    # Print results
    print_results_table(results)
    print_attribution(attribution)
    
    print(f"\n--- Visibility-Trust Correlation ---")
    print(f"Pearson r = {visibility_r:.2f}")
    print(f"(Paper reports r = 0.82)")
    
    # Effect size interpretation
    print("\n--- Effect Size Interpretation ---")
    for metric_key, data in results.items():
        d = data['cohens_d']
        if abs(d) >= 0.8:
            interpretation = "LARGE"
        elif abs(d) >= 0.5:
            interpretation = "MEDIUM"
        elif abs(d) >= 0.2:
            interpretation = "SMALL"
        else:
            interpretation = "NEGLIGIBLE"
        print(f"{data['name']}: Cohen's d = {d:.2f} ({interpretation})")
    
    # LaTeX output
    print_latex_table(results)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())
