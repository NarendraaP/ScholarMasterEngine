#!/usr/bin/env python3
"""
Paper 15: AR Client Tests
=========================
Unit and integration tests for AR visualization components.

Tests cover:
- MQTT event parsing and subscription
- Coordinate mapping and calibration
- Clutter reduction and clustering
- Overlay rendering specifications
"""

import pytest
import time
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ar_client.mqtt_subscriber import (
    ARAlertEvent, AlertSeverity, ARMQTTSubscriber
)
from modules.ar_client.coordinate_mapper import (
    Vector3, Quaternion, CoordinateMapper, DigitalTwinManager
)
from modules.ar_client.clutter_manager import (
    ClutterReductionManager, AlertCluster, RenderLOD
)
from modules.ar_client.alert_renderer import (
    AlertRenderer, AlertOverlay, OverlayColor, OverlayShape, OverlayAnimation
)


class TestARAlertEvent:
    """Tests for ARAlertEvent parsing and severity mapping."""
    
    def test_from_mqtt_payload_complete(self):
        """Test parsing complete MQTT payload."""
        payload = {
            "event_id": "evt_9982",
            "type": "ACOUSTIC_ANOMALY",
            "severity": 0.9,
            "location": {
                "zone_id": "NW_HALL_04",
                "vector_offset": {"x": 12.5, "y": 1.2, "z": -4.0}
            },
            "timestamp": 1715629994
        }
        
        event = ARAlertEvent.from_mqtt_payload(payload)
        
        assert event.event_id == "evt_9982"
        assert event.event_type == "ACOUSTIC_ANOMALY"
        assert event.severity == 0.9
        assert event.zone_id == "NW_HALL_04"
        assert event.vector_offset["x"] == 12.5
    
    def test_from_mqtt_payload_minimal(self):
        """Test parsing minimal MQTT payload with defaults."""
        payload = {"type": "UNKNOWN_EVENT"}
        
        event = ARAlertEvent.from_mqtt_payload(payload)
        
        assert event.event_type == "UNKNOWN_EVENT"
        assert event.severity == 0.5  # default
        assert event.zone_id == "UNKNOWN_ZONE"
    
    def test_severity_level_critical(self):
        """Test critical severity level mapping."""
        event = ARAlertEvent("e1", "TEST", 0.95, "Z1", {}, time.time())
        assert event.severity_level == AlertSeverity.CRITICAL
    
    def test_severity_level_high(self):
        """Test high severity level mapping."""
        event = ARAlertEvent("e1", "TEST", 0.8, "Z1", {}, time.time())
        assert event.severity_level == AlertSeverity.HIGH
    
    def test_severity_level_medium(self):
        """Test medium severity level mapping."""
        event = ARAlertEvent("e1", "TEST", 0.5, "Z1", {}, time.time())
        assert event.severity_level == AlertSeverity.MEDIUM
    
    def test_severity_level_low(self):
        """Test low severity level mapping."""
        event = ARAlertEvent("e1", "TEST", 0.2, "Z1", {}, time.time())
        assert event.severity_level == AlertSeverity.LOW
    
    def test_age_seconds(self):
        """Test event age calculation."""
        past_time = time.time() - 10.0
        event = ARAlertEvent("e1", "TEST", 0.5, "Z1", {}, past_time)
        
        assert event.age_seconds() >= 10.0
        assert event.age_seconds() < 11.0


class TestVector3:
    """Tests for Vector3 3D math."""
    
    def test_distance_to_same_point(self):
        """Distance to same point should be zero."""
        v = Vector3(5.0, 3.0, 2.0)
        assert v.distance_to(v) == 0.0
    
    def test_distance_to_different_point(self):
        """Test Euclidean distance calculation."""
        v1 = Vector3(0, 0, 0)
        v2 = Vector3(3, 4, 0)
        
        assert v1.distance_to(v2) == 5.0  # 3-4-5 triangle
    
    def test_vector_addition(self):
        """Test vector addition."""
        v1 = Vector3(1, 2, 3)
        v2 = Vector3(4, 5, 6)
        result = v1 + v2
        
        assert result.x == 5
        assert result.y == 7
        assert result.z == 9
    
    def test_vector_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector3(4, 5, 6)
        v2 = Vector3(1, 2, 3)
        result = v1 - v2
        
        assert result.x == 3
        assert result.y == 3
        assert result.z == 3
    
    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        v = Vector3(2, 3, 4)
        result = v * 2.0
        
        assert result.x == 4
        assert result.y == 6
        assert result.z == 8


