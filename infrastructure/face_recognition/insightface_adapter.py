"""
Infrastructure Layer - InsightFace Adapter

Implements IFaceRecognizer interface using InsightFace library.
"""
from typing import List
import numpy as np
from insightface.app import FaceAnalysis

from domain.interfaces import IFaceRecognizer, Face
from utils.logging_config import logger


class InsightFaceAdapter(IFaceRecognizer):
    """
    Adapter for InsightFace library.
    
    Wraps InsightFace to conform to our domain interface.
    This keeps the domain layer independent of the specific library.
    """
    
    def __init__(self, det_size=(640, 640)):
        """
        Initialize InsightFace.
        
        Args:
            det_size: Detection size tuple
            
        Raises:
            RuntimeError: If InsightFace fails to initialize
        """
        try:
            logger.info("Initializing InsightFace model...")
            self._app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self._app.prepare(ctx_id=0, det_size=det_size)
            logger.info("InsightFace initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize InsightFace: {e}")
            logger.error("Please ensure InsightFace models are downloaded")
            raise RuntimeError(f"InsightFace initialization failed: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Face]:
        """
        Detect all faces using InsightFace.
        
        Args:
            image: NumPy array in BGR format
            
        Returns:
            List of Face objects (empty if detection fails)
        """
        try:
            # Call InsightFace
            insight_faces = self._app.get(image)
            
            # Convert to our domain Face objects
            faces = []
            for insight_face in insight_faces:
                bbox = insight_face.bbox.astype(int)
                embedding = insight_face.embedding
                confidence = float(insight_face.det_score)
                
                face = Face(
                    bbox=tuple(bbox),
                    embedding=embedding,
                    confidence=confidence
                )
                faces.append(face)
            
            logger.debug(f"Detected {len(faces)} faces")
            return faces
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def extract_embedding(self, image: np.ndarray, bbox: tuple) -> np.ndarray:
        """
        Extract embedding from specific region.
        
        Note: InsightFace doesn't have a direct bbox->embedding method,
        so we crop and detect.
        
        Args:
            image: Full image
            bbox: Region of interest (x1, y1, x2, y2)
            
        Returns:
            512-dimensional embedding
        """
        x1, y1, x2, y2 = bbox
        cropped = image[y1:y2, x1:x2]
        
        faces = self.detect_faces(cropped)
        
        if len(faces) == 0:
            raise ValueError("No face found in the specified region")
        
        return faces[0].embedding
