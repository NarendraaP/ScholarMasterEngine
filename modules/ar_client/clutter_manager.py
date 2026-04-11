#!/usr/bin/env python3
"""
Paper 15: Clutter Reduction Manager
===================================
Implements proximity clustering and Level-of-Detail (LOD) management
to prevent AR visual clutter in high-density event scenarios.

Designed to handle Paper 10's 100k+ daily events without cognitive overload.
"""

import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

from .mqtt_subscriber import ARAlertEvent, AlertSeverity
from .coordinate_mapper import Vector3

logger = logging.getLogger(__name__)


class RenderLOD(Enum):
    """Level of Detail for rendering."""
    FULL = 1        # High-poly, all details (d < 5m)
    MEDIUM = 2      # Medium-poly, reduced effects (5m < d < 15m)
    LOW = 3         # Low-poly, minimal (15m < d < 30m)
    BILLBOARD = 4   # 2D sprite only (d > 30m)
    CULLED = 5      # Not rendered (outside frustum or > 50m)


@dataclass
class AlertCluster:
    """
    A cluster of spatially-grouped alerts.
    
    Collapses multiple nearby events into a single cluster node
    when viewed from distance, expanding as the user approaches.
    """
    cluster_id: str
    center: Vector3
    events: List[ARAlertEvent] = field(default_factory=list)
    max_severity: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    @property
    def event_count(self) -> int:
        return len(self.events)
    
    @property
    def severity_level(self) -> AlertSeverity:
        """Return highest severity in cluster."""
        if self.max_severity >= 0.9:
            return AlertSeverity.CRITICAL
        elif self.max_severity >= 0.7:
            return AlertSeverity.HIGH
        elif self.max_severity >= 0.3:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW
    
    def add_event(self, event: ARAlertEvent, position: Vector3):
        """Add event to cluster and update center."""
        self.events.append(event)
        self.max_severity = max(self.max_severity, event.severity)
        
        # Update center (running average)
        n = len(self.events)
        self.center = Vector3(
            (self.center.x * (n - 1) + position.x) / n,
            (self.center.y * (n - 1) + position.y) / n,
            (self.center.z * (n - 1) + position.z) / n
        )
        self.last_updated = time.time()
    
    def remove_event(self, event_id: str) -> bool:
        """Remove event from cluster by ID."""
        for i, event in enumerate(self.events):
            if event.event_id == event_id:
                self.events.pop(i)
                # Recalculate max severity
                self.max_severity = max((e.severity for e in self.events), default=0.0)
                self.last_updated = time.time()
                return True
        return False
    
    def get_dominant_type(self) -> str:
        """Get the most common event type in cluster."""
        if not self.events:
            return "UNKNOWN"
        
        type_counts: Dict[str, int] = {}
        for event in self.events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1
        
        return max(type_counts, key=type_counts.get)
    
    def should_expand(self, distance: float, expand_threshold: float = 2.0) -> bool:
        """Check if cluster should expand to show individual events."""
        return distance < expand_threshold


@dataclass
class RenderableAlert:
    """
    Alert prepared for rendering with LOD and visibility info.
    """
    event: Optional[ARAlertEvent]
    cluster: Optional[AlertCluster]
    position: Vector3
    distance: float
    lod: RenderLOD
    is_cluster: bool
    opacity: float = 1.0
    pulse_rate: float = 0.0  # Hz, 0 = static
    
    @property
    def label(self) -> str:
        """Generate display label."""
        if self.is_cluster and self.cluster:
            return f"{self.cluster.event_count} Events"
        elif self.event:
            return self.event.event_type.replace("_", " ").title()
        return "Unknown"


