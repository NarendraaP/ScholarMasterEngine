# ScholarMasterEngine - Quick Start Guide (Refactored System)

**Version**: 2.1.0 (Event-Driven Architecture)  
**Last Updated**: January 27, 2026

---

## 🚀 Quick Start

### Run the Event-Driven Version (Recommended - SOTA)
```bash
python3 main_event_driven.py
```

### Run the Refactored Version (Stable)
```bash
python3 main_refactored.py
```

### Run the Original Version (Backward Compatible)
```bash
python3 main_unified.py
```

---

## 📁 System Versions

| File | Lines | Architecture | Status | Use Case |
|------|-------|--------------|--------|----------|
| `main_event_driven.py` | 490 | Event-Driven | ✅ SOTA | Production (recommended) |
| `main_refactored.py` | 467 | Onion Architecture | ✅ Stable | Production (safe) |
| `main_unified.py` | 835 | Monolithic | ✅ Legacy | Backward compat |

---

## 🏗️ Architecture Overview

### New Structure (`core/`)
```
core/
├── domain/              # Business logic (ZERO dependencies)
│   ├── entities/        # Student, Alert, etc.
│   ├── rules/           # ComplianceRules, AlertRules
│   └── events/          # Domain events
│
├── application/         # Use cases & handlers
│   ├── use_cases/       # DetectTruancy, MarkAttendance
│   └── services/        # EventHandlers
│
├── infrastructure/      # External systems
│   ├── sensing/         # Face, audio, pose
│   ├── persistence/     # Repositories
│   ├── notifications/   # Alerts
│   └── events/          # EventBus
│
└── interfaces/          # Dependency inversion ports
    ├── i_face_recognizer.py
    ├── i_audio_analyzer.py
    ├── i_schedule_repository.py
    └── i_alert_service.py
```

---

## 🔧 Key Features

### Event-Driven Architecture
- **Sensors publish events** (NO decision making)
- **Use cases subscribe** to events
- **Side effects triggered** asynchronously
- **Decoupled components** for extensibility

### Dependency Inversion
- Core depends on **interfaces**, not implementations
- Easy to mock for testing
- Swap implementations without changing core logic

### Domain Purity
- Business rules in `core/domain/rules/`
- ZERO infrastructure dependencies
- Testable in isolation

---

## 📊 What Changed?

### Before (main_unified.py)
```python
# Embedded business logic
if current_zone == expected_room:
    return True, "Compliant"
else:
    return False, "TRUANCY"
    
# Direct method calls (tight coupling)
self.trigger_alert("Warning", "Truancy", zone)
```

### After (main_event_driven.py)
```python
# Extracted to domain rules
is_compliant = ComplianceRules.is_in_expected_location(current_zone, expected_zone)

# Event-driven (loose coupling)
self.event_bus.publish(Event(
    type=EventType.VIOLATION_DETECTED,
    payload={'student_id': student_id}
))
```

---

## ✅ All Papers Still Valid

No research logic was changed, only reorganized:
- **Paper 1**: FaceRecognizer adapter (InsightFace + FAISS)
- **Paper 4**: ComplianceRules (ST-CSF logic)
- **Paper 5**: PowerMonitor (unchanged)
- **Paper 6**: AudioAnalyzer (spectral analysis)
- **Paper 8**: SimplifiedAuditLog (Merkle tree)
- **Papers 2, 3, 7, 9, 10**: All intact

---

## 🎯 Recommended: Use Event-Driven Version

**Why?**
- ✅ SOTA architecture
- ✅ Aligns with Papers 9 & 10
- ✅ Extensible (add features by publishing events)
- ✅ Decoupled (sensors don't make decisions)
- ✅ Production-grade

**Run it:**
```bash
python3 main_event_driven.py
```

Press `q` in the video window to quit.

---

## 📝 Next Steps

1. **Test the system**: Run `main_event_driven.py`
2. **Review docs**: Read `REFACTORING_COMPLETE.md`
3. **Explore code**: Check `core/` structure
4. **Deploy**: Use in production when ready

---

**Questions?** See full documentation in `docs/REFACTORING_COMPLETE.md`
