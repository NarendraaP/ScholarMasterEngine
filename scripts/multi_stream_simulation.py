import cv2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import threading
import time
import json
import os
import numpy as np
from modules.master_engine import ScholarMasterEngine
from utils.video_utils import ThreadedCamera

# Configuration
CONFIG_FILE = "data/zones_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return []
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def main():
    print("🚀 Starting Multi-Stream Simulation...")
    
    # Load Config
    cameras_config = load_config()
    print(f"✅ Loaded {len(cameras_config)} Cameras from Config")
    
    # Initialize Engine
    engine = ScholarMasterEngine()
    
    # Initialize Cameras
    cameras = []
    for cam_conf in cameras_config:
        print(f"🔌 Connecting to {cam_conf['id']} ({cam_conf['zone']})...")
        cam = ThreadedCamera(cam_conf['source'], cam_conf['zone'])
        cameras.append(cam)
        
    print("🎥 Streams Active. Press 'q' to quit.")
    
    try:
        while True:
            # Create a grid layout (simplistic 2x2 for now)
            # For simplicity in this script, we'll just show separate windows or iterate
            # Let's try to stitch them if possible, or just process sequentially
            
            # Grid Display Logic
            frames_to_display = []
            
            for i, cam in enumerate(cameras):
                frame = cam.get_frame()
                if frame is not None:
                    # Process Frame with AI Engine
                    annotated_frame = engine.process_frame(frame, current_zone=cam.zone_name)
                    # Resize to standard size for grid
                    display_frame = cv2.resize(annotated_frame, (640, 480))
                else:
                    # Placeholder if no frame
                    display_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(display_frame, f"Waiting for {cam.zone_name}...", (50, 240), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                frames_to_display.append(display_frame)
            
            # Ensure we have 4 frames for 2x2 grid (pad if needed)
            while len(frames_to_display) < 4:
                frames_to_display.append(np.zeros((480, 640, 3), dtype=np.uint8))
            
            # Create Grid
            # Top Row: 0, 1
            top_row = np.hstack((frames_to_display[0], frames_to_display[1]))
            # Bottom Row: 2, 3
            bottom_row = np.hstack((frames_to_display[2], frames_to_display[3]))
            # Full Grid
            grid = np.vstack((top_row, bottom_row))
            
            # Resize grid to fit screen if needed (optional)
            # grid = cv2.resize(grid, (1280, 960))
            
            cv2.imshow("Scholar Master Engine - Live Control Center", grid)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("🛑 Stopping...")
    finally:
        for cam in cameras:
            cam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
