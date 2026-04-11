#!/usr/bin/env python3
"""
Coverage Gap Remediation Tests
==============================
Verify fixes for the 5 coverage gaps identified in INVARIANT_ENFORCEMENT_AUDIT.md.

Gaps covered:
- G1: Audio destruction raises AudioDestructionError on TTL violation
- G2: Deletion request recomputes global model
- G3: FAISS remove_embedding rebuilds index (physical removal)
- G5: Privacy budget ceiling enforced (PrivacyBudgetExhaustedError)
"""

import sys
import types
from unittest.mock import MagicMock, Mock, patch

# =============================================================================
# ROBUST DEPENDENCY MOCKING
# =============================================================================
# Helper to create mock packages that pass "is not a package" checks
def mock_package(name):
    mock = MagicMock()
    mock.__path__ = [] # Crucial to be treated as a package
    sys.modules[name] = mock
    return mock

# 1. Mock base packages first
mock_package("insightface")
mock_package("mediapipe")
mock_package("sklearn")
mock_package("scipy")
mock_package("modules_legacy")

# 2. Mock submodules
sys.modules["insightface.app"] = MagicMock()
sys.modules["mediapipe.python"] = MagicMock()
sys.modules["mediapipe.python.solutions"] = MagicMock()
sys.modules["sklearn.metrics"] = MagicMock()
sys.modules["scipy.spatial"] = MagicMock()

# 3. Mock legacy submodules
sys.modules["modules_legacy.analytics"] = MagicMock()
sys.modules["modules_legacy.audio_sentinel"] = MagicMock()
sys.modules["modules_legacy.face_registry"] = MagicMock()
sys.modules["modules_legacy.context_aware"] = MagicMock()
sys.modules["modules_legacy.scheduler"] = MagicMock()
sys.modules["modules_legacy.auth"] = MagicMock()
sys.modules["modules_legacy.safety_rules"] = MagicMock()
sys.modules["modules_legacy.master_engine"] = MagicMock()

# 4. Mock simple modules
SIMPLE_MOCKS = [
    "cv2", "torch", "ultralytics", "pandas", 
    "sounddevice", "pyaudio", "librosa", "webrtcvad"
]
for mod in SIMPLE_MOCKS:
    sys.modules[mod] = MagicMock()

# 5. Handle FAISS specially
# We want to mock it but allow our test to control it
mock_faiss = MagicMock()
sys.modules["faiss"] = mock_faiss

import pytest
import time
import numpy as np
import shutil
import tempfile
import os

# Configure logging to prevent spam during tests
import logging
logging.basicConfig(level=logging.CRITICAL)

# Import core components
# Note: we import specific classes to avoid triggering full package inits if possible
from core.canonical_layers import (
    EdgeAbstraction,
    AudioDestructionError,
    FederationCoordinator,
    SensorAcquisition
)

# For FL Coordinator, safe to import as it only depends on numpy/standard libs
# (and we mocked things it might transitively import)
from modules.fl_coordinator import (
    FedAvgCoordinator,
    PrivacyBudgetExhaustedError
)

# For FAISS index, we use our mocked faiss
from infrastructure.indexing.faiss_face_index import FaissFaceIndex


# =============================================================================
# G1: Audio Destruction Exception
# =============================================================================

class TestG1_AudioDestruction:
    """Verify G1 fix: Audio destruction raises exception on TTL violation."""
    
    def test_audio_destruction_raises_error(self):
        """Test that _destroy_audio raises AudioDestructionError when TTL exceeded."""
        # Setup mock sensor
        mock_sensor = Mock(spec=SensorAcquisition)
        mock_sensor._audio_buffer = b"mock_audio"
        
        # Init EdgeAbstraction
        edge = EdgeAbstraction(mock_sensor)
        
        # Simulate audio captured 4 seconds ago (TTL is 3s)
        capture_time = time.time() - 4.0
        audio_id = 12345
        audio_data = b"expired_audio"
        
        # Should raise AudioDestructionError
        with pytest.raises(AudioDestructionError) as excinfo:
            edge._destroy_audio(audio_data, audio_id, capture_time)
            
        assert "Audio lifetime exceeded" in str(excinfo.value)
        assert mock_sensor._audio_buffer is None  # Buffer should still be cleared


# =============================================================================
# G2: Deletion Recomputes Global Model
# =============================================================================

