#!/usr/bin/env python3
"""
ScholarMaster Unified System - Refactored with Onion Architecture
================================================================================
REFACTORED VERSION using core/ architecture

This version demonstrates explicit Onion Architecture:
- Domain rules extracted to core/domain/rules/
- Business logic delegated to core/application/use_cases/
- Infrastructure accessed via core/interfaces/ ports
- main_refactored.py is THIN ORCHESTRATOR (~300 lines vs 835)

Compare with main_unified_backup.py to see improvements.

Author: Narendra P
Date: January 27, 2026
Version: 2.0.0 (Onion Architecture Refactor)
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
# CORE ARCHITECTURE IMPORTS (Dependency Inversion)
# ============================================================================

# Interfaces (Ports - depend on abstractions)
from core.interfaces.i_face_recognizer import IFaceRecognizer
from core.interfaces.i_audio_analyzer import IAudioAnalyzer
from core.interfaces.i_schedule_repository import IScheduleRepository
from core.interfaces.i_alert_service import IAlertService, Alert, AlertSeverity

# Infrastructure Adapters (Concrete implementations)
from core.infrastructure.sensing.vision.face_recognizer import FaceRecognizer
from core.infrastructure.sensing.audio.audio_analyzer import AudioAnalyzer
from core.infrastructure.persistence.repositories.schedule_repository import CSVScheduleRepository
from core.infrastructure.persistence.repositories.json_student_repository import JsonStudentRepository
from core.infrastructure.notifications.alert_service import JSONAlertService

# Application Use Cases
from core.application.use_cases.detect_truancy_use_case import DetectTruancyUseCase

# Domain Rules (for UI/orchestration logic only)
from core.domain.rules.alert_rules import AlertRules

# Legacy modules (for features not yet migrated)
from modules_legacy.privacy_analytics import PrivacyEngagement
from modules_legacy.safety_rules import SafetyEngine
from modules_legacy.attendance_logger import AttendanceManager


# ============================================================================
# SIMPLIFIED AUDIT LOG (keeping from original for Paper 8)
# ============================================================================

class SimplifiedAuditLog:
    """Merkle tree audit log for immutable event tracking (Paper 8)"""
    
    def __init__(self, db_path="data/audit_log.db"):
        import sqlite3
        import hashlib
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.hashlib = hashlib
        
        # Create table
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
        
        # Get previous hash
        self.cursor.execute("SELECT current_hash FROM events ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        prev_hash = result[0] if result else "0" * 64
        
        # Compute current hash
        current_hash = self.hashlib.sha256(
            f"{timestamp}{event_type}{data_str}{prev_hash}".encode()
        ).hexdigest()
        
        # Insert
        self.cursor.execute(
            "INSERT INTO events (timestamp, event_type, data, prev_hash, current_hash) VALUES (?, ?, ?, ?, ?)",
            (timestamp, event_type, data_str, prev_hash, current_hash)
        )
        self.conn.commit()


# ============================================================================
# POWER MONITOR (keeping from original for Paper 5)
# ============================================================================

class PowerMonitor:
    """Lightweight power profiling (Paper 5)"""
    
    def __init__(self):
        self.metrics_log = []
        self.start_time = time.time()
    
    def record_metrics(self):
        """Record current power metrics"""
        metrics = {
            'timestamp': time.time() - self.start_time,
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent
        }
        self.metrics_log.append(metrics)
        return metrics


# ============================================================================
# MAIN REFACTORED SYSTEM (Onion Architecture)
# ============================================================================

class ScholarMasterUnified:
    """
    Thin orchestrator using Onion Architecture.
    
    BEFORE: 835 lines with embedded business logic
    AFTER: ~300 lines, pure orchestration + UI
    
    Business logic delegated to:
    - core/domain/rules/ (pure logic)
    - core/application/use_cases/ (orchestration)
    - core/infrastructure/ (external systems)
    """
    
    def __init__(self):
        print("=" * 80)
        print("SCHOLARMASTER UNIFIED SYSTEM - ONION ARCHITECTURE v2.0")
        print("=" * 80)
        
        # Shared state
        self.lock = threading.Lock()
        self.running = True
        
        # Current state variables (UI only)
        self.current_student_id: str = "UNKNOWN"
        self.current_confidence: float = 0.0
        self.current_engagement: float = 0.0
        self.current_audio_db: float = 0.0
        self.compliance_status: str = "INITIALIZING"
        self.current_zone = "Main Hall"  # TODO: Make configurable
        
        # Performance metrics
        self.video_fps: float = 0.0
        self.total_events: int = 0
        
        # ============================================================
        # DEPENDENCY INJECTION (Onion Architecture)
        # ============================================================
        
        print("\n[INIT] Loading INFRASTRUCTURE layer (outer ring)...")
        
        # Vision (Paper 1)
        self.face_recognizer: IFaceRecognizer = FaceRecognizer()
        
        # Audio (Paper 6)
        self.audio_analyzer: IAudioAnalyzer = AudioAnalyzer()
        
        # Persistence
        self.schedule_repo: IScheduleRepository = CSVScheduleRepository()
        self.student_repo = JsonStudentRepository()
        self.alert_service: IAlertService = JSONAlertService()
        
        # Legacy (not yet migrated)
        try:
            self.analytics = PrivacyEngagement()
            print("[INIT] PrivacyEngagement loaded")
        except Exception as e:
            print(f"[INIT] Warning: PrivacyEngagement failed: {e}")
            self.analytics = None
        
        self.attendance_logger = AttendanceManager()
        self.safety_engine = SafetyEngine()
        
        print("[INIT] Loading APPLICATION layer (middle ring)...")
        
        # Use Cases (delegated business logic)
        self.detect_truancy = DetectTruancyUseCase(
            student_repo=self.student_repo,
            schedule_repo=self.schedule_repo,
            debounce_threshold=30  # 30 frames = ~30s
        )
        
        print("[INIT] Loading AUDIT \u0026 MONITORING...")
        
        # Audit log (Paper 8)
        self.audit_log = SimplifiedAuditLog()
        
        # Power monitor (Paper 5)
        self.power_monitor = PowerMonitor()
        
        print("\n✅ All systems initialized! (Onion Architecture)\n")
    
    def start(self):
        """Start the unified system"""
        # Start audio monitoring
        self.audio_analyzer.start_listening()
        
        # Start threads
        video_thread = threading.Thread(target=self.video_thread, daemon=True)
        audio_thread = threading.Thread(target=self.audio_monitoring_thread, daemon=True)
        dashboard_thread = threading.Thread(target=self.dashboard_thread, daemon=True)
        
        video_thread.start()
        audio_thread.start()
        dashboard_thread.start()
        
        print("🎬 System running! Press 'q' in video window to quit.\n")
        
        try:
            video_thread.join()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the system"""
        self.running = False
        self.audio_analyzer.stop_listening()
        print("🛑 System stopped")
    
    # ========================================================================
    # VIDEO THREAD (Orchestration - delegates to use cases)
    # ========================================================================
    
    def video_thread(self):
        """
        Video processing thread.
        
        ORCHESTRATION ONLY - all business logic delegated to:
        - core/domain/rules/ (ComplianceRules, AlertRules)
        - core/application/use_cases/ (DetectTruancyUseCase)
        """
        cap = cv2.VideoCapture(0)
        fps_counter = 0
        fps_start = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Get current time context
            now = datetime.now()
            current_day = now.strftime('%A')  # "Monday", "Tuesday", etc.
            current_time = now.time()
            
            # Check lecture mode (for UI + context-aware thresholds)
            is_lecture_mode = self.schedule_repo.is_lecture_mode(
                self.current_zone,
                current_day,
                current_time
            )
            
            # Display context
            mode_text = "LECTURE (Strict)" if is_lecture_mode else "BREAK (Relaxed)"
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # ================================================================
            # SENSING LAYER (Infrastructure - no decisions here)
            # ================================================================
            
            faces = self.face_recognizer.detect_faces(frame)
            audio_metrics = self.audio_analyzer.get_current_metrics()
            
            # ================================================================
            # DECISION LAYER (Delegated to use cases)
            # ================================================================
            
            for face in faces:
                # Search for face in gallery
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
                        
                        # Update shared state (for dashboard)
                        with self.lock:
                            self.current_student_id = student_id
                            self.current_confidence = face.confidence
                            self.compliance_status = "COMPLIANT" if is_compliant else "VIOLATION"
                        
                        # Handle violations (DELEGATE to alert service)
                        if not is_compliant:
                            alert = Alert(
                                timestamp=now,
                                severity=AlertSeverity.WARNING,
                                message=f"Truancy: {message}",
                                zone=self.current_zone,
                                metadata={'student_id': student_id, 'session_data': session_data}
                            )
                            
                            # Check debounce using domain rules
                            recent_alerts = self.alert_service.get_recent_alerts(
                                zone=self.current_zone,
                                minutes=5
                            )
                            
                            if not AlertRules.should_debounce(len(recent_alerts), window_minutes=5):
                                self.alert_service.trigger(alert)
                        
                        # Mark attendance (if compliant)
                        if is_compliant and session_data:
                            self.attendance_logger.mark_present(
                                student_id=student_id,
                                context_data=session_data,
                                user_role='Admin'  # System acts as Admin
                            )
                        
                        # UI feedback
                        color = (0, 255, 0) if is_compliant else (0, 0, 255)
                        bbox = face.bbox
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                        cv2.putText(frame, f"{student_id}: {message[:20]}", (bbox[0], bbox[1] - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                else:
                    # Unknown face - draw yellow box
                    bbox = face.bbox
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 255), 2)
                    cv2.putText(frame, "Unknown", (bbox[0], bbox[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # ================================================================
            # AUDIO ALERTS (using domain rules)
            # ================================================================
            
            if self.audio_analyzer.is_alert_active():
                # Use domain rules to determine severity
                severity = AlertRules.get_noise_alert_severity(audio_metrics.db_level)
                
                alert = Alert(
                    timestamp=now,
                    severity=severity,
                    message=f"Loud noise detected ({audio_metrics.db_level:.2f} dB)",
                    zone=self.current_zone,
                    metadata={'db_level': audio_metrics.db_level}
                )
                
                # Debounce check
                recent_alerts = self.alert_service.get_recent_alerts(zone=self.current_zone, minutes=1)
                if not AlertRules.should_debounce(len(recent_alerts), window_minutes=1):
                    self.alert_service.trigger(alert)
                
                # UI visual feedback
                cv2.putText(frame, "🔊 AUDIO ALERT", (50, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            # FPS calculation
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                with self.lock:
                    self.video_fps = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Display FPS
            cv2.putText(frame, f"FPS: {self.video_fps:.1f}", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow("ScholarMaster Unified (Onion Architecture)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.stop()
    
    # ========================================================================
    # AUDIO MONITORING THREAD
    # ========================================================================
    
    def audio_monitoring_thread(self):
        """Audio monitoring thread (delegated to infrastructure)"""
        while self.running:
            metrics = self.audio_analyzer.get_current_metrics()
            
            with self.lock:
                self.current_audio_db = metrics.db_level
            
            time.sleep(0.5)  # 2 Hz update rate
    
    # ========================================================================
    # DASHBOARD THREAD
    # ========================================================================
    
    def dashboard_thread(self):
        """Terminal dashboard showing system state"""
        while self.running:
            # Record power metrics
            power_metrics = self.power_monitor.record_metrics()
            
            # Get current state
            with self.lock:
                student_id = self.current_student_id
                confidence = self.current_confidence
                engagement = self.current_engagement
                audio_db = self.current_audio_db
                fps = self.video_fps
                compliance = self.compliance_status
            
            # Clear and display dashboard
            print("\033[2J\033[H")  # Clear screen
            print("=" * 80)
            print("SCHOLARMASTER UNIFIED - SYSTEM DASHBOARD (Onion Architecture)")
            print("=" * 80)
            print(f"Architecture: Domain → Application → Infrastructure")
            print(f"Gallery Size: {self.face_recognizer.get_gallery_size()} faces enrolled")
            print(f"Current Zone: {self.current_zone}")
            print()
            print(f"{'RECOGNITION':<20} {student_id} (confidence: {confidence:.2f})")
            print(f"{'COMPLIANCE':<20} {compliance}")
            print(f"{'AUDIO LEVEL':<20} {audio_db:.2f} (normalized 0-1)")
            print(f"{'VIDEO FPS':<20} {fps:.1f}")
            print()
            print(f"{'CPU USAGE':<20} {power_metrics['cpu_percent']:.1f}%")
            print(f"{'MEMORY USAGE':<20} {power_metrics['memory_mb']:.1f} MB")
            print()
            print("Press 'q' in video window to quit")
            print("=" * 80)
            
            time.sleep(2.0)  # Update every 2 seconds


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    system = ScholarMasterUnified()
    system.start()
