# P22 — TRUE CONTENT-LEVEL PEER REVIEW

**Title**: Perception Integrity Foundations: Evidential Uncertainty, Disagreement Dynamics, and Blur Bounds in Edge Vision  
**Venue Style**: IEEE Transactions / Conference on Cyber-Physical Systems / Computer Vision  
**Physical PDF Pages**: 6 pages  
**Word Count**: ~4,515 substantive words  
**References**: 25 peer-reviewed citations  

---

## 1. Overall Understanding

* **Problem Solved**: High-capacity deep neural network (DNN) classifiers deployed on edge vision appliances become dangerously overconfident under optical defocus, motion blur, and out-of-distribution (OOD) perturbations. Softmax normalization evaluates only relative logit differences ($\sigma(\mathbf{z} + c\mathbf{1}) = \sigma(\mathbf{z})$) rather than absolute evidential support, allowing corrupted frames to produce near-1.0 confidence that triggers catastrophic downstream state corruptions (Data Cascades).
* **Why It Matters**: In multi-tier cyber-physical cascades (e.g., identity verification, tracking, temporal compliance, administrative commits), an uncalibrated false positive at Layer 1 flips discrete states in downstream nearest-neighbor vector search and Kalman tracking, committing false infractions to immutable ledgers.
* **Proposed Solution**: A unified Layer-1 Perception Integrity firewall combining Dirichlet Evidential Deep Learning (EDL), multi-branch spatial cross-agreement, and frequency-domain optical blur bounds into a composite perception risk metric $R_p \in [0, 1]$ with deterministic fail-closed gating ($\bot$ when $R_p > 0.70$).
* **Central Scientific Contribution**: First-principles mathematical derivation of the Dirichlet evidence variance upper bound ($\mathrm{Var}(p_k) \le \frac{1}{4(S+1)} < \frac{1}{4K}$), uniform evidence contraction monotonicity, and physical frequency-domain blur gating ($B(I)$).
* **What the Paper Demonstrates**: Achieves $\text{AUROC} = 1.0000$ and $\text{FPR95} = 0.0000$ on a 2,000-example edge benchmark suite, reducing Expected Calibration Error ($\text{ECE}$) by $90.2\%$ (from $0.4218$ to $0.0412$) with a single-pass inference latency of $1.486\text{ ms}$ (well within the $5.0\text{ ms}$ SLA).

---

## 2. Introduction Assessment

* **Problem & Motivation**: Strongly established in lines 38–52. The explanation of softmax translation invariance in Eq. (2) clearly illustrates why softmax cannot distinguish epistemic from aleatoric uncertainty. The connection to Sambasivan et al.'s Data Cascade survey ($92\%$ AI deployment failure rate) provides compelling cyber-physical systems motivation.
* **Research Gap**: Clearly formulated across five concrete dimensions in lines 54–60 (Softmax Overconfidence, Calibration vs Uncertainty, OOD Scoring vs Deterministic Gating, Image Quality vs Semantic Uncertainty, and Perception Integrity Contracts).
* **Contributions vs Execution**: The four stated contributions (lines 63–68) directly match the technical development in Section III and empirical results in Section IV.
* **Overclaim Warning**: In the Abstract and Introduction, claiming $\text{AUROC} = 1.0000$ and $\text{FPR95} = 0.0000$ sounds like an impossible empirical result unless properly contextualized; the authors do explicitly bound this to the 2,000 benchmark frames in Section IV-C3 (lines 308–309), but the Abstract should clarify this is on the curated benchmark suite rather than an unconstrained open-world guarantee.

---

## 3. Related Work Assessment

* **Coverage**: Analyzes six distinct paradigms in Section II (Softmax Normalization, Bayesian Sampling / MC-Dropout, Parametric Ensembling, Energy-Based Scoring, Frequency-Domain Filters, and Evidential Deep Learning).
* **Synthesis & Table**: Table I (Taxonomy) is exceptional. It provides a structured multi-dimensional comparison across passes, edge latency ($<5\text{ms}$), OOD discrimination, analytic variance proofs, and calibration error.
* **Logical Gap Bridge**: The text establishes that MC-Dropout ($28.5\text{ ms}$) and Deep Ensembles ($18.2\text{ ms}$) violate edge SLAs ($<5\text{ ms}$), while single-pass energy scoring lacks bounded variance guarantees, establishing a clear need for single-pass Dirichlet EDL coupled with Fourier optical metrics.
* **Verdict**: **WELL DEVELOPED**.

---

## 4. Novelty Assessment

* **Known Components**: Dirichlet Subjective Logic (Jøsang, 2016), Evidential Deep Learning (Sensoy et al., NeurIPS 2018), Modified Laplacian ($E_{lap}$), Temperature Scaling (Guo et al., ICML 2017).
* **Actual Contribution**: 
  1. Analytical upper bound proof on Dirichlet marginal variance ($\mathrm{Var}(p_k) \le \frac{1}{4(S+1)}$) and uniform contraction monotonicity (Theorem 1, Proposition 1).
  2. Integration of optical MTF blur filtering with Subjective Logic vacuity ($u = K/S$) into a single bounded metric $R_p \in [0, 1]$.
  3. Fail-closed architectural firewall intercepting corrupted frames before GPU vector extraction.
