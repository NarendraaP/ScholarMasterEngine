from modules.analytics import AnalyticsEngine
import pandas as pd
import os
import pytest

def test_analytics():
    # Setup: Create dummy log file
    test_log_file = "data/test_session_log.csv"
    
    # Create data with ISO8601 timestamps
    # Math: 4 Sad/Fear out of 5 total -> 0/5 = 0.0 engagement (< 0.5)
    # CS: 2 Happy out of 2 total -> 2/2 = 1.0 engagement (> 0.5)
    data = {
        "timestamp": [
            "2025-11-29T10:00:00", 
            "2025-11-29T10:05:00", 
            "2025-11-29T10:10:00",
            "2025-11-29T10:15:00",
            "2025-11-29T10:20:00",
            "2025-11-29T11:00:00",
            "2025-11-29T11:05:00"
        ],
        "subject": ["Math", "Math", "Math", "Math", "Math", "CS", "CS"],
        "emotion": ["Sad", "Fear", "Sad", "Angry", "Fear", "Happy", "Neutral"]
    }
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    df.to_csv(test_log_file, index=False)
    
    try:
        engine = AnalyticsEngine(log_file=test_log_file)
        
        print("Testing get_engagement_metrics...")
        metrics = engine.get_engagement_metrics()
        
        if not metrics.empty:
            print(metrics)
            
            math_row = metrics[metrics['Subject'] == 'Math']
            cs_row = metrics[metrics['Subject'] == 'CS']
            
            if not math_row.empty:
                math_score = math_row['Engagement Score'].values[0]
                print(f"Math Score: {math_score}")
                assert math_score < 0.5, f"Math should have low engagement, got {math_score}"
            
            if not cs_row.empty:
                cs_score = cs_row['Engagement Score'].values[0]
                print(f"CS Score: {cs_score}")
                assert cs_score > 0.5, f"CS should have high engagement, got {cs_score}"
                
            print("✅ Engagement scores are correct.")
        else:
            pytest.fail("❌ No metrics returned.")
    
        print("\nTesting get_emotion_trends...")
        trends = engine.get_emotion_trends()
        if not trends.empty:
            print(f"Trends data shape: {trends.shape}")
            assert 'timestamp' in trends.columns, "Timestamp column missing"
            assert 'emotion' in trends.columns, "Emotion column missing"
            # Verify timestamp parsing
            assert pd.api.types.is_datetime64_any_dtype(trends['timestamp']), "Timestamp not parsed as datetime"
            print("✅ Trends data structure is correct.")
        else:
            pytest.fail("❌ No trends data returned.")
            
    finally:
        # Cleanup
        if os.path.exists(test_log_file):
            os.remove(test_log_file)

if __name__ == "__main__":
    test_analytics()
