import cv2
import sounddevice as sd
import numpy as np
import threading
import time
import sqlite3
import random
from datetime import datetime

class IntegratedSystem:
    """
    ARCHITECTURE B: NAIVE EDGE INTEGRATION (INTERMEDIATE PROTOTYPE)
    ================================================================
    This module represents the "Baseline" integrated system using:
    - 1. Haar Cascade Classifiers (Legacy CV)
    - 2. SQLite Database (Disk/Memory)
    - 3. Linear Logic Flow
    
    Status: REFERENCE ONLY. See 'main_unified.py' for SOTA implementation.
    """
    
    def __init__(self):
        # Shared state variables
        self.current_subject = "NO_DETECTION"
        self.threat_detected = False
        self.audio_level = 0.0
        self.video_fps = 0.0
        self.governance_status = "INITIALIZING"
        self.running = True
        
        # Thread locks
        self.lock = threading.Lock()
        
        # Database setup
        self.setup_database()
    
    def setup_database(self):
        """Initialize in-memory database with schedule rules"""
        self.db_conn = sqlite3.connect(':memory:', check_same_thread=False)
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE Schedule (
                Student_ID TEXT,
                Expected_Zone TEXT,
                Time TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO Schedule VALUES ('ID_9420', 'Zone_1', '10:00')
        ''')
        self.db_conn.commit()
    
    def video_thread(self):
        """Thread 1: Real-time face detection"""
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            with self.lock:
                self.current_subject = "CAMERA_ERROR"
            return
        
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            # Update shared state
            with self.lock:
                if len(faces) > 0:
                    self.current_subject = "ID_9420"
                else:
                    self.current_subject = "NO_DETECTION"
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    self.video_fps = 30 / elapsed if elapsed > 0 else 0
                    start_time = time.time()
                    frame_count = 0
            
            time.sleep(0.03)  # ~30 FPS
        
        cap.release()
    
    def audio_thread(self):
        """Thread 2: Real-time audio monitoring"""
        sample_rate = 44100
        duration = 0.1
        threshold_db = 80
        
        while self.running:
            try:
                # Record audio chunk
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()
                
                # Calculate dB
                rms = np.sqrt(np.mean(audio_data**2))
                db = 20 * np.log10(rms) + 60 if rms > 0 else 0
                
                # Update shared state
                with self.lock:
                    self.audio_level = db
                    self.threat_detected = db > threshold_db
                
                time.sleep(0.1)
            except Exception as e:
                time.sleep(0.5)
    
    def governance_thread(self):
        """Thread 3: Schedule compliance checking"""
        while self.running:
            time.sleep(5)  # Check every 5 seconds
            
            with self.lock:
                subject = self.current_subject
            
            if subject != "NO_DETECTION" and subject != "CAMERA_ERROR":
                # Query schedule
                cursor = self.db_conn.cursor()
                cursor.execute('''
                    SELECT Expected_Zone, Time FROM Schedule 
                    WHERE Student_ID = ?
                ''', (subject,))
                result = cursor.fetchone()
                
                if result:
                    expected_zone, expected_time = result
                    current_time = datetime.now().strftime("%H:%M")
                    
                    # Simulate zone detection (for demo)
                    detected_zone = "Zone_1"  # Assume correct for now
                    
                    with self.lock:
                        if detected_zone == expected_zone:
                            self.governance_status = "MATCH"
                        else:
                            self.governance_status = f"VIOLATION: Expected {expected_zone}"
                else:
                    with self.lock:
                        self.governance_status = "UNKNOWN_SUBJECT"
    
    def dashboard_thread(self):
        """Thread 4: Display clean status dashboard"""
        while self.running:
            with self.lock:
                subject = self.current_subject
                fps = self.video_fps
                audio_db = self.audio_level
                threat = self.threat_detected
                gov_status = self.governance_status
            
            # Clear screen (ANSI escape code)
            print("\033[H\033[J", end="")
            
            # Print dashboard
            print("=" * 70)
            print("SCHOLAR MASTER ENGINE - INTEGRATED SYSTEM DASHBOARD")
            print("=" * 70)
            print()
            
            # Video status
            video_status = "Active" if subject != "CAMERA_ERROR" else "ERROR"
            print(f"[VIDEO]:  {video_status:10} ({fps:4.1f} FPS) | Subject: {subject}")
            
            # Audio status
            audio_status = "🚨 THREAT" if threat else "SECURE"
            print(f"[AUDIO]:  {audio_status:10} ({audio_db:5.1f} dB) | Status: {'ALERT' if threat else 'Quiet'}")
            
            # Governance status
            print(f"[LOGIC]:  Checking Schedule... [{gov_status}]")
            
            print()
            print("Press Ctrl+C to stop")
            
            time.sleep(1)
    
    def start(self):
        """Start all threads"""
        print("Initializing Scholar Master Engine...")
        print("Starting all subsystems...\n")
        time.sleep(1)
        
        # Create threads
        t1 = threading.Thread(target=self.video_thread, daemon=True)
        t2 = threading.Thread(target=self.audio_thread, daemon=True)
        t3 = threading.Thread(target=self.governance_thread, daemon=True)
        t4 = threading.Thread(target=self.dashboard_thread, daemon=True)
        
        # Start threads
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down system...")
            self.running = False
            self.db_conn.close()
            time.sleep(1)
            print("✅ System stopped")

if __name__ == "__main__":
    system = IntegratedSystem()
    system.start()
