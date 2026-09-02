# Spatial-GCN — Statistical Significance & Rigor Audit

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Core Objective:** Assess Statistical Validity of Experimental Claims & Determine Defensible Statistical Reporting Protocol  

---

## 1. Existing Statistical Evidence in Manuscript

| Statistical Element | Existing Data in Manuscript | Statistical Status | Rigor Assessment |
|---|---|---|---|
| **Cross-Validation Scheme** | 22 independent Leave-One-Subject-Out (LOSO) folds | `ESTABLISHED` | Subject-independent validation across all 22 patients in the Nasreddine dataset. |
| **AUROC Dispersion** | $\text{Mean} = 0.94$, $\text{Std. Dev.} = \pm 0.04$, $\text{Range} = [0.89, 0.99]$ | `ESTABLISHED` | Low variance demonstrates stable rank ordering across diverse subjects. |
| **Precision Dispersion** | $\text{Mean} = 31.5\%$, $\text{Std. Dev.} = \pm 5.2\%$, $\text{Range} = [22.0\%, 41.0\%]$ | `ESTABLISHED` | Consistent order-of-magnitude gain over baseline ($<1.0\%$) across all folds. |
| **Specificity Dispersion** | $\text{Mean} = 99.8\%$, $\text{Std. Dev.} = \pm 0.2\%$, $\text{Range} = [99.2\%, 99.9\%]$ | `ESTABLISHED` | Near-perfect artifact suppression across all evaluated patient brains. |
| **Paired Hypothesis Testing (p-values)** | Not performed in original manuscript | `ABSENT` | No Wilcoxon signed-rank test or paired t-test against CNN baseline is reported. |
| **Confidence Intervals (95% CI)** | Not formally calculated via bootstrap | `ABSENT` | Dispersion reported strictly as Mean $\pm$ Standard Deviation. |
| **Multiple Random Seed Repeats** | Single-seed run reported per LOSO fold | `ABSENT` | Inter-seed variance (stochastic initialization) not tabulated. |

---

## 2. Statistical Feasibility & Defensible Reporting Strategy

### Can Statistical Significance be Formally Claimed Right Now?
**NO.** Under scientific governance rules:
- An aggregate comparison (GCN mean vs CNN aggregate) without per-fold paired difference testing cannot mathematically establish a formal $p$-value ($p < 0.05$ or $p < 0.01$).
- Fabricating simulated per-fold p-values is strictly forbidden.

### Most Defensible Protocol for Manuscript & Rebuttal:
1. **Report Full Empirical Dispersion:** Present the mean, standard deviation, and full minimum-to-maximum range across all 22 LOSO folds as honest descriptive statistics of inter-subject variance.
2. **Avoid Unsupported Claims:** Do NOT use the phrase *"statistically significant improvement"* in the manuscript text unless accompanied by an explicit, verifiable paired statistical test.
3. **Use Accurate Descriptive Framing:** Frame findings as *"consistent empirical improvements across all 22 evaluated LOSO folds (AUROC $0.94 \pm 0.04$, Specificity $99.8\% \pm 0.2\%$)"*.
4. **Register Formal Hypothesis Testing as Future Scope:** State transparently in the discussion that multi-seed paired bootstrap testing across multi-center cohorts is part of ongoing extensions.

```text
========================================================================
                      STATISTICAL INTEGRITY POLICY
========================================================================
CLAIMED: "Statistically significant improvement (p < 0.001)" -> REJECTED
PERMITTED: "Consistent empirical improvement across 22 LOSO folds 
           (AUROC 0.94 +/- 0.04, Precision 31.5% +/- 5.2%)"   -> APPROVED
========================================================================
```
