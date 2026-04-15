# PAPER 20 CONTRACT

**Title:** A Unified Privacy-First Reference Architecture for Edge-Based Intelligent Campus Systems  
**Author:** Dr. S. Suresh Kumar  
**Layer:** Meta (System-Level Reference Architecture)  
**Target Venue:** IEEE IoT-J / ACM Computing Surveys / ICSA  
**Status:** ✅ Submission Ready  
**Contract Date:** 2026-04-15  

---

## Primary Contribution

A unified reference architecture for privacy-centered edge intelligence, introducing:

1. **CFAS** (Constraint-First Architectural Synthesis) — design methodology
2. **4-Stratum / 8-Layer Reference Stack** — structural organization
3. **Tiered Adversary Model ($A_0$–$A_4$)** — with architectural defense mapping
4. **Schema-Constrained Semantic Firewalls** — protobuf as privacy enforcement
5. **Trade-off Space Analysis** — 4 fundamental architectural trade-off dimensions
6. **3 Deployment Topologies** — Micro-Edge, Macro-Edge, Hybrid Fog

---

## Exclusive Contributions

| # | Contribution | Uniqueness |
|---|---|---|
| EC-1 | CFAS design methodology (F ⊆ Feasible(C)) | ✅ Only P20 |
| EC-2 | 4-Stratum / 8-Layer stack definition (Physics/Logic/Verification/Sociology) | ✅ Only P20 |
| EC-3 | Adversary-to-stratum architectural defense mapping (A0–A4) | ⚠️ Defense mapping is P20; formal TCB is P19 |
| EC-4 | Schema-constrained semantic firewalls (protobuf as type-level privacy) | ✅ Only P20 |
| EC-5 | Irreversibility as monotonic sensitivity reduction across strata | ✅ Only P20 (as principle; P17 owns doctrine, P3 owns implementation) |
| EC-6 | End-to-end event lifecycle architectural trace | ✅ Only P20 |
| EC-7 | Deployment topology classification (3 profiles) | ✅ Only P20 |
| EC-8 | Trade-off space analysis (4 dimensions) | ✅ Only P20 |

---

## Ownership Boundaries

### P20 OWNS

- CFAS methodology
- 4-Stratum / 8-Layer reference stack definition
- Adversary classification with architectural defense mapping
- Schema-constrained semantic firewalls
- Inter-stratum execution contracts (as architectural patterns)
- Deployment topology classification
- Trade-off space characterization
- Irreversibility boundary as architectural principle
- Event lifecycle trace

### P20 MUST NOT TOUCH

| Domain | Owner | Forbidden in P20 |
|---|---|---|
| Formal axioms, proofs, theorems, decidability | P21 | Mathematical deductions |
| CSP rule language, OR-Tools, constraint solver | P7 | Runtime logic implementation |
| SHA-256 chains, Merkle trees, erasure protocols | P8 | Cryptographic mechanisms |
| Event bus, GovernanceFilter internals, TTL daemon | P9 | Orchestration implementation |
| Pose extraction model, keypoint dimensions | P3 | Neural architecture |
| Thermal benchmarks, UMA vs dGPU numbers | P5 | Hardware evaluation data |
| mlock, POSIX fences, kernel APIs | P11/P12 | OS-level enforcement |
| DP noise injection algorithms, FedAvg variants | P13/P14 | FL algorithm details |
| AR rendering, cognitive load metrics | P15 | Presentation layer |
| Formal TCB definition, attack trees | P19 | Formal threat model |

---

## Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Provides to** All | Architectural reference for layer placement | All papers map to strata |
| **Consumes from** P21 | Formal guarantees (soundness, completeness) | P21 proves what P20 requires |
| **Consumes from** P19 | Formal threat model (A0–A5 definitions) | P19 formalizes; P20 maps to architecture |
| **Consumes from** P18 | Runtime enforcement evidence | P18 validates P20's architectural constraints |
| **Consumes from** P5 | Hardware feasibility validation | P5 validates P20's deployment profiles |

---

## Code Expectations

P20 is a **pure architecture paper**. Minimal code expected. Supporting artifacts:
- `tests/test_canonical_architecture.py` — Validates layer isolation invariants
- `docs/ARCHITECTURE_CANONICAL.md` — Canonical reference document

---

## Fixes Applied

| Priority | Fix | Status |
|---|---|---|
| 🔴 P0 | Fix §II copy-paste error | ✅ Applied (prior session) |
| 🔴 P0 | Remove hardware benchmark numbers from §VIII.A | ✅ Applied (prior session) |
| 🟡 P1 | Soften implementation specifics — remove mlock, IPC, POSIX fences | ✅ Applied (prior session) |
| 🟡 P1 | Soften §VII Step 5 — "tamper-evidently recorded" | ✅ Applied (prior session) |
| 🟡 P1 | Remove image placeholders or replace with actual figures | ✅ Applied (prior session) |
| 🟡 P1 | Remove §V.6 latency jitter implementation anecdote | ✅ Applied (prior session) |
| 🟢 P2 | Add Related Work section | ✅ Applied (prior session) |
| 🟡 P1 | Refactor §III adversary section — reference P19 via `\cite{b20_threat}` | ✅ Applied |
| 🟡 P1 | Soften §V.2 watchdog reference — defer mechanism to P18 | ✅ Applied |
| 🟡 P1 | Soften §VI.B temporal budget — remove enforcement detail | ✅ Applied |
| 🟡 P1 | Soften §VII.2 abstraction — remove "compiler-safe routines" | ✅ Applied |
| 🟡 P1 | Update Related Work — reference P19 for adversary algebra | ✅ Applied |

### P20 vs P18 Boundary

| P20 Owns | P18 Owns |
|---|---|
| WHAT constraints must hold (6 architectural constraints) | HOW constraints are enforced (mlock, SIGKILL, IPC) |
| WHERE in the stack they are enforced (stratum mapping) | EVIDENCE that they hold (475 trials, 0 residue) |
| WHY they are necessary (trade-off analysis) | Specific enforcement mechanisms (timers, signals) |
| WHAT shape the system takes (stack, topologies) | Failure mode testing (8 categories) |

---

## LOCK STATEMENT

```
PAPER 20 LOCK — v2.0
Layer: Meta (System-Level Reference Architecture)
Owns: CFAS methodology, 4-Stratum/8-Layer reference stack, adversary-to-defense
  architectural mapping (A0–A4), schema-constrained semantic firewalls, inter-stratum
  execution contract patterns, deployment topology classification (3 profiles),
  trade-off space analysis (4 dimensions), and irreversibility boundary principle.
Consumes: Formal guarantees from P21, threat model from P19, hardware feasibility
  from P5, component implementations from P1–P18.
Provides: Architectural reference frame consumed by all papers for layer placement,
  constraint classification, and deployment profile selection.
Forbidden: Formal proofs/theorems, cryptographic mechanism design, runtime solver
  implementation, OS-level kernel APIs, hardware benchmark numbers, neural
  architecture specifications, and FL algorithm details.
```
