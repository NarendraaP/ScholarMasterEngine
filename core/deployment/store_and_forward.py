import time
import json
import logging
import sqlite3
import random

logging.basicConfig(level=logging.INFO, format='%(message)s')

class StoreAndForwardAgent:
    """
    Paper 11: Priority-Aware MQTT Store-and-Forward
    Implements a volatile SQLite buffer for offline telemetry. Drops low-priority
    events (e.g., Engagement) to preserve queue space for critical metrics when bounding limits are met.
    """
    # simulated max size in abstract units
    MAX_BUFFER_SIZE_EVENTS = 200 
    
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                payload TEXT,
                priority INTEGER,
                timestamp REAL
            )
        ''')
        self.conn.commit()
        self.network_connected = True
        
    def set_network_status(self, connected: bool):
        self.network_connected = connected
        if connected:
            logging.info("[NETWORK] Connectivity Restored! Draining SQLite buffer...")
        else:
            logging.warning("[NETWORK] Disconnected! Activating volatile SQLite Store-and-Forward mode.")
            
    def enqueue_event(self, priority: int, topic: str, payload: dict):
        """Priority 0 = Critical Safety, 1 = Attendance, 2 = Engagement (Low)"""
        current_size = self._get_queue_size()
        usage_ratio = current_size / self.MAX_BUFFER_SIZE_EVENTS
        
        # Priority-Ejection Policy (Algorithm 2)
        if usage_ratio > 0.90:
            logging.critical(f"[BUFFER] Capacity at {usage_ratio*100:.1f}%. Ejecting Priority 2 events!")
            self._drop_lowest_priority(priority_threshold=2)
            
        # Re-check size post eviction
        if self._get_queue_size() >= self.MAX_BUFFER_SIZE_EVENTS:
            if priority == 0:
                # Force drop priority 1 to fit priority 0
                 logging.critical(f"[BUFFER] Absolute Limit! Ejecting Priority 1 to fit Priority 0.")
                 self._drop_lowest_priority(priority_threshold=1)
            else:
                 logging.error(f"[BUFFER] Queue full. Event (P{priority}) dropped.")
                 return
                 
        self.cursor.execute('''
            INSERT INTO telemetry_queue (topic, payload, priority, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (topic, json.dumps(payload), priority, time.time()))
        self.conn.commit()
        
    def process_queue(self):
        """Simulates the background MQTT draining agent."""
        if not self.network_connected:
            return 0
            
        self.cursor.execute('SELECT id, topic, priority FROM telemetry_queue ORDER BY priority ASC, timestamp ASC LIMIT 50')
        events = self.cursor.fetchall()
        
        if not events:
            return 0
            
        successfully_sent = 0
        for event_id, topic, priority in events:
            if not self.network_connected:
                break # Network dropped mid-drain
                
            logging.info(f"  -> MQTT Published: {topic} [Priority {priority}]")
            
            # ACK Received, remove from SQLite
            self.cursor.execute('DELETE FROM telemetry_queue WHERE id = ?', (event_id,))
            self.conn.commit()
            successfully_sent += 1
            
        return successfully_sent
        
    def _get_queue_size(self) -> int:
        self.cursor.execute('SELECT COUNT(*) FROM telemetry_queue')
        return self.cursor.fetchone()[0]
        
    def _drop_lowest_priority(self, priority_threshold: int):
        self.cursor.execute(f'''
            DELETE FROM telemetry_queue 
            WHERE id IN (
                SELECT id FROM telemetry_queue WHERE priority >= {priority_threshold} LIMIT 20
            )
        ''')
        deleted = self.cursor.rowcount
        self.conn.commit()
        logging.info(f"  -> Discarded {deleted} lowest-priority events.")


def test_store_and_forward():
    print("="*80)
    print("Paper 11 MLOps: Storage Constraint & Telemetry Resiliency")
    print("="*80)
    
    # Intentionally restrict the buffer size to 10 for testing
    agent = StoreAndForwardAgent()
    agent.MAX_BUFFER_SIZE_EVENTS = 10 
    
    # 1. Simulate Network Blackout
    agent.set_network_status(False)
    
    # 2. Flood the queue with High & Low priority events
    logging.info("\n--- INJECTING TRAFFIC FLOOD (No Network) ---")
    for i in range(1, 15):
        # Even are Engagement (P2), Odd are Attendance (P1)
        priority = 2 if i % 2 == 0 else 1
        agent.enqueue_event(priority, topic=f"scholarmaster/class_A/event_{i}", payload={"val": i})
        
    # See what is left in the queue
    agent.cursor.execute('SELECT topic, priority FROM telemetry_queue')
    remaining = agent.cursor.fetchall()
    print(f"\nRemaining Queue Size: {len(remaining)} / {agent.MAX_BUFFER_SIZE_EVENTS}")
    for evt in remaining:
        print(f"  Stored: {evt[0]} (Priority {evt[1]})")
        
    # 3. Simulate Network Restored
    print("\n")
    agent.set_network_status(True)
    agent.process_queue()
    print("Test Complete.")
    
if __name__ == "__main__":
    test_store_and_forward()
