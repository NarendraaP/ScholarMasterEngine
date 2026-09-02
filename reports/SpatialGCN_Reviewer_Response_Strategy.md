# Spatial-GCN — Reviewer Response Strategy & Rebuttal Plan

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Target:** Journal Peer Review Rebuttal  
**Audit Date:** 2026-08-29  

---

## 1. Mismatched Review Handling Strategy (Reviewer 1)

> **Editor / Reviewer Note on Mismatched Content:**  
> Reviewer 1's report includes comments referencing a *"hybrid EKF–GRU framework for battery health estimation."*  
> **Rebuttal Position:** *"We respectfully note that this specific comment appears to have resulted from an unintended cross-paper review mismatch, as our manuscript focuses exclusively on Graph Convolutional Networks and functional connectivity for epileptic seizure screening in clinical EEG. We have addressed all general methodological requests made by the reviewer (implementation details, hyperparameters, dataset partitioning, reproducibility, SOTA contextualization, and novelty defense) in detail below."*

---

## 2. Point-by-Point Response Strategy

### Item R1-01: Implementation & Experimental Details
- **Reviewer Comment:** *More implementation and experimental details.*
- **Our Response:** Synthesize all preprocessing, architecture, and training mechanics into explicit mathematical equations and training algorithms in Section III.
- **Evidence in Paper:** Algorithm 1 (Training loop), Figure 1 (Layer dimensions 64/128, GAP, Sigmoid), Section III.A (Butterworth 0.5–70Hz, Notch 50Hz, 4s epochs at 500Hz, Z-score).
- **Manuscript Revision:** Structured itemized description of preprocessing and algorithmic steps in Section III.A–F.
- **Experiment Required:** `NOT_REQUIRED` (Documented in existing manuscript).

---

### Item R1-02: Hyperparameter Settings
- **Reviewer Comment:** *Hyperparameter settings.*
- **Our Response:** Detail all 19 established hyperparameters across data processing, graph topology, training schedule, and decision post-processing.
- **Evidence in Paper:** Sparsification threshold $\tau=0.30$, 100 training epochs, GCN dimensions (64, 128), ReLU/Sigmoid activations, weighted BCE loss, 1:1 Dynamic Balanced Batching ratio, decision threshold 0.9362, median filter $w=3$ (12s span).
- **Manuscript Revision:** Explicit hyperparameter specifications integrated into Section III.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R1-03: Dataset Partitioning Protocol
- **Reviewer Comment:** *Dataset partitioning.*
- **Our Response:** Highlight the rigorous 22-fold Leave-One-Subject-Out (LOSO) cross-validation protocol, proving zero patient-level data leakage.
- **Evidence in Paper:** Section IV.F explicitly details training on 21 patients and testing on 1 held-out patient per fold across all 22 subjects.
- **Manuscript Revision:** Elevated LOSO protocol description in Abstract, Section I.D, and Section IV.F.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R1-04: Reproducibility Information
- **Reviewer Comment:** *Reproducibility information.*
- **Our Response:** Provide hardware platform specifications and open-access links to executable Google Colab notebooks for baseline and Spatial-GCN models.
- **Evidence in Paper:** Section III.I lists the NVIDIA Tesla T4 platform and provides active URLs (`colab1`, `colab2`).
- **Manuscript Revision:** Formatted open-access reproducibility block in Section III.I.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R1-05: Recent State-of-the-Art Comparisons
- **Reviewer Comment:** *Additional recent state-of-the-art comparisons.*
- **Our Response:** Survey recent 2023–2026 GNN-EEG paradigms (Dynamic/Heterogeneous GNNs, Hybrid GCN-Transformers, Meta-GNNs, and Unsupervised Graph Anomaly screening) in Section II.C and Table I, accompanied by an explicit scientific caveat regarding cross-dataset non-comparability.
- **Evidence in Paper:** Published literature: NeuroGNN (*IEEE TBME* 2024), GCN-Transformer (*BSPC* 2024), Meta-GNN (*IEEE TNSRE* 2024), EEG-GCA (*Front. Neurosci.* 2025).
- **Manuscript Revision:** Added Section II.C and expanded Table I taxonomy.
- **Experiment Required:** `NOT_REQUIRED` (Contextual literature taxonomy).

---

### Item R1-06: Statistical Significance Analysis
- **Reviewer Comment:** *Statistical significance analysis of reported improvements.*
- **Our Response:** Report complete inter-patient distribution statistics across all 22 LOSO folds (AUROC $0.94 \pm 0.04$, Precision $31.5\% \pm 5.2\%$, Specificity $99.8\% \pm 0.2\%$, Min-Max ranges), demonstrating low variance without fabricating unverified paired p-values.
- **Evidence in Paper:** Table III LOSO results table.
- **Manuscript Revision:** Refined Section IV.F and Table III reporting full descriptive dispersion.
- **Experiment Required:** `FUTURE_WORK` (Multi-seed paired testing on multi-center cohorts).

---

### Item R1-07 & R1-08: Writing & Grammar Refinement
- **Reviewer Comment:** *Refinement of writing and correction of minor grammatical issues.*
- **Our Response:** Complete editorial overhaul of the manuscript text, eliminating informal phrasing and standardizing LaTeX formatting.
- **Evidence in Paper:** Full text diff log.
- **Manuscript Revision:** Comprehensive language quality pass across all 6 sections.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R1-09: Novelty Clarification Over Existing Hybrid Approaches
- **Reviewer Comment:** *Clear explanation of novelty over existing hybrid approaches.*
- **Our Response:** Formulate a structured comparative taxonomy in Table I and explicitly differentiate Spatial-GCN from Wagh et al. (2019), Song et al. (2018), and Jang et al. (2019) across adjacency construction, training balance, and clinical triage objectives.
- **Evidence in Paper:** Table I (Taxonomy matrix), Section II.B, and Section I.D.
- **Manuscript Revision:** Inserted Table I comparative taxonomy and novelty defense prose.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R2-01 & R2-02: Framework Motivation & Experimental Analysis
- **Reviewer Comment:** *Framework is well motivated and technically sound; experimental analysis is strong.*
- **Our Response:** Formally acknowledge the reviewer's positive evaluation in the rebuttal letter.
- **Evidence in Paper:** Sections I, III, and IV.
- **Manuscript Revision:** None required.
- **Experiment Required:** `NOT_REQUIRED`.

---

### Item R2-03: Validation on Larger Datasets
- **Reviewer Comment:** *Validation on larger datasets would strengthen the work.*
- **Our Response:** Acknowledge cohort scale limitations and explicitly integrate the CHB-MIT Scalp EEG Database (24 subjects) and the Temple University Hospital (TUH) Seizure Corpus (675+ subjects) into formal Limitations and Future Scope roadmap.
- **Evidence in Paper:** Section V.C and Section VI citations (Goldberger et al. 2000).
- **Manuscript Revision:** Updated Section V.C (Limitations) and Section VI (Future Scope).
- **Experiment Required:** `FUTURE_WORK` (Large-scale multi-cohort benchmarking).

---

### Item R2-04: Reduced Reliance on Self-Citations
- **Reviewer Comment:** *Reduced reliance on self-citations.*
- **Our Response:** Audit all self-citations. Supplement Section III.J with an external foundational edge-computing reference (Chen & Ran, *Proc. IEEE* 2019). Retain Colab links as open-science code artifacts.
- **Evidence in Paper:** Bibliography (`chenran2019`, `colab1`, `colab2`, `narendra2026`).
- **Manuscript Revision:** Updated Section III.J citation string and bibliography.
- **Experiment Required:** `NOT_REQUIRED`.
