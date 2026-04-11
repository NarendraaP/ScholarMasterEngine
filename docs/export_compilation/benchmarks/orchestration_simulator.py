import sys
import os
import json
import time

# Mock environment for standalone run
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_legacy.governance import GovernanceEngine, SystemState

# --- SIMULATION CONFIG ---
DURATION_MINUTES = 60
FPS = 30
TOTAL_FRAMES = DURATION_MINUTES * 60 * FPS

# Lecture Phases (Minute ranges)
PHASES = [
    {"name": "Attendance", "start": 0, "end": 10, "is_critical": True},
    {"name": "Video",      "start": 10, "end": 40, "is_critical": False},
    {"name": "Q&A",        "start": 40, "end": 55, "is_critical": True},
    {"name": "Dismissal",  "start": 55, "end": 60, "is_critical": False}
]

def run_simulation():
    print("🚀 Starting Orchestration Simulator (60-min Lecture)...")
    
    gov = GovernanceEngine(max_captures_per_day=500000) # Uncap for pure IRG test
    
    # Validation Metrics Collectors
    timeline = []
    
    # We will simulate step-by-step but accelerated
    # Each "step" represents 1 minute of activity for speed
    
    for minute_idx in range(DURATION_MINUTES):
        # Determine Phase
        current_phase = "Unknown"
        is_critical = False
        for p in PHASES:
            if p["start"] <= minute_idx < p["end"]:
                current_phase = p["name"]
                is_critical = p["is_critical"]
                break
        
        # Simulate Context Factors
        # Random engagement spikes during Q&A
        is_speaking = False
        hand_raised = False
        
        if current_phase == "Q&A":
            is_speaking = True # Lots of talking
            hand_raised = True
        elif current_phase == "Attendance":
            hand_raised = True # Checking presence
            
        context_state = {
            "phase": current_phase,
            "is_speaking": is_speaking,
            "hand_raised": hand_raised
        }
        
        # Run Governance Logic (Simulate 1 frame decision reused for the minute)
        strategy = gov.get_inference_strategy(context_state)
        
        # Log Timeline State
        state_entry = {
            "minute": minute_idx,
            "phase": current_phase,
            "active_modules": [m for m, active in strategy.items() if active]
        }
        timeline.append(state_entry)
        
        # Aggregate Metrics based on this minute's decision (projected to whole minute)
        # Note: In real engine, this happens 30 times a second.
        # Here we just count it as "1 minute block of cycles"
        frames_in_minute = 60 * FPS
        
        # Manually inject stats into Governance Engine for reporting
        for _ in range(frames_in_minute):
             if strategy["enable_face"]:
                 gov.metrics["justified_cycles"] += 1
                 gov.metrics["total_cycles"] += 1
             else:
                 gov.metrics["suppressed_cycles"] += 1
                 gov.metrics["total_cycles"] += 1

    # End Simulation
    report = gov.get_metrics()
    
    print("\n📊 ORCHESTRATION METRICS (Figure 3 & 4 Data)")
    print("==================================================")
    print(f"Total Cycles:      {gov.metrics['total_cycles']}")
    print(f"ISR (Suppression): {report['ISR']:.2f}% (Target: >70% during non-critical)")
    print(f"ECU (Utilization): {report['ECU']:.2f}% (Target: >90%)")
    print("==================================================")
    
    # Validate against constraints
    verdict = "PASS" if report['ISR'] > 40 else "FAIL" # Video phase is 30/60 = 50% suppression ideally
    print(f"🛡️  VALIDATION VERDICT: {verdict}")
    
    # Save Report
    output = {
        "metrics": report,
        "timeline": timeline,
        "verdict": verdict
    }
    with open("benchmarks/orchestration_results.json", "w") as f:
        json.dump(output, f, indent=2)
        print("✅ Results saved to benchmarks/orchestration_results.json")

if __name__ == "__main__":
    run_simulation()
