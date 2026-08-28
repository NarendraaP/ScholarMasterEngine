"""
ScholarMaster - Citation Synchronization Planner
=================================================
Dedicated planning engine implementing:
DISCOVER -> CLASSIFY -> PLAN -> DIFF -> VALIDATE -> REPORT

Independently answers:
1. Legal / Chronological Eligibility
2. Scientific Relevance (strictly without paper-number heuristics)
3. Citation Necessity & Physical Manuscript Inspection
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from .models import (
    PaperMetadata, PublicationStatus, PublicationEvent,
    CitationClassification, CitationDecision, ChangeType
)
from .registry import PublicationRegistry
from .graphs import DualGraphManager


class CitationSyncPlanner:
    """Plans controlled, safe bibliographic synchronizations and enforces human-review gates."""

    def __init__(self, registry: PublicationRegistry, graph_manager: DualGraphManager,
                 papers_dir: str = "docs/papers"):
        self.registry = registry
        self.graph_manager = graph_manager
        self.papers_dir = papers_dir

    def inspect_manuscript_citations(self, paper_id: str) -> Dict[str, Any]:
        """
        Inspects actual .tex source file on disk to identify existing citations,
        bibitems, and provisional placeholder keys.
        """
        tex_path = os.path.join(self.papers_dir, f"paper{paper_id[1:]}_revised.tex") if paper_id.startswith("P") and paper_id[1:].isdigit() else ""
        if not os.path.exists(tex_path):
            paper = self.registry.get_paper(paper_id)
            if paper and os.path.exists(paper.canonical_manuscript_path):
                tex_path = paper.canonical_manuscript_path

        if not os.path.exists(tex_path):
            return {"exists": False, "tex_path": tex_path, "cites": set(), "bibitems": set(), "raw_text": ""}

        with open(tex_path, "r", errors="ignore") as f:
            raw_text = f.read()

        clean_text = re.sub(r"(?<!\\)%.*", "", raw_text)
        
        # Extract \cite{...}
        cites_raw = re.findall(r"\\cite\{([^}]+)\}", clean_text)
        cites = set()
        for c in cites_raw:
            for k in c.split(","):
                cites.add(k.strip())

        # Extract \bibitem{...}
        bibitems_raw = re.findall(r"\\bibitem(?:\[.*?\])?\{(.*?)\}", clean_text)
        bibitems = set(b.strip() for b in bibitems_raw)

        return {
            "exists": True,
            "tex_path": tex_path,
            "cites": cites,
            "bibitems": bibitems,
            "raw_text": clean_text
        }

    def evaluate_citation_pair(self, citing_id: str, cited_id: str,
                              trigger_event: Optional[PublicationEvent] = None) -> CitationDecision:
        """
        Independently answers:
        Question A: Legal / Chronological Eligibility
        Question B: Scientific Relevance (explicit graph & interfaces; NO paper-number rule)
        Question C: Citation Necessity & Presence in actual .tex file
        """
        citing = self.registry.get_paper(citing_id)
        cited = self.registry.get_paper(cited_id)

        if not citing or not cited:
            return CitationDecision(
                citing_paper=citing_id,
                cited_paper=cited_id,
                chronologically_eligible=False,
                chronology_reason="One or both papers are not registered.",
                scientifically_relevant=False,
                relevance_reason="Unknown paper registration.",
                citation_necessary=False,
                citation_present=False,
                opportunity_reason="Paper not found.",
                recommended_action="NO_ACTION",
                automation_allowed=False,
                human_review_required=True
            )

        # -------------------------------------------------------------
        # Question A: LEGAL / CHRONOLOGICAL ELIGIBILITY
        # -------------------------------------------------------------
        t_citing = citing.draft_date or citing.publication_date or "9999-99-99"
        
        # If trigger event is updating cited paper, use updated publication status & date
        cited_status = trigger_event.new_status if (trigger_event and trigger_event.paper_id == cited_id) else cited.publication_status
        t_cited = (trigger_event.citation_eligible_date or trigger_event.publication_date) if (trigger_event and trigger_event.paper_id == cited_id) else (cited.citation_eligible_date or cited.publication_date or "9999-99-99")

        is_citable_status = cited_status in [PublicationStatus.ACCEPTED_IN_PRESS, PublicationStatus.PUBLISHED]
        has_authoritative_date = bool(t_cited != "9999-99-99")
        
        if not is_citable_status or not has_authoritative_date:
            chronology_eligible = False
            chronology_reason = f"Cited paper {cited_id} is in status '{cited_status.value}' with date '{t_cited}'. Not yet officially citation-eligible."
        elif t_citing < t_cited:
            chronology_eligible = False
            chronology_reason = f"Historical integrity invariant: Citing paper {citing_id} (Date: {t_citing}) historically precedes cited paper {cited_id} (Date: {t_cited}). Forward citation is INVALID."
        else:
            chronology_eligible = True
            chronology_reason = f"Chronologically valid: {citing_id} (Date: {t_citing}) >= {cited_id} (Date: {t_cited}) and {cited_id} status is {cited_status.value}."

        # -------------------------------------------------------------
        # Question B: SCIENTIFIC RELEVANCE (No paper-number heuristics!)
        # -------------------------------------------------------------
        plan_edges = self.graph_manager.research_plan_edges
        is_connected_in_plan = any(
            (e["source"] == citing_id and e["target"] == cited_id) or
            (e["source"] == cited_id and e["target"] == citing_id)
            for e in plan_edges
        )
        is_in_related_papers = (cited_id in citing.related_papers) or (citing_id in cited.related_papers)
        
        if is_connected_in_plan or is_in_related_papers:
            scientifically_relevant = True
            relevance_reason = f"Explicit functional/methodological dependency or declared related paper interface exists between {citing_id} and {cited_id}."
        else:
            scientifically_relevant = False
            relevance_reason = f"No scientific interface or dependency exists between {citing_id} and {cited_id}. 'Published != Cite Everywhere' invariant enforced."

        # -------------------------------------------------------------
        # Question C: CITATION NECESSITY & PHYSICAL MANUSCRIPT INSPECTION
        # -------------------------------------------------------------
        inspection = self.inspect_manuscript_citations(citing_id)
        candidate_keys = {
            f"scholar{cited_id[1:]}", f"b{cited_id[1:]}", f"paper{cited_id[1:]}",
            f"scholarmaster_{cited_id.lower()}_2026", cited.canonical_bibtex_key
        }
        citation_present = bool(candidate_keys.intersection(inspection["cites"]) or candidate_keys.intersection(inspection["bibitems"]))

        if not chronology_eligible and citation_present:
            # Historical forward citation exists in the file -> Must be replaced or reviewed!
            citation_necessary = False
            opportunity_reason = f"Manuscript {citing_id} contains a citation to {cited_id}, but {cited_id} was unpublished at {citing_id} revision time. Historical forward citation detected."
            recommended_action = "REPLACE_INVALID_FORWARD_CITATION"
            automation_allowed = False
            human_review_required = True
        elif not chronology_eligible:
            citation_necessary = False
            opportunity_reason = "Cited paper is not legally/chronologically citable."
            recommended_action = "NO_ACTION"
            automation_allowed = True
            human_review_required = False
        elif not scientifically_relevant:
            citation_necessary = False
            opportunity_reason = f"Paper {cited_id} is citable, but has no scientific relevance to {citing_id}."
            recommended_action = "NO_ACTION"
            automation_allowed = True
            human_review_required = False
        elif citation_present:
            # Paper is eligible, relevant, and citation key is already present -> Safe Bibliographic Sync!
            citation_necessary = True
            opportunity_reason = f"Manuscript {citing_id} already references {cited_id}. Metadata update available."
            recommended_action = "AUTOMATIC_BIBLIOGRAPHIC_SYNC"
            automation_allowed = True
            human_review_required = False
        else:
            # Paper is eligible and relevant, but citation is NOT currently present in the text
            # Inserting new citation into scientific prose requires HUMAN REVIEW!
            citation_necessary = True
            opportunity_reason = f"Paper {cited_id} is relevant to {citing_id}, but not currently cited in text. Adding new in-text citation requires scientific context review."
            recommended_action = "HUMAN_REVIEW_REQUIRED"
            automation_allowed = False
            human_review_required = True

        return CitationDecision(
            citing_paper=citing_id,
            cited_paper=cited_id,
            chronologically_eligible=chronology_eligible,
            chronology_reason=chronology_reason,
            scientifically_relevant=scientifically_relevant,
            relevance_reason=relevance_reason,
            citation_necessary=citation_necessary,
            citation_present=citation_present,
            opportunity_reason=opportunity_reason,
            recommended_action=recommended_action,
            automation_allowed=automation_allowed,
            human_review_required=human_review_required
        )
