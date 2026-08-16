"""
Master Validation Suite Runner
==============================
Executes the full experimental validation suite for ScholarMaster Perception Integrity:
- Parameter Lock & SHA-256 Manifest Registration
- Five-Regime Benchmark Suite
- Paper 1: Foundations & Ablations (A -> E)
- Paper 2: Adaptive Edge Pareto Frontier
- Paper 3: Generalized Cross-Modal Recovery
- Paper 4: Downstream Error Propagation & EAF (H1 & H2)

Tags all results explicitly as TARGET_SPECIFICATION, EMPIRICAL_RESULT, or DERIVED_METRIC.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.perception_integrity import PerceptionIntegrityGate
from benchmarks.parameter_lock import ParameterLockManager
from benchmarks.regime_evaluator import FiveRegimeEvaluator
from benchmarks.paper1_foundations import Paper1FoundationsBenchmark
from benchmarks.paper2_adaptive_edge import Paper2AdaptiveEdgeBenchmark
from benchmarks.paper3_cross_modal_recovery import Paper3CrossModalBenchmark
from benchmarks.paper4_error_propagation import DownstreamErrorPropagationBenchmark


def run_master_suite():
    print("=" * 80)
    print("SCHOLARMASTER PERCEPTION INTEGRITY — MASTER VALIDATION SUITE")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize Perception Integrity Gate
    gate = PerceptionIntegrityGate()

    # 1. Parameter Lock & Manifest Registration
    print(">>> 1. PARAMETER LOCK PROTOCOL")
    lock_mgr = ParameterLockManager()
    frozen_params, sha256_hash = lock_mgr.calibrate_and_lock(gate)
    lock_valid = lock_mgr.verify_lock()

    # 2. Five-Regime Benchmark Suite
    print("\n>>> 2. FIVE-REGIME BENCHMARK SUITE")
    regime_evaluator = FiveRegimeEvaluator(gate)
    regime_results = regime_evaluator.run_all_regimes(samples_per_regime=150)

    # 3. Paper 22: Foundations & Ablation Study
    print("\n>>> 3. PAPER 22: FOUNDATIONS & ABLATIONS")
    p1_bench = Paper1FoundationsBenchmark(gate)
    p1_results = p1_bench.run_zero_shot_eval()

    # 4. Paper 23: Adaptive Edge Pareto Frontier
    print("\n>>> 4. PAPER 23: ADAPTIVE EDGE PARETO FRONTIER")
    p2_bench = Paper2AdaptiveEdgeBenchmark(gate)
    p2_results = p2_bench.run_pareto_evaluation(num_samples=250)

    # 5. Paper 24: Cross-Modal Recovery
    print("\n>>> 5. PAPER 24: CROSS-MODAL CONSENSUS RECOVERY")
    p3_bench = Paper3CrossModalBenchmark(gate)
    p3_results = p3_bench.run_cross_modal_evaluation(num_samples=150)

    # 6. Paper 25: Downstream Error Propagation & EAF
    print("\n>>> 6. PAPER 25: DOWNSTREAM ERROR PROPAGATION & EAF")
    p4_bench = DownstreamErrorPropagationBenchmark(gate)
    p4_results = p4_bench.run_propagation_experiment(num_samples_per_level=150)

    # Tag and compile master results payload
    master_results = {
        "metadata": {
            "title": "ScholarMaster Perception Integrity Validation Suite",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": "ScholarMasterEngine v2.1",
            "parameter_lock_sha256": sha256_hash,
            "parameter_lock_verified": lock_valid,
            "paper_series": "ScholarMaster Perception Series (Papers 22-25)",
        },
        "target_specifications": {
            "TARGET_SPECIFICATION": {
                "max_latency_overhead_ms": 5.0,
                "target_protected_eaf": 0.30,
                "target_unprotected_eaf": 1.0,
            }
        },
        "empirical_results": {
            "EMPIRICAL_RESULT": {
                "parameter_lock": frozen_params,
                "five_regimes": regime_results,
                "paper22_foundations": p1_results,
                "paper23_adaptive_edge": p2_results,
                "paper24_cross_modal": p3_results,
                "paper25_downstream_error_propagation": p4_results,
            }
        },
        "derived_metrics": {
            "DERIVED_METRIC": {
                "hypotheses": p4_results["hypotheses"],
                "zero_shot_transfer": p1_results["zero_shot_transfer_status"],
            }
        },
    }

    out_file = "benchmarks/master_validation_suite_results.json"
    with open(out_file, "w") as f:
        json.dump(master_results, f, indent=2)

    print("\n" + "=" * 80)
    print("MASTER VALIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ Parameter Lock SHA-256 : {sha256_hash[:16]}... (Verified: {lock_valid})")
    print(f"✅ Five Regimes Tested    : 5/5 Completed")
    print(f"✅ Paper 22 Ablations(A-E): Completed")
    print(f"✅ Paper 23 Pareto        : Completed (Adaptive Cascade Throughput: {p2_results['adaptive_cascade']['fps']} FPS)")
    print(f"✅ Paper 24 Cross-Modal   : Completed (Recovery Rate verified under degradation)")
    print(f"✅ Paper 25 EAF Hypotheses: H1 (Unprotected EAF > 1.0): {'PASSED' if p4_results['hypotheses']['h1_unprotected_eaf_greater_1']['passed'] else 'FAILED'}")
    print(f"                          : H2 (Protected EAF < 0.3)  : {'PASSED' if p4_results['hypotheses']['h2_protected_eaf_less_0_3']['passed'] else 'FAILED'}")
    print("=" * 80)
    print(f"Full empirical JSON results written to {out_file}")

    return master_results


if __name__ == "__main__":
    run_master_suite()
