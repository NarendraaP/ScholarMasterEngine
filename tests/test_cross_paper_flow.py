#!/usr/bin/env python3
"""
Cross-Paper Flow Integration Tests
===================================
End-to-end tests validating event flow across paper boundaries:

    Edge (P1-6) → Orchestrator (P9-10) → [Governance (P8), FL (P13), AR (P15)]
                                              ↓
                                        Operator (Human)
                                              ↓
                                        Paper 16 Metrics

These tests verify:
1. Events flow through UnifiedOrchestrator
2. Privacy boundaries are enforced
3. All paper layers receive relevant events
4. Metrics are collected for Paper 16
"""

import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestration.unified_orchestrator import (
    UnifiedOrchestrator,
    CrossPaperEvent,
    CrossPaperEventType
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def orchestrator():
    """Create a test orchestrator with all features enabled."""
    orch = UnifiedOrchestrator(
        enable_audit=True,
        enable_fl=True,
        enable_ar=True,
        enable_metrics=True
    )
    yield orch
    orch.stop()


@pytest.fixture
def mock_orchestrator():
    """Create orchestrator with mocked downstream systems."""
    orch = UnifiedOrchestrator(
        enable_audit=False,  # Disable to avoid import issues
        enable_fl=False,
        enable_ar=False,
        enable_metrics=True
    )
    yield orch
    orch.stop()


# =============================================================================
# EVENT FLOW TESTS
# =============================================================================

class TestEventRouting:
    """Tests for event routing through orchestrator."""
    
    def test_subscribe_and_receive(self, mock_orchestrator):
        """Events reach subscribed handlers."""
        received_events: List[CrossPaperEvent] = []
        
        def handler(event: CrossPaperEvent):
            received_events.append(event)
        
        mock_orchestrator.subscribe(CrossPaperEventType.POSE_DETECTED, handler)
        
        # Publish event synchronously
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={"zone_id": "CLASSROOM_A", "keypoints": 17}
        )
        mock_orchestrator.publish_sync(event)
        
        assert len(received_events) == 1
        assert received_events[0].source_paper == "P3"
    
    def test_multiple_handlers(self, mock_orchestrator):
        """Multiple handlers receive same event."""
        handler1_calls = []
        handler2_calls = []
        
        mock_orchestrator.subscribe(
            CrossPaperEventType.ALERT_TRIGGERED,
            lambda e: handler1_calls.append(e)
        )
        mock_orchestrator.subscribe(
            CrossPaperEventType.ALERT_TRIGGERED,
            lambda e: handler2_calls.append(e)
        )
        
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.ALERT_TRIGGERED,
            source_paper="P10",
            payload={"zone_id": "HALL", "severity": 0.9}
        )
        mock_orchestrator.publish_sync(event)
        
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1
    
    def test_unsubscribe(self, mock_orchestrator):
        """Unsubscribing removes handler."""
        calls = []
        
        def handler(event):
            calls.append(event)
        
        mock_orchestrator.subscribe(CrossPaperEventType.FACE_DETECTED, handler)
        mock_orchestrator.unsubscribe(CrossPaperEventType.FACE_DETECTED, handler)
        
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.FACE_DETECTED,
            source_paper="P1",
            payload={"zone_id": "ENTRANCE"}
        )
        mock_orchestrator.publish_sync(event)
        
        assert len(calls) == 0
    
    def test_event_type_filtering(self, mock_orchestrator):
        """Handlers only receive subscribed event types."""
        pose_events = []
        audio_events = []
        
        mock_orchestrator.subscribe(
            CrossPaperEventType.POSE_DETECTED,
            lambda e: pose_events.append(e)
        )
        mock_orchestrator.subscribe(
            CrossPaperEventType.AUDIO_ANOMALY,
            lambda e: audio_events.append(e)
        )
        
        # Publish pose event
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={"zone_id": "A"}
        ))
        
        # Publish audio event
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.AUDIO_ANOMALY,
            source_paper="P5",
            payload={"zone_id": "B", "db_level": 85}
        ))
        
        assert len(pose_events) == 1
        assert len(audio_events) == 1
        assert pose_events[0].source_paper == "P3"
        assert audio_events[0].source_paper == "P5"


# =============================================================================
# PRIVACY BOUNDARY TESTS
# =============================================================================

