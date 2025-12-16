import cv2
import numpy as np
import time
import sys

# Core Modules
from modules.camera_manager import CameraManager
from modules.master_engine import ScholarMasterEngine
from modules.notification_service import NotificationDispatcher

def main():
    print("===========================================")
    print("🎓 SCHOLAR MASTER ENGINE - SYSTEM STARTUP 🎓")
    print("===========================================")
    
    # 1. Initialize Notification Service
    try:
        notifier = NotificationDispatcher()
        notifier.start()
        print("✅ Notification Service: ONLINE")
    except Exception as e:
        print(f"❌ Notification Service Failed: {e}")
        return

    # 2. Initialize Master AI Engine
    try:
        engine = ScholarMasterEngine()
        print("✅ AI Engine: ONLINE")
    except Exception as e:
        print(f"❌ AI Engine Initialization Failed: {e}")
        notifier.stop()
        return

    # 3. Initialize Camera Manager
    try:
        cam_mgr = CameraManager()
        cam_mgr.start_streams()
        print("✅ Camera Manager: ONLINE")
    except Exception as e:
        print(f"❌ Camera Manager Failed: {e}")
        notifier.stop()
        return

    print("\n🚀 SYSTEM LIVE. Press 'q' to exit.\n")
    
    try:
        while True:
            # 1. Get Frames from all cameras
            frames = cam_mgr.get_frames()
            
            if not frames:
                # No cameras active or ready yet
                time.sleep(0.1)
                continue
            
            processed_frames = []
            
            # 2. Process each frame
            for zone_name, frame in frames.items():
                if frame is None: 
                    continue
                
                # Copy frame to ensure thread safety during processing if needed
                # (Engine usually returns a copy or modifies in place, better to send copy if visualizing raw elsewhere)
                
                # Run AI
                # This will detect faces, pose, check compliance, log attendance, etc.
                annotated_frame = engine.process_frame(frame, current_zone=zone_name)
                
                # Resize for grid display (optional, keeps grid uniform)
                # Let's standardize to 640x480 for display
                resized = cv2.resize(annotated_frame, (640, 480))
                processed_frames.append(resized)
            
            # 3. Stitch Frames for Display
            if processed_frames:
                # Simple Horizonital Stacking for MVP
                # A proper grid logic would be better for > 3 cameras
                if len(processed_frames) == 1:
                    final_display = processed_frames[0]
                else:
                    # Stack horizontally provided they have same height (resized above)
                    try:
                        final_display = np.hstack(processed_frames)
                    except ValueError:
                        # Fallback if dimensions mismatch despite resize
                        final_display = processed_frames[0]
                
                # 4. Show Display directly via CV2
                cv2.imshow("ScholarMaster Control Center", final_display)
                
            # 5. Handle User Input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("🛑 User requested quit.")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Keyboard Interrupt detected.")
        
    finally:
        # Cleanup
        print("🔻 Shutting down system...")
        cam_mgr.stop_all()
        notifier.stop()
        cv2.destroyAllWindows()
        print("✅ Cleanup Complete. Goodbye.")

if __name__ == "__main__":
    main()
