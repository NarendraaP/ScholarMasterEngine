"""
Acoustic Heuristics - Domain Service

Implements the physics-based signal processing heuristics defined in 
ScholarMaster Paper 6 ("Zero-Retention Acoustic Sentinel").

Algorithms Implemented:
1. Spectral Gating (Algorithm 1) - Distinguishes broadband impulses from low-frequency thuds.
2. Periodic Rejection (Algorithm 2) - Uses autocorrelation to reject mechanical HVAC/music noise.
"""
import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not installed. Using numpy fallback for STFT where possible.")


class AcousticHeuristics:
    def __init__(self, sample_rate=44100, db_threshold=95.0, 
                 spectral_min_freq=2000, spectral_max_freq=4000, 
                 max_rho=0.65):
        self.sample_rate = sample_rate
        self.db_threshold = db_threshold
        self.spectral_min_freq = spectral_min_freq
        self.spectral_max_freq = spectral_max_freq
        self.max_rho = max_rho

    def spectral_gating(self, audio_buffer: np.ndarray) -> tuple[bool, str, float]:
        """
        Algorithm 1: Spectral Gating for Anomaly Verification
        Identifies if an audio frame is a high-energy chaotic impulse (e.g. scream, crash)
        or a low-frequency benign thud (e.g. door slam).
        
        Returns:
            (is_anomaly, reason, db_level)
        """
        # 1. Calculate RMS Energy and SPL Estimate
        rms = np.sqrt(np.mean(audio_buffer**2) + 1e-10) # Add epsilon to avoid log(0)
        # Assuming reference pressure mapping where RMS=1.0 maps to ~120dB (AOP)
        # This is a synthetic calibration mapping for the simulation.
        db = 20 * np.log10(rms + 1e-10) + 120 

        if db < self.db_threshold:
            return False, f"Below Threshold ({db:.1f}dB < {self.db_threshold}dB)", db

        # 2. Spectral Analysis
        if LIBROSA_AVAILABLE:
            stft = np.abs(librosa.stft(audio_buffer))
            freqs = librosa.fft_frequencies(sr=self.sample_rate)
        else:
            # Fallback STFT approximation using pure numpy for zero-dependency environments
            stft = np.abs(np.fft.rfft(audio_buffer))
            freqs = np.fft.rfftfreq(len(audio_buffer), 1.0 / self.sample_rate)

        # 3. Energy Band Ratios
        low_band = freqs < 500
        high_band = (freqs > self.spectral_min_freq) & (freqs < self.spectral_max_freq)

        energy_low = np.sum(stft[low_band]) + 1e-10
        energy_high = np.sum(stft[high_band])

        ratio = energy_high / energy_low

        if ratio > 2.5:
            return True, f"Impulse Detected (Ratio: {ratio:.2f})", db
        else:
            return False, f"Low-Freq Thud Detected (Ratio: {ratio:.2f})", db

    def periodic_rejection(self, audio_buffer: np.ndarray) -> tuple[bool, float]:
        """
        Algorithm 2: Autocorrelation Periodic Rejection
        Systematically rejects periodic mechanical noise (e.g., HVAC hum, rhythmic music)
        by formalizing a rejection metric based on discrete autocorrelation.
        
        Returns:
            (is_periodic, rho_value)
        """
        # Calculate full discrete autocorrelation
        # Using numpy correlate mode 'full' and taking the second half (lags >= 0)
        rxx_full = np.correlate(audio_buffer, audio_buffer, mode='full')
        rxx = rxx_full[len(rxx_full)//2:]
        
        peak_zero = rxx[0] + 1e-10
        
        # Define minimum lag to ignore the primary zero-lag energy peak
        # Ignore first ~20ms (frequency components > 50Hz)
        k_min = int((50.0 / 1000.0) * self.sample_rate)
        
        if k_min >= len(rxx):
            return False, 0.0 # Buffer too small to establish periodicity
            
        peak_max = np.max(rxx[k_min:])
        
        rho = peak_max / peak_zero
        
        if rho > self.max_rho:
            return True, rho  # Signal is highly periodic / mechanical
        else:
            return False, rho # Signal is chaotic / broadband
            
    def process_buffer(self, audio_buffer: np.ndarray) -> dict:
        """
        Executes the full pipeline and strictly wipes the buffer immediately
        to comply with zero-retention privacy heuristics.
        """
        event_payload = {
            "is_anomaly": False,
            "reason": "Safe",
            "db_level": 0.0,
            "is_periodic": False,
            "rho": 0.0
        }
        
        # 1. Run Spectral Gating
        is_impulse, reason, db = self.spectral_gating(audio_buffer)
        event_payload["db_level"] = db
        
        if is_impulse:
            # 2. If it passed gating, check if it's just a loud periodic machine
            is_periodic, rho = self.periodic_rejection(audio_buffer)
            event_payload["is_periodic"] = is_periodic
            event_payload["rho"] = rho
            
            if not is_periodic:
                event_payload["is_anomaly"] = True
                event_payload["reason"] = f"Acoustic Anomaly (Impulse, Chaos Confirmed)"
            else:
                event_payload["reason"] = f"Periodic Noise Rejected (Rho: {rho:.2f} > {self.max_rho})"
        else:
            event_payload["reason"] = reason
            
        # 3. CRITICAL: Minimal-Retention Design Rule Override
        # Explicit memory overwrite to ensure no raw audio data survives
        audio_buffer.fill(0)
        
        return event_payload
