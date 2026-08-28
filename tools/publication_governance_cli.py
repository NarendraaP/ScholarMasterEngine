#!/usr/bin/env python3
"""
ScholarMaster - Portfolio Publication State & Automatic Synchronization CLI
============================================================================
Command-line interface for the permanent portfolio publication governance engine.

Usage:
  python3 tools/publication_governance_cli.py status
  python3 tools/publication_governance_cli.py publish --paper P23 --doi 10.1109/SCHOLAR.2026.P23 --venue "IEEE Trans. Edge Computing" --date 2026-08-24
  python3 tools/publication_governance_cli.py register --paper P26 --title "Multi-Modal Sensor Topology" --domain "Sensor Topologies" --pos 26
  python3 tools/publication_governance_cli.py audit
"""

import sys
import os
import argparse
import json

# Ensure repository root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.governance.publication_engine import (
    PublicationRegistry, DualGraphManager, PublicationSynchronizer,
    PublicationStatus, PublicationEvent, PaperMetadata, ReviewerCalibratedValidator
)


def cmd_status(args):
    registry = PublicationRegistry()
    print("=" * 70)
    print("SCHOLARMASTER PORTFOLIO PUBLICATION STATUS")
    print("=" * 70)
    print(f"Total Registered Papers: {len(registry.papers)}")
    print("-" * 70)
    print(f"{'Paper ID':<10} {'Status':<18} {'Pub Date':<12} {'Citable?':<10} {'Title':<30}")
    print("-" * 70)
    for p_id, p in registry.papers.items():
        citable_str = "YES" if p.citation_eligible else "NO"
        print(f"{p_id:<10} {p.publication_status.value:<18} {p.publication_date or 'N/A':<12} {citable_str:<10} {p.title[:28]}...")
    print("=" * 70)


def cmd_publish(args):
    sync = PublicationSynchronizer()
    old_paper = sync.registry.get_paper(args.paper)
    if not old_paper:
        print(f"[ERROR] Paper {args.paper} not found in registry.")
        sys.exit(1)

    event = PublicationEvent(
        event_id=f"EVT_{args.paper}_{args.status}",
        paper_id=args.paper,
        previous_status=old_paper.publication_status,
        new_status=PublicationStatus(args.status),
        doi=args.doi,
        venue=args.venue,
        publication_date=args.date,
        citation_eligible_date=args.citation_date or args.date,
        citation_eligibility_basis=args.basis,
        volume=args.volume,
        issue=args.issue,
        pages=args.pages
    )

    print(f"[INFO] Processing Publication Event for {args.paper} ({old_paper.publication_status.value} -> {args.status})...")
    impact = sync.handle_publication_event(event)

    print("\n" + "=" * 70)
    print(f"PUBLICATION IMPACT ANALYSIS: {args.paper}")
    print("=" * 70)
    print(f"Newly Citation-Eligible Papers: {len(impact.newly_citation_eligible_papers)} ({', '.join(impact.newly_citation_eligible_papers)})")
    print(f"Existing References Requiring Sync: {len(impact.existing_references_requiring_sync)}")
    print(f"Future References Converted: {len(impact.future_paper_references_converted)}")
    print(f"Chronology Violations Detected: {len(impact.chronology_violations_detected)}")
    print(f"Human Review Required: {len(impact.human_review_required)}")
    print(f"Unaffected Manuscripts: {len(impact.unaffected_manuscripts)}")
    print("=" * 70)
    print(f"[SUCCESS] Impact report written to research_governance/publication_events/IMPACT_REPORT_{args.paper}_{args.status}.md")


def cmd_register(args):
    registry = PublicationRegistry()
    if args.paper in registry.papers:
        print(f"[WARN] Paper {args.paper} is already registered. Updating record.")

    meta = PaperMetadata(
        paper_id=args.paper,
        canonical_manuscript_path=f"docs/papers/paper{args.pos}_revised.tex",
        title=args.title,
        authors=["ScholarMaster Research Consortium"],
        research_plan_position=args.pos,
        publication_status=PublicationStatus(args.status),
        submission_status="PLANNED",
        venue=args.venue or "ScholarMaster Series",
        doi=args.doi,
        publication_date=args.date,
        citation_eligible_date=args.citation_date or args.date,
        citation_eligibility_basis=args.basis or "VERSION_OF_RECORD",
        canonical_bibtex_key=f"scholarmaster_{args.paper.lower()}_2026",
        single_owner_domain=args.domain,
        research_question=args.rq,
        primary_contribution=args.contrib,
        evidence_type=args.evidence,
        target_venue=args.venue,
        citation_eligible=args.status in [PublicationStatus.PUBLISHED.value, PublicationStatus.ACCEPTED_IN_PRESS.value] and bool(args.citation_date or args.date)
    )
    registry.register_new_paper(meta)
    
    # Recompute graphs
    gm = DualGraphManager(registry)
    gm.recompute_citation_graph()
    
    print(f"[SUCCESS] Paper {args.paper} successfully registered and integrated into portfolio governance.")