class ClutterReductionManager:
    """
    Manages alert clustering and Level-of-Detail for AR rendering.
    
    Features:
    - Proximity-based clustering (events within 1m merged)
    - Distance-based LOD (detail reduces with distance)
    - View frustum culling (off-screen not rendered)
    - Priority sorting (critical alerts rendered first)
    
    This is designed to handle Paper 10's 100k+ daily events
    without overwhelming the operator's cognitive bandwidth.
    """
    
    # Clustering parameters
    CLUSTER_RADIUS = 1.0  # meters - events within this radius are clustered
    EXPAND_DISTANCE = 2.0  # meters - clusters expand when closer than this
    
    # LOD thresholds (meters)
    LOD_FULL_DISTANCE = 5.0
    LOD_MEDIUM_DISTANCE = 15.0
    LOD_LOW_DISTANCE = 30.0
    LOD_CULL_DISTANCE = 50.0
    
    # Rendering limits
    MAX_VISIBLE_ALERTS = 50  # Maximum simultaneous visible alerts
    MAX_VISIBLE_CLUSTERS = 20  # Maximum visible clusters
    
    def __init__(
        self,
        cluster_radius: float = 1.0,
        expand_distance: float = 2.0,
        max_visible: int = 50
    ):
        """
        Initialize clutter reduction manager.
        
        Args:
            cluster_radius: Distance within which events are clustered
            expand_distance: Distance at which clusters expand
            max_visible: Maximum visible alerts/clusters
        """
        self.cluster_radius = cluster_radius
        self.expand_distance = expand_distance
        self.max_visible = max_visible
        
        self._clusters: Dict[str, AlertCluster] = {}
        self._event_to_cluster: Dict[str, str] = {}
        self._next_cluster_id = 0
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "clusters_created": 0,
            "clusters_merged": 0,
            "alerts_culled": 0
        }
    
    def process_event(
        self,
        event: ARAlertEvent,
        position: Vector3
    ) -> str:
        """
        Process a new event and assign to appropriate cluster.
        
        Args:
            event: The alert event
            position: Position in AR space
        
        Returns:
            Cluster ID the event was assigned to
        """
        self.stats["events_processed"] += 1
        
        # Find nearby cluster
        nearest_cluster = None
        nearest_distance = float('inf')
        
        for cluster_id, cluster in self._clusters.items():
            distance = cluster.center.distance_to(position)
            if distance < self.cluster_radius and distance < nearest_distance:
                nearest_cluster = cluster
                nearest_distance = distance
        
        if nearest_cluster:
            # Add to existing cluster
            nearest_cluster.add_event(event, position)
            self._event_to_cluster[event.event_id] = nearest_cluster.cluster_id
            return nearest_cluster.cluster_id
        else:
            # Create new cluster
            cluster_id = f"cluster_{self._next_cluster_id}"
            self._next_cluster_id += 1
            
            cluster = AlertCluster(
                cluster_id=cluster_id,
                center=position,
                events=[event],
                max_severity=event.severity
            )
            self._clusters[cluster_id] = cluster
            self._event_to_cluster[event.event_id] = cluster_id
            self.stats["clusters_created"] += 1
            
            return cluster_id
    
    def remove_event(self, event_id: str):
        """Remove an event (e.g., acknowledged or expired)."""
        cluster_id = self._event_to_cluster.get(event_id)
        if not cluster_id:
            return
        
        cluster = self._clusters.get(cluster_id)
        if cluster:
            cluster.remove_event(event_id)
            # Remove empty clusters
            if cluster.event_count == 0:
                del self._clusters[cluster_id]
        
        del self._event_to_cluster[event_id]
    
    def get_lod_for_distance(self, distance: float) -> RenderLOD:
        """Determine LOD based on distance."""
        if distance > self.LOD_CULL_DISTANCE:
            return RenderLOD.CULLED
        elif distance > self.LOD_LOW_DISTANCE:
            return RenderLOD.BILLBOARD
        elif distance > self.LOD_MEDIUM_DISTANCE:
            return RenderLOD.LOW
        elif distance > self.LOD_FULL_DISTANCE:
            return RenderLOD.MEDIUM
        return RenderLOD.FULL
    
    def get_pulse_rate(self, severity: float) -> float:
        """Get animation pulse rate based on severity."""
        if severity >= 0.9:
            return 2.0  # Fast strobe for critical
        elif severity >= 0.7:
            return 1.0  # Medium pulse for high
        elif severity >= 0.3:
            return 0.5  # Slow pulse for medium
        return 0.0  # Static for low
    
    def get_opacity_for_distance(self, distance: float) -> float:
        """Calculate opacity based on distance (depth cueing)."""
        if distance < self.LOD_FULL_DISTANCE:
            return 1.0
        elif distance < self.LOD_CULL_DISTANCE:
            # Linear fade from 1.0 to 0.3
            t = (distance - self.LOD_FULL_DISTANCE) / (self.LOD_CULL_DISTANCE - self.LOD_FULL_DISTANCE)
            return 1.0 - (0.7 * t)
        return 0.0
    
    def get_renderable_alerts(
        self,
        camera_position: Vector3,
        min_severity: float = 0.0
    ) -> List[RenderableAlert]:
        """
        Get list of alerts/clusters prepared for rendering.
        
        Applies:
        - Severity filtering
        - Distance-based LOD
        - Cluster expansion
        - Priority sorting
        - Max visible limit
        
        Args:
            camera_position: Current camera position
            min_severity: Minimum severity to display
        
        Returns:
            List of RenderableAlert objects sorted by priority
        """
        renderables: List[RenderableAlert] = []
        
        for cluster in self._clusters.values():
            if cluster.max_severity < min_severity:
                continue
            
            distance = cluster.center.distance_to(camera_position)
            lod = self.get_lod_for_distance(distance)
            
            if lod == RenderLOD.CULLED:
                self.stats["alerts_culled"] += 1
                continue
            
            # Should we expand the cluster?
            if cluster.should_expand(distance, self.expand_distance) and cluster.event_count > 1:
                # Render individual events
                for event in cluster.events:
                    if event.severity < min_severity:
                        continue
                    
                    renderables.append(RenderableAlert(
                        event=event,
                        cluster=None,
                        position=cluster.center,  # Simplified - would use event position
                        distance=distance,
                        lod=lod,
                        is_cluster=False,
                        opacity=self.get_opacity_for_distance(distance),
                        pulse_rate=self.get_pulse_rate(event.severity)
                    ))
            else:
                # Render as cluster
                renderables.append(RenderableAlert(
                    event=None,
                    cluster=cluster,
                    position=cluster.center,
                    distance=distance,
                    lod=lod,
                    is_cluster=True,
                    opacity=self.get_opacity_for_distance(distance),
                    pulse_rate=self.get_pulse_rate(cluster.max_severity)
                ))
        
        # Sort by priority (severity * proximity)
        renderables.sort(
            key=lambda r: (
                (r.cluster.max_severity if r.cluster else r.event.severity) /
                max(r.distance, 0.1)
            ),
            reverse=True
        )
        
        # Limit to max visible
        if len(renderables) > self.max_visible:
            renderables = renderables[:self.max_visible]
        
        return renderables
    
    def get_stats(self) -> Dict:
        """Get manager statistics."""
        return {
            **self.stats,
            "active_clusters": len(self._clusters),
            "total_events": sum(c.event_count for c in self._clusters.values())
        }
    
    def clear(self):
        """Clear all clusters and events."""
        self._clusters.clear()
        self._event_to_cluster.clear()


