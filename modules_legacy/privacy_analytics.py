import numpy as np

class PrivacyEngagement:
    """
    Paper 3: Privacy-Preserving Engagement Analysis
    
    Replaces MediaPipe Face Mesh (468 points) with YOLO-Pose (17 points).
    Calculates engagement based on Head Orientation derived from 
    sparse keypoints (Nose, Eyes, Ears).
    
    "Pose-Only Enforcement" - No dense facial features are processed.
    """
    
    def __init__(self):
        print("✅ PrivacyEngagement loaded (Pose-Only mode)")
        
        # COCO Keypoint Indices
        self.NOSE = 0
        self.L_EYE = 1
        self.R_EYE = 2
        self.L_EAR = 3
        self.R_EAR = 4
        self.L_SHOULDER = 5
        self.R_SHOULDER = 6

    def analyze_engagement(self, keypoints):
        """
        Analyze engagement for a single person from YOLO keypoints.
        
        Args:
            keypoints: Numpy array of shape (17, 2) or (17, 3) 
                       containing (x, y, [conf])
        
        Returns:
            engagement_score (float): 0.0 to 1.0
            orientation (str): "Frontal", "Left", "Right", "Away"
        """
        if keypoints is None or len(keypoints) < 5:
            return 0.0, "Unknown"

        # Extract relevant points
        # Ensure we handle (x,y) or (x,y,conf)
        nose = keypoints[self.NOSE][:2]
        l_ear = keypoints[self.L_EAR][:2]
        r_ear = keypoints[self.R_EAR][:2]
        l_eye = keypoints[self.L_EYE][:2]
        r_eye = keypoints[self.R_EYE][:2]

        # Check visibility/confidence (if 0,0 usually means not detected)
        if np.sum(nose) == 0 or np.sum(l_ear) == 0 or np.sum(r_ear) == 0:
            # Partial detection (e.g. side profile, one ear hidden)
            # If we only see one ear, they are looking to the side.
            if np.sum(l_ear) > 0 and np.sum(r_ear) == 0:
                return 0.3, "Looking Right" # Only left ear visible -> turned right
            if np.sum(r_ear) > 0 and np.sum(l_ear) == 0:
                return 0.3, "Looking Left" # Only right ear visible -> turned left
            return 0.0, "Unknown"

        # --- Calculate Yaw (Left/Right Turn) ---
        # Compare Nose distance to Ears
        # Midpoint between ears
        ear_midpoint_x = (l_ear[0] + r_ear[0]) / 2
        
        # Horizontal distance from nose to ear midpoint
        # If looking straight, nose should be close to midpoint x
        # Normalize by ear-to-ear distance (head size)
        head_width = np.linalg.norm(l_ear - r_ear)
        if head_width == 0: return 0.0, "Unknown"
        
        yaw_ratio = (nose[0] - ear_midpoint_x) / head_width
        
        # Thresholds
        # 0.0 = Perfect center
        # > 0.3 = Turned (Sign tells direction)
        
        yaw_score = 1.0 - min(abs(yaw_ratio) * 2.5, 1.0) # Decay engagement as yaw increases

        # --- Calculate Pitch (Up/Down) ---
        # Compare Eye line to Ear line
        eye_mid_y = (l_eye[1] + r_eye[1]) / 2
        ear_mid_y = (l_ear[1] + r_ear[1]) / 2
        
        # If looking Down, eyes drop below ears (higher Y value)
        # If looking Up, eyes raise above ears (lower Y value)
        pitch_diff = eye_mid_y - ear_mid_y
        pitch_ratio = pitch_diff / head_width
        
        # Heuristic: 
        # Normal range is small. Large deviations imply looking down/up.
        pitch_score = 1.0 - min(abs(pitch_ratio) * 2.0, 1.0)

        # Combined Engagement
        final_score = (yaw_score * 0.7) + (pitch_score * 0.3)
        
        # Determine Label
        orientation = "Frontal"
        if final_score < 0.6:
            orientation = "Distracted"
        
        return max(0.0, min(1.0, final_score)), orientation

    def process_batch(self, keypoints_list):
        """
        Process multiple people. 
        Returns average engagement or list.
        Currently returns the score of the most "engaged" person (primary subject)
        or an average.
        
        For the unified system, we'll return the MAX score found (optimistic)
        or 0.0 if empty.
        """
        if not keypoints_list:
            return 0.0
            
        scores = []
        for kp in keypoints_list:
            # Convert to numpy if it's a tensor
            if hasattr(kp, 'cpu'): kp = kp.cpu().numpy()
            if hasattr(kp, 'numpy'): kp = kp.numpy()
            
            score, _ = self.analyze_engagement(kp)
            scores.append(score)
            
        if not scores:
            return 0.0
            
        # Return max engagement (assuming the 'active' student is the one we care about)
        return max(scores)
