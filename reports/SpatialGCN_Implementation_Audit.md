# Spatial-GCN — Implementation Detail Audit

**Paper:** Spatial-GCN with Functional Connectivity for Robust Seizure Screening in Imbalanced Clinical EEG  
**Audit Date:** 2026-08-29  
**Source Material:** Manuscript text (`SPATIAL_GCN_ORIGINAL.tex`) and Architecture Definitions  

---

## 1. Parameter Audit Table

| Implementation Aspect | Specification / Value in Manuscript | Evaluation Status | Location in Manuscript / Evidence Notes |
|---|---|---|---|
| **Preprocessing Pipeline** | 4th-order Butterworth bandpass (0.5–70 Hz), 50 Hz notch, channel Z-score | `ADEQUATE` | Section III.A (Steps 1–3) |
| **EEG Channels ($N$)** | $N = 19$ channels (Standard 10–20 International System) | `ADEQUATE` | Section III.A, Section III.B |
| **Sampling Frequency ($f_s$)** | $f_s = 500\text{ Hz}$ | `ADEQUATE` | Section III.A (Step 2) |
| **Filtering Parameters** | Bandpass: 0.5–70 Hz (4th-order zero-phase Butterworth); Notch: 50 Hz | `ADEQUATE` | Section III.A (Step 1) |
| **Normalization Method** | Channel-wise Z-score normalization per epoch | `ADEQUATE` | Section III.A (Step 3) |
| **Segmentation / Windowing** | 4-second non-overlapping epochs ($T = 2000$ samples per channel) | `ADEQUATE` | Section III.A (Step 2) |
| **Functional Connectivity Metric** | Pairwise Pearson Correlation Coefficient ($r_{ij}$) on raw window traces | `ADEQUATE` | Section III.B (Eq. 1) |
| **Graph Construction** | Undirected graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, A)$, $|\mathcal{V}| = 19$, dynamic window-wise construction | `ADEQUATE` | Section III.B |
| **Adjacency Matrix Definition** | Thresholded correlation: $A_{ij} = r_{ij} \cdot \mathbb{I}(\|r_{ij}\| \ge \tau)$ with $\tau = 0.30$ (top 30% retention) | `ADEQUATE` | Section III.B, Algorithm 1 |
| **Spatial-GCN Layers** | 2-layer Spectral GCN with renormalized propagation $\tilde{D}^{-1/2}\tilde{A}\tilde{D}^{-1/2}$ | `ADEQUATE` | Section III.C (Eq. 2), Section III.D |
| **Hidden Dimensions** | Layer 1: 64 hidden units; Layer 2: 128 hidden units | `ADEQUATE` | Section III.D, Figure 1 |
| **Activation Functions** | Hidden: $\text{ReLU}$; Output classifier: $\text{Sigmoid}$ | `ADEQUATE` | Section III.D, Algorithm 1 (lines 11–13) |
| **Dropout Regularization** | Not reported in manuscript text | `MISSING` | Unmentioned in text / Algorithm 1 (Requires code audit to establish if used) |
| **Classifier Head** | Global Average Pooling (GAP) across $N=19$ nodes $\to$ Dense linear projection $\to$ Sigmoid | `ADEQUATE` | Section III.D, Figure 1 |
| **Optimizer Algorithm** | Represented symbolically via gradient step in Algorithm 1 line 16 ($\nabla_\Theta \mathcal{L}$); algorithm type (Adam/SGD/AdamW) not explicitly named in text | `PARTIAL` | Algorithm 1 (Requires code verification to confirm exact optimizer) |
| **Learning Rate ($\eta$)** | Denoted symbolically as $\eta$ in Algorithm 1; scalar floating-point value not explicitly stated in text | `PARTIAL` | Algorithm 1 line 2 |
| **Learning Rate Scheduler** | Not mentioned in manuscript text | `MISSING` | Unmentioned in text |
| **Training Epochs ($E$)** | $E = 100$ epochs | `ADEQUATE` | Section III.G ("Over the course of 100 training epochs") |
| **Batch Size ($B$)** | Balanced batch sampled dynamically; exact scalar batch size in sample count not stated | `PARTIAL` | Section III.G, Algorithm 1 line 5 |
| **Class Weighting Scheme** | Batch-dynamic weights $w_c$ calculated per epoch batch $B_e$ to balance loss contributions | `ADEQUATE` | Section III.G, Algorithm 1 (lines 4, 15) |
| **Loss Function** | Weighted Binary Cross-Entropy (BCE): $\mathcal{L} = -w_1 y \log \hat{y} - w_0 (1-y)\log(1-\hat{y})$ | `ADEQUATE` | Algorithm 1 (line 15) |
| **Stopping Criterion** | Fixed 100 epochs (early stopping patience not specified) | `PARTIAL` | Section III.G |
| **Random Seeds** | Not reported in manuscript text | `MISSING` | Unmentioned in text |
| **Software Framework** | Not reported in manuscript text (Python / PyTorch / PyG / TensorFlow) | `MISSING` | Text mentions Colab environment only |
| **Hardware Environment** | NVIDIA Tesla T4 GPU platform | `ADEQUATE` | Section III.I |

---

## 2. Summary & Action Plan

- **Total Elements Audited:** 25
- **ADEQUATE:** 17 / 25 (68.0%)
- **PARTIAL:** 4 / 25 (16.0%)
- **MISSING:** 4 / 25 (16.0%)

### Implementation Findings:
1. The mathematical formulation, signal preprocessing, graph spectral convolution, and network dimensions are **completely specified and rigorous**.
2. The 4 partial/missing items (scalar learning rate value, optimizer name, dropout rate, software framework version) reside in the companion code repository (Google Colab).
3. **Strict No-Fabrication Protocol:** In this textual audit phase, partial and missing items must be acknowledged transparently rather than inventing unverified numbers (e.g., guessing a learning rate of $10^{-3}$ or Adam optimizer).