* **Reviewer Skepticism**: A skeptical reviewer might argue that Sensoy et al. already established EDL for classification; the authors' response must emphasize that Sensoy et al. did not provide the closed-form variance bound $\frac{1}{4(S+1)}$, did not incorporate frequency-domain optical blur, and did not formulate a multi-tier fail-closed cyber-physical gate.

---

## 5. Methodological Assessment

* **Mathematical Clarity**: Equations (4)–(12) are well-formulated. The Beta marginal derivation $p_k \sim \mathrm{Beta}(\alpha_k, S - \alpha_k)$ and conservation identity $\sum b_k + u = 1.0$ in Eq. (12) are mathematically precise.
* **Algorithm**: Algorithm 1 (lines 222–240) is complete and reproducible, specifying exact inputs, temperature scaling, blur extraction, dispersion calculation, and fail-closed interception ($\bot$).
* **Parameter Settings**: Weights are explicitly assigned ($w_u=0.35, w_d=0.25, w_b=0.25, w_k=0.15$) and threshold $\tau_{risk} = 0.70$ is clearly defined.

---

## 6. Theoretical Assessment

* **Theorem 1 (Dirichlet Variance Upper Bound)**: The proof (lines 140–154) is mathematically sound. The concavity of $f(z) = z(1-z)$ reaching its global maximum at $z=1/2$ ($f(1/2) = 1/4$) is standard and correctly applied. The minimum strength $S \ge K$ ensuring $\mathrm{Var}(p_k) < \frac{1}{4K}$ is rigorous.
* **Proposition 1 (Uniform Scaling Monotonicity)**: The derivative $\frac{\partial}{\partial c}\mathrm{Var} = -\frac{S_0 z(1-z)}{(c S_0 + 1)^2} < 0$ is correct.
* **Corollary 1 (Negative Covariance)**: Pairwise covariance $\mathrm{Cov}(p_i, p_j) = -\frac{\alpha_i \alpha_j}{S^2(S+1)} < 0$ is correctly derived from the Dirichlet joint second moment.
* **Proposition 2 (Lipschitz Continuity)**: Convex combination of Lipschitz functions preserves Lipschitz continuity.

---

## 7. Experimental / Evidence Assessment

* **Dataset & Hardware**: 2,000 frames evaluated on an edge-class ARM64 compute node across 5 standardized corruption regimes (Clean, Blur, Motion Smear, Noise, OOD).
* **Empirical Telemetry**: Table II and Table III report comprehensive metrics: AUROC (1.0000), FPR95 (0.0000), ECE reduction (0.4218 $\to$ 0.0412), Brier score (0.1793), and mean gating latency ($1.486\text{ ms}$).
* **What Evidence Establishes**: Demonstrates that for the tested 2,000 frames, combining evidential vacuity with optical blur filters cleanly separates in-distribution from corrupted frames in $1.486\text{ ms}$.
* **What Remains Unestablished**: Does not test extreme lighting transitions (e.g. strobe flicker, direct sunlight saturation) or physical lens cracking.

---

## 8. Discussion Assessment

* **3-Layer Standard**: Section IV-C strictly follows the WHAT $\to$ WHY $\to$ LIMIT structure.
* **Why Softmax Fails**: Explains how Dirichlet evidence accumulation isolates semantic emptiness from logit magnitude scaling.
* **Trade-Off Analysis**: Explains the trade-off of $\tau_{risk} = 0.70$, resulting in a $78.4\%$ fast-path pass rate and $21.6\%$ quarantine rate.

---

## 9. Limitations Assessment

* **Coverage**: Section V explicitly details physical failure boundaries (extreme underexposure where $|\nabla^2 I| \to 0$ and high-velocity smear where $E_{fft} \to 0$).
* **Honesty**: Acknowledges in Section IV-C3 that $\text{AUROC} = 1.0000$ is an empirical benchmark result, not an unconstrained universal theorem.
* **Missing Details**: Could briefly mention CMOS rolling-shutter wobble effects compared to global shutter blur.

---

## 10. Flow, Completeness & Length

* **Physical Pages**: Exactly 6.0 PDF pages. The paper is dense, well-balanced, and contains 2 algorithms/tables, multiple equations, and 25 references.
* **Flow**: Flawless narrative progression from problem $\to$ related taxonomy $\to$ Dirichlet math $\to$ experimental telemetry $\to$ failure boundaries $\to$ conclusion.
* **Article Type**: **FULL RESEARCH ARTICLE** (not a compressed technical note).

---

## 11. Language & Presentation

* Clean, formal academic English.
* Mathematical typography is rigorous and consistent.

---

## 12. Most Likely Reviewer Rejection Argument

> "The paper combines Dirichlet evidential learning with standard Laplacian/Fourier blur metrics. Since both components exist in prior literature, the technical novelty is primarily an engineering integration on an edge compute board."

---

## 13. Required Revisions (Pre-Submission Polish)

1. **Abstract Contextualization**: Clarify in the Abstract that $\text{AUROC} = 1.0000$ applies to the 2,000-sample benchmark suite to avoid skeptical reviewers perceiving it as an ungrounded claim.
2. **Rolling-Shutter Discussion**: Add one sentence in Section V-A acknowledging rolling-shutter geometric distortion vs global-shutter optical blur.

---

## 14. Final Recommendation

**MINOR REVISION** (High Accept Priority — Scientifically rigorous, mathematically sound, full 6-page research article).
