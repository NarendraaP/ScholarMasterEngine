import cv2
import numpy as np
import time
import os

def create_video():
    # Ensure data dir exists
    if not os.path.exists("data"):
        os.makedirs("data")

    width, height = 640, 480
    fps = 30
    duration = 5
    output_path = 'data/test_video.mp4'

    # codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("Error: Could not create video writer. Trying 'avc1' codec...")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Generating video at {output_path}...")
    
    start_time = time.time()
    
    for i in range(fps * duration):
        # Black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add timestamps and frame count
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        text = f"TEST VIDEO | {timestamp} | Frame: {i}"
        
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Moving circle animation
        x = int((i * 10) % width)
        y = int(height // 2 + 50 * np.sin(i / 10.0))
        cv2.circle(frame, (x, y), 30, (0, 255, 0), -1)
        
        # Simulation text
        cv2.putText(frame, "SIMULATION MODE", (180, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        out.write(frame)

    out.release()
    
    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ Successfully created {output_path} ({size_kb:.1f} KB)")
    else:
        print(f"❌ Failed to create {output_path}")

if __name__ == "__main__":
    create_video()
