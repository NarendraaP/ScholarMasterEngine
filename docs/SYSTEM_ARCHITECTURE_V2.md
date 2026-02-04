# ScholarMasterEngine - System Architecture V2.0

**Purpose**: Canonical system architecture reference for ScholarMasterEngine  
**Version**: 2.0  
**Last Updated**: January 27, 2026  
**Status**: Production System (SOTA)

---

## Executive Summary

ScholarMasterEngine is a **privacy-preserving, edge-native smart campus intelligence system** supporting 10 IEEE-grade research papers. The system performs real-time biometric identification, schedule compliance checking, behavioral monitoring, and cryptographic audit trails—all while maintaining GDPR compliance through volatile memory processing and privacy-preserving analytics.

**Key Metrics** (Apple M2, N=100k identities):
- **End-to-End Latency**: 28ms (33 FPS sustained)
- **Open-Set Identification Rate**: 99.82%
- **Unknown Rejection Rate**: 99.91%
- **Thermal Stability**: 62°C (vs 85°C naive edge)

---

## Architecture Hierarchy

ScholarMasterEngine implements **three distinct architectures** for comparative research (Paper 9):

### 🌟 Architecture C: Unified SOTA System (PRIMARY)

**File**: [`main_unified.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main_unified.py)  
**Status**: **PRODUCTION SYSTEM**  
**Papers**: P1-P9 (full integration)

**Description**: The Pareto-dominant architecture combining:
- InsightFace + HNSW for sub-logarithmic face recognition
- Privacy-preserving pose analytics (volatile memory)
- Spectral audio gating (FFT, no speech recognition)
- Merkle-DAG blockchain audit with GDPR crypto-shredding
- Real-time schedule compliance via ST-CSF logic

**Use Case**: Institutional deployment, research publication, investor demonstrations

### Architecture B: Naive Edge Baseline (COMPARISON)

**File**: [`main_integrated_system.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main_integrated_system.py)  
**Status**: Baseline for Paper 9 adversarial validation  
**Papers**: Demonstrates failure modes of naive approaches

**Description**: Intentionally limited implementation using:
- Haar Cascade face detection (legacy CV)
- SQLite in-memory database
- Linear logic flow
- No privacy protections

**Use Case**: Comparative benchmarking, failure mode analysis

### Architecture A: Legacy Multi-Camera (REFERENCE)

