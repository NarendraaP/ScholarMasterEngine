"""
Hardened Future Paper Registration Engine for ScholarMaster Research Governance
Initializes all canonical registries with explicit TBD/NOT_DECLARED placeholders.
"""

import json, os, datetime

class PaperRegistrationEngine:
    def __init__(self, data_dir=None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
        
        self.data_dir = data_dir
        self.paper_registry_path = os.path.join(data_dir, "paper_registry.json")
        self.novelty_registry_path = os.path.join(data_dir, "novelty_registry.json")
        self.venue_registry_path = os.path.join(data_dir, "venue_registry.json")
        self.evidence_registry_path = os.path.join(data_dir, "evidence_registry.json")
        self.claim_registry_path = os.path.join(data_dir, "claim_registry.json")
        self.revision_registry_path = os.path.join(data_dir, "revision_registry.json")
        self.audit_log_path = os.path.join(os.path.dirname(data_dir), "engine_audit_log.jsonl")

    def register_new_paper(self, paper_id, title, research_area, paper_type="SYSTEMS", target_venue_primary="IEEE Transactions", target_venues_alternative=None, status="PLANNED", manuscript_path=None, dry_run=False):
        with open(self.paper_registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        if paper_id in registry:
            raise ValueError(f"Paper ID {paper_id} already exists in canonical registry.")

        existing_orders = [p.get("research_plan_order", 0) for p in registry.values() if isinstance(p.get("research_plan_order"), int)]
        next_order = max(existing_orders) + 1 if existing_orders else 1

        new_record = {
            "paper_id": paper_id,
            "paper_number": next_order,
            "title": title,
            "paper_type": paper_type,
            "research_area": research_area,
            "status": status,
            "publication_date": None,
            "acceptance_date": None,
            "submission_date": None,
            "draft_date": datetime.date.today().isoformat(),
            "venue": target_venue_primary,
            "doi": None,
            "authors": None, # Strict: no guessing
            "manuscript_path": manuscript_path or f"docs/papers/{paper_id.lower()}_revised.tex",
            "pdf_path": f"docs/papers/{paper_id.lower()}_revised.pdf",
            "plan_path": "research_governance/master_paper_plan/generated/PAPER_RECORDS.json",
            "evidence_path": "research_governance/portfolio_engine/data/evidence_registry.json",
            "contribution_owner": True,
            "citation_aliases": [f"Paper {next_order}", f"scholar{next_order}"],
            "research_plan_order": next_order,
            "submission_order": None,
            "acceptance_order": None,
            "publication_order": None,
            "provenance": {
                "source": "register_paper.py CLI / API Registration",
                "verification_status": "REGISTERED_DRAFT",
                "last_verified": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        }

        if not dry_run:
            registry[paper_id] = new_record
            with open(self.paper_registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)

            # Initialize Novelty Registry entry
            if os.path.exists(self.novelty_registry_path):
                with open(self.novelty_registry_path, "r", encoding="utf-8") as f:
                    nov_reg = json.load(f)
                nov_reg[paper_id] = {
                    "paper_id": paper_id,
                    "known_components": "TBD (To be declared upon manuscript completion)",
                    "paper_specific_contribution": "TBD (To be declared)",
                    "novelty_argument": "TBD (To be declared)",
                    "theorems": "TBD",
                    "remaining_novelty_risk": "REVIEW_REQUIRED"
                }
                with open(self.novelty_registry_path, "w", encoding="utf-8") as f:
                    json.dump(nov_reg, f, indent=2)

            # Initialize Venue Registry entry
            if os.path.exists(self.venue_registry_path):
                with open(self.venue_registry_path, "r", encoding="utf-8") as f:
                    v_reg = json.load(f)
                v_reg[paper_id] = {
                    "paper_id": paper_id,
                    "primary_venue": target_venue_primary,
                    "alternative_venues": target_venues_alternative or "TBD",
                    "venue_fit": f"Disciplinary alignment for {paper_type} in {research_area}",
                    "evidence_expectations": "Transactions-level rigor",
                    "known_risks": "REVIEW_REQUIRED"
                }
                with open(self.venue_registry_path, "w", encoding="utf-8") as f:
                    json.dump(v_reg, f, indent=2)

            # Initialize Revision Registry entry
            if os.path.exists(self.revision_registry_path):
                with open(self.revision_registry_path, "r", encoding="utf-8") as f:
                    rev_reg = json.load(f)
                rev_reg.append({
                    "revision_id": f"REV-{paper_id}-001",
                    "paper": paper_id,
                    "issue": "Initial paper onboarding",
                    "severity": "LOW",
                    "revision_type": "INITIAL_REGISTRATION",
                    "status": "PLANNED",
                    "evidence_source": "Registration CLI",
                    "requires_experiment": True,
                    "requires_hardware": False,
                    "requires_author_decision": True
                })
                with open(self.revision_registry_path, "w", encoding="utf-8") as f:
                    json.dump(rev_reg, f, indent=2)

            # Log audit trail
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "command": "REGISTER_NEW_PAPER",
                "paper": paper_id,
                "action": "CREATE_PAPER_RECORD",
                "old_state": None,
                "new_state": status,
                "source": "register_paper.py",
                "operator_mode": "LIVE_EXECUTION",
                "result": "SUCCESS"
            }
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        return {
            "paper_id": paper_id,
            "status": "REGISTERED" if not dry_run else "SIMULATED_REGISTRATION",
            "record": new_record
        }

if __name__ == "__main__":
    reg = PaperRegistrationEngine()
    res = reg.register_new_paper("P26", "Test Paper", "Systems", dry_run=True)
    print("Dry run register P26:", res["status"])
