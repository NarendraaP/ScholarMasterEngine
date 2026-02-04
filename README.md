# ScholarMaster Engine

**Real-time, privacy-preserving intelligent campus monitoring system for educational institutions**

Version: 2.1.0 (Event-Driven Architecture)  
License: Proprietary  
Maintainer: Narendra P (@NarendraaP)

---

## What is ScholarMaster?

ScholarMaster is an edge-based campus monitoring system that combines biometric identification, timetable-driven compliance checking, privacy-preserving behavior analytics, and immutable audit logging into a single integrated platform. It solves the problem of **institution-scale intelligence** (100k+ identities) while maintaining **privacy-first** design (no image retention, only spectral audio features, volatile memory processing).

The system runs on edge hardware (M2 Mac, Raspberry Pi) and provides real-time detection of:
- **Truancy** (students in wrong locations based on timetable)
- **Noise violations** (context-aware: strict during lectures, relaxed during breaks)
- **Safety concerns** (prolonged sleep, violence detection)
- **Attendance** (automated, non-repudiable via blockchain-style audit)

All actions are logged to a tamper-evident Merkle tree, and access is controlled via role-based permissions (7 roles: Super Admin, Admin/HOD, Faculty, Class Teacher, Students, Security, Non-Teaching).

---

## System Architecture

ScholarMaster implements **Hybrid Onion Architecture with Event-Driven Orchestration**:

```
┌─────────────────────────────────────────┐
│  main_event_driven.py (Orchestrator)    │  ← Thin coordinator
└─────────────┬───────────────────────────┘
              │
              ├──→ APPLICATION LAYER (Use Cases)
              │    • DetectTruancyUseCase
              │    • MarkAttendanceUseCase
              │    • EventHandlers (pub/sub)
              │
              ├──→ DOMAIN LAYER (Pure Logic)
              │    • ComplianceRules (ST-CSF)
              │    • AlertRules (context-aware)
              │    • ZERO infrastructure deps
              │
              ├──→ INTERFACES (Contracts)
              │    • IFaceRecognizer
              │    • IAudioAnalyzer
              │    • IScheduleRepository
              │    • IAlertService
              │
              └──→ INFRASTRUCTURE (Adapters)
                   • FaceRecognizer (InsightFace+FAISS)
                   • AudioAnalyzer (Spectral FFT)
                   • Repositories (CSV, JSON)
                   • AuditLog (Merkle chain)
```

### Why This Structure?

1. **Testability**: Domain rules can be unit-tested without database, camera, or microphone
2. **Safety**: Business logic (compliance, alerts) is isolated from hardware failures
3. **Research Integrity**: Each layer maps to specific research papers (see below)
4. **Extensibility**: Swap implementations (e.g., PostgreSQL instead of JSON) without changing logic
5. **Dependency Inversion**: Application depends on interfaces, not concrete implementations

---

## Why There Are THREE Main Files

You'll notice three executable entry points:

### 1. `main.py` (formerly main_unified.py) ← **RECOMMENDED FOR PRODUCTION**
- **What**: The robust, fully integrated system engine
- **When**: Use for deployment (Paper 11) and defense
- **Why**: References all correct modules (P1-P11) verified in the audit
- **LOC**: 400+ lines
- **Status**: ✅ Freeze-Ready, Audited

### 2. `main_refactored.py` ← **CONSERVATIVE ALTERNATIVE**
- **What**: Onion Architecture without event bus
- **When**: Use if event-driven feels aggressive or hard to debug
- **Why**: Explicit Onion layers, but direct method calls (no pub/sub)
- **LOC**: 467 lines (44% smaller than original)
- **Pattern**: Dependency injection with use cases
- **Status**: ✅ Stable, less complex than event-driven

### 3. `main_unified_backup.py` ← **LEGACY / PAPER REPRODUCIBILITY**
- **What**: Original monolithic implementation
- **When**: Use ONLY for reproducing research paper experiments
- **Why**: Preserves exact logic from publications (Papers 1-10)
- **LOC**: 834 lines (original)
- **Pattern**: Monolithic, embedded business logic
- **Status**: ✅ Preserved for backward compatibility, NOT for new work