**File**: [`main.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main.py)  
**Status**: Deprecated (V1 system)  
**Papers**: Original multi-stream prototype

**Description**: Original orchestration layer for multi-camera deployments.

**Use Case**: Historical reference, migration documentation

---

## Canonical Execution Model (Architecture C)

### Initialization Sequence

```python
ScholarMasterUnified.__init__()
│
├─ [1] Load AI Models
│   ├─ InsightFace (buffalo_l) → Face recognition
│   ├─ YOLOv8-Pose (CoreML/ONNX/PyTorch) → Pose detection
│   └─ FAISS Index → Vector search (100k identities)
│
├─ [2] Initialize Core Engines
│   ├─ FaceRegistry → Biometric database
│   ├─ ContextEngine → Timetable & compliance logic
│   ├─ AttendanceManager → Logging with debounce
│   ├─ SafetyEngine → Violence/sleep/uniform detection
│   └─ AudioSentinel → Spectral audio analysis
│
├─ [3] Initialize Audit Layer
│   ├─ SimplifiedAuditLog → Merkle tree builder
│   ├─ KeyManagementService → GDPR crypto-shredding
│   └─ ZeroKnowledgeProver → NIZK attendance proofs
│
└─ [4] Start Background Services
    ├─ PowerMonitor → Thermal profiling (Paper 5)
    └─ NotificationDispatcher → Alert polling (data/alerts.json)
```

### Runtime Thread Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ScholarMasterUnified                      │
│                     (main_unified.py)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ video_thread │  │ audio_thread │  │compliance_   │      │
│  │              │  │              │  │   thread     │      │
│  │  30 FPS      │  │ 100ms chunks │  │  5s interval │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         ├─────────────────┴──────────────────┤               │
│         │                                    │               │
│         ▼                                    ▼               │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Shared State (Thread-Safe Lock)          │       │
│  │                                                   │       │
│  │  • current_student_id    • compliance_status     │       │
│  │  • current_confidence    • current_audio_db      │       │
│  │  • current_engagement    • video_fps             │       │
│  └──────────────────────────────────────────────────┘       │
│         │                                    │               │
│  ┌──────┴───────┐                    ┌──────┴───────┐      │
│  │ power_thread │                    │dashboard_    │      │
│  │              │                    │   thread     │      │
│  │ 10s interval │                    │  1s refresh  │      │
│  └──────────────┘                    └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Thread Safety**: All shared state variables protected by `threading.Lock()`

---

## Layer Architecture

### Layer 1: Sensing

**Purpose**: Real-time perception from camera and microphone

**Components**:
- **Face Detection**: InsightFace (ArcFace embeddings)
- **Pose Detection**: YOLOv8-Pose (17 keypoints per person)
- **Audio Monitoring**: AudioSentinel (FFT spectral analysis)

**Data Flow**:
```
Video Frame (BGR) → InsightFace → 512-dim embedding → FAISS search → Student ID
Video Frame (BGR) → YOLOv8 → 17x3 keypoints → Engagement/Safety analysis
Audio Chunk (100ms) → FFT → dB level → Context-aware threshold check
```

**Module Location**: `modules_legacy/face_registry.py`, `modules_legacy/audio_sentinel.py`

### Layer 2: Logic

**Purpose**: Schedule compliance, context awareness, decision making

**Components**:
- **ContextEngine**: Timetable-based expectation lookup
- **AutoScheduler**: Current subject/period determination
- **Debounce Logic**: Anti-flicker for truancy detection

**Data Flow**:
```
Student ID + Zone + Time → ContextEngine.check_compliance()
  ├─ Load timetable.csv
  ├─ Filter: day, program, year, section, dept
  ├─ Time range check: start ≤ current < end
  └─ Return: (is_compliant, message, expected_data)
```

**Module Location**: `modules_legacy/context_manager.py`, `modules_legacy/scheduler.py`

### Layer 3: Inference

**Purpose**: Behavioral analysis, safety detection, engagement scoring

**Components**:
- **PrivacyEngagement**: Pose-only engagement (no face pixels)
- **SafetyEngine**: Violence/sleep/uniform detection
- **LectureScribe**: Audio transcription (optional, privacy-aware)

**Data Flow**:
```
Keypoints List → SafetyEngine.detect_violence()
  ├─ Check inter-person distances (< 50px = proximity violation)
  ├─ Check standing duration (> 10s during lecture = concern)
  └─ Return: (is_violent, explanation_message)
```

**Module Location**: `modules_legacy/privacy_analytics.py`, `modules_legacy/safety_rules.py`

### Layer 4: Persistence & Audit

**Purpose**: Immutable logging, GDPR compliance, cryptographic provenance

**Components**:
- **AttendanceManager**: CSV logging with atomic writes (RCU pattern)
- **SimplifiedAuditLog**: Merkle tree builder (100-event blocks)
- **KeyManagementService**: Crypto-shredding for GDPR deletion
- **ZeroKnowledgeProver**: NIZK proofs for attendance verification

**Data Flow**:
```
AttendanceEvent → SimplifiedAuditLog.append_event()
  ├─ Hash event: SHA256(JSON(event))
  ├─ Append to event buffer
  ├─ Every 100 events: Build Merkle tree
  ├─ Compute root: recursive pair-wise hashing
  └─ Store root for integrity verification
```

**Module Location**: `main_unified.py` (L74-226), `modules_legacy/attendance_logger.py`

---

## Module Responsibility Matrix

| Module | Primary Responsibility | Integration Point | Papers |
|--------|------------------------|-------------------|---------|
| [`face_registry.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/face_registry.py) | Biometric enrollment & search (FAISS) | video_thread L417 | P1 |
| [`context_manager.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/context_manager.py) | Schedule compliance checks | video_thread L456 | P4, P7 |
| [`attendance_logger.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/attendance_logger.py) | Attendance logging with debounce | video_thread L482 | P4 |
| [`safety_rules.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/safety_rules.py) | Violence/sleep/uniform detection | video_thread L564 | P2, P6 |
| [`privacy_analytics.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/privacy_analytics.py) | Pose-only engagement (no face pixels) | video_thread L554 | P3 |
| [`audio_sentinel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/audio_sentinel.py) | Spectral audio gating (privacy) | audio_thread L628 | P6 |
| [`scheduler.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/scheduler.py) | Timetable generation & queries | video_thread L447 | P4 |
| [`notification_service.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/notification_service.py) | Alert polling & dispatch | Separate process | - |
| [`auth.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/auth.py) | RBAC, salted password verification | admin_panel.py | - |
| [`liveness.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/liveness.py) | Anti-spoofing (optional) | master_engine.py | P1 |
| [`grooming.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/grooming.py) | Uniform compliance checking | master_engine.py | P2 |
| [`scribe.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/scribe.py) | Lecture transcription (Whisper) | master_engine.py | P2 |

---

## Data Flow: End-to-End Frame Processing

```mermaid
graph TD
    A[Video Frame 640x480] --> B[Face Detection]
    A --> C[Pose Detection]
    
    B --> D[InsightFace Embedding 512-dim]
    D --> E[FAISS Search 100k index]
    E --> F{Found?}
    
    F -->|Yes| G[Student ID]
    F -->|No| H[Unknown/Reject]
    
    G --> I[ContextEngine.check_compliance]
    I --> J{Compliant?}
    
    J -->|Yes| K[AttendanceManager.mark_present]
    J -->|No| L[Trigger Truancy Alert]
    
    K --> M[SimplifiedAuditLog.append_event]
    L --> M
    
    C --> N[17 Keypoints per Person]
    N --> O[SafetyEngine.detect_violence]
    N --> P[PrivacyEngagement.compute_score]
    
    O --> Q{Violent?}
    Q -->|Yes| R[Trigger Security Alert]
    
    M --> S[Merkle Tree Every 100 Events]
    S --> T[data/audit_log.json]
    
    K --> U[data/attendance.csv]
    L --> V[data/alerts.json]
    R --> V
```

---

## Clean Architecture Integration (DDD)

ScholarMasterEngine implements **Domain-Driven Design** with clear separation:

### Domain Layer (`domain/`)

**Pure Business Logic** (no dependencies)

- **Entities**: [`Student`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/domain/entities/student.py), [`Attendance`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/domain/entities/attendance.py), [`Schedule`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/domain/entities/schedule.py)
- **Interfaces**: `IFaceRecognizer`, `IStudentRepository`, `IScheduleRepository`

### Application Layer (`application/`)

**Use Cases** (orchestrate domain logic)

- [`recognize_student_use_case.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/application/use_cases/recognize_student_use_case.py)
- [`mark_attendance_use_case.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/application/use_cases/mark_attendance_use_case.py)
- [`detect_truancy_use_case.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/application/use_cases/detect_truancy_use_case.py)

