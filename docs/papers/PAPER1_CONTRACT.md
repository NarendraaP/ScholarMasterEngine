# PAPER 1 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Sub-Millisecond Open-Set Biometric Retrieval at 100K Scale via HNSW on Edge Hardware |
| **Paper ID** | P1 |
| **Layer** | Biometric Identity Retrieval Layer |
| **Author** | Polisetti Narendra |
| **Status** | Initialized |

## 2. Primary Contribution

**A highly optimized, graph-based approximate nearest neighbor (ANN) retrieval module utilizing HNSW and a Local Density Consistency Criterion (LDCC), demonstrating that biometric identification at institutional scale (100K identities) can be executed in under 1ms locally on edge hardware.**

Paper 1 provides the high-throughput identity resolution capability necessary to anchor temporal behaviors (which are processed by higher layers) to specific individuals without incurring cloud latency or sending biometric vectors over the network.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Brute-force cosine similarity fails to meet real-time streaming constraints at 100K gallery scale. | Table 2 (Linear Search = 55.0 ms, budget = 5ms) | Clean |
| C2 | HNSW maintains sub-millisecond latency (0.419 ms) with logarithmic scaling up to 100K. | Table 1 | Clean |
| C3 | Local Density Consistency Criterion (LDCC) combined with HNSW achieves 99.8% unknown rejection under open-set stress. | Table 2 | Clean |
| C4 | Local execution prevents external network transmission of biometric probe vectors. | Architecture / Section VII | Clean |

## 4. Scope

### 4.1 In-Scope
- ArcFace embedding geometry and margin penalties.
- HNSW index construction and search complexity.
- Local Density Consistency Criterion (LDCC) gating logic.
- Benchmarking of *retrieval* latency and open-set identification accuracy.

### 4.2 Out-of-Scope (Strictly Forbidden)
- **General ML / Deep Learning Modeling** (Owned by P13 - P1 uses pre-trained ArcFace/ResNet backbones and does not claim novel CNN architectures).
- **System Architecture / Middleware Orchestration** (Owned by P18 - P1 only governs the identity retrieval algorithm pipeline, not the message broker).
- **Hardware Architecture & Cache Limits** (Owned by P5 - P1 executes *on* unified memory but does not theoretically model memory bandwidth ceilings).
- **Formal Privacy/Cryptographic Proofs** (Owned by P8 - P1's privacy claim is restricted to "no external transmission" via local processing).
- **System-Wide End-to-End Validation** (Owned by P10 - P1 evaluates only the identity retrieval throughput).

## 5. Potential Overlap Risks (Pending Audit)

- **ML Training (P13):** Must ensure P1 explicitly frames ResNet/ArcFace as foundational utilities rather than its core contribution.
- **Hardware (P5):** P1 mentions FP16 quantization and unified memory. These must remain practical execution details, not theoretical hardware modeling.

## 6. What This Paper Does NOT Do

- Does **not** track students over time or monitor engagement (P3/P2).
- Does **not** evaluate spatiotemporal compliance rules (P4/P21).
- Does **not** design the edge hardware (P5).
