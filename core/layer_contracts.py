"""
Layer Boundary Contracts and Guards

ARCHITECTURE_CANONICAL.md COMPLIANCE
- Section 2: Canonical Runtime Layers with hard boundaries
- Data flows unidirectionally from L1 to L8
- Bypass of any layer is prohibited

This module provides:
1. Type-safe layer output contracts
2. Runtime boundary enforcement
3. Upstream access prevention decorators
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    TypeVar, Generic, Optional, List, Dict, Any, 
    Callable, Set, Union, Tuple
)
from enum import Enum, auto
from functools import wraps
import logging
import time
import numpy as np


logger = logging.getLogger(__name__)


# =============================================================================
# LAYER DEFINITIONS
# =============================================================================

class Layer(Enum):
    """Canonical runtime layers (ARCHITECTURE_CANONICAL.md Section 2)."""
    L1_PHYSICAL = 1
    L2_SENSOR = 2
    L3_EDGE = 3
    L4_INFERENCE = 4
    L5_GOVERNANCE = 5
    L6_HUMAN_INTERFACE = 6
    L7_EPHEMERAL = 7
    L8_FEDERATION = 8


# =============================================================================
# FORBIDDEN DATA PATTERNS
# =============================================================================

# Per ARCHITECTURE_CANONICAL.md: Forbidden outputs by layer
FORBIDDEN_OUTPUTS: Dict[Layer, Set[str]] = {
    Layer.L2_SENSOR: {"persistent_storage"},
    Layer.L3_EDGE: {"raw_frame", "waveform", "embedding"},
    Layer.L4_INFERENCE: {"identity_token", "biometric_vector", "face_embedding"},
    Layer.L5_GOVERNANCE: {"unapproved_output"},
    Layer.L6_HUMAN_INTERFACE: {"raw_imagery", "identifiable_data"},
    Layer.L7_EPHEMERAL: {"persistent_biometric"},
    Layer.L8_FEDERATION: {"raw_data", "embedding", "identifier"},
}

# Data types that must not transit upward
UPSTREAM_FORBIDDEN: Dict[Layer, Set[str]] = {
    Layer.L4_INFERENCE: {"raw_frame", "audio_buffer"},  # Cannot receive from L3
    Layer.L5_GOVERNANCE: {"raw_frame", "audio_buffer", "face_embedding", "biometric_vector", "embedding"},
    Layer.L6_HUMAN_INTERFACE: {"raw_frame", "audio_buffer", "embedding", "biometric_vector"},
    Layer.L7_EPHEMERAL: {"raw_frame", "audio_buffer", "embedding", "biometric_vector"},
    Layer.L8_FEDERATION: {"raw_frame", "audio_buffer", "embedding", "identity", "biometric_vector"},
}


# =============================================================================
# TYPE-SAFE LAYER OUTPUT CONTRACTS
# =============================================================================

@dataclass(frozen=True)
class L2Output:
    """
    L2 Sensor Acquisition output.
    
    Allowed: Raw frames, audio buffers (to L3 only)
    Forbidden: Persistent storage writes
    """
    frame_buffer: bytes = field(repr=False)
    audio_buffer: Optional[bytes] = field(default=None, repr=False)
    timestamp: float = field(default_factory=time.time)
    source_id: str = ""
    
    # Compile-time: This data MUST NOT escape L3 boundary
    _layer_bound: Layer = field(default=Layer.L3_EDGE, init=False)


@dataclass(frozen=True)
class L3Output:
    """
    L3 Edge Abstraction output (Irreversible Boundary).
    
    Allowed: Skeleton keypoints (34 dims max), audio features
    Forbidden: Raw frames, waveforms, embeddings
    """
    skeleton_keypoints: Tuple[float, ...] = ()  # Max 34 dimensions
    audio_features: Tuple[float, ...] = ()
    timestamp: float = field(default_factory=time.time)
    zone_id: str = ""
    
    _layer_source: Layer = field(default=Layer.L3_EDGE, init=False)
    
    def __post_init__(self):
        # Compile-time guard: skeleton must be ≤34 dimensions
        if len(self.skeleton_keypoints) > 34:
            raise ValueError(
                f"ARCHITECTURE_CANONICAL.md 2.3: Skeleton max 34 dims, "
                f"got {len(self.skeleton_keypoints)}"
            )


@dataclass(frozen=True)
class L4Output:
    """
    L4 Local Inference output.
    
    Allowed: Symbolic events (hand raise, attention, audio anomaly)
    Forbidden: Identity tokens, biometric vectors
    """
    event_type: str = ""
    severity: float = 0.0
    zone_id: str = ""
    timestamp: float = field(default_factory=time.time)
    is_anonymous: bool = True
    
    _layer_source: Layer = field(default=Layer.L4_INFERENCE, init=False)
    
    def __post_init__(self):
        if not self.is_anonymous:
            raise ValueError(
                "ARCHITECTURE_CANONICAL.md 2.4: L4 output must be anonymous"
            )


@dataclass(frozen=True)
class L5Output:
    """
    L5 Governance & Compliance Filter output.
    
    Allowed: Approved events with governance attestation
    Forbidden: Unapproved inference outputs
    """
    event_type: str = ""
    severity: float = 0.0
    zone_id: str = ""
    timestamp: float = field(default_factory=time.time)
    governance_approved: bool = False
    compliance_attestation: str = ""
    
    _layer_source: Layer = field(default=Layer.L5_GOVERNANCE, init=False)
    
    def __post_init__(self):
        if not self.governance_approved:
            raise ValueError(
                "ARCHITECTURE_CANONICAL.md 2.5: L5 output must be governance-approved"
            )


# =============================================================================
# RUNTIME BOUNDARY ENFORCER
# =============================================================================

class LayerBoundaryViolation(Exception):
    """Raised when layer boundary is violated."""
    pass


class LayerBoundaryEnforcer:
    """
    Runtime enforcement of layer boundaries.
    
    ARCHITECTURE_CANONICAL.md Section 2:
    - Data flows unidirectionally from L1 to L8
    - Bypass of any layer is prohibited
    - No module may access upstream raw data
    """
    
    def __init__(self):
        self._transition_log: List[Dict[str, Any]] = []
        self._violations: List[Dict[str, Any]] = []
    
    def validate_transition(
        self, 
        source_layer: Layer, 
        target_layer: Layer,
        data_types: Set[str]
    ) -> bool:
        """
        Validate layer transition is permitted.
        
        Returns:
            True if transition is valid
            
        Raises:
            LayerBoundaryViolation if transition violates boundaries
        """
        # Rule 1: Must flow forward (L1 → L8)
        if target_layer.value < source_layer.value:
            violation = {
                "type": "BACKWARD_FLOW",
                "source": source_layer.name,
                "target": target_layer.name,
                "timestamp": time.time()
            }
            self._violations.append(violation)
            logger.error(
                f"BOUNDARY VIOLATION: Backward flow {source_layer.name} → {target_layer.name}"
            )
            raise LayerBoundaryViolation(
                f"ARCHITECTURE_CANONICAL.md: Backward flow prohibited "
                f"({source_layer.name} → {target_layer.name})"
            )
        
        # Rule 2: Must transit through adjacent layers (no bypass)
        if target_layer.value > source_layer.value + 1:
            # Exception: L5 → L7 and L5 → L8 are permitted per spec
            if not (source_layer == Layer.L5_GOVERNANCE and 
                    target_layer in {Layer.L7_EPHEMERAL, Layer.L8_FEDERATION}):
                violation = {
                    "type": "LAYER_BYPASS",
                    "source": source_layer.name,
                    "target": target_layer.name,
                    "timestamp": time.time()
                }
                self._violations.append(violation)
                logger.error(
                    f"BOUNDARY VIOLATION: Layer bypass {source_layer.name} → {target_layer.name}"
                )
                raise LayerBoundaryViolation(
                    f"ARCHITECTURE_CANONICAL.md: Layer bypass prohibited "
                    f"({source_layer.name} → {target_layer.name})"
                )
        
        # Rule 3: Check forbidden data types for target layer
        if target_layer in UPSTREAM_FORBIDDEN:
            forbidden = data_types & UPSTREAM_FORBIDDEN[target_layer]
            if forbidden:
                violation = {
                    "type": "FORBIDDEN_DATA",
                    "source": source_layer.name,
                    "target": target_layer.name,
                    "data_types": list(forbidden),
                    "timestamp": time.time()
                }
                self._violations.append(violation)
                logger.error(
                    f"BOUNDARY VIOLATION: Forbidden data {forbidden} in {target_layer.name}"
                )
                raise LayerBoundaryViolation(
                    f"ARCHITECTURE_CANONICAL.md: Forbidden data for {target_layer.name}: {forbidden}"
                )
        
        # Log valid transition
        self._transition_log.append({
            "source": source_layer.name,
            "target": target_layer.name,
            "data_types": list(data_types),
            "timestamp": time.time()
        })
        
        return True
    
    def check_output_constraints(
        self, 
        layer: Layer, 
        output_fields: Set[str]
    ) -> bool:
        """
        Check that layer output doesn't contain forbidden fields.
        
        Raises:
            LayerBoundaryViolation if output contains forbidden fields
        """
        if layer in FORBIDDEN_OUTPUTS:
            forbidden = output_fields & FORBIDDEN_OUTPUTS[layer]
            if forbidden:
                logger.error(
                    f"OUTPUT VIOLATION: {layer.name} contains forbidden: {forbidden}"
                )
                raise LayerBoundaryViolation(
                    f"ARCHITECTURE_CANONICAL.md: {layer.name} forbidden outputs: {forbidden}"
                )
        return True
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Return list of violations."""
        return self._violations.copy()
    
    def get_transition_log(self) -> List[Dict[str, Any]]:
        """Return transition log for audit."""
        return self._transition_log.copy()


