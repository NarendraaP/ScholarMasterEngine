"""
Audio Analyzer - Infrastructure Adapter

Implements IAudioAnalyzer using spectral analysis (Paper 6).
"""
from typing import Optional
import numpy as np
import pyaudio
import threading
import time

from core.interfaces.i_audio_analyzer import IAudioAnalyzer, AudioMetrics


class AudioAnalyzer(IAudioAnalyzer):
    """
    Spectral analysis implementation of audio monitoring.
    
    Papers:
    - Paper 6: Privacy-preserving audio monitoring
    - NO speech recognition, only spectral features
    """
    
    def __init__(self, sample_rate=16000, chunk_size=1024):
        """Initialize audio capture"""
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Threading
        self.listening = False
        self.thread = None
        
        # Current metrics
        self.current_metrics = AudioMetrics(
            db_level=0.0,
            spectral_centroid=0.0,
            zero_crossing_rate=0.0,
            is_voice_detected=False
        )
        
        # Alert state
        self._alert_active = False
        self._sustained_loud_frames = 0
        self.SUSTAINED_THRESHOLD = 10  # 10 frames = ~1 second
        
        print("✅ AudioAnalyzer initialized")
    
    def get_current_metrics(self) -> AudioMetrics:
        """Get current audio metrics"""
        return self.current_metrics
    
    def is_alert_active(self) -> bool:
        """Check if sustained loud noise detected"""
        return self._alert_active
    
    def start_listening(self) -> None:
        """Start audio capture thread"""
        if self.listening:
            return
        
        self.listening = True
        self.thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.thread.start()
        print("🎤 Audio monitoring started")
    
    def stop_listening(self) -> None:
        """Stop audio capture thread"""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("🔇 Audio monitoring stopped")
    
    def _audio_loop(self):
        """Audio capture loop (runs in background thread)"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.listening:
                # Read audio chunk
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.float32)
                
                # Compute spectral features
                self._analyze_audio(samples)
                
                time.sleep(0.1)  # ~10 Hz analysis rate
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"⚠️  Audio capture error: {e}")
            self.listening = False
    
    def _analyze_audio(self, samples: np.ndarray):
        """
        Analyze audio chunk and update metrics.
        
        Privacy: NO speech recognition, only spectral features.
        """
        # 1. dB level (normalized 0-1)
        rms = np.sqrt(np.mean(samples ** 2))
        db_level = min(1.0, rms * 10)  # Normalize to 0-1
        
        # 2. Spectral centroid (frequency content)
        fft = np.fft.rfft(samples)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(samples), 1.0 / self.sample_rate)
        
        if np.sum(magnitude) > 0:
            spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        else:
            spectral_centroid = 0.0
        
        # 3. Zero crossing rate (voice detection proxy)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(samples)))) / len(samples)
        is_voice = zero_crossings > 0.05 and spectral_centroid > 200
        
        # Update metrics
        self.current_metrics = AudioMetrics(
            db_level=db_level,
            spectral_centroid=spectral_centroid,
            zero_crossing_rate=zero_crossings,
            is_voice_detected=is_voice
        )
        
        # Update alert state (sustained loud noise)
        if db_level > 0.7:  # Loud noise threshold
            self._sustained_loud_frames += 1
        else:
            self._sustained_loud_frames = 0
        
        # Trigger alert if sustained
        self._alert_active = self._sustained_loud_frames >= self.SUSTAINED_THRESHOLD
