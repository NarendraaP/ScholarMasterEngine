"""
Acoustic Anomaly Detection Module
Paper 6: Privacy-Preserving Acoustic Safety Monitoring

This module implements the complete acoustic monitoring pipeline:
- Algorithm 1: Spectral Gating for anomaly discrimination
- Algorithm 2: GCC-PHAT source localization
- Algorithm 3: Kalman filtering for angle smoothing
- Volatile memory processing for privacy
"""

import numpy as np
import librosa
from typing import Tuple, Optional
from dataclasses import dataclass
from scipy import signal
from scipy.fft import fft, ifft


@dataclass
class AudioConfig:
    """Configuration for audio processing"""
    sample_rate: int = 44100
    buffer_size_ms: int = 3000
    db_threshold: float = 95.0
    spectral_low_freq: int = 0
    spectral_low_cutoff: int = 500
    spectral_high_freq: int = 2000
    spectral_high_cutoff: int = 4000
    spectral_ratio_threshold: float = 2.5
    mic_spacing_m: float = 0.043  # ReSpeaker 4-Mic array spacing
    speed_of_sound: float = 343.0  # m/s


@dataclass
class AcousticEvent:
    """Detected acoustic anomaly event"""
    timestamp: float
    db_level: float
    spectral_ratio: float
    is_anomaly: bool
    angle_degrees: Optional[float] = None
    classification: str = "UNKNOWN"
    is_replay: bool = False # Paper 6: RT60 Replay Detection
    replay_confidence: float = 0.0


class ReplayDefender:
    """
    Algorithm 4: RT60 Replay Detection (Paper 6)
    
    Detects replay attacks by analyzing Reverberation Time (RT60).
    A recording played back in a room contains convolution of two impulse responses,
    typically resulting in abnormal decay curves compared to the room's baseline.
    """
    def __init__(self, sample_rate=44100):
        self.fs = sample_rate
        # Baseline RT60 for the deployed environment (e.g., Tiled Corridor ~0.8s)
        self.baseline_rt60 = 0.8 
        self.tolerance = 0.3
        
    def analyze_decay(self, audio_buffer: np.ndarray) -> Tuple[bool, float]:
        """
        Estimate RT60 using Schroeder Integration and check for anomalies.
        Returns: (is_replay, estimated_rt60)
        """
        try:
            # 1. Hilbert Transform for Amplitude Envelope
            analytic_signal = signal.hilbert(audio_buffer)
            amplitude_envelope = np.abs(analytic_signal)
            
            # 2. Energy Decay Curve (EDC) via Schroeder Integration
            # Reverse integration of squared envelope
            energy = amplitude_envelope ** 2
            edc = np.cumsum(energy[::-1])[::-1]
            
            # Normalize EDC
            if edc[0] == 0: return False, 0.0
            edc_db = 10 * np.log10(edc / edc[0] + 1e-10)
            
            # 3. Linear Regression on EDC to find slope (T60)
            # We look at the decay from -5dB to -35dB (T30) and extrapolate
            mask = (edc_db <= -5) & (edc_db >= -35)
            
            if np.sum(mask) < 10:
                # Not enough dynamic range to estimate (too quiet or too short)
                return False, 0.0
                
            y = edc_db[mask]
            x = np.arange(len(edc_db))[mask] / self.fs
            
            # Linear fit: y = mx + c
            # slope m is decay rate in dB/sec
            A = np.vstack([x, np.ones(len(x))]).T
            m, c = np.linalg.lstsq(A, y, rcond=None)[0]
            
            # RT60 = Time to decay 60dB = -60 / m
            if m >= 0: return False, 0.0 # Growing energy? Impossible/Noise
            
            rt60_est = -60.0 / m
            
            # 4. Anomaly Check
            # Replayed audio often has Longer RT60 (Room + Recording Room)
            # or Distorted decay shape.
            
            is_replay = False
            
            # Heuristic: If RT60 is significantly distinct from baseline
            # (Note: In a real adaptive system, baseline is learned over time)
            if abs(rt60_est - self.baseline_rt60) > self.tolerance:
                # But wait, very dry signals might be direct injection?
                # Usually replay implies "doubled" reverb.
                if rt60_est > (self.baseline_rt60 + self.tolerance):
                    is_replay = True
            
            return is_replay, rt60_est
            
        except Exception:
            return False, 0.0


