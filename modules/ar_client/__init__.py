"""
Paper 15: AR Visualization Client
=================================
Presentation layer for spatially-anchored safety event visualization.

This module provides:
- MQTT event subscription for real-time alerts
- Coordinate mapping (VPS) for spatial anchoring
- Clutter reduction via proximity clustering
- Alert overlay management

Note: This is a reference implementation demonstrating feasibility.
The production AR client would be implemented in Unity/ARFoundation.
"""

from .mqtt_subscriber import ARMQTTSubscriber
from .coordinate_mapper import CoordinateMapper, DigitalTwinManager
from .clutter_manager import ClutterReductionManager, AlertCluster
from .alert_renderer import AlertOverlay, AlertRenderer

__all__ = [
    "ARMQTTSubscriber",
    "CoordinateMapper",
    "DigitalTwinManager",
    "ClutterReductionManager",
    "AlertCluster",
    "AlertOverlay",
    "AlertRenderer",
]