**Rule of Thumb**: Start with `main_event_driven.py`. If you need to debug event flow, temporarily switch to `main_refactored.py`. Never delete `main_unified_backup.py` (research integrity).

---

## System Roles & Permissions

ScholarMaster implements a 7-layer RBAC (Role-Based Access Control) hierarchy:

### Implemented Roles

| Role | Privileges | Data Scope | Typical Actions |
|------|-----------|------------|-----------------|
| **Super Admin** | System-wide control | All departments | Create users, modify timetables, audit access |
| **Admin / HOD** | Department management | Own department | Manage faculty, approve leave, department reports |
| **Faculty** | Teacher functions | Assigned subjects | Mark attendance, override alerts, view class analytics |
| **Class Teacher** | Class-specific | Own class (year+section) | Student welfare, attendance review, parent communication |
| **Students** | Self-service | Own records | View attendance, check timetable, appeal violations |
| **Security** | Safety monitoring | Campus-wide (alerts only) | Respond to safety alerts, view live violations |
| **Non-Teaching** | Limited ops | Facility-specific | Lab access logs, library monitoring |

### RBAC Boundaries (IMPORTANT)

- **Department Scoping**: Admins can ONLY see their own department's data (e.g., CS HOD cannot see Mech records)
- **Year/Section Scoping**: Class Teachers limited to specific cohort (e.g., "Year 3, Section A")
- **Timetable-Driven**: Permissions change dynamically (Faculty can edit attendance ONLY during their scheduled class)
- **Audit Trail**: All actions logged with role+timestamp (immutable, see `data/audit_log.db`)

### Why Timetable is Central

The timetable (`data/timetable.csv`) is NOT just a schedule—it's the **ground truth** for:
1. **Compliance**: Determines where students SHOULD be (ST-CSF spatiotemporal logic)
2. **Context**: Lecture mode (strict) vs break mode (relaxed) noise thresholds
3. **Attendance**: Marks are valid ONLY during scheduled class time
4. **Teacher Absence**: Alerts if no Faculty present in a scheduled session
5. **Authorization**: Faculty can modify attendance ONLY for their assigned subject

**DO NOT** manually edit timetable without understanding cascading effects on compliance, alerts, and attendance.

---

## Key System Features (Mapped to Code)

### 1. Timetable Auto-Generation
- **File**: `modules_legacy/scheduler.py` (AutoScheduler class)
- **Logic**: Backtracking solver for conflict-free scheduling
- **Output**: `data/timetable.csv` (7-column CSV: dept, program, year, section, day, start, end, subject, teacher, room)
- **Papers**: Not published (infrastructure only)

### 2. Attendance & Compliance
- **Files**: 
  - `core/application/use_cases/detect_truancy_use_case.py` (compliance logic)
  - `modules_legacy/attendance_logger.py` (logging, RBAC enforcement)
- **Logic**: 
  - If `current_location == expected_location` → Compliant, mark attendance
  - Else → Truancy violation, trigger alert
- **Debounce**: 30 frames (~30 seconds) to avoid false positives
- **Papers**: Paper 4 (ST-CSF), Paper 7 (ST reasoning), Paper 10 (integration)

### 3. Teacher Absence Alerts
- **File**: `modules_legacy/context_manager.py` (ContextEngine)
- **Logic**: If `timetable[time].teacher` is not detected via face recognition → Alert Admin/HOD
- **Escalation**: Security notified if absence >15 minutes
- **Papers**: Paper 4 (timetable integration)

### 4. Acoustic Safety Detection
- **File**: `core/infrastructure/sensing/audio/audio_analyzer.py`
- **Logic**: 
  - Spectral FFT analysis (NO speech recognition)
  - Context-aware thresholds: 40 dB lecture, 80 dB break
  - Scream detection: >85 dB → Critical alert to Dean
- **Privacy**: Only dB level, spectral centroid, zero-crossing rate stored (NOT audio samples)
- **Papers**: Paper 6 (acoustic anomaly), Paper 3 (privacy)

### 5. Participation Detection
- **File**: `modules_legacy/master_engine.py` (multi-modal fusion)
- **Logic**: `is_hand_raised AND is_loud` → Confirmed participation event
- **Sensors**: Pose keypoints (MediaPipe) + Audio dB
- **Papers**: Paper 2 (multi-modal fusion), Paper 3 (privacy pose)