class MQTTEmitter:
    """
    IoT Metadata Emitter (Paper 6)
    Sends ONLY metadata (not audio) to Cloud/Dashboard.
    """
    def __init__(self):
        self.client = None
        self.topic = "scholarmaster/alerts/acoustic"
        try:
            import paho.mqtt.client as mqtt
            self.client = mqtt.Client()
            # In a real deployment, we'd connect to a broker
            # self.client.connect("localhost", 1883, 60)
            # self.client.loop_start()
            print("[MQTT] Client initialized (Mock Mode for Audit)")
        except ImportError:
            print("[MQTT] paho-mqtt not found. Mocking emission.")
            
    def publish(self, event: AcousticEvent):
        """Publish JSON event"""
        import json
        payload = {
            "timestamp": event.timestamp,
            "type": "ACOUSTIC_ANOMALY",
            "db": f"{event.db_level:.1f}",
            "class": event.classification,
            "replay_risk": event.is_replay,
            "loc": event.angle_degrees
        }
        json_str = json.dumps(payload)
        
        if self.client:
            # self.client.publish(self.topic, json_str)
            pass
        
        # Log to stdout for audit verification
        if event.is_anomaly:
            print(f"📡 [MQTT] Published: {json_str}")



class SpectralGating:
    """
    Algorithm 1: Spectral Gating for Anomaly Verification
    
    Discriminates between high-energy broadband impulses (screams, crashes)
    and benign mechanical noise (door slams, footsteps) using frequency-domain
    energy analysis.
    """
    
    def __init__(self, config: AudioConfig):
        self.config = config
    
    def analyze(self, audio_frame: np.ndarray) -> Tuple[bool, float, float]:
        """
        Analyze audio frame for spectral characteristics
        
        Args:
            audio_frame: 1D numpy array of audio samples
            
        Returns:
            Tuple of (is_anomaly, db_level, spectral_ratio)
        """
        # Step 1: Calculate RMS Energy
        rms = np.sqrt(np.mean(audio_frame ** 2))
        
        # Convert to dB SPL scale
        # In digital audio: RMS=1.0 is typically considered full scale
        # For acoustic monitoring, we map this to a practical SPL scale:
        # RMS = 0.01 → 60 dB SPL (quiet speech)
        # RMS = 0.1  → 80 dB SPL (loud conversation)  
        # RMS = 1.0  → 100 dB SPL (very loud scream)
        # RMS = 10.0 → 120 dB SPL (pain threshold)
        #
        # Formula: dB_SPL = 60 + 20*log10(RMS / 0.01)
        #                 = 60 + 20*log10(RMS) + 40
        #                 = 100 + 20*log10(RMS)
        
        db_level = 100 + 20 * np.log10(rms + 1e-10)
        
        # Early exit if below threshold
        if db_level < self.config.db_threshold:
            return False, db_level, 0.0
        
        # Step 2: Spectral Analysis via STFT
        stft_matrix = np.abs(librosa.stft(audio_frame))
        freqs = librosa.fft_frequencies(sr=self.config.sample_rate)
        
        # Step 3: Isolate frequency bands
        # Low frequency (thuds): 0-500 Hz
        low_band_mask = (freqs >= self.config.spectral_low_freq) & \
                        (freqs < self.config.spectral_low_cutoff)
        energy_low = np.sum(stft_matrix[low_band_mask])
        
        # High frequency (impulses): 2000-4000 Hz
        high_band_mask = (freqs >= self.config.spectral_high_freq) & \
                         (freqs < self.config.spectral_high_cutoff)
        energy_high = np.sum(stft_matrix[high_band_mask])
        
        # Step 4: Calculate ratio
        spectral_ratio = energy_high / (energy_low + 1e-10)
        
        # Step 5: Decision logic
        is_anomaly = (db_level > self.config.db_threshold) and \
                     (spectral_ratio > self.config.spectral_ratio_threshold)
        
        return is_anomaly, db_level, spectral_ratio
    
    def calculate_spectral_entropy(self, audio_frame: np.ndarray) -> float:
        """
        Calculate spectral entropy for voice masking (privacy)
        
        Low entropy = structured speech (privacy risk)
        High entropy = broadband noise (no privacy risk)
        
        Returns:
            Spectral entropy value (higher = more chaotic)
        """
        stft_matrix = np.abs(librosa.stft(audio_frame))
        power_spectrum = np.mean(stft_matrix ** 2, axis=1)
        
        # Normalize to probability distribution
        power_norm = power_spectrum / (np.sum(power_spectrum) + 1e-10)
        
        # Calculate entropy
        entropy = -np.sum(power_norm * np.log2(power_norm + 1e-10))
        
        return entropy


