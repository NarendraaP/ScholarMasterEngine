import sqlite3
import time
import random

class TruancyEngine:
    """Paper 4: Governance Engine - Schedule Compliance Checking"""
    
    def __init__(self):
        # Create in-memory database
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        """Create schedule table and insert rules"""
        # Create table
        self.cursor.execute('''
            CREATE TABLE Schedule (
                Student_ID TEXT PRIMARY KEY,
                Expected_Zone TEXT,
                Subject TEXT
            )
        ''')
        
        # Insert schedule rules
        self.cursor.execute('''
            INSERT INTO Schedule (Student_ID, Expected_Zone, Subject)
            VALUES ('ID_9420', 'Zone_1', 'MATH CLASS')
        ''')
        
        self.cursor.execute('''
            INSERT INTO Schedule (Student_ID, Expected_Zone, Subject)
            VALUES ('ID_8301', 'Zone_2', 'PHYSICS LAB')
        ''')
        
        self.conn.commit()
        print("✅ Database initialized with schedule rules\n")
    
    def check_compliance(self, student_id, detected_zone):
        """Check if student is in correct zone"""
        # Query schedule
        self.cursor.execute('''
            SELECT Expected_Zone, Subject FROM Schedule 
            WHERE Student_ID = ?
        ''', (student_id,))
        
        result = self.cursor.fetchone()
        
        if not result:
            return None, None, "UNKNOWN_STUDENT"
        
        expected_zone, subject = result
        
        # Compare zones
        if detected_zone == expected_zone:
            return expected_zone, subject, "COMPLIANT"
        else:
            return expected_zone, subject, "VIOLATION"
    
    def simulate_detection(self):
        """Simulate camera detection and check compliance"""
        # Simulate ID_9420 in wrong zone
        student_id = "ID_9420"
        detected_zone = "Zone_4"  # Canteen
        
        expected_zone, subject, status = self.check_compliance(student_id, detected_zone)
        
        if status == "VIOLATION":
            # Map zone names for display
            zone_names = {
                "Zone_1": "MATH CLASS",
                "Zone_2": "PHYSICS LAB", 
                "Zone_4": "CANTEEN"
            }
            
            detected_location = zone_names.get(detected_zone, detected_zone)
            expected_location = subject
            
            print(f"[ALERT] {student_id} detected in {detected_location}. "
                  f"Schedule says: {expected_location}. Status: {status}")
        else:
            print(f"[OK] {student_id} is in correct zone ({subject})")

def main():
    print("=" * 70)
    print("Paper 4: Governance Engine - Truancy Detection Simulation")
    print("=" * 70)
    print()
    
    engine = TruancyEngine()
    
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop\n")
    
    try:
        iteration = 1
        while True:
            print(f"--- Scan {iteration} ---")
            engine.simulate_detection()
            print()
            time.sleep(1)  # Wait 1 second between checks
            iteration += 1
    
    except KeyboardInterrupt:
        print("\n\n✅ Simulation stopped")
        engine.conn.close()

if __name__ == "__main__":
    main()
