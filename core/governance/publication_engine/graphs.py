"""
ScholarMaster - Dual Graph Governance
=====================================
Maintains strict separation between:
1. Research Plan Graph (conceptual, pipeline, and functional dependencies).
2. Actual Publication Citation Graph (chronological, legally citable scholarly references).
"""

import os
import json
from typing import Dict, List, Any, Tuple, Set, Optional
from .models import PaperMetadata, PublicationStatus, CitationClassification
from .registry import PublicationRegistry


class DualGraphManager:
    """Manages and validates both Research Plan Graph and Publication Citation Graph."""

    def __init__(self, registry: PublicationRegistry,
                 plan_graph_file: str = "research_governance/publication_registry/RESEARCH_PLAN_GRAPH.json",
                 citation_graph_file: str = "research_governance/publication_registry/ACTUAL_PUBLICATION_CITATION_GRAPH.json",
                 dep_graph_file: str = "research_governance/publication_registry/CITATION_DEPENDENCY_GRAPH.json",
                 citability_file: str = "research_governance/publication_registry/HISTORICAL_CITABILITY_LEDGER.json"):
        self.registry = registry
        self.plan_graph_file = plan_graph_file
        self.citation_graph_file = citation_graph_file
        self.dep_graph_file = dep_graph_file
        self.citability_file = citability_file
        self.research_plan_edges: List[Dict[str, str]] = []
        self.citation_edges: List[Dict[str, str]] = []
        self.initialize_graphs()

    def initialize_graphs(self) -> None:
        """Initializes both graphs from disk or establishes defaults."""
        if os.path.exists(self.plan_graph_file):
            try:
                with open(self.plan_graph_file, 'r') as f:
                    self.research_plan_edges = json.load(f).get("edges", [])
            except Exception:
                self.research_plan_edges = []
        
        if not self.research_plan_edges:
            self.build_default_plan_graph()

        self.recompute_citation_graph()

    def build_default_plan_graph(self) -> None:
        """Establishes canonical functional and architectural pipeline dependencies."""
        default_edges = [
            {"source": "P1", "target": "P2", "type": "DATAFLOW_DEPENDENCY", "desc": "Cascade Context Ingestion"},
            {"source": "P1", "target": "P3", "type": "FUNCTIONAL_DEPENDENCY", "desc": "Volatile Memory Buffer Confinement"},
            {"source": "P1", "target": "P4", "type": "FUNCTIONAL_DEPENDENCY", "desc": "Relational Predicate Ingestion"},
            {"source": "P1", "target": "P5", "type": "ARCHITECTURAL_DEPENDENCY", "desc": "MBEEE Edge Envelope Profiling"},
            {"source": "P5", "target": "P7", "type": "HARDWARE_DEPENDENCY", "desc": "Zero-Copy Ingestion to HNSW Index"},
            {"source": "P6", "target": "P2", "type": "SENSOR_DEPENDENCY", "desc": "NLOS Acoustic Prior Ingestion"},
            {"source": "P9", "target": "P10", "type": "CONTROL_DEPENDENCY", "desc": "Rate Governance to Acceleration Pipeline"},
            {"source": "P11", "target": "P12", "type": "SYSTEM_DEPENDENCY", "desc": "Immutable OS Base to Fault Containment"},
            {"source": "P13", "target": "P14", "type": "LEARNING_DEPENDENCY", "desc": "Local Active Drift to Hierarchical Aggregation"},
            {"source": "P15", "target": "P4", "type": "INTERFACE_DEPENDENCY", "desc": "AR HUD Spatial Anchoring to Timetable"},
            {"source": "P20", "target": "P1", "type": "REFERENCE_DEPENDENCY", "desc": "CFAS Synthesis to 4-Stratum Implementation"},
            {"source": "P22", "target": "P24", "type": "METHODOLOGICAL_DEPENDENCY", "desc": "Dirichlet Evidential Uncertainty to JSD Fusion"},
            {"source": "P23", "target": "P19", "type": "HARDWARE_DEPENDENCY", "desc": "Dynamic Precision Budgets to Thermal Throttling"},
            {"source": "P23", "target": "P24", "type": "METHODOLOGICAL_DEPENDENCY", "desc": "Precision Budgets to Cross-Modal Recovery"},
            {"source": "P23", "target": "P25", "type": "SYSTEM_DEPENDENCY", "desc": "Operating Envelopes to Multi-Tenant Orchestration"}
        ]
        self.research_plan_edges = default_edges
        self.save_plan_graph()

    def save_plan_graph(self) -> None:
        os.makedirs(os.path.dirname(self.plan_graph_file), exist_ok=True)
        data = {
            "graph_name": "ScholarMaster Research Plan Graph (Conceptual & Functional Architecture)",
            "description": "Models conceptual, methodological, and functional dataflow dependencies. A planned paper may depend on another planned paper.",
            "nodes": list(self.registry.papers.keys()),
            "edges": self.research_plan_edges
        }
        with open(self.plan_graph_file, 'w') as f:
            json.dump(data, f, indent=2)

    def recompute_citation_graph(self) -> None:
        """
        Recomputes Actual Publication Citation Graph enforcing:
        Citation legality: source.finalization_date >= target.publication_date AND target is citable.
        """
        self.citation_edges = []
        citability_matrix: Dict[str, Any] = {}

        papers = self.registry.papers
        for p_source_id, p_source in papers.items():
            t_source = p_source.publication_date or "9999-99-99"
            citability_matrix[p_source_id] = {
                "eligible_citations": [],
                "is_currently_citable": p_source.citation_eligible
            }

            for p_target_id, p_target in papers.items():
                if p_target_id == p_source_id:
                    continue
                t_target = p_target.publication_date or "9999-99-99"
                
                # Rule: cited work must have been published or accepted on or before citing work finalization date
                if t_target <= t_source and p_target.citation_eligible:
                    citability_matrix[p_source_id]["eligible_citations"].append(p_target_id)
                    self.citation_edges.append({
                        "source": p_source_id,
                        "target": p_target_id,
                        "type": "AUTHORITATIVE_SCHOLARLY_CITATION",
                        "status": "VALID_CHRONOLOGY"
                    })

        self.save_citation_graph(citability_matrix)

    def save_citation_graph(self, citability_matrix: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.citation_graph_file), exist_ok=True)
        citation_data = {
            "graph_name": "ScholarMaster Actual Publication Citation Graph (Temporal & Scholarly Order)",
            "description": "Represents valid scholarly citations where Target Publication Date <= Source Publication Date and Target is PUBLISHED or ACCEPTED_IN_PRESS.",
            "nodes": list(self.registry.papers.keys()),
            "edges": self.citation_edges
        }
        with open(self.citation_graph_file, 'w') as f:
            json.dump(citation_data, f, indent=2)

        dep_data = {
            "nodes": list(self.registry.papers.keys()),
            "edges": self.citation_edges,
            "inbound_citation_counts": {p: sum(1 for e in self.citation_edges if e["target"] == p) for p in self.registry.papers}
        }
        with open(self.dep_graph_file, 'w') as f:
            json.dump(dep_data, f, indent=2)

        citability_data = {
            "chronology_rule": "citation_date >= cited_publication_date AND cited_status in [PUBLISHED, ACCEPTED_IN_PRESS]",
            "matrix": citability_matrix
        }
        with open(self.citability_file, 'w') as f:
            json.dump(citability_data, f, indent=2)

    def classify_citation(self, citing_paper_id: str, cited_paper_id: str,
                          manuscript_draft_date: Optional[str] = None) -> CitationClassification:
        """Classifies a candidate or existing citation against chronology and publication states."""
        citing = self.registry.get_paper(citing_paper_id)
        cited = self.registry.get_paper(cited_paper_id)

        if not citing or not cited:
            return CitationClassification.REQUIRES_HUMAN_REVIEW

        t_citing = manuscript_draft_date or citing.publication_date or "9999-99-99"
        t_cited = cited.publication_date or "9999-99-99"

        if not cited.citation_eligible:
            # Check if this is an internal research plan dependency
            if any(e["source"] == citing_paper_id and e["target"] == cited_paper_id for e in self.research_plan_edges):
                return CitationClassification.INTERNAL_RESEARCH_DEPENDENCY
            return CitationClassification.INVALID_FORWARD_CITATION

        if t_cited > t_citing:
            return CitationClassification.INVALID_FORWARD_CITATION

        return CitationClassification.VALID_PUBLISHED_CITATION
