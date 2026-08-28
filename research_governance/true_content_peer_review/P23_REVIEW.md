# PAPER P23: Adaptive Trustworthy Edge Systems: Dynamic Risk-Driven Hardware Operating Envelopes, Schedulability, and Thermal Equilibrium in Multi-Tenant Analytics

**Physical Pages**: 6 pages  
**Effective Body Pages**: 4.7 pages  
**Body Word Count**: 4676 words  
**References**: 26 citations  
**Theorems & Proofs**: 2 formal objects  
**Equations**: 14 equations  
**Tables & Captions**: 3 tables  

---

## Reviewer A — Novelty / Related Work / Positioning

### Overall Assessment
Reviewer A evaluated the manuscript from the perspective of a skeptical domain researcher, focusing on research problem definition, explicit gap formulation, and genuine residual novelty after deconstructing known building blocks.

### Strengths
- 26 peer-reviewed citations structured into a 6-paradigm analytical hardware operating taxonomy.
- Formal queueing theory formulation linking packet arrival rates to precision budget modulation.
- Clear problem statement addressing multi-tenant resource starvation on edge SoCs.

### Major Concerns
- Novelty: Quantization switching and queueing schedulers are well-studied; the novelty lies in the combined closed-loop thermal-precision governor. The paper must emphasize this closed-loop coupling.
- Assumptions: Assumes deterministic execution times for INT8 and FP16 kernels; memory bus contention from concurrent CPU processes can violate this assumption.

### Minor Concerns
- Clarify notation for queue service rate mu under dynamic clock scaling.

### Novelty Deconstruction
* **Claimed Problem**: Thermal throttling and deadline violations in multi-tenant edge vision systems subjected to bursty concurrent inference requests.
* **Claimed Gap**: Existing edge schedulers either apply static quantization (causing permanent accuracy loss) or naive DVFS clock throttling (causing catastrophic frame drops and deadline misses).
* **Known Components**: INT8/FP16 dynamic quantization, M/M/1 and G/G/1 queueing models, Linux DVFS governors, TensorRT.
* **Residual Novelty**: Constrained optimization formulation proving deadline schedulability while dynamically modulating GPU tensor precision under closed-loop thermal equilibrium bounds (Theorem 1, Proposition 1).
* **Closest Competing Literature**: Dynamic Quantization (Jacob et al., CVPR 2018), Queueing Theory in Edge Computing (Satyanarayanan, 2017), Energy-Aware Scheduling (Chen et al., 2019), DeepScale (Lin et al., 2020)
* **Differentiation**: Unlike static schedulers, P23 proves closed-form queue backlog bounds while dynamically modulating INT8/FP16 precision budgets, maintaining sub-45°C SoC equilibrium at sustained 30 FPS.

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
- Physical hardware telemetry on NVIDIA Jetson Orin showing 0 deadline misses and sub-45°C operating stability.
- Clear comparative telemetry tables contrasting static FP16, static INT8, and dynamic precision budgeting.

### Major Concerns
- Kernel Context Switch Overhead: Rapid switching between INT8 and FP16 TensorRT engine contexts can incur CUDA driver reload latency; this reload latency must be quantified.
- Accuracy Trade-Off: Quantization error during dynamic INT8 downscaling should be evaluated across diverse lighting conditions.

### Minor Concerns
- Provide a Pareto frontier plot of accuracy vs latency vs thermal power.

### Claim–Evidence Alignment
* **Primary Contribution**: Constrained optimization formulation proving deadline schedulability while dynamically modulating GPU tensor precision under closed-loop thermal equilibrium bounds (Theorem 1, Proposition 1).
* **Evidence Provided**: Verified via 2 formal theorems and 3 comparative telemetry tables.
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
- Full-length 6-page research article (4,676 words, 4.7 effective body pages) with comprehensive mathematical formulation.
- Well-structured discussion of failure boundaries and overload containment in Section V.

### Major Concerns
- Clarity: The interaction between the Linux kernel DVFS governor and the application-level precision manager needs clearer architectural visualization.
- Terminology: Terms like 'dynamic precision budget' and 'operating envelope' should be rigorously defined in Section I.

### Minor Concerns
- Ensure all equation variables are indexed in a nomenclature table.

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
Reviewers confirm P23 is a substantive full-length research paper with solid mathematical queueing models and real hardware telemetry.

### Reviewer Disagreements
Reviewer B raises practical questions regarding CUDA kernel context reload latency, while Reviewer A focuses on scheduling novelty.

### Most Important Strength
Constrained optimization formulation proving deadline schedulability under thermal equilibrium.

### Most Serious Rejection Risk
Reviewer questioning kernel reload latency during high-frequency quantization switching.

### Most Important Required Revision
Quantify CUDA context switch overhead and provide an accuracy-thermal Pareto frontier plot.

### Final Recommendation
**MINOR_REVISION**
