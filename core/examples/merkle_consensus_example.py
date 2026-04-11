from core.application.services.sync_service import ScheduleSyncService
from core.domain.entities.merkle_tree import MerkleTree
from core.domain.events.domain_events import FaceDetectedEvent
from core.domain.services.consensus_service import ConsensusService
from datetime import datetime
import time

def demo_merkle_sync():
    print("--- 1. MERKLE TREE SYNCHRONIZATION O(log N) PROOF ---")
    # Simulate an Edge Node collecting detections offline
    events_edge = [
        FaceDetectedEvent(student_id="ID_001", zone="Lab A", confidence=0.9, timestamp=datetime.now()),
        FaceDetectedEvent(student_id="ID_002", zone="Lab A", confidence=0.85, timestamp=datetime.now())
    ]
    tree_edge = ScheduleSyncService.generate_sync_tree(events_edge)
    
    # Simulate Central Server initially empty
    tree_central = ScheduleSyncService.generate_sync_tree([])
    
    print(f"Edge Root Hash: {tree_edge.root_hash}")
    print(f"Cent Root Hash: {tree_central.root_hash}")
    
    # Fast O(1) Desync Check
    if ScheduleSyncService.detect_desync(tree_edge, tree_central.root_hash):
        print("-> Out of Sync! Network partition recovery initiated...")
        missing_hashes = ScheduleSyncService.find_missing_events(tree_edge.root, tree_central.root)
        print(f"-> Missing Hashes Identified: {len(missing_hashes)}")
        
        # Simulate Sync
        tree_central = ScheduleSyncService.generate_sync_tree(events_edge)
        print("-> Sync Complete.")
        
    print(f"Edge Root: {tree_edge.root_hash} == Cent Root: {tree_central.root_hash}\n")

def demo_consensus():
    print("--- 2. MULTI-CAMERA WEIGHTED CONSENSUS PROOF ---")
    # Simulate 3 overlapping cameras detecting the same student
    # Two cameras slightly disagree but with low confidence. The high-confidence camera wins.
    multi_cam_frame = [
        {"zone": "Hallway", "confidence": 0.4},  # Cam 1: Far away, blurry
        {"zone": "Hallway", "confidence": 0.3},  # Cam 2: Far away, blurry
        {"zone": "Canteen", "confidence": 0.95}  # Cam 3: Direct overhead, very clear
    ]
    
    print("Incoming Multi-Camera Frame (Overlapping FOV):")
    for d in multi_cam_frame:
        print(f"  - Detected in {d['zone']} with {d['confidence']*100}% confidence")
        
    winning_zone = ConsensusService.resolve_zone_consensus(multi_cam_frame)
    print(f"-> Algorithm 2 Output (Winning Zone): {winning_zone}")
    # Algorithm ensures Canteen wins (0.95) over Hallway (0.4 + 0.3 = 0.7)

if __name__ == '__main__':
    demo_merkle_sync()
    time.sleep(1)
    demo_consensus()
