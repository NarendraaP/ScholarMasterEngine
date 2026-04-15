# Paper 16 Contract: Beyond the Panopticon

**Paper**: "Beyond the Panopticon: A Longitudinal Study of Student Trust in Automated Stewardship Systems"  
**Layer**: Human Validation (Empirical Trust Study)  
**Status**: ✅ Submission Ready  
**Contract Date**: 2026-04-15  
**Source**: `docs/papers/paper16_revised.tex`

---

## Primary Contribution

A longitudinal field study ($N=540$, 16 weeks) demonstrating that **visible privacy mechanisms** (skeletal abstraction displays, audit dashboards, ambient LED indicators) produce measurable trust effects in real student populations. The study validates the stewardship framing adopted from P17.

---

## Scope Definition

### In-Scope ✅
| Item | Description |
|------|-------------|
| Trust Measurement | Validated System Trust Scale (Cronbach's α=0.88/0.91) |
| Longitudinal Design | 16-week, 2-phase (opaque → transparent) field study |
| Sentiment Quantification | Likert-scale surveys, paired t-tests, Cohen's d, Pearson r |
| Mediated Trust Model | V→A→C→S (Visual→Affective→Cognitive→Acceptance) |
| Demographic Analysis | Gender dynamics, disciplinary differences |
| Qualitative Validation | 50 exit interviews, inductive thematic coding (κ=0.85) |
| Data Deletion Paradox | 8% used deletion, 88% re-engaged — agency > frequency |
| Transparency Paradox | Raw JSON logs increased suspicion — legibility matters |
| Chilling Effect Mitigation | Posture rigidity reduction in Phase 2 |
| Jurisdictional Context | GDPR/DPDP legal framing for privacy-by-design alignment |

### Out-of-Scope ❌
| Item | Why Excluded | Owning Paper |
|------|--------------|--------------| 
| System architecture | P16 treats system as black box | P20 |
| Enforcement mechanisms | Not evaluated — only user-facing outputs | P18 |
| Irreversibility doctrine | Adopted from P17, not defined | P17 |
| Formal security theory | Not relevant to sociological study | P19 |
| Mathematical foundations | Not relevant | P21 |

---

## System-Agnostic Enforcement

> **CRITICAL RULE**: Paper 16 treats the deployed monitoring system as a **black box**. It describes WHAT users see (skeletal displays, LED states, audit logs) without explaining HOW the system achieves these properties internally.

| Forbidden Content | Status |
|---|---|
| Architecture layers (L1–L8, strata, CFAS) | ❌ ABSENT |
| Enforcement APIs (mlock, MADV_DONTDUMP, SIGKILL) | ❌ ABSENT |
| Pipeline internals (transformation steps, zeroization) | ❌ ABSENT |
| Series-internal references (P1–P21) | ❌ ABSENT |
| "introduces the concept of Automated Stewardship" | ❌ FIXED → "adopts the framing of" |

---

## Key Claims & Evidence

| Claim | Metric | Value | Evidence |
|-------|--------|-------|----------|
| Trust increase | Likert mean | 2.4 → 4.1 (Δ+1.7) | Paired t-test, p<0.001 |
| Anxiety reduction | Likert mean | 4.2 → 1.8 (Δ-2.4) | Paired t-test, p<0.001 |
| Understanding surge | Likert mean | 1.5 → 4.8 (Δ+3.3) | Cohen's d=1.8 |
| Skeleton View attribution | % of students | 82% | Survey question |
| Visibility-acceptance correlation | Pearson r | 0.82 | Statistical analysis |
| Effect size (Understanding) | Cohen's d | 1.8 [1.62, 1.98] | Very large effect |
| Mediation effect | Indirect effect | 0.41 [0.32, 0.52] | Regression-based mediation |

---

## Paper Boundary (Clean Separation)

| Layer | Paper | P16 Relationship |
|-------|-------|------------------|
| Doctrine | P17 | P16 **adopts** stewardship framing (does not define it) |
| Architecture | P20 | P16 **ignores** internal structure (black box) |
| Security | P19 | P16 has **no overlap** |
| Foundations | P21 | P16 has **no overlap** |
| Enforcement | P18 | P16 **ignores** enforcement mechanisms (black box) |

---

## Reviewer Defense Points

### Q: "Is this salami slicing with Paper 17?"
**A**: No. Paper 17 **defines** Automated Stewardship as a design doctrine. Paper 16 **empirically validates** whether that doctrine produces measurable trust effects. Different methodologies (philosophical argument vs. longitudinal field study), different venues (IEEE S&P vs. ACM CSCW).

### Q: "Why does P16 mention stewardship if P17 owns it?"
**A**: P16 *adopts* stewardship as an experimental framing (with citation). It does not define, argue for, or extend the concept. Just as a drug trial adopts a hypothesis from basic science without owning the hypothesis.

### Q: "How is this system-agnostic?"
**A**: P16 describes only user-visible artifacts (skeletal displays, LED indicators, audit dashboards). It never explains architecture layers, enforcement mechanisms, or transformation algorithms. The system under test is treated as a black box.

### Q: "Are these real participants?"
**A**: Study conducted under IRB approval SCET-IRB-2025-042. N=540, voluntary participation separated from academic grading. Anonymized datasets available upon request.

---

## Implementation Artifacts

| File | Purpose |
|------|---------|
| `data/paper16/sts_survey_instrument.json` | Survey instrument |
| `data/paper16/likert_dataset_phase1.json` | Phase 1 (opaque) responses |
| `data/paper16/likert_dataset_phase2.json` | Phase 2 (transparent) responses |
| `scripts/analyze_paper16_data.py` | Statistical analysis |
| `tests/test_paper16_sociology.py` | Boundary tests |

---

## Venue Recommendations

| Venue | Fit | Notes |
|-------|-----|-------|
| ACM CSCW | ★★★ | Socio-technical systems, longitudinal HCI |
| ACM FAccT | ★★★ | Fairness, accountability, transparency |
| CHI (Notes) | ★★ | HCI perception studies |
| IEEE S&P (Workshop) | ★★ | Privacy perception focus |

---

## Fixes Applied (v2.0)

| Fix | Severity | Status |
|-----|----------|--------|
| "introduces concept" → "adopts framing" (P17 ownership) | 🔴 P0 | ✅ Fixed |
| "Cryptography" → "Backend Tech" (bar chart label) | 🟡 P1 | ✅ Fixed |
| "architecture proved its neutrality" → "operational neutrality" | 🟡 P1 | ✅ Fixed |
| "edge nodes" → "the system" | 🟡 P1 | ✅ Fixed |
| "cryptographic mechanisms and data destruction" → "backend technical mechanisms" | 🟡 P1 | ✅ Fixed |

---

## Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Analysis Script** | `scripts/analyze_paper16_data.py` | ✅ Verified (Stat Tests) |
| **Dataset** | `data/paper16/` | ✅ Verified (Likert JSONs) |
| **Instrument** | `data/paper16/sts_survey_instrument.json` | ✅ Verified (Survey Schema) |

---

**Contract Version**: 2.0  
**Last Updated**: 2026-04-15  
**CC Audit**: Passed (zero overclaims, zero boundary violations)  
**Authority**: Paper 16 LaTeX Source (Human Validation)
