# PAPER 7 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Sub-Millisecond Identity Retrieval via HNSW + LDCC |
| **Paper ID** | P7 |
| **Layer** | Execution / Retrieval Layer |
| **Author** | Polisetti Narendra |
| **Status** | Re-classified / Boundary Enforced |

## 2. Primary Contribution

**A highly optimized, graph-based approximate nearest neighbor (ANN) retrieval module utilizing HNSW and a Local Density Consistency Criterion (LDCC), demonstrating that biometric identification at institutional scale (100K identities) can be executed in under 1ms locally on edge hardware.**

Paper 7 provides the high-throughput identity resolution execution layer. It relies on embeddings provided by upstream layers (P13/P3) and focuses strictly on the logarithmic execution speed required to anchor temporal behaviors to specific individuals without incurring cloud latency.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Brute-force cosine similarity fails to meet real-time streaming constraints at 100K gallery scale. | Table 2 (Linear Search = 55.0 ms, budget = 5ms) | Clean |
| C2 | HNSW maintains sub-millisecond latency (0.419 ms) with logarithmic scaling up to 100K. | Table 1 | Clean |
| C3 | Local Density Consistency Criterion (LDCC) combined with HNSW achieves 99.8% unknown rejection under open-set stress. | Table 2 | Clean |
| C4 | Local execution avoids network transmission of biometric probe vectors during retrieval. | Architecture / Section VII | Clean |

## 4. Scope

### 4.1 In-Scope
- HNSW index construction and search complexity.
- Local Density Consistency Criterion (LDCC) gating logic.
- Benchmarking of *retrieval* latency and open-set identification accuracy.
- Execution speed constraints on edge devices.

### 4.2 Out-of-Scope (Strictly Forbidden)
- **General ML / Deep Learning Modeling** (Owned by P13 - P7 explicitly assumes ArcFace/YOLO is provided externally).
- **System Architecture / Middleware Orchestration** (Owned by P18 - P7 only governs the identity retrieval algorithm segment, not the full pipeline).
- **Hardware Architecture & Cache Limits** (Owned by P5 - P7 executes *on* hardware but does not theoretically model memory bandwidth ceilings).
- **Formal Privacy/Cryptographic Proofs** (Owned by P8 - P7's privacy claim is restricted to "local execution avoids transmission").
- **System Synthesis / Master Vision** (Owned by P1 - P7 is strictly an execution module).

## 5. What This Paper Does NOT Do

- Does **not** represent the "Full System" or synthesize the 21 papers (P1).
- Does **not** track students over time or monitor engagement (P3/P2).
- Does **not** evaluate spatiotemporal compliance rules (P4/P21).
- Does **not** design the edge hardware (P5).
