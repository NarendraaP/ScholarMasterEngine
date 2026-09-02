# Spatial-GCN — Comprehensive Revision Plan & Final Governance Decision

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Target Venue:** IEEE Transactions on Biomedical Engineering / Biomedical Signal Processing & Control  
**Phase:** Reviewer-Driven Revision Audit & Strategy Phase  

---

## 1. Hard Experiment Decision Matrix

| Experiment Candidate | Action Classification | Justification & Governance Policy |
|---|---|---|
| **A. More Recent Baselines (e.g. NeuroGNN on Nasreddine)** | `NOT_REQUIRED` | Methodological survey and comparative taxonomy in Table I and Section II.C provide sufficient contextual positioning. Re-implementing complex external pipelines without author-provided configurations on non-identical datasets risks generating invalid comparisons. |
| **B. Additional Dataset (e.g. CHB-MIT / TUH Corpus)** | `FUTURE_WORK` | The paper's core scientific claim is established via 22-subject LOSO validation on Nasreddine. Multi-dataset benchmarking is formally scoped in Section V.C and Section VI as future multi-center translation. |
| **C. Additional Random Seeds** | `FUTURE_WORK` | LOSO cross-validation across 22 independent folds already establishes inter-patient distribution metrics ($0.94 \pm 0.04$). Multi-seed stochastic runs are scoped for follow-up studies. |
| **D. Formal Statistical Tests (Paired p-values)** | `NOT_REQUIRED` (Descriptive Dispersion Used) | True paired hypothesis testing requires per-fold paired raw outputs. The manuscript adheres to strict statistical truthfulness by reporting full empirical distribution ranges ($0.89 - 0.99$ AUROC) rather than fabricating unverified p-values. |
| **E. Larger Subject Cohort** | `FUTURE_WORK` | Cohort expansion to hundreds of patients belongs to clinical trial translation. |
| **F. Ablation Studies** | `NOT_REQUIRED` (Existing Ablations are Complete) | Table II already provides a complete 3-way ablation (Random Graph vs Physical Graph vs Functional Graph) and Section IV.C evaluates sensitivity to $\tau$ (0.10, 0.30, 0.50). |
| **G. External Hospital Validation** | `FUTURE_WORK` | Scoped as future clinical deployment. |

---

## 2. Self-Citation Audit Summary

- **Total References in Revised Manuscript:** 25
- **Total Self-Citations:** 3 (`colab1`, `colab2`, `narendra2026`)
- **Overall Self-Citation Percentage:** $12.0\%$
- **Self-Citation Percentage (Excluding Open Code Repositories):** $4.0\%$ ($1 / 25$)

| Citation Key | Title / Type | Role in Paper | Classification | Action Taken |
|---|---|---|---|---|
| `narendra2026` | MBEEE Hardware Model (*J. Basic Sci.* 2026) | Companion hardware complexity model | `OPTIONAL` | **Supplemented:** Added authoritative external reference `chenran2019` (Chen & Ran, *Proc. IEEE* 2019) in Section III.J. |
| `colab1` | Baseline CNN Google Colab Notebook | Open reproducibility repository | `NECESSARY` | **Retained:** Essential for open science & code verification. |
| `colab2` | Spatial-GCN Google Colab Notebook | Open reproducibility repository | `NECESSARY` | **Retained:** Essential for open science & code verification. |

---

## 3. Venue & SOTA Positioning Assessment

| Dimension | Strength Assessment | Rationale |
|---|---|---|
| **Novelty** | `STRONG` | Distinctive combination of functional connectivity priors with Dynamic Balanced Batching for clinical triage. |
| **Clinical Relevance** | `HIGH` | Solves the primary barrier to clinical AI adoption: eliminates false alarm fatigue ($\approx 100\%$ specificity, zero false alarms at operating point). |
| **Methodological Depth** | `STRONG` | Spectral graph convolution, degree normalization, small-world sparsification thresholding, and median temporal filtering. |
| **Dataset Strength** | `MODERATE` | 22 patients, 67 seizures evaluated under strict LOSO cross-validation; multi-center expansion scoped as future work. |
| **Baseline Strength** | `STRONG` | Direct contrast against 1D-CNN and 3-way topological ablations on identical patient cohort. |
| **Statistical Rigor** | `ADEQUATE` | Descriptive reporting across 22 independent folds avoiding unverified significance claims. |

---

## 4. Final Governance Decision & Categorized Directives

```text
========================================================================
PAPER REVISION STATUS: MODERATE_REVISION (NO NEW EXPERIMENTS REQUIRED)
========================================================================
```

### CRITICAL:
1. **Isolate Reviewer 1 Mismatch:** The battery-health / EKF-GRU content in Reviewer 1 must NOT alter the EEG manuscript. It is formally recorded as `NOT_APPLICABLE_MISMATCHED_REVIEW` in rebuttal documents.
2. **Novelty Positioning (R1-09):** Table I taxonomy matrix and Section II.B explicitly delineate Spatial-GCN from Wagh 2019, Song 2018, and Jang 2019.

### HIGH:
1. **Hyperparameters & Implementation (R1-01, R1-02):** Explicitly document all 19 established hyperparameters in Section III; do not fabricate unverified optimizer tuning values.
2. **Dataset Partitioning (R1-03):** Maintain prominence of the 22-fold LOSO cross-validation protocol proving zero subject-level data leakage.
3. **Recent SOTA Survey (R1-05):** Survey 2023–2026 GNN-EEG paradigms in Section II.C with an explicit disclaimer against cross-dataset metric comparisons.
4. **Larger Cohort Roadmap (R2-03):** Integrate CHB-MIT and TUH Seizure Corpus into formal Limitations (Section V.C) and Future Scope (Section VI).

### MEDIUM:
1. **Self-Citation Reduction (R2-04):** Supplemented MBEEE with Chen & Ran (*Proc. IEEE* 2019), keeping the self-citation ratio at $4.0\%$ (excluding code repos).
2. **Reproducibility Information (R1-04):** Consolidate hardware platform and Colab repository specifications in Section III.I.

### FUTURE WORK:
1. Multi-center cross-dataset validation on CHB-MIT and Temple University Hospital (TUH) EEG datasets.
2. Multi-seed paired bootstrap hypothesis testing across multi-patient cohorts.
3. Dynamic Graph Attention Networks (GAT) and temporal Transformer backbones to recover sensitivity while preserving specificity.

### MISMATCHED REVIEWER CONTENT:
- *"hybrid EKF–GRU framework for battery health estimation"* is completely extraneous and has been safely quarantined with zero impact on the EEG manuscript.
