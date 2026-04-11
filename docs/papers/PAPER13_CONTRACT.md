# PAPER 13 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Privacy-Preserving Federated Learning for Model Drift Compensation in Educational Edge AI |
| **Paper ID** | P13 |
| **Layer** | Adaptation (L9 — Intra-Campus Federated Learning) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**An intra-campus federated learning framework that compensates for temporal model drift (lighting changes, seasonal variation, furniture rearrangement) across edge nodes within a single institution — using Federated Averaging with user-level Differential Privacy and active learning to maintain model accuracy without centralizing sensitive data.**

Paper 13 operates at the **single-campus** scope, focusing on temporal drift compensation. This is distinct from Paper 14, which addresses cross-campus collaboration at the inter-institutional scope.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Temporal drift causes 12–18% accuracy degradation over 90 days without retraining | Drift measurement study (§VII) | Clean |
| C2 | Federated Averaging with DP (ε=8.0) restores accuracy to within 2% of centrally retrained baseline | FL training results (§VIII) | Clean |
| C3 | Active learning reduces labeling requirements by 67% for drift compensation | Active learning ablation (§VIII) | Clean |
| C4 | User-level DP provides structural boundedness for gradient privacy — GDPR-aligned, not GDPR-compliant | DP analysis (§V) | Clean — "providing structural boundedness" and "GDPR alignment" |
| C5 | Federated approach costs 82% less than cloud-based centralized retraining | Cost analysis (§VIII) | Clean |

## 4. Scope

### 4.1 In-Scope
- Temporal model drift detection and measurement
- Federated Averaging (FedAvg) for intra-campus model update
- User-level Differential Privacy (ε=8.0, δ=10⁻⁵)
- Active learning for efficient labeling
- Single-institution deployment scenario
- Cost comparison vs centralized retraining

### 4.2 Out-of-Scope
- Cross-campus/inter-institutional federation (Paper 14)
- Hierarchical aggregation across institutions (Paper 14)
- Governance of cross-institutional data sharing (Paper 14)
- Base model design or architecture (Papers 1–3)
- Production deployment pipeline (Paper 11)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P13-INV-01 | Raw training data MUST remain on-device — only gradient updates are shared | FedAvg protocol; no raw data in aggregation channel |
| P13-INV-02 | All gradient updates MUST be clipped and noised per DP mechanism | TensorFlow Privacy DP-SGD; enforced in training loop |
| P13-INV-03 | Privacy budget (ε) MUST be tracked cumulatively across rounds | Moments accountant tracks cumulative ε |
| P13-INV-04 | Active learning queries MUST NOT expose raw images — only model uncertainty scores | Query interface returns only confidence scores |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P1–P3 (Perception) | Base models requiring drift compensation |
| **Upstream** | P11 (MLOps) | OTA pipeline delivers updated models to nodes |
| **Upstream** | P9 (Orchestrator) | FL coordination events on orchestration bus |
| **Downstream** | P14 (Cross-Campus FL) | P13's campus-level model feeds into P14's hierarchical aggregation |
| **Downstream** | P10 (Validation) | Drift-compensated models validated under system stress |

## 7. Verification Requirements

- Drift-compensated model accuracy within 3% of centralized baseline
- DP mechanism verified: gradient noise matches theoretical ε=8.0
- Cumulative privacy budget tracked correctly across training rounds
- Zero raw training data present in aggregation channel (network audit)
- Active learning reduces labeling by ≥ 60% vs random sampling

## 8. What This Paper Does NOT Do

- Does **not** operate across institutional boundaries (defers to Paper 14)
- Does **not** claim GDPR compliance — provides "GDPR-aligned structural controls"
- Does **not** design new FL algorithms — applies FedAvg + DP to the drift problem
- Does **not** address base model architecture (defers to Papers 1–3)

## 9. Key Distinction: P13 vs P14

| Dimension | P13 (This Paper) | P14 |
|---|---|---|
| **Scope** | Single campus | Multiple campuses |
| **Problem** | Temporal drift | Cross-environment heterogeneity |
| **Aggregation** | Flat FedAvg | Hierarchical (3-tier) |
| **Governance** | Single institutional IRB | Cross-institutional governance layer |
| **Relationship** | P13 produces campus-level models | P14 aggregates P13 outputs across institutions |

## 10. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Drift Sim** | `benchmarks/paper13_validation.py` | ✅ Verified (Temporal Drift Injection) |
| **FedAvg Logic** | `benchmarks/paper13_validation.py` | ✅ Verified (Weighted Averaging) |
| **DP Noise** | `benchmarks/paper13_validation.py` | ✅ Verified (Gradient Clipping & Noise) |

