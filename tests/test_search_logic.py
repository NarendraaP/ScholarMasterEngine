import numpy as np
import os
import sys
import shutil

# Add project root to path
sys.path.append(os.getcwd())

from modules.face_registry import FaceRegistry

def test_search():
    print("--- Testing Face Search ---")
    
    # Setup clean test environment
    test_dir = "test_data_search"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    registry = FaceRegistry(data_dir=test_dir)
    
    # Check if identity_map created
    if os.path.exists(os.path.join(test_dir, "identity_map.json")):
        print("✅ Identity Map created on init.")
    else:
        print("❌ Identity Map NOT created.")
        
    # Create dummy embedding (normalized)
    emb1 = np.random.rand(512).astype('float32')
    emb1 = emb1 / np.linalg.norm(emb1)
    
    # Register Face
    print("Registering User A...")
    # Mocking image_array passing by mocking app.get? 
    # Actually, register_face expects an image and uses InsightFace to get embedding.
    # We can't easily mock InsightFace without a real image or heavy mocking.
    # However, we can test `search_face` directly if we manually populate the index for this test,
    # OR we can trust the integration if we had a real image.
    # Let's try to manually add to index to test search logic specifically.
    
    registry.index.add(emb1.reshape(1, -1))
    registry.identity_map["0"] = {"id": "UserA", "name": "Alice"}
    
    # Test Search (Exact Match)
    print("Searching for User A (Exact Embedding)...")
    found, uid = registry.search_face(emb1)
    if found and uid == "UserA":
        print("✅ Found User A correctly.")
    else:
        print(f"❌ Failed to find User A. Result: {found}, {uid}")
        
    # Test Search (Near Match)
    print("Searching for User A (Near Embedding)...")
    # Perturb slightly
    emb_near = emb1 + 0.01 * np.random.rand(512).astype('float32')
    emb_near = emb_near / np.linalg.norm(emb_near)
    
    found, uid = registry.search_face(emb_near)
    if found and uid == "UserA":
        print("✅ Found User A (Near Match).")
    else:
        print(f"❌ Failed to find User A (Near Match). Result: {found}, {uid}")
        
    # Test Search (No Match)
    print("Searching for Random User...")
    emb_rand = np.random.rand(512).astype('float32')
    emb_rand = emb_rand / np.linalg.norm(emb_rand)
    # Make sure it's far orthogonal
    while np.dot(emb1, emb_rand) > 0.4:
         emb_rand = np.random.rand(512).astype('float32')
         emb_rand = emb_rand / np.linalg.norm(emb_rand)
         
    found, uid = registry.search_face(emb_rand)
    if not found:
        print("✅ Correctly identified Unknown.")
    else:
        print(f"❌ Incorrectly matched Random User. Result: {found}, {uid}")

    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_search()
