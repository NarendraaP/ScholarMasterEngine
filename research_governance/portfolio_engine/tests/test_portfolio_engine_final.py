"""
Final Trust-Hardened Automated Test Suite for ScholarMaster Research Governance Engine
Tests 1 through 15 and Tests A through G validating strict provenance, zero keyword guessing, and real diff checks.
"""

import unittest, json, os, tempfile, shutil, hashlib, glob
from research_governance.portfolio_engine.source_resolver import SourceResolver
from research_governance.portfolio_engine.citation_resolver import CitationResolver
from research_governance.portfolio_engine.diff_ledger_verifier import DiffLedgerVerifier
from research_governance.portfolio_engine.evidence_provenance import EvidenceProvenanceTracker
from research_governance.portfolio_engine.citation_eligibility import CitationEligibilityEngine
from research_governance.portfolio_engine.publication_propagation import PublicationPropagationEngine
from research_governance.portfolio_engine.register_paper import PaperRegistrationEngine
from research_governance.portfolio_engine.portfolio_consistency import PortfolioConsistencyEngine
from research_governance.portfolio_engine.generator import MasterPlanGenerator

class TestFinalTrustHardening(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.data_dir = os.path.join(self.root_dir, "research_governance", "portfolio_engine", "data")
        self.source_resolver = SourceResolver(self.root_dir)
        self.citation_resolver = CitationResolver(self.root_dir)
        self.diff_verifier = DiffLedgerVerifier(self.root_dir)
        self.evidence_tracker = EvidenceProvenanceTracker(self.root_dir)
        self.elig_engine = CitationEligibilityEngine(os.path.join(self.data_dir, "paper_registry.json"))
        self.prop_engine = PublicationPropagationEngine(self.data_dir)
        self.reg_engine = PaperRegistrationEngine(self.data_dir)
        self.cons_engine = PortfolioConsistencyEngine(self.root_dir)

    # Test A / Test 11: Hard-coded metadata test (missing source returns UNKNOWN, not hard-coded string)
    def test_A_hardcoded_metadata_removed_returns_unknown(self):
        """Test A: Missing publication metadata from authoritative sources returns UNKNOWN, not hardcoded strings."""
        res = self.source_resolver.resolve_paper_metadata(2)
        self.assertEqual(res["publication_date"]["verification_status"], "UNKNOWN")
        self.assertIsNone(res["publication_date"]["value"])
        self.assertIsNone(res["doi"]["value"])

    # Test B / Test 7: Fake keyword citation test (matching keyword without canonical mapping is NOT internal citation)
    def test_B_fake_keyword_citation_is_not_treated_as_internal(self):
        """Test B: A bibliography containing 'Memory-Bound Edge Efficiency Envelope' without canonical mapping is NOT P05."""
        temp_dir = tempfile.mkdtemp()
        tex_path = os.path.join(temp_dir, "paper97_revised.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(r"""
\documentclass{article}
\begin{document}
As shown in \cite{generic_ref}, edge efficiency is important.
\begin{thebibliography}{99}
\bibitem{generic_ref} J. Doe, "Memory-Bound Edge Efficiency Envelope on FPGA," Random Workshop, 2021.
\end{thebibliography}
\end{document}
""")
        resolver = CitationResolver(root_dir=temp_dir)
        resolver.papers_dir = temp_dir
        res = resolver.parse_manuscript_citations(97)
        self.assertEqual(len(res["citations"]), 1)
        self.assertIsNone(res["citations"][0]["target_paper_id"])
        self.assertEqual(res["citations"][0]["citation_type"], "EXTERNAL_CITATION")
        shutil.rmtree(temp_dir)

    # Test C / Test 6: Real citation test (only \cite{KEY} resolved via \bibitem becomes actual internal edge)
    def test_C_real_citation_resolves_through_canonical_key(self):
        """Test C: Only \\cite{KEY} resolved through bibliography and canonical key becomes an actual internal edge."""
        temp_dir = tempfile.mkdtemp()
        tex_path = os.path.join(temp_dir, "paper96_revised.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(r"""
\documentclass{article}
\begin{document}
We build on \cite{kumar2026scholar22} for evidential gating.
\begin{thebibliography}{99}
\bibitem{kumar2026scholar22} P. Narendra et al., "Evidential Perception Gating," 2026.
\end{thebibliography}
\end{document}
""")
        resolver = CitationResolver(root_dir=temp_dir)
        resolver.papers_dir = temp_dir
        res = resolver.parse_manuscript_citations(96)
        self.assertEqual(len(res["citations"]), 1)
        self.assertEqual(res["citations"][0]["target_paper_id"], "P22")
        self.assertEqual(res["citations"][0]["citation_type"], "ACTUAL_CITATION")
        shutil.rmtree(temp_dir)

    # Test D / Test 9: Ledger phantom test (ledger says change happened but diff is empty)
    def test_D_ledger_phantom_returns_not_found(self):
        """Test D: Ledger entry with no corresponding diff returns PARTIALLY_VERIFIED and NOT_FOUND."""
        temp_dir = tempfile.mkdtemp()
        curr_dir = os.path.join(temp_dir, "docs", "papers")
        back_dir = os.path.join(temp_dir, "docs", "papers_backup_pre_revision")
        gov_dir = os.path.join(temp_dir, "research_governance", "controlled_revision")
        os.makedirs(curr_dir); os.makedirs(back_dir); os.makedirs(gov_dir)
        
        with open(os.path.join(back_dir, "paper99_revised.tex"), "w") as f: f.write("Identical text\n")
        with open(os.path.join(curr_dir, "paper99_revised.tex"), "w") as f: f.write("Identical text\n")
        
        with open(os.path.join(gov_dir, "CHANGE_LEDGER.json"), "w") as f:
            json.dump([{"paper": "P99", "old_problem": "Hypothetical issue", "evidence_source": "manual"}], f)
            
        verifier = DiffLedgerVerifier(root_dir=temp_dir)
        verifier.current_dir = curr_dir
        verifier.backup_dir = back_dir
        verifier.ledger_path = os.path.join(gov_dir, "CHANGE_LEDGER.json")
        res = verifier.verify_paper_diff_against_ledger(99)
        self.assertEqual(res["status"], "PARTIALLY_VERIFIED")
        self.assertIn("NOT_FOUND", res["ledger_status"])
        shutil.rmtree(temp_dir)

    # Test E / Test 8: Unledgered diff test (diff exists without ledger)
    def test_E_unledgered_diff_returns_review_required(self):
        """Test E: Substantive diff without matching ledger entry returns REVIEW_REQUIRED / UNLEDGERED."""
        temp_dir = tempfile.mkdtemp()
        curr_dir = os.path.join(temp_dir, "docs", "papers")
        back_dir = os.path.join(temp_dir, "docs", "papers_backup_pre_revision")
        os.makedirs(curr_dir); os.makedirs(back_dir)
        
        with open(os.path.join(back_dir, "paper99_revised.tex"), "w") as f: f.write("Pre-revision baseline\n")
        with open(os.path.join(curr_dir, "paper99_revised.tex"), "w") as f: f.write("Revised content not in ledger\n")
        
        verifier = DiffLedgerVerifier(root_dir=temp_dir)
        verifier.current_dir = curr_dir
        verifier.backup_dir = back_dir
        res = verifier.verify_paper_diff_against_ledger(99)
        self.assertEqual(res["status"], "REVIEW_REQUIRED")
        self.assertIn("UNLEDGERED", res["diff_status"])
        shutil.rmtree(temp_dir)

    # Test F / Test 10: Evidence keyword test (text contains simulation without structured record -> UNKNOWN / REVIEW_REQUIRED)
    def test_F_evidence_without_structured_source_returns_review_required(self):
        """Test F: Numerical claim without structured environment record returns UNKNOWN and REVIEW_REQUIRED."""
        tracker = EvidenceProvenanceTracker()
        temp_num = tempfile.mktemp(suffix=".json")
        temp_scope = tempfile.mktemp(suffix=".json")
        
        # Claim mentioning simulation in text, but scope record has unmapped environment
        with open(temp_num, "w") as f:
            json.dump([{"paper": "P99", "numerical_claim": "simulation result 95%", "source": "ad-hoc script", "final_manuscript_location": "sec 2", "pre_existing_evidence": True}], f)
        with open(temp_scope, "w") as f:
            json.dump({"P99": {"environment_classification": "UNRECOGNIZED_CUSTOM_ENV"}}, f)
            
        tracker.num_audit_path = temp_num
        tracker.scope_audit_path = temp_scope
        
        evs = tracker.build_evidence_registry()
        self.assertEqual(evs[0]["evidence_class"], "UNKNOWN")
        self.assertEqual(evs[0]["verification_status"], "REVIEW_REQUIRED")
        self.assertEqual(evs[0]["classification_method"], "MANUAL_REVIEW_REQUIRED")
        
        os.remove(temp_num); os.remove(temp_scope)

    # Test G / Test 12: Simulation isolation test (simulated values never leak)
    def test_G_simulation_isolation_does_not_mutate_authoritative_state(self):
        """Test G: A simulated DOI/status can never enter authoritative state."""
        with open(os.path.join(self.data_dir, "paper_registry.json")) as f:
            before = json.load(f)
        self.prop_engine.propagate_status_change("P06", "PUBLISHED", date="2026-08-20", doi="10.1109/SIMULATED.123", dry_run=True)
        with open(os.path.join(self.data_dir, "paper_registry.json")) as f:
            after = json.load(f)
        self.assertEqual(before["P06"]["doi"], after["P06"]["doi"])
        self.assertIsNone(after["P06"]["doi"])

    # Chronology & Date Tests
    def test_01_wrong_date_returns_invalid(self):
        """Test 1: citing date earlier than cited pub date -> INVALID_FORWARD_REFERENCE."""
        res = self.elig_engine.evaluate_eligibility("P07", "P05", citing_date="2025-01-01")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")

    def test_02_accepted_paper_earlier_citing_date_is_invalid(self):
        """Test 2: Citing date before acceptance date -> INVALID_FORWARD_REFERENCE."""
        res = self.elig_engine.evaluate_eligibility("P01", "P06", citing_date="2026-01-01")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")

    def test_03_accepted_paper_later_citing_date_is_valid_in_press(self):
        """Test 3: Citing date after acceptance date -> VALID_ACCEPTED_IN_PRESS."""
        res = self.elig_engine.evaluate_eligibility("P01", "P06", citing_date="2026-08-29")
        self.assertEqual(res["verdict"], "VALID_ACCEPTED_IN_PRESS")

    def test_04_unknown_date_returns_uncertain(self):
        """Test 4: Unknown publication date -> STATUS_UNCERTAIN."""
        old_pub = self.elig_engine.registry["P05"]["publication_date"]
        self.elig_engine.registry["P05"]["publication_date"] = None
        try:
            res = self.elig_engine.evaluate_eligibility("P07", "P05")
            self.assertEqual(res["verdict"], "STATUS_UNCERTAIN")
        finally:
            self.elig_engine.registry["P05"]["publication_date"] = old_pub

    def test_05_companion_dependency_does_not_override_chronology(self):
        """Test 5: Companion relationship does NOT override chronology."""
        res = self.elig_engine.evaluate_eligibility("P23", "P22")
        self.assertEqual(res["relationship"], "COMPANION_SERIES_DEPENDENCY")
        self.assertEqual(res["verdict"], "INVALID_FORWARD_REFERENCE")

    def test_14_no_manuscript_modification_after_propagation(self):
        """Test 14: Hashes of manuscript files before and after propagation remain identical."""
        hashes_before = {}
        for fpath in glob.glob(os.path.join(self.root_dir, "docs", "papers", "paper*.tex")):
            with open(fpath, "rb") as f: hashes_before[fpath] = hashlib.sha256(f.read()).hexdigest()
            
        self.prop_engine.propagate_status_change("P06", "PUBLISHED", date="2026-08-20", dry_run=True)
        
        hashes_after = {}
        for fpath in glob.glob(os.path.join(self.root_dir, "docs", "papers", "paper*.tex")):
            with open(fpath, "rb") as f: hashes_after[fpath] = hashlib.sha256(f.read()).hexdigest()
            
        self.assertEqual(hashes_before, hashes_after)

    def test_15_master_plan_status_conditional_when_discrepancies_exist(self):
        """Test 15: When unresolved verification gates exist, Master Plan reports CONDITIONAL, not FULLY VERIFIED."""
        temp_tex = tempfile.mktemp(suffix=".tex")
        gen = MasterPlanGenerator(data_dir=self.data_dir, output_path=temp_tex)
        gen.generate_latex()
        with open(temp_tex, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("FULLY VERIFIED", content)
        self.assertIn("Derived Governance Status", content)
        if os.path.exists(temp_tex): os.remove(temp_tex)

if __name__ == "__main__":
    unittest.main()
