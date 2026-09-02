# Spatial-GCN — Reviewer Concern Matrix

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Governance Scope:** Reviewer Comment Triaging, Applicability Classification & Mismatch Isolation  

---

## 1. Executive Summary

This matrix audits all feedback from Reviewer 1 and Reviewer 2. A critical finding is that **Reviewer 1 contains an explicit cross-paper review mismatch**, referencing a *"hybrid EKF–GRU framework for battery health estimation."* This battery-health content has been isolated and classified as `NOT_APPLICABLE_MISMATCHED_REVIEW`. Under strict governance rules, no battery-health or EKF-GRU content will be injected into this EEG seizure manuscript.

The generic methodological comments embedded within Reviewer 1 and all comments from Reviewer 2 have been triaged below.

---

## 2. Reviewer Concern Matrix Table

| Reviewer | Raw Comment Summary | Relevant to Paper? | Severity | Existing Evidence in Manuscript / Repositories | Can Resolve with Existing Evidence? | New Analysis Required? | New Experiment Required? | Action / Strategy |
|---|---|---|---|---|---|---|---|---|
| **R1-00** | Battery health estimation / hybrid EKF–GRU framework comments | **NO (Mismatch)** | `NOT_APPLICABLE_MISMATCHED_REVIEW` | None (This is an EEG seizure screening paper, not battery health) | No (Mismatched) | No | No | **Reject/Isolate:** Explicitly inform the editor of the review mismatch; do NOT alter EEG manuscript. |
| **R1-01** | More implementation and experimental details | **YES** | `MEDIUM` | Algorithm 1 (training loop), Fig. 1 (architecture), Section III.A (preprocessing pipeline) | Yes (textual) | No | No | Provide structured implementation table synthesizing all existing methodological details in text. |
| **R1-02** | Hyperparameter settings | **YES** | `HIGH` | 19 parameters documented in Section III ($\tau=0.30$, 100 epochs, dims 64/128, ReLU/Sigmoid, weighted BCE, 1:1 DBB ratio, threshold 0.9362, filter $w=3$, 4s window, 500Hz, 19 channels) | Yes (for 19 params) / Partial | No | No | Explicitly tabulate documented hyperparameters in manuscript. State unverified optimizer tuning details transparently without fabrication. |
| **R1-03** | Dataset partitioning | **YES** | `HIGH` | Section IV.F documents Leave-One-Subject-Out (LOSO) cross-validation across all 22 subjects (21 train / 1 test) | Yes | Yes (Clarify validation split within LOSO folds) | No | Document LOSO protocol prominence and discuss hyperparameter tuning protocol on training folds. |
| **R1-04** | Reproducibility information | **YES** | `MEDIUM` | Section III.I lists Tesla T4 GPU, open Colab links (`colab1`, `colab2`) | Yes (platform & URLs) | No | No | Consolidate reproducibility specifications into a structured checklist in Section III.I. |
| **R1-05** | Additional recent SOTA comparisons | **YES** | `HIGH` | Section II.A/B discusses Wagh 2019, Song 2018, Jang 2019; Table I compares topology classes | Yes (via literature taxonomy) | Yes (2023–2026 literature survey) | No (Cross-dataset comparisons without identical data are invalid) | Add Section II.C surveying 2023–2026 GNN-EEG paradigms (NeuroGNN, GCN-Transformer, Meta-GNN, EEG-GCA) with protocol caveat. |
| **R1-06** | Statistical significance analysis of reported improvements | **YES** | `HIGH` | Table III reports 22-fold LOSO metrics: AUROC ($0.94 \pm 0.04$), Precision ($31.5\% \pm 5.2\%$), Specificity ($99.8\% \pm 0.2\%$) | Partial (descriptive distribution established) | Yes (Report distribution bounds) | No (Cannot fabricate paired per-fold raw seeds) | Report full distribution dispersion (mean, std, min-max bounds); clarify that baseline comparison is aggregate, avoiding unverified significance claims. |
| **R1-07** | Refinement of writing | **YES** | `LOW` | Full manuscript text | Yes | Yes (Editorial revision) | No | Execute language polishing pass: eliminate informal phrasing and improve transitions. |
| **R1-08** | Correction of minor grammatical issues | **YES** | `LOW` | Full manuscript text | Yes | Yes (Editorial revision) | No | Correct punctuation, article omissions, and LaTeX quotation marks. |
| **R1-09** | Clear explanation of novelty over existing hybrid approaches | **YES** | `CRITICAL` | Section I.D & Section II discuss topological prior vs distance and DBB | Yes | Yes (Comparative taxonomy matrix) | No | Insert structured Comparative Taxonomy (Table I) explicitly contrasting Spatial-GCN with Wagh, Song, and Jang across 5 dimensions. |
| **R2-01** | Framework is well motivated and technically sound | **YES** | `LOW` | Section I & III mathematical formulations | Yes | No | No | Acknowledge reviewer compliment in response letter. |
| **R2-02** | Experimental analysis is strong | **YES** | `LOW` | Section IV ablations, noise stress tests, LOSO cross-validation | Yes | No | No | Acknowledge reviewer compliment in response letter. |
| **R2-03** | Validation on larger datasets | **YES** | `HIGH` | Evaluated strictly on Nasreddine (22 patients, 67 seizures); Section V.C acknowledges sample scale | Yes (via limitation strengthening) | Yes (Target dataset scoping) | Optional / Future Work | Explicitly integrate CHB-MIT (24 subjects) and TUH EEG Corpus (675+ subjects) into Limitations (Section V.C) and Future Scope (Section VI). |
| **R2-04** | Reduced reliance on self-citations | **YES** | `MEDIUM` | 3 self-citations (15%): `narendra2026` (MBEEE), `colab1`, `colab2` | Yes | Yes (Citation analysis) | No | Supplement `narendra2026` in Section III.J with external edge-computing reference (Chen & Ran 2019). Retain Colab links as open-science code artifacts. |

---

## 3. Severity Tally

- **NOT_APPLICABLE_MISMATCHED_REVIEW:** 1 (R1-00 Battery Health / EKF-GRU)
- **CRITICAL:** 1 (R1-09 Novelty Clarification & Positioning)
- **HIGH:** 4 (R1-02 Hyperparameters, R1-03 Dataset Partitioning, R1-05 SOTA Comparison, R2-03 Larger Datasets)
- **MEDIUM:** 3 (R1-01 Implementation Details, R1-04 Reproducibility Info, R2-04 Self-Citation Reduction)
- **LOW:** 5 (R1-06 Statistical Reporting, R1-07 Writing, R1-08 Grammar, R2-01 Compliment, R2-02 Compliment)
