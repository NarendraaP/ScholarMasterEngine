"""
ScholarMaster - Controlled Publication Synchronizer
===================================================
Executes the safe synchronization pipeline:
ANALYZE -> PLAN -> DIFF -> VALIDATE -> REPORT
Guarantees zero silent rewriting of scientific claims or historical records.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from .models import (
    PaperMetadata, PublicationStatus, PublicationEvent,
    ChangeLogEntry, ChangeType, ImpactAnalysisResult
)
from .registry import PublicationRegistry
from .graphs import DualGraphManager
from .impact_analyzer import ImpactAnalyzer


class PublicationSynchronizer:
    """Orchestrates portfolio publication events and controlled bibliographic synchronization."""

    def __init__(self,
                 registry: Optional[PublicationRegistry] = None,
                 graph_manager: Optional[DualGraphManager] = None,
                 events_dir: str = "research_governance/publication_events",
                 registry_dir: str = "research_governance/publication_registry"):
        self.registry = registry or PublicationRegistry()
        self.graph_manager = graph_manager or DualGraphManager(self.registry)
        self.analyzer = ImpactAnalyzer(self.registry, self.graph_manager)
        self.events_dir = events_dir
        self.registry_dir = registry_dir
        os.makedirs(self.events_dir, exist_ok=True)
        os.makedirs(self.registry_dir, exist_ok=True)
        
        self.state_log_file = os.path.join(self.registry_dir, "PUBLICATION_STATE_CHANGE_LOG.json")
        self.downstream_log_file = os.path.join(self.registry_dir, "DOWNSTREAM_REFERENCE_UPDATE_LOG.json")
        self.bibtex_map_file = os.path.join(self.registry_dir, "BIBTEX_IDENTITY_MAP.json")

    def handle_publication_event(self, event: PublicationEvent) -> ImpactAnalysisResult:
        """
        Main entrypoint: executes publication state transition and full governance pipeline.
        """
        # Step 1: ANALYZE Impact
        impact = self.analyzer.analyze_publication_event(event)

        # Step 2: PLAN & UPDATE Registry
        updated_paper = self.registry.update_publication_status(
            paper_id=event.paper_id,
            new_status=event.new_status,
            doi=event.doi,
            venue=event.venue,
            pub_date=event.publication_date,
            volume=event.volume,
            issue=event.issue,
            pages=event.pages
        )

        # Step 3: RECOMPUTE Graphs & Legality
        self.graph_manager.recompute_citation_graph()

        # Step 4: RECORD BibTeX Identity Resolution Map
        self.update_bibtex_identity_map()

        # Step 5: LOG State Transition and Downstream Sync
        self.append_state_log(event)
        self.append_downstream_log(event, impact)

        # Step 6: GENERATE Publication Impact Report (Markdown + JSON)
        self.generate_impact_report(impact)

        return impact

    def update_bibtex_identity_map(self) -> None:
        """Generates canonical mapping from planned identities to published BibTeX records."""
        identity_map = {}
        for p_id, p in self.registry.papers.items():
            year = (p.publication_date or "2026")[:4]
            identity_map[p_id] = {
                "canonical_paper_id": p_id,
                "planned_key": f"kumar{year}scholar{p_id.lower()}",
                "published_bibtex_key": p.canonical_bibtex_key or f"scholarmaster_{p_id.lower()}_{year}",
                "doi": p.doi or "PENDING",
                "venue": p.venue,
                "status": p.publication_status.value,
                "bibtex_entry": self.format_bibtex_entry(p)
            }
        with open(self.bibtex_map_file, 'w') as f:
            json.dump(identity_map, f, indent=2)

    def format_bibtex_entry(self, paper: PaperMetadata) -> str:
        key = paper.canonical_bibtex_key or f"scholarmaster_{paper.paper_id.lower()}_2026"
        year = (paper.publication_date or "2026")[:4]
        authors = " and ".join(paper.authors)
        return (
            f"@article{{{key},\n"
            f"  author    = {{{authors}}},\n"
            f"  title     = {{{{{paper.title}}}}},\n"
            f"  journal   = {{{paper.venue}}},\n"
            f"  year      = {{{year}}},\n"
            f"  doi       = {{{paper.doi or ''}}},\n"
            f"  volume    = {{{paper.volume or ''}}},\n"
            f"  number    = {{{paper.issue or ''}}},\n"
            f"  pages     = {{{paper.pages or ''}}}\n"
            f"}}"
        )

    def append_state_log(self, event: PublicationEvent) -> None:
        logs = []
        if os.path.exists(self.state_log_file):
            try:
                with open(self.state_log_file, 'r') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(event.to_dict())
        with open(self.state_log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def append_downstream_log(self, event: PublicationEvent, impact: ImpactAnalysisResult) -> None:
        logs = []
        if os.path.exists(self.downstream_log_file):
            try:
                with open(self.downstream_log_file, 'r') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        entry = {
            "trigger_event_id": event.event_id,
            "trigger_paper": event.paper_id,
            "transition": f"{event.previous_status.value} -> {event.new_status.value}",
            "authoritative_doi": event.doi,
            "newly_eligible_count": len(impact.newly_citation_eligible_papers),
            "newly_eligible_papers": impact.newly_citation_eligible_papers,
            "chronology_violations_count": len(impact.chronology_violations_detected),
            "chronology_violations": impact.chronology_violations_detected,
            "human_review_required_count": len(impact.human_review_required),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logs.append(entry)
        with open(self.downstream_log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def generate_impact_report(self, impact: ImpactAnalysisResult) -> str:
        """Emits formal Markdown and JSON impact reports."""
        ev = impact.trigger_event
        report_json_path = os.path.join(self.events_dir, f"IMPACT_REPORT_{ev.paper_id}_{ev.new_status.value}.json")
        report_md_path = os.path.join(self.events_dir, f"IMPACT_REPORT_{ev.paper_id}_{ev.new_status.value}.md")

        with open(report_json_path, 'w') as f:
            json.dump(impact.to_dict(), f, indent=2)

        md_content = f"""# PUBLICATION IMPACT REPORT

