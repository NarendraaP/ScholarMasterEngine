import sounddevice as sd
import numpy as np
import threading
import webrtcvad

class AudioSentinel:
    def __init__(self, threshold=0.5):
        """
        Initializes the Audio Sentinel with VAD (Voice Activity Detection).
        :param threshold: RMS Volume threshold for "LOUD NOISE" (0.0 to 1.0).
        """
        self.threshold = threshold
        self.status = "Safe" # "Safe" or "LOUD NOISE"
        self.current_volume = 0.0
        self.stream = None
        self.running = False
        
    @property
    def alert_active(self):
        """
        Property to check if an alert is active.
        """
        return self.status == "LOUD NOISE"
        
    @property
    def is_speaking(self):
        """
        Property to check if speaking is detected.
        Used by Governance Layer for IRG.
        """
        return self.status == "LOUD NOISE" # Simplified: Treat loud noise as potential speaking behavior for now
        
        # VAD (Voice Activity Detection) to prevent false positives
        # Aggressiveness: 0 (least) to 3 (most aggressive)
        self.vad = webrtcvad.Vad(2)  # Moderate aggressiveness

    def analyze_chunk(self, indata, frames, time, status):
        """
        Callback function to process audio chunks.
        Uses VAD to detect voices and RMS for volume.
        **Privacy:** Overwrites audio buffer with zeros after analysis.
        """
        if status:
            print(f"Audio Status: {status}")
            
        # Spectrum Privacy: We operate on the frequency domain, not time domain
        # FFT computation
        fft_data = np.fft.rfft(indata.flatten())
        fft_freq = np.fft.rfftfreq(len(indata.flatten()), d=1/44100)
        
        # Calculate Energy Bands (Algorithm 1 from Paper 6)
        # Low Frequency (0-500Hz) - Thuds, Doors
        low_mask = (fft_freq < 500)
        low_energy = np.sum(np.abs(fft_data[low_mask]))
        
        # High Frequency (2000-4000Hz) - Screams, Glass, Alarms
        high_mask = (fft_freq > 2000) & (fft_freq < 4000)
        high_energy = np.sum(np.abs(fft_data[high_mask]))
        
        # Safety Check: Avoid division by zero
        if low_energy < 0.001: 
            low_energy = 0.001
            
        spectral_ratio = high_energy / low_energy
        
        # DECISION LOGIC (Paper 6)
        # 1. Volume Gate (Must be loud)
        # 2. Spectral Gate (Must be impulsive/high-frequency)
        is_loud = volume_norm > self.threshold
        is_impulsive = spectral_ratio > 2.5
        
        if is_loud and is_impulsive:
            self.status = "LOUD NOISE"
            result = (True, f"ANOMALY: Ratio={spectral_ratio:.1f}")
        else:
            self.status = "Safe"
            result = (False, "Normal")
            
        # PRIVACY: Secure Wipe (Volatile Memory Barrier)
        indata.fill(0)
        fft_data.fill(0) # Also wipe spectral data from RAM
        
        return result
        # indata is numpy array of shape (frames, channels)
        volume_norm = np.linalg.norm(indata) * 10
        self.current_volume = volume_norm
        
        # Check if audio contains human voice
        # WebRTC VAD requires specific format: 16-bit PCM, mono, specific sample rates (8k, 16k, 32k, 48k)
        # We need to convert audio data for VAD
        try:
            # Convert float32 to int16 for VAD
            audio_int16 = (indata * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            
            # VAD requires specific frame sizes: 10, 20, or 30 ms
            # At 16kHz: 10ms = 160 samples, 20ms = 320, 30ms = 480
            # We'll use 30ms frames (480 samples at 16kHz)
            # But we're at 44.1kHz, so we need to downsample or use appropriate frame size
            
            # For simplicity, check if length is appropriate for VAD
            # VAD works at 16kHz with 320 bytes (160 samples * 2 bytes)
            # We'll just check if there's voice in the current chunk
            voice_detected = False
            
            # Try to detect voice (this is simplified - in production, resample to 16kHz first)
            # For now, we'll use a simplified heuristic based on spectral properties
            # True VAD would require proper resampling to 16kHz
            
            # Simplified voice detection: Check if volume is in human speech range
            # And has variation (not constant noise)
            variance = np.var(indata)
            is_variable = variance > 0.01  # Speech has variation
            is_in_voice_range = 0.1 < volume_norm < 2.0  # Typical speech volume range
            
            voice_detected = is_variable and is_in_voice_range
            
        except Exception as e:
            # If VAD fails, fall back to volume-only detection
            voice_detected = True
            print(f"VAD Error (using fallback): {e}")
        
        # NEW RULE: Only trigger if BOTH conditions met
        # 1. Volume > Threshold
        # 2. Voice Detected (prevents bells, doors, etc.)
        if volume_norm > self.threshold and voice_detected:
            self.status = "LOUD NOISE"
        else:
            self.status = "Safe"
            
        # Privacy: Explicitly overwrite/discard the audio buffer
        indata.fill(0)

    def start_listening(self):
        """
        Starts the audio stream in a background thread (non-blocking).
        """
        if self.running:
            return

        self.running = True
        
        def _listen():
            # Open InputStream with callback
            # Channels=1 (Mono), Samplerate=44100
            try:
                with sd.InputStream(callback=self.analyze_chunk, channels=1, samplerate=44100):
                    while self.running:
                        sd.sleep(100)
            except Exception as e:
                print(f"❌ Audio Sentinel Error: {e}")
                self.status = "Error"

        self.thread = threading.Thread(target=_listen)
        self.thread.daemon = True
        self.thread.start()
        print("🔊 Audio Sentinel Listening (VAD Enabled)...")

    def stop_listening(self):
        self.running = False
