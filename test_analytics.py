from modules.analytics import AnalyticsEngine
import pandas as pd

def test_analytics():
    engine = AnalyticsEngine()
    
    print("Testing get_engagement_metrics...")
    metrics = engine.get_engagement_metrics()
    if not metrics.empty:
        print(metrics)
        # Check if Math has low score and CS has high score
        math_score = metrics[metrics['Subject'] == 'Math']['Engagement Score'].values[0]
        cs_score = metrics[metrics['Subject'] == 'CS']['Engagement Score'].values[0]
        
        print(f"Math Score: {math_score}")
        print(f"CS Score: {cs_score}")
        
        assert math_score < 0.5, "Math should have low engagement"
        assert cs_score > 0.5, "CS should have high engagement"
        print("✅ Engagement scores are correct.")
    else:
        print("❌ No metrics returned.")

    print("\nTesting get_emotion_trends...")
    trends = engine.get_emotion_trends()
    if not trends.empty:
        print(f"Trends data shape: {trends.shape}")
        assert 'timestamp' in trends.columns, "Timestamp column missing"
        assert 'emotion' in trends.columns, "Emotion column missing"
        print("✅ Trends data structure is correct.")
    else:
        print("❌ No trends data returned.")

if __name__ == "__main__":
    try:
        test_analytics()
        print("\n🎉 All analytics tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
