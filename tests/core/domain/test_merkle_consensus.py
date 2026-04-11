import unittest
from datetime import datetime
from core.domain.entities.merkle_tree import MerkleTree, MerkleNode
from core.domain.events.domain_events import FaceDetectedEvent
from core.application.services.sync_service import ScheduleSyncService
from core.domain.services.consensus_service import ConsensusService

class TestPaper4Algorithms(unittest.TestCase):
    
    def test_merkle_tree_sync(self):
        """
        Tests the Merkle Tree synchronization protocol logic for Edge nodes finding mismatches.
        """
        # Node A processes 3 events locally.
        event1 = FaceDetectedEvent(student_id="S1", zone="Hallway", confidence=0.9, timestamp=datetime(2025, 1, 1, 10, 0, 0))
        event2 = FaceDetectedEvent(student_id="S2", zone="Classroom A", confidence=0.8, timestamp=datetime(2025, 1, 1, 10, 0, 5))
        event3 = FaceDetectedEvent(student_id="S3", zone="Lab 1", confidence=0.95, timestamp=datetime(2025, 1, 1, 10, 0, 10))
        
        tree_a = MerkleTree([event1, event2, event3])
        
        # Node B (Central Server) only received the first 2 events due to network cut.
        tree_b = MerkleTree([event1, event2])
        
        # 1. Detect Desync
        self.assertTrue(ScheduleSyncService.detect_desync(tree_a, tree_b.root_hash))
        
        # 2. Re-add event3 to Tree B to simulate recovery.
        tree_recovery = MerkleTree([event1, event2, event3])
        self.assertEqual(tree_a.root_hash, tree_recovery.root_hash)
        self.assertFalse(ScheduleSyncService.detect_desync(tree_a, tree_recovery.root_hash))
        
    def test_confidence_weighted_consensus(self):
        """
        Tests Algorithm 2 from Paper 4 (Confidence-Weighted Consensus).
        Resolves conflicting multi-camera observations.
        """
        # Scenario: Camera A sees student in Hallway (0.6 conf). 
        # Camera B sees them stepping into Classroom 101 (0.85 conf).
        
        detections = [
            {"zone": "Hallway", "confidence": 0.6},
            {"zone": "Classroom 101", "confidence": 0.85}
        ]
        
        winning_zone = ConsensusService.resolve_zone_consensus(detections)
        self.assertEqual(winning_zone, "Classroom 101")
        
        # Scenario: 3 overlapping cameras. Two say Hallway (0.5 and 0.4), One says Canteen (0.8).
        # Hallway Total = 0.9. Canteen = 0.8. Hallway should win despite lower individual confidence.
        detections_complex = [
            {"zone": "Hallway", "confidence": 0.5},
            {"zone": "Hallway", "confidence": 0.4},
            {"zone": "Canteen", "confidence": 0.8}
        ]
        
        winning_zone_complex = ConsensusService.resolve_zone_consensus(detections_complex)
        self.assertEqual(winning_zone_complex, "Hallway")

if __name__ == '__main__':
    unittest.main()