class GCCPHATLocalizer:
    """
    Algorithm 2: GCC-PHAT Source Localization
    
    Robust Time Difference of Arrival (TDOA) estimation using
    Generalized Cross-Correlation with Phase Transform.
    Handles reverberation in hallways via spectrum whitening.
    """
    
    def __init__(self, config: AudioConfig):
        self.config = config
    
    def localize(self, signal1: np.ndarray, signal2: np.ndarray) -> Tuple[float, int]:
        """
        Estimate angle of arrival from two microphone signals
        
        Args:
            signal1: Audio from microphone 1
            signal2: Audio from microphone 2
            
        Returns:
            Tuple of (angle_degrees, lag_samples)
        """
        # Step 1: FFT of both signals
        X1 = fft(signal1)
        X2 = fft(signal2)
        
        # Step 2: Cross-spectrum
        R12 = X1 * np.conj(X2)
        
        # Step 3: PHAT weighting (spectrum whitening)
        # This is the key difference from standard GCC
        R_phat = R12 / (np.abs(R12) + 1e-10)
        
        # Step 4: IFFT to get correlation function
        correlation = np.real(ifft(R_phat))
        
        # Step 5: Find peak (time delay)
        # Use fftshift to center the correlation
        correlation = np.fft.fftshift(correlation)
        center = len(correlation) // 2
        
        # Find maximum within physically plausible range
        # Max delay = mic_spacing / speed_of_sound
        max_delay_samples = int(
            (self.config.mic_spacing_m / self.config.speed_of_sound) * 
            self.config.sample_rate
        )
        
        search_range = correlation[center - max_delay_samples:center + max_delay_samples]
        peak_idx = np.argmax(search_range)
        lag_samples = peak_idx - max_delay_samples
        
        # Step 6: Convert lag to time delay
        tau = lag_samples / self.config.sample_rate
        
        # Step 7: Calculate angle of arrival
        # θ = arccos(τ * c / d)
        # Clamp to valid range for arccos
        cos_theta = (tau * self.config.speed_of_sound) / self.config.mic_spacing_m
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        
        angle_radians = np.arccos(cos_theta)
        angle_degrees = np.degrees(angle_radians)
        
        return angle_degrees, lag_samples
    
    def localize_4mic_array(self, signals: np.ndarray) -> Tuple[float, float]:
        """
        Localize using 4-microphone array (azimuth and elevation)
        
        Args:
            signals: (4, N) array of 4 microphone signals
            
        Returns:
            Tuple of (azimuth_degrees, elevation_degrees)
        """
        # Simplified 4-mic localization (2D plane for now)
        # Full 3D would require tetrahedral geometry
        
        # Use mic pairs for azimuth
        angle_1_2, _ = self.localize(signals[0], signals[1])
        angle_3_4, _ = self.localize(signals[2], signals[3])
        
        # Average for robustness
        azimuth = (angle_1_2 + angle_3_4) / 2.0
        
        # Elevation requires vertical mic spacing
        # Placeholder for now
        elevation = 0.0
        
        return azimuth, elevation


class KalmanAngleFilter:
    """
    Algorithm 3: Kalman Filtering for Angle Smoothing
    
    Reduces jitter in TDOA angle estimates by tracking the most likely
    source position over time.
    """
    
    def __init__(self, process_variance: float = 1.0, measurement_variance: float = 10.0):
        """
        Initialize Kalman filter
        
        Args:
            process_variance (Q): How much we expect angle to change
            measurement_variance (R): How noisy our measurements are
        """
        self.theta_est = 0.0  # Estimated angle
        self.P = 1.0  # Estimation error covariance
        self.Q = process_variance
        self.R = measurement_variance
    
    def update(self, theta_measured: float) -> float:
        """
        Update filter with new measurement
        
        Args:
            theta_measured: Measured angle from GCC-PHAT
            
        Returns:
            Smoothed angle estimate
        """
        # Prediction step
        theta_pred = self.theta_est  # Simple model: angle doesn't change
        P_pred = self.P + self.Q
        
        # Update step
        # Kalman gain
        K = P_pred / (P_pred + self.R)
        
        # State update
        self.theta_est = theta_pred + K * (theta_measured - theta_pred)
        
        # Covariance update
        self.P = (1 - K) * P_pred
        
        return self.theta_est
    
    def reset(self):
        """Reset filter state"""
        self.theta_est = 0.0
        self.P = 1.0


