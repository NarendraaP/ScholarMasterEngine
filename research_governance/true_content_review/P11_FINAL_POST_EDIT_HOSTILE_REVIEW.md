# P11 — FINAL POST-EDIT HOSTILE REVIEW

**Title**: Lifecycle Hardening of Immutable Edge Appliances under Power and Connectivity Instability  
**Review Standard**: Reviewer-6 Skeptical Journal Standard (IEEE / ACM Transactions Level)  
**Status**: Diagnostic Evaluation — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can unattended edge AI appliances maintain 100% state recovery invariance across repeated sudden power cuts and survive corrupted over-the-air (OTA) firmware updates?

## 2. What the Current Paper Successfully Establishes
An immutable appliance architecture combining read-only squashfs root filesystems, volatile overlayfs RAM layers, and dual A/B partition rollback, proving power-cut state invariance (Theorem 1) and bounded rollback liveness (Lemma 1) across 50 physical power-cut cycles.

## 3. Strongest Remaining Reviewer Objection
**Objection**: *"A/B partitioning and squashfs/overlayfs immutable roots are standard embedded Linux distribution patterns (e.g., Yocto, Android, OpenWrt)."*

## 4. Novelty Verdict
* **Classification**: `APPLICATION OF KNOWN TECHNIQUE / NEW ARCHITECTURE`
* **Novelty Evaluation**: Mathematical formalization of power-cut state recovery invariance and dual-partition OTA rollback liveness for edge AI appliances.

## 5. Related Work Verdict
* **Verdict**: ADEQUATE. Covers robust OTA systems (RAUC, Mender), immutable infrastructure, and embedded crash recovery.

## 6. Method Verdict
* **Verdict**: WELL DEVELOPED. Details storage layering ($H_0$ squashfs, $H_{rw}$ overlayfs), A/B partition logic, and observability agent.

## 7. Mathematical Theory Verdict
* **Verdict**: ADEQUATE. Theorem 1 (Power-Cut State Recovery Invariance) and Lemma 1 (Bounded Rollback Liveness under Poisoned OTA) are proven.

## 8. Experimental Evidence Verdict
* **Classification**: `DIRECTLY DEMONSTRATED. 50 physical power-cut cycles with zero filesystem corruption and verified rollback on poisoned OTA.`

## 9. Experimental Breadth
* Number of cycles: n=50 hard power-cuts; Hardware: Embedded ARM64 appliance with flash storage; OTA test cases: Corrupted kernel, bad signature.

## 10. Baseline Adequacy
* **Verdict**: `ADEQUATE. Compares against standard read-write ext4 root filesystems and single-partition OTA updaters.`

## 11. Generalization Verdict
* Applicable across embedded Linux platforms with flash storage and bootloader A/B support (U-Boot/GRUB).

## 12. Hardware / Deployment Verdict
* DIRECTLY DEMONSTRATED on physical ARM64 hardware with bill-of-materials (BOM) cost analysis.

## 13. Claim-Evidence Alignment
* Well-scoped to immutable embedded Linux appliances.

## 14. Limitations Verdict
* ADEQUATE. Notes non-volatile state synchronization latencies and dual-partition storage overhead.

## 15. Reproducibility Verdict
* **Classification**: `HIGH. Storage layering stack, partition tables, and rollback state machines are fully described.`

## 16. Flow and Scientific Depth
* Flow: STRONG. Depth: WELL DEVELOPED (6 pages, 2 theorems, 4 tables/figures).

## 17. Language and Presentation
* COSMETIC. Clear systems and reliability engineering text.

## 18. Salami-Slicing Verdict
* **Classification**: `INDEPENDENT. Specific ownership of OS-level immutability and OTA recovery, distinct from application-level logic.`

## 19. Publication Chronology Verdict
* **Audit Finding**: VIOLATION. Cites unpublished future papers P12 (b29) and P10 (b30).

## 20. Reference Integrity Verdict
* Contains future citations to P10 and P12.

## 21. P6-Style Concerns That Still Apply
* Novelty of A/B and overlayfs patterns (YES), Publication chronology (YES).

## 22. P6-Style Concerns Successfully Resolved
* Theorem 1 and 50-cycle physical power-cut validation establish rigorous lifecycle hardening.

## 23. Strongest Defensible Rejection Argument
'A/B partitioning and read-only squashfs roots are standard embedded Linux engineering; the scientific contribution beyond standard best practices is marginal.'

## 24. Required Revision, If Any
1. Remove citations to P10 and P12. 2. Frame novelty as the formal invariance proof of edge AI state recovery under sudden power loss.

## 25. Final Recommendation
**Recommendation**: `MINOR_REVISION`
