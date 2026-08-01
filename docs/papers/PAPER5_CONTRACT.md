# PAPER 5 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Memory-Bound Edge Efficiency Envelope (MBEEE): A Hardware-Level Analytical Model |
| **Paper ID** | P5 |
| **Layer** | Hardware / Edge Node Infrastructure Layer (L2) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Finalized (Boundary Enforced) |

## 2. Primary Contribution

**An analytical framework (MBEEE) that establishes the operational bounds of continuous edge inference nodes by modeling the physical energy ($pJ/bit$) of data movement, the latency variance of hardware interconnects, and steady-state thermal behavior.**

Paper 5 operates strictly at the hardware evaluation layer. It provides the physical justification for why ScholarMaster relies on Unified Memory Architecture (UMA) edge nodes rather than discrete PCIe-based accelerators, focusing solely on interconnect physics and thermodynamics.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Unified Memory Architecture reduces transfer-induced serialization (Amdahl's Law) by removing the PCIe off-chip H2D phase | Table I / Eq 4-6 | Clean |
| C2 | UMA fabrics approximate $M/D/1$ queue behavior, reducing latency jitter ($\sigma_{lat}$) compared to stochastic $M/M/1$ discrete bus arbitration | Figure 2 / Eq 8-11 | Clean |
| C3 | Lower dynamic power ($P_{dyn}$) in UMA yields lower steady-state junction temperatures ($T_{junc}$), exponentially improving node lifespan via Arrhenius scaling | Eq 12-16 | Clean |
| C4 | UMA platforms exhibit an estimated 5.4× improvement in continuous performance-per-watt ($FPS/W$) | Section VII.B | Clean |

## 4. Scope

### 4.1 In-Scope
- Physical interconnect evaluation (PCIe vs SoC Fabric)
- Energy analysis ($pJ/bit$ for LPDDR vs Off-chip transfer)
- Latency decomposition strictly at the hardware component level
- Thermal modeling ($RC$ circuits, Arrhenius failure acceleration)

### 4.2 Out-of-Scope (Strictly Forbidden)
- **Software Runtime / Container Orchestration** (Owned by P20)
- **Distributed System Topology** (Owned by P18)
- **Stream Algorithm Design** (Owned by P7)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P5-INV-01 | Must NOT claim software scheduling ownership | Replaced software "dynamic allocation" references with "hardware data-paths" |
| P5-INV-02 | Must NOT claim distributed execution | Scoped explicitly to single "edge node" physics, not "clusters" |
| P5-INV-03 | Must NOT delve into OS kernel mechanics | Replaced "kernel pinning" with "memory controller pinning" |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Downstream** | P20 (Runtime) | P5 validates the hardware constraints that the P20 runtime scheduler must execute within |
| **Downstream** | P18 (Architecture) | P5 justifies the physical selection of the edge nodes populating the P18 topological design |

## 7. What This Paper Does NOT Do

- Does **not** build the ScholarMaster system or the container platform.
- Does **not** write or run deep learning models (only models their hardware cost mathematically).
- Does **not** evaluate network routing or distributed systems.

## 8. Verified Implementation Components

| Component | Status | Note |
|---|---|---|
| **MBEEE Analytical Model** | ✅ Verified | Equation 1 accurately bounds the feasible region |
| **Queueing Variance Derivation** | ✅ Verified | $M/M/1$ vs $M/D/1$ applied correctly to arbitration |
| **Thermal RC Approximation** | ✅ Verified | Valid steady-state derivation |
