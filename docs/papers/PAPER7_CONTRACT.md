# PAPER 7 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Spatiotemporal Rule-Based Reasoning for Academic Schedule Compliance Using Constraint Satisfaction Programming |
| **Paper ID** | P7 |
| **Layer** | Reasoning (L4 — Schedule Rules) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A formal rule-based reasoning engine that extends Paper 4's Constraint Evaluation Framework with a declarative rule language for expressing complex academic schedule constraints — including temporal intervals, role-based access, and exception handling.**

Paper 7 provides the rule-definition substrate consumed by Paper 4's runtime constraint solver. Where Paper 4 evaluates constraints, Paper 7 defines the language and semantics for expressing them.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Academic schedule rules can be expressed as typed CSPs with temporal, spatial, and role domains | Formal grammar (§III) | Clean |
| C2 | Rule composition supports exception handling (holidays, substitutions, room changes) | Exception algebra (§IV) | Clean |
| C3 | Pseudonymized identifiers are used throughout — no real names in constraint evaluation | Architecture (§III) | Clean — "pseudonymized," not "anonymized" |
| C4 | Rule engine integrates with schedule repositories (CSV/database) for institutional deployment | Integration API (§VI) | Clean |

## 4. Scope

### 4.1 In-Scope
- Declarative rule language for schedule constraints
- Temporal interval reasoning (overlaps, gaps, sequences)
- Role-based constraint binding (student, faculty, staff)
- Exception handling (holidays, substitutions)
- Integration API for schedule repositories

### 4.2 Out-of-Scope
- Runtime constraint evaluation (Paper 4 — P7 defines rules, P4 evaluates them)
- Identity retrieval (Paper 1)
- Privacy enforcement (Paper 3)
- Trust/audit (Paper 8)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P7-INV-01 | Rule definitions MUST be deterministic — same rule + same input = same constraint set | Declarative formulation; no side effects |
| P7-INV-02 | All identity references in rules MUST use pseudonymized identifiers | Identifiers are opaque tokens, not names |
| P7-INV-03 | Exception rules MUST NOT weaken base compliance constraints, only provide authorized overrides | Exception algebra enforces monotonic relaxation |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | Institutional schedule data | CSV/database schedule repository |
| **Downstream** | P4 (Compliance) | Constraint definitions consumed by CSP solver |
| **Downstream** | P2 (Engagement) | Schedule context (exam/lecture/break) |
| **Downstream** | P9 (Orchestrator) | Rule updates propagated via orchestration bus |

## 7. Verification Requirements

- All test schedule configurations produce correct CSP variable assignments
- Exception rules correctly override base rules without side effects
- Rule parsing completes in < 100 ms for institutional-scale rule sets (1000+ rules)
- Pseudonymized identifiers verified — no real names in any rule output

## 8. What This Paper Does NOT Do

- Does **not** evaluate constraints at runtime (defers to Paper 4)
- Does **not** retrieve or track identities (defers to Paper 1)
- Does **not** enforce privacy at sensing boundary (defers to Paper 3)
- Does **not** log compliance events to trust layer (defers to Paper 8)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **CSP Solver** | `modules_legacy/st_csf.py` | ✅ Verified (OR-Tools Logic) |
| **Conflict Matrix** | `modules_legacy/st_csf.py` | ✅ Verified (Weighted Voting Algorithm 2) |
| **Logic Layer** | `modules_legacy/st_csf.py` | ✅ Verified (Decoupled Validator) |

