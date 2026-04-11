# PAPER 1 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Scalable High-Throughput Biometric Identification Using Hierarchical Navigable Small World Indexing on Edge Devices |
| **Paper ID** | P1 |
| **Layer** | Perception (L2 — Biometric Retrieval) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**Sub-millisecond open-set biometric retrieval at institutional scale (100K+ identities) on edge hardware via HNSW indexing over ArcFace embeddings.**

Paper 1 establishes the core identity-retrieval primitive consumed by all downstream modules. It replaces linear search ($O(N)$) with HNSW graph traversal ($O(\log N)$), enabling real-time biometric lookup within the 33 ms frame budget on UMA-class hardware.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | HNSW retrieval completes in <1 ms for $N=100\text{K}$ on UMA hardware | Latency benchmarks (Table II) | Clean |
| C2 | 99.82% open-set retrieval correctness under 20% unknown injection | Stress-test protocol (§IV) | Clean — scoped as synthetic retrieval correctness, not biometric recognition accuracy |
| C3 | ArcFace 512-d embeddings provide sufficient discriminative power at cosine threshold $\tau=0.6$ | ROC analysis (§V) | Clean |
| C4 | Ephemeral memory design — raw pixel data confined to volatile buffer, discarded after vectorization | Architecture description (§III) | Clean — privacy-compatible, not privacy-native |

## 4. Scope

### 4.1 In-Scope
- HNSW index construction, tuning (`efConstruction`, `efSearch`, `M`)
- ArcFace embedding extraction pipeline
- Latency and retrieval-correctness evaluation under synthetic load
- Open-set rejection via cosine similarity threshold
- Volatile-memory pixel confinement

### 4.2 Out-of-Scope
- Face detection/alignment (upstream dependency)
- Engagement or compliance inference (Paper 2, Paper 4)
- Privacy proofs or architectural irreversibility claims (Paper 3, Paper 17)
- Trust/audit layer (Paper 8)
- System-level integration stress testing (Paper 10)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P1-INV-01 | Raw pixel buffers MUST NOT persist beyond the vectorization step | RAII allocation; buffer deallocated after `ArcFace.forward()` |
| P1-INV-02 | HNSW index MUST return results within the 33 ms frame budget | `efSearch` bounded; monitored by watchdog timer |
| P1-INV-03 | Unknown subjects (cosine < $\tau$) MUST be rejected, not force-matched | Threshold gate at retrieval output |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P5 (UMA Hardware) | Hardware platform providing memory bandwidth |
| **Downstream** | P2 (Engagement) | Identity vector feeds engagement fusion |
| **Downstream** | P4 (Compliance) | Identity feeds spatiotemporal constraint solver |
| **Downstream** | P9 (Orchestrator) | Retrieval module registered as perception service |
| **Downstream** | P10 (Validation) | HNSW component stress-tested under adversarial load |

## 7. Verification Requirements

- Retrieval latency < 1 ms at $N=100\text{K}$ (synthetic embeddings)
- Open-set rejection rate ≥ 99% for unknown injections at $\tau=0.6$
- Zero pixel data recoverable from heap after vectorization (forensic `gcore` test)
- Index rebuild time within acceptable cold-start window

## 8. What This Paper Does NOT Do

- Does **not** claim biometric face-recognition accuracy on real human datasets
- Does **not** make privacy claims (defers to Paper 3/17)
- Does **not** address trust or auditability (defers to Paper 8)
- Does **not** evaluate system-level integration (defers to Paper 10)
- Does **not** claim Secure Boot or boot-chain integrity — boot integrity is a TCB assumption (Appendix R.4)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **HNSW Indexing** | `infrastructure/indexing/faiss_face_index.py` | ✅ Verified (Replaced FlatL2 with HNSW) |
| **Latency Benchmark** | `benchmarks/hnsw_latency_validation.py` | ✅ Verified (Monotonic Scaling Confirmed) |
| **Clean Architecture** | `di/container.py` | ✅ Verified (Wired to Infrastructure) |

