#!/usr/bin/env python3
"""
Paper 15: Visual Positioning System (VPS) Coordinate Mapper
============================================================
Maps abstract zone IDs from the ScholarMaster Engine to
spatial coordinates for AR overlay rendering.

Uses a Digital Twin approach with QR-code anchors for
aligning the virtual coordinate space with physical reality.
"""

import json
import math
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Vector3:
    """3D Vector for spatial positioning."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Vector3":
        return cls(x=float(d.get("x", 0)), y=float(d.get("y", 0)), z=float(d.get("z", 0)))
    
    def distance_to(self, other: "Vector3") -> float:
        """Euclidean distance to another point."""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass
class Quaternion:
    """
    Quaternion for 3D rotation.
    Used for anchor alignment in AR space.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0
    
    @classmethod
    def identity(cls) -> "Quaternion":
        return cls(0, 0, 0, 1)
    
    def inverse(self) -> "Quaternion":
        """Compute quaternion inverse for rotation reversal."""
        norm_sq = self.x**2 + self.y**2 + self.z**2 + self.w**2
        if norm_sq == 0:
            return Quaternion.identity()
        return Quaternion(
            -self.x / norm_sq,
            -self.y / norm_sq,
            -self.z / norm_sq,
            self.w / norm_sq
        )
    
    def rotate_vector(self, v: Vector3) -> Vector3:
        """
        Rotate a vector by this quaternion.
        Formula: q * v * q^-1
        """
        # Simplified quaternion-vector rotation
        qv = Vector3(self.x, self.y, self.z)
        uv = Vector3(
            qv.y * v.z - qv.z * v.y,
            qv.z * v.x - qv.x * v.z,
            qv.x * v.y - qv.y * v.x
        )
        uuv = Vector3(
            qv.y * uv.z - qv.z * uv.y,
            qv.z * uv.x - qv.x * uv.z,
            qv.x * uv.y - qv.y * uv.x
        )
        return v + (uv * self.w + uuv) * 2


@dataclass
class AnchorPoint:
    """
    QR-code anchor for coordinate alignment.
    
    Physical markers placed at hallway intersections
    that serve as alignment points for AR overlays.
    """
    anchor_id: str
    zone_id: str
    world_position: Vector3  # Position in Digital Twin world space
    floor_level: int = 0
    description: str = ""


@dataclass
class ZoneDefinition:
    """
    Physical zone (room/hallway) definition in Digital Twin.
    
    Privacy Note: Contains only zone metadata, not person data.
    """
    zone_id: str
    name: str
    position: Vector3  # Center point of zone
    size: Vector3      # Width, height, depth (bounding box)
    floor_level: int = 0
    zone_type: str = "room"  # room, hallway, stairwell, outdoor
    parent_zone: Optional[str] = None
    anchor_offsets: Dict[str, Vector3] = field(default_factory=dict)


