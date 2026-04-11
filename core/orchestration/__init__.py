"""
Core Orchestration Module
=========================
Provides unified event routing across all ScholarMaster papers.
"""

from core.orchestration.unified_orchestrator import (
    UnifiedOrchestrator,
    CrossPaperEvent,
    CrossPaperEventType,
    get_orchestrator,
    shutdown_orchestrator
)

__all__ = [
    'UnifiedOrchestrator',
    'CrossPaperEvent',
    'CrossPaperEventType',
    'get_orchestrator',
    'shutdown_orchestrator'
]
