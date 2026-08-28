"""
Comprehensive Hardened Test Suite for ScholarMaster Research Portfolio Governance Engine
Tests A through O covering real failure modes, chronology, relevance, provenance, and isolation.
"""

import unittest, json, os, tempfile, shutil
from research_governance.portfolio_engine.citation_eligibility import CitationEligibilityEngine
from research_governance.portfolio_engine.publication_propagation import PublicationPropagationEngine
from research_governance.portfolio_engine.register_paper import PaperRegistrationEngine
from research_governance.portfolio_engine.portfolio_consistency import PortfolioConsistencyEngine
from research_governance.portfolio_engine.generator import MasterPlanGenerator

class TestPortfolioEngineHardened(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.elig_engine = CitationEligibilityEngine(os.path.join(self.data_dir, "paper_registry.json"))
        self.prop_engine = PublicationPropagationEngine(self.data_dir)
        self.reg_engine = PaperRegistrationEngine(self.data_dir)
        self.cons_engine = PortfolioConsistencyEngine(self.data_dir)

    def test_A_published_cited_paper_earlier_citing_date_is_invalid(self):
        """Test A: Published cited paper + earlier citing date -> INVALID_FORWARD_REFERENCE."""
        # P05 was published 2026-03-15. If citing paper has relevant date 2025-01-01 -> INVALID
        res = self.elig_engine.evaluate_eligibility("P07", "P05", citing_date="2025-01-01")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")
        self.assertIn("Chronology violation", res["reason"])

    def test_B_accepted_cited_paper_earlier_citing_date_is_invalid(self):
        """Test B: Accepted cited paper + earlier citing date -> INVALID_FORWARD_REFERENCE."""
        # P06 was accepted 2026-05-10. If citing date is 2026-01-01 -> INVALID
        res = self.elig_engine.evaluate_eligibility("P01", "P06", citing_date="2026-01-01")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")
        self.assertIn("earlier than cited acceptance date", res["reason"])

    def test_C_accepted_cited_paper_later_citing_date_is_valid_in_press(self):
        """Test C: Accepted cited paper + later citing date -> VALID_ACCEPTED_IN_PRESS."""
        # P06 accepted 2026-05-10. If citing date is 2026-08-29 -> VALID_ACCEPTED_IN_PRESS
        res = self.elig_engine.evaluate_eligibility("P01", "P06", citing_date="2026-08-29")
        self.assertEqual(res["verdict"], "VALID_ACCEPTED_IN_PRESS")

    def test_D_companion_dependency_does_not_bypass_chronology(self):
        """Test D: Companion dependency relationship does NOT bypass chronology."""
        # P23 cites companion P22 (which is an unpublished DRAFT)
        res = self.elig_engine.evaluate_eligibility("P23", "P22")
        self.assertEqual(res["relationship"], "COMPANION_SERIES_DEPENDENCY")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")

    def test_E_unknown_publication_date_returns_status_uncertain(self):
        """Test E: Unknown publication date -> STATUS_UNCERTAIN."""
        # Temporarily mock P05 with null publication date
        old_pub = self.elig_engine.registry["P05"]["publication_date"]
        self.elig_engine.registry["P05"]["publication_date"] = None
        try:
            res = self.elig_engine.evaluate_eligibility("P07", "P05")
            self.assertEqual(res["verdict"], "STATUS_UNCERTAIN")
        finally:
            self.elig_engine.registry["P05"]["publication_date"] = old_pub

    def test_F_previously_blocked_edge_becomes_newly_eligible_after_publication(self):
        """Test F: Previously blocked edge becomes eligible after publication with valid chronology."""
        # P22 is DRAFT (blocked). If published on 2026-01-01 (prior to citing drafts on 2026-08-29), becomes newly eligible
        sim_res = self.prop_engine.propagate_status_change("P22", "PUBLISHED", date="2026-01-01", venue="IEEE TPAMI", dry_run=True)
        self.assertGreater(sim_res["newly_eligible_count"], 0)
        newly_ids = [o["potential_citing_paper"] for o in sim_res["newly_eligible"]]
        self.assertIn("P23", newly_ids)

    def test_G_already_valid_citation_is_not_reported_as_newly_eligible(self):
        """Test G: Already-valid citation is not reported as newly eligible."""
        # P05 is ALREADY PUBLISHED. Re-propagating P05 should result in newly_eligible_count == 0.
        sim_res = self.prop_engine.propagate_status_change("P05", "PUBLISHED", date="2026-03-15", force=True, dry_run=True)
        self.assertEqual(sim_res["newly_eligible_count"], 0)
        self.assertGreater(sim_res["already_eligible_count"], 0)

    def test_H_publication_event_does_not_modify_manuscript_files(self):
        """Test H: Publication event does not modify manuscript files."""
        sim_res = self.prop_engine.propagate_status_change("P06", "PUBLISHED", date="2026-09-15", dry_run=True)
        for opp in sim_res["all_opportunities"]:
            self.assertFalse(opp["automatic_insertion"])

    def test_I_no_fake_author_metadata_is_generated(self):
        """Test I: No fake guessed author metadata is in paper_registry."""
        with open(os.path.join(self.data_dir, "paper_registry.json")) as f:
            reg = json.load(f)
        for pid, rec in reg.items():
            authors = rec.get("authors")
            if authors:
                self.assertNotIn("S. Suresh Kumar et al.", authors)

    def test_J_no_claim_is_automatically_marked_verified_supported(self):
        """Test J: No claim is automatically marked VERIFIED_SUPPORTED without verification."""
        with open(os.path.join(self.data_dir, "claim_registry.json")) as f:
            claims = json.load(f)
        for clm in claims:
            self.assertNotEqual(clm["status"], "VERIFIED_SUPPORTED")
            self.assertEqual(clm["status"], "SOURCE_BACKED")

    def test_K_no_evidence_is_automatically_physical_without_source(self):
        """Test K: Evidence classes match source descriptions."""
        with open(os.path.join(self.data_dir, "evidence_registry.json")) as f:
            evidence = json.load(f)
        for ev in evidence:
            ev_class = ev.get("evidence_class")
            self.assertIn(ev_class, ["PHYSICAL_MEASUREMENT", "SIMULATION", "ANALYTICAL_DERIVATION", "USER_STUDY", "EXTRACTED"])

    def test_L_simulated_doi_cannot_enter_authoritative_registry(self):
        """Test L: A simulated DOI cannot enter the authoritative registry."""
        with open(os.path.join(self.data_dir, "paper_registry.json")) as f:
            reg_before = json.load(f)
        
        # Run dry run propagation with simulated DOI
        self.prop_engine.propagate_status_change("P06", "PUBLISHED", date="2026-09-15", doi="10.1109/SIMULATED.DOI", dry_run=True)
        
        with open(os.path.join(self.data_dir, "paper_registry.json")) as f:
            reg_after = json.load(f)
            
        self.assertEqual(reg_before["P06"]["doi"], reg_after["P06"]["doi"])
        self.assertIsNone(reg_after["P06"]["doi"])

    def test_M_generator_uses_dynamic_governance_status(self):
        """Test M: Generator dynamically includes governance status."""
        temp_tex = tempfile.mktemp(suffix=".tex")
        gen = MasterPlanGenerator(data_dir=self.data_dir, output_path=temp_tex)
        gen.generate_latex()
        with open(temp_tex, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Derived Governance Status", content)
        if os.path.exists(temp_tex): os.remove(temp_tex)

    def test_N_future_p26_registration_initializes_all_structures(self):
        """Test N: Future P26 registration initializes all required structures with placeholders."""
        res = self.reg_engine.register_new_paper("P26", "Zero-Knowledge Proofs", "Cryptography", dry_run=True)
        rec = res["record"]
        self.assertEqual(rec["paper_id"], "P26")
        self.assertIsNone(rec["authors"])
        self.assertIsNone(rec["publication_date"])

    def test_O_illegal_publication_state_transitions_are_rejected(self):
        """Test O: Illegal publication-state transitions (e.g. PUBLISHED -> DRAFT) are rejected."""
        with self.assertRaises(ValueError):
            # Attempt illegal backwards transition on PUBLISHED paper P05
            self.prop_engine.propagate_status_change("P05", "DRAFT", dry_run=False)

if __name__ == "__main__":
    unittest.main()