### 6. Immutable Audit Trail
- **File**: `main_event_driven.py` (SimplifiedAuditLog class)
- **Logic**: 
  - Merkle tree: Each event hashes previous event
  - SHA-256 chaining prevents tampering
  - Stored in SQLite (`data/audit_log.db`)
- **Verification**: `verify_integrity()` recomputes root hash
- **Papers**: Paper 8 (blockchain audit)

---

## What NOT to Change Casually

### 🔒 Domain Rules (`core/domain/rules/`)
**DO NOT modify** without understanding paper claims:
- `ComplianceRules.is_in_expected_location()` → Paper 4 (ST-CSF)
- `AlertRules.get_noise_alert_severity()` → Paper 6 (context-aware thresholds)

These are **pure functions** with ZERO dependencies. Changing them invalidates research papers.

### 🔒 Event Semantics (`core/infrastructure/events/event_bus.py`)
**DO NOT rename** event types without updating all subscribers:
- `EventType.FACE_DETECTED` → Subscribed by DetectTruancyUseCase
- `EventType.VIOLATION_DETECTED` → Subscribed by EventHandlers
- `EventType.ALERT_TRIGGERED` → Subscribed by AuditLog

Breaking event flow breaks the entire system.

### 🔒 Privacy Barriers
**DO NOT add logging that exposes**:
- Raw image frames (only 512-dim embeddings allowed)
- Audio samples (only spectral features: dB, centroid, ZCR)
- Real student IDs in public logs (use privacy_hash)

Violations compromise GDPR compliance (Paper 3).

### 🔒 Adaptive Thresholds (`core/infrastructure/sensing/vision/face_recognizer.py`)
**DO NOT hardcode** face recognition threshold:
- Current: `τ(N) = 0.75 + 0.00001 × log(N)` (adaptive to gallery size)
- Changing breaks Paper 1 (open-set identification claims)

### ✅ Safe to Change
- UI/UX (dashboard colors, terminal formatting)
- File paths (via environment variables)
- Database schema (if you maintain interface contracts)
- Logging verbosity

---

## How This Supports the Research Papers

**The system came first, papers were extracted second** (not vice versa).

Each research paper focuses on ONE subsystem of ScholarMaster:
- **Paper 1**: Face recognition subsystem (FAISS indexing, adaptive thresholds)
- **Paper 4**: Compliance subsystem (timetable logic, ST-CSF)
- **Paper 6**: Audio subsystem (spectral analysis, context-aware alerts)
- **Paper 8**: Audit subsystem (Merkle tree, tamper detection)
- **Paper 10**: System integration (validates cross-subsystem interactions)

This is why:
1. **Logic is preserved**: Papers depend on implementation being correct
2. **Architecture is explicit**: Makes subsystem boundaries visible for publication
3. **Three versions exist**: `main_unified_backup.py` reproduces paper experiments exactly

**For reviewers**: If a paper claims "adaptive threshold τ(N)", you can `grep` the codebase and find it implemented in `face_recognizer.py:L78`. This is **reproducible research**.

---

## Quick Start (New Developers)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Initialize Data
```bash
# Create students database
python3 utils/create_student_db.py

# Generate timetable (or use existing data/timetable.csv)
python3 modules_legacy/scheduler.py
```

### 3. Run the System
```bash
# Recommended: Event-driven version
python3 main_event_driven.py

# Alternative: Refactored version
python3 main_refactored.py

# Legacy: Original implementation
python3 main_unified_backup.py
```

Press `q` in the video window to quit.

### 4. Validate Architecture
```bash
# Run validation tests (ensures papers are intact)
python3 test_papers.py

# Expected: 8/8 tests passed (100%)
```

---

## Project Structure

