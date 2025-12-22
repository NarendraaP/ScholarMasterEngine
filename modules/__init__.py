"""
Legacy Modules Compatibility Layer

This package provides backward compatibility with the old modules/ structure.
It re-exports clean architecture components with legacy names.

This allows existing code to work without modification while using
Clean Architecture under the hood.
"""
from di.legacy_adapters import (
    FaceRegistry,
    AttendanceManager,
    ContextEngine
)

# Import other legacy modules that we're keeping temporarily
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules_legacy'))

from modules_legacy.scheduler import AutoScheduler
from modules_legacy.auth import Authenticator, requires_role, check_role, validate_role
from modules_legacy.analytics import AnalyticsEngine
from modules_legacy.safety_rules import SafetyEngine
from modules_legacy.audio_sentinel import AudioSentinel
from modules_legacy.master_engine import ScholarMasterEngine

__all__ = [
    # Clean Architecture (via legacy adapters)
    'FaceRegistry',
    'AttendanceManager',
    'ContextEngine',
    
    # Still using legacy implementations
    'AutoScheduler',
    'Authenticator',
    'requires_role',
    'check_role',
    'validate_role',
    'AnalyticsEngine',
    'SafetyEngine',
    'AudioSentinel',
    'ScholarMasterEngine'
]
