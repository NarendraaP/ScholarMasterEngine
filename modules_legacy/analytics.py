"""
Enhanced Analytics Engine with Real Engagement Inference
================================================================================
Paper 5: Engagement tracking using head pose + eye aspect ratio

Implements:
- Head pose estimation (pitch, yaw, roll)
- Eye Aspect Ratio (EAR) for blink detection
- Multi-modal engagement scoring

Author: Narendra P
Date: January 28, 2026 (Days 3-4 - Integration Sprint)
================================================================================
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Dict


class AnalyticsEngine:
    """
    Enhanced engagement inference using computer vision
    Papers: 5 (Engagement), 3 (Pose estimation)
    """
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh for pose and EAR"""
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks for EAR calculation (MediaPipe indices)
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
        # Engagement thresholds
        self.HEAD_YAW_THRESHOLD = 25  # degrees
        self.HEAD_PITCH_THRESHOLD = 20  # degrees
        self.EAR_THRESHOLD = 0.2  # Below this = eyes closed
        
        print("[ANALYTICS] Engagement engine initialized with MediaPipe")
    
    def compute_engagement(self, frame: np.ndarray) -> float:
        """
        Compute engagement score from frame
        
        Args:
            frame: BGR image from camera
        
        Returns:
            Engagement score 0.0-1.0 (1.0 = fully engaged)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            # No face detected = not engaged
            return 0.0
        
        # Get first face landmarks
        landmarks = results.multi_face_landmarks[0]
        
        # Extract head pose
        pitch, yaw, roll = self._estimate_head_pose(landmarks, frame.shape)
        
        # Extract eye aspect ratio
        left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Compute engagement components
        head_engagement = self._compute_head_engagement(pitch, yaw)
        eye_engagement = self._compute_eye_engagement(avg_ear)
        
        # Weighted combination (70% head, 30% eyes)
        engagement_score = 0.7 * head_engagement + 0.3 * eye_engagement
        
        return max(0.0, min(1.0, engagement_score))
    
    def _estimate_head_pose(self, landmarks, image_shape: Tuple) -> Tuple[float, float, float]:
        """
        Estimate head pose angles
        
        Returns:
            (pitch, yaw, roll) in degrees
        """
        h, w = image_shape[:2]
        
        # Key facial landmarks for pose estimation
        # Nose tip, chin, left eye corner, right eye corner, left mouth, right mouth
        nose_tip = landmarks.landmark[1]
        chin = landmarks.landmark[152]
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]
        left_mouth = landmarks.landmark[61]
        right_mouth = landmarks.landmark[291]
        
        # Convert to pixel coordinates
        points_3d = np.array([
            [nose_tip.x * w, nose_tip.y * h, nose_tip.z * w],
            [chin.x * w, chin.y * h, chin.z * w],
            [left_eye.x * w, left_eye.y * h, left_eye.z * w],
            [right_eye.x * w, right_eye.y * h, right_eye.z * w],
            [left_mouth.x * w, left_mouth.y * h, left_mouth.z * w],
            [right_mouth.x * w, right_mouth.y * h, right_mouth.z * w],
        ], dtype=np.float64)
        
        # 3D model points (canonical face model)
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye corner
            (225.0, 170.0, -135.0),      # Right eye corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
        # Camera matrix (simplified)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # No distortion
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vec, translation_vec = cv2.solvePnP(
            model_points,
            points_3d[:, :2],  # Only x, y coordinates
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return 0.0, 0.0, 0.0
        
        # Convert rotation vector to Euler angles
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        
        # Extract Euler angles
        pitch = np.degrees(np.arcsin(rotation_mat[2, 0]))
        yaw = np.degrees(np.arctan2(-rotation_mat[2, 1], rotation_mat[2, 2]))
        roll = np.degrees(np.arctan2(-rotation_mat[1, 0], rotation_mat[0, 0]))
        
        return pitch, yaw, roll
    
    def _calculate_ear(self, landmarks, eye_indices: list) -> float:
        """
        Calculate Eye Aspect Ratio (EAR)
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        
        Where p1-p6 are eye landmarks
        """
        # Get eye landmark coordinates
        points = []
        for idx in eye_indices:
            lm = landmarks.landmark[idx]
            points.append([lm.x, lm.y])
        
        points = np.array(points)
        
        # Calculate distances
        vertical_1 = np.linalg.norm(points[1] - points[5])
        vertical_2 = np.linalg.norm(points[2] - points[4])
        horizontal = np.linalg.norm(points[0] - points[3])
        
        # EAR formula
        if horizontal == 0:
            return 0.0
        
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear
    
    def _compute_head_engagement(self, pitch: float, yaw: float) -> float:
        """
        Compute engagement from head pose
        
        Engaged = looking straight (small pitch/yaw)
        Distracted = looking away (large pitch/yaw)
        """
        # Distance from center (0, 0)
        head_deviation = np.sqrt(pitch**2 + yaw**2)
        
        # Max expected deviation
        max_deviation = np.sqrt(self.HEAD_PITCH_THRESHOLD**2 + self.HEAD_YAW_THRESHOLD**2)
        
        # Engagement decreases with deviation
        engagement = 1.0 - min(head_deviation / max_deviation, 1.0)
        
        return engagement
    
    def _compute_eye_engagement(self, ear: float) -> float:
        """
        Compute engagement from eye aspect ratio
        
        Engaged = eyes open (EAR > threshold)
        Sleepy/Distracted = eyes closing (EAR < threshold)
        """
        if ear < self.EAR_THRESHOLD:
            # Eyes closed or nearly closed
            return 0.0
        
        # Normal EAR is ~0.25-0.30
        # Map to 0.0-1.0 range
        normalized_ear = min(ear / 0.30, 1.0)
        
        return normalized_ear
    
    def generate_engagement_metrics(self, student_id: str, duration_seconds: int = 60) -> Dict:
        """
        Generate engagement report for a student
        
        (Legacy method for backward compatibility)
        """
        # Placeholder for now - would analyze engagement history
        return {
            "student_id": student_id,
            "duration": duration_seconds,
            "avg_engagement": 0.75,
            "attention_span": "Good"
        }


# Singleton instance for import compatibility
_analytics_instance = None

def get_analytics_engine():
    """Get singleton analytics engine"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsEngine()
    return _analytics_instance
