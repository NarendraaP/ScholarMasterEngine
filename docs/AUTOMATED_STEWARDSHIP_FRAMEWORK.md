# Automated Stewardship Framework

**Paper Reference**: Paper 16 - Beyond the Panopticon  
**Purpose**: Define the paradigm shift from Surveillance to Stewardship in AI monitoring systems

---

## Core Concept

**Automated Stewardship** is a governance model for AI where the system actively demonstrates its limitations. Unlike surveillance, which relies on information asymmetry, stewardship relies on information symmetry.

```
┌─────────────────────────────────────────────────────────────┐
│                     SURVEILLANCE                             │
│  ┌─────────┐                              ┌─────────┐       │
│  │  Admin  │ ────── Watches ─────────────▶│ Student │       │
│  └─────────┘                              └─────────┘       │
│      ▲                                                       │
│      │ Controls                                              │
│      │                                                       │
│  ┌─────────┐                                                 │
│  │ Black   │  (Opaque algorithms, hidden data)              │
│  │   Box   │                                                 │
│  └─────────┘                                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   STEWARDSHIP                                │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐            │
│  │  Admin  │◀─────▶│ Shared  │◀─────▶│ Student │            │
│  └─────────┘       │ Ledger  │       └─────────┘            │
│                    └─────────┘                               │
│                         │                                    │
│                    ┌─────────┐                               │
│                    │ Glass   │  (Visible algorithms,         │
│                    │   Box   │   auditable data)             │
│                    └─────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Information Asymmetry vs. Symmetry

| Dimension | Surveillance | Stewardship |
|-----------|--------------|-------------|
| Data visibility | System sees subject; subject sees nothing | Both parties see shared ledger |
| Algorithm transparency | "Black Box" - unknown capabilities | "Glass Box" - visible logic |
| Retention policies | Unknown or complex | Clear, verifiable |
| Correction rights | Difficult to exercise | One-click erasure |
| Power dynamic | Asymmetric (observer > observed) | Symmetric (mutual audit) |

---

## The Trust Loop Model

Stewardship builds trust through a sequential psychological process:

```
┌─────────────────┐
│ Visible Artifacts│ ─── Skeleton View, Privacy LEDs
└────────┬────────┘
         │ Triggers
         ▼
┌─────────────────┐
│ Affective Trust │ ─── "I feel safe" (emotional)
└────────┬────────┘
         │ Enables
         ▼
┌─────────────────┐
│ Cognitive Trust │ ─── "I can verify" (rational)
└────────┬────────┘
         │ Leads to
         ▼
┌─────────────────┐
│ System Acceptance│ ─── Stable cooperative use
└────────┬────────┘
         │ Reinforces (feedback loop)
         └──────────────────────────────┐
                                        ▼
                              [Visible Artifacts]
```

**Key Finding**: Affective trust is a **prerequisite** for cognitive trust. Anxious users don't audit logs; they demand removal.

---

## Visible Privacy Components

### 1. Skeleton View (Paper 3)
- Shows what the system **sees**: geometric keypoints only
- Proves what the system **cannot see**: facial identity, expressions
- Psychological effect: "It's just checking if I'm raising my hand"

### 2. Privacy LEDs (Paper 11)
- 🔴 Red: Recording mode active
- 🟢 Green: Volatile sensing (no storage)
- ⚫ Off: Privacy mode
- Ambient, always-visible reassurance

### 3. Audit Dashboard (Paper 8)
- Blockchain-backed immutable logs
- Student-accessible via mobile app
- Clear, simplified summaries (not raw JSON)

### 4. Delete Button (GDPR Article 17)
- One-click erasure via crypto-shredding
- **Paradox observed**: 38/43 users who clicked "Delete" immediately re-opted in
- Value is in **existence**, not usage

---

## Legal Alignment

### GDPR (EU)
| Article | Stewardship Implementation |
|---------|---------------------------|
| Art. 13/14 (Transparency) | Skeleton View + Dashboard |
| Art. 15 (Access) | Audit App |
| Art. 17 (Erasure) | Delete Button + Crypto-Shredding |
| Art. 25 (Privacy by Design) | Pose-only architecture |

### DPDP 2023 (India)
| Requirement | Stewardship Implementation |
|-------------|---------------------------|
| Consent Manager | Opt-in/Opt-out toggle |
| Data Fiduciary duties | Immutable audit trail |
| Purpose limitation | Zone-specific processing |

---

## Metrics of Success

A system achieves Automated Stewardship when:

1. **Trust Score > 4.0/5.0** (post-intervention)
2. **Anxiety Score < 2.5/5.0** (post-intervention)
3. **Visibility Attribution > 50%** (users cite visible features)
4. **Delete Re-Opt-In > 80%** (proves agency, not fear)

---

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Problem | Stewardship Alternative |
|--------------|---------|------------------------|
| "Trust us" messaging | Unverifiable claim | Provide audit trail |
| Hidden data collection | Violates autonomy | Show skeleton view |
| Complex retention policies | Creates confusion | One-click erasure |
| Technical-only privacy | Invisible to users | Visible privacy artifacts |
| Consent theater | Dark patterns | Genuine opt-out |

---

## References

- Bentham, J. (1995). *The Panopticon Writings*
- Nissenbaum, H. (2009). *Privacy in Context*
- Zuboff, S. (2019). *The Age of Surveillance Capitalism*
- Pasquale, F. (2015). *The Black Box Society*
- Mayer, R.C. et al. (1995). "An integrative model of organizational trust"

---

**Framework Version**: 1.0  
**Applicable Papers**: Paper 16 (Primary), Papers 3, 8, 11, 15 (Supporting)  
**Last Updated**: February 6, 2026
