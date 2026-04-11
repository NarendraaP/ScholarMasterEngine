#!/usr/bin/env python3
"""
Paper 15: Alert Overlay Renderer
================================
Generates AR-renderable overlay specifications for safety events.

This module produces rendering specifications that would be
consumed by the Unity/ARFoundation client. In production,
this logic runs on the mobile device.

Privacy Note: Renders only symbolic visualization (spheres, icons).
             No biometric data or identifiable information is displayed.
"""

import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .mqtt_subscriber import ARAlertEvent, AlertSeverity
from .coordinate_mapper import Vector3
from .clutter_manager import ClutterReductionManager, RenderableAlert, RenderLOD

logger = logging.getLogger(__name__)


class OverlayShape(Enum):
    """Shape of the AR overlay."""
    SPHERE = "sphere"           # Standard alert marker
    CONE = "cone"               # Directional indicator
    RING = "ring"               # Area boundary
    BILLBOARD = "billboard"     # Distance text/icon
    ARROW = "arrow"             # Navigation waypoint


@dataclass
class OverlayColor:
    """
    RGBA color for overlay rendering.
    Maps to HSV for severity gradient.
    """
    r: float  # 0-1
    g: float  # 0-1
    b: float  # 0-1
    a: float = 1.0  # opacity
    
    @classmethod
    def from_severity(cls, severity: float, opacity: float = 1.0) -> "OverlayColor":
        """
        Generate color from severity level.
        
        Low (0.0-0.3): Blue/Green
        Medium (0.3-0.7): Amber/Yellow
        High (0.7-1.0): Red
        """
        if severity >= 0.7:
            # Red gradient
            t = (severity - 0.7) / 0.3
            return cls(1.0, 0.2 * (1 - t), 0.0, opacity)
        elif severity >= 0.3:
            # Yellow/Amber gradient
            t = (severity - 0.3) / 0.4
            return cls(1.0, 1.0 - 0.5 * t, 0.0, opacity)
        else:
            # Blue/Green gradient
            t = severity / 0.3
            return cls(0.2 * t, 0.8 - 0.3 * t, 1.0 - 0.5 * t, opacity)
    
    def to_hex(self) -> str:
        """Convert to hex color string."""
        return "#{:02x}{:02x}{:02x}".format(
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255)
        )
    
    def to_dict(self) -> Dict[str, float]:
        return {"r": self.r, "g": self.g, "b": self.b, "a": self.a}


@dataclass
class OverlayAnimation:
    """Animation parameters for overlay."""
    pulse_rate: float = 0.0     # Hz (0 = static)
    strobe: bool = False        # Flash effect for critical
    scale_min: float = 1.0      # Minimum scale during pulse
    scale_max: float = 1.0      # Maximum scale during pulse
    glow_intensity: float = 0.0 # Emission strength
    
    @classmethod
    def from_severity(cls, severity: float) -> "OverlayAnimation":
        """Generate animation parameters from severity."""
        if severity >= 0.9:
            return cls(
                pulse_rate=2.0,
                strobe=True,
                scale_min=0.9,
                scale_max=1.3,
                glow_intensity=1.0
            )
        elif severity >= 0.7:
            return cls(
                pulse_rate=1.0,
                strobe=False,
                scale_min=0.95,
                scale_max=1.15,
                glow_intensity=0.7
            )
        elif severity >= 0.3:
            return cls(
                pulse_rate=0.5,
                strobe=False,
                scale_min=0.98,
                scale_max=1.05,
                glow_intensity=0.3
            )
        return cls()  # Static


