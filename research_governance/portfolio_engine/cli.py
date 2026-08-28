"""
Hardened Command-Line Interface for ScholarMaster Research Portfolio Governance Engine
Supports all 9 governance operations with strict provenance and dry-run isolation.
"""

import argparse, json, sys, os

from .citation_eligibility import CitationEligibilityEngine
from .publication_propagation import PublicationPropagationEngine
from .register_paper import PaperRegistrationEngine
from .portfolio_consistency import PortfolioConsistencyEngine
from .generator import MasterPlanGenerator

def main():
    parser = argparse.ArgumentParser(description="ScholarMaster Research Portfolio Governance Engine (Hardened)")
    subparsers = parser.add_subparsers(dest="command", help="Governance Commands")

    # 1. full-audit
    subparsers.add_parser("full-audit", help="Run full portfolio consistency, chronology, and evidence audit")

    # 2. audit-chronology
    subparsers.add_parser("audit-chronology", help="Audit citation chronology with real date comparison")

    # 3. audit-citations
    cit_parser = subparsers.add_parser("audit-citations", help="Audit specific citation edge or all citation edges")
    cit_parser.add_argument("--citing", help="Citing Paper ID (e.g. P07)")
    cit_parser.add_argument("--cited", help="Cited Paper ID (e.g. P05)")

    # 4. audit-evidence
    ev_parser = subparsers.add_parser("audit-evidence", help="Audit evidence records and classifications")
    ev_parser.add_argument("--paper", help="Filter by Paper ID (e.g. P06)")

    # 5. audit-claims
    clm_parser = subparsers.add_parser("audit-claims", help="Audit claim-to-evidence linkages")
    clm_parser.add_argument("--paper", help="Filter by Paper ID (e.g. P06)")

    # 6. update-status
    up_parser = subparsers.add_parser("update-status", help="Update paper publication status directly")
    up_parser.add_argument("--paper", required=True, help="Paper ID (e.g. P06)")
    up_parser.add_argument("--status", required=True, choices=["PLANNED", "DRAFT", "SUBMITTED", "UNDER_REVIEW", "ACCEPTED", "IN_PRESS", "PUBLISHED"], help="New status")
    up_parser.add_argument("--date", help="Date of transition")
    up_parser.add_argument("--venue", help="Venue")
    up_parser.add_argument("--doi", help="DOI string")
    up_parser.add_argument("--force", action="store_true", help="Force exceptional transition")
    up_parser.add_argument("--dry-run", action="store_true", help="Simulate update")

    # 7. propagate-publication
    prop_parser = subparsers.add_parser("propagate-publication", help="Propagate publication lifecycle transition & detect citation opportunities")
    prop_parser.add_argument("--paper", required=True, help="Paper ID (e.g. P06)")
    prop_parser.add_argument("--status", required=True, choices=["ACCEPTED", "IN_PRESS", "PUBLISHED"], help="New publication state")
    prop_parser.add_argument("--date", help="Date of state transition (YYYY-MM-DD)")
    prop_parser.add_argument("--venue", help="Publication / acceptance venue")
    prop_parser.add_argument("--doi", help="DOI string if published")
    prop_parser.add_argument("--force", action="store_true", help="Force exceptional transition")
    prop_parser.add_argument("--dry-run", action="store_true", help="Simulate state transition without modifying registries")

    # 8. register-paper
    reg_parser = subparsers.add_parser("register-paper", help="Register a new future research paper (e.g. P26)")
    reg_parser.add_argument("--paper", required=True, help="New Paper ID (e.g. P26)")
    reg_parser.add_argument("--title", required=True, help="Paper Title")
    reg_parser.add_argument("--area", required=True, help="Research Area")
    reg_parser.add_argument("--type", default="SYSTEMS", help="Methodological Type")
    reg_parser.add_argument("--venue", default="IEEE Transactions", help="Primary Target Venue")
    reg_parser.add_argument("--dry-run", action="store_true", help="Simulate registration")

    # 9. generate-master-plan
    gen_parser = subparsers.add_parser("generate-master-plan", help="Generate Master Paper Plan LaTeX from registries")
    gen_parser.add_argument("--output", help="Output LaTeX file path")

    args = parser.parse_args()

    if args.command == "full-audit":
        print("=== SCHOLARMASTER PORTFOLIO ENGINE — FULL AUDIT ===")
        cons_engine = PortfolioConsistencyEngine()
        cons_res = cons_engine.run_full_consistency_audit()
        print(f"Overall Governance Status: {cons_res['governance_status']}")
        print(f"Total Discrepancies: {cons_res['total_discrepancies']}")
        for k, v in cons_res["checks"].items():
            print(f"  [{'PASS' if v else 'FAIL'}] {k}")
        print("\nPortfolio Summary:")
        for k, v in cons_res["portfolio_summary"].items():
            print(f"  {k}: {v}")

    elif args.command == "audit-chronology":
        print("=== SCHOLARMASTER PORTFOLIO ENGINE — CHRONOLOGY AUDIT ===")
        elig_engine = CitationEligibilityEngine()
        audit = elig_engine.audit_portfolio_chronology()
        print(f"Chronology Clean: {audit['is_clean']} (Violations: {audit['total_violations']} / {audit['total_citations_checked']})")
        for res in audit["all_results"]:
            cp = res["citing_paper"]
            tp = res["cited_paper"]
            v = res["evaluation"]["verdict"]
            rel = res["evaluation"].get("relationship", "STANDARD")
            print(f"  Edge: {cp} -> {tp} | Verdict: {v} | Rel: {rel}")

    elif args.command == "audit-citations":
        print("=== SCHOLARMASTER CITATION ELIGIBILITY EVALUATION ===")
        elig_engine = CitationEligibilityEngine()
        if args.citing and args.cited:
            res = elig_engine.evaluate_eligibility(args.citing, args.cited)
            print(f"Citing: {args.citing} | Cited: {args.cited}")
            print(f"Verdict: {res['verdict']}")
            print(f"Relationship: {res.get('relationship')}")
            print(f"Reason: {res['reason']}")
        else:
            audit = elig_engine.audit_portfolio_chronology()
            print(f"Audited {audit['total_citations_checked']} citation edges.")

    elif args.command == "audit-evidence":
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "data", "evidence_registry.json")) as f:
            ev_list = json.load(f)
        if args.paper:
            ev_list = [e for e in ev_list if e["paper"] == args.paper]
        print(f"=== EVIDENCE AUDIT ({len(ev_list)} records) ===")
        for e in ev_list:
            print(f"  [{e['evidence_id']}] Paper {e['paper']} | Class: {e.get('evidence_class', e.get('type'))} | Status: {e.get('verification_status')} | Claim: {e['claim'][:40]}...")

    elif args.command == "audit-claims":
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "data", "claim_registry.json")) as f:
            clm_list = json.load(f)
        if args.paper:
            clm_list = [c for c in clm_list if c["paper"] == args.paper]
        print(f"=== CLAIM AUDIT ({len(clm_list)} claims) ===")
        for c in clm_list:
            print(f"  [{c['claim_id']}] Paper {c['paper']} | Status: {c['status']} | Evidence IDs: {c['evidence_ids']}")

    elif args.command in ["update-status", "propagate-publication"]:
        print(f"=== PUBLICATION STATE PROPAGATION: {args.paper} -> {args.status} (Dry Run: {args.dry_run}) ===")
        prop_engine = PublicationPropagationEngine()
        res = prop_engine.propagate_status_change(args.paper, args.status, date=args.date, venue=args.venue, doi=args.doi, force=getattr(args, 'force', False), dry_run=args.dry_run)
        print(f"Transition: {res['old_status']} -> {res['new_status']}")
        print(f"Newly Eligible Potential Citations: {res['newly_eligible_count']}")
        print(f"Already Eligible Citations: {res['already_eligible_count']}")
        print(f"Still Blocked Citations: {res['still_blocked_count']}")
        for opp in res["newly_eligible"]:
            print(f"  -> Newly Eligible Candidate: {opp['potential_citing_paper']} ({opp['target_paper_title'][:40]}...) | Relevance: {opp['scientific_relevance']}")

    elif args.command == "register-paper":
        print(f"=== REGISTERING PAPER {args.paper} (Dry Run: {args.dry_run}) ===")
        reg_engine = PaperRegistrationEngine()
        res = reg_engine.register_new_paper(args.paper, args.title, args.area, paper_type=args.type, target_venue_primary=args.venue, dry_run=args.dry_run)
        print(f"Status: {res['status']}")
        print(f"Record: {json.dumps(res['record'], indent=2)}")

    elif args.command == "generate-master-plan":
        print("=== GENERATING MASTER PAPER PLAN LATEX ===")
        gen = MasterPlanGenerator(output_path=args.output)
        out = gen.generate_latex()
        print(f"Master Paper Plan generated at: {out}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
