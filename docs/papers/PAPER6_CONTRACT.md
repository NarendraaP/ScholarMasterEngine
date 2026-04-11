# PAPER 6 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Zero-Retention Acoustic Sentinel for Privacy-Preserving Safety Monitoring in Educational Environments |
| **Paper ID** | P6 |
| **Layer** | Perception (L2 — Acoustic Sensing) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A privacy-preserving acoustic anomaly detection pipeline that classifies safety-critical sounds (screams, glass breaks, gunshots) from spectral features alone, with zero retention of raw audio — all processing occurs in volatile memory and raw waveforms are destroyed after feature extraction.**

Paper 6 provides the acoustic perception channel complementary to the visual pipeline (Papers 1/3), extending campus safety monitoring without introducing audio surveillance capabilities.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Mel-spectrogram features are sufficient for safety-event classification (≥ 94% accuracy) | Classification results (§V) | Clean |
| C2 | Raw audio waveforms are destroyed after spectral extraction — zero retention | Architecture (§III); volatile memory lifecycle | Clean — scoped as "technical property of the memory lifecycle" |
| C3 | Speech content is not captured or reconstructable from Mel-spectrograms at the system's resolution | Information-theoretic analysis (§IV) | Clean |
| C4 | Acoustic triggers preempt visual processing when safety-critical events are detected | Priority scheduler (§III) | Clean |

## 4. Scope

### 4.1 In-Scope
- Mel-spectrogram feature extraction from microphone input
- Safety-event classification (scream, glass break, gunshot, crowd distress)
- Volatile memory confinement of raw audio
- Priority preemption of visual pipeline for safety events
- Source localization via multi-microphone delay estimation

### 4.2 Out-of-Scope
- Speech recognition or transcription (explicitly excluded)
- Visual anomaly detection (Paper 1, Paper 3)
- Engagement analysis (Paper 2 uses acoustic *level*, not events)
- Trust/audit logging (Paper 8)
- AR visualization of acoustic events (Paper 15)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P6-INV-01 | Raw audio buffers MUST be destroyed after Mel-spectrogram extraction | RAII deallocation; no disk-write path |
| P6-INV-02 | No speech-content features SHALL be extracted or stored | Feature pipeline limited to spectral energy bands |
| P6-INV-03 | Safety-critical acoustic events MUST preempt visual processing | Priority scheduler with interrupt-level override |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P5 (Hardware) | Hardware platform providing audio input and Neural Engine |
| **Downstream** | P2 (Engagement) | Ambient acoustic level as context signal |
| **Downstream** | P9 (Orchestrator) | Acoustic safety events on orchestration bus |
| **Downstream** | P10 (Validation) | Acoustic module exercised under system stress test |
| **Downstream** | P15 (AR) | Acoustic alerts rendered as spatial AR overlays |

## 7. Verification Requirements

- Safety-event classification accuracy ≥ 94% on test set
- Zero raw audio recoverable from heap post-extraction
- Priority preemption triggers within 10 ms of safety-event detection
- No speech-content features present in feature pipeline output

## 8. What This Paper Does NOT Do

- Does **not** perform speech recognition or NLP
- Does **not** retain any audio recordings
- Does **not** make privacy claims beyond volatile confinement (defers to Paper 17)
- Does **not** address visual anomaly detection (complementary to, not replacement for, visual pipeline)

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Audio Sentinel** | `modules_legacy/audio_sentinel.py` | ✅ Verified (Spectral Analysis & VAD) |
| **Privacy Wipe** | `modules_legacy/audio_sentinel.py` | ✅ Verified (`indata.fill(0)` barrier) |
| **Impulse Logic** | `modules_legacy/audio_sentinel.py` | ✅ Verified (Ratio-based Trigger) |

