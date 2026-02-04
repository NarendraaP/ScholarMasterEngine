#!/usr/bin/env python3
"""
ScholarMaster Unified - Event-Driven Architecture (Phase 2)
================================================================================
Phase 2: Event-driven orchestration with decoupled components

Changes from Phase 1:
- Sensors publish events (NO direct decision making)
- Use cases subscribe to events
- Side effects triggered by events (alerts, logging)

Aligns with Papers 9 & 10 (Orchestration, System Effects)

Author: Narendra P
Date: January 27, 2026
Version: 2.1.0 (Event-Driven Refactor)
================================================================================
"""

import cv2
import numpy as np
import threading
import time
import psutil
from datetime import datetime
from typing import Optional
from pathlib import Path

# ============================================================================
# EVENT-DRIVEN ARCHITECTURE IMPORTS
# ============================================================================

# Event infrastructure
from core.infrastructure.events.event_bus import EventBus, Event, EventType

# Event handlers (subscribers)
from core.application.services.event_handlers import EventHandlers

# Interfaces (Ports)
from core.interfaces.i_face_recognizer import IFaceRecognizer
from core.interfaces.i_audio_analyzer import IAudioAnalyzer
from core.interfaces.i_schedule_repository import IScheduleRepository
from core.interfaces.i_alert_service import IAlertService

# Infrastructure Adapters
from core.infrastructure.sensing.vision.face_recognizer import FaceRecognizer
from core.infrastructure.sensing.audio.audio_analyzer import AudioAnalyzer
from core.infrastructure.persistence.repositories.schedule_repository import CSVScheduleRepository
from core.infrastructure.persistence.repositories.json_student_repository import JsonStudentRepository
from core.infrastructure.notifications.alert_service import JSONAlertService

# Application Use Cases
from core.application.use_cases.detect_truancy_use_case import DetectTruancyUseCase

# Domain Rules
from core.domain.rules.alert_rules import AlertRules

# Legacy modules
from modules_legacy.privacy_analytics import PrivacyEngagement
from modules_legacy.safety_rules import SafetyEngine
from modules_legacy.attendance_logger import AttendanceManager


# ============================================================================
# AUDIT & MONITORING (from Phase 1)
# ============================================================================

