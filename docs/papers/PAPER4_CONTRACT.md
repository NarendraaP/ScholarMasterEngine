# PAPER 4 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Spatiotemporal Adherence Evaluation System Using Constraint Satisfaction Programming |
| **Paper ID** | P4 |
| **Layer** | Reasoning (L4 — Compliance Logic) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A Constraint Evaluation Framework (CEF) that models campus regulations as Constraint Satisfaction Problems (CSPs), fusing real-time vision detections with schedule repositories to evaluate spatiotemporal alignment of student presence.**

Paper 4 formalizes the compliance-checking logic: given a detected identity at location $L$ and time $T$, does this satisfy the institutional schedule constraints?

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Campus regulations can be modeled as CSP variables with temporal and spatial domains | Formal CSP formulation (§III) | Clean |
| C2 | The "Teleportation Heuristic" filters physically impossible detections (same student at two locations within Δt) | Algorithm description (§IV) | Clean |
| C3 | PCVF (Privacy-Compliant Validation Filter) ensures only schedule-relevant events propagate | Architecture (§V) | Clean |
| C4 | PostgreSQL-backed production deployment supports institutional-scale constraint checking | Proposed deployment strategy (§VII) | Clean — framed as proposed, not validated |

## 4. Scope

### 4.1 In-Scope
- CSP formulation of schedule constraints (time, location, role)
- Data fusion: vision detections × schedule repository
- Teleportation Heuristic for false-positive rejection
- PCVF for privacy-compliant event filtering
- Production deployment proposal (PostgreSQL)

### 4.2 Out-of-Scope
- Identity retrieval (Paper 1)
- Privacy enforcement at sensing layer (Paper 3)
- Schedule rule definition language (Paper 7 extends this)
- Trust/audit logging (Paper 8)
- System-level integration testing (Paper 10)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P4-INV-01 | Compliance decisions MUST be deterministic given the same (identity, location, time) tuple | CSP solver is stateless per-query |
| P4-INV-02 | Events failing the Teleportation Heuristic MUST be rejected before reaching downstream | Pre-filter gate in data fusion layer |
| P4-INV-03 | Only schedule-relevant metadata SHALL propagate beyond the PCVF boundary | PCVF strips non-compliant fields |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P1 (Identity) | Identity vector for person-location binding |
| **Upstream** | P3 (Pose) | Presence signal (anonymized) |
| **Upstream** | P7 (Schedule Rules) | CSP constraint definitions |
| **Downstream** | P2 (Engagement) | Schedule context for engagement fusion |
| **Downstream** | P8 (Provenance) | Compliance events logged to trust layer |
| **Downstream** | P9 (Orchestrator) | Compliance events published to orchestration bus |

## 7. Verification Requirements

- CSP solver produces correct compliance label for all test scenarios in schedule matrix
- Teleportation Heuristic correctly rejects ≥ 99% of physically impossible detections
- PCVF strips all non-schedule metadata before downstream emission
- Decision latency < 5 ms per constraint evaluation

## 8. What This Paper Does NOT Do

- Does **not** detect or track individuals (defers to Paper 1)
- Does **not** enforce privacy at the sensing boundary (defers to Paper 3)
- Does **not** define rule syntax or reasoning formalism (extended in Paper 7)
- Does **not** provide audit/trust claims (defers to Paper 8)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Constraint Solver** | `modules_legacy/context_manager.py` | ✅ Verified (Spatial & Temporal Checks) |
| **PCVF Filter** | `modules_legacy/context_manager.py` | ✅ Verified (`check_compliance` filters metadata) |
| **Deployment** | `modules_legacy/master_engine.py` | ✅ Verified (Integration with Orchestrator) |

