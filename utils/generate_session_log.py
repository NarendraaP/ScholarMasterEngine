import csv
import datetime
import random
import os

def generate_mock_log():
    log_file = "data/session_log.csv"
    os.makedirs("data", exist_ok=True)
    
    subjects = ["Math 101", "Physics 101", "Math Advanced"]
    emotions = ["Happy", "Neutral", "Surprise", "Sadness", "Anger", "Fear"]
    zones = ["Lab 1", "Lab 2"]
    
    # Generate 500 records spread over the last 24 hours
    now = datetime.datetime.now()
    records = []
    
    for i in range(500):
        # Time distribution: uniform over last 24 hours
        minutes_ago = random.randint(0, 24 * 60)
        time_stamp = now - datetime.timedelta(minutes=minutes_ago)
        
        subject = random.choice(subjects)
        
        # Bias emotions depending on subject for demo interest
        if subject == "Math 101":
            # Math 101: high happy/neutral
            emotion = random.choices(emotions, weights=[0.4, 0.4, 0.1, 0.05, 0.025, 0.025])[0]
            zone = "Lab 1"
        elif subject == "Physics 101":
            # Physics 101: moderate surprise/neutral
            emotion = random.choices(emotions, weights=[0.2, 0.5, 0.2, 0.05, 0.025, 0.025])[0]
            zone = "Lab 2"
        else:
            # Math Advanced: high neutral/sadness/anger (complex course!)
            emotion = random.choices(emotions, weights=[0.1, 0.4, 0.1, 0.2, 0.1, 0.1])[0]
            zone = "Lab 1"
            
        records.append({
            "timestamp": time_stamp.isoformat(),
            "date": time_stamp.strftime("%Y-%m-%d"),
            "subject": subject,
            "emotion": emotion,
            "zone": zone
        })
        
    # Sort by timestamp
    records.sort(key=lambda x: x["timestamp"])
    
    with open(log_file, "w", newline="") as f:
        fieldnames = ["timestamp", "date", "subject", "emotion", "zone"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"✅ Generated 500 mock engagement records in {log_file}")

if __name__ == "__main__":
    generate_mock_log()