@dataclass
class AlertOverlay:
    """
    Complete specification for rendering an AR alert overlay.
    
    This is the output format consumed by Unity/ARFoundation.
    """
    overlay_id: str
    position: Vector3
    shape: OverlayShape
    color: OverlayColor
    animation: OverlayAnimation
    scale: float
    label: str
    sublabel: str = ""
    icon: str = ""  # Icon sprite name
    distance_label: str = ""  # "15m" etc.
    is_cluster: bool = False
    event_count: int = 1
    lod: RenderLOD = RenderLOD.FULL
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON/Unity consumption."""
        return {
            "overlay_id": self.overlay_id,
            "position": self.position.to_dict(),
            "shape": self.shape.value,
            "color": self.color.to_dict(),
            "animation": {
                "pulse_rate": self.animation.pulse_rate,
                "strobe": self.animation.strobe,
                "scale_min": self.animation.scale_min,
                "scale_max": self.animation.scale_max,
                "glow_intensity": self.animation.glow_intensity
            },
            "scale": self.scale,
            "label": self.label,
            "sublabel": self.sublabel,
            "icon": self.icon,
            "distance_label": self.distance_label,
            "is_cluster": self.is_cluster,
            "event_count": self.event_count,
            "lod": self.lod.name
        }


class AlertRenderer:
    """
    Generates AR overlay specifications from processed alerts.
    
    Features:
    - Severity-based coloring
    - Distance-based scale and opacity
    - Animation parameters for visual urgency
    - Navigation arrow generation
    - Cluster visualization
    """
    
    # Scale parameters based on LOD
    SCALE_BY_LOD = {
        RenderLOD.FULL: 1.0,
        RenderLOD.MEDIUM: 0.8,
        RenderLOD.LOW: 0.5,
        RenderLOD.BILLBOARD: 0.3,
        RenderLOD.CULLED: 0.0
    }
    
    # Icon mapping for event types
    ICONS = {
        "ACOUSTIC_ANOMALY": "icon_sound_alert",
        "CROWD_ALERT": "icon_crowd",
        "CAPACITY_VIOLATION": "icon_capacity",
        "SENSOR_FAILURE": "icon_sensor_warning",
        "SCHEDULE_VIOLATION": "icon_schedule",
        "UNKNOWN": "icon_alert_generic"
    }
    
    def __init__(self, clutter_manager: Optional[ClutterReductionManager] = None):
        """
        Initialize alert renderer.
        
        Args:
            clutter_manager: Clutter manager for processed alerts
        """
        self.clutter_manager = clutter_manager or ClutterReductionManager()
    
    def render_alert(self, renderable: RenderableAlert) -> AlertOverlay:
        """
        Generate overlay specification from renderable alert.
        
        Args:
            renderable: Processed alert from clutter manager
        
        Returns:
            AlertOverlay specification
        """
        # Get severity for color/animation
        if renderable.is_cluster and renderable.cluster:
            severity = renderable.cluster.max_severity
            event_type = renderable.cluster.get_dominant_type()
            label = f"{renderable.cluster.event_count} Alerts"
            overlay_id = renderable.cluster.cluster_id
        elif renderable.event:
            severity = renderable.event.severity
            event_type = renderable.event.event_type
            label = event_type.replace("_", " ").title()
            overlay_id = renderable.event.event_id
        else:
            severity = 0.5
            event_type = "UNKNOWN"
            label = "Unknown"
            overlay_id = f"overlay_{int(time.time() * 1000)}"
        
        # Determine shape based on LOD and type
        if renderable.lod == RenderLOD.BILLBOARD:
            shape = OverlayShape.BILLBOARD
        elif renderable.is_cluster:
            shape = OverlayShape.RING  # Ring for clusters
        else:
            shape = OverlayShape.SPHERE
        
        # Calculate scale based on LOD
        base_scale = self.SCALE_BY_LOD.get(renderable.lod, 1.0)
        
        # Create color from severity
        color = OverlayColor.from_severity(severity, renderable.opacity)
        
        # Create animation
        animation = OverlayAnimation.from_severity(severity)
        
        # Get icon
        icon = self.ICONS.get(event_type, self.ICONS["UNKNOWN"])
        
        # Distance label
        distance_label = ""
        if renderable.distance > 5.0:
            distance_label = f"{int(renderable.distance)}m"
        
        return AlertOverlay(
            overlay_id=overlay_id,
            position=renderable.position,
            shape=shape,
            color=color,
            animation=animation,
            scale=base_scale,
            label=label,
            sublabel=f"Zone: {renderable.event.zone_id if renderable.event else 'Multiple'}",
            icon=icon,
            distance_label=distance_label,
            is_cluster=renderable.is_cluster,
            event_count=renderable.cluster.event_count if renderable.cluster else 1,
            lod=renderable.lod
        )
    
    def render_all(self, camera_position: Vector3) -> List[AlertOverlay]:
        """
        Render all active alerts.
        
        Args:
            camera_position: Current camera position
        
        Returns:
            List of AlertOverlay specifications
        """
        renderables = self.clutter_manager.get_renderable_alerts(camera_position)
        return [self.render_alert(r) for r in renderables]
    
    def create_navigation_arrow(
        self,
        target_position: Vector3,
        camera_position: Vector3,
        label: str = ""
    ) -> AlertOverlay:
        """
        Create navigation arrow pointing to target.
        
        Used for directional guidance to events.
        """
        # Calculate direction vector
        direction = target_position - camera_position
        distance = direction.distance_to(Vector3(0, 0, 0))
        
        # Place arrow 2m in front of camera
        arrow_distance = 2.0
        if distance > 0:
            normalized = direction * (arrow_distance / distance)
            arrow_position = camera_position + normalized
        else:
            arrow_position = camera_position + Vector3(0, 0, arrow_distance)
        
        return AlertOverlay(
            overlay_id=f"nav_arrow_{int(time.time() * 1000)}",
            position=arrow_position,
            shape=OverlayShape.ARROW,
            color=OverlayColor(0.2, 0.6, 1.0, 0.9),  # Blue navigation color
            animation=OverlayAnimation(),  # Static
            scale=0.5,
            label=label or "Navigate",
            sublabel=f"{int(distance)}m ahead",
            icon="icon_navigate",
            distance_label=f"{int(distance)}m",
            is_cluster=False,
            event_count=1,
            lod=RenderLOD.FULL
        )
    
    def get_stale_indicator(self) -> Optional[AlertOverlay]:
        """
        Create stale connection indicator overlay.
        
        Shown when MQTT connection is lost for >5 seconds.
        """
        return AlertOverlay(
            overlay_id="stale_indicator",
            position=Vector3(0, 2.0, 1.5),  # Fixed position in HUD
            shape=OverlayShape.BILLBOARD,
            color=OverlayColor(0.7, 0.7, 0.7, 0.8),  # Grey
            animation=OverlayAnimation(pulse_rate=0.5),
            scale=0.3,
            label="⚠️ Stale Data",
            sublabel="Connection lost",
            icon="icon_warning",
            distance_label="",
            is_cluster=False,
            event_count=1,
            lod=RenderLOD.FULL
        )


def format_for_unity(overlays: List[AlertOverlay]) -> str:
    """
    Format overlays as JSON for Unity consumption.
    
    This would be sent over WebSocket/MQTT to the AR client.
    """
    import json
    return json.dumps({
        "overlay_count": len(overlays),
        "timestamp": time.time(),
        "overlays": [o.to_dict() for o in overlays]
    }, indent=2)


if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.DEBUG)
    
    print("🎨 Testing Alert Renderer")
    print("=" * 50)
    
    from .mqtt_subscriber import ARAlertEvent
    
    # Create clutter manager with test events
    clutter = ClutterReductionManager()
    
    events = [
        (ARAlertEvent("evt_1", "ACOUSTIC_ANOMALY", 0.95, "ZONE_A", {}, time.time()), 
         Vector3(5, 0, 3)),
        (ARAlertEvent("evt_2", "CROWD_ALERT", 0.6, "ZONE_B", {}, time.time()), 
         Vector3(15, 0, 10)),
        (ARAlertEvent("evt_3", "SENSOR_FAILURE", 0.3, "ZONE_C", {}, time.time()), 
         Vector3(35, 0, 0)),
    ]
    
    for event, pos in events:
        clutter.process_event(event, pos)
    
    # Create renderer
    renderer = AlertRenderer(clutter)
    
    # Render from camera at origin
    camera = Vector3(0, 0, 0)
    overlays = renderer.render_all(camera)
    
    print(f"\n🎯 Generated {len(overlays)} overlays:")
    for o in overlays:
        print(f"\n  [{o.lod.name}] {o.label}")
        print(f"    Shape: {o.shape.value}")
        print(f"    Color: {o.color.to_hex()}")
        print(f"    Pulse: {o.animation.pulse_rate}Hz")
        print(f"    Distance: {o.distance_label or '<5m'}")
    
    # Export for Unity
    print("\n📄 Unity JSON (sample):")
    json_output = format_for_unity(overlays)
    print(json_output[:500] + "...")