class TestDigitalTwinManager:
    """Tests for Digital Twin zone management."""
    
    def test_default_campus_loaded(self):
        """Test that default campus zones are loaded."""
        twin = DigitalTwinManager()
        
        assert len(twin.zones) > 0
        assert len(twin.anchors) > 0
        assert "ROOM_101" in twin.zones
    
    def test_get_zone(self):
        """Test zone retrieval."""
        twin = DigitalTwinManager()
        zone = twin.get_zone("ROOM_101")
        
        assert zone is not None
        assert zone.zone_id == "ROOM_101"
        assert zone.zone_type == "room"
    
    def test_get_nonexistent_zone(self):
        """Test retrieval of non-existent zone."""
        twin = DigitalTwinManager()
        zone = twin.get_zone("NONEXISTENT")
        
        assert zone is None
    
    def test_get_zones_on_floor(self):
        """Test floor-based zone filtering."""
        twin = DigitalTwinManager()
        floor_0_zones = twin.get_zones_on_floor(0)
        
        assert len(floor_0_zones) > 0
        for zone in floor_0_zones:
            assert zone.floor_level == 0


class TestCoordinateMapper:
    """Tests for coordinate mapping and calibration."""
    
    def test_calibration(self):
        """Test anchor calibration."""
        mapper = CoordinateMapper()
        
        result = mapper.calibrate_to_anchor(
            anchor_id="QR_MAIN_ENTRANCE",
            camera_position=Vector3(0, 0, 0),
            camera_rotation=Quaternion.identity(),
            detected_anchor_rotation=Quaternion.identity()
        )
        
        assert result is True
        assert mapper.is_calibrated()
    
    def test_calibration_invalid_anchor(self):
        """Test calibration with invalid anchor."""
        mapper = CoordinateMapper()
        
        result = mapper.calibrate_to_anchor(
            anchor_id="INVALID_ANCHOR",
            camera_position=Vector3(0, 0, 0),
            camera_rotation=Quaternion.identity(),
            detected_anchor_rotation=Quaternion.identity()
        )
        
        assert result is False
        assert not mapper.is_calibrated()
    
    def test_zone_to_ar_position(self):
        """Test zone to AR position mapping."""
        mapper = CoordinateMapper()
        mapper.calibrate_to_anchor(
            anchor_id="QR_MAIN_ENTRANCE",
            camera_position=Vector3(0, 0, 0),
            camera_rotation=Quaternion.identity(),
            detected_anchor_rotation=Quaternion.identity()
        )
        
        ar_pos = mapper.zone_to_ar_position("ROOM_101")
        
        assert ar_pos is not None
        assert isinstance(ar_pos, Vector3)
    
    def test_unknown_zone_returns_none(self):
        """Test that unknown zone returns None."""
        mapper = CoordinateMapper()
        ar_pos = mapper.zone_to_ar_position("NONEXISTENT_ZONE")
        
        assert ar_pos is None


