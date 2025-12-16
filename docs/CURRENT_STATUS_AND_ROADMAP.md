# Project Status & Roadmap: Scholar Master Engine

## 1. What is Built? (Current System Status)

### ✅ Core Infrastructure
- **Admin Panel (`admin_panel.py`)**:
  - **University Scheduler**: Implemented with `AutoScheduler` integration.
  - **RBAC (Role-Based Access Control)**: Implemented (Super Admin, Faculty Manager, Faculty, Student).
  - **Grooming Tab**: Added for Uniform Compliance settings.
- **Authentication (`modules/auth.py`)**:
  - **Salted Hashing**: Implemented (verified via `utils/hasher.py` usage).
- **Context Engine (`modules/context_manager.py`)**:
  - **Context Logic**: Implemented `ContextEngine` class for schedule-aware compliance checking.
- **Master Engine (`modules/master_engine.py`)**:
  - **Status**: **ACTIVE** (Running on Mac M2).
  - **Features**:
    - Face Recognition (InsightFace)
    - Safety Rules (Violence, Hand Raise, Sleeping)
    - Grooming Inspection (Uniform Check)
    - Audio Sentinel (Keyword Detection)

### 📊 Benchmarks
- **Hardware Acceleration (Paper 5)**:
  - CPU: ~1.09 FPS
  - M2 (MPS): ~2.77 FPS (**2.5x Speedup**)
- **Scalability (Paper 1)**:
  - FAISS vs Linear: **~28x Speedup** at 100k vectors.

---

## 2. The "New Strategy" (AI Layer Roadmap)

We are shifting focus to advanced AI features leveraging the Mac M2's capabilities.

### 🧠 AI Layer Features
1.  **Paper 2 (Emotion & Engagement):**
    -   **Feature:** "Lecture Scribe" (Offline Whisper).
    -   **Goal:** Transcribe lecture audio to extract keywords for context-aware engagement analysis.
2.  **Paper 3 (Behavioral Analytics):**
    -   **Feature:** "Non-Intrusive Attention".
    -   **Goal:** Detect "Sleeping" and "Phone Usage" events without flagging them as security threats (Behavioral vs Critical).
3.  **Paper 4 (Attendance Automation):**
    -   **Feature:** "Dual-Mode Attendance".
    -   **Goal:** Combine "Choke-Point ID" (Face Rec at door) with "Crowd Counting" (YOLO in room) for robust verification.
4.  **Paper 6 (Campus Security):**
    -   **Feature:** "Multi-Modal Violence Detection".
    -   **Goal:** Fuse Skeleton Heuristics (Pose) with Audio Analytics (Decibel/Spectral) for high-confidence alerts.

### 📱 Hardware Strategy
-   **Mobile Grid:** Utilize mobile phones as IP Cameras to create a flexible, low-cost surveillance grid.

---

## 3. Immediate Action Items (Next 3 Tasks)

To execute this strategy on the Mac M2, the immediate coding tasks are:

1.  **Implement Lecture Scribe (Paper 2):**
    -   Integrate `faster_whisper` or `openai-whisper` (Base model).
    -   Create `modules/scribe.py` to transcribe audio buffers and extract keywords.
2.  **Refine Behavior Detection (Paper 3):**
    -   Update `modules/safety_rules.py` to include `detect_phone_usage()` (using YOLO object detection for 'cell phone' class).
    -   Refine `detect_sleeping()` to be more robust.
3.  **Implement Dual-Mode Attendance (Paper 4):**
    -   Create `modules/crowd_counter.py` using YOLOv8.
    -   Update `master_engine.py` to cross-reference Face ID count with Crowd Count.
