# Paper 17 Contract: Architectural Irreversibility

**Paper**: "Architectural Irreversibility: Enforcing Privacy, Governance, and Trust in Intelligent Campus Systems"  
**Layer**: Capstone Doctrine  
**Status**: ✅ Submission Ready  
**Contract Date**: 2026-04-15  
**Source**: `docs/papers/paper17_revised.tex`

---

## Primary Contribution

Establishes **Architectural Irreversibility** as a foundational design principle for privacy-centered edge intelligence. Argues that privacy must be enforced through structural elimination of surveillance capability, not through post-hoc policy or administrative restraint.

---

## Scope Definition

### In-Scope ✅
| Item | Description |
|------|-------------|
| Architectural Irreversibility | Core design principle — destructive transformation |
| Capability Elimination Principle | $f: X→Y$ non-invertible + raw destruction |
| 3-Class Privacy Architecture Taxonomy | Policy / Crypto / Architecturally Constrained |
| Epistemic Humility | Judgment ≠ authority separation |
| Automated Stewardship | Ethical paradigm definition |
| Visible Privacy & Semiotics | Transparency vs legibility distinction |
| Data-as-Liability Framing | Raw data as hazardous institutional asset |
| Constraint-Based Design | Utility limited to preserve contextual integrity |
| PET Differentiation | Why DP/FL/SGX don't eliminate capability |
| De-Identification Illusion | Anonymization / pseudonymization critique |
| Non-Negotiable Architectural Constraints | Boundary irreversibility, governance liveness, algorithmic forgetting |
| Pipeline Doctrine (§VII) | 4 conceptual constraints — monotonic reduction, unidirectional flow, governance interposition, fail-closed default |

### Out-of-Scope ❌
| Item | Why Excluded | Owning Paper |
|------|--------------|--------------| 
| 8-layer structural specification | P17 motivates; P20 specifies | P20 |
| Enforcement mechanisms | P17 prescribes; P18 implements | P18 |
| Formal security theory | Different domain | P19 |
| Mathematical foundations | Different domain | P21 |
| Empirical trust validation | P17 argues; P16 measures | P16 |
| Deployment topologies | Structural detail | P20 |

---

## Boundary Enforcement (v3.0 Cleaning)

> **CRITICAL RULE**: Paper 17 defines DOCTRINE — it states WHY and WHAT, never HOW or WHERE.

| Forbidden Content | Status |
|---|---|
| 8-layer L1–L8 detailed descriptions | ❌ REMOVED — replaced with 4 doctrinal constraints |
| TikZ 8-layer stack figure | ❌ REMOVED |
| "disabling OS swap mechanisms" | ❌ REMOVED |
| "modifying camera drivers" | ❌ REMOVED |
| "disk storage, swap memory partitions, crash dumps" | ❌ REMOVED → "system caches or backup mechanisms" |
| "An eight-layer architectural model" (abstract) | ❌ REMOVED |
| Series-internal references | ❌ ZERO (fully standalone) |

---

## Key Claims

| ID | Claim | Section | Type |
|----|-------|---------|------|
| 17.1 | Privacy-by-Policy fails; capability precedes governance | §II | Doctrinal |
| 17.2 | Architectural Irreversibility eliminates classes of harm by design | §IV | Doctrinal |
| 17.3 | $f: X→Y$ non-invertible + raw destruction = structural impossibility | §IV.2 | Mathematical |
| 17.4 | PETs don't eliminate capability — they secure existing data | §IV.3 | Doctrinal |
| 17.5 | De-identification is illusory — reversible by design | §IV.4 | Doctrinal |
| 17.6 | Governance must be architectural, not administrative | §V.1 | Doctrinal |
| 17.7 | Epistemic Humility — AI judgment ≠ institutional authority | §V.2 | Doctrinal |
| 17.8 | Fail-closed > fail-open under uncertainty | §V.3 | Doctrinal |
| 17.9 | Visible privacy is necessary for social trust (transparency ≠ legibility) | §VI | Doctrinal |
| 17.10 | Automated Stewardship contrasts with surveillance paradigm | §IX.2 | Ethical |

---

## Paper Boundary (Clean Separation)

| Layer | Paper | P17 Relationship |
|-------|-------|------------------|
| Architecture | P20 | P17 **motivates**; P20 **specifies** structure |
| Enforcement | P18 | P17 **prescribes** constraints; P18 **enforces** them |
| Security | P19 | P17 **frames** privacy philosophy; P19 **models** adversaries |
| Foundations | P21 | P17 **argues** principles; P21 **proves** theorems |
| Validation | P16 | P17 **defines** stewardship; P16 **validates** it empirically |

---

## §VII Replacement

Old §VII contained full L1–L8 architectural descriptions with TikZ figure (~15 paragraphs). Replaced with:

- **2 paragraphs** stating the doctrinal principle of monotonic sensitivity reduction
- Reference to "companion work on reference architecture design" (→ P20)
- **4 bullet constraints**: monotonic sensitivity reduction, unidirectional flow, mandatory governance interposition, fail-closed default

---

## Implementation Artifacts

| File | Purpose |
|------|---------|
| `tests/test_irreversibility.py` | Irreversibility structural test |
| `tests/test_failsafe_dropout.py` | Fail-closed watchdog logic test |
| `tests/test_canonical_architecture.py` | 8-layer constraint validator |

---

## Venue Recommendations

| Venue | Fit | Notes |
|-------|-----|-------|
| IEEE S&P | ★★★ | Privacy architecture philosophy |
| ACM CCS (Workshop) | ★★★ | Security design principles |
| USENIX Security | ★★ | Systems privacy design |
| IEEE Computer | ★★ | Architectural critique |

---

## Fixes Applied (v3.0)

| Fix | Severity | Status |
|-----|----------|--------|
| Remove 8-layer L1–L8 detail from §VII | 🔴 P0 | ✅ Fixed |
| Remove TikZ 8-layer stack figure | 🔴 P0 | ✅ Fixed |
| Remove "disabling OS swap" / "modifying camera drivers" | 🔴 P0 | ✅ Fixed |
| Remove "swap memory partitions, crash dumps" specificity | 🟡 P1 | ✅ Fixed |
| Remove "eight-layer" from abstract | 🟡 P1 | ✅ Fixed |

---

**Contract Version**: 3.0  
**Last Updated**: 2026-04-15  
**CC Audit**: Passed (zero overclaims, zero boundary violations)  
**Authority**: Paper 17 LaTeX Source (Capstone Doctrine)
