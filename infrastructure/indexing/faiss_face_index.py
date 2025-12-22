"""
Infrastructure Layer - FAISS Face Index

Implements IFaceIndex interface using FAISS library.
"""
from typing import Tuple, Optional
import numpy as np
import faiss
import json
import os

from domain.interfaces import IFaceIndex
from utils.logging_config import logger
from utils.config import FAISS_INDEX_PATH, DATA_PATH


class FaissFaceIndex(IFaceIndex):
    """
    FAISS-based implementation of face embedding storage.
    
    Uses FAISS for efficient similarity search and JSON for identity mapping.
    """
    
    def __init__(self, 
                 index_file: str = None,
                 identity_map_file: str = None,
                 embedding_dim: int = 512):
        """
        Initialize FAISS index.
        
        Args:
            index_file: Path to FAISS index file (defaults to config)
            identity_map_file: Path to identity mapping JSON
            embedding_dim: Dimension of face embeddings
        """
        self.index_file = index_file or os.path.join(DATA_PATH, "faiss_index.bin")
        self.identity_map_file = identity_map_file or os.path.join(DATA_PATH, "identity_map.json")
        self.embedding_dim = embedding_dim
        
        # Initialize or load index with error handling
        if os.path.exists(self.index_file):
            try:
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Corrupted FAISS index at {self.index_file}: {e}")
                logger.warning("Creating new index to replace corrupted one")
                self.index = faiss.IndexFlatL2(embedding_dim)
        else:
            # Create L2 index
            self.index = faiss.IndexFlatL2(embedding_dim)
            logger.info("Created new FAISS index")
        
        # Load identity mapping: {index_position: student_id}
        if os.path.exists(self.identity_map_file):
            try:
                with open(self.identity_map_file, 'r') as f:
                    self.identity_map = json.load(f)
                logger.debug(f"Loaded {len(self.identity_map)} identity mappings")
            except Exception as e:
                logger.error(f"Failed to load identity map: {e}")
                self.identity_map = {}
        else:
            self.identity_map = {}
            logger.info("Created new identity mapping")
    
    def add_embedding(self, student_id: str, embedding: np.ndarray) -> bool:
        """
        Add face embedding to FAISS index.
        
        Args:
            student_id: Unique identifier
            embedding: 512-dimensional vector
            
        Returns:
            True if successful
        """
        try:
            # Normalize embedding (L2)
            embedding = embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(embedding)
            
            # Add to index
            self.index.add(embedding)
            
            # Map position to student ID
            position = self.index.ntotal - 1
            self.identity_map[str(position)] = student_id
            
            # Persist
            self._save()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add embedding for {student_id}: {e}")
            return False
    
    def search(self, embedding: np.ndarray, threshold: float = 0.6) -> Tuple[bool, Optional[str]]:
        """
        Search for matching face.
        
        Args:
            embedding: Query vector
            threshold: Similarity threshold (lower distance = more similar)
            
        Returns:
            (found, student_id) tuple
        """
        try:
            if self.index.ntotal == 0:
                return False, None
            
            # Normalize query
            embedding = embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(embedding)
            
            # Search (k=1 for closest match)
            distances, indices = self.index.search(embedding, k=1)
            
            distance = float(distances[0][0])
            index_pos = int(indices[0][0])
            
            # Convert distance to similarity (lower is better for L2)
            # Threshold: typical range 0.4-0.8 for L2 normalized vectors
            if distance < threshold:
                student_id = self.identity_map.get(str(index_pos))
                return True, student_id
            else:
                return False, None
                
        except Exception as e:
            logger.error(f"Face search failed: {e}")
            return False, None
    
    def remove_embedding(self, student_id: str) -> bool:
        """
        Remove embedding (FAISS doesn't support direct removal).
        
        This is a limitation - would need to rebuild index.
        For now, just remove from identity map.
        """
        try:
            # Find and remove from identity map
            for pos, sid in list(self.identity_map.items()):
                if sid == student_id:
                    del self.identity_map[pos]
            
            self._save()
            logger.info(f"Removed embedding for {student_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove embedding for {student_id}: {e}")
            return False
    
    def get_count(self) -> int:
        """Get number of indexed faces"""
        return self.index.ntotal
    
    def _save(self):
        """Persist index and mapping to disk"""
        # Save FAISS index
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        faiss.write_index(self.index, self.index_file)
        
        # Save identity mapping
        with open(self.identity_map_file, 'w') as f:
            json.dump(self.identity_map, f, indent=4)
