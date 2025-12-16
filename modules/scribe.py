import whisper
import os
import re
from collections import Counter

class LectureScribe:
    """
    Lecture Scribe Module (Paper 2).
    Uses OpenAI Whisper to transcribe lecture audio and extract keywords.
    """
    
    def __init__(self, model_size="tiny.en"):
        """
        Initialize Whisper model.
        Args:
            model_size: 'tiny.en' (fastest), 'base.en', 'small.en'
        """
        print(f"🎤 Loading Whisper Model ({model_size})...")
        try:
            self.model = whisper.load_model(model_size)
            print("✅ Whisper Model Loaded")
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            self.model = None

    def transcribe(self, audio_path):
        """
        Transcribe audio file and extract keywords.
        
        Args:
            audio_path: Path to audio file (wav/mp3)
            
        Returns:
            (text, keywords): Transcribed text and list of top keywords
        """
        if not self.model:
            return "", []
        
        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            return "", []
            
        try:
            # Transcribe
            result = self.model.transcribe(audio_path)
            text = result["text"].strip()
            
            # Extract Keywords (Simple Frequency Count)
            # 1. Remove punctuation and lowercase
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            words = clean_text.split()
            
            # 2. Filter stop words (basic list)
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "this", "that", "it", "i", "you", "he", "she", "we", "they"}
            filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
            
            # 3. Count frequency
            word_counts = Counter(filtered_words)
            
            # 4. Get top 5 keywords
            keywords = [word for word, count in word_counts.most_common(5)]
            
            return text, keywords
            
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return "", []

if __name__ == "__main__":
    # Test
    scribe = LectureScribe()
    # Create dummy audio if needed or just print status
    print("✅ LectureScribe initialized")