# =============================================================================
# DECORATORS FOR LAYER BOUNDARY ENFORCEMENT
# =============================================================================

# Global enforcer instance
_enforcer = LayerBoundaryEnforcer()


def layer_guard(source_layer: Layer, target_layer: Layer):
    """
    Decorator to enforce layer boundary on function.
    
    Usage:
        @layer_guard(Layer.L3_EDGE, Layer.L4_INFERENCE)
        def process_skeleton(skeleton_data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Infer data types from args (simplified)
            data_types: Set[str] = set()
            
            for arg in args:
                if isinstance(arg, L2Output):
                    data_types.add("raw_frame")
                elif isinstance(arg, L3Output):
                    data_types.add("skeleton")
                elif isinstance(arg, L4Output):
                    data_types.add("symbolic_event")
                elif isinstance(arg, np.ndarray):
                    # Heuristic: large arrays might be raw data
                    if arg.size > 1000:
                        data_types.add("potential_raw_data")
            
            # Validate transition
            _enforcer.validate_transition(source_layer, target_layer, data_types)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def forbid_upstream_data(*forbidden_types: str):
    """
    Decorator to prevent function from receiving forbidden data types.
    
    Usage:
        @forbid_upstream_data("raw_frame", "embedding")
        def process_inference(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in kwargs.items():
                if key in forbidden_types:
                    raise LayerBoundaryViolation(
                        f"Forbidden data '{key}' passed to {func.__name__}"
                    )
            
            # Check for L2Output in args (contains raw frame)
            for arg in args:
                if isinstance(arg, L2Output) and "raw_frame" in forbidden_types:
                    raise LayerBoundaryViolation(
                        f"L2Output (raw frame) forbidden in {func.__name__}"
                    )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_governance_approval(func: Callable) -> Callable:
    """
    Decorator requiring L5 governance approval before execution.
    
    Used for L6 human interface functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check for L5Output with governance_approved=True
        for arg in args:
            if isinstance(arg, L5Output) and arg.governance_approved:
                return func(*args, **kwargs)
        
        # Check kwargs
        for key, value in kwargs.items():
            if isinstance(value, L5Output) and value.governance_approved:
                return func(*args, **kwargs)
        
        raise LayerBoundaryViolation(
            f"ARCHITECTURE_CANONICAL.md 2.5: {func.__name__} requires governance approval"
        )
    
    return wrapper


# =============================================================================
# COMPILE-TIME TYPE GUARDS (Using Protocol for structural typing)
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
    
    @runtime_checkable
    class LayerOutput(Protocol):
        """Protocol for valid layer outputs."""
        _layer_source: Layer
        timestamp: float
    
    @runtime_checkable
    class AnonymousData(Protocol):
        """Protocol for anonymous (non-biometric) data."""
        is_anonymous: bool
    
    def assert_layer_output(data: Any, expected_layer: Layer) -> None:
        """
        Compile-time check that data is from expected layer.
        
        Raises TypeError if data is not from expected layer.
        """
        if not isinstance(data, LayerOutput):
            raise TypeError(f"Data must be LayerOutput, got {type(data)}")
        
        if data._layer_source != expected_layer:
            raise TypeError(
                f"Expected data from {expected_layer.name}, "
                f"got {data._layer_source.name}"
            )

except ImportError:
    # Python < 3.8 fallback
    LayerOutput = object
    AnonymousData = object
    
    def assert_layer_output(data: Any, expected_layer: Layer) -> None:
        pass


# =============================================================================
# INTEGRATION WITH CANONICAL LAYERS
# =============================================================================

def get_enforcer() -> LayerBoundaryEnforcer:
    """Get the global layer boundary enforcer."""
    return _enforcer


def reset_enforcer() -> None:
    """Reset the enforcer (for testing)."""
    global _enforcer
    _enforcer = LayerBoundaryEnforcer()
