# P18 — AUTHENTIC SCIENTIFIC PEER REVIEW (SECOND PASS)

**Manuscript Title**: Runtime Enforcement of Architectural Irreversibility in Edge AI Systems  
**Evaluation Standard**: Real Paper-6 Reviewer Calibration Standard (IEEE / ACM Transactions Level)  
**Primary Source of Truth**: `docs/papers/paper18_revised.tex` (651 lines)  
**Diagnostic Status**: AUTHENTIC DIAGNOSIS — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can an edge operating system deterministically enforce memory zeroization and process-isolated watchdogs when an application crashes, hangs, or attempts unauthorized state retention?

## 2. Actual Contribution
A runtime enforcement framework with process-isolated Watchdog daemons, shared memory fences, and SIGKILL termination, validating 100% fail-closed transitions across 6 failure injection scenarios and proving zero post-crash residue.

### Identified Structural Artifacts in Manuscript:
**Sections (9 total)**:
- Section 1: `Introduction` (Line 81)
- Section 2: `Threat Model and Failure Taxonomy` (Line 97)
- Section 3: `Runtime Enforcement Mechanisms` (Line 136)
- Section 4: `Formal Irreversibility Invariants` (Line 253)
- Section 5: `Failure Injection and Test Harness` (Line 313)
- Section 6: `Results` (Line 394)
- Section 7: `Discussion` (Line 500)
- Section 8: `Scope and Relation to Prior Work` (Line 553)
- Section 9: `Conclusion` (Line 574)

**Theorems & Formal Invariants (0 total)**:
None (Empirical / Architecture paper)

**Tables & Figures (9 total)**:
- Line 112: Caption: *"Failure Taxonomy"*
- Line 226: Caption: *"Watchdog Architecture. The Watchdog operates with process-level isolation within the same OS instance, monitoring the Shared Fence. If the Main Process hangs or violates TTL, the Watchdog issues a SIGKILL."*
- Line 330: Caption: *"Fault Injection Scenarios"*
- Line 399: Caption: *"TTL Enforcement Results"*
- Line 418: Caption: *"Watchdog Termination Results"*
- Line 436: Caption: *"Post-Crash Residue Detection (Application Layer)"*
- Line 459: Caption: *"System Halt Behavior"*
- Line 478: Caption: *"Invariant Verification"*
- Line 522: Caption: *"Fail-Closed State Machine. Any critical invariant violation (TTL, Watchdog) causes transition to the HALT state. The only possible transition caused by network problems is the move to the Degraded (Safe) state, from which no outputs are produced, but the local processing is still allowed."*

**Citations**: 24 bibliography entries.

---

## 3. Novelty Assessment
* **Classification**: `Complete runtime harness and failure injection methodology for enforcing irreversible memory destruction on edge AI nodes.`
* **Deconstruction**: The paper's conceptual foundation is evaluated against existing literature. The genuine residual research contribution is strictly isolated from established engineering primitives.

---

## 4. Strongest Reviewer Objection
**Hostile Reviewer Objection**: *"The watchdog and shared memory fence mechanisms use standard POSIX OS signals (SIGKILL, POSIX shared memory, timerfd); memory zeroization uses memset/bzero equivalents. Furthermore, the manuscript contains a massive cluster of forward citations (P3, P9, P10, P11, P12, P13, P17, P22, P23) referencing unpublished papers."*

---

## 5. Related Work Assessment
Section II covers runtime verification, OS fault tolerance, secure deallocation, and fail-safe systems.

---

## 6. Methodology Assessment
Section III-V details Watchdog architecture, TTL timers, fault injection harness, and fail-closed state machines.

---

## 7. Mathematical/Theoretical Assessment
Contains formal invariant definitions (INV-01 through INV-06) and state machine transitions without mathematical theorem environments.

---

## 8. Experimental Validation Assessment
6 fault injection scenarios (TTL violation, thread hang, buffer overflow, SIGSEGV, memory leak, unhandled exception) with 9 tables/figures.

---

## 9. Baseline Assessment
ADEQUATE. Compares against unmonitored baseline execution and standard non-isolated exception handlers.

---

## 10. Generalization Assessment
Valid for POSIX Linux operating systems; microcontrollers without MMU/process isolation are unsupported.

---

## 11. Hardware/Deployment Assessment
Physical ARM64 Linux edge appliance.

---

## 12. Limitations Assessment
Section VIII discusses OS kernel panic limits and hardware-level DMA attack vectors.

---

## 13. Language/Presentation Assessment
Professional systems security text.

---

## 14. Claim–Evidence Alignment
Empirically supported by the fault injection test results.

---

## 15. Reproducibility
* **Rating**: `HIGH. Invariant specifications, watchdog logic, and fault injection matrices are fully documented.`

---

## 16. Publication Chronology
* **Chronology Audit**: SEVERE VIOLATIONS: Cites unpublished papers P3 (`b10`), P10 (`b11`), P11 (`b12`), P9 (`b13`), P17 (`b17`), P22 (`kumar2026scholar22`), and P23 (`kumar2026scholar23`).

---

## 17. Reference Integrity
Contains massive cluster of forward citations that must be sanitized.

---

## 18. Venue Fit
* **Recommended Publication Venues**: `IEEE Transactions on Dependable and Secure Computing / ACM Transactions on Computer Systems.`

---

## 19. Reviewer-6 Transfer Test
Reviewer-6 would criticize: (1) Reliance on standard POSIX timerfd and SIGKILL signals, (2) Massive forward-referencing of unpublished internal reports. Criticism is VALID.

---

## 20. Required Revisions
1. Sanitize all forward internal citations (P3, P9, P10, P11, P12, P13, P17, P22, P23), replacing them with external systems literature.
2. Add formal theorem environment for State Reachability.
3. Add latency overhead measurements of the watchdog polling thread.

---

## 21. Revision Priority
* **Priority Level**: `CRITICAL`

---

## 22. Final Reviewer Recommendation
**AUTHORITATIVE RECOMMENDATION**: `MAJOR_REVISION`