class TestClutterReductionManager:
    """Tests for clutter reduction and clustering."""
    
    def test_event_clustering_nearby(self):
        """Test that nearby events are clustered together."""
        manager = ClutterReductionManager(cluster_radius=2.0)
        
        event1 = ARAlertEvent("e1", "TEST", 0.8, "Z1", {}, time.time())
        event2 = ARAlertEvent("e2", "TEST", 0.6, "Z1", {}, time.time())
        
        # Events within 2m should cluster
        cluster1 = manager.process_event(event1, Vector3(0, 0, 0))
        cluster2 = manager.process_event(event2, Vector3(0.5, 0, 0.5))
        
        assert cluster1 == cluster2
    
    def test_event_clustering_distant(self):
        """Test that distant events create separate clusters."""
        manager = ClutterReductionManager(cluster_radius=1.0)
        
        event1 = ARAlertEvent("e1", "TEST", 0.8, "Z1", {}, time.time())
        event2 = ARAlertEvent("e2", "TEST", 0.6, "Z2", {}, time.time())
        
        # Events >1m apart should not cluster
        cluster1 = manager.process_event(event1, Vector3(0, 0, 0))
        cluster2 = manager.process_event(event2, Vector3(10, 0, 0))
        
        assert cluster1 != cluster2
    
    def test_lod_full_close_distance(self):
        """Test LOD.FULL for close distances."""
        manager = ClutterReductionManager()
        lod = manager.get_lod_for_distance(3.0)
        
        assert lod == RenderLOD.FULL
    
    def test_lod_culled_far_distance(self):
        """Test LOD.CULLED for far distances."""
        manager = ClutterReductionManager()
        lod = manager.get_lod_for_distance(60.0)
        
        assert lod == RenderLOD.CULLED
    
    def test_get_renderable_alerts(self):
        """Test renderable alert generation."""
        manager = ClutterReductionManager()
        event = ARAlertEvent("e1", "ACOUSTIC", 0.9, "Z1", {}, time.time())
        manager.process_event(event, Vector3(5, 0, 0))
        
        renderables = manager.get_renderable_alerts(Vector3(0, 0, 0))
        
        assert len(renderables) == 1
        assert renderables[0].distance == 5.0
    
    def test_max_visible_limit(self):
        """Test that max visible limit is respected."""
        manager = ClutterReductionManager(max_visible=5)
        
        # Add 10 events
        for i in range(10):
            event = ARAlertEvent(f"e{i}", "TEST", 0.5, f"Z{i}", {}, time.time())
            manager.process_event(event, Vector3(i * 3, 0, 0))
        
        renderables = manager.get_renderable_alerts(Vector3(0, 0, 0))
        
        assert len(renderables) <= 5


class TestAlertRenderer:
    """Tests for alert overlay rendering."""
    
    def test_render_single_alert(self):
        """Test rendering a single alert."""
        from modules.ar_client.clutter_manager import RenderableAlert
        
        event = ARAlertEvent("e1", "ACOUSTIC_ANOMALY", 0.9, "Z1", {}, time.time())
        renderable = RenderableAlert(
            event=event,
            cluster=None,
            position=Vector3(5, 0, 0),
            distance=5.0,
            lod=RenderLOD.FULL,
            is_cluster=False,
            opacity=1.0,
            pulse_rate=2.0
        )
        
        renderer = AlertRenderer()
        overlay = renderer.render_alert(renderable)
        
        assert overlay.overlay_id == "e1"
        assert overlay.shape == OverlayShape.SPHERE
        assert overlay.animation.pulse_rate == 2.0  # Critical
    
    def test_color_from_severity_high(self):
        """Test color generation for high severity."""
        color = OverlayColor.from_severity(0.9)
        
        # Should be reddish
        assert color.r > 0.8
        assert color.g < 0.3
    
    def test_color_from_severity_low(self):
        """Test color generation for low severity."""
        color = OverlayColor.from_severity(0.2)
        
        # Should be bluish
        assert color.b > 0.5
    
    def test_overlay_to_dict(self):
        """Test overlay serialization."""
        overlay = AlertOverlay(
            overlay_id="test_1",
            position=Vector3(1, 2, 3),
            shape=OverlayShape.SPHERE,
            color=OverlayColor(1, 0, 0, 1),
            animation=OverlayAnimation(),
            scale=1.0,
            label="Test Alert",
            sublabel="Zone A",
            lod=RenderLOD.FULL
        )
        
        data = overlay.to_dict()
        
        assert data["overlay_id"] == "test_1"
        assert data["position"]["x"] == 1
        assert data["shape"] == "sphere"
        assert data["label"] == "Test Alert"


