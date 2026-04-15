# Paper 14 Contract: Hierarchical Asynchronous Federation

**Paper**: "Hierarchical Federated Aggregation for Cross-Institution Model Adaptation Under Asynchronous Participation"  
**Layer**: Distributed ML Optimization Algorithm  
**Status**: ✅ Submission Ready  
**Contract Date**: 2026-04-15  
**Source**: `docs/papers/paper14_revised.tex`

---

## Primary Contribution

A hierarchical algorithmic formulation (H-FedAvg) for distributed empirical risk minimization across non-IID partitions. The paper introduces a mathematical update algebra that incorporates dual-level Dirichlet heterogeneity and applies polynomial staleness dampening $\alpha(\tau_i)$ to safely integrate asynchronous updates, achieving a +4.8% cross-domain F1 increase and maintaining convergence under 50% node dropout.

---

## Scope Definition

### In-Scope ✅
| Item | Description |
|------|-------------|
| H-FedAvg Objective | The core mathematical formulation combining edge, intermediate, and global risks. |
| Dual-Level Non-IID | Covariate shift at the edge layer and Dirichlet label skew ($\beta$) at the domain layer. |
| Staleness Dampening | Polynomial scaling function $\alpha(\tau_i) = 1/(1+\tau_i)^\gamma$ applied to delayed gradients. |
| Two-Tier DP Mechanism | Dual-clipping ($C_1, C_2$) injected to obfuscate empirical gradient updates. |
| Simulation Results | Algorithm optimization under induced delay and 50% structural dropout. |

### Out-of-Scope ❌
| Item | Why Excluded | Owning Paper |
|------|--------------|--------------| 
| Physical Network Topology | P14 defines abstract clustering, not WAN/LAN infrastructure. | P18, P20 |
| Orchestration & Queues | P14 defines the math of arrival, not the software queuing it. | P20 |
| Full DP Budget Proofs | P14 uses DP as a mechanism; pure theory is extracted. | P8 |
| Formal Compliance Axioms | Statistical adaptation $\neq$ logical spatial/temporal proof. | P21 |

---

## System-Agnostic Enforcement

> **CRITICAL RULE**: Paper 14 strictly bounds itself to the **mathematics of statistical learning**. It must not describe event routing, networking hardware, MQTT execution, or precise logical privacy boundaries.

| Forbidden Content | Status |
|---|---|
| MQTT, Firewalls, Network topologies | ❌ ABSENT (replaced with abstract aggregation) |
| Active server orchestration language | ❌ ABSENT (replaced with mathematical arrival) |
| Deep DP Budget Derivations | ❌ ABSENT (P14 only defines clipping math) |
| Security analyses (Sybil, poisoning) | ❌ ABSENT (Outside optimization scope) |

---

## Key Claims & Evidence

| Claim | Metric | Value | Evidence |
|-------|--------|-------|----------|
| Generalization on skewed domains | F1 Improvement | **+4.8% Absolute** | Test on simulated Dirichlet domains |
| Dropout robustness | Model accuracy | **> 90%** | Stable up to 50% node dropout |
| Asynchronous stability | Ablation metric | optimal at **$\gamma = 0.5$** | Empirical comparison vs $\gamma=0$ and $\gamma=2.0$ |
| Dual-Level Divergence Model | Parameter definitions | Structural math | Formally defined in §II.B |

---

## Paper Boundary (Clean Separation)

| Layer | Paper | P14 Relationship |
|-------|-------|------------------|
| Runtime Arch | P18 | No overlap. P18 builds the system; P14 provides the model training algorithm. |
| Orchestration | P20 | No overlap. P20 routes messages; P14 mathematically integrates them. |
| Privacy Theory | P8 | Clean boundary. P8 proves deep budget; P14 uses generic clipping structural constraints. |
| Formal Bounds | P21 | No overlap. Statistical optimization (P14) vs logical compliance proofs (P21). |

---

## Fixes Applied (v2.0)

| Fix | Severity | Status |
|-----|----------|--------|
| Purged "infrastructure detail" and network topology diagrams (P18 overlap) | 🔴 P0 | ✅ Fixed |
| Replaced orchestration language with mathematical arrival behavior (P20 overlap) | 🔴 P0 | ✅ Fixed |
| Cut theoretical DP / RDP derivations down to local clipping ops (P8 overlap) | 🟡 P1 | ✅ Fixed |
| Renamed mechanism from generic "exponential decay" to actual "polynomial dampening" | 🟡 P1 | ✅ Fixed |

---

**Contract Version**: 2.0  
**Last Updated**: 2026-04-15  
**CC Audit**: Passed (zero boundary violations, zero software engineering overclaims)  
**Authority**: Paper 14 LaTeX Source (Distributed Learning Layer)
