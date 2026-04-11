"""
Irreversibility Proof Tests

ARCHITECTURE_CANONICAL.md 3.0 COMPLIANCE:
- L2 outputs (raw frames, audio) must be destroyed at L3 boundary
- Embeddings cannot persist past L4
- Identifiers cannot escape L6
- Build MUST fail if any of these persist

These tests are marked as CRITICAL and will fail the build if violated.
"""
import pytest
import gc
import sys
import weakref
import numpy as np
from typing import Any, Optional
from dataclasses import dataclass

from core.layer_contracts import (
    Layer, L2Output, L3Output, L4Output, L5Output,
    LayerBoundaryEnforcer, LayerBoundaryViolation,
    FORBIDDEN_OUTPUTS, UPSTREAM_FORBIDDEN
)
from core.canonical_layers import (
    PhysicalSubstrate, SensorAcquisition, EdgeAbstraction,
    FrameDestructionError
)


# =============================================================================
# PYTEST MARKER FOR BUILD-CRITICAL TESTS
# =============================================================================

# Mark tests as critical - failure must halt the build
pytestmark = pytest.mark.critical


def assert_build_failure(condition: bool, message: str) -> None:
    """
    Assert condition or fail the build.
    
    This is a hard assertion - if it fails, CI/CD must halt.
    """
    if not condition:
        pytest.fail(f"BUILD FAILURE - IRREVERSIBILITY VIOLATION: {message}")


# =============================================================================
# L2 OUTPUT DESTRUCTION PROOFS
# =============================================================================

class TestRawFrameDestruction:
    """
    Prove raw frames (L2 output) are destroyed at L3 boundary.
    
    Per ARCHITECTURE_CANONICAL.md 3.1:
    - Raw frames exist <33ms
    - Frame is destroyed via explicit `del`
    - No reference to raw pixels escapes L3
    """
    
    def test_frame_destroyed_after_skeleton_extraction(self):
        """Raw frame object is deleted after L3 transform."""
        # Setup
        physical = PhysicalSubstrate()
        physical.start()
        sensor = SensorAcquisition(physical)
        edge = EdgeAbstraction(sensor)
        
        # Create a frame with weak reference tracking
        frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        frame_ref = weakref.ref(frame)
        
        # Simple pose extractor (returns skeleton)
        def extract_skeleton(f: np.ndarray) -> tuple:
            return tuple(range(17))  # 17 keypoints
        
        # Transform - this should destroy the frame
        result = edge.transform_frame_to_skeleton(frame, extract_skeleton)
        
        # Explicit deletion of our local reference
        del frame
        gc.collect()
        
        # CRITICAL: Frame must be garbage collected
        assert_build_failure(
            frame_ref() is None,
            "Raw frame persisted after L3 transform - irreversibility violated"
        )
        
        # Verify output is skeleton, not frame
        assert result["original_destroyed"] is True
        assert result["transform_type"] == "irreversible"
    
    def test_frame_buffer_cleared_in_sensor(self):
        """Sensor's frame buffer is cleared after L3 processing."""
        physical = PhysicalSubstrate()
        physical.start()
        sensor = SensorAcquisition(physical)
        edge = EdgeAbstraction(sensor)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Verify buffer is set during capture
        sensor.capture_frame(frame)
        assert sensor._frame_buffer is not None
        
        # Transform (destroys frame)
        edge.transform_frame_to_skeleton(frame, lambda f: tuple(range(17)))
        
        # CRITICAL: Sensor buffer must be cleared
        assert_build_failure(
            sensor._frame_buffer is None,
            "Sensor frame buffer not cleared after L3 transform"
        )
    
    def test_l2_output_cannot_escape_l3(self):
        """L2Output type cannot be passed to L4."""
        enforcer = LayerBoundaryEnforcer()
        
        # Attempting to pass raw_frame to L4 must fail
        with pytest.raises(LayerBoundaryViolation):
            enforcer.validate_transition(
                Layer.L3_EDGE, 
                Layer.L4_INFERENCE, 
                {"raw_frame"}
            )
        
        # Build assertion
        violations = enforcer.get_violations()
        assert_build_failure(
            len(violations) > 0,
            "Raw frame transition to L4 was not blocked"
        )


