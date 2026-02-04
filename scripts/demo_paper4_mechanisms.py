#!/usr/bin/env python3
"""
Demo for Paper 4 Mechanisms: 
1. Conflict Resolution (Algorithm 2)
2. Persistent Constraint Violation Filtering (PCVF)

This script validates the "Debounce" and "Weighted Voting" logic added to st_csf.py.
"""

import sys
import os
import time
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_legacy.st_csf import SpatiotemporalCSF
from modules_legacy.state_manager import RedisStateManager

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Paper4-Demo")

def run_conflict_resolution_demo():
    print("\n" + "="*60)
    print("DEMO SCENARIO 1: Algorithm 2 (Conflict Resolution Matrix)")
    print("="*60)
    
    # Use in-memory state for demo
    st_csf = SpatiotemporalCSF(state_manager=RedisStateManager(use_redis=False))
    
    student_id = "student_123"
    t_now = time.time()
    
    # Step 1: Student seen in Math Class (Baseline)
    print("\n[1] Initial State: Student seen in 'Zone_1' (Math Class)")
    st_csf.validate_event({'student_id': student_id, 'timestamp': t_now, 'zone': 'Zone_1'})
    
    # Step 2: Simultaneous conflict (Clock drift < 0.5s)
    # Event A: Library (Weight 0.5)
    # Event B: Lab (Weight 0.9) - Should win
    
    print(f"\n[2] Conflict Arrives at t+{0.1}s")
    print("    - Sensor A claims: 'Library' (Weight 0.5)")
    print("    - Sensor B claims: 'Lab' (Weight 0.9)")
    
    # Simulate first conflicting event (Library)
    valid_a, reason_a = st_csf.validate_event({
        'student_id': student_id, 
        'timestamp': t_now + 0.1, 
        'zone': 'Library'
    })
    print(f"    -> Result A (Library): {valid_a}, {reason_a}")
    
    # Simulate second conflicting event (Lab) - Should resolve conflict
    valid_b, reason_b = st_csf.validate_event({
        'student_id': student_id, 
        'timestamp': t_now + 0.1, 
        'zone': 'Lab'
    })
    print(f"    -> Result B (Lab): {valid_b}, {reason_b}")
    
    # Verify final state
    final_state = st_csf.state.get(f"state:{student_id}")
    print(f"\n[3] Final Resolved State: {final_state['zone']}")
    
    if final_state['zone'] == 'Lab':
        print("✅ SUCCESS: Higher wighted zone (Lab) prevailed.")
    else:
        print("❌ FAILURE: Conflict resolution failed.")

def run_pcvf_demo():
    print("\n" + "="*60)
    print("DEMO SCENARIO 2: PCVF (Persistent Constraint Violation Filtering)")
    print("="*60)
    
    st_csf = SpatiotemporalCSF(state_manager=RedisStateManager(use_redis=False))
    student_id = "teleporter_999"
    t0 = time.time()
    
    # Initial: Zone 1
    st_csf.validate_event({'student_id': student_id, 'timestamp': t0, 'zone': 'Zone_1'})
    print(f"[0s] Student at Zone_1")
    
    # Teleport to Zone 4 (500m away) in 10s (v = 50m/s >> 5m/s)
    # This is a violation.
    
    print("\n--- Phase 1: Transient Glitch (Duration < 5s) ---")
    t1 = t0 + 10
    valid, reason = st_csf.validate_event({'student_id': student_id, 'timestamp': t1, 'zone': 'Zone_4'})
    print(f"[10s] Teleport Detection 1: {valid}, {reason}")
    if "WARNING_POTENTIAL" in reason:
        print("✅ CORRECT: Alert suppressed (Debounce started)")
    else:
        print("❌ FAILED: Unexpected response")

    # Still persisting... but ONLY 2s later
    t2 = t1 + 2
    valid, reason = st_csf.validate_event({'student_id': student_id, 'timestamp': t2, 'zone': 'Zone_4'})
    print(f"[12s] Teleport Detection 2: {valid}, {reason}")
    if "PENDING" in reason:
        print("✅ CORRECT: Still pending (Duration 2s < 5s)")
        
    print("\n--- Phase 2: Persistent Violation (Duration > 5s) ---")
    # Persisting > 5s threshold
    t3 = t1 + 6 
    valid, reason = st_csf.validate_event({'student_id': student_id, 'timestamp': t3, 'zone': 'Zone_4'})
    print(f"[16s] Teleport Detection 3: {valid}, {reason}")
    
    if not valid and "CONFIRMED" in reason:
         print("✅ SUCCESS: Violation Confirmed after persistence.")
    else:
         print(f"❌ FAILURE: expected confirmed violation. Got: {reason}")

if __name__ == "__main__":
    run_conflict_resolution_demo()
    run_pcvf_demo()
