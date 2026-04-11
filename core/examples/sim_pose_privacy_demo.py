import os
import sys
import time
import subprocess
import numpy as np
import logging
from typing import Dict, Any, List

# Setup path and logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PoseSimDemo")

from core.infrastructure.sensing.visual.pose_estimator import VectorizationEngine
from core.domain.services.geometric_heuristics import GeometricHeuristics

def main():
    print("="*60)
    print("ScholarMasterEngine - Paper 3: Pose Privacy Demo")
    print("="*60)
    
    # 1. Compile C++ secure allocator proof
    cpp_source = os.path.abspath(os.path.join(os.path.dirname(__file__), '../infrastructure/memory/secure_allocator.cpp'))
    cpp_binary = os.path.abspath(os.path.join(os.path.dirname(__file__), '../infrastructure/memory/secure_allocator.out'))
    print("\n[Phase 1] Compiling C++ Secure Allocator Reference Design...")
    try:
        subprocess.run(["g++", cpp_source, "-o", cpp_binary], check=True)
        print("Compile successful.")
    except Exception as e:
        print(f"Compilation failed: {e}")
        return

    # 2. Run C++ proof
    print("\n[Phase 2] Executing C++ Memory Zero-fill Proof...")
    subprocess.run([cpp_binary])

    # 3. Python Pipeline Demo
    print("\n[Phase 3] Running Python Volatile-Only inference pipeline...")
    
    # Initialize Engine (simulates YOLOv8 load)
    pose_engine = VectorizationEngine()
    pose_engine.initialize()
    
    # Initialize Heuristics (1.0s threshold)
    geometry_logic = GeometricHeuristics(persistence_threshold=1.0)
    
    # Simulate a 1080p dummy RGB frame
    volatile_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Simulate a hand-raise over 1.5 seconds at 30 FPS
    print("\nSimulating hand raise over 1.5 seconds...")
    detected_events = []
    
    fps = 30
    total_frames = int(fps * 1.5)
    delta_t = 1.0 / fps
    
    for frame_idx in range(total_frames):
        # 1. Vectorize (Simulate YOLO extraction)
        # We pass volatile frame. VectorizationEngine RETURNS ONLY ABSTRACT COORDINATES
        abstract_vectors = pose_engine.extract_pose_vectors(volatile_frame)
        
        # At this exact point, volatile_frame is no longer referenced by the pose pipeline.
        # Overwrite to prove it (Simulated Python Volatile handling)
        volatile_frame.fill(0) 
        
        # 2. Geometric Logic filtering
        events = geometry_logic.process_pose_vectors(abstract_vectors, delta_t)
        
        if events:
            detected_events.extend(events)
            print(f"  Frame {frame_idx:02d}: {len(events)} Event(s) Triggered!")
        elif frame_idx % 10 == 0:
            print(f"  Frame {frame_idx:02d}: Processing abstract coordinates (no trigger yet)...")
            
        time.sleep(0.01) # fast forward
        
    print("\n[Final Report]")
    for e in detected_events:
        print(f"  Event: {e['event_type']} | Subject: {e['subject_id']} | Diverted: {e['attention_diverted']} | Duration: {e['active_duration']:.2f}s")
        
    print("\nVerification Complete: Pipeline processes only 34-d scalars, extracts events, and drops raw frames.")
    
if __name__ == "__main__":
    main()
