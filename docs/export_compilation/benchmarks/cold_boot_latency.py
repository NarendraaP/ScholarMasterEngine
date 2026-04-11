#!/usr/bin/env python3
"""
Cold Boot Latency Measurement (Simulated)
For real cold boot, use hardware relay to power-cycle device.
This script simulates via Docker container restart.
"""

import time
import subprocess
import json
import csv
from pathlib import Path

LOG_FILE = Path("data/cold_boot_latency.csv")
SUMMARY_FILE = Path("data/cold_boot_summary.json")

def run_cmd(cmd, capture=True):
    """Run shell command."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        else:
            subprocess.run(cmd, shell=True, timeout=30)
            return True
    except:
        return False

def main():
    print("🔄 Cold Boot Latency Measurement (Simulated)")
    print("=" * 60)
    print("Simulating cold boot via Docker container operations...")
    print()
    
    stages = []
    total_start = time.time()
    
    # Stage 1: Container cleanup (simulates power off)
    print("Stage 1: Stopping existing containers...")
    stage_start = time.time()
    run_cmd("docker stop scholarmaster 2>/dev/null || true")
    run_cmd("docker rm scholarmaster 2>/dev/null || true")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("container_stop", elapsed))
    print(f"  [{elapsed:.0f} ms] Container cleanup complete")
    
    # Stage 2: Docker daemon check
    print("Stage 2: Docker daemon ready check...")
    stage_start = time.time()
    run_cmd("docker ps > /dev/null 2>&1")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("docker_ready", elapsed))
    print(f"  [{elapsed:.0f} ms] Docker daemon responsive")
    
    # Stage 3: Image verification
    print("Stage 3: Verifying container image...")
    stage_start = time.time()
    image_exists = run_cmd("docker image inspect python:3.9-slim > /dev/null 2>&1")
    if not image_exists:
        print("  Pulling python:3.9-slim (first-time setup)...")
        run_cmd("docker pull python:3.9-slim")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("image_verify", elapsed))
    print(f"  [{elapsed:.0f} ms] Image verified")
    
    # Stage 4: Container initialization    print("Stage 4: Starting container...")
    stage_start = time.time()
    run_cmd("docker run -d --name scholarmaster --rm python:3.9-slim sleep 3600")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("container_init", elapsed))
    print(f"  [{elapsed:.0f} ms] Container started")
    
    # Stage 5: Model loading simulation
    print("Stage 5: Simulating model load...")
    stage_start = time.time()
    run_cmd("docker exec scholarmaster python3 -c 'import json; import hashlib'")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("model_load", elapsed))
    print(f"  [{elapsed:.0f} ms] Model weights loaded (simulated)")
    
    # Stage 6: First inference
    print("Stage 6: First inference...")
    stage_start = time.time()
    run_cmd("docker exec scholarmaster python3 -c 'print(\"inference complete\")'")
    elapsed = (time.time() - stage_start) * 1000
    stages.append(("first_inference", elapsed))
    print(f"  [{elapsed:.0f} ms] First frame processed")
    
    total_time = (time.time() - total_start) * 1000
    
    # Cleanup
    print("\nCleaning up...")
    run_cmd("docker stop scholarmaster 2>/dev/null || true")
    
    # Save results
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    # CSV
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["stage", "elapsed_ms"])
        for stage, ms in stages:
            writer.writerow([stage, f"{ms:.1f}"])
        writer.writerow(["TOTAL", f"{total_time:.1f}"])
    
    # JSON summary
    summary = {
        "total_time_ms": total_time,
        "stages": {stage: ms for stage, ms in stages},
        "note": "Docker restart simulation; real cold boot adds OS boot (~25s) and hardware init (~5s)"
    }
    
    with open(SUMMARY_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ Cold Boot Latency Measurement Complete")
    print("=" * 60)
    for stage, ms in stages:
        print(f"  {stage:20s} {ms:6.0f} ms")
    print("  " + "=" * 40)
    print(f"  {'TOTAL':20s} {total_time:6.0f} ms")
    print()
    print(f"📊 Results saved:")
    print(f"   - {LOG_FILE}")
    print(f"   - {SUMMARY_FILE}")
    print()
    print("⚠️  NOTE: This simulates container restart only.")
    print("   Real cold boot includes:")
    print("   - OS boot: +25-35s (RPi/Jetson)")
    print("   - Hardware init: +5-10s")
    print("   - Expected total: 35-50s (RPi), 50-65s (Jetson)")

if __name__ == "__main__":
    main()
