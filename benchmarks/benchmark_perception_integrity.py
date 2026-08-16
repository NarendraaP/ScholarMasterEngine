"""
Perception Integrity Benchmark Script
====================================
Measures processing latency, throughput, risk calibration accuracy, and
cascade decision routing distribution under clean and degraded stream conditions.
"""

import time
import json
import numpy as np

from core.perception_integrity import (
    SensorInputPacket,
    PerceptionIntegrityGate,
    CascadeDecision,
)


def run_benchmark(num_frames: int = 1000):
    print("=" * 80)
    print(f"RUNNING PERCEPTION INTEGRITY BENCHMARK ({num_frames} FRAMES)")
    print("=" * 80)

    gate = PerceptionIntegrityGate()

    # Generate synthetic frames
    clean_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    noisy_frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Blurry/black frame

    latencies = []
    decisions = {d: 0 for d in CascadeDecision}

    for i in range(num_frames):
        # 80% clean frames, 20% corrupted / noisy frames
        is_clean = (i % 5 != 0)

        frame = clean_frame if is_clean else noisy_frame
        conf = [0.92] if is_clean else [0.35]
        kps = [np.zeros((17, 3))] if is_clean else []
        audio = 50.0 if is_clean else 92.0

        t0 = time.perf_counter()
        packet = gate.process_frame(
            frame=frame,
            keypoints=kps,
            face_confidences=conf,
            audio_db=audio,
            zone_id="Bench_Zone",
        )
        t1 = time.perf_counter()

        latency_ms = (t1 - t0) * 1000.0
        latencies.append(latency_ms)
        decisions[packet.decision] += 1

    mean_lat = np.mean(latencies)
    std_lat = np.std(latencies)
    p50_lat = np.percentile(latencies, 50)
    p95_lat = np.percentile(latencies, 95)
    p99_lat = np.percentile(latencies, 99)

    print("\n--- LATENCY OVERHEAD BENCHMARK ---")
    print(f"Total Frames Processed: {num_frames}")
    print(f"Mean Latency          : {mean_lat:.3f} ms")
    print(f"Std Dev               : {std_lat:.3f} ms")
    print(f"P50 Latency           : {p50_lat:.3f} ms")
    print(f"P95 Latency           : {p95_lat:.3f} ms")
    print(f"P99 Latency           : {p99_lat:.3f} ms")
    print(f"Throughput (FPS)      : {1000.0 / mean_lat:.1f} FPS")

    print("\n--- CASCADE ROUTING DISTRIBUTION ---")
    for decision, count in decisions.items():
        pct = (count / num_frames) * 100.0
        print(f"{decision.name:<10}: {count:5d} ({pct:5.1f}%)")

    latency_pass = mean_lat <= 5.0
    print("\n--- VERIFICATION STATUS ---")
    print(f"Latency Constraint (< 5.0 ms): {'✅ PASSED' if latency_pass else '❌ FAILED'}")

    results = {
        "num_frames": num_frames,
        "mean_latency_ms": round(float(mean_lat), 4),
        "p95_latency_ms": round(float(p95_lat), 4),
        "p99_latency_ms": round(float(p99_lat), 4),
        "throughput_fps": round(float(1000.0 / mean_lat), 2),
        "decisions": {d.name: c for d, c in decisions.items()},
        "passed": bool(latency_pass),
    }

    return results


if __name__ == "__main__":
    results = run_benchmark()
    with open("benchmarks/perception_integrity_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to benchmarks/perception_integrity_benchmark_results.json")
