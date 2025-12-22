import pandas as pd
import os

class AnalyticsEngine:
    def __init__(self, log_file="data/session_log.csv"):
        self.log_file = log_file

    def _load_data(self):
        if os.path.exists(self.log_file):
            return pd.read_csv(self.log_file)
        return pd.DataFrame()

    def get_engagement_metrics(self):
        """
        Calculates Engagement Score per Subject.
        High Engagement: Happy, Neutral, Surprise
        Low Engagement: Sad, Fear, Angry
        Returns DataFrame grouped by Subject.
        """
        df = self._load_data()
        if df.empty:
            return pd.DataFrame()

        # Define engagement mapping
        high_engagement = ["Happy", "Neutral", "Surprise"]
        
        # Calculate score: 1 for High, 0 for Low
        df['score'] = df['emotion'].apply(lambda x: 1 if x in high_engagement else 0)
        
        # Group by Subject and calculate mean score (percentage)
        metrics = df.groupby('subject')['score'].mean().reset_index()
        metrics.columns = ['Subject', 'Engagement Score']
        
        return metrics

    def get_emotion_trends(self):
        """
        Returns data for emotion trends over time.
        """
        df = self._load_data()
        if df.empty:
            return pd.DataFrame()
            
        # Ensure timestamp is datetime (handle ISO format)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
        
        # Drop rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        return df
