import cv2
import mediapipe as mp
import numpy as np

def main():
    print("=" * 60)
    print("Paper 3: Privacy-Preserving Pose Detection")
    print("=" * 60)
    print("Demonstrating Anonymous Skeleton Visualization")
    print("Press 'q' to quit\n")
    
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize webcam
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
    
    print(f"🎥 Webcam initialized ({frame_width}x{frame_height})")
    print("🔒 Privacy Mode: Only skeleton landmarks visible\n")
    
    with mp_pose.Pose(
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3) as pose:
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Error: Could not read frame")
                    break
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose detection
                results = pose.process(rgb_frame)
                
                # Create BLACK background (privacy-safe)
                privacy_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                
                # Draw pose landmarks on BLACK background
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        privacy_frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    
                    # Add privacy indicator
                    cv2.putText(privacy_frame, "PRIVACY MODE: ACTIVE", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(privacy_frame, "Anonymous Skeleton Only", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                else:
                    # No pose detected
                    cv2.putText(privacy_frame, "CAMERA: ACTIVE", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(privacy_frame, "No pose detected", 
                                (frame_width//2 - 100, frame_height//2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                    cv2.putText(privacy_frame, "Stand in front of camera", 
                                (frame_width//2 - 150, frame_height//2 + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
                
                # Display the privacy-safe frame
                cv2.imshow('Paper 3 - Privacy Pose (Anonymous)', privacy_frame)
                
                # Check for 'q' key to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Exiting...")
                    break
        
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✅ Privacy demonstration complete")

if __name__ == "__main__":
    main()