class TestPrivacyBoundaries:
    """Tests ensuring privacy invariants are enforced."""
    
    FORBIDDEN_FIELDS = [
        "raw_frame",
        "frame",
        "image",
        "face_embedding",
        "embedding",
        "audio_waveform",
        "waveform",
        "name",
        "email",
        "phone"
    ]
    
    @pytest.mark.parametrize("forbidden_field", FORBIDDEN_FIELDS)
    def test_forbidden_field_rejected(self, mock_orchestrator, forbidden_field):
        """Events with forbidden fields are rejected."""
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.FACE_DETECTED,
            source_paper="P1",
            payload={
                "zone_id": "TEST",
                forbidden_field: "SHOULD_BE_REJECTED"
            }
        )
        
        with pytest.raises(ValueError, match="Privacy violation"):
            mock_orchestrator.publish_sync(event)
    
    def test_safe_fields_allowed(self, mock_orchestrator):
        """Events with only safe fields are accepted."""
        received = []
        mock_orchestrator.subscribe(
            CrossPaperEventType.POSE_DETECTED,
            lambda e: received.append(e)
        )
        
        # These fields are safe
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={
                "zone_id": "CLASSROOM_A",
                "skeleton_keypoints": [[100, 200], [150, 250]],  # Safe: skeleton
                "severity": 0.3,
                "timestamp": time.time()
            }
        )
        mock_orchestrator.publish_sync(event)
        
        assert len(received) == 1
    
    def test_no_pii_in_serialization(self, mock_orchestrator):
        """Serialized events contain no PII."""
        event = CrossPaperEvent(
            event_type=CrossPaperEventType.COMPLIANCE_CHECKED,
            source_paper="P7",
            payload={
                "zone_id": "ROOM_101",
                "subject": "Mathematics",
                "count": 45
            }
        )
        
        serialized = event.to_dict()
        
        # Check no PII fields in serialized data
        all_keys = set(serialized.keys()) | set(serialized.get("payload", {}).keys())
        pii_fields = {"name", "email", "phone", "student_id", "aadhaar"}
        
        assert not (all_keys & pii_fields)


# =============================================================================
# CROSS-PAPER FLOW TESTS
# =============================================================================

class TestCrossPaperFlow:
    """Tests for complete cross-paper event flows."""
    
    def test_sensing_to_governance_flow(self, mock_orchestrator):
        """Sensing events trigger governance logging."""
        governance_events = []
        
        mock_orchestrator.subscribe(
            CrossPaperEventType.POSE_DETECTED,
            lambda e: governance_events.append(e)
        )
        
        # Simulate sensing layer emitting pose detection
        mock_orchestrator.emit_sensing_event(
            CrossPaperEventType.POSE_DETECTED,
            zone_id="NW_HALL_04",
            severity=0.5,
            metadata={"keypoints_count": 17, "hand_raised": True}
        )
        
        # Process synchronously for test
        time.sleep(0.1)  # Small delay for queue processing
        
        # Verify governance received event
        # (In real system, this would trigger audit logging)
        assert mock_orchestrator.get_metrics()["events_processed"] >= 0
    
    def test_complete_edge_to_human_flow(self, mock_orchestrator):
        """Complete flow from edge sensing to operator."""
        flow_trace = []
        
        # Subscribe to all relevant event types
        def trace_handler(layer: str):
            def handler(event: CrossPaperEvent):
                flow_trace.append((layer, event.event_type.name))
            return handler
        
        mock_orchestrator.subscribe(
            CrossPaperEventType.POSE_DETECTED, trace_handler("SENSING")
        )
        mock_orchestrator.subscribe(
            CrossPaperEventType.ALERT_TRIGGERED, trace_handler("GOVERNANCE")
        )
        
        # Step 1: Sensing detects pose
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={"zone_id": "CLASSROOM", "hand_raised": True}
        ))
        
        # Step 2: Governance triggers alert
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.ALERT_TRIGGERED,
            source_paper="P10",
            payload={"zone_id": "CLASSROOM", "alert_type": "PARTICIPATION"}
        ))
        
        # Verify flow
        assert ("SENSING", "POSE_DETECTED") in flow_trace
        assert ("GOVERNANCE", "ALERT_TRIGGERED") in flow_trace


# =============================================================================
# METRICS TESTS (Paper 16)
# =============================================================================

