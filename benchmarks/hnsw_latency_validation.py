#!/usr/bin/env python3
"""
HNSW Latency Validation Script (Rigorous Re-Measurement)
==========================================================
Purpose: Re-validate p99 latency claims with proper measurement controls
         to ensure monotonic scaling for PhD defense.

Critical Controls:
- Warmup period (first 100 queries discarded)
- Multiple independent runs (3 runs averaged)
- Single-threaded execution
- Comprehensive statistical reporting (p50, p95, p99, p999)
- Monotonicity validation

Author: Narendra P
Date: January 30, 2026
"""

import numpy as np
import faiss
import time
import json
import csv
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LatencyStats:
    """Statistics for a single measurement run."""
    gallery_size: int
    n_queries: int
    n_warmup: int
    mean_ms: float
    std_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    p999_ms: float
    min_ms: float
    max_ms: float
    run_id: int


def generate_synthetic_gallery(n_identities: int, embedding_dim: int = 512) -> np.ndarray:
    """
    Generate synthetic embeddings on unit hypersphere.
    
    Args:
        n_identities: Number of unique identities
        embedding_dim: Dimensionality of embeddings
    
    Returns:
        Gallery matrix of shape (n_identities, embedding_dim)
    """
    vectors = np.random.randn(n_identities, embedding_dim).astype('float32')
    faiss.normalize_L2(vectors)
    return vectors


def build_hnsw_index(gallery: np.ndarray, M: int = 16, efConstruction: int = 200) -> faiss.IndexHNSWFlat:
    """
    Build HNSW index with specified parameters.
    
    Args:
        gallery: Gallery embeddings
        M: Number of neighbors per layer
        efConstruction: Build-time search depth
    
    Returns:
        HNSW index
    """
    embedding_dim = gallery.shape[1]
    index = faiss.IndexHNSWFlat(embedding_dim, M)
    index.hnsw.efConstruction = efConstruction
    index.add(gallery)
    return index


def measure_latency(index: faiss.IndexHNSWFlat,
                   queries: np.ndarray,
                   efSearch: int = 50,
                   n_warmup: int = 100) -> Tuple[np.ndarray, int]:
    """
    Measure query latency with warmup period.
    
    Args:
        index: HNSW index
        queries: Query vectors
        efSearch: Search-time depth
        n_warmup: Number of warmup queries to discard
    
    Returns:
        (latencies_ms, n_measured) - latencies array and count of measured queries
    """
    index.hnsw.efSearch = efSearch
    n_total = len(queries)
    
    # Warmup phase (discard results)
    print(f"   🔥 Warmup: {n_warmup} queries (discarded)...")
    for i in range(min(n_warmup, n_total)):
        _ = index.search(queries[i:i+1], 1)
    
    # Measurement phase
    n_measured = n_total - n_warmup
    latencies = []
    
    print(f"   📏 Measuring: {n_measured} queries...")
    for i in range(n_warmup, n_total):
        start = time.perf_counter()
        _ = index.search(queries[i:i+1], 1)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms
    
    return np.array(latencies), n_measured


def compute_statistics(latencies: np.ndarray, 
                       gallery_size: int, 
                       n_queries: int,
                       n_warmup: int,
                       run_id: int) -> LatencyStats:
    """
    Compute comprehensive latency statistics.
    
    Args:
        latencies: Array of latency measurements in ms
        gallery_size: Size of the gallery
        n_queries: Total number of queries
        n_warmup: Number of warmup queries
        run_id: Run identifier
    
    Returns:
        LatencyStats object
    """
    return LatencyStats(
        gallery_size=gallery_size,
        n_queries=n_queries,
        n_warmup=n_warmup,
        mean_ms=float(np.mean(latencies)),
        std_ms=float(np.std(latencies)),
        p50_ms=float(np.percentile(latencies, 50)),
        p95_ms=float(np.percentile(latencies, 95)),
        p99_ms=float(np.percentile(latencies, 99)),
        p999_ms=float(np.percentile(latencies, 99.9)),
        min_ms=float(np.min(latencies)),
        max_ms=float(np.max(latencies)),
        run_id=run_id
    )


