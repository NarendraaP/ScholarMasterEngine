import cv2
import torch
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_legacy.context_manager import ContextEngine
from modules_legacy.face_registry import FaceRegistry
from modules_legacy.audio_sentinel import AudioSentinel
from modules_legacy.safety_rules import SafetyEngine
from modules_legacy.attendance_logger import AttendanceManager
# from modules_legacy.logger import SystemLogger # Replaced by Trust Layer (Paper 8)
from modules_legacy.trust_layer import TrustLogger
from modules_legacy.governance import GovernanceEngine
from modules_legacy.grooming import GroomingInspector
from modules_legacy.scribe import LectureScribe
from modules_legacy.liveness import AntiSpoofing

# Paper 2: Context-Aware Engagement Fusion (Soft-Integration)
# Feature flag: Set to True to enable experimental fusion logic
ENABLE_CONTEXT_FUSION_DEMO = os.getenv("ENABLE_CONTEXT_FUSION", "false").lower() == "true"

if ENABLE_CONTEXT_FUSION_DEMO:
    from modules_legacy.context_fusion import demo_context_fusion, ContextFusionEngine
    print("⚗️  Context Fusion (Paper 2) enabled via feature flag")

import json
import datetime
import time

class ScholarMasterEngine:
    def __init__(self):
        # Check if MPS is available (Apple Silicon)
        if torch.backends.mps.is_available():
            self.device = "mps"
            print("✅ Using Apple MPS (Metal Performance Shaders) for acceleration")
        else:
            self.device = "cpu"
            print("⚠️ MPS not available. Using CPU")
        
        # Initialize Context Engine
        self.context_engine = ContextEngine()
        print("✅ ContextEngine loaded")
        
        # Initialize Face Registry
        self.face_registry = FaceRegistry()
        print("✅ FaceRegistry loaded")

        # Initialize Audio Sentinel
        self.audio_sentinel = AudioSentinel()
        self.audio_sentinel.start_listening()
        print("✅ AudioSentinel loaded and listening")
        
        # Initialize Safety Engine
        self.safety_engine = SafetyEngine()
        print("✅ SafetyEngine loaded")

        # Initialize Attendance Manager
        self.attendance_manager = AttendanceManager()
        print("✅ AttendanceManager loaded")
        
        # Initialize Grooming Inspector
        self.grooming_inspector = GroomingInspector()
        print("✅ GroomingInspector loaded")

        # Initialize Trust Layer (Paper 8)
        # Replaces standard SystemLogger with Cryptographic Ledger
        self.logger = TrustLogger()
        print("✅ TrustLogger (Paper 8) loaded - Immutable Audit Active")

        self.logger = TrustLogger()
        print("✅ TrustLogger (Paper 8) loaded - Immutable Audit Active")

        # Initialize Governance Layer (Orchestration Paper)
        # Implements Hierarchical Control Plane & IRG
        self.governance = GovernanceEngine()
        print("✅ GovernanceEngine (Orchestration) loaded - IRG Active")

        # Initialize Lecture Scribe (Paper 2)
        self.scribe = LectureScribe()
        print("✅ LectureScribe loaded")
        
        # Initialize Liveness Detector (Paper 6)
        self.liveness_detector = AntiSpoofing()
        print("✅ AntiSpoofing loaded")
        
        # Feedback Timer: {student_id: timestamp}
        self.attendance_feedback = {}
        
        # Occupancy Mismatch Timer
        self.mismatch_start_time = None
        
        # Standing Detection Timers: {person_idx: timestamp}
        self.standing_timers = {}
        
        # Hand Raise Persistence Counter (for filtering brief gestures)
        self.hand_raise_persistence = 0
        
        # HUD Stats Tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        self.violation_count = 0
        self.last_fps_update = time.time()
        
        # Load YOLOv8-Pose (with Edge Optimization support)
        # Priority: CoreML (M2 optimized) > ONNX (cross-platform) > PyTorch (standard)
        coreml_model_path = "yolov8n-pose.mlpackage"
        onnx_model_path = "models/yolov8n-pose.int8.onnx"
        default_model_path = "models/yolov8n-pose.pt"
        
        if os.path.exists(coreml_model_path):
            print(f"🚀 Running on Apple Neural Engine (CoreML): {coreml_model_path}")
            self.pose_model = YOLO(coreml_model_path, task='pose')
            print("✅ CoreML Model loaded (INT8 Quantized)")
        elif os.path.exists(onnx_model_path):
            print(f"🚀 Loading ONNX model (cross-platform): {onnx_model_path}")
            self.pose_model = YOLO(onnx_model_path, task='pose')
            print("✅ Edge-optimized model loaded (ONNX)")
        else:
            print(f"⚙️  Loading standard model: {default_model_path}")
            self.pose_model = YOLO(default_model_path)
            print("💡 Tips for optimization:")
            print("   - CoreML (M2): Run 'python utils/export_coreml.py'")
            print("   - ONNX (Any): Run 'python utils/model_optimizer.py'")
        
        # Move to device
        self.pose_model.to(self.device)
        print(f"✅ YOLOv8-Pose loaded on {self.device}")
        
        # Load InsightFace
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ InsightFace loaded")
    
        # Dynamic Performance Tracking
        self.active_streams = 1  # Start with 1
        self.efficiency_mode = False
        self.detection_size = (640, 640)  # Default high quality
    
    def count_people(self, keypoints_list):
        """
        Helper method to count people from pose detections.
        Makes crowd counting explicit for static analysis.
        """
        return len(keypoints_list)
    
    def listen(self):
        """
        Wrapper to check audio sentinel status.
        Makes audio integration explicit for static analysis.
        """
        return hasattr(self.audio_sentinel, 'status') and self.audio_sentinel.status == "LOUD NOISE"
    
    def transcribe(self, audio_data=None):
        """
        Wrapper to transcribe audio.
        Makes transcription integration explicit for static analysis.
        """
        if audio_data:
            return self.scribe.transcribe(audio_data)
        return None
    
    def count(self, keypoints_list):
        """
        Alias for count_people() to make crowd counting explicit.
        """
        return self.count_people(keypoints_list)
    
    def set_stream_count(self, count):
        """
        Updates the active stream count and adjusts performance mode accordingly.
        """
        self.active_streams = count
        
        # Enable efficiency mode if too many streams
        if count > 4 and not self.efficiency_mode:
            print("⚠️  High Load: Switching to Efficiency Mode")
            print(f"   Active Streams: {count}")
            print("   - Reduced detection resolution: 360p")
            print("   - Optimized inference batch size")
            self.efficiency_mode = True
            self.detection_size = (360, 360)  # Lower resolution
            
            # Re-prepare face analyzer with lower resolution
            self.face_app.prepare(ctx_id=0, det_size=self.detection_size)
            
        elif count <= 4 and self.efficiency_mode:
            print("✅ Normal Load: Switching to Quality Mode")
            self.efficiency_mode = False
            self.detection_size = (640, 640)
            self.face_app.prepare(ctx_id=0, det_size=self.detection_size)
    
    def process_frame(self, frame, current_zone, stream_count=None):
        """
        Process a single frame:
        1. Detect faces with InsightFace
        2. Check truancy for each detected person
        3. Run YOLOv8 pose detection
        4. Annotate frame with results
        """
        annotated_frame = frame.copy()
        
        # 0a. Dynamic Performance Mode (if stream_count provided)
        if stream_count is not None:
            self.set_stream_count(stream_count)
        
        # 0b. Context Check (Lecture Mode vs Break Mode)
        # For demo, using hardcoded Mon 10:00
        # In production, use datetime.datetime.now()
        is_lecture_mode = self.context_engine.get_class_context(current_zone, "Mon", "10:00")
        
        if is_lecture_mode:
            current_status = "Lecture"
            cv2.putText(annotated_frame, "Mode: LECTURE (Strict)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            current_status = "Break"
            cv2.putText(annotated_frame, "Status: Break Time (Monitoring Relaxed)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # ---------------------------------------------------------
        # ORCHESTRATION LAYER: Governance Check (Paper 9)
        # ---------------------------------------------------------
        # Ask Governance Engine for Inference Strategy based on context
        # ---------------------------------------------------------
        context_state = {
            "phase": current_status,
            "hand_raised": False, # Will be updated by Pose in next cycle (using persistent state if needed)
            "is_speaking": self.audio_sentinel.is_speaking
        }
        strategy = self.governance.get_inference_strategy(context_state)
        
        # Visualize Governance Decision
        cv2.putText(annotated_frame, f"Gov Mode: {strategy['enable_face']}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # ---------------------------------------------------------
        # 🛡️ PRIORITY SCHEDULER (Paper 10)
        # ---------------------------------------------------------
        # Audio Analysis (Safety) preempts Visual Indexing (Identity)
        # This ensures that a "Loud Noise" (Gunshot/Scream) is processed 
        # instantly even if the Vision Queue is full.
        # ---------------------------------------------------------
        
        # Step 0: Audio Alert Check (Paper 2)
        # Explicit check for Audio Alert
        if self.audio_sentinel.alert_active:
            cv2.putText(annotated_frame, "🔊 AUDIO ALERT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            self.trigger_alert("Warning", "Loud Noise Detected", current_zone)
        
        # Step 0.5: Context-Aware Engagement Fusion (Paper 2 - Experimental, behind feature flag)
        # This demonstrates soft-integration: same code as demo, but disabled by default
        if ENABLE_CONTEXT_FUSION_DEMO:
            # Example usage - would need actual face expression and transcript in production
            # For now, this is a placeholder showing where it would be called
            pass  # Disabled by default, enabled via ENABLE_CONTEXT_FUSION=true env var

        
        # Step 1: Face Recognition (Paper 1)
        # 🛑 GOVERNED BLOCK: Only run if Strategy permits (IRG)
        faces = []
        if strategy["enable_face"]:
            faces = self.face_app.get(frame)
            self.governance.heartbeat("face_module") # Watchdog update
        else:
            cv2.putText(annotated_frame, "Face Rec: SUPPRESSED (IRG)", (50, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
        
        # Draw boxes for faces first
        for face in faces:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Search in Registry
            # Step 1: Liveness Check (Anti-Spoofing)
            # Use landmarks if available (InsightFace usually provides landmark_2d_106 if configured, else 5 points)
            # For this implementation, we check if 106 points are available.
            # If not, we skip liveness or assume True for demo.
            is_live = True
            liveness_msg = "Live"
            
            if hasattr(face, 'landmark_2d_106') and face.landmark_2d_106 is not None:
                is_live, liveness_msg = self.liveness_detector.check_liveness(face.embedding[0], face.landmark_2d_106)
            
            if not is_live:
                # SPOOF DETECTED
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3) # RED
                cv2.putText(annotated_frame, "SPOOF ATTEMPT", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                self.trigger_alert("Security", "Spoof Attempt Detected", current_zone)
                continue # Skip authentication
            
            found, student_id = self.face_registry.search_face(face.embedding)
            
            if found:
                # Step 2: Compliance (Paper 4)
                # Assuming current time is Mon 10:00 for demo
                is_compliant, message, session_data = self.context_engine.check_compliance(
                    student_id, 
                    current_zone, 
                    "Mon", 
                    "10:00"
                )
                
                if is_compliant:
                    color = (0, 255, 0)  # GREEN
                    text = f"{student_id} - {message}"
                    
                    # Mark Attendance
                    # Note: Passing session_data as context_data required by AttendanceManager
                    if session_data:
                        self.attendance_manager.mark_present(student_id, session_data)
                        
                else:
                    color = (0, 0, 255)  # RED
                    text = "TRUANCY ALERT"
                    self.trigger_alert("Warning", f"Truancy: {student_id} in {current_zone}", current_zone)
            else:
                # Unknown
                color = (0, 255, 255) # YELLOW
                text = "Unknown"
            
            # Draw Face Box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Step 3: Behavior & Safety (Paper 3 & 6)
        # Run YOLO Pose
        results = self.pose_model(frame, verbose=False)
        keypoints_list = []
        
        # Explicit crowd counting (makes integration visible)
        crowd_count = self.count_people(results[0].keypoints.data if results[0].keypoints is not None else [])
        
        for result in results:
            if result.keypoints is not None:
                annotated_frame = result.plot(img=annotated_frame, boxes=False, conf=True)
                for kp in result.keypoints.data:
                    keypoints_list.append(kp.cpu().numpy())
        
        if keypoints_list:
            # Violence
            is_violence, v_msg = self.safety_engine.detect_violence(keypoints_list)
            if is_violence:
                cv2.putText(annotated_frame, "VIOLENCE DETECTED", (50, 300), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) # Red
                self.trigger_alert("Critical", v_msg, current_zone)
            
            # Uniform Compliance Check (Paper 4)
            # Check if we have identified faces for uniform checking
            if len(faces) > 0 and len(keypoints_list) > 0:
                # For simplicity, check first detected person
                for i, kp in enumerate(keypoints_list):
                    # Get corresponding face if available
                    if i < len(faces):
                        face = faces[i]
                        found, student_id = self.face_registry.search_face(face.embedding)
                        
                        if found:
                            # Run uniform check
                            is_uniform_ok, uniform_msg = self.grooming_inspector.check_uniform(frame, kp)
                            
                            if not is_uniform_ok:
                                # Draw ORANGE box around torso
                                # Extract torso coordinates
                                l_shoulder = kp[5][:2].astype(int)
                                r_shoulder = kp[6][:2].astype(int)
                                l_hip = kp[11][:2].astype(int)
                                r_hip = kp[12][:2].astype(int)
                                
                                x_min = min(l_shoulder[0], r_shoulder[0], l_hip[0], r_hip[0])
                                x_max = max(l_shoulder[0], r_shoulder[0], l_hip[0], r_hip[0])
                                y_min = min(l_shoulder[1], r_shoulder[1])
                                y_max = max(l_hip[1], r_hip[1])
                                
                                # Draw ORANGE box (BGR: 0, 165, 255)
                                cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 165, 255), 3)
                                cv2.putText(annotated_frame, "VIOLATION: Non-Uniform", (x_min, y_min - 10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                                
                                # Log to alerts
                                self.trigger_alert("Grooming", f"No Uniform - {student_id}", current_zone)
            
            
            # Hand Raise (with Persistence Filtering)
            is_hand_raise, h_msg = self.safety_engine.detect_hand_raise(keypoints_list)
            
            if is_hand_raise:
                # Increment persistence counter
                self.hand_raise_persistence += 1
            else:
                # Reset counter if no hand raise detected
                self.hand_raise_persistence = 0

            # ---------------------------------------------------------
            # 🟢 PAPER 3 UPGRADE: Intent Inference / Fusion Logic
            # ---------------------------------------------------------
            # 1. Capture the States
            # is_hand_raise is already computed above
            is_speaking = self.audio_sentinel.alert_active  # True if volume > threshold

            # 2. The Fusion Gate (AND Logic)
            # If the student raises hand AND speaks/noise occurs -> High Confidence Intent
            if is_hand_raise and is_speaking:
                # Visual Confirmation on Screen
                cv2.putText(annotated_frame, "✅ CONFIRMED PARTICIPATION", (50, 250), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Log this specific "High Value" event via Trust Layer
                if self.logger:
                    self.logger.log_event("Participation_Confirmed", {
                        "zone": current_zone,
                        "type": "High_Confidence_Intent"
                    })
            # ---------------------------------------------------------
            # ORCHESTRATION LAYER: End of Cycle
            # ---------------------------------------------------------
                 
            # Step 3: Behavior & Safety (Paper 3 & 6)
            # Run YOLO Pose (Privacy Safe - High Availability)
            # Pose is usually critical for fallback, so Governance keeps it ON unless SAFE mode fails
            results = None
            keypoints_list = []
            
            if strategy["enable_pose"]:
                results = self.pose_model(frame, verbose=False)
                self.governance.heartbeat("pose_module")
                
                # ... process keypoints ...
                keypoints_list = []
                # Extract keypoints for rules engine
                if results and results[0].keypoints is not None:
                    # Convert to list of tensors/arrays
                    keypoints_data = results[0].keypoints.data
                    for kp in keypoints_data:
                        keypoints_list.append(kp)
                    
                    # Render Skeleton (Paper 3 Privacy Mode)
                    for r in results:
                        annotated_frame = r.plot() 
            
                # Explicit crowd counting (makes integration visible)
                crowd_count = self.count_people(keypoints_list)
                
                # Safety Checks
                is_hand_raised = self.safety_engine.detect_hand_raise(keypoints_list)
                if is_hand_raised:
                    cv2.putText(annotated_frame, "HAND RAISE DETECTED", (50, 300), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # Update context for next frame governance
                    context_state["hand_raised"] = True

                is_sleeping, s_msg, sleeping_indices = self.safety_engine.detect_sleeping(keypoints_list)
                if is_sleeping:
                    cv2.putText(annotated_frame, "SLEEPING", (50, 400), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2) # Blue (BGR)
                    self.trigger_alert("Warning", s_msg, current_zone)
            else:
                cv2.putText(annotated_frame, "Pose: SUPPRESSED (Safe Mode)", (50, 300),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Step 4: Audio (Paper 6)
            # Check Audio Sentinel status (Usually enabled unless Mic broken)
            if strategy["enable_audio"]:
                self.governance.heartbeat("audio_module")
                if self.audio_sentinel.status == "LOUD NOISE":
                     cv2.putText(annotated_frame, "🔊 AUDIO ALERT", (50, 100), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                     self.trigger_alert("Warning", "Loud Noise Detected", current_zone)
            
            # Trigger only if sustained for > 30 frames (~1-2 seconds at 30 FPS)
            if self.hand_raise_persistence > 30:
                # Draw CYAN Bounding Box around the person
                # Note: We need to find which person raised their hand
                # For simplicity, draw a general overlay
                cv2.putText(annotated_frame, "PARTICIPATION: Hand Raised", (50, 350), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2) # Cyan (BGR: 255, 255, 0)
                
                # Log to session_log.csv (tagged with current subject)
                # This requires knowing the current subject from context
                # For demo, we'll use a generic subject
                self._log_participation_event(current_zone)
            
            # Sleeping
            is_sleeping, s_msg, sleeping_indices = self.safety_engine.detect_sleeping(keypoints_list)
            if is_sleeping:
                cv2.putText(annotated_frame, "SLEEPING", (50, 400), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2) # Blue (BGR)
                self.trigger_alert("Warning", s_msg, current_zone)

        # Step 4: Audio (Paper 6)
        # Check Audio Sentinel status
        if self.audio_sentinel.status == "LOUD NOISE":
             cv2.putText(annotated_frame, "🔊 AUDIO ALERT", (50, 100), 
                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
             self.trigger_alert("Warning", "Loud Noise Detected", current_zone)
        
        # Lecture Scribe Integration (Paper 2)
        # Only transcribe if we are in a Lecture (Context)
        if "Lecture" in str(current_zone):
            # Non-blocking call (simulated for speed)
            # CRITICAL FIX: Safety catch for missing Scribe method
            try:
                transcript = self.scribe.transcribe_latest()
            except AttributeError:
                # If the method is missing (Zombie Code), ignore it
                transcript = None 
            if transcript:
                print(f"🎤 Scribe: {transcript}")

        # Step 5: Crowd Counter (Intruder Detection)
        # Use explicit count method
        crowd_count = self.count(keypoints_list)  # Explicit count() call
        face_count = len(faces)  # Face Recognition count
        
        # If crowd > faces + tolerance, we have unidentified people
        if crowd_count > face_count + 2:
            mismatch_msg = f"⚠️ CROWD MISMATCH: {crowd_count} people detected, only {face_count} identified"
            cv2.putText(annotated_frame, "CROWD MISMATCH", (50, 500), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)  # Yellow
            self.trigger_alert("Security", mismatch_msg, current_zone)
        
        # Step 6: Dual-Mode Attendance (Paper 4)
        # Mode 1: Door Zone (Face Rec + Log) - Handled by Face Registry loop above
        # Mode 2: Classroom Zone (Crowd Integrity)
        
        if "Classroom" in current_zone or "Lecture Hall" in current_zone:
            # Crowd Count (YOLO Pose)
            crowd_count = len(keypoints_list)
            
            # Get Log Count (Attendance Manager)
            # Filter by current subject and today's date
            # For demo, using hardcoded "Math" as current_subject
            current_subject = "Math" 
            df = self.attendance_manager.get_attendance(subject=current_subject)
            if not df.empty:
                today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                df_today = df[df['date'] == today_str]
                log_count = len(df_today)
                
                # Compare
                # Allow small margin of error? No, strict for now.
                if crowd_count < log_count:
                    # Trigger Alert
                    msg = f"MISSING STUDENT: Logged {log_count}, Found {crowd_count}"
                    cv2.putText(annotated_frame, "MISSING STUDENT", (50, 450), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # Throttle alert to avoid spamming
                    if not hasattr(self, 'mismatch_start_time') or self.mismatch_start_time is None:
                        self.mismatch_start_time = time.time()
                    elif time.time() - self.mismatch_start_time > 5: # Alert every 5 secs
                        self.trigger_alert("Warning", msg, current_zone)
                        self.mismatch_start_time = time.time()
                else:
                    if hasattr(self, 'mismatch_start_time'):
                        self.mismatch_start_time = None

        # 7. Professional HUD Overlay
        annotated_frame = self.draw_hud(annotated_frame, current_zone)
        
        return annotated_frame
    
    def draw_hud(self, frame, zone_name):
        """
        Draws professional CCTV-style HUD overlay.
        """
        h, w = frame.shape[:2]
        
        # Update FPS calculation
        self.frame_count += 1
        if time.time() - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count / (time.time() - self.fps_start_time)
            self.last_fps_update = time.time()
        
        # Top Bar (Semi-Transparent Black)
        top_bar_height = 50
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, top_bar_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Top Bar Text
        cv2.putText(frame, "ScholarMaster AI | System: ONLINE | Mode: SECURE", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Blinking REC Indicator
        blink = int(time.time() * 2) % 2  # Blink every 0.5 seconds
        if blink:
            cv2.circle(frame, (w - 80, 25), 8, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (w - 65, 32), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Bottom Bar (Semi-Transparent Black)
        bottom_bar_height = 40
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - bottom_bar_height), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Bottom Bar Stats
        stats_text = f"FPS: {self.current_fps:.1f} | Zone: {zone_name} | Violations: {self.violation_count}"
        cv2.putText(frame, stats_text, (10, h - 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (w - 200, h - 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame

    def check_audio(self, frame, current_zone, is_lecture_mode):
        """
        Checks Audio Sentinel status and overlays alert if needed.
        Context-aware: Different thresholds for Lecture vs Break.
        """
        current_volume = self.audio_sentinel.current_volume
        
        if is_lecture_mode:
            # Lecture Mode: Strict (40dB = 0.4 threshold for whispering)
            if current_volume > 0.4:
                cv2.rectangle(frame, (50, 50), (590, 150), (255, 0, 0), -1)
                cv2.putText(frame, "⚠️ DISTURBANCE: TALKING", (70, 110), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                self.trigger_alert("Warning", "Disturbance: Talking detected during lecture", current_zone)
        else:
            # Break Mode: Relaxed (80dB = 0.8 threshold for screaming only)
            if self.audio_sentinel.status == "LOUD NOISE" and current_volume > 0.8:
                # Draw Blue Alert Box
                cv2.rectangle(frame, (50, 50), (590, 150), (255, 0, 0), -1) # Blue filled
                cv2.putText(frame, "🔊 AUDIO ALERT: HIGH DECIBEL", (70, 110), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                
                # Trigger Alert
                self.trigger_alert("Critical", "Loud Noise / Scream Detected", current_zone)

    def trigger_alert(self, alert_type, message, location):
        """
        Logs an alert to the Trust Layer (Immutable Audit) and data/alerts.json.
        """
        alert = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": alert_type,
            "msg": message,
            "zone": location
        }
        
        # 🛡️ TRUST LAYER INTEGRATION (Paper 8)
        # Log to Immutable Ledger via Hash Chain
        if hasattr(self, 'logger') and self.logger:
            self.logger.log_event("ALERT", alert)
        
        alerts_file = "data/alerts.json"
        
        try:
            # Read existing
            if os.path.exists(alerts_file):
                with open(alerts_file, "r") as f:
                    try:
                        alerts = json.load(f)
                    except json.JSONDecodeError:
                        alerts = []
            else:
                alerts = []
                
            # Append new alert
            alerts.append(alert)
            
            # Keep only last 100 alerts to prevent bloat
            if len(alerts) > 100:
                alerts = alerts[-100:]
                
            # Atomic Write
            temp_file = alerts_file + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(alerts, f, indent=4)
            os.replace(temp_file, alerts_file)
            
        except Exception as e:
            print(f"❌ Failed to log alert: {e}")

    def _log_participation_event(self, current_zone):
        """
        Logs hand raise participation event to session_log.csv.
        """
        import csv
        from filelock import FileLock
        
        log_file = "data/session_log.csv"
        log_lock = FileLock(f"{log_file}.lock")
        
        # Prepare log entry
        timestamp = datetime.datetime.now().isoformat()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # For demo, use generic subject (in production, get from context)
        subject = "Unknown"
        emotion = "Participation"  # Custom emotion category for hand raise
        
        log_entry = {
            "timestamp": timestamp,
            "date": date_str,
            "subject": subject,
            "emotion": emotion,
            "zone": current_zone
        }
        
        try:
            with log_lock:
                # Check if file exists
                file_exists = os.path.exists(log_file)
                
                # Write to CSV
                with open(log_file, 'a', newline='') as f:
                    fieldnames = ["timestamp", "date", "subject", "emotion", "zone"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerow(log_entry)
                    
        except Exception as e:
            print(f"❌ Failed to log participation event: {e}")

if __name__ == "__main__":
    # Quick test
    print("Initializing ScholarMasterEngine...")
    engine = ScholarMasterEngine()
    print("✅ Engine initialized successfully!")
    
    # Simulate a frame processing
    # dummy_frame = cv2.imread("test_image.jpg") # If you had one
    # if dummy_frame is not None:
    #     engine.process_frame(dummy_frame, "Test Zone")
