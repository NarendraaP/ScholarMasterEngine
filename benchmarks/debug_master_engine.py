import cv2
import numpy as np
import sys
import os

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_legacy.master_engine import ScholarMasterEngine

def test_engine():
    print("🚀 Initializing Engine...")
    engine = ScholarMasterEngine()
    
    # Create dummy frame
    frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    print("🎥 Processing Frame...")
    try:
        # Should crash if current_status is undefined
        engine.process_frame(frame, "Zone_A") 
        print("✅ Frame Processed Successfully")
    except Exception as e:
        print(f"❌ CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engine()
