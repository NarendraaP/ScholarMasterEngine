"""
Final Hardened Portfolio Consistency Engine for ScholarMaster Research Governance
Integrates SourceResolver, CitationResolver, DiffLedgerVerifier, and EvidenceProvenanceTracker.
Eliminates false absolutes and dynamic status derivations.
"""

import json, os
from .source_resolver import SourceResolver
from .citation_resolver import CitationResolver
from .diff_ledger_verifier import DiffLedgerVerifier
from .evidence_provenance import EvidenceProvenanceTracker
from .citation_eligibility import CitationEligibilityEngine

class PortfolioConsistencyEngine:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        else:
            self.root_dir = root_dir
            
        self.data_dir = os.path.join(self.root_dir, "research_governance", "portfolio_engine", "data")
        self.source_resolver = SourceResolver(self.root_dir)
        self.citation_resolver = CitationResolver(self.root_dir)
        self.diff_verifier = DiffLedgerVerifier(self.root_dir)
        self.evidence_tracker = EvidenceProvenanceTracker(self.root_dir)
        self.eligibility_engine = CitationEligibilityEngine(os.path.join(self.data_dir, "paper_registry.json"))

    def run_full_consistency_audit(self):
        # 1. Resolve authoritative metadata
        resolved_portfolio = self.source_resolver.resolve_portfolio()
        
        # 2. Resolve actual citation graph
        actual_citations = self.citation_resolver.build_actual_citation_graph()
        
        # 3. Verify actual diffs vs ledger & frozen hashes
        diff_audit = self.diff_verifier.verify_entire_portfolio()
        
        # 4. Track evidence & claims
        evidence_records = self.evidence_tracker.build_evidence_registry()
        claim_records = self.evidence_tracker.build_claim_registry(evidence_records)

        # 5. Load revision & venue registries
        venue_path = os.path.join(self.data_dir, "venue_registry.json")
        venues = {}
        if os.path.exists(venue_path):
            with open(venue_path, "r", encoding="utf-8") as f:
                venues = json.load(f)

        checks = {}
        discrepancies = []

        # Check 1: Paper IDs unique & 25 canonical present
        p_ids = list(resolved_portfolio.keys())
        checks["unique_paper_ids"] = len(p_ids) == len(set(p_ids))
        checks["canonical_p01_p25_present"] = all(f"P{i:02d}" in resolved_portfolio for i in range(1, 26))

        # Check 2: Publication state integrity (dates verified)
        pub_intact = True
        for pid, meta in resolved_portfolio.items():
            st = meta["status"]["value"]
            if st == "PUBLISHED" and not meta["publication_date"]["value"]:
                pub_intact = False
                discrepancies.append(f"Paper {pid} marked PUBLISHED without verified publication_date.")
            if st in ["ACCEPTED", "IN_PRESS"] and not meta["acceptance_date"]["value"]:
                pub_intact = False
                discrepancies.append(f"Paper {pid} marked ACCEPTED without verified acceptance_date.")
        checks["publication_state_integrity"] = pub_intact

        # Check 3: Chronology of actual in-text citations
        chron_clean = True
        chron_results = []
        for edge in actual_citations["edges"]:
            eval_res = self.eligibility_engine.evaluate_eligibility(edge["citing_paper"], edge["cited_paper"])
            chron_results.append({
                "citing": edge["citing_paper"],
                "cited": edge["cited_paper"],
                "key": edge["citation_key"],
                "verdict": eval_res["verdict"],
                "relationship": eval_res.get("relationship")
            })
            # In published literature, only VALID_PUBLISHED or VALID_ACCEPTED_IN_PRESS are allowed
            if eval_res["verdict"] == "INVALID_FORWARD_REFERENCE":
                chron_clean = False
                discrepancies.append(f"Actual citation {edge['citing_paper']} -> {edge['cited_paper']} violates chronology: {eval_res['reason']}")
        checks["actual_citation_chronology"] = chron_clean

        # Check 4: Frozen manuscript hashes
        checks["frozen_papers_integrity"] = diff_audit["frozen_verification"]["all_frozen_identical"]
        if not diff_audit["frozen_verification"]["all_frozen_identical"]:
            discrepancies.append("Frozen paper hash breach detected.")

        # Check 5: Diff to Ledger Verification
        checks["diff_ledger_integrity"] = diff_audit["all_verified"]

        # Check 6: Claim-to-Evidence Linkage
        ev_ids = set(e["evidence_id"] for e in evidence_records)
        claims_backed = all(all(eid in ev_ids for eid in c["evidence_ids"]) for c in claim_records)
        checks["claims_evidence_linkage"] = claims_backed

        # Check 7: Venue Completeness
        checks["venue_strategy_completeness"] = all(p in venues and venues[p].get("primary_venue") for p in resolved_portfolio)

        # Dynamic Status Derivation (Avoid False Absolutes)
        if all(checks.values()) and len(discrepancies) == 0:
            gov_status = "PASS (No issues detected by available checks)"
        elif checks["unique_paper_ids"] and checks["canonical_p01_p25_present"]:
            gov_status = "CONDITIONAL (Companion dependency alerts or unverified items pending review)"
        else:
            gov_status = "FAIL (Structural failures detected)"

        return {
            "governance_status": gov_status,
            "all_passed": all(checks.values()) and len(discrepancies) == 0,
            "checks": checks,
            "total_discrepancies": len(discrepancies),
            "discrepancies": discrepancies,
            "actual_citations_count": len(actual_citations["edges"]),
            "actual_citations": chron_results,
            "evidence_count": len(evidence_records),
            "claims_count": len(claim_records)
        }

if __name__ == "__main__":
    cons = PortfolioConsistencyEngine()
    audit = cons.run_full_consistency_audit()
    print("Portfolio Consistency Audit Result:", audit["governance_status"])
    print("Discrepancies Count:", audit["total_discrepancies"])
    for k, v in audit["checks"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
