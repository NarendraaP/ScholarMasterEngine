#!/usr/bin/env python3
"""
MQTT Publisher for AR Visualization Layer
==========================================
Publishes ScholarMaster events to
 MQTT broker for AR client consumption (Paper 15).

Topics:
- scholarmaster/alerts/safety    - Safety-related alerts
- scholarmaster/alerts/compliance - Compliance violations
- scholarmaster/FL/model_update  - FL model updates
- scholarmaster/audit/log        - Audit trail events (for AR dashboard)

PRIVACY INVARIANT:
Published messages contain ONLY symbolic data:
- Zone IDs
- Severity levels
- Timestamps
- Event types
NEVER raw biometrics, face embeddings, or PII.
"""

import json
import logging
import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Optional MQTT import
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("⚠️  paho-mqtt not installed, MQTT publishing disabled")


@dataclass
class MQTTConfig:
    """MQTT broker configuration."""
    host: str = "localhost"
    port: int = 1883
    keepalive: int = 60
    client_id: str = "scholarmaster_publisher"
    qos: int = 1  # At least once delivery
    retain: bool = False


class MQTTPublisher:
    """
    Publishes ScholarMaster events to MQTT broker.
    
    Used by UnifiedOrchestrator to surface events to AR layer (Paper 15).
    
    Thread Safety: All operations are thread-safe.
    """
    
    # Topic routing based on event type
    TOPIC_MAP = {
        "ALERT_TRIGGERED": "scholarmaster/alerts/safety",
        "AUDIO_ANOMALY": "scholarmaster/alerts/safety",
        "DRIFT_DETECTED": "scholarmaster/alerts/compliance",
        "COMPLIANCE_CHECKED": "scholarmaster/alerts/compliance",
        "MODEL_UPDATED": "scholarmaster/FL/model_update",
        "GRADIENT_READY": "scholarmaster/FL/model_update",
        "AUDIT_LOGGED": "scholarmaster/audit/log",
        "CRYPTO_SHRED_EXECUTED": "scholarmaster/audit/log",
    }
    
    DEFAULT_TOPIC = "scholarmaster/events/general"
    
    def __init__(self, config: Optional[MQTTConfig] = None):
        """
        Initialize MQTT publisher.
        
        Args:
            config: MQTT broker configuration
        """
        self.config = config or MQTTConfig()
        self._client: Optional[Any] = None
        self._connected = False
        self._lock = threading.Lock()
        
        # Statistics
        self._stats = {
            "messages_published": 0,
            "messages_failed": 0,
            "last_publish_time": 0.0
        }
        
        if MQTT_AVAILABLE:
            self._setup_client()
        else:
            logger.warning("⚠️  MQTT not available, running in simulation mode")
    
    def _setup_client(self) -> None:
        """Setup MQTT client with callbacks."""
        self._client = mqtt.Client(client_id=self.config.client_id)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        
        # Try to connect
        try:
            self._client.connect(
                self.config.host,
                self.config.port,
                self.config.keepalive
            )
            self._client.loop_start()
        except Exception as e:
            logger.warning(f"⚠️  MQTT connection failed (will retry): {e}")
    
    def _on_connect(self, client, userdata, flags, rc) -> None:
        """Handle successful connection."""
        if rc == 0:
            self._connected = True
            logger.info(f"✅ MQTT connected to {self.config.host}:{self.config.port}")
        else:
            logger.error(f"❌ MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc) -> None:
        """Handle disconnection."""
        self._connected = False
        if rc != 0:
            logger.warning(f"⚠️  MQTT unexpected disconnect (rc={rc})")
    
    def _on_publish(self, client, userdata, mid) -> None:
        """Handle publish confirmation."""
        with self._lock:
            self._stats["messages_published"] += 1
            self._stats["last_publish_time"] = time.time()
    
    def publish_alert(self, event: Any) -> bool:
        """
        Publish a CrossPaperEvent to the appropriate MQTT topic.
        
        Args:
            event: CrossPaperEvent from UnifiedOrchestrator
            
        Returns:
            True if published successfully
        """
        # Get event data
        event_dict = event.to_dict() if hasattr(event, 'to_dict') else {
            "event_id": getattr(event, 'event_id', f"evt_{int(time.time())}"),
            "type": getattr(event, 'event_type', 'UNKNOWN'),
            "payload": getattr(event, 'payload', {}),
            "timestamp": getattr(event, 'timestamp', time.time())
        }
        
        # Handle enum conversion
        event_type_str = str(event_dict.get("type", "UNKNOWN"))
        if hasattr(event_type_str, 'name'):
            event_type_str = event_type_str.name
        
        # Determine topic
        topic = self.TOPIC_MAP.get(event_type_str, self.DEFAULT_TOPIC)
        
        # Format message (AR-compatible format)
        message = {
            "event_id": event_dict.get("event_id"),
            "type": event_type_str,
            "severity": event_dict.get("payload", {}).get("severity", 0.5),
            "location": {
                "zone_id": event_dict.get("payload", {}).get("zone_id", "UNKNOWN"),
                "vector_offset": event_dict.get("payload", {}).get("offset", {"x": 0, "y": 0, "z": 0})
            },
            "timestamp": int(event_dict.get("timestamp", time.time()))
        }
        
        return self._publish(topic, message)
    
    def publish_raw(self, topic: str, payload: Dict[str, Any]) -> bool:
        """
        Publish raw payload to specific topic.
        
        Args:
            topic: MQTT topic
            payload: Message payload (dict)
            
        Returns:
            True if published successfully
        """
        return self._publish(topic, payload)
    
    def _publish(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Internal publish method."""
        message = json.dumps(payload)
        
        if not MQTT_AVAILABLE or self._client is None:
            # Simulation mode - just log
            logger.debug(f"📤 [SIM] {topic}: {message[:100]}...")
            with self._lock:
                self._stats["messages_published"] += 1
            return True
        
        if not self._connected:
            logger.warning(f"⚠️  MQTT not connected, message dropped: {topic}")
            with self._lock:
                self._stats["messages_failed"] += 1
            return False
        
        try:
            result = self._client.publish(
                topic,
                message,
                qos=self.config.qos,
                retain=self.config.retain
            )
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"❌ MQTT publish failed: {result.rc}")
                with self._lock:
                    self._stats["messages_failed"] += 1
                return False
            
            logger.debug(f"📤 Published to {topic}: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ MQTT publish error: {e}")
            with self._lock:
                self._stats["messages_failed"] += 1
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        with self._lock:
            return {
                **self._stats.copy(),
                "connected": self._connected,
                "mqtt_available": MQTT_AVAILABLE
            }
    
    def shutdown(self) -> None:
        """Gracefully shutdown the publisher."""
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("🛑 MQTT publisher shutdown")


# Convenience functions
def create_publisher(host: str = "localhost", port: int = 1883) -> MQTTPublisher:
    """Create a configured MQTT publisher."""
    config = MQTTConfig(host=host, port=port)
    return MQTTPublisher(config)


if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.DEBUG)
    
    print("=" * 50)
    print("MQTT Publisher Test")
    print("=" * 50)
    
    publisher = MQTTPublisher()
    
    # Simulate event
    class MockEvent:
        event_id = "evt_test_123"
        event_type = "ALERT_TRIGGERED"
        timestamp = time.time()
        payload = {
            "zone_id": "NW_HALL_04",
            "severity": 0.8,
            "alert_type": "NOISE"
        }
        
        def to_dict(self):
            return {
                "event_id": self.event_id,
                "type": self.event_type,
                "timestamp": self.timestamp,
                "payload": self.payload
            }
    
    # Publish test
    result = publisher.publish_alert(MockEvent())
    print(f"Publish result: {result}")
    print(f"Stats: {publisher.get_stats()}")
    
    publisher.shutdown()
    print("\n✅ Test complete!")