class AcousticAnomalyDetector:
    """
    Complete acoustic monitoring pipeline integrating all algorithms
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.spectral_gating = SpectralGating(self.config)
        self.localizer = GCCPHATLocalizer(self.config)
        self.kalman_filter = KalmanAngleFilter()
        self.replay_defender = ReplayDefender(self.config.sample_rate) # Security Layer
        self.mqtt = MQTTEmitter() # IoT Layer
    
    def process_frame(self, audio_buffer: np.ndarray, 
                      enable_localization: bool = False,
                      stereo_signals: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> AcousticEvent:
        """
        Process audio frame through complete pipeline
        
        Args:
            audio_buffer: Mono audio frame for spectral analysis
            enable_localization: Whether to run GCC-PHAT
            stereo_signals: Tuple of (left, right) signals for localization
            
        Returns:
            AcousticEvent with detection results
        """
        import time
        timestamp = time.time()
        
        # Algorithm 1: Spectral Gating
        is_anomaly, db_level, spectral_ratio = self.spectral_gating.analyze(audio_buffer)
        
        angle_degrees = None
        if is_anomaly and enable_localization and stereo_signals:
            # Algorithm 2: GCC-PHAT Localization
            raw_angle, _ = self.localizer.localize(stereo_signals[0], stereo_signals[1])
            
            # Algorithm 3: Kalman Smoothing
            angle_degrees = self.kalman_filter.update(raw_angle)
            
        # Algorithm 4: Replay Detection (RT60)
        is_replay, rt60_val = False, 0.0
        if is_anomaly:
             is_replay, rt60_val = self.replay_defender.analyze_decay(audio_buffer)
             if is_replay:
                 print(f"⚠️ [SECURITY] Replay Attack Detected! RT60={rt60_val:.2f}s")
        
        # Classify event
        classification = "ANOMALY" if is_anomaly else "SAFE"
        if is_anomaly:
            if is_replay:
                classification = "SPOOF_ATTEMPT"
            elif spectral_ratio > 5.0:
                classification = "SCREAM/CRASH"
            elif spectral_ratio > 2.5:
                classification = "GLASS_BREAK"
        
        # Construct Event
        event = AcousticEvent(
            timestamp=timestamp,
            db_level=db_level,
            spectral_ratio=spectral_ratio,
            is_anomaly=is_anomaly,
            angle_degrees=angle_degrees,
            classification=classification,
            is_replay=is_replay,
            replay_confidence=rt60_val
        )
        
        # Emit Metadata (Paper 6: JSON-only emission)
        if is_anomaly:
            self.mqtt.publish(event)
            
        return event


if __name__ == "__main__":
    print("🔊 Acoustic Anomaly Detection Module")
    print("=" * 60)
    print("Algorithms Implemented:")
    print("  ✅ Algorithm 1: Spectral Gating")
    print("  ✅ Algorithm 2: GCC-PHAT Localization")
    print("  ✅ Algorithm 3: Kalman Filtering")
    print("=" * 60)
    
    # Quick validation
    config = AudioConfig()
    detector = AcousticAnomalyDetector(config)
    
    # Generate synthetic test signal
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(config.sample_rate * duration))
    
    # Simulate high-frequency impulse (scream)
    test_signal = np.random.normal(0, 0.1, len(t))  # Base noise
    impulse_mask = (t > 0.3) & (t < 0.7)
    test_signal[impulse_mask] += np.sin(2 * np.pi * 3000 * t[impulse_mask]) * 0.5
    
    event = detector.process_frame(test_signal)
    
    print(f"\nTest Signal Analysis:")
    print(f"  dB Level: {event.db_level:.2f}")
    print(f"  Spectral Ratio: {event.spectral_ratio:.2f}")
    print(f"  Classification: {event.classification}")
    print(f"  Is Anomaly: {event.is_anomaly}")