class DigitalTwinManager:
    """
    Manages the Digital Twin map of the campus.
    
    Loads zone definitions and anchor points for spatial mapping.
    This is the server-side component; the AR client caches
    a subset based on current floor.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Digital Twin manager.
        
        Args:
            config_path: Path to Digital Twin JSON configuration
        """
        self.zones: Dict[str, ZoneDefinition] = {}
        self.anchors: Dict[str, AnchorPoint] = {}
        self._floor_index: Dict[int, List[str]] = {}  # floor -> zone_ids
        
        if config_path:
            self.load_from_file(config_path)
        else:
            self._load_default_campus()
    
    def _load_default_campus(self):
        """Load a default test campus layout."""
        # Sample campus layout for demonstration
        sample_zones = [
            ZoneDefinition(
                zone_id="NW_HALL_01",
                name="Northwest Hallway 1",
                position=Vector3(0.0, 0.0, 0.0),
                size=Vector3(30.0, 3.0, 5.0),
                floor_level=0,
                zone_type="hallway"
            ),
            ZoneDefinition(
                zone_id="NW_HALL_04",
                name="Northwest Hallway 4",
                position=Vector3(12.5, 0.0, 10.0),
                size=Vector3(20.0, 3.0, 5.0),
                floor_level=0,
                zone_type="hallway"
            ),
            ZoneDefinition(
                zone_id="ROOM_101",
                name="Classroom 101",
                position=Vector3(-10.0, 0.0, 5.0),
                size=Vector3(10.0, 3.0, 8.0),
                floor_level=0,
                zone_type="room"
            ),
            ZoneDefinition(
                zone_id="ROOM_102",
                name="Classroom 102",
                position=Vector3(10.0, 0.0, 5.0),
                size=Vector3(10.0, 3.0, 8.0),
                floor_level=0,
                zone_type="room"
            ),
            ZoneDefinition(
                zone_id="STAIRWELL_N3",
                name="North Stairwell 3",
                position=Vector3(25.0, 0.0, -5.0),
                size=Vector3(4.0, 10.0, 4.0),
                floor_level=0,
                zone_type="stairwell"
            ),
            # Floor 1
            ZoneDefinition(
                zone_id="ROOM_201",
                name="Classroom 201",
                position=Vector3(-10.0, 3.0, 5.0),
                size=Vector3(10.0, 3.0, 8.0),
                floor_level=1,
                zone_type="room"
            ),
        ]
        
        sample_anchors = [
            AnchorPoint(
                anchor_id="QR_MAIN_ENTRANCE",
                zone_id="NW_HALL_01",
                world_position=Vector3(0.0, 1.5, 0.0),
                floor_level=0,
                description="Main entrance QR marker"
            ),
            AnchorPoint(
                anchor_id="QR_STAIRWELL_N",
                zone_id="STAIRWELL_N3",
                world_position=Vector3(25.0, 1.5, -5.0),
                floor_level=0,
                description="North stairwell QR marker"
            ),
        ]
        
        for zone in sample_zones:
            self.add_zone(zone)
        for anchor in sample_anchors:
            self.add_anchor(anchor)
        
        logger.info(f"📍 Loaded default campus: {len(self.zones)} zones, {len(self.anchors)} anchors")
    
    def load_from_file(self, path: str):
        """Load Digital Twin configuration from JSON file."""
        config_path = Path(path)
        if not config_path.exists():
            logger.warning(f"⚠️  Config not found: {path}. Using default.")
            self._load_default_campus()
            return
        
        try:
            with open(config_path) as f:
                data = json.load(f)
            
            for zone_data in data.get("zones", []):
                zone = ZoneDefinition(
                    zone_id=zone_data["zone_id"],
                    name=zone_data.get("name", zone_data["zone_id"]),
                    position=Vector3.from_dict(zone_data.get("position", {})),
                    size=Vector3.from_dict(zone_data.get("size", {})),
                    floor_level=zone_data.get("floor_level", 0),
                    zone_type=zone_data.get("zone_type", "room")
                )
                self.add_zone(zone)
            
            for anchor_data in data.get("anchors", []):
                anchor = AnchorPoint(
                    anchor_id=anchor_data["anchor_id"],
                    zone_id=anchor_data.get("zone_id", ""),
                    world_position=Vector3.from_dict(anchor_data.get("position", {})),
                    floor_level=anchor_data.get("floor_level", 0),
                    description=anchor_data.get("description", "")
                )
                self.add_anchor(anchor)
            
            logger.info(f"📍 Loaded Digital Twin: {len(self.zones)} zones, {len(self.anchors)} anchors")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Digital Twin: {e}")
            self._load_default_campus()
    
    def add_zone(self, zone: ZoneDefinition):
        """Add a zone to the Digital Twin."""
        self.zones[zone.zone_id] = zone
        
        # Index by floor
        if zone.floor_level not in self._floor_index:
            self._floor_index[zone.floor_level] = []
        self._floor_index[zone.floor_level].append(zone.zone_id)
    
    def add_anchor(self, anchor: AnchorPoint):
        """Add an anchor point."""
        self.anchors[anchor.anchor_id] = anchor
    
    def get_zone(self, zone_id: str) -> Optional[ZoneDefinition]:
        """Get zone by ID."""
        return self.zones.get(zone_id)
    
    def get_zones_on_floor(self, floor_level: int) -> List[ZoneDefinition]:
        """Get all zones on a specific floor."""
        zone_ids = self._floor_index.get(floor_level, [])
        return [self.zones[zid] for zid in zone_ids]
    
    def get_nearest_anchor(self, position: Vector3, floor_level: int) -> Optional[AnchorPoint]:
        """Find the nearest anchor to a given position."""
        floor_anchors = [a for a in self.anchors.values() if a.floor_level == floor_level]
        if not floor_anchors:
            return None
        
        return min(floor_anchors, key=lambda a: a.world_position.distance_to(position))
    
    def export_to_json(self) -> str:
        """Export Digital Twin to JSON string."""
        data = {
            "zones": [
                {
                    "zone_id": z.zone_id,
                    "name": z.name,
                    "position": z.position.to_dict(),
                    "size": z.size.to_dict(),
                    "floor_level": z.floor_level,
                    "zone_type": z.zone_type
                }
                for z in self.zones.values()
            ],
            "anchors": [
                {
                    "anchor_id": a.anchor_id,
                    "zone_id": a.zone_id,
                    "position": a.world_position.to_dict(),
                    "floor_level": a.floor_level,
                    "description": a.description
                }
                for a in self.anchors.values()
            ]
        }
        return json.dumps(data, indent=2)