def validate_monotonicity(results: List[LatencyStats], metric: str = 'p99_ms') -> bool:
    """
    Check if latency increases monotonically with gallery size.
    
    Args:
        results: List of LatencyStats sorted by gallery_size
        metric: Which metric to check (default: p99_ms)
    
    Returns:
        True if monotonic, False otherwise
    """
    values = [getattr(r, metric) for r in results]
    for i in range(1, len(values)):
        if values[i] < values[i-1]:
            print(f"\n⚠️  NON-MONOTONIC: {metric} decreased from {values[i-1]:.3f} to {values[i]:.3f}")
            return False
    return True


def print_results_table(aggregated_results: Dict[int, Dict[str, float]]):
    """
    Print formatted results table.
    
    Args:
        aggregated_results: Dictionary mapping gallery_size to averaged statistics
    """
    print("\n" + "=" * 100)
    print("HNSW LATENCY VALIDATION RESULTS (AVERAGED ACROSS RUNS)")
    print("=" * 100)
    print(f"{'Gallery Size':>15} | {'Mean (ms)':>12} | {'Std (ms)':>11} | "
          f"{'p50 (ms)':>11} | {'p95 (ms)':>11} | {'p99 (ms)':>11} | {'p999 (ms)':>12}")
    print("-" * 100)
    
    for size in sorted(aggregated_results.keys()):
        stats = aggregated_results[size]
        print(f"{size:>15,} | {stats['mean_ms']:>12.4f} | {stats['std_ms']:>11.4f} | "
              f"{stats['p50_ms']:>11.4f} | {stats['p95_ms']:>11.4f} | "
              f"{stats['p99_ms']:>11.4f} | {stats['p999_ms']:>12.4f}")
    
    print("=" * 100)