class SpatialQuadtree:
    """
    Spatial indexing for efficient frustum culling.
    
    Organizes alerts in a quadtree structure for O(log n)
    visibility queries instead of O(n).
    """
    
    def __init__(
        self,
        bounds_min: Vector3,
        bounds_max: Vector3,
        max_items: int = 10,
        max_depth: int = 8
    ):
        """
        Initialize quadtree.
        
        Args:
            bounds_min: Minimum corner of bounding box
            bounds_max: Maximum corner of bounding box
            max_items: Max items before subdivision
            max_depth: Maximum tree depth
        """
        self.bounds_min = bounds_min
        self.bounds_max = bounds_max
        self.max_items = max_items
        self.max_depth = max_depth
        
        self.items: List[tuple] = []  # (position, data)
        self.children: Optional[List["SpatialQuadtree"]] = None
        self.depth = 0
    
    def insert(self, position: Vector3, data: any) -> bool:
        """Insert item at position."""
        if not self._contains(position):
            return False
        
        if len(self.items) < self.max_items or self.depth >= self.max_depth:
            self.items.append((position, data))
            return True
        
        # Subdivide if needed
        if self.children is None:
            self._subdivide()
        
        for child in self.children:
            if child.insert(position, data):
                return True
        
        return False
    
    def query_sphere(self, center: Vector3, radius: float) -> List:
        """Query items within sphere."""
        results = []
        
        if not self._intersects_sphere(center, radius):
            return results
        
        for pos, data in self.items:
            if pos.distance_to(center) <= radius:
                results.append(data)
        
        if self.children:
            for child in self.children:
                results.extend(child.query_sphere(center, radius))
        
        return results
    
    def _contains(self, point: Vector3) -> bool:
        """Check if point is within bounds."""
        return (
            self.bounds_min.x <= point.x <= self.bounds_max.x and
            self.bounds_min.y <= point.y <= self.bounds_max.y and
            self.bounds_min.z <= point.z <= self.bounds_max.z
        )
    
    def _intersects_sphere(self, center: Vector3, radius: float) -> bool:
        """Check if sphere intersects bounding box."""
        # Find closest point on box to sphere center
        closest = Vector3(
            max(self.bounds_min.x, min(center.x, self.bounds_max.x)),
            max(self.bounds_min.y, min(center.y, self.bounds_max.y)),
            max(self.bounds_min.z, min(center.z, self.bounds_max.z))
        )
        return closest.distance_to(center) <= radius
    
    def _subdivide(self):
        """Subdivide into 8 children (octree)."""
        mid = Vector3(
            (self.bounds_min.x + self.bounds_max.x) / 2,
            (self.bounds_min.y + self.bounds_max.y) / 2,
            (self.bounds_min.z + self.bounds_max.z) / 2
        )
        
        self.children = []
        corners = [
            (self.bounds_min, mid),
            (Vector3(mid.x, self.bounds_min.y, self.bounds_min.z), 
             Vector3(self.bounds_max.x, mid.y, mid.z)),
            # ... (simplified - full octree would have 8 children)
        ]
        
        for bmin, bmax in corners[:2]:  # Simplified to 2 children for demo
            child = SpatialQuadtree(bmin, bmax, self.max_items, self.max_depth)
            child.depth = self.depth + 1
            self.children.append(child)


