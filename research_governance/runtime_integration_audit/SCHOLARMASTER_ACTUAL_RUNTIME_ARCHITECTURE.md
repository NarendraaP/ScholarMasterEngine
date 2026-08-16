# Canonical ScholarMaster Actual Runtime Architecture

## 1. Executable Runtime Data-Flow Pipeline

The production ScholarMaster Engine executes an asynchronous multi-threaded perception-to-decision pipeline defined in `main.py` (`ScholarMasterUnified.run()`, `process_video()`) and coordinated with canonical layer contracts in `core/canonical_layers.py`:

```
RAW SENSOR INPUT (Camera / Microphone)
  ↓
[L1 / L2 Physical & Sensor Acquisition] (core/canonical_layers.py: SensorAcquisition)
  ↓
[L1 Upstream Perception Gate] (core/perception_integrity/gate.py: PerceptionIntegrityGate.process_frame())
  ├─► [HALT] ──► Drop Frame / Fail-Closed Quarantine (main.py: line 677)
  ├─► [DEGRADE] ──► Anonymous Pose-Only Privacy Pipeline (main.py: lines 860-896)
  └─► [ACCEPT / DELEGATE] ──► Validated Perception Packet
        ↓
[L2 Biometric Identity Search] (modules_legacy/face_registry.py: FaceRegistry.search_face() via InsightFace + FAISS-HNSW)
  ↓
[L3 Context, Pose & Kinematic Tracking] (modules_legacy/privacy_analytics.py: PrivacyEngagement + YOLO-Pose)
  ↓
[L4 Spatio-Temporal Compliance Logic] (modules_legacy/st_csf.py: SpatiotemporalCSF.validate_event())
  ↓
[L5 Governance & Filter Gate] (core/canonical_layers.py: GovernanceFilter.compliance_check())
  ↓
[L5 Decision, Attendance & Audit Logging] (modules_legacy/attendance_logger.py + modules_legacy/audit_trail.py: Merkle Chain)
  ↓
[L3 Memory Wipe / Irreversible Boundary] (core/canonical_layers.py: EdgeAbstraction._destroy_frame() 33ms TTL)
```

## 2. Component Ownership and Call Sites

| Stage | Canonical Layer | Runtime Implementation Module | Function / Class | Call Site in `main.py` |
|:---:|:---:|:---|:---|:---:|
| **0** | Sensor Ingestion | `cv2.VideoCapture` + `sounddevice` | `SensorAcquisition` | `main.py:660, 668` |
| **1** | Perception Gate | `core.perception_integrity.gate` | `PerceptionIntegrityGate.process_frame()` | `main.py:671` |
| **2** | Identity Search | `modules_legacy.face_registry` | `FaceRegistry.search_face()` | `main.py:695` |
| **3** | Context Tracking | `modules_legacy.privacy_analytics` | `PrivacyEngagement.process_batch()` | `main.py:875` |
| **4** | Compliance Logic | `modules_legacy.st_csf` | `SpatiotemporalCSF.validate_event()` | `main.py:782` |
| **5** | Governance Filter| `core.canonical_layers` | `GovernanceFilter.compliance_check()` | `main.py:816` |
| **6** | Audit Ledger | `modules_legacy.audit_trail` | `AuditLog.append_event()` | `main.py:828` |
| **7** | Memory Wipe | `core.canonical_layers` | `EdgeAbstraction._destroy_frame()` | `main.py:911` |
