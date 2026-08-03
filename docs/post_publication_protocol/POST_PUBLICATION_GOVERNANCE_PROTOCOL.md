# SCHOLARMASTER POST-PUBLICATION GOVERNANCE & REGISTRY UPDATE PROTOCOL
## Canonical Recommendations for Updating SROS Registries, Knowledge Graph, CCLM & Board Records Post-Acceptance

**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SROS-010 Publication Policy`  
**Policy Rule:** **DO NOT EXECUTE AUTOMATICALLY.** All recommendations must be presented to the ScholarMaster Program Board (SPB) for formal approval before updating database files or SROS registries.

---

## 1. POST-PUBLICATION UPDATE WORKFLOW

When an individual paper (e.g., `P3`, `P4`, `P7`, `P11`, `P18`, or `P1`) is officially accepted and assigned a Digital Object Identifier (DOI):

```
[Paper Acceptance & DOI Issuance] ➔ [Generate Registry Update Recommendations] ➔
[Submit to SPB for Class B Approval] ➔ [Execute Controlled Registry Updates] ➔
[Propagate DOI Citations to Downstream Papers]
```

---

## 2. COMPREHENSIVE REGISTRY UPDATE RECOMMENDATIONS

### 2.1 SROS Publication Registry (`SROS-010`) Recommendations
- **Action:** Transition paper state from `UNDER_REVIEW` to `PUBLISHED`.
- **Target Fields:**
  - `doi`: Insert official DOI string (e.g., `10.1109/TIFS.2026.XXXXXXX`).
  - `publication_date`: Record formal online publication timestamp.
  - `venue`: Confirm final journal volume, issue, and page numbers.
  - `pdf_archive_path`: Deposit compiled final PDF in `docs/papers/published_archives/`.

### 2.2 SROS Paper Registry (`SROS-004`) Recommendations
- **Action:** Lock paper contract and enable downstream inheritance.
- **Target Fields:**
  - `contract_status`: Shift from `DRAFT_CONTRACT` to `LOCKED_CANONICAL`.
  - `downstream_inheritance_enabled`: Set to `TRUE`.
  - `canonical_citation`: Update BibTeX entry across all dependent papers.

### 2.3 Knowledge Graph (`SROS-013`) Recommendations
- **Action:** Update node status in the ScholarMaster Master Knowledge Graph.
- **Target Nodes:**
  - Update paper node from `PROPOSED_NODE` to `RATIFIED_KNOWLEDGE_NODE`.
  - Add explicit directed edges linking the published paper DOI to its implementing codebase classes in `core/canonical_layers.py`.

### 2.4 Cross-Claim Lineage Matrix (CCLM) Recommendations
- **Action:** Verify unbroken lineage between accepted claims and repository modules.
- **Target Verification:**
  - Confirm that the published DOI is bound to the exact Git commit hash (e.g., `4416cb6` or latest tag).
  - Update CCLM audit log to mark claims as `OFFICIALLY_PEER_REVIEWED_AND_VERIFIED`.

### 2.5 Decision Log (`SROS-000` / SPB Records) Recommendations
- **Action:** Record formal SPB Ratification Resolution.
- **Target Format:**
  ```markdown
  RESOLUTION ID : SPB-RES-2026-P[X]-ACCEPTED
  PAPER ID      : P[X] ([PAPER_TITLE])
  DOI           : 10.1109/[VENUE].2026.[DOI]
  ACTION        : Officially ratified and locked into SROS 2.1 ecosystem lineage.
  VOTE          : SPB Class B Supermajority (Passed 100%)
  ```

### 2.6 Program Board (SPB) Master Dashboard Recommendations
- **Action:** Update the Standing Executive Master Dashboard.
- **Target KPI:** Increment `Published Papers Count` and update Ecosystem Phasing progress from `Phase 1 (Foundations)` to next phase.

---

## 3. STRICT NON-AUTOMATION MANDATE

> [!CAUTION]
> **NO AUTOMATIC SCRIPT EXECUTION IS PERMITTED.**
> All post-publication updates MUST be presented to the user / SPB as explicit recommendations.
> Registry files (`docs/governance/`, `SROS-000` to `SROS-015`) may only be modified after receiving explicit user approval (`"approved"`).
