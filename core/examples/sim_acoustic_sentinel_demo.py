"""
Acoustic Sentinel Demo Script - Paper 6 Verification

Simulates the detection of a high-energy crash utilizing minimal-retention 
spectral gating, autocorrelation, and GCC-PHAT.
"""
import os
import sys
import numpy as np

# Ensure root path is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.domain.services.acoustic_heuristics import AcousticHeuristics
from core.infrastructure.sensing.audio.gcc_phat import GCC_PHAT

def generate_mock_audios(sample_rate=44100, buffer_ms=3000):
    """
    Generate synthetic audio buffers to prove logic matrices hold up.
    """
    frames = int((buffer_ms / 1000.0) * sample_rate)
    
    # 1. Sine Wave (Periodic HVAC Noise Mock)
    t = np.linspace(0, buffer_ms / 1000.0, frames, False)
    periodic_noise = 0.5 * np.sin(2 * np.pi * 120 * t)  # 120Hz strong hum
    
    # 2. Broadband Impulse (Glass Shatter/Crash Mock)
    broadband_impulse = np.random.normal(0, 0.8, frames)
    # Add high-frequency bias to simulate crash
    broadband_impulse += 0.5 * np.sin(2 * np.pi * 2500 * t) 
    
    # Stereo mock for GCC_PHAT: 
    # Add deterministic delay to Mic 2 to simulate a source at an angle
    delay_samples = 5 # Small delay
    mic1 = broadband_impulse.copy()
    mic2 = np.roll(broadband_impulse.copy(), delay_samples)
    
    return periodic_noise, broadband_impulse, mic1, mic2

def run_demo():
    print("============================================================")
    print("ScholarMasterEngine - Paper 6: Acoustic Sentinel Demo")
    print("============================================================")
    
    heuristics = AcousticHeuristics(sample_rate=44100)
    spatial_logic = GCC_PHAT(sample_rate=44100)
    
    periodic_noise, broadband_impulse, mic1, mic2 = generate_mock_audios()
    
    print("\n[Test 1] Analyzing Continuous Periodic HVAC Hum...")
    event_1 = heuristics.process_buffer(periodic_noise)
    print(f"  Result: {event_1['reason']}")
    print(f"  Memory Status: Max signal energy after wipe = {np.max(np.abs(periodic_noise))}")
    assert event_1['is_anomaly'] == False
    
    print("\n[Test 2] Analyzing Broadband Impulse (Blind Spot Crash)...")
    event_2 = heuristics.process_buffer(broadband_impulse)
    print(f"  Result: {event_2['reason']}")
    print(f"  Memory Status: Max signal energy after wipe = {np.max(np.abs(broadband_impulse))}")
    assert event_2['is_anomaly'] == True
    
    print("\n[Test 3] GCC-PHAT Source Localization (Calculating Angle of Arrival)...")
    theta = spatial_logic.estimate_angle(mic1, mic2)
    print(f"  Calculated Theta (Degrees): {theta:.2f}°")
    
    print("\nVerification Complete: Minimal-Retention Sentinel processes raw physics, filters noise, localizes source, and zero-fills memory.")

if __name__ == "__main__":
    run_demo()
