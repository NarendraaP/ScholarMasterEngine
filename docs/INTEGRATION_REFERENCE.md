# ScholarMaster System Integration Reference
**Version**: 1.0  
**Last Updated**: January 26, 2026  
**Purpose**: Quick reference for integration points and system architecture

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCHOLARMASTER UNIFIED SYSTEM                  │
├─────────────────────────────────────────────────────────────────┤
│  main_unified.py - Central Orchestrator (722 lines)             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   SENSING    │  │    LOGIC     │  │  INFERENCE   │          │
│  │             │  │              │  │              │          │
│  │ • Face Rec  │→ │ • Context    │→ │ • Analytics  │          │
│  │ • Audio     │  │ • Schedule   │  │ • Safety     │          │
│  │ • Pose      │  │ • Compliance │  │ • Engagement │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         ↓                 ↓                  ↓                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │           PERSISTENCE & AUDIT LAYER               │          │
│  │  • Attendance Logging  • Blockchain Audit         │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Integration Map

### Core Modules (`modules_legacy/`)

| Module | Class | Key Methods | Integration Point | Status |
|--------|-------|-------------|-------------------|--------|
| `face_registry.py` | FaceRegistry | `search_face()` | Line 334, video_thread | ✅ Active |
| `context_manager.py` | ContextEngine | `check_compliance()` | Line 365, video_thread | ✅ Active |
| `attendance_logger.py` | AttendanceManager | `mark_present()` | Line 403, video_thread | ✅ Active |
| `safety_rules.py` | SafetyEngine | `detect_violence()`, `detect_sleeping()` | Line 452-461, video_thread | ✅ Active |
| `analytics.py` | AnalyticsEngine | `compute_engagement()` | Line 432, video_thread | ✅ Active |
| `audio_sentinel.py` | AudioSentinel | `listen()` | Line 447, audio_thread | ✅ Active |
| `scheduler.py` | AutoScheduler | `get_current_subject()` | Line 355, video_thread | ✅ Active |

---

## Integration Flow (main_unified.py)

### Thread Architecture

```python
ScholarMasterUnified (main_unified.py)
│
├── __init__ (Lines 205-257)
│   ├── Initialize FaceRegistry
│   ├── Initialize AnalyticsEngine
│   ├── Initialize AudioSentinel
│   ├── Initialize AutoScheduler
│   ├── Initialize ContextEngine
│   ├── Initialize AttendanceManager      # Phase 1
│   ├── Initialize SafetyEngine           # Phase 3
│   ├── Initialize SimplifiedAuditLog     # Phase 4
│   └── Initialize PowerMonitor
│
├── video_thread() (Lines 304-490)
│   ├── YOLOv8 Pose Init (Line 311-318)
│   ├── Face Detection (Line 331)
│   ├── Face Recognition (Line 334)        # search_face()
│   ├── Context Check (Line 365)           # check_compliance()
│   ├── Attendance Log (Line 403)          # mark_present()
│   ├── Audit Trail (Line 420)             # append_event()
│   ├── Engagement (Line 432)              # compute_engagement()
│   └── Safety Detection (Line 452-461)    # detect_*()
│
├── audio_thread() (Lines 447-492)
├── compliance_thread() (Lines 498-536)
├── power_thread() (Lines 542-556)
└── dashboard_thread() (Lines 562-603)
```

---

## Critical Integration Points

### 1. Face Recognition Pipeline
**Location**: `video_thread()` lines 329-356  
**Trigger**: Every video frame (30 FPS)  
**Dependencies**: 
- `FaceRegistry.search_face()` → FAISS index lookup
- Returns: `(found, match_id)` tuple

### 2. Context Compliance Check
**Location**: `video_thread()` lines 362-383  
**Trigger**: After successful face recognition  
**Dependencies**:
- `ContextEngine.check_compliance(student_id, zone, day, time)`
- Returns: `(is_compliant, message, expected_data)` tuple
- Updates: `self.compliance_status` (shared state)

### 3. Attendance Logging
**Location**: `video_thread()` lines 384-414  
**Trigger**: After compliance check  
**Dependencies**:
- `AttendanceManager.mark_present(student_id, context_data, user_role)`
- `AutoScheduler.get_current_subject(day, time)` for context
- Requires: RBAC bypass (uses `user_role='Admin'`)

### 4. Audit Trail
**Location**: `video_thread()` lines 415-442  
**Trigger**: After successful attendance logging  
**Dependencies**:
- Creates `AttendanceEvent` dataclass
- `SimplifiedAuditLog.append_event()` → Merkle tree
- Auto-builds Merkle root every 100 events

### 5. Safety Detection
**Location**: `video_thread()` lines 434-469  
**Trigger**: Every frame (parallel to face recognition)  
**Dependencies**:
- YOLOv8 Pose model (`yolov8n-pose.pt`)
- `SafetyEngine.detect_violence(keypoints_list)`
- `SafetyEngine.detect_sleeping(keypoints_list)`

---

## Data Flow Diagram

```
┌──────────────┐
│ Video Frame  │
└──────┬───────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌─────────────┐          ┌──────────────┐
│ InsightFace │          │ YOLOv8 Pose  │
│ (Face Rec)  │          │ (Keypoints)  │
└──────┬──────┘          └──────┬───────┘
       │                        │
       ▼                        ▼
 student_id              keypoints_list
       │                        │
       ├────────────────────────┤
       │                        │
       ▼                        ▼
┌─────────────┐          ┌──────────────┐
│ Context     │          │ Safety       │
│ Compliance  │          │ Detection    │
└──────┬──────┘          └──────────────┘
       │
       ▼
┌─────────────┐
│ Attendance  │
│ Logger      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Audit Trail │
│ (Merkle)    │
└─────────────┘
```

