# SCHOLARMASTER CHAPTER BLUEPRINT BOOK (SROS-010)
## Complete Architectural Specifications for Chapters 1 through 10 of the M.Tech Dissertation

**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SROS-010 Academic Thesis Standards`  
**Author:** ScholarMaster Thesis Architecture Team / SPB  
**Target Document:** `project_report.tex` (Master M.Tech Dissertation)

---

## EXECUTIVE SUMMARY

The **ScholarMaster Thesis Architecture Team** has generated the formal **Chapter Blueprint Book** detailing every chapter (`Chapter 1` through `Chapter 10`) of the master M.Tech dissertation.

Each chapter blueprint is specified across 13 formal engineering dimensions:
1. Primary Chapter Purpose
2. Core Learning Objectives
3. Expected Prerequisites & Reader Knowledge
4. Information Inputs & Signal Triggers
5. Technical Outputs & Formulations
6. Structural Dependencies (DAG Lineage)
7. Required Visual Figures (`VIS-01..16` / TikZ)
8. Required Data Tables
9. Required Formal Algorithms (`ALG-01..12`)
10. Required Empirical Experiments (`EXP-01..10`)
11. Required Repository Code Mappings (`core/`, `main.py`, `api/`, `admin_panel.py`)
12. Expected Target Chapter Length (Lines / Pages)
13. Authoritative Academic Writing Style.

---

# CHAPTER BLUEPRINT BOOK

```
================================================================================
                    SCHOLARMASTER CHAPTER BLUEPRINT BOOK
