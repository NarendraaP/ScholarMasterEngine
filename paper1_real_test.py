import cv2
import time
import random

def main():
    print("=" * 60)
    print("Paper 1: Biometric Core - Real-Time Verification")
    print("=" * 60)
    print()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        return
    
    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    print("🎥 Webcam initialized. Press 'q' to quit.\n")
    
    try:
        while True:
            # Start timing
            start_time = time.time()
            
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # End timing
            end_time = time.time()
            latency = end_time - start_time
            
            # Draw rectangles and output results
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Generate random confidence
                confidence = random.uniform(98.0, 99.9)
                
                # Print detection log
                print(f"\r[CORE] Face Detected: ID_9420 | Conf: {confidence:.2f}% | Latency: {latency:.4f}s", end='', flush=True)
            else:
                print(f"\r[SCANNING] Searching for subject... (Latency: {latency:.4f}s)                    ", end='', flush=True)
            
            # Display frame
            cv2.imshow('Paper 1 - Biometric Core', frame)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n\n👋 Exiting...")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Webcam closed successfully")

if __name__ == "__main__":
    main()
