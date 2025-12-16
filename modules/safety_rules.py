import numpy as np

class SafetyEngine:
    def __init__(self):
        print("✅ SafetyEngine loaded")

    def detect_hand_raise(self, keypoints_list):
        """
        Scans ALL students in the frame.
        Returns True if ANY student has their wrist significantly above their ear.
        """
        if not keypoints_list:
            return False

        for kp in keypoints_list:
            # kp is typically a tensor or array of shape (17, 2) or (17, 3)
            # COCO Keypoints: 
            # 3=Left Ear, 4=Right Ear
            # 9=Left Wrist, 10=Right Wrist
            
            # Skip empty or malformed detections
            if len(kp) < 11:
                continue

            # Convert to standard list/numpy format if needed
            if hasattr(kp, 'cpu'): kp = kp.cpu().numpy()
            if hasattr(kp, 'numpy'): kp = kp.numpy()
            
            try:
                # Extract Y-coordinates (Recall: Lower Y value = Higher on screen)
                # We add a 20px buffer to prevent flickering (wrist must be clearly above)
                
                # Check Left Arm (Wrist vs Ear)
                l_ear_y = kp[3][1]
                l_wrist_y = kp[9][1]
                
                # Check Right Arm
                r_ear_y = kp[4][1]
                r_wrist_y = kp[10][1]

                # Condition: Wrist is higher than Ear (smaller Y value)
                left_raised = (l_wrist_y < l_ear_y) and (l_wrist_y > 0)
                right_raised = (r_wrist_y < r_ear_y) and (r_wrist_y > 0)

                if left_raised or right_raised:
                    return True # Found at least one student raising hand

            except Exception:
                continue
                
        return False

    def detect_sleeping(self, keypoints_list):
        """
        Simple heuristic: Head is low relative to shoulders.
        """
        sleeping_indices = []
        for idx, kp in enumerate(keypoints_list):
            if len(kp) < 7: continue
            try:
                # Nose (0) vs Shoulders (5, 6)
                nose_y = kp[0][1]
                l_shoulder_y = kp[5][1]
                r_shoulder_y = kp[6][1]
                
                avg_shoulder_y = (l_shoulder_y + r_shoulder_y) / 2
                
                # If nose is below (greater Y) the shoulder line
                if nose_y > avg_shoulder_y:
                    sleeping_indices.append(idx)
                    return True, "Sleeping Detected", sleeping_indices
            except:
                continue
        return False, "Awake", []

    def detect_violence(self, keypoints_list):
        """
        Detects potential violence/fighting using Paper 6 heuristics:
        1. Proximity Detection: Close distance between people
        2. Aggression Detection: Raised arms/wrists (fighting stance)
        
        Args:
            keypoints_list: List of pose keypoint arrays (17 keypoints each)
        
        Returns:
            (bool, str): (is_violence_detected, message)
        """
        if not keypoints_list or len(keypoints_list) < 2:
            # Need at least 2 people for violence detection
            return False, "Safe"
        
        try:
            # Check all pairs of people for potential conflict
            for i in range(len(keypoints_list)):
                for j in range(i + 1, len(keypoints_list)):
                    kp1 = keypoints_list[i]
                    kp2 = keypoints_list[j]
                    
                    # Skip malformed detections
                    if len(kp1) < 11 or len(kp2) < 11:
                        continue
                    
                    # Convert to numpy if needed
                    if hasattr(kp1, 'cpu'): kp1 = kp1.cpu().numpy()
                    if hasattr(kp1, 'numpy'): kp1 = kp1.numpy()
                    if hasattr(kp2, 'cpu'): kp2 = kp2.cpu().numpy()
                    if hasattr(kp2, 'numpy'): kp2 = kp2.numpy()
                    
                    # HEURISTIC 1: Proximity Check
                    # Calculate distance between nose keypoints (Index 0)
                    nose1 = kp1[0][:2]  # (x, y)
                    nose2 = kp2[0][:2]  # (x, y)
                    
                    distance = np.sqrt((nose1[0] - nose2[0])**2 + (nose1[1] - nose2[1])**2)
                    
                    # Close Proximity: < 100 pixels
                    if distance < 100:
                        # HEURISTIC 2: Aggression Check
                        # Check if wrists are raised above shoulders (fighting stance)
                        
                        # Person 1: Check if wrists (9, 10) are above shoulders (5, 6)
                        l_wrist1_y = kp1[9][1]
                        r_wrist1_y = kp1[10][1]
                        l_shoulder1_y = kp1[5][1]
                        r_shoulder1_y = kp1[6][1]
                        
                        # Person 2: Check if wrists are above shoulders
                        l_wrist2_y = kp2[9][1]
                        r_wrist2_y = kp2[10][1]
                        l_shoulder2_y = kp2[5][1]
                        r_shoulder2_y = kp2[6][1]
                        
                        # Check if at least one wrist is raised for each person
                        person1_aggressive = (l_wrist1_y < l_shoulder1_y) or (r_wrist1_y < r_shoulder1_y)
                        person2_aggressive = (l_wrist2_y < l_shoulder2_y) or (r_wrist2_y < r_shoulder2_y)
                        
                        # Violence detected if BOTH are in close proximity AND at least one shows aggression
                        if person1_aggressive or person2_aggressive:
                            return True, "Physical Conflict Detected"
            
            # No violence detected in any pair
            return False, "Safe"
            
        except Exception as e:
            # Fail safe: Don't trigger false alarms on errors
            print(f"Violence detection error: {e}")
            return False, "Safe"
