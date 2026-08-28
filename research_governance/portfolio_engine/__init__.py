"""
ScholarMaster Research Portfolio Governance Engine
"""

from .citation_eligibility import CitationEligibilityEngine
from .publication_propagation import PublicationPropagationEngine
from .register_paper import PaperRegistrationEngine
from .portfolio_consistency import PortfolioConsistencyEngine
from .generator import MasterPlanGenerator

__all__ = [
    "CitationEligibilityEngine",
    "PublicationPropagationEngine",
    "PaperRegistrationEngine",
    "PortfolioConsistencyEngine",
    "MasterPlanGenerator"
]
