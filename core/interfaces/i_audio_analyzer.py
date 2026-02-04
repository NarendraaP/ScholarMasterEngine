"""
Audio Analyzer Interface (Port)

Abstracts audio monitoring infrastructure.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class AudioMetrics:
    """Audio analysis result"""
    db_level: float  # Decibel level (normalized 0-1)
    spectral_centroid: float
    zero_crossing_rate: float
    is_voice_detected: bool


class IAudioAnalyzer(ABC):
    """
    Port for audio monitoring infrastructure.
    
    Implementations: Spectral analysis with FFT (Paper 6)
    Privacy: NO speech recognition, only spectral features
    """
    
    @abstractmethod
    def get_current_metrics(self) -> AudioMetrics:
        """
        Get current audio metrics.
        
        Returns:
            AudioMetrics with db_level, spectral features
        """
        pass
    
    @abstractmethod
    def is_alert_active(self) -> bool:
        """
        Check if audio alert condition is active.
        
        Returns:
            True if sustained loud noise detected
        """
        pass
    
    @abstractmethod
    def start_listening(self) -> None:
        """Start audio capture thread"""
        pass
    
    @abstractmethod
    def stop_listening(self) -> None:
        """Stop audio capture thread"""
        pass