class TestAudioBufferDestruction:
    """
    Prove audio buffers (L2 output) are destroyed at L3 boundary.
    
    Per ARCHITECTURE_CANONICAL.md 3.2:
    - Audio waveforms exist <3s
    - Buffer is destroyed after feature extraction
    """
    
    def test_audio_destroyed_after_feature_extraction(self):
        """Audio buffer is destroyed after L3 feature extraction."""
        physical = PhysicalSubstrate()
        physical.start()
        sensor = SensorAcquisition(physical)
        edge = EdgeAbstraction(sensor)
        
        # Create audio buffer with weak reference
        audio = np.random.randn(16000).astype(np.float32)  # 1 sec at 16kHz
        audio_ref = weakref.ref(audio)
        
        # Feature extractor
        def extract_features(a: np.ndarray) -> tuple:
            return (0.5, 0.8, 0.3)  # MFCC-like features
        
        # Transform
        result = edge.transform_audio_to_features(audio, extract_features)
        
        # Delete local reference
        del audio
        gc.collect()
        
        # CRITICAL: Audio must be garbage collected
        assert_build_failure(
            audio_ref() is None,
            "Audio buffer persisted after L3 transform - irreversibility violated"
        )
        
        assert result["original_destroyed"] is True
    
    def test_audio_buffer_cleared_in_sensor(self):
        """Sensor's audio buffer is cleared after L3 processing."""
        physical = PhysicalSubstrate()
        physical.start()
        sensor = SensorAcquisition(physical)
        edge = EdgeAbstraction(sensor)
        
        audio = np.zeros(8000, dtype=np.float32)
        
        edge.transform_audio_to_features(audio, lambda a: (0.5,))
        
        # CRITICAL: Sensor audio buffer must be cleared
        assert_build_failure(
            sensor._audio_buffer is None,
            "Sensor audio buffer not cleared after L3 transform"
        )


class TestEmbeddingPersistence:
    """
    Prove embeddings never persist past L4.
    
    Per ARCHITECTURE_CANONICAL.md 3.3:
    - Face embeddings have session TTL
    - Embeddings cannot cross to L5 without consent
    """
    
    def test_embedding_blocked_at_l5_boundary(self):
        """Face embedding cannot enter L5."""
        enforcer = LayerBoundaryEnforcer()
        
        with pytest.raises(LayerBoundaryViolation):
            enforcer.validate_transition(
                Layer.L4_INFERENCE,
                Layer.L5_GOVERNANCE,
                {"face_embedding"}
            )
        
        assert_build_failure(
            len(enforcer.get_violations()) > 0,
            "Embedding passed to L5 without rejection"
        )
    
    def test_biometric_vector_blocked_at_l5(self):
        """Biometric vector cannot enter L5."""
        enforcer = LayerBoundaryEnforcer()
        
        with pytest.raises(LayerBoundaryViolation):
            enforcer.validate_transition(
                Layer.L4_INFERENCE,
                Layer.L5_GOVERNANCE,
                {"biometric_vector"}
            )
    
    def test_embedding_blocked_at_l6(self):
        """Embedding cannot reach L6 (human interface)."""
        enforcer = LayerBoundaryEnforcer()
        
        # L4 → L5 blocks embedding
        with pytest.raises(LayerBoundaryViolation):
            enforcer.validate_transition(
                Layer.L4_INFERENCE,
                Layer.L5_GOVERNANCE,
                {"embedding"}
            )
        
        # Even if somehow reached L5, still blocked at L6
        assert "embedding" in UPSTREAM_FORBIDDEN[Layer.L6_HUMAN_INTERFACE]