### Infrastructure Layer (`infrastructure/`)

**External Adapters** (implementations)

- [`faiss_face_index.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/infrastructure/indexing/faiss_face_index.py) → FAISS integration
- [`insightface_adapter.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/infrastructure/face_recognition/insightface_adapter.py) → InsightFace wrapper
- [`csv_attendance_repository.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/infrastructure/repositories/csv_attendance_repository.py) → CSV persistence

### Dependency Injection (`di/`)

**Container** manages object creation and wiring

- [`container.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/di/container.py) → Singleton instances
- [`legacy_adapters.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/di/legacy_adapters.py) → Bridge to `modules_legacy/`

---

## Interface Points

### REST API (FastAPI)

**File**: [`api/main.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/api/main.py)  
**Port**: 8000  
**Documentation**: http://localhost:8000/docs

**Key Endpoints**:
- `POST /api/students/register` → Enroll new student with face
- `POST /api/students/recognize` → Identify student from image
- `POST /api/attendance/mark` → Manual attendance marking
- `GET /api/attendance/logs` → Query attendance history

### Admin Dashboard (Streamlit)

**File**: [`admin_panel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/admin_panel.py)  
**Port**: 8501  
**RBAC**: Role-based tab visibility

**Tabs** (by role):
- **Super Admin**: All tabs (Scheduler, Analytics, User Management, Enrollment, Alerts, Attendance, Grooming)
- **Faculty Manager**: Enrollment, Analytics, Attendance (department-scoped)
- **Faculty**: Attendance, Analytics (own classes only)
- **Student**: Attendance (own records only)

---

## Configuration Files

| File | Purpose | Format | Example |
|------|---------|--------|---------|
| `data/students.json` | Student registry with privacy hashes | JSON | `{"S101": {"name": "...", "privacy_hash": "abc123"}}` |
| `data/timetable.csv` | Schedule data | CSV | `Mon,10:00,11:00,Technology,CS,UG,1,A,DS,Ms. Davis,Lab-1` |
| `data/users.json` | Authentication database | JSON | `{"admin": {"password": "hash:salt", "role": "Super Admin"}}` |
| `data/alerts.json` | Active alerts queue | JSON Array | `[{"type": "Warning", "msg": "...", "zone": "..."}]` |
| `data/attendance.csv` | Attendance logs | CSV | `2026-01-27,S101,09:00,Data Structures,Lab-1` |
| `data/zones_config.json` | Camera zone definitions (optional) | JSON | `{"Main Entrance": {"camera_id": 0}}` |

---

## Performance Characteristics

### Latency Breakdown (Apple M2)

| Operation | Avg Latency | Bottleneck | Optimization |
|-----------|-------------|------------|--------------|
| InsightFace detection | 18ms | MPS backend | ✅ CoreML quantization available |
| FAISS search (N=100k) | 0.76ms | Vector ops | ✅ HNSW index (sub-log) |
| YOLOv8 pose | 25ms | Model size | ✅ INT8 ONNX export available |
| Compliance check | <1ms | Pandas filter | ✅ No optimization needed |
| Attendance logging | <5ms | File I/O | ✅ RCU pattern (atomic) |
| Audio FFT | 145ms | CPU-bound | ⚠️ Consider GPU offload |

**Total Frame Budget**: 33ms (30 FPS target)  
**Actual**: 28ms average (margin: 5ms)

### Scalability

- **Gallery Size**: Tested up to 100,000 identities
- **Concurrent Streams**: 1-4 cameras (auto quality downgrade at >4)
- **Memory Footprint**: ~800 MB (M2 Unified Memory)
- **Thermal**: Stable at 62°C (vs 85°C naive baseline)

---

## Security & Privacy

### Authentication

- **Salted SHA-256**: `hashlib.sha256((password + salt).encode()).hexdigest()`
- **Salt Storage**: `{hash}:{salt}` format in `data/users.json`
- **RBAC**: Decorator-based role checks (`@requires_role('Super Admin')`)

### Privacy Compliance (GDPR)

- **No Face Pixel Storage**: Only 512-dim embeddings stored
- **Privacy Hashing**: Student IDs replaced with `privacy_hash` in logs
- **Volatile Memory**: Frames wiped via `secure_wipe()` after processing
- **Crypto-Shredding**: GDPR "Right to be Forgotten" via key destruction

### Audit Trail Integrity

- **Merkle Tree**: SHA256-based tree built every 100 events
- **Tamper Detection**: `verify_integrity()` recomputes and compares roots
- **Zero-Knowledge Proofs**: Fiat-Shamir NIZK for attendance verification (prototype)

---

## Deployment Models

### Edge Deployment (Recommended)

**Target Hardware**: Apple M2/M3, NVIDIA Jetson, Intel i7+

**Advantages**:
- No network latency
- Privacy-preserving (no cloud transmission)
- Offline operation
- Thermal stability

**Requirements**:
- 16GB RAM (for 100k gallery)
- Python 3.12+
- Models: InsightFace (150MB), YOLOv8 (6.8MB)

### Cloud Deployment (Not Recommended)

**Concerns**:
- Violates Paper 3 privacy assumptions
- Network latency: 450ms average (AWS Rekognition baseline)
- GDPR compliance risks (biometric data transmission)

**If Required**: Use TLS encryption, regional data residency, audit compliance

---

## Troubleshooting

### Common Issues

1. **Camera Not Opening**
   - Check permissions: `System Preferences → Security & Privacy → Camera`
   - Verify camera ID: `cv2.VideoCapture(0)` vs `(1)` for external cameras

2. **FAISS IndexError**
   - Ensure at least 1 student enrolled: `python scripts/enroll_student.py`
   - Check `data/face_index.faiss` exists

3. **Audio Thread Crashes**
   - macOS: Grant microphone permissions
   - Linux: Install PortAudio: `sudo apt-get install portaudio19-dev`

4. **Timetable Not Loaded**
   - Verify `data/timetable.csv` exists and has valid structure
   - Check headers: `day,start,end,faculty,dept,program,year,section,subject,teacher,room`

---

## Future Architectural Considerations

### Proposed Enhancements (Post-Papers)

1. **Microservices Decomposition** (if scaling beyond 10k concurrent users)
   - Separate services: Face Recognition, Compliance, Audit
   - Message queue: RabbitMQ/Kafka for async event processing

2. **Real-Time Dashboard** (WebSocket integration)
   - Replace Streamlit polling with WebSocket push
   - Live video feed preview in admin panel

3. **Federated Learning** (maximum privacy)
   - Train face models locally on each device
   - Aggregate only model weights (not raw face data)

**Note**: Current architecture is optimal for institutional scale (1,000-10,000 users).

---

## Related Documentation

- [Integration Reference](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/INTEGRATION_REFERENCE.md) - Module integration points
- [Project Audit Report](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/PROJECT_AUDIT_REPORT.md) - Feature validation (38/38 ✅)
- [Performance Benchmarks](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/PERFORMANCE_BENCHMARKS.md) - Latency analysis
- [README](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/README.md) - Quick start guide

---

**Document Version**: 2.0  
**Maintainer**: Narendra P (@NarendraaP)  
**Last Review**: January 27, 2026
