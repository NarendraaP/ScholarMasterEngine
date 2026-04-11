#!/usr/bin/env python3
"""
Paper 15: MQTT Event Subscriber for AR Visualization
====================================================
Consumes safety events from the ScholarMaster Engine MQTT broker
and transforms them into AR-renderable alert objects.

Consumes: Paper 6 (Acoustic Events), Paper 9 (Orchestration Events)
Uses: Paper 11 (MQTT Architecture)
"""

import json
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional
from queue import Queue, Empty
import threading

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels with corresponding visualization parameters."""
    LOW = 0.3       # Blue/Green, static
    MEDIUM = 0.5    # Amber, slow pulse (0.5 Hz)
    HIGH = 0.7      # Orange, medium pulse (1.0 Hz)
    CRITICAL = 0.9  # Red, fast pulse (2.0 Hz) + strobe


@dataclass
class ARAlertEvent:
    """
    Alert event formatted for AR visualization.
    
    Privacy Note: Contains NO biometric data, only symbolic metadata.
    """
    event_id: str
    event_type: str
    severity: float
    zone_id: str
    vector_offset: Dict[str, float]  # {"x": float, "y": float, "z": float}
    timestamp: float
    metadata: Dict = field(default_factory=dict)
    
    @property
    def severity_level(self) -> AlertSeverity:
        """Map numeric severity to categorical level."""
        if self.severity >= 0.9:
            return AlertSeverity.CRITICAL
        elif self.severity >= 0.7:
            return AlertSeverity.HIGH
        elif self.severity >= 0.3:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW
    
    @classmethod
    def from_mqtt_payload(cls, payload: Dict) -> "ARAlertEvent":
        """
        Parse MQTT JSON payload into ARAlertEvent.
        
        Expected format:
        {
            "event_id": "evt_9982",
            "type": "ACOUSTIC_ANOMALY",
            "severity": 0.9,
            "location": {
                "zone_id": "NW_HALL_04",
                "vector_offset": {"x": 12.5, "y": 1.2, "z": -4.0}
            },
            "timestamp": 1715629994
        }
        """
        location = payload.get("location", {})
        return cls(
            event_id=payload.get("event_id", f"evt_{int(time.time()*1000)}"),
            event_type=payload.get("type", "UNKNOWN"),
            severity=float(payload.get("severity", 0.5)),
            zone_id=location.get("zone_id", "UNKNOWN_ZONE"),
            vector_offset=location.get("vector_offset", {"x": 0, "y": 0, "z": 0}),
            timestamp=float(payload.get("timestamp", time.time())),
            metadata=payload.get("metadata", {})
        )
    
    def age_seconds(self) -> float:
        """Calculate age of alert in seconds."""
        return time.time() - self.timestamp


class ARMQTTSubscriber:
    """
    MQTT Subscriber for AR Alert Visualization.
    
    Subscribes to ScholarMaster event topics and transforms
    them into AR-renderable alert objects.
    
    Features:
    - Topic filtering by event type
    - Severity-based priority queue
    - Stale event detection (>5s without updates)
    - Event expiry (auto-remove old alerts)
    """
    
    # Topics from the ScholarMaster ecosystem
    TOPIC_ACOUSTIC = "scholar/acoustic/+"
    TOPIC_CROWD = "scholar/crowd/+"
    TOPIC_SCHEDULE = "scholar/schedule/+"
    TOPIC_SENSOR = "scholar/sensor/+"
    TOPIC_ALL_ALERTS = "scholar/+/+"
    
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        topics: Optional[List[str]] = None,
        event_expiry_seconds: float = 300.0,
        stale_threshold_seconds: float = 5.0,
        max_queue_size: int = 1000
    ):
        """
        Initialize AR MQTT subscriber.
        
        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            topics: List of topics to subscribe (default: all alerts)
            event_expiry_seconds: Auto-remove alerts older than this
            stale_threshold_seconds: Mark connection stale after this
            max_queue_size: Maximum events in priority queue
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topics = topics or [self.TOPIC_ALL_ALERTS]
        self.event_expiry_seconds = event_expiry_seconds
        self.stale_threshold_seconds = stale_threshold_seconds
        self.max_queue_size = max_queue_size
        
        # State
        self.connected = False
        self.last_message_time = 0.0
        self.client: Optional[mqtt.Client] = None
        
        # Event storage
        self._event_queue: Queue[ARAlertEvent] = Queue(maxsize=max_queue_size)
        self._active_events: Dict[str, ARAlertEvent] = {}
        self._lock = threading.Lock()
        
        # Callbacks
        self._on_event_callbacks: List[Callable[[ARAlertEvent], None]] = []
        
        # Statistics
        self.stats = {
            "events_received": 0,
            "events_expired": 0,
            "connection_losses": 0
        }
    
    def add_event_callback(self, callback: Callable[[ARAlertEvent], None]):
        """Register callback for new events."""
        self._on_event_callbacks.append(callback)
    
    def connect(self):
        """Connect to MQTT broker and start subscription."""
        if not MQTT_AVAILABLE:
            logger.warning("⚠️  paho-mqtt not available. Running in mock mode.")
            return
        
        self.client = mqtt.Client(client_id=f"ar_client_{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        try:
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"🔗 AR Client connecting to {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.error(f"❌ MQTT connection failed: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle successful connection."""
        if rc == 0:
            self.connected = True
            self.last_message_time = time.time()
            logger.info("✅ AR Client connected to MQTT broker")
            
            # Subscribe to all configured topics
            for topic in self.topics:
                client.subscribe(topic, qos=1)
                logger.info(f"📡 Subscribed to: {topic}")
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        self.connected = False
        self.stats["connection_losses"] += 1
        if rc != 0:
            logger.warning(f"⚠️  AR Client disconnected unexpectedly (rc={rc})")
    
    def _on_message(self, client, userdata, msg):
        """Process incoming MQTT message."""
        self.last_message_time = time.time()
        
        try:
            payload = json.loads(msg.payload.decode())
            event = ARAlertEvent.from_mqtt_payload(payload)
            
            self.stats["events_received"] += 1
            
            # Store in active events
            with self._lock:
                self._active_events[event.event_id] = event
            
            # Add to queue for processing
            try:
                self._event_queue.put_nowait(event)
            except Exception:
                # Queue full - remove oldest, add new
                try:
                    self._event_queue.get_nowait()
                    self._event_queue.put_nowait(event)
                except Empty:
                    pass
            
            # Notify callbacks
            for callback in self._on_event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            logger.debug(f"📨 Event received: {event.event_type} @ {event.zone_id}")
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  Invalid JSON payload: {e}")
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    def get_active_events(self) -> List[ARAlertEvent]:
        """Get all currently active (non-expired) events."""
        self._cleanup_expired()
        with self._lock:
            return list(self._active_events.values())
    
    def get_events_by_severity(self, min_severity: float = 0.0) -> List[ARAlertEvent]:
        """Get events filtered by minimum severity."""
        events = self.get_active_events()
        return [e for e in events if e.severity >= min_severity]
    
    def get_events_sorted_by_priority(self) -> List[ARAlertEvent]:
        """Get events sorted by severity (highest first)."""
        events = self.get_active_events()
        return sorted(events, key=lambda e: e.severity, reverse=True)
    
    def _cleanup_expired(self):
        """Remove events older than expiry threshold."""
        current_time = time.time()
        expired_ids = []
        
        with self._lock:
            for event_id, event in self._active_events.items():
                if event.age_seconds() > self.event_expiry_seconds:
                    expired_ids.append(event_id)
            
            for event_id in expired_ids:
                del self._active_events[event_id]
                self.stats["events_expired"] += 1
        
        if expired_ids:
            logger.debug(f"🗑️  Expired {len(expired_ids)} old events")
    
    def is_stale(self) -> bool:
        """Check if connection is stale (no messages for threshold period)."""
        if not self.connected:
            return True
        return (time.time() - self.last_message_time) > self.stale_threshold_seconds
    
    def acknowledge_event(self, event_id: str):
        """Acknowledge and remove an event (operator response)."""
        with self._lock:
            if event_id in self._active_events:
                del self._active_events[event_id]
                logger.info(f"✓ Event {event_id} acknowledged")
    
    def get_stats(self) -> Dict:
        """Get subscriber statistics."""
        return {
            **self.stats,
            "connected": self.connected,
            "is_stale": self.is_stale(),
            "active_events": len(self._active_events),
            "queue_size": self._event_queue.qsize()
        }
    
    def shutdown(self):
        """Graceful shutdown."""
        if self.client and MQTT_AVAILABLE:
            self.client.loop_stop()
            self.client.disconnect()
        logger.info("🛑 AR MQTT Subscriber shutdown")


# Convenience factory for common use cases
def create_acoustic_subscriber(broker_host: str = "localhost") -> ARMQTTSubscriber:
    """Create subscriber for acoustic anomaly events only."""
    return ARMQTTSubscriber(
        broker_host=broker_host,
        topics=[ARMQTTSubscriber.TOPIC_ACOUSTIC]
    )


def create_safety_subscriber(broker_host: str = "localhost") -> ARMQTTSubscriber:
    """Create subscriber for all safety-related events."""
    return ARMQTTSubscriber(
        broker_host=broker_host,
        topics=[
            ARMQTTSubscriber.TOPIC_ACOUSTIC,
            ARMQTTSubscriber.TOPIC_CROWD
        ]
    )


if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.DEBUG)
    
    print("📡 Testing AR MQTT Subscriber")
    print("=" * 50)
    
    subscriber = ARMQTTSubscriber(broker_host="localhost")
    
    # Add test callback
    def on_event(event: ARAlertEvent):
        print(f"  → {event.event_type}: {event.severity_level.name} @ {event.zone_id}")
    
    subscriber.add_event_callback(on_event)
    subscriber.connect()
    
    try:
        print("\nWaiting for events (Ctrl+C to stop)...")
        while True:
            time.sleep(1)
            if subscriber.is_stale():
                print("⚠️  Connection stale - no recent messages")
    except KeyboardInterrupt:
        pass
    
    print(f"\n📊 Stats: {subscriber.get_stats()}")
    subscriber.shutdown()
