#!/usr/bin/env python3
"""
Paper 11: MQTT Store-and-Forward Buffer
========================================
Partition-tolerant telemetry with SQLite persistence.
Buffers events during network outages and replays on reconnection.
"""

import json
import sqlite3
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.warning("⚠️  'paho-mqtt' not installed. MQTT buffering disabled.")

logger = logging.getLogger(__name__)


class MQTTBuffer:
    """
    Partition-tolerant MQTT client with SQLite persistence.
    
    Features:
    - Store-and-forward during network outages
    - QoS 1 (At Least Once delivery)
    - Automatic reconnection
    - Persistent buffer survives crashes
    """
    
    def __init__(self, 
                 broker_host: str = "localhost",
                 broker_port: int = 1883,
                 buffer_db: str = "data/mqtt_buffer.db",
                 max_buffer_size: int = 10000):
        """
        Initialize MQTT buffer.
        
        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            buffer_db: SQLite database path for buffering
            max_buffer_size: Maximum buffered events (prevents disk overflow)
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.buffer_db = Path(buffer_db)
        self.max_buffer_size = max_buffer_size
        
        self.connected = False
        self.client = None
        self._init_buffer_db()
        
        if MQTT_AVAILABLE:
            self._init_mqtt_client()
    
    def _init_buffer_db(self):
        """Initialize SQLite buffer database."""
        self.buffer_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.buffer_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mqtt_buffer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                qos INTEGER DEFAULT 1,
                timestamp REAL NOT NULL,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"📂 MQTT buffer initialized: {self.buffer_db}")
    
    def _init_mqtt_client(self):
        """Initialize MQTT client with callbacks."""
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        try:
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"🔗 Connecting to MQTT broker {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.error(f"❌ MQTT connection failed: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback on successful connection."""
        if rc == 0:
            self.connected = True
            logger.info("✅ MQTT connected")
            # Drain buffer on reconnection
            threading.Thread(target=self._drain_buffer, daemon=True).start()
        else:
            logger.error(f"❌ MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback on disconnection."""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️  MQTT disconnected unexpectedly (rc={rc}). Buffering events...")
    
    def _on_publish(self, client, userdata, mid):
        """Callback on successful publish."""
        logger.debug(f"📤 Message {mid} published")
    
    def publish(self, topic: str, payload: Dict, qos: int = 1):
        """
        Publish message with automatic buffering on failure.
        
        Args:
            topic: MQTT topic
            payload: Message payload (will be JSON-serialized)
            qos: Quality of Service (0, 1, or 2)
        """
        payload_str = json.dumps(payload)
        
        if self.connected and MQTT_AVAILABLE:
            try:
                result = self.client.publish(topic, payload_str, qos=qos)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.debug(f"📡 Published to {topic}")
                    return
            except Exception as e:
                logger.warning(f"⚠️  Publish failed: {e}. Buffering...")
        
        # Fallback: Buffer to SQLite
        self._buffer_event(topic, payload_str, qos)
    
    def _buffer_event(self, topic: str, payload: str, qos: int):
        """Buffer event to SQLite."""
        conn = sqlite3.connect(self.buffer_db)
        cursor = conn.cursor()
        
        # Check buffer size limit
        cursor.execute("SELECT COUNT(*) FROM mqtt_buffer")
        count = cursor.fetchone()[0]
        
        if count >= self.max_buffer_size:
            logger.warning(f"⚠️  Buffer full ({count} events). Dropping oldest...")
            cursor.execute("DELETE FROM mqtt_buffer WHERE id IN "
                         "(SELECT id FROM mqtt_buffer ORDER BY timestamp ASC LIMIT 100)")
        
        cursor.execute("""
            INSERT INTO mqtt_buffer (topic, payload, qos, timestamp)
            VALUES (?, ?, ?, ?)
        """, (topic, payload, qos, time.time()))
        
        conn.commit()
        conn.close()
        logger.debug(f"💾 Buffered event to {topic} (total buffered: {count + 1})")
    
    def _drain_buffer(self):
        """Replay buffered events after reconnection."""
        conn = sqlite3.connect(self.buffer_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, topic, payload, qos FROM mqtt_buffer ORDER BY timestamp ASC")
        buffered = cursor.fetchall()
        
        if not buffered:
            logger.info("✅ No buffered events to replay")
            conn.close()
            return
        
        logger.info(f"🔄 Replaying {len(buffered)} buffered events...")
        
        for event_id, topic, payload, qos in buffered:
            try:
                if self.connected:
                    self.client.publish(topic, payload, qos=qos)
                    cursor.execute("DELETE FROM mqtt_buffer WHERE id = ?", (event_id,))
                    conn.commit()
                else:
                    logger.warning("⚠️  Disconnected during buffer drain. Pausing...")
                    break
            except Exception as e:
                logger.error(f"❌ Failed to replay event {event_id}: {e}")
        
        conn.close()
        logger.info("✅ Buffer drain complete")
    
    def get_buffer_stats(self) -> Dict:
        """Get buffer statistics."""
        conn = sqlite3.connect(self.buffer_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM mqtt_buffer")
        buffered_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM mqtt_buffer")
        oldest, newest = cursor.fetchone()
        
        conn.close()
        
        return {
            "connected": self.connected,
            "buffered_events": buffered_count,
            "oldest_event_age_s": time.time() - oldest if oldest else None,
            "buffer_path": str(self.buffer_db)
        }
    
    def shutdown(self):
        """Graceful shutdown."""
        if self.client and MQTT_AVAILABLE:
            self.client.loop_stop()
            self.client.disconnect()
        logger.info("🛑 MQTT buffer shutdown")


if __name__ == "__main__":
    # Test MQTT buffering
    logging.basicConfig(level=logging.DEBUG)
    
    print("📡 Testing MQTT Store-and-Forward Buffer")
    print("=" * 50)
    
    buffer = MQTTBuffer(broker_host="localhost")
    
    # Simulate events (will buffer if broker is offline)
    for i in range(5):
        buffer.publish("scholar/test", {"msg": f"Test event {i}", "timestamp": time.time()})
        time.sleep(0.5)
    
    time.sleep(2)
    stats = buffer.get_buffer_stats()
    print(f"\n📊 Buffer Stats: {json.dumps(stats, indent=2)}")
    
    buffer.shutdown()
