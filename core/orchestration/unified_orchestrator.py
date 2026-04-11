#!/usr/bin/env python3
"""
Unified Orchestrator - Cross-Paper Event Flow Integration
==========================================================
Central hub that routes events between all ScholarMaster papers:

  Sensing (P1-6) → EventBus → Governance (P7-11) + FL (P12-14) + AR (P15)

This module implements the "single continuous project" requirement by
wiring all papers through a unified event-driven architecture.

Papers Integrated:
- P1-6: Sensing/Inference (MasterEngine)
- P7-11: Governance (Blockchain, Audit, Privacy)
- P12-14: Federated Learning (DP-FedAvg, Drift)
- P15: AR Visualization (MQTT)
- P16: Sociological Validation (Observer, no mutations)

INVARIANTS:
- No raw biometrics cross boundaries (only skeletons/embeddings)
- FL receives gradients, never raw frames
- AR sees symbolic data only (zone IDs, severity, timestamps)
- Paper 16 is read-only observer
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue, Empty
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CROSS-PAPER EVENT TYPES
# =============================================================================

class CrossPaperEventType(Enum):
    """Events that flow across paper boundaries."""
    
    # Sensing Layer (P1-6) Events
    FRAME_CAPTURED = auto()          # Camera → MasterEngine
    FACE_DETECTED = auto()           # P1 → P7, P8
    POSE_DETECTED = auto()           # P3 → P8, P13, P16
    AUDIO_ANOMALY = auto()           # P5 → P8, P10, P15
    ENGAGEMENT_MEASURED = auto()     # P6 → P10
    
    # Governance Layer (P7-11) Events
    COMPLIANCE_CHECKED = auto()      # P7 → P10
    AUDIT_LOGGED = auto()            # P8 → P15 (surfaces in AR)
    PRIVACY_LED_STATE = auto()       # P11 → P16
    ALERT_TRIGGERED = auto()         # P10 → P15
    CRYPTO_SHRED_EXECUTED = auto()   # P8 → P16 (trust signal)
    
    # FL Layer (P12-14) Events
    GRADIENT_READY = auto()          # Local trainer → Aggregator
    MODEL_UPDATED = auto()           # Aggregator → Local nodes
    DRIFT_DETECTED = auto()          # P13 → P8, P15
    PRIVACY_BUDGET_WARNING = auto()  # P13 → P8
    
    # Presentation Layer (P15) Events
    AR_ALERT_RENDERED = auto()       # AR → Operator
    OPERATOR_ACKNOWLEDGED = auto()   # Operator → P8, P16
    
    # System Events
    SYSTEM_HEALTH = auto()
    SHUTDOWN_REQUESTED = auto()


@dataclass
class CrossPaperEvent:
    """
    Event structure for cross-paper communication.
    
    Privacy Invariant: payload must NEVER contain raw biometrics.
    Only symbolic data (zone IDs, severity, timestamps, skeleton keypoints).
    """
    event_type: CrossPaperEventType
    source_paper: str               # e.g., "P3" or "P13"
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: f"evt_{int(time.time() * 1000)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for MQTT/logging."""
        return {
            "event_id": self.event_id,
            "type": self.event_type.name,
            "source": self.source_paper,
            "payload": self.payload,
            "timestamp": self.timestamp
        }


# =============================================================================
# UNIFIED ORCHESTRATOR
# =============================================================================

