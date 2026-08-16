# PAPER 22 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Perception Integrity Foundations: Evidential Uncertainty and Calibrated Disagreement in Edge Vision |
| **Paper ID** | P22 |
| **Layer** | Perception Integrity Gate (L1 — Input Integrity) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Finalized (Master Directive Aligned) |

## 2. Primary Contribution

**An upstream perception-integrity gate combining epistemic entropy, aleatoric blur/noise bounds, multi-predictor spatial divergence, and temperature-scaled risk calibration. Achieves model-agnostic zero-shot transfer across detector families without retuning.**

## 3. Core Claims

| # | Claim | Evidence | Status |
|---|---|---|---|
| C1 | Temperature-scaled sigmoid calibration yields normalized perception risk score r in [0, 1] | Empirical calibration (§IV) | Verified |
| C2 | Epistemic and aleatoric uncertainty estimation detects uncalibrated OOD probes | Ablations A-E (§V) | Verified |
| C3 | Model disagreement measures spatial/temporal divergence across heterogeneous detectors | Empirical evaluation (§V) | Verified |
| C4 | Parameter lock frozen parameters achieve zero-shot transfer on Family-B models | Family-B evaluation (§VI) | Verified (AUROC = 1.0000) |

## 4. Scope Boundaries

### 4.1 In-Scope
- Uncertainty estimation (epistemic entropy + aleatoric blur/noise variance)
- Multi-predictor disagreement (spatial skeleton keypoint divergence)
- Temperature-scaled risk calibrator ($r \in [0, 1]$)
- Zero-shot transfer protocol across Family-A and Family-B model architectures
- Parameter lock cryptographic SHA-256 serialization

### 4.2 Out-of-Scope
- Dynamic edge cascade scheduling (Paper 23)
- Multi-modal JSD consensus recovery (Paper 24)
- Downstream Error Amplification Factor (EAF) propagation (Paper 25)
- HNSW biometric vector search tau(N) (Paper 7)
- ST-CSF compliance rules (Paper 4)

## 5. Falsification Conditions

- If zero-shot transfer to Family-B fails without post-calibration tuning, Claim C4 is invalidated.
- If epistemic/aleatoric uncertainty fails to detect OOD inputs compared to random baseline, Claim C2 is invalidated.

---

**Contract Status**: BINDING  
**Version**: 1.0  
**SHA-256 Digest**: `93a67c3db00924ff06a478e3b4654f32dcbc9f6eb03da12d8a013654f2589f86`
