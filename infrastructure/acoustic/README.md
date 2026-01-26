# Acoustic Anomaly Detection Module

## Paper 6: Privacy-Preserving Acoustic Safety Monitoring

### Overview

This module implements the complete acoustic monitoring system described in Paper 6, including:

- **Algorithm 1**: Spectral Gating for anomaly discrimination
- **Algorithm 2**: GCC-PHAT source localization (TDOA-based)
- **Algorithm 3**: Kalman filtering for angle smoothing
- **Volatile Memory Processing**: Privacy-preserving buffer management

### Installation

```bash
pip3 install librosa soundfile scipy numpy
```

### Quick Start

```python
from infrastructure.acoustic import AcousticAnomalyDetector, AudioConfig

# Initialize detector
config = AudioConfig(
    sample_rate=44100,
    db_threshold=95.0,
    spectral_ratio_threshold=2.5
)
detector = AcousticAnomalyDetector(config)

# Process audio frame
import numpy as np
audio_frame = np.random.randn(44100)  # 1 second of audio
event = detector.process_frame(audio_frame)

print(f"Is Anomaly: {event.is_anomaly}")
print(f"dB Level: {event.db_level:.2f}")
print(f"Classification: {event.classification}")
```

### Running Validation Tests

```bash
python3 tests/test_acoustic_anomaly.py
```

This will:
- Run blind-spot detection tests at 5m, 15m, 25m, 35m
- Generate Table III data for the paper
- Test spectral discrimination (screams vs door slams)
- Output results to `data/acoustic_tests/`

### Module Structure

```
infrastructure/acoustic/
├── __init__.py
└── anomaly_detector.py          # Complete implementation
    ├── SpectralGating            # Algorithm 1
    ├── GCCPHATLocalizer          # Algorithm 2
    ├── KalmanAngleFilter         # Algorithm 3
    └── AcousticAnomalyDetector   # Main pipeline
```

### Key Classes

#### `SpectralGating`
Discriminates high-energy broadband impulses from mechanical noise using frequency-domain energy ratios.

**Key Method**: `analyze(audio_frame) -> (is_anomaly, db_level, spectral_ratio)`

#### `GCCPHATLocalizer`
Performs TDOA-based source localization using Phase Transform for reverberation robustness.

**Key Method**: `localize(signal1, signal2) -> (angle_degrees, lag_samples)`

#### `KalmanAngleFilter`
Smooths noisy angle estimates from GCC-PHAT using Kalman filtering.

**Key Method**: `update(theta_measured) -> theta_smoothed`

### Configuration

```python
@dataclass
class AudioConfig:
    sample_rate: int = 44100
    db_threshold: float = 95.0          # Trigger threshold (dB)
    spectral_low_cutoff: int = 500      # Low freq band (Hz)
    spectral_high_freq: int = 2000      # High freq band start (Hz)
    spectral_high_cutoff: int = 4000    # High freq band end (Hz)
    spectral_ratio_threshold: float = 2.5  # Energy ratio threshold
    mic_spacing_m: float = 0.043        # Mic array spacing (meters)
```

### Privacy Guarantees

The system implements **volatile memory processing**:

1. Audio frames are buffered in RAM only
2. After feature extraction, buffers are overwritten with zeros
3. No raw audio is persisted to disk
4. Only non-reconstructible features (energy ratios, TDOA lags) are retained

### Validation Results

After running tests, results are saved to:
- `data/acoustic_tests/blind_spot_detection_rates.json`
- `data/acoustic_tests/table_iii_data.csv`
- `data/acoustic_tests/discrimination_test.json`

### Citation

If using this module, please cite:

```
Narendra Babu P, "Privacy-Preserving Acoustic Anomaly Detection Under 
Adversarial and Non-Line-of-Sight Conditions," ScholarMaster Research Series, 2025.
```

### License

See main project LICENSE file.
