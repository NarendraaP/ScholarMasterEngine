import os
import json
import numpy as np
import faiss
import cv2
from insightface.app import FaceAnalysis

class FaceRegistry:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.index_file = os.path.join(data_dir, "faiss_index.bin")
        self.identity_map_file = os.path.join(data_dir, "identity_map.json")
        self.students_file = os.path.join(data_dir, "students.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize FaceAnalysis
        # providers=['CPUExecutionProvider'] is safer for general compatibility if GPU isn't guaranteed
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        # Load or Create FAISS Index
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            # 512-D for InsightFace (ArcFace)
            self.index = faiss.IndexFlatL2(512)
            
        # Load Identity Map
        if os.path.exists(self.identity_map_file):
            with open(self.identity_map_file, "r") as f:
                self.identity_map = json.load(f)
        else:
            self.identity_map = {}

    def register_face(self, image_array, user_id, name, role, dept=None):
        """
        Detects face, extracts embedding, adds to FAISS, and updates records.
        Returns: (success: bool, message: str)
        """
        # Detect faces
        faces = self.app.get(image_array)
        
        if len(faces) == 0:
            return False, "No face detected in the image."
        
        if len(faces) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in the frame."
            
        # Get embedding
        embedding = faces[0].embedding
        
        # Normalize embedding (L2) - Important for Cosine Similarity / L2 distance consistency
        faiss.normalize_L2(embedding.reshape(1, -1))
        
        # De-Duplication Logic
        if self.index.ntotal > 0:
            # Search for nearest neighbor
            D, I = self.index.search(embedding.reshape(1, -1), 1)
            # D is squared L2 distance. For normalized vectors: d^2 = 2(1 - cosine_similarity)
            # Cosine Distance = 1 - cosine_similarity = d^2 / 2
            # Condition: Cosine Distance < 0.6 => d^2 / 2 < 0.6 => d^2 < 1.2
            
            if D[0][0] < 1.2:
                match_idx = str(I[0][0])
                match_info = self.identity_map.get(match_idx, {})
                match_name = match_info.get("name", "Unknown")
                match_uid = match_info.get("id", "Unknown")
                return False, f"Duplicate Face Detected! Matches User {match_name} (ID: {match_uid})"
        
        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Get the new index ID (it's sequential, so current size - 1)
        # Note: faiss.IndexFlatL2 adds sequentially. 
        # If we reload, ntotal tells us how many are there.
        # The ID of the newly added vector is self.index.ntotal - 1
        new_id = self.index.ntotal - 1
        
        # Update Identity Map
        user_data = {
            "id": user_id,
            "name": name,
            "role": role,
            "dept": dept
        }
        self.identity_map[str(new_id)] = user_data
        
        # Save Index and Map
        faiss.write_index(self.index, self.index_file)
        with open(self.identity_map_file, "w") as f:
            json.dump(self.identity_map, f, indent=4)
            
        # Update students.json if role is Student
        if role == "Student":
            self._update_students_file(user_id, name, dept)
            
        return True, f"Successfully registered {name} (ID: {user_id})"

    def _update_students_file(self, student_id, name, dept):
        """Updates the main students.json file with the new student if not exists."""
        if os.path.exists(self.students_file):
            with open(self.students_file, "r") as f:
                try:
                    students_data = json.load(f)
                except json.JSONDecodeError:
                    students_data = {}
        else:
            students_data = {}
            
        # Update or Create Student Record
        if student_id not in students_data:
            students_data[student_id] = {}
            
        # Update fields
        students_data[student_id]["name"] = name
        if dept:
            students_data[student_id]["dept"] = dept
            
        # Mark as Enrolled
        students_data[student_id]["status"] = "Enrolled"
        students_data[student_id]["registered"] = True # Keep for backward compatibility if needed
        
        with open(self.students_file, "w") as f:
            json.dump(students_data, f, indent=4)