class UnifiedOrchestrator:
    """
    Central event router for ScholarMaster.
    
    Responsibilities:
    1. Subscribe to sensing events from MasterEngine
    2. Route to appropriate paper handlers
    3. Enforce privacy boundaries
    4. Emit downstream events (Governance, FL, AR)
    5. Maintain audit trail
    
    Thread Safety: All operations are thread-safe.
    """
    
    def __init__(
        self,
        enable_audit: bool = True,
        enable_fl: bool = True,
        enable_ar: bool = True,
        enable_metrics: bool = True
    ):
        """
        Initialize the unified orchestrator.
        
        Args:
            enable_audit: Enable blockchain audit logging (P8)
            enable_fl: Enable federated learning integration (P12-14)
            enable_ar: Enable AR event publishing (P15)
            enable_metrics: Enable Paper 16 metrics collection
        """
        self._handlers: Dict[CrossPaperEventType, List[Callable]] = {}
        self._lock = threading.RLock()
        self._event_queue: Queue = Queue(maxsize=10000)
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Feature flags
        self.enable_audit = enable_audit
        self.enable_fl = enable_fl
        self.enable_ar = enable_ar
        self.enable_metrics = enable_metrics
        
        # Metrics (for Paper 16)
        self._metrics = {
            "events_processed": 0,
            "events_by_type": {},
            "avg_latency_ms": 0.0,
            "total_latency_ms": 0.0
        }
        
        # Lazy-loaded components (avoid circular imports)
        self._audit_log = None
        self._fl_trainer = None
        self._mqtt_publisher = None
        
        logger.info("✅ UnifiedOrchestrator initialized")
    
    # -------------------------------------------------------------------------
    # Event Subscription
    # -------------------------------------------------------------------------
    
    def subscribe(
        self, 
        event_type: CrossPaperEventType, 
        handler: Callable[[CrossPaperEvent], None]
    ) -> None:
        """Subscribe a handler to an event type."""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            logger.debug(f"📡 Subscribed handler to {event_type.name}")
    
    def unsubscribe(
        self, 
        event_type: CrossPaperEventType, 
        handler: Callable
    ) -> None:
        """Remove a handler subscription."""
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type].remove(handler)
    
    # -------------------------------------------------------------------------
    # Event Publishing
    # -------------------------------------------------------------------------
    
    def publish(self, event: CrossPaperEvent) -> None:
        """
        Publish an event to all subscribers.
        
        This is non-blocking; events are queued for async processing.
        """
        if not self._running:
            logger.warning("⚠️  Orchestrator not running, event dropped")
            return
        
        try:
            self._event_queue.put_nowait(event)
        except Exception as e:
            logger.error(f"❌ Event queue full, event dropped: {e}")
    
    def publish_sync(self, event: CrossPaperEvent) -> None:
        """Publish and process event synchronously (for testing)."""
        self._process_event(event)
    
    def _process_event(self, event: CrossPaperEvent) -> None:
        """Process a single event through all handlers."""
        start_time = time.time()
        
        # Validate privacy invariants
        self._validate_privacy(event)
        
        # Get handlers
        with self._lock:
            handlers = self._handlers.get(event.event_type, []).copy()
        
        # Execute handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"❌ Handler error for {event.event_type.name}: {e}")
        
        # Route to downstream systems
        self._route_to_downstream(event)
        
        # Update metrics
        latency_ms = (time.time() - start_time) * 1000
        self._update_metrics(event, latency_ms)
    
    # -------------------------------------------------------------------------
    # Privacy Enforcement
    # -------------------------------------------------------------------------
    
    def _validate_privacy(self, event: CrossPaperEvent) -> None:
        """
        Validate that event payload uses ALLOWLIST-ONLY fields.
        
        Per ARCHITECTURE_CANONICAL.md 4.3-4.4:
        - Denylist-based filtering is PROHIBITED
        - All cross-boundary data must be allowlist-validated
        - Unknown fields must be REJECTED, not ignored
        
        ALLOWED fields only:
        - zone_id, timestamp, event_type, severity
        - skeleton_keypoints, audio_class, event_id
        - source_paper, is_valid, reason
        """
        # ALLOWLIST (denylist is prohibited per ARCHITECTURE_CANONICAL.md 4.3)
        allowed_keys = {
            # Core fields per ARCHITECTURE_CANONICAL.md 4.4
            "zone_id", "timestamp", "event_type", "severity",
            "skeleton_keypoints", "audio_class", "event_id",
            "source_paper", "is_valid", "reason",
            # Extended allowlist for operational needs
            "zone", "alert_type", "message", "student_count",
            "engagement_score", "check_type", "metric_type",
            # Pose detection (Paper 1-3)
            "keypoints", "hand_raised", "attention_score", "pose_type",
            # Audio monitoring (Paper 6)
            "db_level", "acoustic_event",
            # Audit logging (Paper 8)
            "log_hash", "chain_length", "block_id",
            # Drift detection (Paper 13-14)
            "drift_type", "drift_score", "recommended_action",
            # Power/system health (Paper 4, 12)
            "cpu_percent", "memory_mb", "memory_percent", "uptime_seconds",
            "write_count", "bytes_written_mb", "writes_per_minute",
            # Privacy LED (Paper 11)
            "state", "previous_state", "is_transparent",
        }
        
        payload_keys = set(event.payload.keys())
        unknown_keys = payload_keys - allowed_keys
        
        if unknown_keys:
            logger.error(
                f"🚨 PRIVACY VIOLATION in {event.event_type.name}: "
                f"Unknown fields rejected (allowlist-only): {unknown_keys}"
            )
            raise ValueError(
                f"Privacy violation: Unknown fields {unknown_keys} not in allowlist"
            )

    
    # -------------------------------------------------------------------------
    # Downstream Routing
    # -------------------------------------------------------------------------
    
    def _route_to_downstream(self, event: CrossPaperEvent) -> None:
        """Route event to appropriate downstream systems."""
        
        # Paper 8: Audit logging
        if self.enable_audit and event.event_type in {
            CrossPaperEventType.FACE_DETECTED,
            CrossPaperEventType.POSE_DETECTED,
            CrossPaperEventType.ALERT_TRIGGERED,
            CrossPaperEventType.OPERATOR_ACKNOWLEDGED,
            CrossPaperEventType.CRYPTO_SHRED_EXECUTED
        }:
            self._log_to_audit(event)
        
        # Paper 13-14: FL triggers
        if self.enable_fl and event.event_type in {
            CrossPaperEventType.POSE_DETECTED,
            CrossPaperEventType.DRIFT_DETECTED
        }:
            self._notify_fl(event)
        
        # Paper 15: AR alerts
        if self.enable_ar and event.event_type in {
            CrossPaperEventType.ALERT_TRIGGERED,
            CrossPaperEventType.AUDIO_ANOMALY,
            CrossPaperEventType.DRIFT_DETECTED,
            CrossPaperEventType.AUDIT_LOGGED
        }:
            self._publish_to_ar(event)
    
    def _log_to_audit(self, event: CrossPaperEvent) -> None:
        """Log event to blockchain audit trail (Paper 8)."""
        if self._audit_log is None:
            try:
                # Late import to avoid circular dependency
                from modules_legacy.trust_layer import TrustLogger
                self._audit_log = TrustLogger()
            except ImportError:
                logger.warning("⚠️  TrustLogger not available")
                return
        
        try:
            self._audit_log.log_event(
                event_type=event.event_type.name,
                data={
                    "event_id": event.event_id,
                    "source": event.source_paper,
                    "timestamp": event.timestamp,
                    **{k: v for k, v in event.payload.items() 
                       if k not in {"raw_frame", "embedding"}}
                }
            )
            
            # Emit audit logged event (for AR dashboard)
            audit_event = CrossPaperEvent(
                event_type=CrossPaperEventType.AUDIT_LOGGED,
                source_paper="P8",
                payload={
                    "original_event": event.event_id,
                    "original_type": event.event_type.name
                }
            )
            # Don't recurse - just update metrics
            self._update_metrics(audit_event, 0)
            
        except Exception as e:
            logger.error(f"❌ Audit logging failed: {e}")
    
    def _notify_fl(self, event: CrossPaperEvent) -> None:
        """Notify FL system of relevant events (Papers 12-14)."""
        # FL integration is triggered by specific events
        # but actual gradient computation happens in FL module
        logger.debug(f"📊 FL notified: {event.event_type.name}")
    
    def _publish_to_ar(self, event: CrossPaperEvent) -> None:
        """Publish event to AR visualization layer (Paper 15)."""
        if self._mqtt_publisher is None:
            try:
                from core.infrastructure.mqtt.mqtt_publisher import MQTTPublisher
                self._mqtt_publisher = MQTTPublisher()
            except ImportError:
                logger.warning("⚠️  MQTTPublisher not available")
                return
        
        try:
            self._mqtt_publisher.publish_alert(event)
        except Exception as e:
            logger.error(f"❌ MQTT publish failed: {e}")
    
    # -------------------------------------------------------------------------
    # Metrics (Paper 16)
    # -------------------------------------------------------------------------
    
    def _update_metrics(self, event: CrossPaperEvent, latency_ms: float) -> None:
        """Update processing metrics for Paper 16 analysis."""
        if not self.enable_metrics:
            return
        
        with self._lock:
            self._metrics["events_processed"] += 1
            
            type_name = event.event_type.name
            if type_name not in self._metrics["events_by_type"]:
                self._metrics["events_by_type"][type_name] = 0
            self._metrics["events_by_type"][type_name] += 1
            
            # Running average
            self._metrics["total_latency_ms"] += latency_ms
            self._metrics["avg_latency_ms"] = (
                self._metrics["total_latency_ms"] / 
                self._metrics["events_processed"]
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current orchestrator metrics."""
        with self._lock:
            return self._metrics.copy()
    
    # -------------------------------------------------------------------------
    # Lifecycle Management
    # -------------------------------------------------------------------------
    
    def start(self) -> None:
        """Start the orchestrator's event processing loop."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._event_loop,
            daemon=True,
            name="OrchestratorWorker"
        )
        self._worker_thread.start()
        logger.info("🚀 UnifiedOrchestrator started")
    
    def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        logger.info("🛑 UnifiedOrchestrator stopped")
    
    def _event_loop(self) -> None:
        """Main event processing loop."""
        while self._running:
            try:
                event = self._event_queue.get(timeout=0.1)
                self._process_event(event)
            except Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Event loop error: {e}")
    
    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def emit_sensing_event(
        self,
        event_type: CrossPaperEventType,
        zone_id: str,
        severity: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> None:
        """Convenience method for sensing layer to emit events."""
        event = CrossPaperEvent(
            event_type=event_type,
            source_paper="P1-6",
            payload={
                "zone_id": zone_id,
                "severity": severity,
                **(metadata or {})
            }
        )
        self.publish(event)
    
    def emit_governance_event(
        self,
        event_type: CrossPaperEventType,
        details: Dict[str, Any]
    ) -> None:
        """Convenience method for governance layer to emit events."""
        event = CrossPaperEvent(
            event_type=event_type,
            source_paper="P7-11",
            payload=details
        )
        self.publish(event)
    
    def emit_fl_event(
        self,
        event_type: CrossPaperEventType,
        details: Dict[str, Any]
    ) -> None:
        """Convenience method for FL layer to emit events."""
        event = CrossPaperEvent(
            event_type=event_type,
            source_paper="P12-14",
            payload=details
        )
        self.publish(event)


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_orchestrator_instance: Optional[UnifiedOrchestrator] = None
_orchestrator_lock = threading.Lock()


def get_orchestrator() -> UnifiedOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        with _orchestrator_lock:
            if _orchestrator_instance is None:
                _orchestrator_instance = UnifiedOrchestrator()
                _orchestrator_instance.start()
    
    return _orchestrator_instance


def shutdown_orchestrator() -> None:
    """Shutdown the singleton orchestrator."""
    global _orchestrator_instance
    
    if _orchestrator_instance is not None:
        _orchestrator_instance.stop()
        _orchestrator_instance = None


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("UnifiedOrchestrator Test")
    print("=" * 60)
    
    # Create orchestrator
    orch = UnifiedOrchestrator(enable_ar=False)  # AR disabled for test
    
    # Add test handler
    events_received = []
    
    def test_handler(event: CrossPaperEvent):
        events_received.append(event)
        print(f"📥 Received: {event.event_type.name} from {event.source_paper}")
    
    orch.subscribe(CrossPaperEventType.POSE_DETECTED, test_handler)
    orch.subscribe(CrossPaperEventType.ALERT_TRIGGERED, test_handler)
    
    # Start orchestrator
    orch.start()
    
    # Emit test events
    orch.emit_sensing_event(
        CrossPaperEventType.POSE_DETECTED,
        zone_id="NW_HALL_04",
        severity=0.3,
        metadata={"keypoints_count": 17}
    )
    
    orch.emit_governance_event(
        CrossPaperEventType.ALERT_TRIGGERED,
        {"alert_type": "NOISE", "zone": "CLASSROOM_A", "db_level": 85}
    )
    
    # Wait for processing
    time.sleep(0.5)
    
    # Check results
    print(f"\n✅ Events processed: {len(events_received)}")
    print(f"📊 Metrics: {orch.get_metrics()}")
    
    # Cleanup
    orch.stop()
    print("\n✅ Test complete!")
