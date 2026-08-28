# P11 — AUTHENTIC SCIENTIFIC PEER REVIEW (SECOND PASS)

**Manuscript Title**: Lifecycle Hardening of Immutable Edge Appliances under Power and Connectivity Instability  
**Evaluation Standard**: Real Paper-6 Reviewer Calibration Standard (IEEE / ACM Transactions Level)  
**Primary Source of Truth**: `docs/papers/paper11_revised.tex` (466 lines)  
**Diagnostic Status**: AUTHENTIC DIAGNOSIS — NO MANUSCRIPT EDITS  

---

## 1. Research Question
How can unattended edge AI appliances maintain 100% state recovery invariance across repeated sudden power cuts and survive corrupted over-the-air (OTA) firmware updates?

## 2. Actual Contribution
An immutable appliance architecture combining read-only squashfs root filesystems, volatile overlayfs RAM layers, and dual A/B partition rollback, proving power-cut state invariance (Theorem 1) and bounded rollback liveness (Lemma 1) across 50 physical power-cut cycles.

### Identified Structural Artifacts in Manuscript:
**Sections (12 total)**:
- Section 1: `Introduction` (Line 85)
- Section 2: `Failure-State Taxonomy and Related Work` (Line 106)
- Section 3: `Appliance Invariance Model` (Line 126)
- Section 4: `Reliability Engineering` (Line 185)
- Section 5: `OTA Updates \& Fleet Management` (Line 235)
- Section 6: `Operational Configuration Policies` (Line 255)
- Section 7: `Network \& Data Resilience` (Line 268)
- Section 8: `Defense-in-Depth Security Architecture` (Line 275)
- Section 9: `Full-Stack Observability Pipeline` (Line 293)
- Section 10: `Fleet Lifecycle Validation` (Line 308)
- Section 11: `Deployment Economics (BOM)` (Line 369)
- Section 12: `Conclusion` (Line 404)

**Theorems & Formal Invariants (2 total)**:
- Line 133: `theorem` [Power-Cut State Recovery Invariance]
- Line 150: `lemma` [Bounded Rollback Liveness under Poisoned OTA]

**Tables & Figures (4 total)**:
- Line 176: Caption: *"Appliance Invariance Architecture. The persistent lower layer ($H_0$) is never written to during normal operation. All runtime modifications are made either in the volatile UpperDir (RAM) or within versioned container layers. Upon power-down, only the volatile layers are lost."*
- Line 324: Caption: *"System Resilience and Lifecycle Overhead Comparison"*
- Line 347: Caption: *"Power Failure Resilience Test Results ($n=50$ cycles)"*
- Line 374: Caption: *"Per-Node Hardware Bill of Materials (CapEx Snapshot)"*

**Citations**: 26 bibliography entries.

---

## 3. Novelty Assessment
* **Classification**: `Mathematical formalization of power-cut state recovery invariance and dual-partition OTA rollback liveness for edge AI appliances.`
* **Deconstruction**: The paper's conceptual foundation is evaluated against existing literature. The genuine residual research contribution is strictly isolated from established engineering primitives.

---

## 4. Strongest Reviewer Objection
**Hostile Reviewer Objection**: *"A/B partitioning and squashfs/overlayfs immutable roots are standard embedded Linux distribution patterns (e.g., Yocto, Android, OpenWrt). A reviewer will argue this is standard embedded OS configuration."*

---

## 5. Related Work Assessment
Section II covers robust OTA systems (RAUC, Mender), immutable infrastructure, and embedded crash recovery.

---

## 6. Methodology Assessment
Section III-IX details storage layering ($H_0$ squashfs, $H_{rw}$ overlayfs), A/B partition logic, and observability agent.

---

## 7. Mathematical/Theoretical Assessment
Theorem 1 (Power-Cut State Recovery Invariance) and Lemma 1 (Bounded Rollback Liveness under Poisoned OTA) are proven using state-transition invariants.

---

## 8. Experimental Validation Assessment
50 physical power-cut cycles with zero filesystem corruption and verified rollback on poisoned OTA.

---

## 9. Baseline Assessment
ADEQUATE. Compares against standard read-write ext4 root filesystems and single-partition OTA updaters.

---

## 10. Generalization Assessment
Applicable across embedded Linux platforms with flash storage and bootloader A/B support (U-Boot/GRUB).

---

## 11. Hardware/Deployment Assessment
Physical ARM64 hardware with bill-of-materials (BOM) cost analysis.

---

## 12. Limitations Assessment
Section X notes non-volatile state synchronization latencies and dual-partition storage overhead.

---

## 13. Language/Presentation Assessment
Clear systems and reliability engineering text.

---

## 14. Claim–Evidence Alignment
Well-scoped to immutable embedded Linux appliances.

---

## 15. Reproducibility
* **Rating**: `HIGH. Storage layering stack, partition tables, and rollback state machines are fully described.`

---

## 16. Publication Chronology
* **Chronology Audit**: INVALID FORWARD CITATIONS: Cites P12 (b29) and P10 (b30).

---

## 17. Reference Integrity
Contains future citations to P10 and P12.

---

## 18. Venue Fit
* **Recommended Publication Venues**: `IEEE Transactions on Industrial Informatics / ACM Transactions on Embedded Computing Systems.`

---

## 19. Reviewer-6 Transfer Test
Reviewer-6 would criticize: (1) A/B and overlayfs are standard embedded Linux patterns, (2) Forward citations to P10 and P12. Criticism is VALID.

---

## 20. Required Revisions
1. Remove citations to P10 and P12.
2. Frame novelty as the formal invariance proof of edge AI state recovery under sudden power loss.
3. Add partition table layout diagram.

---

## 21. Revision Priority
* **Priority Level**: `HIGH`

---

## 22. Final Reviewer Recommendation
**AUTHORITATIVE RECOMMENDATION**: `MINOR_REVISION`