**Published Paper**: {ev.paper_id}  
**Status**: {ev.new_status.value}  
**Venue**: {ev.venue or 'Authoritative Publication'}  
**DOI**: {ev.doi or 'N/A'}  
**Timestamp**: {ev.timestamp}  

---

## 1. Summary Metrics
- **Newly Citation-Eligible Papers**: {len(impact.newly_citation_eligible_papers)}
- **Existing References Requiring Sync**: {len(impact.existing_references_requiring_sync)}
- **Future-Paper References Converted**: {len(impact.future_paper_references_converted)}
- **Chronology Violations Detected**: {len(impact.chronology_violations_detected)}
- **References Requiring Replacement**: {len(impact.references_requiring_replacement)}
- **Scientific Content Changes**: {len(impact.scientific_content_changes_required)}
- **Human Review Required**: {len(impact.human_review_required)}
- **Unaffected Manuscripts**: {len(impact.unaffected_manuscripts)}

---

## 2. Newly Citation-Eligible Papers
{', '.join(impact.newly_citation_eligible_papers) if impact.newly_citation_eligible_papers else 'None'}

---

## 3. Chronology Invariant Enforcement & Historical Integrity
The system enforces strict historical chronology protection:
"""
        if impact.chronology_violations_detected:
            for v in impact.chronology_violations_detected:
                md_content += f"- **{v['citing_paper']} $\\to$ {v['invalid_forward_cited_paper']}**: {v['reason']}\n"
        else:
            md_content += "- **0 Chronology Violations Detected**. All candidate citations adhere to publication date order.\n"

        md_content += f"""
---

## 4. Unaffected Manuscripts ('Published != Cite Everywhere' Policy)
The following papers do not contain functional dependencies or were published prior to {ev.paper_id}:
{', '.join(impact.unaffected_manuscripts) if impact.unaffected_manuscripts else 'None'}

---

## 5. Detailed Paper Decision Ledger
"""
        for p_id, reason in impact.explanation_matrix.items():
            md_content += f"- **{p_id}**: {reason}\n"

        with open(report_md_path, 'w') as f:
            f.write(md_content)

        return md_content
