# PAPER 6 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Edge-Based NLOS Acoustic Safety Monitoring via Spectral Gating and GCC-PHAT |
| **Paper ID** | P6 |
| **Layer** | Edge Signal Processing (L3 — Acoustic Sensor Layer) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Finalized (Boundary Enforced) |

## 2. Primary Contribution

**An edge-native acoustic monitoring pipeline capable of detecting high-decibel impulsive events originating from visually occluded regions (NLOS) within reverberant environments, utilizing deterministic physics-based signal processing rather than deep semantic classification.**

Paper 6 operates strictly at the signal processing layer. It bridges the gap between raw physical sensor hardware and high-level evaluation engines by filtering and interpreting raw audio waves into structural metadata.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Logarithmic Spectral Gating ($\delta$) effectively separates broadband impulsive events from low-frequency mechanical impacts | Algorithm 1 + Fig 1 | Clean |
| C2 | Autocorrelation-derived Periodic Rejection ($\rho$) reduces recurring mechanical false positives | Algorithm 1 | Clean |
| C3 | GCC-PHAT accurately estimates source azimuth in multipath-dominant indoor reverberant environments ($\mathcal{R}_{rev}$) | Eq 10-11 | Clean |
| C4 | Immediate PCM overwrite from bounded buffers inherently provides privacy without semantic retention | §IV.B Buffer Management | Clean (Runtime API generalized) |

## 4. Scope

### 4.1 In-Scope
- Signal processing transformations (FFT, STFT, Autocorrelation, Cross-Correlation)
- Physical modeling of corridor acoustics ($RT_{60}$, $D_c$, SPL bounds)
- Microbenchmarks of spectral vs. amplitude triggering
- Algorithm complexity and deterministic latency bounding ($\le 120ms$)

### 4.2 Out-of-Scope (Strictly Forbidden)
- **Deep Learning / Semantic Audio Classification** (Violates latency/privacy constraints)
- **System Architecture** (Owned by P18)
- **OS-Level Thread/Memory Management** (Owned by P20)
- **Application Validation Logic** (Owned by P10)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P6-INV-01 | Must NOT claim runtime scheduling ownership | Replaced "mutex" and "operating system tasks" with abstract threading references |
| P6-INV-02 | Must NOT claim deep learning evaluation | Explicitly defined against AST/CNN approaches |
| P6-INV-03 | Must NOT claim formal architectural design | ARM Cortex-A72 scoped purely as an experimental prototype |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P18 (Architecture) | Operates on the edge sensing nodes defined by P18 |
| **Upstream** | P20 (Runtime) | Relies on P20 to provide the actual isolated OS execution environment |
| **Downstream** | P7 (Stream Engine) | Passes lightweight `[TIMESTAMP, CONFIDENCE, AZIMUTH]` tuples up to the stream evaluation layer |

## 7. What This Paper Does NOT Do

- Does **not** categorize what the sound actually is (e.g., "screaming woman", "breaking glass"). It only detects "high-energy, chaotic, non-periodic anomaly".
- Does **not** manage the system lifecycle or clustering mechanisms.
- Does **not** provide mathematical proofs of safety logic.

## 8. Verified Implementation Components

| Component | Status | Note |
|---|---|---|
| **Spectral Gating Filter ($\delta$)** | ✅ Verified | Ablation study confirmed FPR reduction |
| **Periodic Rejection Filter ($\rho$)** | ✅ Verified | Tested against HVAC signatures |
| **GCC-PHAT Implementation** | ✅ Verified | Tested via RIR convolution datasets |
