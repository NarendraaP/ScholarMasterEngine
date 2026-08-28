# P09 — FINAL POST-EDIT HOSTILE REVIEW

**Title**: A Hierarchical Edge Control Plane for Policy-Aware Multi-Module AI Orchestration  
**Review Standard**: Reviewer-6 Skeptical Journal Standard (IEEE / ACM Transactions Level)  
**Status**: Diagnostic Evaluation — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can an edge orchestrator dynamically schedule heterogeneous perception modules (Vision, Pose, ASR) to maximize battery/thermal longevity while guaranteeing that safety-critical tracking is never starved?

## 2. What the Current Paper Successfully Establishes
A hierarchical edge control plane with a kinematic-coupled sampling rate governor (Theorem 1) and Lyapunov-stable rate adaptation (Theorem 2) suppressing up to 72% of heavy vision and 85% of ASR cycles during idle periods.

## 3. Strongest Remaining Reviewer Objection
**Objection**: *"The compute justification model uses heuristic state-dependent rules (attendance vs lecture vs dismissal); Lyapunov stability proof applies to a standard queue-length feedback controller."*

## 4. Novelty Verdict
* **Classification**: `NEW ARCHITECTURE / NEW ANALYTICAL RESULT`
* **Novelty Evaluation**: Kinematic-coupled sampling bound and Lyapunov stability proof for dynamic multi-module edge AI orchestration.

## 5. Related Work Verdict
* **Verdict**: ADEQUATE. Covers edge resource management, dynamic duty cycling, and adaptive video analytics (NoScope, Chameleon).

## 6. Method Verdict
* **Verdict**: WELL DEVELOPED. Details hierarchical state transitions, compute justification engine, and fault-injection harness.

## 7. Mathematical Theory Verdict
* **Verdict**: ADEQUATE. Theorem 1 (Kinematic-Coupled Sampling Bound) and Theorem 2 (Lyapunov Stability of Rate Governor) are formally proven.

## 8. Experimental Evidence Verdict
* **Classification**: `DIRECTLY DEMONSTRATED. Evaluated across 60-minute multi-module classroom timelines with fault injection.`

## 9. Experimental Breadth
* Number of datasets: 60-minute synthetic multi-modal classroom trace; Hardware: Embedded edge node; Modules: Vision, Pose, ASR.

## 10. Baseline Adequacy
* **Verdict**: `ADEQUATE. Compares against static full-rate execution, periodic round-robin scheduling, and naive threshold gating.`

## 11. Generalization Verdict
* Schedules assume predictable session phases; rapid unstructured event bursts require graceful fallback.

## 12. Hardware / Deployment Verdict
* DEMONSTRATED on embedded edge platform; duty cycles and thermal profiles logged.

## 13. Claim-Evidence Alignment
* Well-scoped to hierarchical multi-module edge scheduling.

## 14. Limitations Verdict
* ADEQUATE. Section X explicitly discusses phase transition lag and rapid burst handling limits.

## 15. Reproducibility Verdict
* **Classification**: `HIGH. Rate governor equations, Lyapunov functions, and state transition matrices are fully documented.`

## 16. Flow and Scientific Depth
* Flow: STRONG. Depth: WELL DEVELOPED (6 pages, 2 theorems, 5 tables/figures).

## 17. Language and Presentation
* COSMETIC. Clear control theory and systems prose.

## 18. Salami-Slicing Verdict
* **Classification**: `INDEPENDENT. Owns multi-module control plane orchestration, distinct from P23's single-pipeline queueing cascade.`

## 19. Publication Chronology Verdict
* **Audit Finding**: CLEAN. Cites P5 (b40, published). No future unpublished citations.

## 20. Reference Integrity Verdict
* PASS. 26 citations, all valid.

## 21. P6-Style Concerns That Still Apply
* Control plane novelty (YES), Rapid burst reactivity (YES).

## 22. P6-Style Concerns Successfully Resolved
* Lyapunov stability and kinematic sampling rate bounds are rigorously established.

## 23. Strongest Defensible Rejection Argument
'The orchestration relies on pre-programmed institutional state phases; unpredictable ambient dynamics could cause phase misclassification.'

## 24. Required Revision, If Any
1. Add a brief remark on handling out-of-schedule anomalous bursts. 2. Ensure consistency in Lyapunov notation.

## 25. Final Recommendation
**Recommendation**: `MINOR_REVISION`
