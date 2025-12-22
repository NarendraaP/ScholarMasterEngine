import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.video_utils import ThreadedCamera

class CameraManager:
    def __init__(self, config_path="data/zones_config.json"):
        self.config_path = config_path
        self.cameras = {} # {zone_name: ThreadedCamera}
        self.config = self._load_config()
        
    def _load_config(self):
        if not os.path.exists(self.config_path):
            print(f"⚠️ Zones config not found at {self.config_path}. Returning empty config.")
            return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load zones config: {e}")
            return {}

    def start_streams(self):
        """
        Initializes and starts all cameras defined in the config.
        """
        print("🔌 Initializing Camera Streams...")
        
        for cam_config in self.config:
            zone_name = cam_config.get("zone")
            source = cam_config.get("source")
            
            if source is None or zone_name is None:
                print(f"⚠️ Skipping config entry: Missing source or zone")
                continue
                
            print(f"   - Connecting to {zone_name} (Source: {source})...")
            
            # Create and start camera (ThreadedCamera handles the thread)
            try:
                cam = ThreadedCamera(source, zone_name)
                self.cameras[zone_name] = cam
            except Exception as e:
                print(f"❌ Failed to start camera for {zone_name}: {e}")

        print(f"✅ {len(self.cameras)} streams active.")

    def get_frames(self):
        """
        Returns a dictionary of latest frames from all active cameras.
        Format: {zone_name: frame}
        """
        frames = {}
        for zone_name, cam in self.cameras.items():
            frame = cam.get_frame()
            if frame is not None:
                frames[zone_name] = frame
        return frames

    def stop_all(self):
        """
        Stops all camera threads.
        """
        print("🛑 Stopping all streams...")
        for cam in self.cameras.values():
            cam.stop()
        print("✅ All streams stopped.")

if __name__ == "__main__":
    # Test
    manager = CameraManager()
    manager.start_streams()
    
    # Run for a few seconds then stop
    import time
    try:
        for i in range(5):
            frames = manager.get_frames()
            print(f"Loop {i}: Got {len(frames)} frames")
            time.sleep(1)
    finally:
        manager.stop_all()
