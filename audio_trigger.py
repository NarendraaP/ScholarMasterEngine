import sounddevice as sd
import numpy as np
import time

class AudioSentinel:
    """Paper 6: Audio Sentinel - Real-time Threat Detection"""
    
    def __init__(self, threshold_db=80):
        self.threshold_db = threshold_db
        self.sample_rate = 44100
        self.duration = 0.1  # 100ms chunks
        
    def calculate_db(self, audio_data):
        """Calculate decibel level from audio data"""
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Convert to decibels (with reference value)
        if rms > 0:
            db = 20 * np.log10(rms) + 60  # Add offset for realistic dB range
        else:
            db = 0
        
        return db
    
    def monitor_audio(self):
        """Monitor microphone and detect threats"""
        print("=" * 70)
        print("Paper 6: Audio Sentinel - Real-time Threat Detection")
        print("=" * 70)
        print(f"Threshold: {self.threshold_db} dB")
        print("Monitoring microphone... (Press Ctrl+C to stop)")
        print()
        
        try:
            while True:
                # Record audio chunk
                audio_data = sd.rec(
                    int(self.duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()  # Wait for recording to complete
                
                # Calculate decibel level
                db_level = self.calculate_db(audio_data)
                
                # Check threshold
                if db_level > self.threshold_db:
                    status = "[THREAT DETECTED]"
                    color = "🚨"
                else:
                    status = "[LISTENING]"
                    color = "🔊"
                
                # Print status (overwrite line)
                print(f"\r{color} Audio Level: {db_level:5.1f} dB | Status: {status}    ", end='', flush=True)
                
                time.sleep(0.05)  # Small delay between checks
        
        except KeyboardInterrupt:
            print("\n\n✅ Audio monitoring stopped")

def main():
    sentinel = AudioSentinel(threshold_db=80)
    sentinel.monitor_audio()

if __name__ == "__main__":
    main()
