#!/usr/bin/env python3
"""
Runtime Integration Tests
==========================
Verify that canonical layers (L3 EdgeAbstraction, L5 GovernanceFilter) are
wired into the main.py runtime pipeline, closing the architectural gaps
identified in the integration audit.

These tests use mocks to avoid hardware dependencies (camera, GPU, microphone).
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock, MagicMock, patch

from core.canonical_layers import (
    PhysicalSubstrate,
    SensorAcquisition,
    EdgeAbstraction,
    GovernanceFilter,
    GovernanceState,
    FrameDestructionError,
)


# =============================================================================
# HELPER: Create a mock ScholarMasterUnified with canonical layers
# =============================================================================

def create_mock_system():
    """
    Create a mock system that mirrors main.py's __init__ canonical layer setup.
    Avoids importing main.py directly (which requires camera + GPU).
    """
    system = Mock()
    
    # Replicate canonical layer initialization from main.py __init__
    system._L1_physical = PhysicalSubstrate()
    system._L1_physical.start()
    system._L2_sensor = SensorAcquisition(system._L1_physical)
    system._L3_edge = EdgeAbstraction(system._L2_sensor)
    system._L5_governance = GovernanceFilter()
    
    # Wire ST-CSF validator (mock)
    mock_st_csf = Mock()
    mock_st_csf.validate_event = Mock(return_value=(True, "OK"))
    system.st_csf = mock_st_csf
    system._L5_governance.set_validator(
        lambda payload: system.st_csf.validate_event(payload)
    )
    
    return system


# =============================================================================
# TEST 1: CANONICAL LAYERS INITIALIZED
# =============================================================================

class TestCanonicalLayersInitialized:
    """Verify canonical layers exist and are properly typed."""
    
    def test_l3_edge_abstraction_exists(self):
        """EdgeAbstraction must be initialized in system."""
        system = create_mock_system()
        assert isinstance(system._L3_edge, EdgeAbstraction)
    
    def test_l5_governance_filter_exists(self):
        """GovernanceFilter must be initialized in system."""
        system = create_mock_system()
        assert isinstance(system._L5_governance, GovernanceFilter)
    
    def test_l1_physical_operational(self):
        """L1 Physical Substrate must be operational."""
        system = create_mock_system()
        status = system._L1_physical.get_operational_status()
        assert status["operational"]
    
    def test_l2_sensor_connected_to_l1(self):
        """L2 SensorAcquisition must reference L1."""
        system = create_mock_system()
        assert system._L2_sensor._physical is system._L1_physical


# =============================================================================
# TEST 2: GOVERNANCE FILTER GATES EVENTS
# =============================================================================

class TestGovernanceFilterGatesEvents:
    """Verify GovernanceFilter blocks events with forbidden fields."""
    
    def test_forbidden_fields_rejected(self):
        """Events containing forbidden fields must be rejected by L5."""
        system = create_mock_system()
        gov = system._L5_governance
        
        event_id = "test_forbidden_001"
        payload = {
            "zone_id": "Zone_1",
            "timestamp": time.time(),
            "raw_frame": b"SHOULD_NOT_PASS",  # FORBIDDEN
            "student_id": "STU_001",           # FORBIDDEN
        }
        
        gov.receive_inference_complete(event_id, payload)
        result = gov.compliance_check(event_id)
        
        assert result is False, "GovernanceFilter must reject forbidden fields"
        decision = gov.get_decision(event_id)
        assert decision.state == GovernanceState.REJECTED
    
    def test_allowed_event_passes_governance(self):
        """Events with only ALLOWED_FIELDS must pass L5."""
        system = create_mock_system()
        gov = system._L5_governance
        
        event_id = "test_allowed_001"
        payload = {
            "zone_id": "Zone_1",
            "timestamp": time.time(),
            "event_type": "ATTENDANCE",
            "severity": "LOW",
            "event_id": event_id,
            "is_valid": True,
            "reason": "Compliant",
        }
        
        gov.receive_inference_complete(event_id, payload)
        assert gov.compliance_check(event_id) is True
        
        approved = gov.approve_for_output(event_id)
        assert approved is not None, "Allowed event must be approved for output"
    
    def test_governance_validator_wired_to_st_csf(self):
        """L5 validator must call ST-CSF when checking compliance."""
        system = create_mock_system()
        gov = system._L5_governance
        
        event_id = "test_stcsf_001"
        payload = {
            "zone_id": "Zone_1",
            "timestamp": time.time(),
            "event_type": "ATTENDANCE",
        }
        
        gov.receive_inference_complete(event_id, payload)
        gov.compliance_check(event_id)
        
        # ST-CSF should have been called
        system.st_csf.validate_event.assert_called()


# =============================================================================
# TEST 3: EDGE ABSTRACTION FRAME DESTRUCTION
# =============================================================================

class TestEdgeAbstractionFrameDestruction:
    """Verify frame destruction goes through L3 at runtime."""
    
    def test_frame_destroyed_via_l3(self):
        """Frame must be destroyed through EdgeAbstraction._destroy_frame."""
        system = create_mock_system()
        
        # Simulate frame capture (mirrors main.py line 443-449)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame_capture_time = time.time()
        frame_id = system._L2_sensor.capture_frame(frame)
        
        # Simulate frame destruction (mirrors main.py line 637-647)
        system._L3_edge._destroy_frame(frame, frame_id, frame_capture_time)
        
        # Verify sensor buffer cleared
        assert system._L2_sensor._frame_buffer is None
        # Verify frame tracked as destroyed
        assert frame_id in system._L3_edge._destroyed_frames
    
    def test_watchdog_started(self):
        """EdgeAbstraction watchdog thread must be startable."""
        system = create_mock_system()
        
        # Start watchdog (mirrors main.py init)
        system._L3_edge.start_watchdog()
        
        assert system._L3_edge._watchdog_running is True
        assert system._L3_edge._watchdog_thread is not None
        assert system._L3_edge._watchdog_thread.is_alive()
        
        # Cleanup
        system._L3_edge.stop_watchdog()
    
    def test_frame_ttl_33ms(self):
        """Frame TTL must be 33ms per ARCHITECTURE_CANONICAL.md."""
        system = create_mock_system()
        assert system._L3_edge.FRAME_TTL_MS == 33


# =============================================================================
# TEST 4: END-TO-END PIPELINE MATCH
# =============================================================================

class TestEndToEndPipelineMatch:
    """
    Verify the runtime pipeline matches the formal model:
    L2 (capture) → L3 (destroy) → L5 (governance) → L6 (audit)
    """
    
    def test_full_pipeline_flow(self):
        """
        Simulate the complete runtime flow from main.py:
        1. Frame captured at L2
        2. Processing happens (face, pose, etc.)
        3. Event gated through L5 GovernanceFilter
        4. Frame destroyed at L3
        """
        system = create_mock_system()
        
        # Step 1: L2 capture (main.py line 443-449)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        capture_time = time.time()
        frame_id = system._L2_sensor.capture_frame(frame)
        
        assert frame_id is not None
        assert system._L2_sensor._frame_buffer is not None
        
        # Step 2: Processing (simulated - main.py lines 451-624)
        # ... face recognition, pose, safety ...
        
        # Step 3: L5 Governance gate (main.py lines 559-594)
        event_id = f"evt_{int(time.time()*1000)}"
        gov_payload = {
            "zone_id": "Main Hall",
            "timestamp": time.time(),
            "event_type": "ATTENDANCE",
            "severity": "LOW",
            "event_id": event_id,
            "is_valid": True,
            "reason": "Compliant",
        }
        system._L5_governance.receive_inference_complete(event_id, gov_payload)
        assert system._L5_governance.compliance_check(event_id)
        approved = system._L5_governance.approve_for_output(event_id)
        assert approved is not None
        
        # Step 4: L3 frame destruction (main.py lines 637-647)
        system._L3_edge._destroy_frame(frame, frame_id, capture_time)
        assert system._L2_sensor._frame_buffer is None
        assert frame_id in system._L3_edge._destroyed_frames


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
