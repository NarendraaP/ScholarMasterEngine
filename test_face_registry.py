import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

def test_imports():
    print("Testing imports...")
    try:
        import insightface
        import onnxruntime
        import faiss
        print("✅ Imports successful: insightface, onnxruntime, faiss")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

def test_registry_init():
    print("\nTesting FaceRegistry initialization...")
    try:
        from modules.face_registry import FaceRegistry
        registry = FaceRegistry()
        print("✅ FaceRegistry initialized successfully")
        print(f"   - FAISS Index size: {registry.index.ntotal}")
        print(f"   - Identity Map size: {len(registry.identity_map)}")
        return registry
    except Exception as e:
        print(f"❌ FaceRegistry initialization failed: {e}")
        sys.exit(1)

def test_face_detection_failure(registry):
    print("\nTesting face detection (expecting failure on dummy image)...")
    # Create a blank black image
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    
    success, message = registry.register_face(dummy_image, "test_id", "Test User", "Student")
    
    if not success and "No face detected" in message:
        print(f"✅ Correctly handled no-face image: {message}")
    else:
        print(f"❌ Unexpected result: Success={success}, Message={message}")

if __name__ == "__main__":
    test_imports()
    registry = test_registry_init()
    test_face_detection_failure(registry)
    print("\n🎉 Verification Complete!")
