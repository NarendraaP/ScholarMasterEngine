# PAPER 5 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Architectural Evaluation of Unified Memory Systems for Edge Vision Workloads |
| **Paper ID** | P5 |
| **Layer** | Infrastructure (L1 — Hardware Platform) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A quantitative evaluation of Unified Memory Architecture (UMA) versus discrete-GPU systems for edge vision workloads, demonstrating that UMA eliminates PCIe copy overhead and provides superior energy efficiency (FPS/Watt) for sustained inference at thermal equilibrium.**

Paper 5 provides the hardware justification layer — it validates that the UMA-class platform selected for ScholarMaster meets the thermal, bandwidth, and energy constraints required by the perception pipeline.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | UMA achieves >100 GB/s effective memory bandwidth, eliminating the PCIe bottleneck | Bandwidth benchmarks (§IV) | Clean |
| C2 | UMA sustains inference under thermal constraints (<65°C) where discrete-GPU throttles | Thermal profiling (§V) | Clean |
| C3 | Energy efficiency (FPS/Watt) favors UMA for continuous 24/7 edge workloads | Power measurement (§VI) | Clean |
| C4 | Zero-copy memory design enables sub-33 ms end-to-end pipeline latency | Pipeline latency breakdown (§IV) | Clean |

## 4. Scope

### 4.1 In-Scope
- Memory bandwidth benchmarking (UMA vs dGPU)
- Thermal profiling under sustained inference load
- Energy efficiency comparison (FPS/Watt)
- Zero-copy pipeline latency analysis
- Hardware selection justification for edge deployment

### 4.2 Out-of-Scope
- Algorithm design or model architecture (all papers)
- Privacy enforcement (Paper 3, Paper 17)
- Production deployment infrastructure (Paper 11)
- Flash storage endurance (Paper 12)
- System-level integration testing (Paper 10)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P5-INV-01 | Selected hardware MUST sustain inference at ≥30 FPS under thermal equilibrium (35°C ambient) | Thermal profiling validates pre-deployment |
| P5-INV-02 | Memory bandwidth MUST exceed pipeline requirements without PCIe copy overhead | UMA architecture eliminates discrete copy |
| P5-INV-03 | Power budget MUST fit within institutional PoE+ constraints (≤25W) | Hardware selection criteria |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Downstream** | P1 (Retrieval) | Hardware platform for HNSW inference |
| **Downstream** | P3 (Pose) | Hardware platform for pose extraction |
| **Downstream** | P6 (Acoustic) | Hardware platform for audio processing |
| **Downstream** | P10 (Validation) | Hardware testbed for adversarial stress testing |
| **Downstream** | P11 (MLOps) | Hardware deployment target specification |

## 7. Verification Requirements

- Sustained 30 FPS at 35°C ambient for ≥7 days (burn-in test)
- Memory bandwidth ≥ 100 GB/s measured via benchmarking tool
- Power consumption ≤ 25W under full inference load
- Junction temperature stable below throttling threshold (85°C)

## 8. What This Paper Does NOT Do

- Does **not** propose new hardware or chip design
- Does **not** evaluate algorithms or models
- Does **not** address production deployment logistics (defers to Paper 11)
- Does **not** make privacy or trust claims

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Zero-Copy Pipeline** | `modules_legacy/master_engine.py` | ✅ Verified (CoreML Integration) |
| **Ablation Report** | `benchmarks/hardware_test.py` | ✅ Verified (Energy Efficiency Metrics) |
| **Cold Boot Logic** | `benchmarks/cold_boot_latency.py` | ✅ Verified (Docker Simulation) |

- Results are specific to UMA-class hardware and should not be extrapolated to lower-tier embedded platforms
