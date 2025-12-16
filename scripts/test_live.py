import cv2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.master_engine import ScholarMasterEngine

def main():
    print("="*60)
    print("ScholarMasterEngine - Live Webcam Test")
    print("="*60)
    print()
    
    # Initialize the engine
    print("Initializing ScholarMasterEngine...")
    engine = ScholarMasterEngine()
    
    # Start Audio Sentinel
    print("Starting Audio Sentinel...")
    engine.audio_sentinel.start_listening()
    
    print()
    print("="*60)
    print("Starting webcam feed...")
    print("Press 'q' to quit")
    print("="*60)
    print()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        return
    
    # Set resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Error: Could not read frame")
            break
        
        frame_count += 1
        
        # Process frame with hardcoded zone "Canteen" to trigger truancy
        # (Since the schedule expects students in "Lab 1" at Mon 10:00)
        annotated_frame = engine.process_frame(frame, current_zone="Canteen")
        
        # Add frame info
        cv2.putText(
            annotated_frame,
            f"Frame: {frame_count} | Zone: Canteen",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Display the frame
        cv2.imshow('ScholarMasterEngine - Live Feed', annotated_frame)
        
        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n👋 Exiting...")
            break
    
    # Cleanup
    engine.audio_sentinel.stop_listening()
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Webcam closed successfully")

if __name__ == "__main__":
    main()
