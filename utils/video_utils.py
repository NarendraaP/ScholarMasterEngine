import cv2
import threading
import time
import os

class ThreadedCamera:
    def __init__(self, source, zone_name):
        self.source = source
        self.zone_name = zone_name
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # Initialize capture
        self._connect()
            
        # Start thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def _connect(self):
        """Helper to connect/reconnect to the source."""
        if isinstance(self.source, str) and self.source.isdigit():
            self.capture = cv2.VideoCapture(int(self.source))
        else:
            self.capture = cv2.VideoCapture(self.source)

    def update(self):
        while self.running:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                else:
                    # If file, loop it
                    if isinstance(self.source, str) and os.path.exists(self.source):
                        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        # Reconnection Logic for Streams
                        print(f"⚠️ Connection lost to {self.zone_name}. Reconnecting in 2s...")
                        time.sleep(2)
                        try:
                            self.capture.release()
                            self._connect()
                            if self.capture.isOpened():
                                print(f"✅ Reconnected to {self.zone_name}")
                        except Exception as e:
                            print(f"❌ Reconnection failed: {e}")
            else:
                # Capture not opened, try to reconnect
                print(f"⚠️ Camera {self.zone_name} not open. Retrying in 2s...")
                time.sleep(2)
                try:
                    self._connect()
                except:
                    pass
            
            # Small sleep to prevent CPU spin if failing fast
            time.sleep(0.01)

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.capture.release()