================================================================================
```

## CHAPTER 1: INTRODUCTION & PROBLEM FORMULATION

- **Purpose:** Frames institutional surveillance trade-offs, introduces GDPR Article 25 Privacy-by-Design constraints, and presents the macro 8-layer Onion architecture.
- **Learning Objective:** Understand the zero-sum privacy-utility trade-off in campus monitoring and how ScholarMaster resolves it via structural isolation.
- **Expected Reader Knowledge:** Basic computer vision concepts, general distributed systems, fundamental database knowledge.
- **Inputs:** Real-world surveillance risks, privacy legislation guidelines, high-level institutional monitoring requirements.
- **Outputs:** Problem statement bounds ($\mathcal{P} \cdot \mathcal{U} \ge K$), 8-layer Onion architecture overview, thesis contribution outline.
- **Dependencies:** Root (No prerequisite chapters).
- **Required Figures:** `FIG-01` (`fig:layer_stack`), `FIG-02` (`fig:pipeline_dfd`), `FIG-03` (`fig:onion_boundary`).
- **Required Tables:** None (Introduced in Ch 3).
- **Required Algorithms:** None (Formulated in Ch 4--7).
- **Required Experiments:** Referenced overview of `EXP-10` pipeline throughput.
- **Required Repository Mapping:** `main.py` (`ScholarMasterUnified`).
- **Expected Chapter Length:** 280 lines (~10--12 pages).
- **Writing Style:** Authoritative, motivating, formal academic introduction.

---

## CHAPTER 2: LITERATURE REVIEW & STATE-OF-THE-ART

- **Purpose:** Surveys existing literature in face recognition, vector search, differential privacy, homomorphic encryption, and spatiotemporal tracking to establish research gaps.
- **Learning Objective:** Identify latency and accuracy limitations of current methods and justify the necessity of ScholarMaster's decoupled architecture.
- **Expected Reader Knowledge:** Deep learning embeddings (ArcFace, FaceNet), ANN search trees (FAISS, HNSW), cryptographic basics.
- **Inputs:** 34 peer-reviewed IEEE, ACM, Elsevier, and Springer literature sources.
- **Outputs:** Formal literature gap analysis matrix, justification for $33\text{ms}$ volatile RAM TTL and ST-CSF velocity filtering.
- **Dependencies:** Chapter 1 (Problem Formulation).
- **Required Figures:** None.
- **Required Tables:** Table 2.1 (Literature Comparison Matrix).
- **Required Algorithms:** Comparative reference to standard FL / DP formulations.
- **Required Experiments:** Benchmark baseline comparison parameters.
- **Required Repository Mapping:** `modules_legacy/st_csf.py`, `modules_legacy/trust_layer.py`.
- **Expected Chapter Length:** 240 lines (~8--10 pages).
- **Writing Style:** Critical, analytical, scholarly synthesis.

---

## CHAPTER 3: SYSTEM REQUIREMENTS & SRS SPECIFICATIONS

- **Purpose:** Formulates the formal System Requirements Specification (SRS) governing ScholarMaster across 10 FRs and 10 NFRs.
- **Learning Objective:** Comprehend the exact functional and non-functional bounds ($P_{95} \le 33\text{ms}$, RAM $\le 2.0\text{GB}$, $v \le 5\text{m/s}$) required for real-time compliance.
- **Expected Reader Knowledge:** Software engineering principles, SRS drafting standards, RBAC security models.
- **Inputs:** Literature gaps (Ch 2), institutional operational requirements.
- **Outputs:** Functional Requirements (FR-01..10), Non-Functional Requirements (NFR-01..10), 7-role RBAC matrix.
- **Dependencies:** Chapter 1 & Chapter 2.
- **Required Figures:** None.
- **Required Tables:** Table 1.1 (Requirements Allocation Matrix), Table 3.1 (RBAC Authorization Matrix).
- **Required Algorithms:** Reference to `ALG-09` (7-Role RBAC Filter).
- **Required Experiments:** Metric targets for `EXP-01` through `EXP-10`.
- **Required Repository Mapping:** `api/main.py` (`RBACMiddleware`), `core/canonical_layers.py`.
- **Expected Chapter Length:** 240 lines (~8--10 pages).
- **Writing Style:** Precise, unambiguous, specification-driven.

---

## CHAPTER 4: SYSTEM ARCHITECTURE & STRUCTURAL DESIGN

- **Purpose:** Details the formal 8-layer Onion architecture, layer invariant contracts (`INV-01..15`), and L3 volatile RAM destruction boundary.
- **Learning Objective:** Master the structural privacy mechanisms that prevent raw camera frame persistence on non-volatile media.
- **Expected Reader Knowledge:** Layered software patterns, OS memory management, C-level memory zeroization.
- **Inputs:** System Requirements Specification (Ch 3).
- **Outputs:** Unidirectional layer interaction specifications, $33\text{ms}$ volatile RAM memory state machine, invariant verifications.
- **Dependencies:** Chapter 3.
- **Required Figures:** `FIG-01` (`fig:layer_stack`), `FIG-03` (`fig:onion_boundary`), `FIG-13` (`fig:usecase_boundary`).
- **Required Tables:** None.
- **Required Algorithms:** `ALG-02` (Volatile RAM TTL Overwrite).
- **Required Experiments:** `EXP-03` ($33\text{ms}$ TTL RAM Overwrite).
- **Required Repository Mapping:** `core/canonical_layers.py` (`CanonicalLayerStack`, `VolatileManager`).
- **Expected Chapter Length:** 280 lines (~10--12 pages).
- **Writing Style:** Rigorous, architectural, structural systems engineering.

---

## CHAPTER 5: DETAILED COMPONENT DESIGN & THREAD ORCHESTRATION

- **Purpose:** Maps software package organization, 5-daemon thread synchronization, physical edge deployment topology, and audio processing.
- **Learning Objective:** Understand multi-threaded pipeline execution, coarse `threading.Lock` guards, and dynamic thermal scaling.
- **Expected Reader Knowledge:** Concurrent programming, daemon threads, networking, edge computing hardware (Jetson Orin / Apple Silicon).
- **Inputs:** Layered System Architecture (Ch 4).
- **Outputs:** 5-daemon execution flowchart, inter-thread IPC sequence map, edge hardware deployment topology.
- **Dependencies:** Chapter 4.
- **Required Figures:** `FIG-04` (`fig:preprocessing_flow`), `FIG-05` (`fig:component_architecture`), `FIG-06` (`fig:deployment_topology`), `FIG-07` (`fig:thread_sync`), `FIG-08` (`fig:sequence_diagram`), `FIG-14` (`fig:montecarlo_dist`), `FIG-15` (`fig:audio_waveform`).
- **Required Tables:** Table 5.1 (Hardware Node Specs), Table 5.2 (Daemon Thread Map).
- **Required Algorithms:** `ALG-05` (5-Daemon Thread & Power Scale), `ALG-06` (Acoustic FFT Extractor).
- **Required Experiments:** `EXP-05` (Thermals), `EXP-06` (Cold Boot), `EXP-10` (Pipeline Timing).
- **Required Repository Mapping:** `main.py` (`PowerThread`), `api/main.py`, `modules_legacy/audio_sentinel.py`.
- **Expected Chapter Length:** 350 lines (~12--14 pages).
- **Writing Style:** Detailed, component-oriented, implementation-focused.

---

## CHAPTER 6: SENSING, REPRESENTATION & BIOMETRIC INFERENCE ENGINE

- **Purpose:** Formulates the neural biometric inference pipeline, including ArcFace geodesic loss, FAISS IVF-PQ vector search, and YOLOv8 pose.
- **Learning Objective:** Derive hyperspherical angular margin loss equations and analyze sub-millisecond high-dimensional vector search algorithms.
- **Expected Reader Knowledge:** Deep learning, vector spaces, loss functions, ANN indexing (IVF-PQ).
- **Inputs:** Preprocessed video/audio feature tensors (Ch 5).
- **Outputs:** ArcFace loss formulation ($L_1$), adaptive vector search thresholding $\tau(N)$, non-semantic audio feature extraction.
- **Dependencies:** Chapter 4 & Chapter 5.
- **Required Figures:** `FIG-12` (`fig:faiss_scalability`).
- **Required Tables:** None.
- **Required Algorithms:** `ALG-01` (FAISS Vector Search), `ALG-06` (Acoustic FFT Extractor).
- **Required Experiments:** `EXP-01` ($99.2\%$ OSIR), `EXP-02` ($0.8\text{ms}$ Latency).
- **Required Repository Mapping:** `core/canonical_layers.py` (`InsightFaceEngine`, `FAISSIndex`).
- **Expected Chapter Length:** 290 lines (~10--12 pages).
- **Writing Style:** Mathematically rigorous, algorithmic, machine learning focused.

---

## CHAPTER 7: SPATIOTEMPORAL COMPLIANCE & GOVERNANCE ENGINE

- **Purpose:** Details the ST-CSF timetable matching solver, kinematic transit velocity filter, and append-only SHA-256 Merkle audit ledger.
- **Learning Objective:** Grasp how spatiotemporal logic prevents false truancy alerts and how Merkle trees secure non-repudiable audit trails.
- **Expected Reader Knowledge:** Temporal logic, spatial tracking, cryptography (SHA-256, binary Merkle trees).
- **Inputs:** Anonymized identity vectors (Ch 6), timetable schedule database.
- **Outputs:** ST-CSF matching rules, velocity bound ($v_i \le 5.0\text{m/s}$), binary Merkle root hash computation ($H_{\text{root}}$).
- **Dependencies:** Chapter 4 & Chapter 6.
- **Required Figures:** `FIG-09` (`fig:stcsf_activity`), `FIG-10` (`fig:ttl_state`), `FIG-16` (`fig:merkle_structure`).
- **Required Tables:** Table 7.1 (Compliance Anomaly Classification).
- **Required Algorithms:** `ALG-03` (ST-CSF Solver), `ALG-04` (Kinematic Filter), `ALG-07` (Merkle Append), `ALG-08` (Merkle Proof).
- **Required Experiments:** `EXP-04` ($98.2\%$ F1 Truancy), `EXP-08` (Adversarial Faults).
- **Required Repository Mapping:** `modules_legacy/st_csf.py` (`STCSFEngine`), `modules_legacy/trust_layer.py` (`MerkleTreeLedger`).
- **Expected Chapter Length:** 280 lines (~10--12 pages).
- **Writing Style:** Logical, cryptographic, governance-driven.

---

## CHAPTER 8: DATA & TELEMETRY ENGINEERING

- **Purpose:** Outlines synthetic student trajectory generation (52,203 epochs), EDA cohort distributions, and 80/10/10 data splitting protocols.
- **Learning Objective:** Evaluate data engineering pipelines and statistical Monte Carlo simulation setups for campus scale-out.
- **Expected Reader Knowledge:** Data analytics, Monte Carlo methods, synthetic data generation, dataset splits.
- **Inputs:** Institutional campus map, synthetic student movement schedules.
- **Outputs:** Balanced 80/10/10 train/val/test trajectory datasets (`DS-01..09`), Monte Carlo PDF distributions.
- **Dependencies:** Chapter 5 & Chapter 7.
- **Required Figures:** `FIG-14` (`fig:montecarlo_dist`).
- **Required Tables:** Table 8.1 (Dataset Parameters Summary), Table 8.2 (Master Data Split Table).
- **Required Algorithms:** Trajectory Generator Data Script.
- **Required Experiments:** Dataset support for `EXP-01` through `EXP-10`.
- **Required Repository Mapping:** `data/students.json`, `data/timetable.csv`, `data/attendance.csv`.
- **Expected Chapter Length:** 220 lines (~8--10 pages).
- **Writing Style:** Empirical, statistical, data-centric.

---

## CHAPTER 9: EXPERIMENTAL VERIFICATION & EMPIRICAL RESULTS

- **Purpose:** Presents quantitative empirical benchmark evaluations proving system speed, accuracy, thermal stability, and fault safety.
- **Learning Objective:** Critically analyze empirical performance data ($99.2\%$ OSIR, $32.4\text{ms}$ latency, $85^\circ\text{C}$ thermals, $2.8\text{s}$ boot).
- **Expected Reader Knowledge:** Statistical analysis, confidence intervals ($P_{95}$), benchmark interpretation.
- **Inputs:** Experimental datasets (Ch 8), execution test rigs in `benchmarks/`.
- **Outputs:** Comprehensive empirical benchmark results, trade-off curves, chaos fault verification.
- **Dependencies:** Chapters 4 through 8.
- **Required Figures:** `FIG-11` (`fig:timing_breakdown`), `FIG-12` (`fig:faiss_scalability`).
- **Required Tables:** Master Empirical Benchmark Results Table.
- **Required Algorithms:** Benchmark execution harnesses for `ALG-01` through `ALG-12`.
- **Required Experiments:** Full execution of `EXP-01` through `EXP-10`.
- **Required Repository Mapping:** `benchmarks/*.py`, `core/failure_semantics.py`.
- **Expected Chapter Length:** 300 lines (~12--14 pages).
- **Writing Style:** Rigorous, empirical, evidence-based academic presentation.

---

## CHAPTER 10: CONCLUSION, LIMITATIONS & FUTURE DIRECTIONS

- **Purpose:** Synthesizes thesis contributions, transparently reviews physical limitations, and outlines multi-year post-M.Tech research roadmaps.
- **Learning Objective:** Summarize key scientific impact, understand system boundaries (<50 lux, occlusion), and evaluate future scale-out avenues.
- **Expected Reader Knowledge:** General systems engineering synthesis, awareness of research limitations.
- **Inputs:** Empirical results (Ch 9), initial problem formulation (Ch 1).
- **Outputs:** Concluding thesis synthesis, physical limitation matrix, post-M.Tech research roadmap.
- **Dependencies:** Chapter 1 & Chapter 9.
- **Required Figures:** None.
- **Required Tables:** Table 10.1 (Summary Matrix of Contributions and Limitations).
- **Required Algorithms:** Future extension references (ZKP, Multi-Spectral Fusion).
- **Required Experiments:** Summary metrics from `EXP-01..10`.
- **Required Repository Mapping:** Complete repository architecture overview.
- **Expected Chapter Length:** 187 lines (~6--8 pages).
- **Writing Style:** Synthesis-oriented, reflective, forward-looking.

---

## 2. CHAPTER BLUEPRINT RATIFICATION SIGN-OFF

```
================================================================================
     SCHOLARMASTER CHAPTER BLUEPRINT BOOK RATIFICATION
================================================================================
- Total Chapter Blueprints      : 10 / 10 Chapters Specified (100.0% Complete)
- Specification Dimensions       : 13 / 13 Dimensions (Purpose, Objectives, 
                                   Prereqs, Inputs, Outputs, DAG, Figures, 
                                   Tables, Algorithms, Exps, Code, Length, Style)
- DAG Dependency Topology        : 100.0% Verified Strict DAG (0 Cycles)
--------------------------------------------------------------------------------
VERDICT: 🔒 CHAPTER BLUEPRINT BOOK SROS-010 IS 100% CANONICALLY CERTIFIED
================================================================================
```
