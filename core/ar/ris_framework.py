import json
import time
import random
import uuid
import paho.mqtt.client as mqtt

# Mock MQTT settings for reproducible local simulation
MQTT_BROKER = "localhost" 
MQTT_PORT = 1883
MQTT_TOPIC = "campus/telemetry/alerts"

ZONES = ["NW_HALL_04", "EAST_WING_02", "LIBRARY_MAIN", "CAFETERIA", "STAIRWELL_SOUTH"]
EVENT_TYPES = ["ACOUSTIC_ANOMALY", "CAPACITY_VIOLATION", "SENSOR_FAILURE"]

class RISFramework:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT):
        self.client = mqtt.Client(client_id="RISF_Stress_Harness")
        self.broker = broker
        self.port = port
        self.connected = False
        
    def connect(self):
        try:
            # We wrap in try-except so the simulation can run locally even if no mock Mosquitto broker is installed
            self.client.connect(self.broker, self.port, 60)
            self.connected = True
            print(f"[RISF] Connected to MQTT Broker at {self.broker}:{self.port}")
        except ConnectionRefusedError:
            print("[RISF] Warning: No local MQTT Broker found. Running in MOCK mode (printing to console).")

    def generate_event(self):
        """Generates a synthetic telemetry event matching the JSON schema from Paper 15, Listing 1."""
        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:6]}",
            "type": random.choice(EVENT_TYPES),
            "severity": round(random.uniform(0.1, 1.0), 2),
            "location": {
                "zone_id": random.choice(ZONES),
                # Generate a random 3D spatial coordinate offset for the "Visual Positioning Anchor"
                "vector_offset": {
                    "x": round(random.uniform(-15.0, 15.0), 2),
                    "y": round(random.uniform(-2.0, 5.0), 2),
                    "z": round(random.uniform(-15.0, 15.0), 2)
                }
            },
            "timestamp": int(time.time())
        }
        return event

    def run_stress_test(self, num_events=150, delay_ms=50):
        print(f"================================================================")
        print(f"Paper 15: Reproducible Institutional Simulation Framework (RISF)")
        print(f"Initializing Stress Test: Publishing {num_events} abnormal events")
        print(f"================================================================")
        
        self.connect()
        
        for i in range(num_events):
            event_payload = self.generate_event()
            payload_str = json.dumps(event_payload)
            
            if self.connected:
                self.client.publish(MQTT_TOPIC, payload_str)
            
            # Print a sample to console for verification
            if i % 25 == 0:
                print(f"[PUBLISH] {event_payload['type']} | Severity: {event_payload['severity']} | Zone: {event_payload['location']['zone_id']}")
                
            time.sleep(delay_ms / 1000.0)

        print("[RISF] Stress Test Complete.")

if __name__ == "__main__":
    risf = RISFramework()
    # Execute a rapid barrage of 150 events to simulate a multi-point campus failure
    risf.run_stress_test(num_events=150, delay_ms=10)