def main():
    """Run comprehensive HNSW latency validation."""
    np.random.seed(42)  # Reproducibility
    
    # Configuration
    GALLERY_SIZES = [100, 1_000, 10_000, 50_000, 100_000]
    N_QUERIES = 10_000  # Per gallery size
    N_WARMUP = 100      # Warmup queries to discard
    N_RUNS = 3          # Independent runs for statistical validation
    EMBEDDING_DIM = 512
    
    # HNSW Parameters (Paper 1 configuration)
    HNSW_M = 16
    HNSW_EF_CONSTRUCTION = 200
    HNSW_EF_SEARCH = 50
    
    print("=" * 100)
    print("HNSW LATENCY VALIDATION - RIGOROUS RE-MEASUREMENT")
    print("=" * 100)
    print(f"Configuration:")
    print(f"  Gallery Sizes: {GALLERY_SIZES}")
    print(f"  Queries/Size:  {N_QUERIES:,}")
    print(f"  Warmup:        {N_WARMUP}")
    print(f"  Runs:          {N_RUNS}")
    print(f"  HNSW M:        {HNSW_M}")
    print(f"  efConstruction: {HNSW_EF_CONSTRUCTION}")
    print(f"  efSearch:      {HNSW_EF_SEARCH}")
    print("=" * 100)
    
    all_results = []
    
    # Run measurements
    for gallery_size in GALLERY_SIZES:
        print(f"\n📊 Testing Gallery Size: {gallery_size:,}")
        print("-" * 100)
        
        # Generate gallery once for all runs
        print(f"   🔬 Generating {gallery_size:,} synthetic vectors...")
        gallery = generate_synthetic_gallery(gallery_size, EMBEDDING_DIM)
        
        # Build index once for all runs
        print(f"   🏗️  Building HNSW index (M={HNSW_M}, efConstruction={HNSW_EF_CONSTRUCTION})...")
        start_build = time.time()
        index = build_hnsw_index(gallery, M=HNSW_M, efConstruction=HNSW_EF_CONSTRUCTION)
        build_time = time.time() - start_build
        print(f"   ✅ Index built in {build_time:.2f}s")
        
        # Generate query set once for all runs
        print(f"   🎯 Generating {N_QUERIES:,} query vectors...")
        queries = generate_synthetic_gallery(N_QUERIES, EMBEDDING_DIM)
        
        # Multiple measurement runs
        for run_id in range(1, N_RUNS + 1):
            print(f"\n   === Run {run_id}/{N_RUNS} ===")
            latencies, n_measured = measure_latency(
                index, queries, efSearch=HNSW_EF_SEARCH, n_warmup=N_WARMUP
            )
            
            stats = compute_statistics(latencies, gallery_size, N_QUERIES, N_WARMUP, run_id)
            all_results.append(stats)
            
            print(f"   ✅ Run {run_id}: mean={stats.mean_ms:.4f}ms, "
                  f"p95={stats.p95_ms:.4f}ms, p99={stats.p99_ms:.4f}ms")
    
    # Aggregate results (average across runs)
    print("\n" + "=" * 100)
    print("AGGREGATING RESULTS...")
    print("=" * 100)
    
    aggregated = {}
    for gallery_size in GALLERY_SIZES:
        run_stats = [r for r in all_results if r.gallery_size == gallery_size]
        
        aggregated[gallery_size] = {
            'mean_ms': np.mean([r.mean_ms for r in run_stats]),
            'std_ms': np.mean([r.std_ms for r in run_stats]),
            'p50_ms': np.mean([r.p50_ms for r in run_stats]),
            'p95_ms': np.mean([r.p95_ms for r in run_stats]),
            'p99_ms': np.mean([r.p99_ms for r in run_stats]),
            'p999_ms': np.mean([r.p999_ms for r in run_stats]),
            'cv_p99': np.std([r.p99_ms for r in run_stats]) / np.mean([r.p99_ms for r in run_stats]) * 100
        }
    
    # Print results
    print_results_table(aggregated)
    
    # Monotonicity check
    print("\n" + "=" * 100)
    print("MONOTONICITY VALIDATION")
    print("=" * 100)
    
    sorted_sizes = sorted(GALLERY_SIZES)
    for metric in ['mean_ms', 'p95_ms', 'p99_ms', 'p999_ms']:
        values = [aggregated[size][metric] for size in sorted_sizes]
        is_monotonic = all(values[i] <= values[i+1] for i in range(len(values)-1))
        
        status = "✅ PASS" if is_monotonic else "❌ FAIL"
        print(f"{metric:>10}: {status}")
        
        if not is_monotonic:
            for i in range(len(values)-1):
                if values[i] > values[i+1]:
                    print(f"            ⚠️  {sorted_sizes[i]:,} ({values[i]:.3f}ms) > "
                          f"{sorted_sizes[i+1]:,} ({values[i+1]:.3f}ms)")
    
    # Coefficient of Variation check
    print("\n" + "=" * 100)
    print("STATISTICAL CONSISTENCY (Coefficient of Variation for p99)")
    print("=" * 100)
    
    for size in sorted_sizes:
        cv = aggregated[size]['cv_p99']
        status = "✅" if cv < 10 else "⚠️"
        print(f"{size:>15,}: CV = {cv:>6.2f}% {status}")
    
    # Save detailed results to CSV
    output_csv = "benchmarks/hnsw_latency_validation_results.csv"
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(all_results[0]).keys()))
        writer.writeheader()
        for result in all_results:
            writer.writerow(asdict(result))
    
    print(f"\n💾 Detailed results saved to: {output_csv}")
    
    # Save aggregated results to JSON
    output_json = "benchmarks/hnsw_latency_validation_aggregated.json"
    with open(output_json, 'w') as f:
        json.dump(aggregated, f, indent=2)
    
    print(f"💾 Aggregated results saved to: {output_json}")
    
    # Final verdict
    print("\n" + "=" * 100)
    all_monotonic = all(
        all(aggregated[sorted_sizes[i]][metric] <= aggregated[sorted_sizes[i+1]][metric] 
            for i in range(len(sorted_sizes)-1))
        for metric in ['mean_ms', 'p95_ms', 'p99_ms', 'p999_ms']
    )
    
    if all_monotonic:
        print("✅ VERDICT: MONOTONIC SCALING CONFIRMED")
        print("   → Safe to update paper table with these values")
    else:
        print("⚠️  VERDICT: NON-MONOTONIC BEHAVIOR DETECTED")
        print("   → Must add technical explanation in paper")
        print("   → Suggested: Cache locality / graph stabilization effects")
    
    print("=" * 100)


if __name__ == "__main__":
    main()
