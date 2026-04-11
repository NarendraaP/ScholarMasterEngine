# Cross-Paper Event Flow Architecture

**Document**: ScholarMaster Cross-Paper Flow Verification  
**Purpose**: Document the unified event-driven architecture connecting all 16 papers

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCHOLARMASTER UNIFIED ARCHITECTURE                    │
│                              (16 Papers, 1 System)                          │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │       UNIFIED ORCHESTRATOR       │
                    │   core/orchestration/unified_   │
                    │         orchestrator.py         │
                    └────────────────┬────────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       │                             │                             │
       ▼                             ▼                             ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│   SENSING    │           │  GOVERNANCE  │           │ DISTRIBUTED  │
│   P1-P6      │           │   P7-P11     │           │ INTELLIGENCE │
│              │           │              │           │   P12-P14    │
│ • Face (P1)  │           │ • Audit (P8) │           │ • FL (P13)   │
│ • Context(P2)│           │ • Crypto(P8) │           │ • Drift (P13)│
│ • Pose (P3)  │           │ • Privacy(P7)│           │ • Cross (P14)│
│ • Edge (P4)  │           │ • Orch (P9)  │           │              │
│ • Audio (P5) │           │ • Rules (P10)│           │              │
│ • Engage(P6) │           │ • LED (P11)  │           │              │
└──────────────┘           └──────────────┘           └──────────────┘
       │                             │                             │
       └─────────────────────────────┼─────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │         PRESENTATION            │
                    │           Paper 15              │
                    │                                 │
                    │  • MQTT Subscriber              │
                    │  • AR Renderer                  │
                    │  • Clutter Manager              │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │          OPERATOR               │
                    │          (Human)                │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     SOCIOLOGICAL VALIDATION     │
                    │           Paper 16              │
                    │  (Read-Only Observer Layer)     │
                    └─────────────────────────────────┘
```

---

## Event Types

| Event | Source | Subscribers | Purpose |
|-------|--------|-------------|---------|
| `FACE_DETECTED` | P1 | P7, P8, P15 | Identity verification |
| `POSE_DETECTED` | P3 | P8, P13, P16 | Skeleton for privacy + FL |
| `AUDIO_ANOMALY` | P5 | P8, P10, P15 | Noise detection |
| `ALERT_TRIGGERED` | P10 | P8, P15 | Safety/compliance alert |
| `AUDIT_LOGGED` | P8 | P15 | AR dashboard update |
| `GRADIENT_READY` | P13 | P14 | FL aggregation signal |
| `DRIFT_DETECTED` | P13 | P8, P15 | Model drift warning |
| `OPERATOR_ACKNOWLEDGED` | P15 | P8, P16 | Human response |

---

## Privacy Boundaries

**INVARIANT**: No raw biometrics cross paper boundaries.

| Layer | May Send | May NOT Send |
|-------|----------|--------------|
| Sensing | Skeleton keypoints, zone IDs | Raw frames, face images |
| Governance | Hashes, audit IDs | Embeddings, PII |
| FL | Gradient hashes | Raw weights, training data |
| AR | Symbolic alerts | Any biometric data |

---

## Integration Code Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/orchestration/unified_orchestrator.py` | 420 | Central event router |
| `core/infrastructure/mqtt/mqtt_publisher.py` | 250 | AR event publishing |
| `core/domain/events/cross_paper_events.py` | 170 | FL/Audit/AR events |
| `tests/test_cross_paper_flow.py` | 350 | Integration tests |

---

## Running Verification

```bash
# Run cross-paper flow tests
pytest tests/test_cross_paper_flow.py -v

# Test orchestrator standalone
python core/orchestration/unified_orchestrator.py

# Test MQTT publisher
python core/infrastructure/mqtt/mqtt_publisher.py
```

---

**Last Updated**: February 7, 2026
