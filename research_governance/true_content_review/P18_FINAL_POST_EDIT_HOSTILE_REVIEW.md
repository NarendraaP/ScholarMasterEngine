# P18 — FINAL POST-EDIT HOSTILE REVIEW

**Title**: Runtime Enforcement of Architectural Irreversibility in Edge AI Systems  
**Review Standard**: Reviewer-6 Skeptical Journal Standard (IEEE / ACM Transactions Level)  
**Status**: Diagnostic Evaluation — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can an edge operating system deterministically enforce memory zeroization and process-isolated watchdogs when an application crashes, hangs, or attempts unauthorized state retention?

## 2. What the Current Paper Successfully Establishes
A runtime enforcement framework with process-isolated Watchdog daemons, shared memory fences, and SIGKILL termination, validating 100% fail-closed transitions across 6 failure injection scenarios and proving zero post-crash residue.

## 3. Strongest Remaining Reviewer Objection
**Objection**: *"The watchdog and shared memory fence mechanisms use standard POSIX OS signals (SIGKILL, POSIX shared memory, timerfd); memory zeroization uses memset/bzero equivalents."*

## 4. Novelty Verdict
* **Classification**: `ENGINEERING IMPLEMENTATION / NEW ARCHITECTURE`
* **Novelty Evaluation**: Complete runtime harness and failure injection methodology for enforcing irreversible memory destruction on edge AI nodes.

## 5. Related Work Verdict
* **Verdict**: ADEQUATE. Covers runtime verification, OS fault tolerance, secure deallocation, and fail-safe systems.

## 6. Method Verdict
* **Verdict**: WELL DEVELOPED. Details Watchdog architecture, TTL timers, fault injection harness, and fail-closed state machines.

## 7. Mathematical Theory Verdict
* **Verdict**: COMPRESSED. Contains formal invariant definitions (INV-01 through INV-06) and state machine transitions without mathematical theorem environments.

## 8. Experimental Evidence Verdict
* **Classification**: `DIRECTLY DEMONSTRATED. 6 fault injection scenarios (TTL violation, thread hang, buffer overflow, SIGSEGV, memory leak, unhandled exception) with 9 tables/figures.`

## 9. Experimental Breadth
* Number of injection scenarios: 6 scenarios; Test runs: 100 iterations per scenario; Hardware: Physical ARM64 edge node; Post-crash memory audit: Core dump byte scanning.

## 10. Baseline Adequacy
* **Verdict**: `ADEQUATE. Compares against unmonitored baseline execution and standard non-isolated exception handlers.`

## 11. Generalization Verdict
* Valid for POSIX Linux operating systems; microcontrollers without MMU/process isolation are unsupported.

## 12. Hardware / Deployment Verdict
* DIRECTLY DEMONSTRATED on physical ARM64 Linux edge appliance.

## 13. Claim-Evidence Alignment
* Empirically supported by the fault injection test results.

## 14. Limitations Verdict
* ADEQUATE. Section VIII discusses OS kernel panic limits and hardware-level DMA attack vectors.

## 15. Reproducibility Verdict
* **Classification**: `HIGH. Invariant specifications, watchdog logic, and fault injection matrices are fully documented.`

## 16. Flow and Scientific Depth
* Flow: STRONG. Depth: WELL DEVELOPED (7 pages, 9 tables/figures).

## 17. Language and Presentation
* COSMETIC. Professional systems security text.

## 18. Salami-Slicing Verdict
* **Classification**: `PROGRAMMATICALLY RELATED BUT INDEPENDENT. Provides runtime implementation for P17's doctrine and P19's formal TCB.`

## 19. Publication Chronology Verdict
* **Audit Finding**: VIOLATION. Cites unpublished future papers P10, P11, P12, P13, P17, P22 (kumar2026scholar22), and P23 (kumar2026scholar23).

## 20. Reference Integrity Verdict
* Contains massive cluster of future citations (P10, P11, P12, P13, P17, P22, P23). Must be sanitized.

## 21. P6-Style Concerns That Still Apply
* Novelty of POSIX watchdog signals (YES), Publication chronology violations (YES).

## 22. P6-Style Concerns Successfully Resolved
* Comprehensive 6-scenario fault injection telemetry and byte-level residue audits are presented.

## 23. Strongest Defensible Rejection Argument
'The runtime relies on standard POSIX timerfd and SIGKILL signals; the manuscript suffers from severe publication chronology violations citing multiple future papers.'

## 24. Required Revision, If Any
1. Sanitize all future citations (P10, P11, P12, P13, P17, P22, P23). 2. Highlight the formal state machine and memory residue scanning as the empirical contribution.

## 25. Final Recommendation
**Recommendation**: `MAJOR_REVISION`
