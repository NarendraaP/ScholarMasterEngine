"""
Truthful Evidence Provenance & Classification Engine for ScholarMaster Research Governance
Derives evidence classification strictly from structured audit fields in EXPERIMENTAL_SCOPE_AUDIT.json.
Never uses keyword detection as proof of evidence classification.
Preserves AUDIT_DERIVED, SOURCE_VERIFIED, and REVIEW_REQUIRED statuses truthfully.
"""

import json, os

STRUCTURED_CLASS_MAP = {
    "PHYSICAL_HARDWARE_BENCHMARK": "PHYSICAL_MEASUREMENT",
    "SIMULATED_HARNESS": "SIMULATION",
    "ANALYTICAL_MODEL": "ANALYTICAL_DERIVATION",
    "STAGED_USER_DRILL": "USER_STUDY",
    "PHYSICAL_CLASSROOM_SURVEY": "USER_STUDY",
    "DEDUCTIVE_FORMAL_PROOFS": "FORMAL_PROOF",
    "MEASURE_THEORETIC_LOGIC": "FORMAL_PROOF",
    "META_SYSTEMS_SURVEY": "OTHER"
}

class EvidenceProvenanceTracker:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        else:
            self.root_dir = root_dir
            
        self.scope_audit_path = os.path.join(self.root_dir, "research_governance", "controlled_revision", "final_verification_v2", "EXPERIMENTAL_SCOPE_AUDIT.json")
        self.num_audit_path = os.path.join(self.root_dir, "research_governance", "controlled_revision", "final_verification_v2", "NUMERICAL_PROVENANCE_AUDIT.json")

    def build_evidence_registry(self):
        scope_audit = {}
        if os.path.exists(self.scope_audit_path):
            with open(self.scope_audit_path, "r", encoding="utf-8") as f:
                scope_audit = json.load(f)

        numerical_audit = []
        if os.path.exists(self.num_audit_path):
            with open(self.num_audit_path, "r", encoding="utf-8") as f:
                numerical_audit = json.load(f)

        evidence_records = []
        for idx, item in enumerate(numerical_audit):
            p_str = item["paper"]
            scope_info = scope_audit.get(p_str, {})
            
            raw_env = scope_info.get("environment_classification")
            
            if raw_env in STRUCTURED_CLASS_MAP:
                ev_class = STRUCTURED_CLASS_MAP[raw_env]
                class_method = "STRUCTURED_SOURCE_FIELD"
                v_status = "AUDIT_DERIVED"
            else:
                ev_class = "UNKNOWN"
                class_method = "MANUAL_REVIEW_REQUIRED"
                v_status = "REVIEW_REQUIRED"

            evidence_records.append({
                "evidence_id": f"EV-{p_str}-{idx+1:03d}",
                "paper": p_str,
                "evidence_class": ev_class,
                "classification_method": class_method,
                "verification_status": v_status,
                "description": item.get("numerical_claim", ""),
                "source_file": item.get("final_manuscript_location", "").split(":")[0] if ":" in item.get("final_manuscript_location", "") else item.get("final_manuscript_location", ""),
                "source_location": item.get("final_manuscript_location", ""),
                "pre_existing_evidence": item.get("pre_existing_evidence", True)
            })

        return evidence_records

    def build_claim_registry(self, evidence_records=None):
        if evidence_records is None:
            evidence_records = self.build_evidence_registry()

        claim_records = []
        for ev in evidence_records:
            # Preserve truthful audit status (no automatic promotion)
            if ev["verification_status"] == "AUDIT_DERIVED":
                clm_status = "AUDIT_DERIVED"
            elif ev["verification_status"] == "SOURCE_VERIFIED":
                clm_status = "SOURCE_VERIFIED"
            elif ev["verification_status"] == "REVIEW_REQUIRED":
                clm_status = "REVIEW_REQUIRED"
            else:
                clm_status = "UNVERIFIED"

            claim_records.append({
                "claim_id": f"CLM-{ev['evidence_id']}",
                "paper": ev["paper"],
                "claim": ev["description"],
                "evidence_ids": [ev["evidence_id"]],
                "scope": "Bounded to evaluated environment in EXPERIMENTAL_SCOPE_AUDIT.json",
                "limitations": "Subject to limitations disclosed in manuscript",
                "status": clm_status,
                "verification_procedure": "Cross-checked against EXPERIMENTAL_SCOPE_AUDIT.json and NUMERICAL_PROVENANCE_AUDIT.json"
            })

        return claim_records

if __name__ == "__main__":
    tracker = EvidenceProvenanceTracker()
    evs = tracker.build_evidence_registry()
    clms = tracker.build_claim_registry(evs)
    print("Evidence Records built:", len(evs))
    print("Claim Records built:", len(clms))
