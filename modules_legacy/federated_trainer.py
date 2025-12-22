import faiss
import numpy as np
import json
import os
from insightface.app import FaceAnalysis

class FederatedTrainer:
    def __init__(self, index_path="data/face_index.faiss", identity_map_path="data/identity_map.json"):
        """
        Federated Learning Trainer for Privacy-Preserving Biometric Updates.
        Updates local FAISS index without transmitting raw biometric data.
        """
        self.index_path = index_path
        self.identity_map_path = identity_map_path
        
        # Initialize Face Analysis
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        
        # Load or create FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            # Create new index (512-dim for InsightFace)
            self.index = faiss.IndexFlatL2(512)
        
        # Load or create identity map
        if os.path.exists(self.identity_map_path):
            with open(self.identity_map_path, 'r') as f:
                self.identity_map = json.load(f)
        else:
            self.identity_map = {}
    
    
    def train_local(self, new_face_vectors):
        """
        Federated Learning: Update local model with new face vectors.
        Simulates privacy-preserving local training without cloud transmission.
        
        Args:
            new_face_vectors: List of 512-D numpy arrays (face embeddings)
            
        Returns:
            str: Status message
        """
        print("🔒 Federated Learning Mode: Privacy-First Training")
        print(f"   Processing {len(new_face_vectors)} new face vectors...")
        
        if len(new_face_vectors) == 0:
            print("❌ No vectors to add")
            return "Error: No data"
        
        # 1. Convert to numpy array and normalize
        embeddings_array = np.array(new_face_vectors).astype('float32')
        
        # Ensure correct shape
        if embeddings_array.ndim == 1:
            embeddings_array = embeddings_array.reshape(1, -1)
        
        # Normalize for consistent distance calculation
        faiss.normalize_L2(embeddings_array)
        
        # 2. Append to local cache (simulated model update)
        cache_path = "data/local_model_updates.bin"
        
        # Load existing cache if it exists
        if os.path.exists(cache_path):
            existing_cache = np.load(cache_path)
            updated_cache = np.vstack([existing_cache, embeddings_array])
        else:
            updated_cache = embeddings_array
        
        # Save updated cache (atomic write)
        temp_cache_path = cache_path + ".tmp"
        np.save(temp_cache_path, updated_cache)
        os.replace(temp_cache_path, cache_path)
        
        # 3. Update local FAISS index (for search capability)
        self.index.add(embeddings_array)
        
        # Save updated index (atomic write)
        temp_index_path = self.index_path + ".tmp"
        faiss.write_index(self.index, temp_index_path)
        os.replace(temp_index_path, self.index_path)
        
        # Log completion
        num_samples = len(new_face_vectors)
        print(f"✅ Local Model Updated with {num_samples} new samples")
        print("🔐 No data sent to cloud. Privacy preserved.")
        print(f"   Total vectors in local cache: {len(updated_cache)}")
        
        return "Success"

if __name__ == "__main__":
    # Test
    print("Federated Trainer initialized successfully!")
    trainer = FederatedTrainer()
    print(f"Current index size: {trainer.index.ntotal}")