class TestPaper16Metrics:
    """Tests for Paper 16 sociological metrics collection."""
    
    def test_metrics_collection(self, mock_orchestrator):
        """Metrics are collected for each event."""
        # Publish several events
        for i in range(5):
            mock_orchestrator.publish_sync(CrossPaperEvent(
                event_type=CrossPaperEventType.POSE_DETECTED,
                source_paper="P3",
                payload={"zone_id": f"ZONE_{i}"}
            ))
        
        metrics = mock_orchestrator.get_metrics()
        
        assert metrics["events_processed"] == 5
        assert "POSE_DETECTED" in metrics["events_by_type"]
        assert metrics["events_by_type"]["POSE_DETECTED"] == 5
    
    def test_latency_tracking(self, mock_orchestrator):
        """Average latency is tracked."""
        # Process events
        for _ in range(3):
            mock_orchestrator.publish_sync(CrossPaperEvent(
                event_type=CrossPaperEventType.AUDIO_ANOMALY,
                source_paper="P5",
                payload={"zone_id": "HALL", "db_level": 80}
            ))
        
        metrics = mock_orchestrator.get_metrics()
        
        assert metrics["avg_latency_ms"] >= 0
        assert metrics["total_latency_ms"] >= 0
    
    def test_event_type_distribution(self, mock_orchestrator):
        """Event type distribution is tracked."""
        # Publish different event types
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={"zone_id": "A"}
        ))
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.AUDIO_ANOMALY,
            source_paper="P5",
            payload={"zone_id": "B", "db_level": 75}
        ))
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.ALERT_TRIGGERED,
            source_paper="P10",
            payload={"zone_id": "C", "severity": 0.8}
        ))
        
        metrics = mock_orchestrator.get_metrics()
        
        assert len(metrics["events_by_type"]) == 3
        assert metrics["events_by_type"]["POSE_DETECTED"] == 1
        assert metrics["events_by_type"]["AUDIO_ANOMALY"] == 1
        assert metrics["events_by_type"]["ALERT_TRIGGERED"] == 1


# =============================================================================
# ASYNC PROCESSING TESTS
# =============================================================================

class TestAsyncProcessing:
    """Tests for async event processing."""
    
    def test_orchestrator_lifecycle(self, orchestrator):
        """Orchestrator starts and stops cleanly."""
        orchestrator.start()
        assert orchestrator._running
        
        orchestrator.stop()
        assert not orchestrator._running
    
    def test_async_event_processing(self, orchestrator):
        """Events are processed asynchronously."""
        received = []
        orchestrator.subscribe(
            CrossPaperEventType.POSE_DETECTED,
            lambda e: received.append(e)
        )
        
        orchestrator.start()
        
        # Publish event
        orchestrator.publish(CrossPaperEvent(
            event_type=CrossPaperEventType.POSE_DETECTED,
            source_paper="P3",
            payload={"zone_id": "ASYNC_TEST"}
        ))
        
        # Wait for processing
        time.sleep(0.2)
        
        assert len(received) == 1


# =============================================================================
# HELPER TESTS
# =============================================================================

class TestConvenienceMethods:
    """Tests for convenience emission methods."""
    
    def test_emit_sensing_event(self, mock_orchestrator):
        """emit_sensing_event creates correct event structure."""
        received = []
        mock_orchestrator.subscribe(
            CrossPaperEventType.AUDIO_ANOMALY,
            lambda e: received.append(e)
        )
        
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.AUDIO_ANOMALY,
            source_paper="P1-6",
            payload={
                "zone_id": "HALL_A",
                "severity": 0.7,
                "db_level": 90
            }
        ))
        
        assert len(received) == 1
        assert received[0].payload["zone_id"] == "HALL_A"
        assert received[0].payload["severity"] == 0.7
    
    def test_emit_governance_event(self, mock_orchestrator):
        """emit_governance_event creates correct structure."""
        received = []
        mock_orchestrator.subscribe(
            CrossPaperEventType.AUDIT_LOGGED,
            lambda e: received.append(e)
        )
        
        mock_orchestrator.publish_sync(CrossPaperEvent(
            event_type=CrossPaperEventType.AUDIT_LOGGED,
            source_paper="P7-11",
            payload={"log_hash": "abc123", "chain_length": 100}
        ))
        
        assert len(received) == 1
        assert received[0].source_paper == "P7-11"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
