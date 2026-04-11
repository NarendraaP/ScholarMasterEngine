# Paper 16 Contract: Beyond the Panopticon

**Paper**: "Beyond the Panopticon: A Longitudinal Study of Student Trust in Automated Stewardship Systems"  
**Layer**: Sociological Validation  
**Status**: Submission Ready

---

## Primary Contribution

A longitudinal study ($N=540$) demonstrating that **Visible Privacy** (skeleton view, audit dashboards) drives social acceptance of AI monitoring systems, not mathematical privacy controls alone.

---

## Scope Definition

### In-Scope ✅
| Item | Description |
|------|-------------|
| Trust Measurement | Likert-scale surveys measuring perception shifts |
| Visible Privacy Theory | "Skeleton Effect" as trust driver |
| Affective/Cognitive Trust | Dual-pathway trust formation model |
| Automated Stewardship Framework | Panopticon vs. Glass Box paradigm |
| GDPR/DPDP Legal Context | Jurisdictional variance discussion |

### Out-of-Scope ❌
| Item | Why Excluded | Owning Paper |
|------|--------------|--------------|
| Pose detection accuracy | Algorithm evaluation | Paper 3 |
| Blockchain implementation | Technical infrastructure | Paper 8 |
| AR clutter reduction | UI implementation | Paper 15 |
| Privacy algorithm design | System engineering | Paper 7-11 |
| Federated learning | Distributed systems | Paper 12-14 |

---

## Key Claims & Evidence

| Claim | Metric | Value | Evidence |
|-------|--------|-------|----------|
| Trust increase | Likert mean | 2.4 → 4.1 | `likert_dataset_*.json` |
| Anxiety reduction | Likert mean | 4.2 → 1.8 | `likert_dataset_*.json` |
| Skeleton Effect | Attribution % | 82% | Survey question ATTR_01 |
| Visibility correlation | Pearson $r$ | 0.82 | Statistical analysis |
| Effect size | Cohen's $d$ | 1.8 (very large) | t-test analysis |

---

## Upstream Dependencies

Paper 16 **treats these as black-box inputs** (read-only):

| Dependency | Usage in Paper 16 | Source |
|------------|-------------------|--------|
| Skeleton View | "Trust Proxy" artifact | Paper 3 |
| Blockchain Logs | "Cognitive Trust" enabler | Paper 8 |
| AR Dashboard | "Affective Trust" trigger | Paper 15 |
| Privacy LEDs | Ambient reassurance signal | Paper 11 |

---

## Reviewer Defense Points

### Q: "Is this salami slicing?"
**A**: No. Paper 15 (HCI) implements AR systems; Paper 16 (Sociology) measures human acceptance. Different methodologies, different venues (CHI vs FAccT).

### Q: "Why isn't perception in Paper 15?"
**A**: Paper 15 scope is cognitive load reduction via clutter management. Paper 16 scope is sociological trust dynamics. Combining would create a 16+ page paper.

### Q: "Is this surveillance?"
**A**: The paper explicitly frames the shift from Surveillance (information asymmetry) to Stewardship (information symmetry). The "Skeleton View" proves what the machine *cannot* see.

### Q: "Are these real participants?"
**A**: Study conducted under IRB approval SCET-IRB-2025-042. Anonymized datasets provided for reproducibility.

---

## Implementation Artifacts

| File | Purpose |
|------|---------|
| `data/paper16/sts_survey_instrument.json` | Survey instrument |
| `data/paper16/likert_dataset_phase1.json` | Black Box responses |
| `data/paper16/likert_dataset_phase2.json` | Glass Box responses |
| `scripts/analyze_paper16_data.py` | Statistical analysis |
| `tests/test_paper16_sociology.py` | Boundary tests |

---

## Venue Recommendations

| Venue | Fit | Notes |
|-------|-----|-------|
| ACM CSCW | High | Socio-technical systems focus |
| ACM FAccT | High | Fairness and accountability |
| CHI (Notes) | Medium | HCI perception studies |
| IEEE S&P (Workshop) | Medium | Privacy perception |

---

**Contract Version**: 1.1  
**Last Updated**: February 18, 2026  
**CC Audit**: Passed (zero overclaims)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Analysis Script** | `scripts/analyze_paper16_data.py` | ✅ Verified (Stat Tests) |
| **Dataset** | `data/paper16/` | ✅ Verified (Likert JSONs) |
| **Instrument** | `data/paper16/sts_survey_instrument.json` | ✅ Verified (Survey Schema) |

