"""
Core Integration Module
=======================
Provides integration adapters that bridge existing modules
to the unified event-driven architecture.
"""

from core.integration.adapters import (
    BlockchainARAdapter,
    EventBusFLAdapter,
    FLARAdapter,
    MainEventBridge,
    IntegrationManager,
    auto_integrate_system
)

from core.integration.complete_adapters import (
    PowerMonitorAdapter,
    STCSFAdapter,
    PrivacyLEDAdapter,
    FlashEnduranceAdapter,
    CompleteIntegrationManager,
    full_auto_integrate
)

__all__ = [
    # Original adapters
    'BlockchainARAdapter',
    'EventBusFLAdapter',
    'FLARAdapter',
    'MainEventBridge',
    'IntegrationManager',
    'auto_integrate_system',
    # Complete adapters
    'PowerMonitorAdapter',
    'STCSFAdapter',
    'PrivacyLEDAdapter',
    'FlashEnduranceAdapter',
    'CompleteIntegrationManager',
    'full_auto_integrate'
]
