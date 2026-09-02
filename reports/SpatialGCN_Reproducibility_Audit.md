# Spatial-GCN — Reproducibility & Open Science Audit

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Evaluation Standard:** ACM / IEEE Reproducibility Guidelines for Machine Learning in Healthcare  

---

## 1. Reproducibility Checklist & Dimension Audit

| Reproducibility Dimension | Status | Current Evidence in Manuscript / Open Artifacts | Action Needed to Reach Full Independent Reproducibility |
|---|---|---|---|
| **1. Data Preprocessing** | `REPRODUCIBLE` | Fully documented in Section III.A (Butterworth 0.5–70 Hz, Notch 50 Hz, 4s epochs, Z-score). | None (Complete in text). |
| **2. Model Architecture** | `REPRODUCIBLE` | Formulated mathematically in Eqs. 2–6 and Fig. 1 (2 Spatial-GCN layers, 64/128 dims, GAP, Sigmoid). | None (Complete in text). |
| **3. Training Procedure** | `REPRODUCIBLE` | Algorithm 1 provides step-by-step training loop with Dynamic Balanced Batching (1:1 sampling). | None (Complete in text). |
| **4. Documented Hyperparameters** | `REPRODUCIBLE` | 19 core parameters explicitly stated ($\tau=0.30$, 100 epochs, $N=19$, filter $w=3$, etc.). | Tabulate in methodology section. |
| **5. Data Splitting Protocol** | `REPRODUCIBLE` | Detailed in Section IV.F (22-fold Leave-One-Subject-Out cross-validation). | None (LOSO protocol is unambiguous). |
| **6. Evaluation Metrics** | `REPRODUCIBLE` | Standard medical classification metrics (AUROC, Precision, Recall, Specificity, LOSO mean $\pm$ std). | None. |
| **7. Hardware Platform** | `REPRODUCIBLE` | NVIDIA Tesla T4 GPU platform stated in Section III.I. | None. |
| **8. Open Code Access** | `REPRODUCIBLE` | Two permanent Google Colab repository links provided in Section III.I (`colab1`, `colab2`). | Keep URLs intact. |
| **9. Software Dependency Lockfile** | `PARTIAL` | Executable via Colab runtime; explicit `requirements.txt` with pip package versions not printed in LaTeX. | Document in code repository README. |
| **10. Random Seeds** | `MISSING` | Random initialization and epoch sampling seeds not recorded in LaTeX text. | Document in code repository. |

---

## 2. Independent Replication Feasibility Assessment

```text
========================================================================
             REPRODUCIBILITY SCORECARD: 8 / 10 FULLY VERIFIED
========================================================================
[PASS] Theoretical & Mathematical Specification : 100% Complete
[PASS] Pipeline & Preprocessing Steps            : 100% Complete
[PASS] Experimental Evaluation Protocol         : 100% Complete (LOSO)
[PASS] Open-Source Repository Links              : Provided (Colab 1 & 2)
[WARN] Execution Version Pinning & Seeds         : Dependent on Colab
========================================================================
OVERALL REPRODUCIBILITY STATUS: REPRODUCIBLE WITH COMPANION REPOSITORIES
========================================================================
```

### Key Findings for Reviewer Response:
1. An independent researcher can implement the model and training algorithm from the mathematical equations (Eqs. 1–6) and Algorithm 1 alone.
2. The exact evaluation protocol (22-fold LOSO on Nasreddine dataset) is fully specified.
3. Colab links provide working code notebooks for both the baseline 1D-CNN and Spatial-GCN models.
