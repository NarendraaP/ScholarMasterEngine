# PAPER 2 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | A Context-Aware Multi-Modal Framework for Asymmetric Risk Control in Student Engagement Analysis |
| **Paper ID** | P2 |
| **Layer** | Multi-Modal Fusion Layer |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Initialized |

## 2. Primary Contribution

**A context-aware logical fusion framework that applies a Bayesian prior shift to visual engagement metrics using acoustic lexical density and schedule metadata, reducing asymmetric false-negative errors during high-load instruction.**

Paper 2 establishes the fusion layer that prevents unimodal visual classifiers from misinterpreting concentrated cognitive effort as disengagement. It formalizes this correction as a "Valence Discrepancy" and uses domain-specific ASR to compute a contextual load factor that re-weights the decision boundary.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Visual models systematically misclassify high-load concentration as disengagement (Valence Discrepancy). | Sim-Class-24 Baseline (42.0% Sim-FNR-HL) | Clean |
| C2 | Lexical density derived from ASR can serve as an effective proxy for germane cognitive load. | Eq 6 | Clean |
| C3 | Applying a sigmoid Bayesian prior shift based on load reduces false negatives. | Eq 7, Table 2 (6.0% Sim-FNR-HL) | Clean |
| C4 | This logic layer outperforms opaque cost-sensitive deep learning models while preserving interpretability. | Table 1 | Clean |

## 4. Scope

### 4.1 In-Scope
- Multi-modal fusion logic (Visual + Acoustic + Schedule)
- Bayesian prior adjustment formulations (Eq 5-7)
- Validation against the Sim-Class-24 dataset
- Semantic density extraction logic via VAD and ASR dictionaries

### 4.2 Out-of-Scope (Strictly Forbidden)
- **Acoustic Signal Processing** (Owned by P6 - P2 focuses on semantic tokens, not acoustic localization)
- **Relational Schedule Enforcement** (Owned by P4)
- **Deep Learning Model Architectures** (Owned by P13 - P2 focuses on the fusion *logic*, not designing the underlying ASR model)

## 5. Potential Overlap Risks (Pending Audit)

- **Privacy Invariants (P3 / P8):** P2 mentions applying CLAHE to raw RGB frames for valence extraction. This must be carefully scoped to avoid violating the volatile memory / no-RGB-persistence constraints established in P3.
- **Validation (P10):** P2 uses Sim-Class-24. We must ensure it only claims logical validation, not full system throughput.

## 6. What This Paper Does NOT Do

- Does **not** design the physical acoustic sensors or edge hardware.
- Does **not** train the foundational ASR models (it treats them as oracles/extractors).
- Does **not** execute schedule compliance penalties.
