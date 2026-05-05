# PAPER 9 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | A Hierarchical Edge Control Plane for Policy-Aware Multi-Module AI Orchestration |
| **Paper ID** | P9 |
| **Layer** | Orchestration (L5 — Control Plane) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Corrected (CC v3.0 aligned) |

## 2. Primary Contribution

**A hierarchical control-plane architecture that separates Perception, Reasoning, and Governance. It formalizes Inference Rate Governance (IRG) via a Compute Justification Model, enforcing context-aware module activation (ISR/ECU/CADC) and failure containment through a deterministic watchdog state machine.**

Paper 9 serves as the orchestration foundation. It ensures models are only active when pedagogically justified and that isolated module crashes do not trigger cascading system failures.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Hierarchical separation of Perception, Reasoning, and Governance contains isolated crashes | Layer Isolation Factor (LIF) $\approx 95\%$ | Clean |
| C2 | Compute Justification Model reduces scheduled inference cycles without losing policy coverage | Inference Suppression Ratio (ISR) > 70\% for heavy vision | Clean |
| C3 | Deterministic state machine provides graceful degradation (Normal $\to$ Degraded $\to$ Safe) | Failure Mode Analysis (§VI) | Clean |
| C4 | Validation via fault injection confirms control decisions align with policy | Abstract state transitions maintained | Clean |

## 4. Scope

### 4.1 In-Scope
- Hierarchical Control Plane Architecture (Perception $\to$ Reasoning $\to$ Governance)
- Compute Justification Model (ISR, ECU, CADC metrics)
- Failure Containment Design (Watchdog timers, Fallback state machine)
- Operational Budget tracking
- Validation via fault injection (logical state transition maintenance)

### 4.2 Out-of-Scope
- Perception algorithms (Papers 1, 3, 6)
- Reasoning logic (Papers 2, 4, 7)
- Trust/audit storage (Paper 8)
- Hardware platform (Paper 5)
- System-level stress testing (Paper 10)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P9-INV-01 | Modules MUST NOT communicate raw sensory data across the Governance/Reasoning boundary | Typed context vectors $\vec{C}$ |
| P9-INV-02 | System MUST transition to Safe state upon continuous module timeout | Deterministic State Machine + Watchdog |
| P9-INV-03 | Module activation cycles MUST NOT exceed daily operational budgets $B_{max}$ | Compute Justification Model |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P1 (Identity) | Identity retrieval events |
| **Upstream** | P2 (Engagement) | Engagement labels |
| **Upstream** | P3 (Pose) | Pose events |
| **Upstream** | P4 (Compliance) | Compliance decisions |
| **Upstream** | P6 (Acoustic) | Safety events |
| **Upstream** | P7 (Schedule) | Rule updates |
| **Downstream** | P8 (Trust) | Governance-filtered events for audit logging |
| **Downstream** | P10 (Validation) | Orchestrator exercised under integration stress |
| **Downstream** | P15 (AR) | Events routed to presentation layer |

## 7. Verification Requirements

- ISR for heavy vision modules > 70% under standard lecture scenarios
- ECU (Ethical Compute Utilization) > 90%
- Abstract state transitions execute successfully under simulated timeouts
- 95% Layer Isolation Factor (LIF) across chaos testing lifecycles

## 8. What This Paper Does NOT Do

- Does **not** implement perception, reasoning, or trust algorithms
- Does **not** make privacy claims beyond governance enforcement (defers to Paper 3/17)
- Does **not** perform system-level stress testing (defers to Paper 10)
- Does **not** define the trust storage mechanism (defers to Paper 8)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **IRG Logic** | `modules_legacy/governance.py` | ✅ Verified (`get_inference_strategy`) |
| **Control Plane** | `modules_legacy/governance.py` | ✅ Verified (State Machine: Normal/Degraded/Safe) |
| **Failover** | `modules_legacy/governance.py` | ✅ Verified (Watchdog Timers) |
