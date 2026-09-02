# Spatial-GCN — Dataset, Partitioning & Clinical Error Audit

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Focus Areas:** Dataset Provenance, Subject-Level Partitioning, Class Imbalance Dynamics & Clinical Error Characterization  

---

## 1. Dataset Provenance and Characteristics

| Attribute | Specification in Manuscript | Verification Status | Notes / Source Location |
|---|---|---|---|
| **Dataset Name / Reference** | Nasreddine Multi-Center Clinical Scalp EEG Dataset~\cite{nasreddine} | `DOCUMENTED` | Section III.A, Section IV.A |
| **Patient / Subject Count** | 22 patients | `DOCUMENTED` | Abstract, Section III.A, Section IV.A |
| **Total Annotated Seizures** | 67 ictal events | `DOCUMENTED` | Section IV.A |
| **Electrode Configuration** | 19 scalp electrodes (Standard International 10–20 System) | `DOCUMENTED` | Section III.A, Section III.B |
| **Sampling Frequency** | 500 Hz | `DOCUMENTED` | Section III.A |
| **Epoch Duration** | 4.0 seconds (non-overlapping, 2000 points/epoch) | `DOCUMENTED` | Section III.A |
| **Class Imbalance Magnitude** | Severe ($>99\%$ normal background, $<1\%$ seizure duration) | `DOCUMENTED` | Section III.G |
| **Clinical Seizure Subtypes** | Focus on Temporal Lobe Epilepsy (TLE) and fronto-temporal propagation | `DOCUMENTED` | Section V.C |

---

## 2. Partitioning Protocol & Data Leakage Verification

### Critical Partitioning Finding:
The manuscript implements a **strict Leave-One-Subject-Out (LOSO) cross-validation protocol** across all 22 subjects (Section IV.F).

```text
========================================================================
             LEAVE-ONE-SUBJECT-OUT (LOSO) PARTITIONING PROTOCOL
========================================================================
Fold  1: Train = [Patients 2..22] (21 subjects) | Test = Patient 1  (1 subject)
Fold  2: Train = [Patients 1, 3..22] (21 subjects) | Test = Patient 2  (1 subject)
...
Fold 22: Train = [Patients 1..21] (21 subjects) | Test = Patient 22 (1 subject)
========================================================================
Cross-Subject Leakage: ZERO (No windows from test patient appear in training)
========================================================================
```

- **Subject-Level Separation:** Fully enforced. Model training on 21 patients is tested strictly on the 22nd held-out patient per fold.
- **Window Leakage Risk:** Eliminated by LOSO design at the patient level.
- **Hyperparameter Leakage Consideration:** The sparsification threshold ($\tau=0.30$) and post-processing median window radius ($w=3$) are structural priors grounded in network neuroscience literature, rather than parameters continuously retuned per test fold.

---

## 3. Class Imbalance Performance & Metric Decomposition

Under the clinical operating threshold of $\theta = 0.9362$, the manuscript reports the following performance characteristics:

| Metric | Euclidean 1D-CNN Baseline | Spatial-GCN (Ours) | Delta / Behavioral Shift |
|---|---|---|---|
| **AUROC** | $\sim 0.75 - 0.88$ (under noise) | **0.98** (Global) / **0.94 $\pm$ 0.04** (LOSO) | $+0.10$ to $+0.23$ rank-ordering gain |
| **Precision (PPV)** | $< 1.0\%$ ($0.8\%$) | **36.0\%** (Global) / **31.5\% $\pm$ 5.2\%** (LOSO) | **$>36\times$ Improvement** (Eliminates alarm fatigue) |
| **Specificity (TNR)** | $\sim 12.0\%$ | **$\approx 100.0\%$** (Global) / **99.8\% $\pm$ 0.2\%** (LOSO) | Near-zero false positive detections |
| **Recall / Sensitivity** | **88.0\%** | **48.0\%** | $-40.0\%$ Trade-off (Conservative triage operating point) |
| **False Positive Rate** | Severe ($>99\%$ false discovery) | **0.0%** at designated operating point | Complete suppression of uncoordinated artifacts |

### Is the "Robustness" Claim Supported Under Imbalance?
- **YES, for Precision & Specificity:** Standard CNNs collapse to $<1.0\%$ precision because localized scalp noise triggers false alarms across millions of non-seizure windows. Spatial-GCN requires multi-electrode coherence, filtering out localized artifacts.
- **CAVEAT for Sensitivity:** The model achieves extreme specificity by raising the decision threshold to 0.9362, which suppresses sensitivity to $48.0\%$. The manuscript explicitly frames this as an intentional **clinical screening/triage tool** (compressing 24-hour EEG records into a high-confidence subset for expert review) rather than an autonomous diagnostic system.

---

## 4. Clinical Error Analysis

Based on the empirical evidence documented in Sections IV and V:

1. **Failure Mode in False Negatives (Missed Seizures, 52%):**
   - Seizures that remain focal to a single electrode or have not yet recruited distant cortical lobes do not exhibit significant multi-channel Pearson correlation ($r_{ij} < 0.30$). Consequently, the functional graph remains sparse or disconnected, causing the GCN to miss early or strictly localized focal discharges.
2. **False Positives Elimination Mechanism:**
   - Isolated electromyographic (EMG) muscle bursts, ocular flutter (EOG), and electrode pop artifacts produce high-amplitude spikes locally, but lack pairwise temporal covariance across distant channels. Spatial-GCN isolates these electrodes as disconnected nodes, preventing false positive alarms.
3. **Inter-Patient Dispersion:**
   - Under LOSO, Precision ranges from $22.0\%$ to $41.0\%$ across patients (mean $31.5\% \pm 5.2\%$), indicating that patient-specific background impedance and montage variations cause moderate variance, but specificity remains consistently high ($99.2\% - 99.9\%$).
