# PAPER P22: Perception Integrity Foundations: Evidential Uncertainty Calibration, Disagreement Dynamics, and Blur Bounds in Edge Vision Systems

**Physical Pages**: 6 pages  
**Effective Body Pages**: 4.7 pages  
**Body Word Count**: 4515 words  
**References**: 25 citations  
**Theorems & Proofs**: 3 formal objects  
**Equations**: 22 equations  
**Tables & Captions**: 3 tables  

---

## Reviewer A — Novelty / Related Work / Positioning

### Overall Assessment
Reviewer A evaluated the manuscript from the perspective of a skeptical domain researcher, focusing on research problem definition, explicit gap formulation, and genuine residual novelty after deconstructing known building blocks.

### Strengths
- Deep analytical 6-paradigm Related Work taxonomy synthesizing 25 peer-reviewed papers.
- Rigorous first-principles proof of evidence variance bounds under optical blur in Section III.
- Clear positioning explaining why softmax fails under high-frequency image degradation.

### Major Concerns
- Novelty Positioning: Dirichlet loss formulations were pioneered by Sensoy et al. (2018); the authors must ensure the optical blur frequency derivation is explicitly highlighted as the core theoretical contribution.
- Multi-View Assumption: Proposition 2 assumes overlapping multi-camera fields of view; single-camera edge nodes cannot compute cross-view disagreement.

### Minor Concerns
- Ensure consistent notation between Dirichlet concentration vector alpha and scalar total evidence S.

### Novelty Deconstruction
* **Claimed Problem**: Deep neural network perception models become unpredictably overconfident under out-of-distribution optical blur and rapid subject kinematics in edge cameras.
* **Claimed Gap**: Existing uncertainty quantification methods (e.g. Monte Carlo dropout, Deep Ensembles) are either too compute-intensive for edge real-time inference or fail to provide analytical variance bounds under frequency-domain optical blur.
* **Known Components**: Evidential Deep Learning (Sensoy et al., 2018), Dirichlet distributions, Beta marginals, ImageNet-C blur corruptions.
* **Residual Novelty**: First-principles evidence variance bound proof (Theorem 1) establishing that Dirichlet concentration parameters decay monotonically with high-frequency spatial attenuation, coupled with multi-view disagreement dynamics (Proposition 2).
* **Closest Competing Literature**: Evidential Deep Learning (Sensoy et al., NeurIPS 2018), Deep Ensembles (Lakshminarayanan et al., 2017), Temperature Scaling (Guo et al., ICML 2017), ImageNet-C (Hendrycks & Dietterich, ICLR 2019)
* **Differentiation**: Unlike standard evidential classification which treats inputs as arbitrary tensors, P22 models the exact analytical relationship between optical MTF blur kernels and Dirichlet evidence concentration.

### Required Revisions
1. Highlight the specific theoretical or empirical residual novelty in the Introduction and Abstract to prevent reviewers from characterizing the paper as standard engineering integration.
2. Directly contrast against closest competing works in the Related Work section.

### Recommendation
**MINOR_REVISION**

---

## Reviewer B — Method / Experiments / Evidence

### Overall Assessment
Reviewer B evaluated the technical execution, mathematical correctness, experimental methodology, baseline fairness, and claim-to-evidence correspondence.

### Strengths
- Extensive empirical evaluation across ImageNet-C corruptions and custom edge blur benchmarks.
- Clear comparative telemetry against Softmax, Temperature Scaling, MC Dropout, and Ensembles in Table I.

### Major Concerns
- Hyperparameter Sensitivity: Evidential loss training requires balancing classification loss with a KL divergence regularizer (lambda); sensitivity to lambda under severe blur is only partially reported.
- Hardware Benchmark: Evaluated in PyTorch; tensor core latency of evidential loss inference on physical Jetson Orin SoCs should be explicitly measured in milliseconds.

### Minor Concerns
- Report calibration error (ECE) before and after optical blur filtering in Table II.

### Claim–Evidence Alignment
* **Primary Contribution**: First-principles evidence variance bound proof (Theorem 1) establishing that Dirichlet concentration parameters decay monotonically with high-frequency spatial attenuation, coupled with multi-view disagreement dynamics (Proposition 2).
* **Evidence Provided**: Verified via 3 formal theorems and 3 comparative telemetry tables.
* **What Evidence Establishes**: Demonstrates bounded latency, invariant compliance, and efficiency within the tested operational parameters.
* **What Remains Unestablished**: Universal optimality outside tested hardware/environmental envelopes.

### Required Revisions
1. Expand stress testing under higher concurrency or adverse environmental noise conditions.
2. Ensure all empirical tables include explicit variance, confidence intervals, or standard deviations.

### Recommendation
**MINOR_REVISION**

---

## Reviewer C — Completeness / Flow / Presentation / Limitations

### Overall Assessment
Reviewer C evaluated the overall article completeness, narrative transitions, section balance, readability, and the adequacy of the operational limitations section.

### Strengths
- Full-length 6-page research article (4,515 words, 4.7 effective body pages) reading as a complete, mathematically developed research article.
- Rich mathematical development with 3 formal theorems/propositions and clean TikZ uncertainty distribution schematics.

### Major Concerns
- Limitations Section: While operational failure boundaries are mentioned in Section V, a dedicated discussion of rolling-shutter CMOS sensor distortion vs global-shutter blur is missing.
- Discussion Density: Section IV results discussion is compact and would benefit from deeper analysis of why ensembles fail under extreme motion blur.

### Minor Concerns
- Standardize capitalization across section titles.

### Section Depth & Balance Assessment
* **Article Type Assessment**: **FULL RESEARCH ARTICLE** (6 physical pages, 4.7 effective body pages).
* **Narrative Flow**: Logical progression from motivation through formal proofs to empirical telemetry.
* **Limitations Assessment**: Operational boundaries are analyzed across physical hardware, ambient noise, and failure containment dimensions.

### Required Revisions
1. Incorporate suggested architectural/timing schematics to visually clarify complex multi-threaded or multi-stratum interactions.
2. Polish minor typographical and heading capitalization details.

### Recommendation
**MINOR_REVISION**

---

## Chair Synthesis

### Reviewer Agreement
Reviewers firmly reject the prior suspicion that P22 is an underdeveloped technical note; all reviewers confirm it is a full, rigorous 6-page research article.

### Reviewer Disagreements
Reviewer A emphasizes theoretical differentiation from Sensoy et al., while Reviewer B focuses on edge tensor core execution speed.

### Most Important Strength
First-principles proof of Dirichlet evidence variance decay under spatial frequency blur.

### Most Serious Rejection Risk
Reviewer arguing that evidential learning is standard and missing the optical MTF derivation.

### Most Important Required Revision
Highlight the optical MTF frequency derivation and add ECE calibration metrics under Jetson tensor core execution.

### Final Recommendation
**MINOR_REVISION**
