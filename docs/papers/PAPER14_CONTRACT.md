# PAPER 14 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Cross-Campus Federated Intelligence: Hierarchical Privacy-Preserving Learning for Distributed Academic Institutions |
| **Paper ID** | P14 |
| **Layer** | Adaptation (L10 — Cross-Campus Federation) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A hierarchical three-tier federated learning architecture (Classroom → Campus → Global) that enables cross-institutional model improvement while respecting institutional governance boundaries, heterogeneous environments, and privacy budgets — with hierarchical Differential Privacy composing across aggregation tiers.**

Paper 14 extends Paper 13's intra-campus FL to the inter-institutional scope, introducing governance and staleness protocols for asynchronous multi-campus collaboration.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Three-tier hierarchical FedAvg converges within 5% of centralized accuracy while maintaining DP bounds | Convergence analysis (§X) | Clean |
| C2 | Staleness-aware aggregation (exponential decay weighting) tolerates campus connectivity gaps of up to 72 hours | Staleness protocol (§IV); robustness analysis | Clean |
| C3 | Hierarchical DP composition (ε_campus=4.0, ε_global=2.0) provides tighter bounds than flat aggregation | Privacy analysis (§V) | Clean — "GDPR alignment," not "compliance" |
| C4 | Governance layer enables per-institution opt-in/opt-out and contribution auditing | Governance protocol (§VII) | Clean |
| C5 | Cross-campus FL reduces per-institution training cost by 89% vs independent retraining | Cost analysis (§X) | Clean |

## 4. Scope

### 4.1 In-Scope
- Three-tier hierarchical FedAvg (Classroom → Campus → Global)
- Staleness-aware asynchronous aggregation
- Hierarchical Differential Privacy with budget composition
- Cross-institutional governance layer (IRB-compatible)
- Communication infrastructure (MQTT federation)
- Security analysis (Sybil resistance, model poisoning defense)

### 4.2 Out-of-Scope
- Intra-campus drift compensation (Paper 13)
- Base model design (Papers 1–3)
- Production deployment (Paper 11)
- System-level validation (Paper 10)
- AR visualization (Paper 15)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P14-INV-01 | Raw data MUST NOT leave institutional boundaries — only aggregated gradients | Protocol: no raw data serializer at campus gateway |
| P14-INV-02 | Each aggregation tier MUST apply independent DP noise | Hierarchical DP mechanism with per-tier moments accountant |
| P14-INV-03 | Stale updates (>72h) MUST be exponentially down-weighted, not discarded | Staleness decay function applied at aggregation |
| P14-INV-04 | Institutions MUST be able to opt out of federation without affecting local model | Governance: opt-out preserves last-known campus model |
| P14-INV-05 | "Reducing risk of reconstruction" — hierarchical DP reduces but does not eliminate reconstruction risk | Scoped privacy claim |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P13 (Intra-Campus FL) | Campus-level aggregated models as input to global tier |
| **Upstream** | P11 (MLOps) | OTA pipeline delivers globally-updated models |
| **Upstream** | P8 (Trust) | Audit logs for cross-campus governance |
| **Downstream** | P1–P3 (Perception) | Globally-improved models deployed to perception modules |
| **Downstream** | P10 (Validation) | Cross-campus models validated under system stress |

## 7. Verification Requirements

- Global model accuracy within 5% of centralized baseline after 50 rounds
- Hierarchical DP budget tracked correctly per tier (ε_campus, ε_global)
- Staleness decay correctly weights 72-hour-stale updates
- Opt-out leaves local campus model unchanged
- Zero raw data in any cross-campus communication channel

## 8. What This Paper Does NOT Do

- Does **not** handle intra-campus temporal drift (defers to Paper 13)
- Does **not** claim GDPR compliance — provides "GDPR-aligned technical architecture"
- Does **not** prevent all reconstruction attacks — "reduces risk"
- Does **not** validate results on more than 3 simulated campus environments

## 9. Key Distinction: P14 vs P13

| Dimension | P14 (This Paper) | P13 |
|---|---|---|
| **Scope** | Multiple campuses | Single campus |
| **Problem** | Cross-environment heterogeneity | Temporal drift |
| **Aggregation** | Hierarchical (3-tier) | Flat FedAvg |
| **Governance** | Cross-institutional layer | Single institution |
| **Relationship** | Aggregates P13 campus outputs | Feeds into P14's hierarchical aggregation |

## 10. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Multi-Campus Sim** | `benchmarks/paper14_end_to_end_simulation.py` | ✅ Verified (5-Campus Topology) |
| **Hierarchical Agg** | `modules/h_fedavg_coordinator.py` | ✅ Verified (Tier 3 Coordinator) |
| **Campus Node** | `modules/campus_aggregator.py` | ✅ Verified (Tier 2 Aggregator) |

