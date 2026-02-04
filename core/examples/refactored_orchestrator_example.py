"""
ScholarMaster Unified - Thin Orchestrator (Refactored)

This is an EXAMPLE of how main_unified.py should look after refactoring.
Shows dependency wiring using the new core/ architecture.

BEFORE: 835 lines with embedded logic
AFTER: ~150 lines, pure orchestration
"""
import cv2
import threading
from datetime import datetime

# Core Interfaces (depend on abstractions, NOT implementations)
from core.interfaces.i_face_recognizer import IFaceRecognizer
from core.interfaces.i_audio_analyzer import IAudioAnalyzer
from core.interfaces.i_schedule_repository import IScheduleRepository
from core.interfaces.i_alert_service import IAlertService

# Infrastructure Adapters (concrete implementations)
from core.infrastructure.sensing.vision.face_recognizer import FaceRecognizer

from core.infrastructure.sensing.audio.audio_analyzer import AudioAnalyzer
from core.infrastructure.persistence.repositories.schedule_repository import CSVScheduleRepository
from core.infrastructure.persistence.repositories.json_student_repository import JsonStudentRepository
from core.infrastructure.notifications.alert_service import JSONAlertService

# Application Use Cases
from core.application.use_cases.detect_truancy_use_case import DetectTruancyUseCase
from core.application.use_cases.mark_attendance_use_case import MarkAttendanceUseCase

# Domain Rules (for UI logic only)
from core.domain.rules.alert_rules import AlertRules


class ScholarMasterUnified:
    """
    Thin orchestrator - wires dependencies and manages threads.
    
    NO business logic here - all delegated to use cases.
    """
    
    def __init__(self):
        print("🚀 Initializing ScholarMaster Unified (Refactored)...")
        
        # ========================
        # INFRASTRUCTURE LAYER (Outer Ring)
        # ========================
        self.face_recognizer: IFaceRecognizer = FaceRecognizer()
        self.audio_analyzer: IAudioAnalyzer = AudioAnalyzer()
        self.schedule_repo: IScheduleRepository = CSVScheduleRepository()
        self.student_repo = JsonStudentRepository()
        self.alert_service: IAlertService = JSONAlertService()
        
        # ========================
        # APPLICATION LAYER (Middle Ring)
        # ========================
        self.detect_truancy = DetectTruancyUseCase(
            student_repo=self.student_repo,
            schedule_repo=self.schedule_repo,
            debounce_threshold=30
        )
        
        self.mark_attendance = MarkAttendanceUseCase(
            attendance_repo=None,  # TODO: Create AttendanceRepository
            schedule_repo=self.schedule_repo
        )
        
        # Threading
        self.running = False
        self.current_zone = "Main Hall"
        
        print("✅ All dependencies wired!")
    
    def start(self):
        """Start orchestration (threads)"""
        self.running = True
        
        # Start infrastructure
        self.audio_analyzer.start_listening()
        
        # Start threads
        video_thread = threading.Thread(target=self.video_loop, daemon=True)
        video_thread.start()
        
        print("🎬 System running! Press 'q' to quit.\n")
        
        # Blocking wait (in real system, this would be GUI)
        video_thread.join()
    
    def stop(self):
        """Stop orchestration"""
        self.running = False
        self.audio_analyzer.stop_listening()
        print("🛑 System stopped")
    
    def video_loop(self):
        """
        Video processing thread.
        
        ORCHESTRATION ONLY - delegates to use cases.
        """
        cap = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Get current time context
            now = datetime.now()
            current_day = now.strftime('%A')
            current_time = now.time()
            
            # Check lecture mode (for UI only)
            is_lecture_mode = self.schedule_repo.is_lecture_mode(
                self.current_zone,
                current_day,
                current_time
            )
            
            # Display context
            mode_text = "LECTURE (Strict)" if is_lecture_mode else "BREAK (Relaxed)"
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # ========================
            # SENSING (Infrastructure Layer)
            # ========================
            faces = self.face_recognizer.detect_faces(frame)
            audio_metrics = self.audio_analyzer.get_current_metrics()
            
            # ========================
            # DECISION (Application Layer - delegated to use cases)
            # ========================
            for face in faces:
                # Search in gallery
                found, student_id = self.face_recognizer.search_face(face.embedding)
                
                if found:
                    # Get student info
                    student = self.student_repo.get_by_id(student_id)
                    
                    if student:
                        # DELEGATE to use case (NO embedded logic)
                        is_compliant, message, session_data = self.detect_truancy.execute(
                            student_id=student_id,
                            current_location=self.current_zone,
                            day=current_day,
                            check_time=current_time
                        )
                        
                        # UI feedback only
                        color = (0, 255, 0) if is_compliant else (0, 0, 255)
                        bbox = face.bbox
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                        cv2.putText(frame, f"{student_id}: {message}", (bbox[0], bbox[1] - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Audio alert check (UI only)
            if self.audio_analyzer.is_alert_active():
                cv2.putText(frame, "🔊 AUDIO ALERT", (50, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            # Display
            cv2.imshow("ScholarMaster (Refactored)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.stop()


if __name__ == "__main__":
    # Dependency injection at entry point
    system = ScholarMasterUnified()
    system.start()
