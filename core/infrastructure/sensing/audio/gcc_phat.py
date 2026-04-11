"""
GCC-PHAT Implementation - Sensing Infrastructure

Implements Generalized Cross-Correlation with Phase Transform (GCC-PHAT)
for source localization in highly reverberant corridors as defined in Paper 6.
"""
import numpy as np

try:
    from scipy.fftpack import fft, ifft
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not installed. Using numpy fallback for FFT.")


class GCC_PHAT:
    def __init__(self, sample_rate=44100, mic_distance=0.08, speed_of_sound=343.0):
        self.sample_rate = sample_rate
        self.mic_distance = mic_distance # d = 8cm (ReSpeaker 4-Mic Array standard)
        self.c = speed_of_sound
        
    def estimate_angle(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """
        Algorithm 3: GCC-PHAT Source Localization
        Whitens the cross-spectrum to isolate the direct-path signal from reflections.
        
        Args:
            sig1: Audio samples from Mic 1
            sig2: Audio samples from Mic 2
            
        Returns:
            theta_degrees: Angle of arrival
        """
        n = sig1.shape[0] + sig2.shape[0]
        
        if SCIPY_AVAILABLE:
            X1 = fft(sig1, n=n)
            X2 = fft(sig2, n=n)
        else:
            X1 = np.fft.fft(sig1, n=n)
            X2 = np.fft.fft(sig2, n=n)
            
        # Cross-Spectrum
        R12 = X1 * np.conj(X2)
        
        # Whitening (Phase Transform)
        magnitude = np.abs(R12) + 1e-10 # Prevent division by zero
        R_phat = R12 / magnitude
        
        # Inverse FFT
        if SCIPY_AVAILABLE:
            r12_tau = np.real(ifft(R_phat))
        else:
            r12_tau = np.real(np.fft.ifft(R_phat))
            
        # ArgMax to find the lag with the highest correlation peak
        r12_tau = np.fft.fftshift(r12_tau)
        lag_samples = np.argmax(r12_tau) - (n // 2)
        
        # Convert lag to time
        tau = lag_samples / self.sample_rate
        
        # Calculate angle of arrival (theta) using Arccos
        ratio = (tau * self.c) / self.mic_distance
        
        # Clip ratio to valid domain [-1.0, 1.0] to prevent math domain error
        ratio = max(-1.0, min(1.0, float(ratio)))
        
        theta_rad = np.arccos(ratio)
        theta_deg = theta_rad * (180.0 / np.pi)
        
        return theta_deg
