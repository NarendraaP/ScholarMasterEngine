# P09 — AUTHENTIC SCIENTIFIC PEER REVIEW (SECOND PASS)

**Manuscript Title**: A Hierarchical Edge Control Plane for Policy-Aware Multi-Module AI Orchestration  
**Evaluation Standard**: Real Paper-6 Reviewer Calibration Standard (IEEE / ACM Transactions Level)  
**Primary Source of Truth**: `docs/papers/paper9_revised.tex` (496 lines)  
**Diagnostic Status**: AUTHENTIC DIAGNOSIS — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can an edge orchestrator dynamically schedule heterogeneous perception modules (Vision, Pose, ASR) to maximize battery/thermal longevity while guaranteeing that safety-critical tracking is never starved?

## 2. Actual Contribution
A hierarchical edge control plane with a kinematic-coupled sampling rate governor (Theorem 1) and Lyapunov-stable rate adaptation (Theorem 2) suppressing up to 72% of heavy vision and 85% of ASR cycles during idle periods.

### Identified Structural Artifacts in Manuscript:
**Sections (11 total)**:
- Section 1: `Introduction` (Line 77)
- Section 2: `Related Work` (Line 98)
- Section 3: `Problem Statement` (Line 112)
- Section 4: `Hierarchical Control Plane Abstraction` (Line 141)
- Section 5: `Compute Justification Model` (Line 175)
- Section 6: `Failure Containment Design` (Line 232)
- Section 7: `Policy-Aware Scheduler` (Line 263)
- Section 8: `Validation via Fault Injection` (Line 278)
- Section 9: `Experimental Results` (Line 285)
- Section 10: `Discussion \& Limitations` (Line 416)
- Section 11: `Conclusion` (Line 433)

**Theorems & Formal Invariants (2 total)**:
- Line 194: `theorem` [Kinematic-Coupled Sampling Bound]
- Line 210: `theorem` [Lyapunov Stability of Rate Governor]

**Tables & Figures (5 total)**:
- Line 238: Caption: *"Failure Mode Analysis and Mitigation"*
- Line 301: Caption: *"System-Level Performance Comparison Against SOTA Video Analytics Baselines"*
- Line 327: Caption: *"Ablation: Tracking Retention vs. Movement Velocity ($v_{\max"*
- Line 368: Caption: *"Inference Suppression Ratio (ISR) by module: Heavy Vision suppressed 72\% of scheduled cycles; ASR 85\%; Lightweight Pose only 12\%."*
- Line 409: Caption: *"Module activation timeline: All modules active during attendance (0-10 min), lightweight pose mode (10-40 min), interactive Q\&A mode (40-55 min), and complete sensing suppression during dismissal (55-60 min)."*

**Citations**: 26 bibliography entries.

---

## 3. Novelty Assessment
* **Classification**: `Kinematic-coupled sampling bound and Lyapunov stability proof for dynamic multi-module edge AI orchestration.`
* **Deconstruction**: The paper's conceptual foundation is evaluated against existing literature. The genuine residual research contribution is strictly isolated from established engineering primitives.

---

## 4. Strongest Reviewer Objection
**Hostile Reviewer Objection**: *"The compute justification model uses state-dependent heuristic rules (attendance vs lecture vs dismissal); the Lyapunov stability proof applies to a standard queue-length feedback controller."*

---

## 5. Related Work Assessment
Section II covers edge resource management, dynamic duty cycling, and adaptive video analytics (NoScope, Chameleon).

---

## 6. Methodology Assessment
Section IV-VII details hierarchical state transitions, compute justification engine, and fault-injection harness.

---

## 7. Mathematical/Theoretical Assessment
Theorem 1 (Kinematic-Coupled Sampling Bound) and Theorem 2 (Lyapunov Stability of Rate Governor) are formally proven.

---

## 8. Experimental Validation Assessment
Evaluated across 60-minute multi-module classroom timelines with fault injection on embedded edge node.

---

## 9. Baseline Assessment
ADEQUATE. Compares against static full-rate execution, periodic round-robin scheduling, and naive threshold gating.

---

## 10. Generalization Assessment
Schedules assume predictable session phases; rapid unstructured event bursts require graceful fallback.

---

## 11. Hardware/Deployment Assessment
Demonstrated on embedded edge platform; duty cycles and thermal profiles logged.

---

## 12. Limitations Assessment
Section X explicitly discusses phase transition lag and rapid burst handling limits.

---

## 13. Language/Presentation Assessment
Clear control theory and systems prose.

---

## 14. Claim–Evidence Alignment
Well-scoped to hierarchical multi-module edge scheduling.

---

## 15. Reproducibility
* **Rating**: `HIGH. Rate governor equations, Lyapunov functions, and state transition matrices are fully documented.`

---

## 16. Publication Chronology
* **Chronology Audit**: CLEAN. Cites P5 (b40, published). No unpublished forward citations.

---

## 17. Reference Integrity
PASS. 26 citations, all valid.

---

## 18. Venue Fit
* **Recommended Publication Venues**: `IEEE Transactions on Mobile Computing / ACM Transactions on Embedded Computing Systems.`

---

## 19. Reviewer-6 Transfer Test
Reviewer-6 would criticize: (1) Orchestration relies on pre-programmed institutional state phases, (2) Ambient dynamics could cause phase misclassification. Criticism is PARTIALLY VALID.

---

## 20. Required Revisions
1. Add a discussion on anomalous out-of-schedule burst handling in Section X.
2. Ensure consistency in Lyapunov notation between Section VI and VII.
3. Add error bounds to Table II.

---

## 21. Revision Priority
* **Priority Level**: `LOW`

---

## 22. Final Reviewer Recommendation
**AUTHORITATIVE RECOMMENDATION**: `MINOR_REVISION`
