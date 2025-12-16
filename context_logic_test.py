import time
import random

class ContextEngine:
    """Simulates Paper 2: Context-Aware Emotion Correction"""
    
    def __init__(self):
        self.subjects = ['Math', 'History', 'Math', 'Math', 'History', 'Math']
        self.current_index = 0
    
    def get_raw_emotion(self):
        """Simulate AI emotion detection (biased towards 'Sad')"""
        # Random but weighted towards sadness
        sadness = random.uniform(0.75, 0.95)
        happiness = round(1.0 - sadness, 2)
        return {
            'emotion': 'Sad',
            'sadness': round(sadness, 2),
            'happiness': happiness
        }
    
    def apply_context_correction(self, subject, raw_emotion):
        """
        Context Rule Implementation:
        - Math + Sad = Concentrating (High Engagement)
        - History + Sad = Bored (Low Engagement)
        """
        sadness_score = raw_emotion['sadness']
        
        if subject == 'Math' and raw_emotion['emotion'] == 'Sad':
            # High sadness in Math = Deep Concentration
            engagement = 0.9
            status = 'CONCENTRATING'
        elif subject == 'History' and raw_emotion['emotion'] == 'Sad':
            # High sadness in History = Bored
            engagement = 0.2
            status = 'BORED'
        else:
            # Default fallback
            engagement = 0.5
            status = 'NEUTRAL'
        
        return {
            'engagement': engagement,
            'status': status
        }
    
    def get_next_subject(self):
        """Cycle through subjects"""
        subject = self.subjects[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.subjects)
        return subject

def main():
    print("=" * 80)
    print("Paper 2: Context Engine - Logic Verification")
    print("=" * 80)
    print("Demonstrating Context-Aware Emotion Correction")
    print("Press Ctrl+C to stop\n")
    
    engine = ContextEngine()
    
    try:
        while True:
            # Get current subject
            subject = engine.get_next_subject()
            
            # Simulate raw AI emotion detection
            raw_emotion = engine.get_raw_emotion()
            
            # Apply context correction
            corrected = engine.apply_context_correction(subject, raw_emotion)
            
            # Format output log
            log = (f"[CLASS: {subject.upper()}] "
                   f"Raw Emotion: {raw_emotion['emotion']} ({raw_emotion['sadness']}) "
                   f"-> [CONTEXT ENGINE] Status: {corrected['status']} "
                   f"(Score: {corrected['engagement']})")
            
            print(log)
            
            # Wait 0.5 seconds
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n✅ Context Engine verification complete")

if __name__ == "__main__":
    main()
