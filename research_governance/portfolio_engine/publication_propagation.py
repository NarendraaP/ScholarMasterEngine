"""
Hardened Publication State Propagation Engine for ScholarMaster Research Governance
Manages verified lifecycle transitions, computes real previously-blocked status,
and evaluates scientific relevance through domain and architectural feature matching.
"""

import json, os, datetime, re
from .citation_eligibility import CitationEligibilityEngine

# Legal State Transitions
LEGAL_TRANSITIONS = {
    "PLANNED": ["DRAFT", "WITHDRAWN"],
    "DRAFT": ["SUBMITTED", "PLANNED", "WITHDRAWN"],
    "SUBMITTED": ["UNDER_REVIEW", "WITHDRAWN", "REJECTED"],
    "UNDER_REVIEW": ["ACCEPTED", "REJECTED", "SUBMITTED", "WITHDRAWN"],
    "ACCEPTED": ["IN_PRESS", "PUBLISHED", "WITHDRAWN"],
    "IN_PRESS": ["PUBLISHED", "WITHDRAWN"],
    "PUBLISHED": [], # Terminal state
    "REJECTED": ["DRAFT", "RESUBMITTED", "PLANNED"],
    "RESUBMITTED": ["UNDER_REVIEW", "ACCEPTED", "REJECTED"],
    "WITHDRAWN": ["PLANNED", "DRAFT"]
}

