import sys
import os
import pytest
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

@pytest.fixture
def mock_registry():
    """Fixture to create a mocked FaceRegistry for testing."""
    with patch('modules.face_registry.FaceAnalysis') as mock_face_analysis, \
         patch('modules.face_registry.faiss') as mock_faiss, \
         patch('builtins.open', unittest.mock.mock_open(read_data='{"0": {"id": "S100", "name": "Existing User"}}')), \
         patch('json.load', return_value={"0": {"id": "S100", "name": "Existing User"}}), \
         patch('os.path.exists', return_value=True):
        
        from modules.face_registry import FaceRegistry
        
        # Setup Mock FAISS Index
        mock_index = MagicMock()
        type(mock_index).ntotal = unittest.mock.PropertyMock(return_value=5)
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.read_index.return_value = mock_index
        
        # Mock normalize_L2
        mock_faiss.normalize_L2 = MagicMock()
        
        # Setup Mock Search Result (Low distance = Match)
        mock_index.search.return_value = (np.array([[0.5]], dtype=np.float32), np.array([[0]], dtype=np.int64))
        
        # Setup Mock Face Analysis
        mock_app = MagicMock()
        mock_face_analysis.return_value = mock_app
        
        # Mock Face Detection Result
        mock_face = MagicMock()
        mock_face.embedding = np.random.rand(512).astype(np.float32)
        mock_app.get.return_value = [mock_face]
        
        registry = FaceRegistry()
        
        yield registry

def test_register_face_duplicate(mock_registry):
    """Test that registering a duplicate face returns False and 'Duplicate' message."""
    # Attempt to register
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    success, message = mock_registry.register_face(dummy_image, "S101", "New User", "Student")
    
    # Assertions
    assert success == False
    assert "Duplicate" in message
    assert "Existing User" in message
    print(f"✅ Duplicate detection verified: {message}")

def test_face_detection_failure(mock_registry):
    """Test that no face detected returns appropriate error."""
    # Mock no faces detected
    mock_registry.app.get.return_value = []
    
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    success, message = mock_registry.register_face(dummy_image, "S102", "Test User", "Student")
    
    assert success == False
    assert "No face detected" in message
    print(f"✅ No face detection verified: {message}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
