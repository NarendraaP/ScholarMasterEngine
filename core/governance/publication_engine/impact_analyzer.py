"""
ScholarMaster - Deterministic Impact Analyzer
==============================================
Calculates portfolio-wide consequences of a publication state event.
Integrates CitationSyncPlanner to evaluate Legal Eligibility, Scientific Relevance,
and Physical Manuscript Citation Necessity. Enforces 'Published != Cite Everywhere'.
"""

from typing import Dict, List, Any, Optional, Set
from .models import (
    PaperMetadata, PublicationStatus, PublicationEvent,
    CitationClassification, CitationDecision, ImpactAnalysisResult
)
from .registry import PublicationRegistry
from .graphs import DualGraphManager
from .citation_sync_planner import CitationSyncPlanner


class ImpactAnalyzer:
    """Computes deterministic machine-readable impact of publication events."""

    def __init__(self, registry: PublicationRegistry, graph_manager: DualGraphManager):
        self.registry = registry
        self.graph_manager = graph_manager
        self.planner = CitationSyncPlanner(self.registry, self.graph_manager)

    def analyze_publication_event(self, event: PublicationEvent) -> ImpactAnalysisResult:
        """
        Performs comprehensive, deterministic impact analysis when a paper transitions state.
        """
        pub_id = event.paper_id
        target_paper = self.registry.get_paper(pub_id)
        if not target_paper:
            raise ValueError(f"Paper {pub_id} not found in registry.")

        decisions: Dict[str, CitationDecision] = {}
        newly_eligible: List[str] = []
        existing_refs_to_sync: List[str] = []
        future_refs_converted: List[Dict[str, Any]] = []
        refs_requiring_replacement: List[Dict[str, Any]] = []
        chronology_violations: List[Dict[str, Any]] = []
        scientific_changes: List[Dict[str, Any]] = []
        human_review_required: List[Dict[str, Any]] = []
        unaffected: List[str] = []
        explanation_matrix: Dict[str, str] = {}

        for p_id in self.registry.papers:
            if p_id == pub_id:
                explanation_matrix[p_id] = f"Trigger paper {pub_id}: state transitioning from {event.previous_status.value} to {event.new_status.value}."
                continue

            decision = self.planner.evaluate_citation_pair(citing_id=p_id, cited_id=pub_id, trigger_event=event)
            decisions[p_id] = decision

            if not decision.chronologically_eligible:
                if decision.citation_present:
                    chronology_violations.append({
                        "citing_paper": p_id,
                        "invalid_forward_cited_paper": pub_id,
                        "classification": CitationClassification.INVALID_FORWARD_CITATION.value,
                        "reason": decision.chronology_reason
                    })
                    refs_requiring_replacement.append({
                        "paper": p_id,
                        "invalid_target": pub_id,
                        "remediation": "REPLACE_WITH_HISTORICAL_PREDECESSOR_OR_INTERNAL_REF"
                    })
                    human_review_required.append({
                        "paper": p_id,
                        "action": "REVIEW_HISTORICAL_FORWARD_REFERENCE",
                        "guidance": "Confirm reference is framed as future work or replace with contemporary literature."
                    })
                    explanation_matrix[p_id] = f"{p_id}: {decision.chronology_reason} [FLAGGED AS INVALID FORWARD CITATION]"
                else:
                    unaffected.append(p_id)
                    explanation_matrix[p_id] = f"{p_id}: Published prior to {pub_id}. No historical reference exists; remains unaffected."

            elif not decision.scientifically_relevant:
                unaffected.append(p_id)
                explanation_matrix[p_id] = f"{p_id}: Chronologically eligible, but no scientific interface exists. 'Published != Cite Everywhere' enforced."

            else:
                # Chronologically eligible AND scientifically relevant
                newly_eligible.append(p_id)
                if decision.recommended_action == "AUTOMATIC_BIBLIOGRAPHIC_SYNC":
                    existing_refs_to_sync.append(p_id)
                    future_refs_converted.append({
                        "citing_paper": p_id,
                        "cited_paper": pub_id,
                        "action": "CONVERT_PLANNED_TO_AUTHORITATIVE_BIBTEX",
                        "authoritative_doi": event.doi or target_paper.doi,
                        "canonical_bib_key": target_paper.canonical_bibtex_key
                    })
                    explanation_matrix[p_id] = f"{p_id}: Eligible and already references {pub_id}. Bibliographic metadata sync planned."
                elif decision.recommended_action == "HUMAN_REVIEW_REQUIRED":
                    human_review_required.append({
                        "paper": p_id,
                        "action": "PROPOSED_NEW_IN_TEXT_CITATION",
                        "guidance": f"Paper {pub_id} is now available and relevant to {p_id}. Human review required before inserting new citation into scientific prose."
                    })
                    explanation_matrix[p_id] = f"{p_id}: Eligible and relevant, but not currently cited in text. Human review required for text modification."
                else:
                    unaffected.append(p_id)
                    explanation_matrix[p_id] = f"{p_id}: {decision.opportunity_reason}"

        return ImpactAnalysisResult(
            trigger_event=event,
            decisions=decisions,
            newly_citation_eligible_papers=sorted(newly_eligible),
            existing_references_requiring_sync=sorted(existing_refs_to_sync),
            future_paper_references_converted=future_refs_converted,
            references_requiring_replacement=refs_requiring_replacement,
            chronology_violations_detected=chronology_violations,
            scientific_content_changes_required=scientific_changes,
            human_review_required=human_review_required,
            unaffected_manuscripts=sorted(unaffected),
            explanation_matrix=explanation_matrix
        )