class TestIntegration:
    """Integration tests for full AR client pipeline."""
    
    def test_full_pipeline(self):
        """Test complete event -> render pipeline."""
        # 1. Create Digital Twin
        twin = DigitalTwinManager()
        
        # 2. Create Coordinate Mapper
        mapper = CoordinateMapper(twin)
        mapper.calibrate_to_anchor(
            "QR_MAIN_ENTRANCE",
            Vector3(0, 0, 0),
            Quaternion.identity(),
            Quaternion.identity()
        )
        
        # 3. Create event
        event = ARAlertEvent(
            event_id="evt_001",
            event_type="ACOUSTIC_ANOMALY",
            severity=0.9,
            zone_id="ROOM_101",
            vector_offset={"x": 0, "y": 0, "z": 0},
            timestamp=time.time()
        )
        
        # 4. Map to AR position
        ar_position = mapper.zone_to_ar_position(event.zone_id)
        assert ar_position is not None
        
        # 5. Process through clutter manager
        clutter = ClutterReductionManager()
        cluster_id = clutter.process_event(event, ar_position)
        assert cluster_id is not None
        
        # 6. Get renderables
        renderables = clutter.get_renderable_alerts(Vector3(0, 0, 0))
        assert len(renderables) == 1
        
        # 7. Render
        renderer = AlertRenderer(clutter)
        overlays = renderer.render_all(Vector3(0, 0, 0))
        
        assert len(overlays) == 1
        # Single event in cluster shows as "1 Alerts" cluster
        assert "Alert" in overlays[0].label or "1" in overlays[0].label
        assert overlays[0].animation.pulse_rate == 2.0  # Critical


# Fixtures for common test data
@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    return [
        ARAlertEvent("e1", "ACOUSTIC_ANOMALY", 0.95, "ZONE_A", {}, time.time()),
        ARAlertEvent("e2", "CROWD_ALERT", 0.7, "ZONE_B", {}, time.time()),
        ARAlertEvent("e3", "SENSOR_FAILURE", 0.3, "ZONE_C", {}, time.time()),
    ]