class CoordinateMapper:
    """
    Maps zone IDs to AR-space coordinates.
    
    Performs the transformation from Digital Twin world space
    to the AR client's local coordinate space based on
    the current anchor alignment.
    
    Formula: P_render = P_camera + (Q_cam * Q_inverse_anchor) * (P_target - P_anchor)
    """
    
    def __init__(self, digital_twin: Optional[DigitalTwinManager] = None):
        """
        Initialize coordinate mapper.
        
        Args:
            digital_twin: Digital Twin manager instance
        """
        self.digital_twin = digital_twin or DigitalTwinManager()
        
        # Current AR client state
        self._camera_position = Vector3(0, 0, 0)
        self._camera_rotation = Quaternion.identity()
        self._current_anchor: Optional[AnchorPoint] = None
        self._anchor_rotation = Quaternion.identity()
        
        # Calibration state
        self._calibrated = False
        self._last_calibration_time = 0.0
    
    def calibrate_to_anchor(
        self,
        anchor_id: str,
        camera_position: Vector3,
        camera_rotation: Quaternion,
        detected_anchor_rotation: Quaternion
    ) -> bool:
        """
        Calibrate coordinate system using detected QR anchor.
        
        This establishes the transformation bridge between
        the Digital Twin world space and AR local space.
        
        Args:
            anchor_id: ID of the detected QR anchor
            camera_position: Current camera position in AR space
            camera_rotation: Current camera rotation
            detected_anchor_rotation: Rotation of anchor as seen by camera
        
        Returns:
            True if calibration successful
        """
        anchor = self.digital_twin.anchors.get(anchor_id)
        if not anchor:
            logger.warning(f"⚠️  Unknown anchor: {anchor_id}")
            return False
        
        self._current_anchor = anchor
        self._camera_position = camera_position
        self._camera_rotation = camera_rotation
        self._anchor_rotation = detected_anchor_rotation
        self._calibrated = True
        
        import time
        self._last_calibration_time = time.time()
        
        logger.info(f"✅ Calibrated to anchor: {anchor_id} ({anchor.description})")
        return True
    
    def update_camera_pose(self, position: Vector3, rotation: Quaternion):
        """Update current camera position and rotation."""
        self._camera_position = position
        self._camera_rotation = rotation
    
    def zone_to_ar_position(self, zone_id: str) -> Optional[Vector3]:
        """
        Convert zone ID to AR-renderable position.
        
        Args:
            zone_id: Zone identifier from MQTT event
        
        Returns:
            Position in AR local space, or None if zone unknown
        """
        zone = self.digital_twin.get_zone(zone_id)
        if not zone:
            logger.warning(f"⚠️  Unknown zone: {zone_id}")
            return None
        
        if not self._calibrated or not self._current_anchor:
            # Return world position if not calibrated
            logger.debug(f"⚠️  Not calibrated, returning world position for {zone_id}")
            return zone.position
        
        # Calculate offset from anchor to target zone
        offset = zone.position - self._current_anchor.world_position
        
        # Apply rotation transformation
        inverse_anchor_rotation = self._anchor_rotation.inverse()
        combined_rotation = Quaternion(
            self._camera_rotation.x,
            self._camera_rotation.y,
            self._camera_rotation.z,
            self._camera_rotation.w
        )
        # Simplified: just apply inverse anchor to offset
        rotated_offset = inverse_anchor_rotation.rotate_vector(offset)
        
        # Add to camera position
        ar_position = self._camera_position + rotated_offset
        
        return ar_position
    
    def offset_to_ar_position(self, zone_id: str, offset: Vector3) -> Optional[Vector3]:
        """
        Convert zone ID + offset to AR position.
        
        Used when MQTT payload includes a specific vector_offset
        within the zone.
        """
        zone_pos = self.zone_to_ar_position(zone_id)
        if zone_pos is None:
            return None
        return zone_pos + offset
    
    def get_distance_to_zone(self, zone_id: str) -> Optional[float]:
        """Get distance from camera to zone center."""
        ar_pos = self.zone_to_ar_position(zone_id)
        if ar_pos is None:
            return None
        return ar_pos.distance_to(Vector3(0, 0, 0))  # Distance from origin in AR space
    
    def is_calibrated(self) -> bool:
        """Check if coordinate mapper is calibrated."""
        return self._calibrated
    
    def get_calibration_age(self) -> float:
        """Get age of current calibration in seconds."""
        if not self._calibrated:
            return float('inf')
        import time
        return time.time() - self._last_calibration_time
    
    def get_zones_in_view(
        self,
        fov_horizontal: float = 60.0,
        max_distance: float = 50.0
    ) -> List[Tuple[str, float]]:
        """
        Get zones within current camera view frustum.
        
        Args:
            fov_horizontal: Camera field of view in degrees
            max_distance: Maximum render distance in meters
        
        Returns:
            List of (zone_id, distance) tuples
        """
        visible_zones = []
        
        for zone_id, zone in self.digital_twin.zones.items():
            ar_pos = self.zone_to_ar_position(zone_id)
            if ar_pos is None:
                continue
            
            distance = ar_pos.distance_to(Vector3(0, 0, 0))
            if distance > max_distance:
                continue
            
            # Simplified frustum check (proper implementation would use dot product)
            # For now, include all zones within distance
            visible_zones.append((zone_id, distance))
        
        # Sort by distance
        visible_zones.sort(key=lambda x: x[1])
        return visible_zones


