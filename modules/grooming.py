import cv2
import numpy as np

class GroomingInspector:
    """
    Dress Code & Grooming Compliance Inspector.
    Checks uniform color and footwear compliance using computer vision.
    """
    
    def __init__(self):
        # YOLOv8 Pose Keypoint Indices
        self.KP_L_SHOULDER = 5
        self.KP_R_SHOULDER = 6
        self.KP_L_HIP = 11
        self.KP_R_HIP = 12
        self.KP_L_ANKLE = 15
        self.KP_R_ANKLE = 16
        
        # Default uniform color (Navy Blue in HSV)
        # H: 110 (Blue hue), S: 100-255, V: 50-200
        self.default_uniform_hsv = {
            'h_min': 100,
            'h_max': 120,
            's_min': 100,
            's_max': 255,
            'v_min': 50,
            'v_max': 200
        }
    
    def check_uniform(self, frame, keypoints, expected_color_hsv=None):
        """
        Checks if the person is wearing the correct uniform color.
        
        Args:
            frame: BGR image
            keypoints: numpy array of shape (17, 3) - YOLOv8 pose keypoints
            expected_color_hsv: dict with h_min, h_max, s_min, s_max, v_min, v_max
        
        Returns:
            (bool, str): (is_compliant, message)
        """
        if expected_color_hsv is None:
            expected_color_hsv = self.default_uniform_hsv
        
        try:
            # Extract Torso ROI using Shoulder and Hip keypoints
            l_shoulder = keypoints[self.KP_L_SHOULDER][:2].astype(int)
            r_shoulder = keypoints[self.KP_R_SHOULDER][:2].astype(int)
            l_hip = keypoints[self.KP_L_HIP][:2].astype(int)
            r_hip = keypoints[self.KP_R_HIP][:2].astype(int)
            
            # Calculate torso bounding box
            x_min = min(l_shoulder[0], r_shoulder[0], l_hip[0], r_hip[0])
            x_max = max(l_shoulder[0], r_shoulder[0], l_hip[0], r_hip[0])
            y_min = min(l_shoulder[1], r_shoulder[1])
            y_max = max(l_hip[1], r_hip[1])
            
            # Add padding
            padding = 10
            x_min = max(0, x_min - padding)
            x_max = min(frame.shape[1], x_max + padding)
            y_min = max(0, y_min - padding)
            y_max = min(frame.shape[0], y_max + padding)
            
            # Extract torso ROI
            torso_roi = frame[y_min:y_max, x_min:x_max]
            
            if torso_roi.size == 0:
                return True, "Uniform Check: ROI Invalid"
            
            # Convert to HSV
            hsv_roi = cv2.cvtColor(torso_roi, cv2.COLOR_BGR2HSV)
            
            # Calculate average HSV color
            avg_h = np.mean(hsv_roi[:, :, 0])
            avg_s = np.mean(hsv_roi[:, :, 1])
            avg_v = np.mean(hsv_roi[:, :, 2])
            
            # Check if color matches expected uniform color
            h_match = expected_color_hsv['h_min'] <= avg_h <= expected_color_hsv['h_max']
            s_match = expected_color_hsv['s_min'] <= avg_s <= expected_color_hsv['s_max']
            v_match = expected_color_hsv['v_min'] <= avg_v <= expected_color_hsv['v_max']
            
            is_compliant = h_match and s_match and v_match
            
            if is_compliant:
                return True, "Uniform OK"
            else:
                return False, "Uniform Violation"
                
        except Exception as e:
            print(f"   Error in check_uniform: {e}")
            return True, "Uniform Check: Error"
    
    def check_shoes(self, frame, keypoints):
        """
        Checks if the person is wearing proper shoes (not slippers/sandals).
        Uses a simple heuristic based on ankle ROI color analysis.
        
        Args:
            frame: BGR image
            keypoints: numpy array of shape (17, 3) - YOLOv8 pose keypoints
        
        Returns:
            (bool, str): (is_compliant, message)
        """
        try:
            # Extract Feet ROI using Ankle keypoints
            l_ankle = keypoints[self.KP_L_ANKLE][:2].astype(int)
            r_ankle = keypoints[self.KP_R_ANKLE][:2].astype(int)
            
            # Calculate feet bounding box (expand downward from ankles)
            x_min = min(l_ankle[0], r_ankle[0]) - 30
            x_max = max(l_ankle[0], r_ankle[0]) + 30
            y_min = min(l_ankle[1], r_ankle[1])
            y_max = y_min + 80  # Extend downward to capture feet
            
            # Bounds check
            x_min = max(0, x_min)
            x_max = min(frame.shape[1], x_max)
            y_min = max(0, y_min)
            y_max = min(frame.shape[0], y_max)
            
            # Extract feet ROI
            feet_roi = frame[y_min:y_max, x_min:x_max]
            
            if feet_roi.size == 0:
                return True, "Shoes Check: ROI Invalid"
            
            # Convert to HSV
            hsv_roi = cv2.cvtColor(feet_roi, cv2.COLOR_BGR2HSV)
            
            # Simple heuristic: Check for skin color (slippers/sandals)
            # Skin color in HSV: H: 0-20, S: 30-150, V: 60-255
            lower_skin = np.array([0, 30, 60], dtype=np.uint8)
            upper_skin = np.array([20, 150, 255], dtype=np.uint8)
            
            skin_mask = cv2.inRange(hsv_roi, lower_skin, upper_skin)
            skin_ratio = np.sum(skin_mask > 0) / skin_mask.size
            
            # If more than 30% skin color detected -> likely slippers/sandals
            if skin_ratio > 0.3:
                return False, "Lab Safety: Slippers Detected"
            else:
                return True, "Shoes OK"
                
        except Exception as e:
            print(f"   Error in check_shoes: {e}")
            return True, "Shoes Check: Error"

if __name__ == "__main__":
    print("✅ GroomingInspector initialized successfully!")
    inspector = GroomingInspector()
    print(f"   Default uniform HSV: {inspector.default_uniform_hsv}")
