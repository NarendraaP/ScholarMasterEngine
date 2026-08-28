# PAPER P01: ScholarMaster: A Layered Edge-Native Architecture for Real-Time Campus Intelligence and Privacy-Preserving Governance

**Physical Pages**: 7 pages  
**Effective Body Pages**: 5.7 pages  
**Body Word Count**: 4983 words  
**References**: 25 citations  
**Theorems & Proofs**: 0 formal objects  
**Equations**: 1 equations  
**Tables & Captions**: 4 tables  

---

## Reviewer A — Novelty / Related Work / Positioning

### Overall Assessment
Reviewer A evaluated the manuscript from the perspective of a skeptical domain researcher, focusing on research problem definition, explicit gap formulation, and genuine residual novelty after deconstructing known building blocks.

### Strengths
- Comprehensive architectural formulation with 12 structured sections defining canonical strata boundaries.
- Explicit threat model articulating the hazards of cross-layer memory and state leakage.
- Structured Related Architectural Paradigms section contrasting against distributed middleware.

### Major Concerns
- Novelty Risk: The 4-stratum stack combines well-known software engineering patterns (POSIX shared memory, microservices, layered architecture). A skeptical reviewer could argue this is an architectural integration rather than a new foundational paradigm.
- Differentiation: The manuscript must more aggressively articulate why existing robotics/edge middleware (ROS 2, Plasma Store) cannot simply be configured with read-only permissions to achieve the same result.

### Minor Concerns
- Section II could expand on memory footprint comparisons across different ring buffer queue depths.

### Novelty Deconstruction
* **Claimed Problem**: Operational fragility and privacy leakage in monolithic smart-campus sensing pipelines where high-level policy code directly consumes raw sensor buffers.
* **Claimed Gap**: Lack of a formally decoupled multi-stratum edge architecture that isolates raw sensor ingestion from downstream compliance reasoning via volatile zero-copy memory barriers.
* **Known Components**: POSIX shared memory ring buffers, multi-threaded pipeline middleware, Unix domain sockets, 4-tier architectural patterns.
* **Residual Novelty**: Formalization of the 4-Stratum boundary invariants (Physical Ingestion, Feature Projection, Relational Compliance, Cryptographic Audit) with mathematical zero-overwrite memory confinement.
* **Closest Competing Literature**: ROS 2 (Macenski et al., 2020), EdgeX Foundry (Linux Foundation, 2021), Ray / Plasma Store (Moritz et al., 2018), ZeroMQ (Hintjens, 2013)
* **Differentiation**: Unlike ROS 2 and EdgeX which rely on serialized inter-process messaging, P1 enforces zero-copy volatile ring buffers with bounded memory lifetimes, preventing raw frame persistence.

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
- Concrete memory latency breakdown (0.42 ms to 1.1 ms) across inter-stratum boundaries.
- Detailed operational trace walkthrough in Section VI (attendance validation event lifecycle).

### Major Concerns
- Concurrency Limits: Stress evaluation is limited to 16 concurrent worker threads; IPC contention and cache line invalidation under 64+ contending workers on multi-NUMA edge servers is not evaluated.
- Platform Specificity: Relies heavily on POSIX shared memory primitives; portability to non-POSIX embedded RTOS environments is unverified.

### Minor Concerns
- Ensure standard deviation bars are provided for the latency measurements in Table I.

### Claim–Evidence Alignment
* **Primary Contribution**: Formalization of the 4-Stratum boundary invariants (Physical Ingestion, Feature Projection, Relational Compliance, Cryptographic Audit) with mathematical zero-overwrite memory confinement.
* **Evidence Provided**: Verified via 0 formal theorems and 4 comparative telemetry tables.
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
- Full-length 7-page article (4,983 body words) with thorough discussion of regulatory and institutional deployment considerations.
- Clear scientific narrative progressing from fragility through strata definitions to operational traces.

### Major Concerns
- Missing Architectural Sequence Diagram: The text describes the event flow through Stratum I-IV in Section VI, but lacks an end-to-end UML/TikZ sequence diagram illustrating thread lifecycles.
- Failure Modes: Section VII discusses cross-layer leakage hazards but lacks an explicit protocol for handling buffer overflow when Stratum III falls behind Stratum I.

### Minor Concerns
- Capitalization in subsection headings should be standardized.

### Section Depth & Balance Assessment
* **Article Type Assessment**: **FULL RESEARCH ARTICLE** (7 physical pages, 5.7 effective body pages).
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
All reviewers recognize P1 as a thorough, well-written foundational architecture paper establishing the core framework for the series.

### Reviewer Disagreements
Reviewer A questions whether 4-stratum separation constitutes theoretical novelty, while Reviewer B and C emphasize its practical systems and governance value.

### Most Important Strength
Clear formalization of the 4-stratum boundary invariants and zero-copy memory isolation.

### Most Serious Rejection Risk
Reviewer characterizing the paper as an engineering whitepaper/design pattern rather than a novel computing systems contribution.

### Most Important Required Revision
Add a formal sequence diagram and provide direct quantitative latency comparisons against ROS 2 under heavy concurrency.

### Final Recommendation
**MINOR_REVISION**
