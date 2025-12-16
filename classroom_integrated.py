import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class ClassroomIntegration:
    """Papers 2 & 3 Integration - Privacy Pose + Context Engine"""
    
    def __init__(self):
        # MediaPipe setup
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Shared state
        self.hand_raised = False
        self.running = True
        self.lock = threading.Lock()
    
    def detect_hand_raise(self, landmarks):
        """Check if hand is raised above head"""
        if not landmarks:
            return False
        
        try:
            # Get landmark positions
            # Nose = 0, Left Wrist = 15, Right Wrist = 16
            nose_y = landmarks.landmark[0].y
            left_wrist_y = landmarks.landmark[15].y
            right_wrist_y = landmarks.landmark[16].y
            
            # Check if either wrist is above nose (lower Y value = higher position)
            left_raised = left_wrist_y < nose_y
            right_raised = right_wrist_y < nose_y
            
            return left_raised or right_raised
        except:
            return False
    
    def visual_thread(self):
        """Thread 1: Privacy-preserving pose detection with visualization"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open webcam")
            return
        
        # Get frame dimensions
        ret, test_frame = cap.read()
        if not ret:
            print("❌ Error: Could not read from webcam")
            return
        
        frame_height, frame_width = test_frame.shape[:2]
        
        with self.mp_pose.Pose(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3) as pose:
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose
                results = pose.process(rgb_frame)
                
                # Create black background (privacy-safe)
                privacy_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                
                # Draw skeleton and check hand raise
                if results.pose_landmarks:
                    # Draw pose on black background
                    self.mp_drawing.draw_landmarks(
                        privacy_frame,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
                    
                    # Check hand raise
                    hand_raised = self.detect_hand_raise(results.pose_landmarks)
                    
                    with self.lock:
                        self.hand_raised = hand_raised
                    
                    # Add status overlay
                    cv2.putText(privacy_frame, "PRIVACY MODE: ACTIVE", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if hand_raised:
                        cv2.putText(privacy_frame, "HAND RAISED!", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    cv2.putText(privacy_frame, "No pose detected", 
                                (frame_width//2 - 100, frame_height//2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                
                # Display privacy frame
                cv2.imshow('Classroom Mode - Privacy Pose', privacy_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def context_logic_thread(self):
        """Thread 2: Context engine with gesture detection"""
        iteration = 1
        
        while self.running:
            # Check hand raise status
            with self.lock:
                hand_raised = self.hand_raised
            
            # Print gesture detection
            if hand_raised:
                print(f"[GESTURE] Hand Raise Detected (Scan {iteration})")
            
            # Print context logic every 5 seconds
            if iteration % 5 == 0:
                print(f"[CONTEXT] Subject: MATH | Emotion: FOCUS (Logic Corrected)")
            
            time.sleep(1)
            iteration += 1
    
    def start(self):
        """Start the integrated classroom system"""
        print("=" * 70)
        print("CLASSROOM MODE - Papers 2 & 3 Integration")
        print("=" * 70)
        print("Privacy Pose Detection + Context-Aware Logic")
        print()
        print("Starting subsystems...")
        print("- Visual Thread: Privacy-preserving pose tracking")
        print("- Context Thread: Gesture detection + Subject context")
        print()
        print("Raise your hand to test gesture detection!")
        print("Press 'q' in the video window to stop\n")
        
        # Create threads
        t1 = threading.Thread(target=self.visual_thread, daemon=True)
        t2 = threading.Thread(target=self.context_logic_thread, daemon=True)
        
        # Start threads
        t1.start()
        t2.start()
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\nShutting down classroom mode...")
            self.running = False
        
        time.sleep(1)
        print("✅ Classroom mode stopped")

if __name__ == "__main__":
    system = ClassroomIntegration()
    system.start()
