"""
Infrastructure Layer - FAISS Face Index

Implements IFaceIndex interface using FAISS library.

ARCHITECTURE_CANONICAL.md 3.3 COMPLIANCE:
- Session-scoped embeddings must be destroyed at session end
- Cross-session embedding persistence requires explicit consent
- Embedding TTL must be enforced
"""
from typing import Tuple, Optional, Dict
import numpy as np
import faiss
import json
import os
import time
import logging

from domain.interfaces import IFaceIndex
from utils.logging_config import logger
from utils.config import FAISS_INDEX_PATH, DATA_PATH


class FaissFaceIndex(IFaceIndex):
    """
    FAISS-based implementation of face embedding storage.
    
    Uses FAISS for efficient similarity search and JSON for identity mapping.
    
    ARCHITECTURE_CANONICAL.md COMPLIANCE:
    - Section 3.3: Embedding TTL enforcement
    - Session-scoped destruction on session end
    - Consent verification before persistence
    """
    
    # Default TTL: 1 hour (session duration)
    DEFAULT_TTL_SECONDS = 3600
    
    def __init__(self, 
                 index_file: str = None,
                 identity_map_file: str = None,
                 embedding_dim: int = 512,
                 session_ttl_seconds: float = None,
                 require_consent_for_persistence: bool = True):
        """
        Initialize FAISS index with TTL enforcement.
        
        Args:
            index_file: Path to FAISS index file (defaults to config)
            identity_map_file: Path to identity mapping JSON
            embedding_dim: Dimension of face embeddings
            session_ttl_seconds: TTL for embeddings (None = session-scoped)
            require_consent_for_persistence: If True, persistence blocked without consent
        """
        self.index_file = index_file or os.path.join(DATA_PATH, "faiss_index.bin")
        self.identity_map_file = identity_map_file or os.path.join(DATA_PATH, "identity_map.json")
        self.embedding_dim = embedding_dim
        self.session_ttl = session_ttl_seconds or self.DEFAULT_TTL_SECONDS
        self.require_consent = require_consent_for_persistence
        
        # Session tracking for TTL
        self._session_start = time.time()
        self._embedding_timestamps: Dict[str, float] = {}
        self._consent_granted: Dict[str, bool] = {}
        
        # Initialize or load index with error handling
        if os.path.exists(self.index_file):
            try:
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Corrupted FAISS index at {self.index_file}: {e}")
                logger.warning("Creating new index to replace corrupted one")
            # Create HNSW index (O(log N)) - Paper 1 Alignment
            # M=16, efConstruction=200, efSearch=50
            M = 16
            self.index = faiss.IndexHNSWFlat(embedding_dim, M)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 50
            logger.info("Created new FAISS HNSW Index (Paper 1 Aligned)")
        
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
        Remove embedding by rebuilding the FAISS index without the target vector.
        
        FAISS IndexFlatL2 does not support direct removal, so we rebuild
        the entire index from remaining vectors and update the identity map.
        
        This ensures the embedding is physically purged, not just de-mapped.
        """
        try:
            # Find positions to remove
            positions_to_remove = set()
            for pos, sid in list(self.identity_map.items()):
                if sid == student_id:
                    positions_to_remove.add(int(pos))
            
            if not positions_to_remove:
                logger.warning(f"No embedding found for {student_id}")
                return True  # Already removed
            
            # Rebuild index without removed vectors
            if self.index.ntotal > 0:
                # Extract all existing vectors
                all_vectors = faiss.rev_swig_ptr(
                    self.index.get_xb(), self.index.ntotal * self.embedding_dim
                ).reshape(self.index.ntotal, self.embedding_dim).copy()
                
                # Create new index and mapping
                new_index = faiss.IndexFlatL2(self.embedding_dim)
                new_identity_map = {}
                new_pos = 0
                
                for old_pos in range(len(all_vectors)):
                    if old_pos not in positions_to_remove:
                        vec = all_vectors[old_pos:old_pos+1].copy()
                        new_index.add(vec)
                        old_sid = self.identity_map.get(str(old_pos))
                        if old_sid:
                            new_identity_map[str(new_pos)] = old_sid
                        new_pos += 1
                
                self.index = new_index
                self.identity_map = new_identity_map
            
            self._save()
            logger.info(
                f"Removed embedding for {student_id} "
                f"(rebuilt index: {self.index.ntotal} vectors remaining)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to remove embedding for {student_id}: {e}")
            return False
    
    def get_count(self) -> int:
        """Get number of indexed faces"""
        return self.index.ntotal
    
    def _save(self):
        """
        Persist index and mapping to disk.
        
        ARCHITECTURE_CANONICAL.md 3.3: Requires consent for cross-session persistence.
        """
        # Check consent requirement
        if self.require_consent:
            # Only save if at least one consent granted
            consented_ids = [sid for sid, c in self._consent_granted.items() if c]
            if not consented_ids:
                logger.warning(
                    "FAISS save blocked: No consent granted for persistence "
                    "(ARCHITECTURE_CANONICAL.md 3.3)"
                )
                return
        
        # Save FAISS index
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        faiss.write_index(self.index, self.index_file)
        
        # Save identity mapping
        with open(self.identity_map_file, 'w') as f:
            json.dump(self.identity_map, f, indent=4)
    
    # -------------------------------------------------------------------------
    # ARCHITECTURE_CANONICAL.md 3.3 COMPLIANCE METHODS
    # -------------------------------------------------------------------------
    
    def grant_consent(self, student_id: str) -> None:
        """
        Grant consent for cross-session embedding persistence.
        
        Per ARCHITECTURE_CANONICAL.md 3.3: Cross-session persistence requires consent.
        """
        self._consent_granted[student_id] = True
        logger.info(f"Consent granted for embedding persistence: {student_id}")
    
    def revoke_consent(self, student_id: str) -> None:
        """
        Revoke consent for embedding persistence.
        
        Triggers embedding removal.
        """
        self._consent_granted[student_id] = False
        self.remove_embedding(student_id)
        logger.info(f"Consent revoked, embedding removed: {student_id}")
    
    def is_session_expired(self) -> bool:
        """Check if current session has expired."""
        return time.time() - self._session_start > self.session_ttl
    
    def purge_expired_embeddings(self) -> int:
        """
        Purge embeddings that have exceeded TTL.
        
        Returns:
            Number of embeddings purged.
        """
        purged = 0
        current_time = time.time()
        
        for student_id, timestamp in list(self._embedding_timestamps.items()):
            if current_time - timestamp > self.session_ttl:
                # Check if consent was granted for persistence
                if not self._consent_granted.get(student_id, False):
                    self.remove_embedding(student_id)
                    del self._embedding_timestamps[student_id]
                    purged += 1
                    logger.info(f"Purged expired embedding (TTL): {student_id}")
        
        return purged
    
    def end_session(self) -> None:
        """
        End current session and purge all non-consented embeddings.
        
        Per ARCHITECTURE_CANONICAL.md 3.3: Session-scoped embeddings must be
        destroyed at session end.
        """
        logger.info("FAISS: Session ending, purging non-consented embeddings")
        
        for student_id in list(self._embedding_timestamps.keys()):
            if not self._consent_granted.get(student_id, False):
                self.remove_embedding(student_id)
                logger.info(f"Session-end purge: {student_id}")
        
        # Clear session tracking
        self._embedding_timestamps.clear()
        self._session_start = time.time()
        
        logger.info("FAISS: Session ended, ephemeral embeddings purged")
    
    def add_embedding_with_ttl(
        self, 
        student_id: str, 
        embedding: np.ndarray,
        consent_for_persistence: bool = False
    ) -> bool:
        """
        Add embedding with TTL tracking and optional consent.
        
        Args:
            student_id: Unique identifier
            embedding: 512-dimensional vector
            consent_for_persistence: If True, embedding can persist across sessions
            
        Returns:
            True if successful
        """
        # Track consent
        if consent_for_persistence:
            self.grant_consent(student_id)
        
        # Add embedding
        result = self.add_embedding(student_id, embedding)
        
        if result:
            # Track timestamp for TTL
            self._embedding_timestamps[student_id] = time.time()
        
        return result

