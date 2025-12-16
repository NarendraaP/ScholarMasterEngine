import json
import os
import time
import datetime
import threading

class NotificationDispatcher:
    def __init__(self, alerts_file="data/alerts.json"):
        self.alerts_file = alerts_file
        self.last_checked_timestamp = datetime.datetime.now().isoformat()
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """
        Starts the background polling thread.
        """
        self.running = True
        self.thread = threading.Thread(target=self._poll_alerts)
        self.thread.daemon = True
        self.thread.start()
        print("🔔 Notification Service Started (Polling data/alerts.json)")

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
            
    def _poll_alerts(self):
        while self.running:
            try:
                new_alerts = self._check_new_alerts()
                
                for alert in new_alerts:
                    self._dispatch(alert)
                    
                # Update timestamp to the latest one processed
                # Note: This simple logic assumes chronological order. 
                # Ideally, we track processed IDs, but timestamp + memory is fine for MVP.
                if new_alerts:
                    # Sort by timestamp to be sure
                    new_alerts.sort(key=lambda x: x.get("timestamp", ""))
                    self.last_checked_timestamp = new_alerts[-1]["timestamp"]
                    
            except Exception as e:
                print(f"⚠️ Notification Poller Error: {e}")
                
            time.sleep(2) # Poll every 2 seconds

    def _check_new_alerts(self):
        """
        Reads alerts.json and filters for messages newer than last_checked_timestamp.
        """
        if not os.path.exists(self.alerts_file):
            return []
            
        try:
            with open(self.alerts_file, "r") as f:
                alerts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
        new_items = []
        for alert in alerts:
            ts = alert.get("timestamp", "")
            if ts > self.last_checked_timestamp:
                new_items.append(alert)
                
        return new_items

    def _dispatch(self, alert):
        """
        Simulates dispatching an alert via SMS/Email.
        """
        alert_type = alert.get("type", "INFO")
        msg = alert.get("msg", "No message")
        zone = alert.get("zone", "Unknown")
        ts = alert.get("timestamp", "")
        
        # In a real system, you would call Twilio / SendGrid here.
        # For audit/demo, we print a structured log.
        print(f"\n🔔 DISPATCHING ALERT [{alert_type}]")
        print(f"   - Zone: {zone}")
        print(f"   - Message: {msg}")
        print(f"   - Time: {ts}")
        print("-" * 40)

if __name__ == "__main__":
    # Test
    dispatcher = NotificationDispatcher()
    dispatcher.start()
    
    # Simulate adding an alert
    print("Simulating an alert in 2s...")
    time.sleep(2)
    
    test_alert = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "Test",
        "msg": "This is a test alert from main",
        "zone": "Test Lab"
    }
    
    # Append to file
    if os.path.exists("data/alerts.json"):
        with open("data/alerts.json", "r") as f:
            alerts = json.load(f)
    else:
        alerts = []
    
    alerts.append(test_alert)
    
    with open("data/alerts.json", "w") as f:
        json.dump(alerts, f, indent=4)
        
    time.sleep(3)
    dispatcher.stop()
