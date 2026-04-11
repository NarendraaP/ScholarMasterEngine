import math
import cv2
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class GeometricHeuristics:
    """
    Implements the deterministic logic defined in Algorithm 1 of Paper 3.
    This module analyzes "Architecturally Irreversible" skeletal vectors
    to detect behavioral events without performing biometric recognition or 
    affect scoring.
    """
    
    def __init__(self, persistence_threshold: float = 1.0):
        self.persistence_threshold = persistence_threshold
        # State machine tracking: subject_id -> active time (seconds)
        self.fsm_timers: Dict[str, float] = {}
        
        # 3D Anthropomorphic Generic Face Model for PnP (No identity)
        # Using a standard simplified reference model (6 points required for DLT)
        self.standard_3d_face = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (-30.0, -30.0, -30.0),       # Left eye corner
            (30.0, -30.0, -30.0),        # Right eye corner
            (-60.0, 0.0, -60.0),         # Left ear
            (60.0, 0.0, -60.0),          # Right ear
            (0.0, -60.0, -30.0)          # Chin / Neck base proxy
        ], dtype="double")
        
        # Assume standard 1080p webcam intrinsics for PnP math
        self.camera_matrix = np.array([
            [1000, 0, 960],
            [0, 1000, 540],
            [0, 0, 1]
        ], dtype="double")
        self.dist_coeffs = np.zeros((4,1))

    def process_pose_vectors(self, abstract_vectors: List[Dict[str, Any]], delta_t: float) -> List[Dict[str, Any]]:
        """
        Processes a list of anonymous pose vectors, applying relative topology rules 
        and the PnP projection.
        
        Args:
            abstract_vectors: List of dictionaries containing 'subject_id' and 'keypoints' (17x2).
            delta_t: Time elapsed since last frame (seconds).
            
        Returns:
            List of detected geometric event logs.
        """
        events = []
        
        for vector_set in abstract_vectors:
            subject_id = vector_set.get("subject_id", "anon_unknown")
            kpts = np.array(vector_set.get("keypoints", []))
            
            if kpts.shape != (17, 2):
                logger.warning(f"Invalid keypoint array shape for {subject_id}")
                continue
                
            # Initialize timer if new subject
            if subject_id not in self.fsm_timers:
                self.fsm_timers[subject_id] = 0.0

            # 1. Geometric Check: Hand Raise (Wrist Y < Ear Y)
            # COCO indices: LEar=3, REar=4, LWrist=9, RWrist=10
            # Note: image coordinates have origin at top-left, so smaller Y means higher physically.
            l_ear_y = kpts[3][1]
            r_ear_y = kpts[4][1]
            l_wrist_y = kpts[9][1]
            r_wrist_y = kpts[10][1]
            
            # Simple thresholding logic
            is_hand_raised = (l_wrist_y < l_ear_y) or (r_wrist_y < r_ear_y)
            
            if is_hand_raised:
                self.fsm_timers[subject_id] += delta_t
            else:
                self.fsm_timers[subject_id] = 0.0 # Reset on break
                
            # 2. Head Pose Check (Attention Direction using PnP)
            attention_diverted = self.estimate_head_orientation_pnp(kpts)
            
            # 3. Event Logging (Only geometric truths, no affective inference)
            if self.fsm_timers[subject_id] > self.persistence_threshold:
                # Trigger confirmed event
                events.append({
                    "event_type": "hand_raise_geometry",
                    "subject_id": subject_id,
                    "spatial_zone": "aggregated_zone",  # Placeholder for spatial logic
                    "attention_diverted": attention_diverted,
                    "active_duration": self.fsm_timers[subject_id]
                })
                # Reset FSM after log to avoid spamming
                self.fsm_timers[subject_id] = 0.0
                
        return events

    def estimate_head_orientation_pnp(self, kpts: np.ndarray) -> bool:
        """
        Solves Perspective-n-Point to find head yaw. Returns True if > 45 degrees.
        
        Args:
            kpts: Full 17x2 keypoint array.
            
        Returns:
            Boolean indicating if attention is diverted (>45 degrees yaw).
        """
        # Create a proxy chin/neck point by averaging the shoulders (indices 5 and 6)
        chin_proxy = (kpts[5] + kpts[6]) / 2.0
        
        # Extract 2D image points matching the 3D model: Nose(0), L_Eye(1), R_Eye(2), L_Ear(3), R_Ear(4), Chin(Proxy)
        image_points = np.array([
            kpts[0],
            kpts[1],
            kpts[2],
            kpts[3],
            kpts[4],
            chin_proxy
        ], dtype="double")
        
        # Ensure points are somewhat valid (not all zeroes indicating failed detection)
        if np.all(image_points == 0):
            return True # If face is gone, attention is gone
            
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.standard_3d_face, 
            image_points, 
            self.camera_matrix, 
            self.dist_coeffs, 
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return True # Default to diverted on failure
            
        # Convert rotation vector to rotation matrix, then to Euler angles
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        proj_matrix = np.hstack((rotation_matrix, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)
        
        yaw = euler_angles[1][0] # Y-axis rotation
        
        # If absolute yaw exceeds 45 degrees, trigger
        return abs(yaw) > 45.0