def cmd_audit(args):
    registry = PublicationRegistry()
    gm = DualGraphManager(registry)
    validator = ReviewerCalibratedValidator()

    print("=" * 70)
    print("PORTFOLIO CHRONOLOGY & DUAL-GRAPH AUDIT")
    print("=" * 70)
    print(f"Research Plan Graph Edges: {len(gm.research_plan_edges)}")
    print(f"Publication Citation Graph Valid Edges: {len(gm.citation_edges)}")
    print(f"Total Registered Papers: {len(registry.papers)}")
    print("-" * 70)
    
    passed_count = 0
    for p_id, p in registry.papers.items():
        res = validator.validate_paper(p)
        if res["overall_status"] == "PASSED_CALIBRATION_STANDARD":
            passed_count += 1
    
    print(f"Reviewer-Calibrated Standard: {passed_count}/{len(registry.papers)} papers compliant.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="ScholarMaster Portfolio Publication Governance CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status
    subparsers.add_parser("status", help="Show portfolio publication status")

    # Publish
    p_pub = subparsers.add_parser("publish", help="Trigger a publication event and run impact analysis")
    p_pub.add_argument("--paper", required=True, help="Paper ID (e.g. P23)")
    p_pub.add_argument("--status", default="PUBLISHED", choices=["PUBLISHED", "ACCEPTED_IN_PRESS", "SUBMITTED", "DRAFT"])
    p_pub.add_argument("--doi", help="Official DOI")
    p_pub.add_argument("--venue", help="Publication venue")
    p_pub.add_argument("--date", help="Publication date (YYYY-MM-DD)")
    p_pub.add_argument("--citation_date", help="Citation eligible date (YYYY-MM-DD)")
    p_pub.add_argument("--basis", default="VERSION_OF_RECORD", help="Citation eligibility basis (e.g. ACCEPTED_IN_PRESS, ONLINE_FIRST, VERSION_OF_RECORD)")
    p_pub.add_argument("--volume", help="Volume number")
    p_pub.add_argument("--issue", help="Issue number")
    p_pub.add_argument("--pages", help="Page range")

    # Register (P26+)
    p_reg = subparsers.add_parser("register", help="Register a new paper into the portfolio architecture")
    p_reg.add_argument("--paper", required=True, help="Paper ID (e.g. P26)")
    p_reg.add_argument("--title", required=True, help="Paper Title")
    p_reg.add_argument("--domain", required=True, help="SROS-004 Single-Owner Domain")
    p_reg.add_argument("--rq", help="Core Research Question")
    p_reg.add_argument("--contrib", help="Primary Scientific Contribution")
    p_reg.add_argument("--evidence", default="MEASURED", help="Evidence Type (MEASURED, BENCHMARK, USER_STUDY, FORMAL)")
    p_reg.add_argument("--pos", type=int, default=26, help="Research Plan Position")
    p_reg.add_argument("--status", default="PLANNED", choices=["PLANNED", "DRAFT", "SUBMITTED", "ACCEPTED_IN_PRESS", "PUBLISHED"])
    p_reg.add_argument("--venue", help="Target venue")
    p_reg.add_argument("--doi", help="DOI if known")
    p_reg.add_argument("--date", help="Target date")
    p_reg.add_argument("--citation_date", help="Citation eligible date")
    p_reg.add_argument("--basis", help="Citation eligibility basis")

    # Audit
    subparsers.add_parser("audit", help="Run chronology and dual-graph audit")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "register":
        cmd_register(args)
    elif args.command == "audit":
        cmd_audit(args)


if __name__ == "__main__":
    main()

