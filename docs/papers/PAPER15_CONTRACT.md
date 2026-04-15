# Paper 15 Contract: Augmented Situation Awareness

**Paper**: "Augmented Situation Awareness: Reducing Cognitive Load in Campus Security via Spatially-Anchored AR Visualization"  
**Layer**: HCI / AR Interface Performance  
**Status**: ✅ Submission Ready  
**Contract Date**: 2026-04-15  
**Source**: `docs/papers/paper15_revised.tex`

---

## Primary Contribution

An Augmented Reality (AR) spatial computing interface that anchors critical system alerts directly to physical environments, acting as a cognitive offloading mechanism. Demonstrated a 42% reduction in Time-to-Action (TTA) and 87% fewer navigational errors against standard 2D dashboards in a controlled longitudinal study ($N=20$).

---

## Scope Definition

### In-Scope ✅
| Item | Description |
|------|-------------|
| AR Client Design | Anchor mathematics (Quaternion), SLAM, and EKF drift correction. |
| Cognitive Load Theory | Extraneous load reduction via split-attention mitigation. |
| Multiple Resource Theory | Wickens' spatial vs verbal channel offloading. |
| Fitts's Law | Conceptual modeling of visual search $ID_d$ vs $ID_a$. |
| Holographic Design System | Distance-based occlusion culling, Gestalt spatial clustering. |
| Empirical Performance | Time-to-action (TTA) and Navigational Error metrics. |
| NASA-TLX Evaluator | Quantitative survey of Mental Demand, Frustration, and Effort. |

### Out-of-Scope ❌
| Item | Why Excluded | Owning Paper |
|------|--------------|--------------| 
| Alert detection logic | Not an interface contribution | P2, P4, P6 |
| Event routing / Broker | Architecture layer | P18 / P20 |
| QoS / Event formatting | Architecture layer | P18 / P20 |
| Digital Twin synchronization | Orchestration layer | P20 |
| Sociology / Trust metrics | Not a performance metric | P16 |

---

## System-Agnostic Enforcement

> **CRITICAL RULE**: Paper 15 treats all upstream data as an **opaque event stream**. It describes HOW data is rendered visually but NEVER how data is generated, routed, or verified.

| Forbidden Content | Status |
|---|---|
| MQTT, Broker, QoS guarantees | ❌ ABSENT (removed from §III) |
| Digital Twin logic/backend sync | ❌ ABSENT (removed from §III) |
| System architecture / pipelines | ❌ ABSENT (clean overlap with P18) |
| Lifecycle orchestration logic | ❌ ABSENT (clean overlap with P20) |
| Trust, privacy anxiety, stewardship | ❌ ABSENT (clean overlap with P16) |

---

## Key Claims & Evidence

| Claim | Metric | Value | Evidence |
|-------|--------|-------|----------|
| Reduced Time-to-Action | Speed improvement | **42% faster** (28.1s vs 48.5s) | Paired t-test ($t=14.8, p<0.01$) |
| Navigation alignment | Errors per trial | **87% fewer** (0.4 vs 3.2) | Empirical trial data |
| Very large performance effect | Cohen's $d$ | **1.12** | Statistical analysis |
| Reduced Frustration | NASA-TLX score | **30 vs 60** | Repeated-measures ANOVA ($p<0.01$) |
| Spatial tracking accuracy | Error threshold | $\pm 10$ cm | Periodic QR visual relocalization |

---

## Paper Boundary (Clean Separation)

| Layer | Paper | P15 Relationship |
|-------|-------|------------------|
| Empirical Trust | P16 | P15 studies **cognitive performance**; P16 studies **human perception/trust**. |
| Capstone Doctrine | P17 | No overlap. P15 focuses strictly on UI ergonomics. |
| Enforcement | P18 | No overlap. P15 treats backend constraints as black-box outputs. |
| Reference Arch | P20 | No overlap. P15 completely avoids data routing or orchestration. |

---

## Reviewer Defense Points

### Q: "Does this paper duplicate the evaluation in Paper 16?"
**A**: No. Paper 15 measures objective **cognitive performance** (Time-to-action, Fitts's Law indexing, mental fatigue). Paper 16 measures subjective **sociological perception** (anxiety, trust, systemic legitimacy). The methods and contributions have no overlap.

### Q: "How does the AR client synchronize state?"
**A**: This paper explicitly bounds synchronization out of scope. It assumes a valid, opaque, spatially-referenced event stream is provided by the upstream architecture (covered in P18/P20) and evaluates purely the interface's cognitive rendering properties.

### Q: "Is N=20 sufficient for the claims?"
**A**: Yes. Within-subject designs assessing low-level perceptual/cognitive load typically require only $N \ge 12$ to achieve statistical power. Strong effect sizing ($d=1.12$) and high-frequency measurements compensate for the targeted sample size in an HCI context.

---

## Fixes Applied (v2.0)

| Fix | Severity | Status |
|-----|----------|--------|
| Rewrite §III to strip MQTT broker and digital twin logic | 🔴 P0 | ✅ Fixed |
| Redraw TikZ diagram to limit to UI-side (Opaque Source) | 🔴 P0 | ✅ Fixed |
| Removed references to "pipeline process", "system guarantees" | 🟡 P1 | ✅ Fixed |
| Ensure no mentions of trust or visible privacy (P16 overlap) | 🟡 P1 | ✅ Fixed |

---

**Contract Version**: 2.0  
**Last Updated**: 2026-04-15  
**CC Audit**: Passed (zero overclaims, zero boundary violations)  
**Authority**: Paper 15 LaTeX Source (HCI Performance)
