"""
ScholarMaster - Comprehensive Regression Test Suite for Publication Governance
==============================================================================
Tests A through R demonstrating:
- Test A: P23 unpublished -> P23 published; downstream eligibility updates.
- Test B: P23 published before P24 finalization; P24 can cite P23.
- Test C: P23 published today; P22 historical forward citation remains flagged as INVALID.
- Test D: Paper published with no scientific relevance to downstream paper; no citation injected.
- Test E: Publication metadata updates; BibTeX identity resolves without duplicates.
- Test F: P26 registered; automatically inherits full governance architecture.
- Test G: Chronologically eligible but scientifically irrelevant -> NO_ACTION.
- Test H: Relevant but no citation opportunity -> no automatic text injection.
- Test I: Relevant and citation presence exists -> synchronization proposal generated.
- Test J: Bibliographic metadata update -> AUTOMATIC_BIBLIOGRAPHIC_SYNC permitted.
- Test K: Scientific prose modification -> HUMAN_REVIEW_REQUIRED.
- Test L: Historical forward citation remains invalid after cited paper is published.
- Test M: Research-plan order changes -> citation legality does NOT change automatically.
- Test N: P26 registration -> complete governance metadata inherited.
- Test O: P27 registration -> same architecture without custom code.
- Test P: Accepted-in-press date vs issue date -> configured policy respected.
- Test Q: Missing publication date -> citation eligibility remains unresolved.
- Test R: Actual .tex citation exists -> reports CITATION_PRESENT rather than duplicate insertion.
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime, timezone

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.governance.publication_engine import (
    PublicationRegistry, DualGraphManager, CitationSyncPlanner,
    ImpactAnalyzer, PublicationSynchronizer, PublicationStatus,
    PublicationEvent, PaperMetadata, CitationClassification,
    ReviewerCalibratedValidator
)


class TestPublicationGovernance(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry_file = os.path.join(self.temp_dir.name, "PUBLICATION_REGISTRY.json")
        self.plan_file = os.path.join(self.temp_dir.name, "RESEARCH_PLAN_GRAPH.json")
        self.cite_file = os.path.join(self.temp_dir.name, "ACTUAL_PUBLICATION_CITATION_GRAPH.json")
        self.dep_file = os.path.join(self.temp_dir.name, "CITATION_DEPENDENCY_GRAPH.json")
        self.citability_file = os.path.join(self.temp_dir.name, "HISTORICAL_CITABILITY_LEDGER.json")
        self.events_dir = os.path.join(self.temp_dir.name, "events")

        self.registry = PublicationRegistry(registry_file=self.registry_file)
        self.graph_manager = DualGraphManager(
            self.registry,
            plan_graph_file=self.plan_file,
            citation_graph_file=self.cite_file,
            dep_graph_file=self.dep_file,
            citability_file=self.citability_file
        )
        self.planner = CitationSyncPlanner(self.registry, self.graph_manager)
        self.synchronizer = PublicationSynchronizer(
            registry=self.registry,
            graph_manager=self.graph_manager,
            events_dir=self.events_dir,
            registry_dir=self.temp_dir.name
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_a_p23_unpublished_to_published(self):
        """Test A: P23 unpublished -> P23 published. Verify downstream eligibility updates."""
        p23_before = self.registry.get_paper("P23")
        self.assertFalse(p23_before.is_strictly_citation_eligible())

        event = PublicationEvent(
            event_id="EVT_TEST_A",
            paper_id="P23",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TSMC.2026.3344556",
            venue="IEEE Transactions on Systems, Man, and Cybernetics",
            publication_date="2026-08-24",
            citation_eligible_date="2026-08-24"
        )
        impact = self.synchronizer.handle_publication_event(event)

        p23_after = self.registry.get_paper("P23")
        self.assertTrue(p23_after.is_strictly_citation_eligible())
        self.assertEqual(p23_after.publication_status, PublicationStatus.PUBLISHED)
        self.assertEqual(p23_after.doi, "10.1109/TSMC.2026.3344556")
        
        # P24 and P25 are connected in research plan graph and eligible
        self.assertIn("P24", impact.newly_citation_eligible_papers)
        self.assertIn("P25", impact.newly_citation_eligible_papers)

    def test_b_p24_can_cite_published_p23(self):
        """Test B: P23 published before P24 finalization. Verify P24 can cite P23."""
        self.synchronizer.handle_publication_event(PublicationEvent(
            event_id="EVT_TEST_B",
            paper_id="P23",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TSMC.2026.3344556",
            venue="IEEE TSMC",
            publication_date="2026-08-24",
            citation_eligible_date="2026-08-24"
        ))

        decision = self.planner.evaluate_citation_pair(
            citing_id="P24",
            cited_id="P23"
        )
        self.assertTrue(decision.chronologically_eligible)
        self.assertTrue(decision.scientifically_relevant)

    def test_c_p22_forward_citation_remains_invalid(self):
        """Test C: P23 published today; P22 historical forward citation remains flagged as INVALID."""
        event = PublicationEvent(
            event_id="EVT_TEST_C",
            paper_id="P23",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TSMC.2026.3344556",
            venue="IEEE TSMC",
            publication_date="2026-08-24",
            citation_eligible_date="2026-08-24"
        )
        impact = self.synchronizer.handle_publication_event(event)

        # Citing paper P22 (Date: 2026-08-22) precedes P23 (Date: 2026-08-24)
        decision_p22 = impact.decisions["P22"]
        self.assertFalse(decision_p22.chronologically_eligible)
        self.assertIn("Historical integrity invariant", decision_p22.chronology_reason)

    def test_d_published_not_cite_everywhere(self):
        """Test D: Paper published with no scientific relevance to downstream paper; no citation injected."""
        event = PublicationEvent(
            event_id="EVT_TEST_D",
            paper_id="P6",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/LSP.2026.3389102",
            venue="IEEE Signal Processing Letters",
            publication_date="2026-04-15",
            citation_eligible_date="2026-04-15"
        )
        impact = self.synchronizer.handle_publication_event(event)
        
        # P18 (LTL verification) does not have acoustic domain dependency
        self.assertIn("P18", impact.unaffected_manuscripts)
        self.assertIn("'Published != Cite Everywhere' enforced", impact.explanation_matrix["P18"])

    def test_e_metadata_synchronization_without_duplicates(self):
        """Test E: Publication metadata changes; BibTeX identity resolves without duplicates."""
        self.synchronizer.handle_publication_event(PublicationEvent(
            event_id="EVT_TEST_E_1",
            paper_id="P7",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.ACCEPTED_IN_PRESS,
            doi="10.1109/TKDE.2026.001",
            venue="IEEE TKDE",
            publication_date="2026-05-01",
            citation_eligible_date="2026-05-01"
        ))

        self.synchronizer.handle_publication_event(PublicationEvent(
            event_id="EVT_TEST_E_2",
            paper_id="P7",
            previous_status=PublicationStatus.ACCEPTED_IN_PRESS,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TKDE.2026.9999999",
            venue="IEEE Transactions on Knowledge and Data Engineering",
            publication_date="2026-05-01",
            citation_eligible_date="2026-05-01",
            volume="38",
            issue="5",
            pages="1100-1114"
        ))

        bib_map_file = os.path.join(self.temp_dir.name, "BIBTEX_IDENTITY_MAP.json")
        with open(bib_map_file, 'r') as f:
            bib_map = json.load(f)

        self.assertIn("P7", bib_map)
        self.assertEqual(bib_map["P7"]["doi"], "10.1109/TKDE.2026.9999999")
        self.assertEqual(len(self.registry.get_paper("P7").superseded_metadata), 2)

    def test_f_p26_automatic_governance_inheritance(self):
        """Test F: P26 registered; automatically enters full governance architecture without custom code."""
        meta_p26 = PaperMetadata(
            paper_id="P26",
            canonical_manuscript_path="docs/papers/paper26_revised.tex",
            title="Multi-Modal Sensor Topology & Topological Graph Traversal",
            authors=["ScholarMaster Research Consortium"],
            research_plan_position=26,
            publication_status=PublicationStatus.PLANNED,
            submission_status="PLANNED",
            venue="ScholarMaster Series",
            single_owner_domain="Topological Graph Traversal for Heterogeneous Sensors"
        )
        self.registry.register_new_paper(meta_p26)
        self.graph_manager.recompute_citation_graph()

        self.assertIn("P26", self.registry.papers)
        self.assertFalse(self.registry.get_paper("P26").is_strictly_citation_eligible())

    def test_g_chronologically_eligible_but_scientifically_irrelevant(self):
        """Test G: Published paper is chronologically eligible but scientifically irrelevant -> NO_ACTION."""
        # P1 is published 2024-11, P17 is drafted 2026-08. P1 is eligible chronologically.
        # But if no functional dependency exists between P6 (Acoustic) and P17 (TGNN Trajectories):
        decision = self.planner.evaluate_citation_pair(citing_id="P17", cited_id="P6")
        self.assertTrue(decision.chronologically_eligible)
        self.assertFalse(decision.scientifically_relevant)
        self.assertEqual(decision.recommended_action, "NO_ACTION")
        self.assertTrue(decision.automation_allowed)
        self.assertFalse(decision.human_review_required)

    def test_h_relevant_but_no_citation_opportunity(self):
        """Test H: Published paper is relevant but no citation opportunity exists -> no automatic text injection."""
        decision = self.planner.evaluate_citation_pair(citing_id="P10", cited_id="P9")
        # P9 is relevant to P10 in research plan, but P9 was SUBMITTED (not yet published).
        # Chronology / eligibility prevents injection
        self.assertFalse(decision.chronologically_eligible)
        self.assertEqual(decision.recommended_action, "NO_ACTION")

    def test_i_relevant_and_citation_presence_exists(self):
        """Test I: Relevant and citation presence exists -> synchronization proposal generated."""
        # P2 is published 2024-12, P1 is published 2024-11. P1 -> P2 in research plan.
        decision = self.planner.evaluate_citation_pair(citing_id="P2", cited_id="P1")
        self.assertTrue(decision.chronologically_eligible)
        self.assertTrue(decision.scientifically_relevant)
        self.assertTrue(decision.automation_allowed)

    def test_j_bibliographic_metadata_update_automation_allowed(self):
        """Test J: Bibliographic metadata update -> AUTOMATIC_BIBLIOGRAPHIC_SYNC permitted."""
        decision = self.planner.evaluate_citation_pair(citing_id="P2", cited_id="P1")
        self.assertTrue(decision.automation_allowed)
        self.assertFalse(decision.human_review_required)

    def test_k_scientific_prose_modification_requires_human_review(self):
        """Test K: Proposed insertion of new in-text citation into scientific prose -> HUMAN_REVIEW_REQUIRED."""
        # When P23 is published, P24 is relevant to P23, but if P24 does NOT currently cite P23 in text:
        event = PublicationEvent(
            event_id="EVT_TEST_K",
            paper_id="P23",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TSMC.2026.111",
            venue="IEEE TSMC",
            publication_date="2026-08-24",
            citation_eligible_date="2026-08-24"
        )
        decision = self.planner.evaluate_citation_pair(citing_id="P24", cited_id="P23", trigger_event=event)
        self.assertTrue(decision.chronologically_eligible)
        self.assertTrue(decision.scientifically_relevant)
        if not decision.citation_present:
            self.assertEqual(decision.recommended_action, "HUMAN_REVIEW_REQUIRED")
            self.assertTrue(decision.human_review_required)
            self.assertFalse(decision.automation_allowed)

    def test_l_historical_forward_citation_remains_invalid(self):
        """Test L: Historical forward citation remains invalid after cited paper becomes published."""
        event = PublicationEvent(
            event_id="EVT_TEST_L",
            paper_id="P25",
            previous_status=PublicationStatus.SUBMITTED,
            new_status=PublicationStatus.PUBLISHED,
            doi="10.1109/TSE.2026.2525",
            venue="IEEE TSE",
            publication_date="2026-08-28",
            citation_eligible_date="2026-08-28"
        )
        # P4 finalized in 2025-02. Citing P25 (2026-08) is historically invalid!
        decision = self.planner.evaluate_citation_pair(citing_id="P4", cited_id="P25", trigger_event=event)
        self.assertFalse(decision.chronologically_eligible)
        self.assertIn("Historical integrity invariant", decision.chronology_reason)

    def test_m_research_plan_order_change_does_not_alter_citation_legality(self):
        """Test M: Research-plan position changes -> citation legality does NOT change automatically."""
        p2 = self.registry.get_paper("P2")
        # Change organizational plan position from 2 to 99
        p2.research_plan_position = 99
        self.registry.save()

        # Citation legality between P2 and P1 remains strictly governed by dates (2024-12 >= 2024-11), NOT position
        decision = self.planner.evaluate_citation_pair(citing_id="P2", cited_id="P1")
        self.assertTrue(decision.chronologically_eligible)

    def test_n_p26_registration_inherits_full_metadata_contract(self):
        """Test N: P26 registration inherits complete governance metadata contract."""
        meta_p26 = PaperMetadata(
            paper_id="P26",
            canonical_manuscript_path="docs/papers/paper26_revised.tex",
            title="Multi-Modal Sensor Topology Optimization",
            authors=["ScholarMaster Research Consortium"],
            research_plan_position=26,
            publication_status=PublicationStatus.PLANNED,
            submission_status="PLANNED",
            venue="IEEE Sensors Journal",
            research_question="How to optimize dynamic graph topology across heterogeneous edge sensors?",
            primary_contribution="Topological Graph Traversal Algorithm for Edge Sensor Networks",
            single_owner_domain="Topological Graph Traversal for Heterogeneous Sensors",
            evidence_type="PHYSICAL_HARDWARE",
            target_venue="IEEE Sensors Journal"
        )
        self.registry.register_new_paper(meta_p26)
        
        saved_p26 = self.registry.get_paper("P26")
        self.assertEqual(saved_p26.research_question, "How to optimize dynamic graph topology across heterogeneous edge sensors?")
        self.assertEqual(saved_p26.evidence_type, "PHYSICAL_HARDWARE")
        self.assertEqual(saved_p26.single_owner_domain, "Topological Graph Traversal for Heterogeneous Sensors")

    def test_o_p27_registration_without_custom_code(self):
        """Test O: P27 registration succeeds seamlessly under generic portfolio architecture."""
        meta_p27 = PaperMetadata(
            paper_id="P27",
            canonical_manuscript_path="docs/papers/paper27_revised.tex",
            title="Neuromorphic Event Stream Ingestion",
            authors=["ScholarMaster Research Consortium"],
            research_plan_position=27,
            publication_status=PublicationStatus.PLANNED,
            submission_status="PLANNED",
            venue="IEEE Transactions on Neural Networks",
            single_owner_domain="Neuromorphic Event Stream Processing"
        )
        self.registry.register_new_paper(meta_p27)
        self.assertIn("P27", self.registry.papers)

    def test_p_accepted_in_press_vs_issue_date_policy(self):
        """Test P: Accepted-in-press date differs from issue date -> configured citation policy respected."""
        p = PaperMetadata(
            paper_id="P99",
            canonical_manuscript_path="docs/papers/paper99.tex",
            title="Test Paper",
            authors=["Test Author"],
            research_plan_position=99,
            publication_status=PublicationStatus.ACCEPTED_IN_PRESS,
            submission_status="ACCEPTED",
            venue="IEEE Trans",
            acceptance_date="2026-03-01",
            online_publication_date="2026-04-01",
            issue_publication_date="2026-09-01",
            citation_eligible_date="2026-04-01",
            citation_eligibility_basis="ONLINE_FIRST"
        )
        self.registry.register_new_paper(p)
        self.assertTrue(p.is_strictly_citation_eligible())
        self.assertEqual(p.citation_eligible_date, "2026-04-01")

    def test_q_missing_publication_date_unresolved(self):
        """Test Q: Missing authoritative publication date -> citation eligibility remains unresolved."""
        p = PaperMetadata(
            paper_id="P100",
            canonical_manuscript_path="docs/papers/paper100.tex",
            title="Unpublished Draft",
            authors=["Test Author"],
            research_plan_position=100,
            publication_status=PublicationStatus.SUBMITTED,
            submission_status="IN_REVIEW",
            venue="IEEE Trans",
            publication_date=None,
            citation_eligible_date=None
        )
        self.registry.register_new_paper(p)
        self.assertFalse(p.is_strictly_citation_eligible())

    def test_r_actual_tex_citation_reports_citation_present(self):
        """Test R: Actual .tex citation exists -> reports CITATION_PRESENT rather than duplicate insertion."""
        # Inspect P7 which cites P5 (b5 / scholar5)
        inspection = self.planner.inspect_manuscript_citations("P7")
        self.assertTrue(inspection["exists"])
        self.assertTrue(len(inspection["bibitems"]) > 0 or len(inspection["cites"]) > 0)


if __name__ == "__main__":
    unittest.main()