if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.DEBUG)
    
    print("📍 Testing Coordinate Mapper")
    print("=" * 50)
    
    # Create Digital Twin
    twin = DigitalTwinManager()
    print(f"\n📋 Loaded zones: {list(twin.zones.keys())}")
    print(f"📌 Loaded anchors: {list(twin.anchors.keys())}")
    
    # Create mapper
    mapper = CoordinateMapper(twin)
    
    # Simulate calibration
    mapper.calibrate_to_anchor(
        anchor_id="QR_MAIN_ENTRANCE",
        camera_position=Vector3(1.0, 1.5, 2.0),
        camera_rotation=Quaternion.identity(),
        detected_anchor_rotation=Quaternion.identity()
    )
    
    # Test zone mapping
    for zone_id in ["ROOM_101", "STAIRWELL_N3", "NW_HALL_04"]:
        ar_pos = mapper.zone_to_ar_position(zone_id)
        distance = mapper.get_distance_to_zone(zone_id)
        print(f"\n  {zone_id}:")
        print(f"    AR Position: ({ar_pos.x:.1f}, {ar_pos.y:.1f}, {ar_pos.z:.1f})")
        print(f"    Distance: {distance:.1f}m")
    
    # Test view frustum
    print("\n📷 Zones in view:")
    for zone_id, dist in mapper.get_zones_in_view():
        print(f"    {zone_id}: {dist:.1f}m")
    
    # Export Digital Twin
    print("\n📄 Digital Twin JSON sample:")
    print(twin.export_to_json()[:500] + "...")
