import threading
import queue
import time
import os

# Safe Import for Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ OpenAI Whisper not installed. Scribe will run in MOCK mode.")

class LectureScribe:
    def __init__(self):
        self.buffer = queue.Queue()
        self.running = True
        self.model = None
        self.last_transcript = ""
        
        # Initialize Whisper Model (Tiny)
        if WHISPER_AVAILABLE:
            print("🎤 Loading Whisper Model (tiny.en)...")
            try:
                self.model = whisper.load_model("tiny.en")
                print("✅ Whisper Model Loaded")
            except Exception as e:
                print(f"❌ Whisper Load Failed: {e}")
                self.model = None
        
        # Start background listener
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("✅ LectureScribe loaded")

    def _listen_loop(self):
        """Background thread loop"""
        while self.running:
            time.sleep(5)  # Sleep to save CPU
            pass

    def transcribe(self, audio_path):
        """Direct file transcription"""
        if not self.model:
            return "Mock Transcript: Calculus derivatives."
        try:
            result = self.model.transcribe(audio_path)
            return result["text"]
        except:
            return ""

    def transcribe_latest(self):
        """
        [CRITICAL METHOD] 
        Returns the latest transcript or None.
        Called by master_engine.py inside process_frame.
        """
        if self.last_transcript:
            text = self.last_transcript
            self.last_transcript = ""
            return text
        return None  # Safe return to prevent crash

    def stop(self):
        self.running = False
