# SCHOLARMASTER RESEARCH PORTFOLIO GOVERNANCE ENGINE — ARCHITECTURE

## System Overview & Component Interactions

The **ScholarMaster Research Portfolio Governance Engine** is an extensible, source-driven governance and lifecycle management automation layer designed to manage multi-paper research agendas from inception to peer-reviewed publication.

```text
+-----------------------------------------------------------------------------------+
|                            RESEARCH PORTFOLIO GOVERNANCE ENGINE                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|  |  paper_registry.json  | <-> | publication_events    | <-> | citation_graph  |  |
|  |  (Canonical DB)       |     | (Append-Only Log)     |     | (Directed DAG)  |  |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|              ^                             ^                          ^           |
|              |                             |                          |           |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|  | citation_eligibility  |     | publication_          |     | portfolio_      |  |
|  | (Chronology Rule)     |     | propagation           |     | consistency     |  |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|              ^                             ^                          ^           |
|              |                             |                          |           |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|  | evidence_registry     |     | novelty_registry      |     | venue_registry  |  |
|  | & claim_registry      |     | (Reviewer-6 Pillar 1) |     | & revisions     |  |
|  +-----------------------+     +-----------------------+     +-----------------+  |
|                                            |                                      |
|                                            v                                      |
|                               +-------------------------+                         |
|                               | generator.py            |                         |
|                               | (Master Plan LaTeX Gen) |                         |
|                               +-------------------------+                         |
|                                            |                                      |
|                                            v                                      |
|                               SCHOLARMASTER_MASTER_PLAN                           |
+-----------------------------------------------------------------------------------+
```

---

## Core Components

### 1. Canonical Paper Registry (`paper_registry.json`)
Stores authoritative metadata for all papers in the portfolio (`P01` to `P25`, and future additions `P26+`). 
Crucially separates:
- `research_plan_order` (conceptual sequence)
- `submission_order` (planned submission batches)
- `acceptance_order` (formal acceptance sequence)
- `publication_order` (public appearance date)

### 2. Publication Event Log (`publication_events.json`)
Append-only log recording every status transition with explicit verification provenance (`date`, `venue`, `doi`, `source`, `verified`).

### 3. Citation Eligibility Engine (`citation_eligibility.py`)
Enforces the fundamental scientific rule:
$$\text{Eligible}(P_A \to P_B) \iff \text{Status}(P_B) \in \{\text{PUBLISHED}, \text{ACCEPTED/IN\_PRESS}\} \land \text{Date}(P_A) \ge \text{Date}(P_B)$$

### 4. Publication State Propagation Engine (`publication_propagation.py`)
When a paper transitions state (e.g. $P_B \to \text{PUBLISHED}$):
1. Updates $P_B$'s state in the registry.
2. Appends an event to the log.
3. Recalculates portfolio-wide citation eligibility.
4. Identifies manuscripts that were previously blocked from citing $P_B$.
5. Applies an independent **Scientific Relevance Gate** ($\text{Relevance}(P_B, P_A) \in \{\text{HIGH}, \text{MEDIUM}, \text{LOW}\}$).
6. Generates `citation_opportunities.json` with `automatic_insertion = false`.

### 5. Evidence & Claim Registries (`evidence_registry.json`, `claim_registry.json`)
Maintains strict provenance linking every numerical and theoretical claim to verified evidence classes (`PHYSICAL_MEASUREMENT`, `SIMULATION`, `ANALYTICAL_DERIVATION`, `USER_STUDY`).

### 6. Novelty & Reviewer Calibration (`novelty_registry.json`, `reviewer_calibration.json`)
Operationalizes the 4 Reviewer-6 Skepticism Pillars (Novelty beyond known tools, Environmental breadth, Professional language, and Limitations disclosure).

### 7. Portfolio Consistency Engine (`portfolio_consistency.py`)
Automated audit verifying multi-paper structural invariants, zero chronology violations, and claim-evidence completeness.

### 8. Master Plan Generator (`generator.py`)
Synthesizes `SCHOLARMASTER_MASTER_PAPER_PLAN.tex` dynamically from canonical registries without hardcoded paper profiles.
