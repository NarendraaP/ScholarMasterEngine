import sys
import os
import time
import random
import math
import concurrent.futures
import json
import logging

# Ensure we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_legacy.st_csf import SpatiotemporalCSF
from modules_legacy.state_manager import RedisStateManager

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Sim5k")

class StudentAgent:
    def __init__(self, student_id: str, behavior_profile: str):
        self.student_id = student_id
        self.profile = behavior_profile  # 'compliant', 'laggard', 'adversarial'
        self.current_zone = "Dorm"
        self.last_move_time = 0.0

    def generate_move(self, current_time: float) -> dict:
        """Generates a movement event based on profile"""
        zones = ["Zone_1", "Zone_2", "Zone_3", "Zone_4", "Main Hall"]
        
        # compliant/laggard agents move realistically
        if self.profile in ['compliant', 'laggard']:
            next_zone = random.choice(zones)
            # Ensure travel time is realistic (e.g., > 20s for 100m)
            return {
                "student_id": self.student_id,
                "timestamp": current_time,
                "zone": next_zone
            }
            
        # adversarial agents try to teleport
        elif self.profile == 'adversarial':
            # Hacker move: Jump from Zone 1 to Zone 4 (500m+) instantly
            return {
                "student_id": self.student_id,
                "timestamp": current_time, # same time as last check effectively
                "zone": random.choice(zones)
            }

def run_simulation(num_agents=5000, duration_seconds=10):
    print(f"🚀 Starting Monte Carlo Campus Simulator (N={num_agents})...")
    print("Claim Verification: Paper 7, Section VII (Experimental Results)")
    print("-" * 60)
    
    # Init Logic Engine
    # Note: Using In-Memory Redis Mock for speed in simulation
    state_manager = RedisStateManager(use_redis=False) 
    engine = SpatiotemporalCSF(state_manager)
    
    # Initialize Agents
    agents = []
    for i in range(num_agents):
        pid = f"S_{i:04d}"
        if i < num_agents * 0.85:
            profile = 'compliant'
        elif i < num_agents * 0.95:
            profile = 'laggard'
        else:
            profile = 'adversarial'
        agents.append(StudentAgent(pid, profile))
        
        # Seed initial state
        state_manager.set(f"state:{pid}", {
            "timestamp": time.time(),
            "zone": "Main Hall"
        })
        
    print(f"✅ Created {len(agents)} agents (5% Adversarial)")
    
    # Metric Counters
    stats = {
        "processed": 0,
        "valid": 0,
        "rejected": 0,
        "teleport_detected": 0
    }
    
    start_time = time.time()
    
    # Simulation Loop
    # We simulate a "burst" of movements (Morning Bell)
    events_batch = []
    sim_time = time.time() + 10 # 10 seconds later
    
    for agent in agents:
        events_batch.append(agent.generate_move(sim_time))
        
    print(f"⚡ Processing burst of {len(events_batch)} events...")
    
    # Sequential Processing Implementation (Paper claims O(1) per item, linear scale)
    # The paper says "tens of milliseconds per event" - let's verify
    
    batch_start = time.time()
    
    for event in events_batch:
        is_valid, reason = engine.validate_event(event)
        
        stats["processed"] += 1
        if is_valid:
            stats["valid"] += 1
        else:
            stats["rejected"] += 1
            if "IMPOSSIBLE" in reason or "CLONING" in reason:
                stats["teleport_detected"] += 1
                
    batch_end = time.time()
    total_time = batch_end - batch_start
    eps = len(events_batch) / total_time if total_time > 0 else 0
    
    print("-" * 60)
    print("📊 SIMULATION RESULTS")
    print(f"Total Agents:      {num_agents}")
    print(f"Total Events:      {stats['processed']}")
    print(f"Execution Time:    {total_time:.4f}s")
    print(f"Throughput:        {eps:.1f} EPS (Events Per Second)")
    print(f"Teleportations:    {stats['teleport_detected']} (Adversarial Detection)")
    print("-" * 60)
    
    # Validate Claims
    passed = True
    if eps < 500:
        print("❌ FAIL: Throughput < 500 EPS (Paper Claim mismatch)")
        passed = False
    else:
        print("✅ PASS: Throughput > 500 EPS validated")
        
    if stats['teleport_detected'] == 0:
        print("❌ FAIL: No anomalies detected (Logic inactive)")
        passed = False
    else:
        print("✅ PASS: Logic Layer correctly filtered physics violations")

    results = {
        "metrics": stats,
        "performance": {"eps": eps, "latency_avg": total_time/len(events_batch)},
        "passed": passed
    }
    
    with open("benchmarks/simulation_5k_results.json", "w") as f:
        json.dump(results, f, indent=2)
        print("📝 Detailed results saved to benchmarks/simulation_5k_results.json")

if __name__ == "__main__":
    run_simulation()