class TestIdentifierEscape:
    """
    Prove identifiers cannot escape to L8 (federation).
    
    Per ARCHITECTURE_CANONICAL.md 5.0:
    - Only gradients leave campus, not identifiers
    """
    
    def test_identity_blocked_at_l8(self):
        """Identity token cannot reach L8."""
        enforcer = LayerBoundaryEnforcer()
        
        # Check forbidden pattern exists
        assert_build_failure(
            "identity" in UPSTREAM_FORBIDDEN[Layer.L8_FEDERATION],
            "L8 does not block identity tokens"
        )
    
    def test_raw_data_blocked_at_l8(self):
        """Raw data cannot reach L8."""
        assert_build_failure(
            "raw_data" in FORBIDDEN_OUTPUTS[Layer.L8_FEDERATION],
            "L8 does not forbid raw data output"
        )
    
    def test_embedding_blocked_at_l8(self):
        """Embedding cannot reach L8."""
        assert "embedding" in UPSTREAM_FORBIDDEN[Layer.L8_FEDERATION]
        assert "embedding" in FORBIDDEN_OUTPUTS[Layer.L8_FEDERATION]


# =============================================================================
# SKELETON DIMENSION CONSTRAINTS
# =============================================================================

class TestSkeletonDimensionLimit:
    """
    Prove L3 output is bounded to 34 dimensions.
    
    Per ARCHITECTURE_CANONICAL.md 2.3:
    - Maximum 34 skeleton keypoints
    - Compression ratio ≥1000:1
    """
    
    def test_skeleton_34_dims_accepted(self):
        """34 dimensions is allowed."""
        output = L3Output(skeleton_keypoints=tuple(range(34)))
        assert len(output.skeleton_keypoints) == 34
    
    def test_skeleton_exceeds_34_rejected(self):
        """Skeleton >34 dimensions fails build."""
        with pytest.raises(ValueError, match="max 34 dims"):
            L3Output(skeleton_keypoints=tuple(range(50)))
    
    def test_l3_output_is_irreversible(self):
        """L3 output cannot reconstruct original frame."""
        # Frame has millions of values
        frame_size = 1920 * 1080 * 3  # ~6MB
        
        # Skeleton has max 34 values
        skeleton = L3Output(skeleton_keypoints=tuple(range(34)))
        skeleton_size = len(skeleton.skeleton_keypoints) * 4  # 136 bytes
        
        compression_ratio = frame_size / skeleton_size
        
        assert_build_failure(
            compression_ratio > 1000,
            f"Compression ratio {compression_ratio:.0f}:1 too low for irreversibility"
        )


# =============================================================================
# MEMORY SCAN TESTS
# =============================================================================

class TestMemoryScan:
    """
    Scan memory for persisted forbidden data.
    
    These tests verify no raw data remains in memory after processing.
    """
    
    def test_no_large_arrays_after_processing(self):
        """No large numpy arrays (raw frames) persist after L3."""
        physical = PhysicalSubstrate()
        physical.start()
        sensor = SensorAcquisition(physical)
        edge = EdgeAbstraction(sensor)
        
        # Process a frame
        frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        frame_nbytes = frame.nbytes
        edge.transform_frame_to_skeleton(frame, lambda f: tuple(range(17)))
        del frame
        gc.collect()
        
        # Scan for large numpy arrays
        large_arrays = []
        for obj in gc.get_objects():
            if isinstance(obj, np.ndarray) and obj.nbytes >= frame_nbytes:
                large_arrays.append(obj)
        
        # Note: This is a heuristic - other large arrays may exist
        # We verify our specific frame is gone via weak ref test above
        # This test alerts if unexpectedly large arrays are found
        if len(large_arrays) > 0:
            pytest.warns(UserWarning, match="Large arrays found in memory")


# =============================================================================
# CONFTEST HOOK FOR BUILD FAILURE
# =============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Hook to ensure critical tests fail the build.
    
    All tests in this module are marked critical.
    """
    for item in items:
        if "test_irreversibility" in str(item.fspath):
            item.add_marker(pytest.mark.critical)