class SimplifiedAuditLog:
    """Merkle tree audit log (Paper 8)"""
    
    def __init__(self, db_path="data/audit_log.db"):
        import sqlite3
        import hashlib
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.hashlib = hashlib
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                data TEXT,
                prev_hash TEXT,
                current_hash TEXT
            )
        """)
        self.conn.commit()
    
    def log_event(self, event_type: str, data: dict):
        """Log event with Merkle chaining"""
        timestamp = datetime.now().isoformat()
        data_str = str(data)
        
        self.cursor.execute("SELECT current_hash FROM events ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        prev_hash = result[0] if result else "0" * 64
        
        current_hash = self.hashlib.sha256(
            f"{timestamp}{event_type}{data_str}{prev_hash}".encode()
        ).hexdigest()
        
        self.cursor.execute(
            "INSERT INTO events (timestamp, event_type, data, prev_hash, current_hash) VALUES (?, ?, ?, ?, ?)",
            (timestamp, event_type, data_str, prev_hash, current_hash)
        )
        self.conn.commit()


class PowerMonitor:
    """Power monitoring (Paper 5)"""
    
    def __init__(self):
        self.metrics_log = []
        self.start_time = time.time()
    
    def record_metrics(self):
        metrics = {
            'timestamp': time.time() - self.start_time,
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent
        }
        self.metrics_log.append(metrics)
        return metrics


# ============================================================================
# EVENT-DRIVEN ORCHESTRATOR
# ============================================================================

class ScholarMasterUnified:
    """
    Event-driven orchestrator (Phase 2).
    
    Sensors publish events → Handlers process → Side effects triggered
    """
    
    def __init__(self):
        print("=" * 80)
        print("SCHOLARMASTER UNIFIED - EVENT-DRIVEN ARCHITECTURE v2.1")
        print("=" * 80)
        
        # Shared state
        self.lock = threading.Lock()
        self.running = True
        self.current_zone = "Main Hall"
        
        # UI state
        self.current_student_id = "UNKNOWN"
        self.current_confidence = 0.0
        self.current_audio_db = 0.0
        self.compliance_status = "INITIALIZING"
        self.video_fps = 0.0
        
        # ============================================================
        # EVENT BUS (NEW IN PHASE 2)
        # ============================================================
        print("\n[INIT] Creating event bus...")
        self.event_bus = EventBus()
        
        # ============================================================
        # INFRASTRUCTURE LAYER
        # ============================================================
        print("[INIT] Loading infrastructure (sensors, repositories)...")
        
        self.face_recognizer: IFaceRecognizer = FaceRecognizer()
        self.audio_analyzer: IAudioAnalyzer = AudioAnalyzer()
        self.schedule_repo: IScheduleRepository = CSVScheduleRepository()
        self.student_repo = JsonStudentRepository()
        self.alert_service: IAlertService = JSONAlertService()
        
        # Legacy
        try:
            self.analytics = PrivacyEngagement()
            print("[INIT] PrivacyEngagement loaded")
        except Exception as e:
            print(f"[INIT] Warning: PrivacyEngagement failed: {e}")
            self.analytics = None
        
        self.attendance_logger = AttendanceManager()
        self.safety_engine = SafetyEngine()
        
        # ============================================================
        # APPLICATION LAYER
        # ============================================================
        print("[INIT] Loading application layer (use cases, handlers)...")
        
        self.detect_truancy = DetectTruancyUseCase(
            student_repo=self.student_repo,
            schedule_repo=self.schedule_repo,
            debounce_threshold=30
        )
        
        # EVENT HANDLERS (NEW IN PHASE 2)
        self.event_handlers = EventHandlers(
            alert_service=self.alert_service,
            event_bus=self.event_bus
        )
        
        # ============================================================
        # AUDIT & MONITORING
        # ============================================================
        print("[INIT] Loading audit & monitoring...")
        self.audit_log = SimplifiedAuditLog()
        self.power_monitor = PowerMonitor()
        
        # Subscribe to alerts for audit logging
        self.event_bus.subscribe(EventType.ALERT_TRIGGERED, self._log_alert)
        
        print("\n✅ Event-driven system initialized!\n")
    
    def _log_alert(self, event: Event):
        """Log alerts to audit trail"""
        self.audit_log.log_event("alert", event.payload)
    
    def start(self):
        """Start the system"""
        self.audio_analyzer.start_listening()
        
        video_thread = threading.Thread(target=self.video_thread, daemon=True)
        audio_thread = threading.Thread(target=self.audio_monitoring_thread, daemon=True)
        dashboard_thread = threading.Thread(target=self.dashboard_thread, daemon=True)
        
        video_thread.start()
        audio_thread.start()
        dashboard_thread.start()
        
        print("🎬 System running! Press 'q' to quit.\n")
        
        try:
            video_thread.join()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the system"""
        self.running = False
        self.audio_analyzer.stop_listening()
        self.event_bus.clear_all()
        print("🛑 System stopped")
    
    # ========================================================================
    # VIDEO THREAD (Event-driven - publishes events)
    # ========================================================================
    
    def video_thread(self):
        """
        Video processing thread (EVENT-DRIVEN).
        
        SENSORS PUBLISH EVENTS - NO direct decision making!
        """
        cap = cv2.VideoCapture(0)
        fps_counter = 0
        fps_start = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            now = datetime.now()
            current_day = now.strftime('%A')
            current_time = now.time()
            
            is_lecture_mode = self.schedule_repo.is_lecture_mode(
                self.current_zone, current_day, current_time
            )
            
            mode_text = "LECTURE (Strict)" if is_lecture_mode else "BREAK (Relaxed)"
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # ================================================================
            # SENSING - PUBLISH EVENTS (NO decisions here!)
            # ================================================================
            
            faces = self.face_recognizer.detect_faces(frame)
            
            for face in faces:
                found, student_id = self.face_recognizer.search_face(face.embedding)
                
                if found:
                    # PUBLISH EVENT instead of making decision
                    self.event_bus.publish(Event(
                        type=EventType.FACE_DETECTED,
                        payload={
                            'student_id': student_id,
                            'zone': self.current_zone,
                            'confidence': face.confidence,
                            'day': current_day,
                            'time': current_time.isoformat()
                        }
                    ))
                    
                    # For UI: Check compliance (non-blocking)
                    student = self.student_repo.get_by_id(student_id)
                    if student:
                        is_compliant, message, session_data = self.detect_truancy.execute(
                            student_id=student_id,
                            current_location=self.current_zone,
                            day=current_day,
                            check_time=current_time
                        )
                        
                        # Update UI state
                        with self.lock:
                            self.current_student_id = student_id
                            self.current_confidence = face.confidence
                            self.compliance_status = "COMPLIANT" if is_compliant else "VIOLATION"
                        
                        # PUBLISH EVENT if violation
                        if not is_compliant:
                            self.event_bus.publish(Event(
                                type=EventType.VIOLATION_DETECTED,
                                payload={
                                    'student_id': student_id,
                                    'zone': self.current_zone,
                                    'message': message,
                                    'session_data': session_data
                                }
                            ))
                        
                        # Mark attendance if compliant
                        if is_compliant and session_data:
                            self.attendance_logger.mark_present(
                                student_id=student_id,
                                context_data=session_data,
                                user_role='Admin'
                            )
                        
                        # UI feedback
                        color = (0, 255, 0) if is_compliant else (0, 0, 255)
                        bbox = face.bbox
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                        cv2.putText(frame, f"{student_id}: {message[:20]}", 
                                   (bbox[0], bbox[1] - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                else:
                    bbox = face.bbox
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 255), 2)
                    cv2.putText(frame, "Unknown", (bbox[0], bbox[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # FPS
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                with self.lock:
                    self.video_fps = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            cv2.putText(frame, f"FPS: {self.video_fps:.1f}", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("ScholarMaster (Event-Driven)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.stop()
    
    # ========================================================================
    # AUDIO MONITORING THREAD (Event-driven)
    # ========================================================================
    
    def audio_monitoring_thread(self):
        """Audio monitoring thread - PUBLISHES EVENTS"""
        while self.running:
            metrics = self.audio_analyzer.get_current_metrics()
            
            with self.lock:
                self.current_audio_db = metrics.db_level
            
            # PUBLISH EVENT if alert active
            if self.audio_analyzer.is_alert_active():
                self.event_bus.publish(Event(
                    type=EventType.AUDIO_ALERT,
                    payload={
                        'zone': self.current_zone,
                        'db_level': metrics.db_level,
                        'is_voice': metrics.is_voice_detected
                    }
                ))
            
            time.sleep(0.5)
    
    # ========================================================================
    # DASHBOARD THREAD
    # ========================================================================
    
    def dashboard_thread(self):
        """Terminal dashboard"""
        while self.running:
            power_metrics = self.power_monitor.record_metrics()
            
            with self.lock:
                student_id = self.current_student_id
                confidence = self.current_confidence
                audio_db = self.current_audio_db
                fps = self.video_fps
                compliance = self.compliance_status
            
            print("\033[2J\033[H")
            print("=" * 80)
            print("SCHOLARMASTER UNIFIED - EVENT-DRIVEN DASHBOARD")
            print("=" * 80)
            print(f"Architecture: Event-Driven (Sensors → Events → Handlers)")
            print(f"Gallery Size: {self.face_recognizer.get_gallery_size()} faces")
            print(f"Current Zone: {self.current_zone}")
            print()
            print(f"{'RECOGNITION':<20} {student_id} (conf: {confidence:.2f})")
            print(f"{'COMPLIANCE':<20} {compliance}")
            print(f"{'AUDIO LEVEL':<20} {audio_db:.2f}")
            print(f"{'VIDEO FPS':<20} {fps:.1f}")
            print()
            print(f"{'CPU':<20} {power_metrics['cpu_percent']:.1f}%")
            print(f"{'MEMORY':<20} {power_metrics['memory_mb']:.1f} MB")
            print()
            print("Press 'q' in video window to quit")
            print("=" * 80)
            
            time.sleep(2.0)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    system = ScholarMasterUnified()
    system.start()
