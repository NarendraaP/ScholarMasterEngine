"""
Face Recognizer - Infrastructure Adapter

Implements IFaceRecognizer using InsightFace + FAISS (Paper 1).
"""
from typing import List, Tuple, Optional
import numpy as np
from insightface.app import FaceAnalysis
import faiss
import os
import json

from core.interfaces.i_face_recognizer import IFaceRecognizer, Face


class FaceRecognizer(IFaceRecognizer):
    """
    InsightFace + FAISS implementation of face recognition.
    
    Papers:
    - Paper 1: ArcFace for deep face recognition
    - Uses adaptive threshold based on gallery size
    """
    
    def __init__(self,  model_root="~/.insightface", faiss_index_path="data/faiss_index.bin", student_ids_path="data/student_ids.json"):
        """Initialize InsightFace and FAISS index"""
        # Initialize InsightFace
        self.app = FaceAnalysis(name='buffalo_sc', root=model_root, providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        # FAISS index
        self.faiss_index_path = faiss_index_path
        self.student_ids_path = student_ids_path
        
        # Load existing index or create new
        if os.path.exists(faiss_index_path) and os.path.exists(student_ids_path):
            self.index = faiss.read_index(faiss_index_path)
            with open(student_ids_path, 'r') as f:
                self.student_ids = json.load(f)
            print(f"✅ Loaded FAISS index with {len(self.student_ids)} faces")
        else:
            # Create new index (512-dim L2)
            self.index = faiss.IndexFlatL2(512)
            self.student_ids = []
            print("✅ Created new FAISS index")
    
    def detect_faces(self, frame: np.ndarray) -> List[Face]:
        """Detect all faces in frame using InsightFace"""
        insightface_faces = self.app.get(frame)
        
        faces = []
        for f in insightface_faces:
            face = Face(
                bbox=f.bbox.astype(int),
                embedding=f.embedding,
                confidence=f.det_score if hasattr(f, 'det_score') else 0.9,
                landmarks=f.landmark_2d_106 if hasattr(f, 'landmark_2d_106') else None
            )
            faces.append(face)
        
        return faces
    
    def search_face(self, embedding: np.ndarray) -> Tuple[bool, Optional[str]]:
        """Search for face in FAISS gallery"""
        if len(self.student_ids) == 0:
            return False, None
        
        # Get adaptive threshold based on gallery size (Paper 1)
        tau = self._get_adaptive_threshold(len(self.student_ids))
        
        # Search in FAISS (k=1, nearest neighbor)
        embedding_query = embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(embedding_query, k=1)
        
        distance = distances[0][0]
        idx = indices[0][0]
        
        # Check if distance is below threshold
        if distance < tau and idx < len(self.student_ids):
            return True, self.student_ids[idx]
        else:
            return False, None
    
    def enroll_face(self, student_id: str, embedding: np.ndarray) -> bool:
        """Add face to FAISS gallery"""
        try:
            # Add to FAISS index
            embedding_vec = embedding.reshape(1, -1).astype('float32')
            self.index.add(embedding_vec)
            
            # Add student ID
            self.student_ids.append(student_id)
            
            # Persist to disk
            faiss.write_index(self.index, self.faiss_index_path)
            with open(self.student_ids_path, 'w') as f:
                json.dump(self.student_ids, f)
            
            print(f"✅ Enrolled face for {student_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to enroll {student_id}: {e}")
            return False
    
    def get_gallery_size(self) -> int:
        """Get number of enrolled faces"""
        return len(self.student_ids)
    
    def _get_adaptive_threshold(self, gallery_size: int) -> float:
        """
        Calculate adaptive threshold based on gallery size (Paper 1).
        
        Larger galleries require stricter thresholds to maintain precision.
        """
        if gallery_size < 10:
            return 1.2  # Lenient for small galleries
        elif gallery_size < 100:
            return 1.0  # Medium
        elif gallery_size < 1000:
            return 0.8 # Strict
        else:
            return 0.6  # Very strict for large galleries