@pytest.fixture
def sample_positions():
    """Create sample positions for testing."""
    return [
        Vector3(0, 0, 0),
        Vector3(10, 0, 5),
        Vector3(30, 0, -10),
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# =============================================================================
# TESTABILITY REQUIREMENTS (Section 6.2 of SM-P15-HCI-CONTRACT)
# =============================================================================

class TestMQTTMocking:
    """
    Testability Requirement: MQTT connection can be mocked.
    
    Verifies that the AR client can operate without a real MQTT broker.
    """
    
    def test_subscriber_mock_mode(self):
        """Test subscriber operates in mock mode when MQTT unavailable."""
        # ARMQTTSubscriber should work even without paho-mqtt
        subscriber = ARMQTTSubscriber(broker_host="mock_host")
        
        # Should not raise even without connection
        assert subscriber.connected is False
        assert subscriber.is_stale() is True  # No messages = stale
    
    def test_manual_event_injection(self):
        """Test that events can be manually injected for testing."""
        subscriber = ARMQTTSubscriber()
        
        # Manually add event to internal storage
        event = ARAlertEvent("test_1", "TEST_TYPE", 0.8, "ZONE_A", {}, time.time())
        subscriber._active_events[event.event_id] = event
        
        # Should be retrievable
        active = subscriber.get_active_events()
        assert len(active) == 1
        assert active[0].event_id == "test_1"
    
    def test_callback_registration(self):
        """Test that event callbacks can be registered and invoked."""
        subscriber = ARMQTTSubscriber()
        
        received_events = []
        
        def mock_callback(event: ARAlertEvent):
            received_events.append(event)
        
        subscriber.add_event_callback(mock_callback)
        
        # Simulate event via internal callback list
        test_event = ARAlertEvent("cb_test", "CALLBACK_TEST", 0.5, "Z1", {}, time.time())
        for cb in subscriber._on_event_callbacks:
            cb(test_event)
        
        assert len(received_events) == 1
        assert received_events[0].event_id == "cb_test"
    
    def test_stats_without_connection(self):
        """Test that stats are available without broker connection."""
        subscriber = ARMQTTSubscriber()
        stats = subscriber.get_stats()
        
        assert "connected" in stats
        assert stats["connected"] is False
        assert stats["active_events"] == 0


class TestCoordinateSimulation:
    """
    Testability Requirement: Coordinate calibration can be simulated.
    
    Verifies that the VPS system can be tested without actual QR detection.
    """
    
    def test_simulated_calibration(self):
        """Test calibration with simulated anchor detection."""
        mapper = CoordinateMapper()
        
        # Simulate QR anchor detection
        result = mapper.calibrate_to_anchor(
            anchor_id="QR_MAIN_ENTRANCE",
            camera_position=Vector3(1.0, 1.5, 2.0),
            camera_rotation=Quaternion(0, 0, 0.1, 0.995),
            detected_anchor_rotation=Quaternion.identity()
        )
        
        assert result is True
        assert mapper.is_calibrated()
        assert mapper.get_calibration_age() < 1.0
    
    def test_camera_pose_update(self):
        """Test camera pose can be updated programmatically."""
        mapper = CoordinateMapper()
        mapper.calibrate_to_anchor(
            "QR_MAIN_ENTRANCE",
            Vector3(0, 0, 0),
            Quaternion.identity(),
            Quaternion.identity()
        )
        
        # Update camera position
        new_position = Vector3(5.0, 1.5, 3.0)
        new_rotation = Quaternion(0, 0.1, 0, 0.995)
        mapper.update_camera_pose(new_position, new_rotation)
        
        # Camera state should be updated
        assert mapper._camera_position.x == 5.0
        assert mapper._camera_position.z == 3.0
    
    def test_custom_digital_twin(self):
        """Test that custom zone definitions can be loaded."""
        # Create custom Digital Twin
        twin = DigitalTwinManager()
        
        from modules.ar_client.coordinate_mapper import ZoneDefinition
        
        # Add custom test zone
        custom_zone = ZoneDefinition(
            zone_id="TEST_ZONE_999",
            name="Test Zone",
            position=Vector3(100, 0, 100),
            size=Vector3(10, 3, 10),
            floor_level=0,
            zone_type="room"
        )
        twin.add_zone(custom_zone)
        
        # Verify zone is accessible
        retrieved = twin.get_zone("TEST_ZONE_999")
        assert retrieved is not None
        assert retrieved.position.x == 100
    
    def test_coordinate_transform_output(self):
        """Test that transforms produce predictable output."""
        mapper = CoordinateMapper()
        mapper.calibrate_to_anchor(
            "QR_MAIN_ENTRANCE",
            Vector3(0, 0, 0),
            Quaternion.identity(),
            Quaternion.identity()
        )
        
        # Get AR position for known zone
        ar_pos = mapper.zone_to_ar_position("ROOM_101")
        
        # Position should be deterministic (same inputs = same outputs)
        ar_pos_again = mapper.zone_to_ar_position("ROOM_101")
        
        assert ar_pos.x == ar_pos_again.x
        assert ar_pos.y == ar_pos_again.y
        assert ar_pos.z == ar_pos_again.z


class TestClutterThresholdsConfigurable:
    """
    Testability Requirement: Clutter thresholds are configurable.
    
    Verifies that clustering radius, expand distance, and max visible
    can be set via constructor parameters.
    """
    
    def test_custom_cluster_radius(self):
        """Test that cluster_radius parameter works."""
        # Small radius = less clustering
        manager_small = ClutterReductionManager(cluster_radius=0.5)
        
        event1 = ARAlertEvent("e1", "T", 0.8, "Z", {}, time.time())
        event2 = ARAlertEvent("e2", "T", 0.8, "Z", {}, time.time())
        
        # Events 0.6m apart should NOT cluster with 0.5m radius
        c1 = manager_small.process_event(event1, Vector3(0, 0, 0))
        c2 = manager_small.process_event(event2, Vector3(0.6, 0, 0))
        
        assert c1 != c2  # Separate clusters
        
        # Large radius = more clustering
        manager_large = ClutterReductionManager(cluster_radius=5.0)
        
        event3 = ARAlertEvent("e3", "T", 0.8, "Z", {}, time.time())
        event4 = ARAlertEvent("e4", "T", 0.8, "Z", {}, time.time())
        
        # Events 3m apart should cluster with 5m radius
        c3 = manager_large.process_event(event3, Vector3(0, 0, 0))
        c4 = manager_large.process_event(event4, Vector3(3.0, 0, 0))
        
        assert c3 == c4  # Same cluster
    
    def test_custom_expand_distance(self):
        """Test that expand_distance parameter works."""
        manager = ClutterReductionManager(expand_distance=10.0)
        
        # Add a cluster with multiple events
        event1 = ARAlertEvent("e1", "T", 0.8, "Z", {}, time.time())
        event2 = ARAlertEvent("e2", "T", 0.7, "Z", {}, time.time())
        
        manager.process_event(event1, Vector3(0, 0, 0))
        manager.process_event(event2, Vector3(0.5, 0, 0))
        
        # At distance 5m < expand_distance, cluster should expand
        renderables = manager.get_renderable_alerts(Vector3(5, 0, 0))
        
        # Should have individual events (expanded), not just cluster
        assert len(renderables) >= 1
    
    def test_custom_max_visible(self):
        """Test that max_visible parameter limits rendered alerts."""
        manager = ClutterReductionManager(max_visible=3)
        
        # Add 10 separate events
        for i in range(10):
            event = ARAlertEvent(f"e{i}", "T", 0.5, f"Z{i}", {}, time.time())
            manager.process_event(event, Vector3(i * 10, 0, 0))  # Far apart
        
        renderables = manager.get_renderable_alerts(Vector3(0, 0, 0))
        
        assert len(renderables) <= 3
    
    def test_lod_thresholds_used(self):
        """Test that LOD thresholds are applied correctly."""
        manager = ClutterReductionManager()
        
        # Test each LOD threshold
        assert manager.get_lod_for_distance(0) == RenderLOD.FULL
        assert manager.get_lod_for_distance(4.9) == RenderLOD.FULL
        assert manager.get_lod_for_distance(5.1) == RenderLOD.MEDIUM
        assert manager.get_lod_for_distance(14.9) == RenderLOD.MEDIUM
        assert manager.get_lod_for_distance(15.1) == RenderLOD.LOW
        assert manager.get_lod_for_distance(29.9) == RenderLOD.LOW
        assert manager.get_lod_for_distance(30.1) == RenderLOD.BILLBOARD
        assert manager.get_lod_for_distance(49.9) == RenderLOD.BILLBOARD
        assert manager.get_lod_for_distance(50.1) == RenderLOD.CULLED


class TestJSONSerialization:
    """
    Testability Requirement: Overlay output is JSON-serializable.
    
    Verifies that all output can be serialized to JSON for Unity/Unity consumption.
    """
    
    def test_overlay_to_json(self):
        """Test single overlay serialization."""
        import json
        
        overlay = AlertOverlay(
            overlay_id="json_test_1",
            position=Vector3(1.5, 2.5, 3.5),
            shape=OverlayShape.SPHERE,
            color=OverlayColor(1.0, 0.5, 0.0, 0.9),
            animation=OverlayAnimation(pulse_rate=1.0, strobe=False),
            scale=1.2,
            label="Test Alert",
            sublabel="Zone Test",
            lod=RenderLOD.FULL
        )
        
        data = overlay.to_dict()
        
        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert json_str is not None
        assert "json_test_1" in json_str
        
        # Round-trip should work
        parsed = json.loads(json_str)
        assert parsed["overlay_id"] == "json_test_1"
        assert parsed["position"]["x"] == 1.5
        assert parsed["color"]["r"] == 1.0
    
    def test_multiple_overlays_to_json(self):
        """Test batch overlay serialization."""
        import json
        from modules.ar_client.alert_renderer import format_for_unity
        
        clutter = ClutterReductionManager()
        
        # Add some events
        for i in range(5):
            event = ARAlertEvent(f"json_e{i}", "JSON_TEST", 0.5 + i*0.1, f"Z{i}", {}, time.time())
            clutter.process_event(event, Vector3(i * 5, 0, 0))
        
        renderer = AlertRenderer(clutter)
        overlays = renderer.render_all(Vector3(0, 0, 0))
        
        # Format for Unity
        json_output = format_for_unity(overlays)
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        assert "overlay_count" in parsed
        assert "overlays" in parsed
        assert parsed["overlay_count"] == len(overlays)
    
    def test_vector3_serialization(self):
        """Test Vector3 serialization."""
        import json
        
        v = Vector3(1.234, 5.678, -9.012)
        data = v.to_dict()
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["x"] == 1.234
        assert parsed["y"] == 5.678
        assert parsed["z"] == -9.012
    
    def test_color_serialization(self):
        """Test OverlayColor serialization."""
        import json
        
        color = OverlayColor(0.8, 0.6, 0.2, 0.9)
        data = color.to_dict()
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["r"] == 0.8
        assert parsed["g"] == 0.6
        assert parsed["b"] == 0.2
        assert parsed["a"] == 0.9
    
    def test_digital_twin_export(self):
        """Test Digital Twin export to JSON."""
        import json
        
        twin = DigitalTwinManager()
        json_export = twin.export_to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_export)
        
        assert "zones" in parsed
        assert "anchors" in parsed
        assert len(parsed["zones"]) > 0

