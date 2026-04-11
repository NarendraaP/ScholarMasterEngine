# PAPER 3 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Privacy-Preserving Academic Participation Sensing via Pose-Only Architectural Irreversibility |
| **Paper ID** | P3 |
| **Layer** | Perception (L3 — Privacy Abstraction) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A pose-only processing pipeline that enforces Architectural Irreversibility — raw pixel data is destroyed immediately after skeletal extraction, ensuring biometric features cannot propagate beyond the volatile memory boundary.**

Paper 3 defines the privacy-enforcement primitive for the ScholarMaster perception layer. It extracts anonymous skeletal vector maps from video frames and discards all raw pixel data before any downstream processing occurs.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Raw pixel buffers are deallocated immediately after pose extraction — no persistence to disk | Architecture description (§III); RAII pattern | Clean |
| C2 | Skeletal vectors are structurally insufficient for facial reconstruction under the stated threat model | Information-theoretic analysis (§IV) | Clean — scoped to "structurally underdetermined," not "mathematically impossible" |
| C3 | Pose-only representation preserves sufficient engagement signal (posture, hand-raise, head-tilt) | Feature-utility analysis (§V) | Clean |
| C4 | Identity reconstruction from skeletal data alone is structurally underdetermined | Degrees-of-freedom analysis (§IV) | Clean — gait-based re-identification caveat acknowledged |

## 4. Scope

### 4.1 In-Scope
- Pose estimation pipeline (MediaPipe / lightweight detector)
- Volatile memory confinement of raw frames
- Skeletal vector extraction and representation
- Privacy analysis: reconstruction infeasibility under stated threat model
- Gait re-identification caveat and limitations

### 4.2 Out-of-Scope
- Identity retrieval (Paper 1)
- Engagement classification logic (Paper 2)
- Formal privacy proofs or DP bounds (Paper 13)
- Architectural irreversibility formalization across full system (Paper 17)
- Runtime verification of irreversibility claims (Paper 18)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P3-INV-01 | Raw pixel buffers MUST be destroyed before any downstream module receives data | RAII deallocation; volatile-only allocation |
| P3-INV-02 | No raw frame SHALL be written to non-volatile storage at any point | Architecture: no disk-write path exists for pixel buffers |
| P3-INV-03 | Skeletal vectors MUST NOT contain sufficient information for facial reconstruction | Representation limited to joint coordinates (17–33 keypoints) |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | Camera input | Raw video frames (consumed and destroyed) |
| **Downstream** | P2 (Engagement) | Skeletal pose vector as engagement input |
| **Downstream** | P4 (Compliance) | Anonymized presence signal |
| **Downstream** | P9 (Orchestrator) | Privacy-safe pose events on orchestration bus |
| **Downstream** | P17 (Irreversibility) | P3 implements the edge-level irreversibility that P17 formalizes system-wide |
| **Downstream** | P18 (Verification) | P18 runtime-verifies P3's volatile-memory claims |

## 7. Verification Requirements

- Zero raw pixel data recoverable from heap post-extraction (`gcore` forensic test)
- Skeletal output contains only joint coordinates — no texture, color, or facial features
- Pose-based engagement signal maintains ≥ 90% correlation with ground-truth labels
- End-to-end volatile confinement validated under continuous operation (Paper 10 stress test)

## 8. What This Paper Does NOT Do

- Does **not** claim reconstruction is "mathematically impossible" — uses "structurally underdetermined"
- Does **not** defend against gait-based re-identification (acknowledged limitation)
- Does **not** provide formal differential privacy bounds (defers to Paper 13)
- Does **not** formalize irreversibility across the full architecture (defers to Paper 17)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Anonymous Visualization** | `privacy_pose.py` | ✅ Verified (Black background, Skeleton only) |
| **Volatile Processing** | `modules_legacy/master_engine.py` | ✅ Verified (`del frame` at end of cycle) |
| **Pose Logic** | `modules_legacy/master_engine.py` | ✅ Verified (YOLOv8-Pose Integration) |