class PublicationPropagationEngine:
    def __init__(self, data_dir=None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
        
        self.data_dir = data_dir
        self.paper_registry_path = os.path.join(data_dir, "paper_registry.json")
        self.publication_events_path = os.path.join(data_dir, "publication_events.json")
        self.citation_opportunities_path = os.path.join(data_dir, "citation_opportunities.json")
        self.audit_log_path = os.path.join(os.path.dirname(data_dir), "engine_audit_log.jsonl")

    def _log_action(self, command, paper_id, action, old_state, new_state, source, result, dry_run=False):
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "command": command,
            "paper": paper_id,
            "action": action,
            "old_state": old_state,
            "new_state": new_state,
            "source": source,
            "operator_mode": "DRY_RUN" if dry_run else "LIVE_EXECUTION",
            "result": result
        }
        if not dry_run and os.path.exists(os.path.dirname(self.audit_log_path)):
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        return log_entry

    def evaluate_scientific_relevance(self, newly_published_rec, target_rec):
        """
        Generic, source-driven scientific relevance gate.
        Uses research area token sets, contribution keywords, and architectural couplings.
        """
        new_area = set(re.findall(r"\w+", newly_published_rec.get("research_area", "").lower()))
        tgt_area = set(re.findall(r"\w+", target_rec.get("research_area", "").lower()))
        
        new_title = set(re.findall(r"\w+", newly_published_rec.get("title", "").lower()))
        tgt_title = set(re.findall(r"\w+", target_rec.get("title", "").lower()))

        # Remove generic stopwords
        stopwords = {"and", "for", "in", "via", "of", "the", "a", "an", "with", "under", "systems", "system", "edge", "model"}
        new_area -= stopwords
        tgt_area -= stopwords
        new_title -= stopwords
        tgt_title -= stopwords

        area_overlap = new_area.intersection(tgt_area)
        title_overlap = new_title.intersection(tgt_title)

        # Check explicit citation dependency declaration in paper plan
        tgt_deps = target_rec.get("citation_dependencies", [])
        if newly_published_rec.get("paper_id") in tgt_deps or any(newly_published_rec.get("paper_id") in str(d) for d in tgt_deps):
            return "CRITICAL_DECLARED_DEPENDENCY (Direct architectural dependency in paper plan)"

        if len(area_overlap) >= 2 or len(title_overlap) >= 2:
            return f"HIGH (Domain overlap: {', '.join(area_overlap.union(title_overlap))})"
        elif len(area_overlap) >= 1 or len(title_overlap) >= 1:
            return f"MEDIUM (Shared topic: {', '.join(area_overlap.union(title_overlap))})"
        else:
            return "REVIEW_REQUIRED (Cross-stratum reference requires author justification)"

    def propagate_status_change(self, paper_id, new_status, date=None, venue=None, doi=None, source="Authoritative Project Record", force=False, dry_run=False):
        """
        Propagates a publication lifecycle transition.
        """
        if date is None:
            date = datetime.date.today().isoformat()

        with open(self.paper_registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        if paper_id not in registry:
            raise ValueError(f"Paper {paper_id} not found in paper registry.")

        old_status = registry[paper_id].get("status", "UNKNOWN")

        # Validate legal transition
        allowed_next = LEGAL_TRANSITIONS.get(old_status, [])
        if new_status not in allowed_next and not force and not dry_run:
            raise ValueError(f"Illegal state transition: {old_status} -> {new_status}. Allowed next states: {allowed_next}")

        # Set up before-and-after eligibility engines
        engine_before = CitationEligibilityEngine(self.paper_registry_path)
        
        # In-memory updated registry
        updated_registry = json.loads(json.dumps(registry))
        updated_registry[paper_id]["status"] = new_status
        if new_status == "PUBLISHED":
            updated_registry[paper_id]["publication_date"] = date
            if venue: updated_registry[paper_id]["venue"] = venue
            if doi: updated_registry[paper_id]["doi"] = doi
        elif new_status in ["ACCEPTED", "IN_PRESS"]:
            updated_registry[paper_id]["acceptance_date"] = date
            if venue: updated_registry[paper_id]["venue"] = venue

        engine_after = CitationEligibilityEngine(self.paper_registry_path)
        engine_after.registry = updated_registry

        # Evaluate portfolio citation opportunities
        opportunities = []
        newly_eligible = []
        already_eligible = []
        still_blocked = []

        for other_id, other_rec in updated_registry.items():
            if other_id == paper_id:
                continue

            elig_before = engine_before.evaluate_eligibility(other_id, paper_id)
            elig_after = engine_after.evaluate_eligibility(other_id, paper_id)

            was_blocked = elig_before["verdict"] in ["INVALID_FORWARD_REFERENCE", "STATUS_UNCERTAIN"]
            is_now_eligible = elig_after["verdict"] in ["VALID_PUBLISHED", "VALID_ACCEPTED_IN_PRESS"]

            relevance = self.evaluate_scientific_relevance(updated_registry[paper_id], other_rec)

            opp_record = {
                "newly_transitioned_paper": paper_id,
                "potential_citing_paper": other_id,
                "target_paper_title": other_rec.get("title", ""),
                "target_paper_area": other_rec.get("research_area", ""),
                "eligibility_before": elig_before["verdict"],
                "eligibility_after": elig_after["verdict"],
                "was_previously_blocked": was_blocked,
                "is_now_eligible": is_now_eligible,
                "is_newly_eligible": was_blocked and is_now_eligible,
                "scientific_relevance": relevance,
                "automatic_insertion": False, # Strict policy
                "recommendation": "Author review required before proposing citation."
            }

            opportunities.append(opp_record)
            if was_blocked and is_now_eligible:
                newly_eligible.append(opp_record)
            elif not was_blocked and is_now_eligible:
                already_eligible.append(opp_record)
            elif not is_now_eligible:
                still_blocked.append(opp_record)

        # Record publication event
        event_record = {
            "event_id": f"EVT-PUB-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "paper_id": paper_id,
            "event": new_status,
            "date": date,
            "venue": venue or updated_registry[paper_id].get("venue"),
            "doi": doi or updated_registry[paper_id].get("doi"),
            "source": source,
            "verification_status": "VERIFIED" if not dry_run else "SIMULATED"
        }

        # Update persistent registries if not dry run
        if not dry_run:
            with open(self.paper_registry_path, "w", encoding="utf-8") as f:
                json.dump(updated_registry, f, indent=2)

            with open(self.publication_events_path, "r", encoding="utf-8") as f:
                events = json.load(f)
            events.append(event_record)
            with open(self.publication_events_path, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2)

            # Save citation opportunities report
            with open(self.citation_opportunities_path, "w", encoding="utf-8") as f:
                json.dump({
                    "last_propagation_timestamp": datetime.datetime.now().isoformat(),
                    "transition": f"{paper_id}: {old_status} -> {new_status}",
                    "newly_eligible_count": len(newly_eligible),
                    "newly_eligible": newly_eligible,
                    "all_opportunities": opportunities
                }, f, indent=2)

        self._log_action("PROPAGATE_STATUS_CHANGE", paper_id, f"TRANSITION_TO_{new_status}", old_status, new_status, source, "SUCCESS", dry_run=dry_run)

        return {
            "paper_id": paper_id,
            "old_status": old_status,
            "new_status": new_status,
            "event_recorded": event_record,
            "is_dry_run": dry_run,
            "total_portfolio_evaluated": len(updated_registry),
            "newly_eligible_count": len(newly_eligible),
            "already_eligible_count": len(already_eligible),
            "still_blocked_count": len(still_blocked),
            "newly_eligible": newly_eligible,
            "all_opportunities": opportunities
        }

if __name__ == "__main__":
    prop = PublicationPropagationEngine()
    res = prop.propagate_status_change("P06", "PUBLISHED", date="2026-09-15", dry_run=True)
    print(f"Propagation dry run P06 -> PUBLISHED: {res['newly_eligible_count']} newly eligible citations.")
