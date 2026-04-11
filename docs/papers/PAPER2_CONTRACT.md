# PAPER 2 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | A Context-Aware Multi-Modal Framework for Reducing False Negatives in Student Engagement Analysis |
| **Paper ID** | P2 |
| **Layer** | Reasoning (L4 — Engagement Logic) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**An interpretable logic layer that fuses visual, schedule, and acoustic signals to reduce Type-II errors (false negatives) in engagement classification — specifically, misclassifying high cognitive load as disengagement.**

Paper 2 addresses the "deep thought looks like sleeping" problem by introducing context-aware fusion rules that cross-reference pose data with schedule context and acoustic environment before issuing a disengagement label.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Baseline vision-only engagement classifiers exhibit 22% false-negative rate under high-cognitive-load scenarios | Controlled experiment (§IV) | Clean |
| C2 | Context-aware fusion reduces FN rate to 4.3% — a 79% relative improvement | Comparative results (Table III) | Clean |
| C3 | Schedule cross-referencing (exam period flag) prevents 68% of misclassifications | Ablation study (§V) | Clean |
| C4 | Acoustic ambient signal (quiet classroom = focused, not sleeping) provides complementary cue | Feature importance analysis (§V) | Clean |

## 4. Scope

### 4.1 In-Scope
- Multimodal fusion logic (visual pose + schedule context + acoustic level)
- Type-II error (false negative) reduction in engagement classification
- Interpretable rule-based reasoning (not black-box ML)
- Integration point with schedule repository (Paper 4/7)

### 4.2 Out-of-Scope
- Identity retrieval (Paper 1)
- Privacy enforcement or raw data handling (Paper 3, Paper 17)
- Acoustic anomaly detection (Paper 6 — Paper 2 uses ambient level, not event detection)
- Compliance rule enforcement (Paper 4, Paper 7)
- Federated model retraining (Paper 13)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P2-INV-01 | Engagement labels MUST NOT be derived from identity — only from posture/context signals | Architecture: identity vector not input to engagement classifier |
| P2-INV-02 | No engagement label shall be emitted without schedule-context cross-reference | Fusion gate requires schedule lookup before label output |
| P2-INV-03 | Buffer deallocated after inference — no raw frame persistence | RAII pattern; volatile memory only |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P1 (Identity) | Identity vector provides frame association (not used for classification) |
| **Upstream** | P3 (Pose) | Skeletal pose vector is primary visual input |
| **Upstream** | P6 (Acoustic) | Ambient acoustic level as context signal |
| **Upstream** | P7 (Schedule) | Schedule context (exam/lecture/break) as fusion input |
| **Downstream** | P9 (Orchestrator) | Engagement events published to orchestration bus |
| **Downstream** | P10 (Validation) | Engagement module exercised under system stress test |

## 7. Verification Requirements

- FN rate ≤ 5% under high-cognitive-load test scenarios
- No identity data leakage into engagement classification pathway
- Engagement labels correlate with schedule context (exam → higher tolerance)
- Latency < 33 ms for fusion decision per frame

## 8. What This Paper Does NOT Do

- Does **not** perform identity recognition or biometric retrieval
- Does **not** make privacy claims (defers to Paper 3/17)
- Does **not** detect acoustic anomalies (uses only ambient level from Paper 6)
- Does **not** enforce schedule compliance rules (defers to Paper 4/7)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Fusion Logic** | `modules_legacy/master_engine.py` | ✅ Verified (Fusion Gate at Step 0.5 & 3) |
| **Context Engine** | `modules_legacy/context_manager.py` | ✅ Verified (Schedule Lookup) |
| **Acoustic Context** | `modules_legacy/audio_sentinel.py` | ✅ Verified (Ambient Level Input) |

