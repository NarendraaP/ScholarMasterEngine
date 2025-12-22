import cv2
import numpy as np
import torch
from insightface.app import FaceAnalysis

class FaceEngine:
    def __init__(self):
        """
        Initializes the Face Analysis app.
        Uses 'ArcFace r100' model implicitly via InsightFace default 'buffalo_l' or similar.
        """
        self.providers = ['CPUExecutionProvider']
        
        # Check for Hardware Acceleration
        if torch.backends.mps.is_available():
            print("✅ FaceEngine: Apple MPS Detected. (Note: InsightFace ONNX uses CPU/CoreML)")
            # ONNXRuntime for Mac often defaults to CPU unless CoreML provider is installed.
            # We stick to CPU for stability in this environment.
        elif torch.cuda.is_available():
            print("✅ FaceEngine: CUDA Detected. Switching to CUDAExecutionProvider.")
            self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            print("ℹ️ FaceEngine: Using CPU.")

        # Initialize InsightFace
        # 'buffalo_l' includes ArcFace r100 for recognition
        self.app = FaceAnalysis(name='buffalo_l', providers=self.providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def get_faces(self, frame):
        """
        Detects faces in the frame.
        Returns a list of Face objects.
        """
        return self.app.get(frame)

    def extract_vector(self, face):
        """
        Returns the 512-D embedding vector for a given Face object.
        This uses the ArcFace r100 model.
        """
        if face is None:
            return None
        return face.embedding