```
ScholarMasterEngine/
├── core/                              # Refactored Onion Architecture
│   ├── domain/                        # Pure business logic
│   │   ├── entities/                  # Student, Alert
│   │   ├── rules/                     # ComplianceRules, AlertRules
│   │   └── events/                    # Domain events
│   ├── application/                   # Use cases
│   │   ├── use_cases/                 # DetectTruancy, MarkAttendance
│   │   └── services/                  # EventHandlers
│   ├── infrastructure/                # External systems
│   │   ├── sensing/                   # Vision, audio, pose
│   │   ├── persistence/               # Repositories
│   │   ├── notifications/             # Alert service
│   │   └── events/                    # Event bus
│   └── interfaces/                    # Dependency inversion ports
│
├── modules_legacy/                    # Original implementations (backward compat)
│   ├── face_registry.py               # Paper 1
│   ├── context_manager.py             # Paper 4, 7
│   ├── audio_sentinel.py              # Paper 6
│   └── ... (11 more modules)
│
├── data/                              # Runtime data (DO NOT commit to git)
│   ├── timetable.csv                  # Schedule ground truth
│   ├── students.json                  # Student database
│   ├── alerts.json                    # Alert log
│   ├── audit_log.db                   # Merkle chain (SQLite)
│   └── faiss_index.bin                # Face gallery (FAISS)
│
├── docs/                              # Documentation
│   ├── SYSTEM_ARCHITECTURE_DIAGRAM.md # IEEE-grade architecture
│   ├── PAPER_SAFETY_MATRIX.md         # Paper validation matrix
│   ├── REFACTORING_COMPLETE.md        # Refactoring summary
│   └── ... (8 more docs)
│
├── main_event_driven.py              # Production entry point (RECOMMENDED)
├── main_refactored.py                # Conservative entry point
├── main_unified_backup.py            # Legacy entry point
├── test_papers.py                    # Validation suite
└── README.md                         # This file
```

---

## Common Tasks

### Add a New Student
```bash
python3 utils/create_superuser.py
# Then use admin panel to enroll face
```

### Modify Timetable
```bash
# Edit data/timetable.csv (7 columns: dept, program, year, section, day, start, end, subject, teacher, room)
# Restart system to reload
```

### Debug Event Flow
```bash
# Switch to refactored version (no event bus)
python3 main_refactored.py

# Or add debug logging to event bus
# In core/infrastructure/events/event_bus.py:
# print(f"Event published: {event.type}")
```

### Export Attendance Report
```bash
python3 utils/export_attendance.py --format csv --month 2026-01
```

---

## Testing

### Unit Tests (Domain Rules)
```bash
pytest tests/test_compliance_rules.py
pytest tests/test_alert_rules.py
```

### Integration Tests (Use Cases)
```bash
pytest tests/test_detect_truancy.py
```

### System Validation (All Papers)
```bash
python3 test_papers.py
# Expected: 8/8 tests passed
```

---

## Troubleshooting

### "FAISS index not found"
- Run `python3 utils/create_student_db.py` to initialize face gallery
- Or create empty index: `touch data/faiss_index.bin`

### "Timetable CSV corrupted"
- Check columns: `dept,program,year,section,day,start,end,subject,teacher,room`
- Validate with: `python3 utils/validate_timetable.py`

### "Event handler not receiving events"
- Ensure event type is subscribed: `event_bus.subscribe(EventType.X, handler)`
- Check event bus imports in `main_event_driven.py`

### "Paper validation fails"
- DO NOT proceed with deployment
- Revert changes to domain rules or interfaces
- Check `test_papers.py` output for exact failure

---

## Contributing

### Rules
1. **DO NOT modify domain rules** without paper author approval
2. **DO write tests** for new features (unit + integration)
3. **DO update documentation** (this README, architecture diagrams)
4. **DO run validation** before committing: `python3 test_papers.py`

### Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes (prefer infrastructure/application layers)
3. Run tests: `pytest tests/`
4. Validate papers: `python3 test_papers.py`
5. Update docs if architecture changed
6. Submit PR with clear justification

---

## Support & Contact

- **Primary Maintainer**: Narendra P (@NarendraaP)
- **Research Papers**: See `docs/PAPER_SAFETY_MATRIX.md` for full list
- **Architecture Questions**: See `docs/SYSTEM_ARCHITECTURE_DIAGRAM.md`
- **Onboarding**: This README (15-minute read)

---

**Last Updated**: January 27, 2026  
**Version**: 2.1.0  
**Status**: ✅ Production-Ready
