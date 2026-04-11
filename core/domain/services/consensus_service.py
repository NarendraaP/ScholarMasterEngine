from typing import List, Dict, Any

class ConsensusService:
    """
    Domain Service for Confidence-Weighted Consensus.
    Implements Algorithm 2 from Paper 4, resolving conflicting spatial detections
    from overlapping camera feeds before logic evaluation.
    """
    
    @staticmethod
    def resolve_zone_consensus(detections: List[Dict[str, Any]]) -> str:
        """
        Resolves the true zone of a student using Confidence-Weighted Voting.
        
        Args:
            detections: List of detection dicts, e.g. 
                       [{'zone': 'Hallway', 'confidence': 0.6}, 
                        {'zone': 'Room 101', 'confidence': 0.85}]
                        
        Returns:
            The winning zone string based on highest aggregate confidence.
        """
        if not detections:
            return "UNKNOWN"
            
        if len(detections) == 1:
            return detections[0].get('zone', "UNKNOWN")
            
        candidate_votes: Dict[str, float] = {}
        
        for d in detections:
            zone = d.get('zone', "UNKNOWN")
            confidence = float(d.get('confidence', 0.0))
            candidate_votes[zone] = candidate_votes.get(zone, 0.0) + confidence
            
        # Extract the zone with the maximum aggregated confidence sum
        winning_zone = max(candidate_votes.items(), key=lambda item: item[1])[0]
        
        return winning_zone
