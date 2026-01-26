"""
Quick diagnostic test to calibrate synthetic signals
"""

import numpy as np
import sys
sys.path.insert(0, '/Users/premkumartatapudi/Desktop/ScholarMasterEngine')

from infrastructure.acoustic.anomaly_detector import AcousticAnomalyDetector, AudioConfig

# Test different amplitude levels
print("=" * 70)
print("SIGNAL CALIBRATION TEST")
print("=" * 70)
print()

detector = AcousticAnomalyDetector()

for rms_level in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
    # Create signal with specific RMS
    duration = 1.0
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # Generate signal
    signal = np.sin(2 * np.pi * 3000 * t)  # 3kHz sine
    
    # Scale to desired RMS
    current_rms = np.sqrt(np.mean(signal ** 2))
    signal = signal * (rms_level / current_rms)
    
    # Measure actual RMS
    measured_rms = np.sqrt(np.mean(signal ** 2))
    measured_db = 20 * np.log10(measured_rms + 1e-10)
    
    # Test detection
    event = detector.process_frame(signal)
    
    print(f"Target RMS: {rms_level:6.2f} | Measured: {measured_rms:6.3f} | "
          f"dB: {measured_db:7.2f} | Detected: {event.is_anomaly}")

print()
print(f"Threshold: {detector.config.db_threshold} dB")
print()
print("Testing actual scream signal...")

# Generate scream at 5m
def generate_scream_5m():
    duration = 1.0
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    base_rms_target = 10.0
    distance_m = 5.0
    
    attenuation_db = 20 * np.log10(distance_m / 1.0)
    amplitude_factor = 10 ** (-attenuation_db / 20)
    
    signal = np.zeros_like(t)
    frequencies = [1000, 1500, 2000, 2500, 3000, 3500, 4000]
    weights = [0.5, 0.6, 1.0, 1.2, 1.3, 1.1, 0.9]
    
    for freq, weight in zip(frequencies, weights):
        signal += np.sin(2 * np.pi * freq * t) * weight
    
    current_rms = np.sqrt(np.mean(signal ** 2))
    signal = signal * (base_rms_target / current_rms) * amplitude_factor
    
    return signal

scream = generate_scream_5m()
scream_rms = np.sqrt(np.mean(scream ** 2))
scream_db = 20 * np.log10(scream_rms + 1e-10)

event = detector.process_frame(scream)

print(f"Scream @5m: RMS={scream_rms:.3f}, dB={scream_db:.2f}, Detected={event.is_anomaly}")
print(f"  Spectral Ratio: {event.spectral_ratio:.2f} (threshold: {detector.config.spectral_ratio_threshold})")