if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.DEBUG)
    
    print("🎯 Testing Clutter Reduction Manager")
    print("=" * 50)
    
    manager = ClutterReductionManager()
    
    # Simulate events at various positions
    test_events = [
        (ARAlertEvent("evt_1", "ACOUSTIC_ANOMALY", 0.9, "ZONE_A", {"x": 0, "y": 0, "z": 0}, time.time()), Vector3(0, 0, 0)),
        (ARAlertEvent("evt_2", "CROWD_ALERT", 0.7, "ZONE_A", {"x": 0.5, "y": 0, "z": 0.5}, time.time()), Vector3(0.5, 0, 0.5)),
        (ARAlertEvent("evt_3", "ACOUSTIC_ANOMALY", 0.8, "ZONE_B", {"x": 10, "y": 0, "z": 0}, time.time()), Vector3(10, 0, 0)),
        (ARAlertEvent("evt_4", "SENSOR_FAILURE", 0.3, "ZONE_C", {"x": 30, "y": 0, "z": 0}, time.time()), Vector3(30, 0, 0)),
    ]
    
    print("\n📥 Processing events...")
    for event, position in test_events:
        cluster_id = manager.process_event(event, position)
        print(f"  {event.event_id} → {cluster_id}")
    
    print(f"\n📊 Stats: {manager.get_stats()}")
    
    # Get renderables from camera at origin
    camera_pos = Vector3(0, 0, 0)
    renderables = manager.get_renderable_alerts(camera_pos)
    
    print(f"\n🎨 Renderable alerts ({len(renderables)}):")
    for r in renderables:
        print(f"  [{r.lod.name}] {r.label} @ {r.distance:.1f}m (opacity: {r.opacity:.2f}, pulse: {r.pulse_rate}Hz)")