---

## Shared State Variables

### Thread-Safe Variables (Protected by `self.lock`)

```python
self.current_student_id: str          # Last recognized student
self.current_confidence: float        # Recognition confidence
self.current_engagement: float        # Engagement score (0-1)
self.current_audio_db: float          # Audio level (decibels)
self.compliance_status: str           # "COMPLIANT" | "VIOLATION" | "INITIALIZING"
self.video_fps: float                 # Real-time FPS
```

### Metrics (No Lock - Atomic Updates)

```python
self.total_events: int                # Total audit events
self.known_correct: int               # Correctly identified known faces
self.unknown_rejected: int            # Successfully rejected unknowns
self.total_known_probes: int          # Total known face attempts
self.total_unknown_probes: int        # Total unknown face attempts
```

---

## Configuration Points

### Module Initialization Locations

```python
# main_unified.py __init__ (Lines 233-252)
line 234: self.face_registry = FaceRegistry()
line 237: self.analytics = AnalyticsEngine()
line 240: self.audio_sentinel = AudioSentinel()
line 243: self.scheduler = AutoScheduler()
line 246: self.context_engine = ContextEngine()
line 249: self.attendance_logger = AttendanceManager()
line 252: self.safety_engine = SafetyEngine()
line 255: self.audit_log = SimplifiedAuditLog()
line 258: self.power_monitor = PowerMonitor()
```

### External Dependencies

```python
# Required ML Models
- InsightFace: buffalo_l (auto-download)
- YOLOv8: yolov8n-pose.pt (auto-download)

# Required Data Files
- data/students.json          # Student registry
- data/timetable.csv         # Schedule data
- data/attendance.csv        # Attendance log (auto-created)
- data/zones_config.json     # Zone definitions (optional)
```

---

## Modification Guidelines

### To Add New Integration Point:

1. **Import module** (top of file, ~line 34-40)
2. **Initialize in __init__** (~line 233-258)
3. **Call in appropriate thread**:
   - Face-related: `video_thread()` (line 304+)
   - Audio-related: `audio_thread()` (line 447+)
   - Background: Create new thread method
4. **Update shared state** with `self.lock`
5. **Add error handling** (`try/except` wrapper)

### To Modify Existing Flow:

1. **Locate thread** (see Thread Architecture above)
2. **Find integration line** (see Integration Points)
3. **Preserve error handling** (don't crash threads)
4. **Update this reference document**

---

## Error Handling Pattern

All integration points follow this pattern:

```python
try:
    # Integration logic
    result = self.module.method(args)
    
    # Update shared state
    with self.lock:
        self.shared_var = result
    
    # Log success
    print(f"✅ [MODULE] Success message")
    
except Exception as err:
    # Don't crash thread
    print(f"⚠️ [MODULE] Error: {err}")
```

**Critical**: Never let module failures crash main threads

---

## Logging Conventions

```python
# Module prefixes (for grep/log filtering)
[VIDEO]        # Face recognition thread
[AUDIO]        # Audio monitoring thread
[COMPLIANCE]   # Context compliance thread
[ATTENDANCE]   # Attendance logging
[SAFETY]       # Safety detection
[AUDIT]        # Blockchain audit
[POWER]        # Power monitoring
[DASHBOARD]    # Dashboard updates
[INIT]         # System initialization
```

---

## Testing Entry Points

### Unit Testing (Per Module)
```bash
python -m pytest tests/test_face_registry.py
python -m pytest tests/test_context_manager.py
python -m pytest tests/test_attendance_logger.py
```

### Integration Testing
```bash
python main_unified.py  # Full system
```

### Verification Scripts
```bash
python utils/verify_integration.py  # Check method calls
```

---

## Performance Benchmarks

| Operation | Latency | Thread | Bottleneck Risk |
|-----------|---------|--------|-----------------|
| Face Detection | 18ms | video_thread | Low |
| Face Recognition | 0.76ms | video_thread | Low (FAISS) |
| Pose Detection | 25ms | video_thread | Medium |
| Compliance Check | <1ms | video_thread | Low |
| Attendance Log | <5ms | video_thread | Low |
| Audio Analysis | 145ms | audio_thread | Medium |

**Target**: 30 FPS video processing (33ms frame budget)  
**Current**: ~31 FPS (within spec)

---

## Quick Reference: Where to Find Things

| Need to... | File | Lines |
|------------|------|-------|
| Add new module | `main_unified.py` | 34-40 (import), 233-258 (init) |
| Modify face recognition flow | `main_unified.py` | 329-356 |
| Change compliance logic | `modules_legacy/context_manager.py` | 121-139 |
| Update attendance rules | `modules_legacy/attendance_logger.py` | 45-115 |
| Adjust safety detection | `modules_legacy/safety_rules.py` | 76-148 |
| Modify audit trail | `main_unified.py` | 74-147 (SimplifiedAuditLog) |

---

## Version History

- **v1.0** (Jan 26, 2026): Initial integrated system
  - Face recognition pipeline
  - Context compliance checking
  - Attendance logging
  - Safety detection (violence/sleep)
  - Blockchain audit trail

---

**Note**: This is a living document. Update after major architectural changes.  
**Contact**: Narendra P (@NarendraaP) for integration questions.
