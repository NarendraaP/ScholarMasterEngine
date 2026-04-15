# PAPER 19 CONTRACT — v3.0

**Paper:** P19  
**Title:** Formal Threat Modeling and Trusted Computing Base Analysis for Privacy-Constrained Edge AI Systems  
**Author:** Dr. S. Suresh Kumar  
**Layer:** Security Formalization  
**Target Venue:** IEEE S&P / CCS / USENIX Security / ACM TOPS  
**Status:** ✅ Submission Ready  
**Contract Date:** 2026-04-15  
**Source File:** `docs/papers/paper19_revised.tex`  

---

## Primary Contribution

A formal security analysis framework for privacy-constrained edge AI systems, defining:

1. **Adversary Capability Algebra** ($A_0$–$A_5$) with formal tuple $\langle \mathcal{O}, \mathcal{M}, \mathcal{E} \rangle$
2. **TCB Decomposition** — explicit set $\{C_{boot}, C_{kernel}, C_{alloc}, C_{watchdog}, C_{gov}\}$
3. **TCB Minimization as Optimization** — $\min |T|$ s.t. invariant satisfaction (novel framing)
4. **Goguen-Meseguer Non-Interference** — $\mathcal{D}_{High}$/$\mathcal{D}_{Low}$ unwinding theorem
5. **Inline TLA+ Specification** — IrreversibleEdge module with TemporalBound invariant
6. **Environmental Bounding Assumptions** — $A_{HW}$, $A_{PHYS}$, $A_{SPEC}$
7. **5 Narrative Security Properties** — Non-Reconstructability, Probabilistic NI, Bounded Exposure, Governance Non-Bypass, Fail-Closed
8. **Explicit Residual Attack Surface** — $A_4$/$A_5$ honest scope exclusion
9. **Mechanized Verification Limits** — state-space explosion acknowledgment

---

## Exclusive Contributions

| # | Contribution | Uniqueness |
|---|---|---|
| EC-1 | Adversary capability algebra $\langle \mathcal{O}, \mathcal{M}, \mathcal{E} \rangle$ with 6 tiers | ✅ Only P19 |
| EC-2 | TCB minimization as constrained optimization ($\min |T|$ s.t. invariant satisfaction) | ✅ Only P19 — novel framing |
| EC-3 | Inline TLA+ specification (IrreversibleEdge module) with TLC model checking | ✅ Only P19 |
| EC-4 | Goguen-Meseguer Non-Interference unwinding for edge AI domains | ✅ Only P19 |
| EC-5 | Environmental bounding assumptions ($A_{HW}$, $A_{PHYS}$, $A_{SPEC}$) | ✅ Only P19 |
| EC-6 | seL4-inspired TCB verification surface reduction | ✅ Only P19 |
| EC-7 | Explicit residual attack surface characterization ($A_4$/$A_5$) | ✅ Only P19 |
| EC-8 | TOCTOU race condition framing for temporal enforcement | ✅ Only P19 |

---

## Ownership Boundaries

### P19 OWNS

- Adversary capability algebra ($A_0$–$A_5$ with formal tuples)
- TCB boundary definition and component set
- TCB minimization as optimization problem ($\min |T|$)
- Non-Interference formalization (Goguen-Meseguer unwinding)
- TLA+ specification (IrreversibleEdge module, TemporalBound invariant)
- Environmental assumptions ($A_{HW}$, $A_{PHYS}$, $A_{SPEC}$)
- 5 narrative security properties mapped to adversary tiers
- Residual attack surface analysis
- Mechanization limits acknowledgment

### P19 MUST NOT TOUCH

| Domain | Owner | Status in v3.0 |
|---|---|---|
| CFAS, 4-stratum/8-layer stack, deployment topologies | P20 | ✅ Not mentioned |
| Kinematic axioms, event calculus, compliance predicates, decidability | P21 | ✅ Not mentioned |
| Architectural Irreversibility doctrine naming | P17 | ✅ Not named |
| Runtime fault injection, empirical watchdog testing | P18 | ✅ Not mentioned |
| SHA-256 hash chains, Merkle trees, erasure protocols | P8 | ✅ Not mentioned |
| Differential Privacy algorithms, FedAvg, gradient compression | P13/P14 | ✅ Not mentioned |
| Pose estimation, neural architecture | P3 | ✅ Not mentioned |
| GovernanceFilter, event bus implementation | P9 | ✅ Not mentioned |

---

## Boundary Compliance

| Boundary | Status |
|---|---|
| vs P21 (formal system theory) | ✅ **ZERO OVERLAP** |
| vs P20 (architecture) | ✅ **RESOLVED** — P20 cites P19 via `\cite{b20_threat}` |
| vs P8 (cryptography) | ✅ **CLEAN** — no mechanism definition |
| vs P17 (doctrine) | ✅ **ZERO OVERLAP** |
| vs P18 (runtime verification) | ✅ **ZERO OVERLAP** |
| vs P13/P14 (FL/DP) | ✅ **ZERO OVERLAP** |
| Series-internal references | ✅ **ZERO** — fully standalone |

---

## Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Provides to** P20 | Formal adversary model ($A_0$–$A_5$) | P20 maps tiers to architectural strata |
| **Consumes from** | None | Fully standalone with external references only |
| **Parallel with** P8 | Different security domains | P8 = audit provenance; P19 = adversary-TCB boundary |

---

## Code Expectations

P19 is a **formal security specification paper**. Minimal code:
- `formal/ScholarMaster_Invariants.tla` — TLA+ model (aligns with inline spec)
- `core/failure_semantics.py` — Fail-closed state transitions
- `tests/test_failsafe_dropout.py` — Fail-closed testing

---

## Bibliography

23 external references, zero series-internal. Key citations:
- Saltzer-Schroeder [b1], Dolev-Yao [b2], Orange Book [b3]
- seL4 [b5, b20], Goguen-Meseguer [b8], Rushby [b22]
- Lamport TLA+ [b13], Sabelfeld-Myers [b11], Denning [b12]
- Fredrikson MI [b6], Shokri MIA [b7], Carlini [b14]

---

## Lock Statement

```
PAPER 19 LOCK — v3.0
Layer: Security Formalization
Title: Formal Threat Modeling and TCB Analysis for Privacy-Constrained Edge AI
Source: docs/papers/paper19_revised.tex
Owns: Adversary capability algebra (A0–A5 with ⟨O, M, E⟩ tuples), TCB decomposition
  and minimization as constrained optimization (min|T|), Goguen-Meseguer Non-
  Interference unwinding for D_High/D_Low partitions, inline TLA+ specification
  (IrreversibleEdge module with TemporalBound invariant), environmental bounding
  assumptions (A_HW, A_PHYS, A_SPEC), and 5 narrative security properties.
Consumes: Nothing — fully standalone with external references only.
Provides: Formal adversary model consumed by P20 (architectural defense mapping).
Forbidden: Architectural structure (P20), system-theoretic axioms (P21), differential
  privacy derivation (P13/P14), cryptographic mechanism design (P8), runtime fault
  injection methodology (P18), and irreversibility doctrine naming (P17).
```