class TestG2_DeletionRecompute:
    """Verify G2 fix: Deletion request recomputes global model."""
    
    def test_deletion_recomputes_global_model(self):
        """Test that removing an individual triggers model recomputation."""
        coord = FederationCoordinator()
        
        # Mock some gradient contributions
        # We need objects with 'individual_id' attribute
        # Using a simple class instead of Mock to ensure attribute access works simply
        class MockGrad:
            def __init__(self, ind_id, val):
                self.individual_id = ind_id
                self.data = val
                
        g1 = MockGrad("student_1", 10)
        g2 = MockGrad("student_2", 20)
        g3 = MockGrad("student_1", 11) 
        
        coord._gradient_contributions = {
            "campus_A": [g1, g2, g3]
        }
        coord._global_model_version = 1
        
        # Process deletion for student_1
        coord.process_deletion_request("campus_A", "student_1")
        
        # 1. Check student_1 gradients are gone
        remaining = coord._gradient_contributions["campus_A"]
        assert len(remaining) == 1
        assert remaining[0].individual_id == "student_2"
        
        # 2. Check model version incremented
        assert coord._global_model_version == 2


# =============================================================================
# G3: FAISS Index Rebuild
# =============================================================================

class TestG3_FaissRebuild:
    """Verify G3 fix: remove_embedding rebuilds index."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_remove_embedding_rebuilds_index(self):
        """Test that removing an embedding physically reduces index size."""
        # Create temp files
        test_dir = tempfile.mkdtemp()
        try:
            index_file = os.path.join(test_dir, "index.bin")
            map_file = os.path.join(test_dir, "map.json")
            
            # Setup mock FAISS
            mock_faiss = sys.modules["faiss"]
            
            # Mock the IndexFlatL2
            mock_index = Mock()
            mock_index.ntotal = 3
            mock_index.get_xb.return_value = "mock_ptr"
            
            # Setup read_index to return our mock
            mock_faiss.read_index.return_value = mock_index
            
            # Setup IndexFlatL2 constructor to return our mock (initially)
            # and a NEW mock (on rebuild)
            new_mock_index = Mock()
            mock_faiss.IndexFlatL2.side_effect = [mock_index, new_mock_index, new_mock_index]
            
            # Mock rev_swig_ptr to return fake vectors
            # 3 vectors of dim 128
            fake_vectors = np.zeros((3, 128), dtype='float32')
            fake_vectors[0, 0] = 1.0 # vec 0
            fake_vectors[1, 0] = 2.0 # vec 1 (to remove)
            fake_vectors[2, 0] = 3.0 # vec 2
            
            mock_faiss.rev_swig_ptr.return_value = fake_vectors.flatten()
            
            # Init index
            faiss_idx = FaissFaceIndex(
                index_file=index_file, 
                identity_map_file=map_file,
                embedding_dim=128
            )
            
            # Manually set state to bypass file loading logic if mocks didn't catch it
            faiss_idx.index = mock_index
            faiss_idx.identity_map = {
                "0": "s1",
                "1": "s2", # Target to remove
                "2": "s3"
            }
            
            # Reset side effect for next call (the rebuild call)
            # We want the next IndexFlatL2 call to return new_mock_index
            mock_faiss.IndexFlatL2.side_effect = None
            mock_faiss.IndexFlatL2.return_value = new_mock_index
            
            # Call remove_embedding for "s2"
            result = faiss_idx.remove_embedding("s2")
            
            assert result is True
            
            # VERIFY REBUILD LOGIC:
            # 1. New index created
            assert faiss_idx.index == new_mock_index
            
            # 2. Add called exactly twice (for s1 and s3)
            assert new_mock_index.add.call_count == 2
            
            # 3. Verify identity map updated correctly
            # Should now look like {"0": "s1", "1": "s3"} (re-indexed)
            assert len(faiss_idx.identity_map) == 2
            assert faiss_idx.identity_map["0"] == "s1"
            assert faiss_idx.identity_map["1"] == "s3"
            
        finally:
            shutil.rmtree(test_dir)


# =============================================================================
# G5: Privacy Budget Ceiling
# =============================================================================

class TestG5_PrivacyBudgetCeiling:
    """Verify G5 fix: Privacy budget ceiling enforcement."""
    
    def test_budget_ceiling_enforced(self):
        """Test that training halts if epsilon would exceed max."""
        coord = FedAvgCoordinator(privacy_sigma=0.5)
        
        # Set a low ceiling for testing
        coord.MAX_EPSILON = 10.0
        
        # Force current epsilon to be near limit
        coord.epsilon = 9.0
        
        gradients = np.zeros(10)
        
        # Should raise PrivacyBudgetExhaustedError
        with pytest.raises(PrivacyBudgetExhaustedError) as excinfo:
            coord.apply_differential_privacy(gradients)
            
        assert "Privacy budget would exceed ceiling" in str(excinfo.value)
        
        # Verify epsilon was NOT updated
        assert coord.epsilon == 9.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
