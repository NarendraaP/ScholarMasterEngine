import cv2
import torch
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.context_manager import ContextEngine

class ScholarMasterEngine:
    def __init__(self):
        # Check if MPS is available (Apple Silicon)
        if torch.backends.mps.is_available():
            self.device = "mps"
            print("✅ Using Apple MPS (Metal Performance Shaders) for acceleration")
        else:
            self.device = "cpu"
            print("⚠️ MPS not available. Using CPU")
        
        # Initialize Context Engine
        self.context_engine = ContextEngine()
        print("✅ ContextEngine loaded")
        
        # Load YOLOv8-Pose
        self.pose_model = YOLO('yolov8n-pose.pt')
        # Move to device
        self.pose_model.to(self.device)
        print(f"✅ YOLOv8-Pose loaded on {self.device}")
        
        # Load InsightFace
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ InsightFace loaded")
    
    def process_frame(self, frame, current_zone):
        """
        Process a single frame:
        1. Detect faces with InsightFace
        2. Check truancy for each detected person
        3. Run YOLOv8 pose detection
        4. Annotate frame with results
        """
        annotated_frame = frame.copy()
        
        # 1. Face Detection
        faces = self.face_app.get(frame)
        
        # 2. Truancy Check for each face
        for face in faces:
            # Get bounding box
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Simulate student ID (for now, hardcoded as "S101")
            # In production, this would use face recognition to match against a database
            student_id = "S101"
            
            # Check compliance
            is_compliant, message = self.context_engine.check_compliance(
                student_id, 
                current_zone, 
                "Mon", 
                "10:00"
            )
            
            # Draw box and text based on compliance
            if is_compliant:
                color = (0, 255, 0)  # GREEN
                text = f"ID: {student_id} - {message}"
            else:
                color = (0, 0, 255)  # RED
                text = f"⚠️ TRUANCY ALERT - {message}"
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw text background
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(
                annotated_frame, 
                (x1, y1 - text_size[1] - 10), 
                (x1 + text_size[0], y1), 
                color, 
                -1
            )
            
            # Draw text
            cv2.putText(
                annotated_frame, 
                text, 
                (x1, y1 - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255, 255, 255), 
                2
            )
        
        # 3. YOLOv8 Pose Detection
        results = self.pose_model(frame, verbose=False)
        
        # Overlay pose skeleton on the annotated frame
        for result in results:
            if result.keypoints is not None:
                # Plot keypoints on the frame
                annotated_frame = result.plot(
                    img=annotated_frame,
                    boxes=False,  # Don't show boxes, only skeleton
                    conf=True
                )
        
        return annotated_frame

if __name__ == "__main__":
    # Quick test
    print("Initializing ScholarMasterEngine...")
    engine = ScholarMasterEngine()
    print("✅ Engine initialized successfully!")
