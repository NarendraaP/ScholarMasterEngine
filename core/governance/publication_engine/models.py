"""
ScholarMaster - Publication State & Governance Models
=====================================================
Defines authoritative data structures, Enums, and contracts for
the permanent Portfolio Publication-State Synchronization Architecture.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone


class PublicationStatus(str, Enum):
    """Authoritative lifecycle status of a research manuscript."""
    PLANNED = "PLANNED"
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED_IN_PRESS = "ACCEPTED_IN_PRESS"
    PUBLISHED = "PUBLISHED"


class CitationClassification(str, Enum):
    """Formal taxonomy of citation states evaluated against chronology, relevance, and necessity."""
    # Formal Invariant States
    CITATION_ELIGIBLE = "CITATION_ELIGIBLE"
    CITATION_NOT_YET_ELIGIBLE = "CITATION_NOT_YET_ELIGIBLE"
    CITATION_CHRONOLOGICALLY_INVALID = "CITATION_CHRONOLOGICALLY_INVALID"
    CITATION_SCIENTIFICALLY_RELEVANT = "CITATION_SCIENTIFICALLY_RELEVANT"
    CITATION_SCIENTIFICALLY_IRRELEVANT = "CITATION_SCIENTIFICALLY_IRRELEVANT"
    CITATION_PRESENT = "CITATION_PRESENT"
    CITATION_REQUIRED = "CITATION_REQUIRED"
    CITATION_OPTIONAL = "CITATION_OPTIONAL"
    CITATION_SYNCHRONIZATION_REQUIRED = "CITATION_SYNCHRONIZATION_REQUIRED"
    CITATION_REQUIRES_HUMAN_REVIEW = "CITATION_REQUIRES_HUMAN_REVIEW"
    
    # Backward-Compatible Taxa
    VALID_PUBLISHED_CITATION = "VALID_PUBLISHED_CITATION"
    FUTURE_WORK_REFERENCE = "FUTURE_WORK_REFERENCE"
    INTERNAL_RESEARCH_DEPENDENCY = "INTERNAL_RESEARCH_DEPENDENCY"
    INVALID_FORWARD_CITATION = "INVALID_FORWARD_CITATION"
    REQUIRES_REPLACEMENT = "REQUIRES_REPLACEMENT"


class ChangeType(str, Enum):
    """Classification of changes applied during synchronization."""
    METADATA_UPDATE = "METADATA_UPDATE"
    BIBLIOGRAPHIC_UPDATE = "BIBLIOGRAPHIC_UPDATE"
    CITATION_UPDATE = "CITATION_UPDATE"
    CHRONOLOGY_CORRECTION = "CHRONOLOGY_CORRECTION"
    SCIENTIFIC_CORRECTION = "SCIENTIFIC_CORRECTION"
    REFERENCE_SUPPORT = "REFERENCE_SUPPORT"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


@dataclass
class PaperMetadata:
    """Authoritative metadata record for a single paper in the portfolio."""
    paper_id: str
    canonical_manuscript_path: str
    title: str
    authors: List[str]
    research_plan_position: int
    publication_status: PublicationStatus
    submission_status: str
    venue: str
    doi: Optional[str] = None
    publication_date: Optional[str] = None  # Canonical effective publication date (YYYY-MM or YYYY-MM-DD)
    
    # Fine-Grained Publication Chronology Fields
    draft_date: Optional[str] = None
    submission_date: Optional[str] = None
    acceptance_date: Optional[str] = None
    online_publication_date: Optional[str] = None
    issue_publication_date: Optional[str] = None
    citation_eligible_date: Optional[str] = None
    citation_eligibility_basis: Optional[str] = None  # e.g. ACCEPTED_IN_PRESS, ONLINE_FIRST, VERSION_OF_RECORD, ISSUE_PUBLICATION
    
    # Bibliographic Details
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    official_url: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    official_bibliographic_citation: Optional[str] = None
    canonical_bibtex_key: str = ""
    repository_artifact_id: Optional[str] = None
    superseded_metadata: List[Dict[str, Any]] = field(default_factory=list)
    
    # Research & Contribution Governance Fields
    research_question: Optional[str] = None
    primary_contribution: Optional[str] = None
    secondary_contributions: List[str] = field(default_factory=list)
    evidence_type: Optional[str] = None  # MEASURED, PHYSICAL_HARDWARE, BENCHMARK, USER_STUDY, FORMAL
    known_boundaries: List[str] = field(default_factory=list)
    target_venue: Optional[str] = None
    related_papers: List[str] = field(default_factory=list)
    single_owner_domain: str = ""
    citation_eligible: bool = False
    last_synchronization_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata_provenance: Dict[str, str] = field(default_factory=dict)

    def is_strictly_citation_eligible(self) -> bool:
        """
        Hard Invariant: citation_eligible = TRUE only when:
        publication_status in {ACCEPTED_IN_PRESS, PUBLISHED} AND citation_eligible_date is known.
        """
        valid_status = self.publication_status in [PublicationStatus.ACCEPTED_IN_PRESS, PublicationStatus.PUBLISHED]
        has_date = bool(self.citation_eligible_date or self.publication_date)
        return valid_status and has_date

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['publication_status'] = self.publication_status.value
        data['citation_eligible'] = self.is_strictly_citation_eligible()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaperMetadata':
        data_copy = data.copy()
        if isinstance(data_copy.get('publication_status'), str):
            data_copy['publication_status'] = PublicationStatus(data_copy['publication_status'])
        return cls(**data_copy)


@dataclass
class PublicationEvent:
    """First-class system event emitted when a paper changes publication state."""
    event_id: str
    paper_id: str
    previous_status: PublicationStatus
    new_status: PublicationStatus
    doi: Optional[str] = None
    venue: Optional[str] = None
    publication_date: Optional[str] = None
    online_publication_date: Optional[str] = None
    issue_publication_date: Optional[str] = None
    citation_eligible_date: Optional[str] = None
    citation_eligibility_basis: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    official_bibliographic_metadata: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: str = "RESEARCHER_AUTHORITATIVE_INPUT"
    metadata_delta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['previous_status'] = self.previous_status.value
        data['new_status'] = self.new_status.value
        return data


@dataclass
class CitationDecision:
    """
    Formal 3-way evaluation for any (Citing Paper -> Cited Paper) relationship:
    1. Chronological / Legal Eligibility
    2. Scientific Relevance
    3. Citation Necessity / Opportunity
    """
    citing_paper: str
    cited_paper: str
    chronologically_eligible: bool
    chronology_reason: str
    scientifically_relevant: bool
    relevance_reason: str
    citation_necessary: bool
    citation_present: bool
    opportunity_reason: str
    recommended_action: str  # NO_ACTION, AUTOMATIC_BIBLIOGRAPHIC_SYNC, HUMAN_REVIEW_REQUIRED, REPLACE_INVALID_CITATION
    automation_allowed: bool
    human_review_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChangeLogEntry:
    """Detailed record of a single atomic change applied or proposed."""
    paper_id: str
    file_path: str
    section_or_line: str
    old_value: Any
    new_value: Any
    reason: str
    trigger_event_id: str
    governance_rule: str
    change_type: ChangeType
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['change_type'] = self.change_type.value
        return data


@dataclass
class ImpactAnalysisResult:
    """Deterministic machine-readable outcome of a publication event impact analysis."""
    trigger_event: PublicationEvent
    decisions: Dict[str, CitationDecision]
    newly_citation_eligible_papers: List[str]
    existing_references_requiring_sync: List[str]
    future_paper_references_converted: List[Dict[str, Any]]
    references_requiring_replacement: List[Dict[str, Any]]
    chronology_violations_detected: List[Dict[str, Any]]
    scientific_content_changes_required: List[Dict[str, Any]]
    human_review_required: List[Dict[str, Any]]
    unaffected_manuscripts: List[str]
    explanation_matrix: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_event": self.trigger_event.to_dict(),
            "decisions": {k: v.to_dict() for k, v in self.decisions.items()},
            "newly_citation_eligible_papers": self.newly_citation_eligible_papers,
            "existing_references_requiring_sync": self.existing_references_requiring_sync,
            "future_paper_references_converted": self.future_paper_references_converted,
            "references_requiring_replacement": self.references_requiring_replacement,
            "chronology_violations_detected": self.chronology_violations_detected,
            "scientific_content_changes_required": self.scientific_content_changes_required,
            "human_review_required": self.human_review_required,
            "unaffected_manuscripts": self.unaffected_manuscripts,
            "explanation_matrix": self.explanation_matrix
        }
