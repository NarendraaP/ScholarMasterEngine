import numpy as np
from collections import deque

class AntiSpoofing:
    """
    Advanced Liveness Detection Module (Anti-Spoofing).
    Uses Eye Aspect Ratio (EAR) to detect real humans vs photo attacks.
    """
    
    def __init__(self, blink_threshold=0.2, static_frames=150):
        """
        Args:
            blink_threshold: EAR threshold below which is considered a blink (default 0.2).
            static_frames: Number of frames with static EAR to flag as photo (default 150 = 5 seconds at 30fps).
        """
        # Dictionary to store EAR history for each tracked face ID
        self.ear_history = {}
        self.blink_threshold = blink_threshold
        self.static_frames_threshold = static_frames
        
        # Track consecutive frames without blink
        self.consecutive_frames = {}

    def calculate_ear(self, landmarks):
        """
        Calculate Eye Aspect Ratio (EAR) from facial landmarks.
        Supports both 68-point (dlib) and 106-point (InsightFace) formats.
        
        Args:
            landmarks: Nx2 numpy array of facial landmarks
            
        Returns:
            float: Average EAR for both eyes
        """
        if landmarks is None:
            return None
        
        num_points = len(landmarks)
        
        # InsightFace 106-point format
        if num_points == 106:
            # Left Eye: points 35 (top), 40 (bottom), 33 (outer), 39 (inner)
            l_v = np.linalg.norm(landmarks[35] - landmarks[40])
            l_h = np.linalg.norm(landmarks[33] - landmarks[39])
            ear_left = l_v / (l_h + 1e-6)
            
            # Right Eye: points 89 (top), 94 (bottom), 87 (inner), 93 (outer)
            r_v = np.linalg.norm(landmarks[89] - landmarks[94])
            r_h = np.linalg.norm(landmarks[87] - landmarks[93])
            ear_right = r_v / (r_h + 1e-6)
            
            return (ear_left + ear_right) / 2.0
        
        # Dlib 68-point format (for completeness)
        elif num_points == 68:
            # Left eye: points 36-41
            # Vertical: (37+38)/2 to (41+40)/2
            l_v1 = np.linalg.norm(landmarks[37] - landmarks[41])
            l_v2 = np.linalg.norm(landmarks[38] - landmarks[40])
            l_h = np.linalg.norm(landmarks[36] - landmarks[39])
            ear_left = (l_v1 + l_v2) / (2.0 * l_h + 1e-6)
            
            # Right eye: points 42-47
            r_v1 = np.linalg.norm(landmarks[43] - landmarks[47])
            r_v2 = np.linalg.norm(landmarks[44] - landmarks[46])
            r_h = np.linalg.norm(landmarks[42] - landmarks[45])
            ear_right = (r_v1 + r_v2) / (2.0 * r_h + 1e-6)
            
            return (ear_left + ear_right) / 2.0
        
        return None

    def check_eye_blink(self, face_landmarks, face_id=0):
        """
        Check if face is real person based on eye blink detection.
        
        Args:
            face_landmarks: Facial landmarks array (68 or 106 points)
            face_id: Unique identifier for tracking (default 0)
            
        Returns:
            bool: True if real person (blink detected), False if photo attack
        """
        # Calculate EAR
        ear = self.calculate_ear(face_landmarks)
        
        if ear is None:
            # No valid landmarks, assume safe (don't block)
            return True
        
        # Initialize tracking for this face
        if face_id not in self.ear_history:
            self.ear_history[face_id] = deque(maxlen=self.static_frames_threshold)
            self.consecutive_frames[face_id] = 0
        
        # Store EAR history
        self.ear_history[face_id].append(ear)
        
        # Check for blink (EAR < threshold)
        if ear < self.blink_threshold:
            # Blink detected! Increment counter
            self.consecutive_frames[face_id] += 1
            
            # Need 3 consecutive frames below threshold to confirm blink
            if self.consecutive_frames[face_id] >= 3:
                # Real person - blink detected
                return True
        else:
            # Reset consecutive frame counter
            self.consecutive_frames[face_id] = 0
        
        # Check if EAR has been static (no blink) for too long
        if len(self.ear_history[face_id]) >= self.static_frames_threshold:
            # Check if EAR variance is very low (static photo)
            ear_array = np.array(self.ear_history[face_id])
            variance = np.var(ear_array)
            
            # If variance < threshold and no blink detected, it's a photo
            if variance < 0.001 and self.consecutive_frames[face_id] < 3:
                return False  # Photo Attack!
        
        # Default: assume real (collecting data)
        # Default: assume real (collecting data)
        return True

    def check_liveness(self, embedding, landmarks):
        """
        Verifies if the face is live.
        Args:
            embedding: Face embedding (unused for now, kept for signature match)
            landmarks: Face landmarks
        Returns:
            (is_live, message)
        """
        try:
            # Use existing logic
            is_real = self.check_eye_blink(landmarks)
            
            if is_real:
                return True, "Live"
            else:
                return False, "Spoof Detected (Static Eyes)"
                
        except Exception as e:
            # Fallback to prevent crash
            print(f"⚠️ Liveness Check Failed: {e}")
            return True, "Live (Fallback)"

# Alias for backward compatibility
LivenessDetector = AntiSpoofing

if __name__ == "__main__":
    # Test
    anti_spoof = AntiSpoofing()
    print("✅ AntiSpoofing module initialized")
