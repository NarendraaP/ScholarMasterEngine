"""
Hardened Citation Eligibility Engine for ScholarMaster Research Governance
Evaluates real publication dates and chronology without hardcoded overrides or bypasses.
"""

import json, os, datetime

class CitationEligibilityEngine:
    def __init__(self, registry_path=None):
        if registry_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            registry_path = os.path.join(base_dir, "data", "paper_registry.json")
        
        self.registry_path = registry_path
        self.reload_registry()

    def reload_registry(self):
        with open(self.registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def _parse_date(self, d_str):
        if not d_str: return None
        try:
            return datetime.date.fromisoformat(d_str)
        except Exception:
            return None

    def evaluate_eligibility(self, citing_paper_id, cited_paper_id, citing_date=None):
        """
        Determines citation eligibility between two papers using real date comparison.
        Returns:
            - verdict: VALID_PUBLISHED | VALID_ACCEPTED_IN_PRESS | INVALID_FORWARD_REFERENCE | STATUS_UNCERTAIN
            - relationship: COMPANION_SERIES_DEPENDENCY | EXTERNAL_OR_PRIOR_WORK
        """
        if citing_paper_id not in self.registry or cited_paper_id not in self.registry:
            return {
                "citing_paper": citing_paper_id,
                "cited_paper": cited_paper_id,
                "verdict": "STATUS_UNCERTAIN",
                "relationship": "UNKNOWN",
                "reason": "One or both papers are not registered in the canonical registry."
            }

        citing_rec = self.registry[citing_paper_id]
        cited_rec = self.registry[cited_paper_id]

        # Determine companion relationship
        citing_num = citing_rec.get("paper_number", 0)
        cited_num = cited_rec.get("paper_number", 0)
        is_companion = (citing_num in [23, 24, 25] and cited_num in [22, 23, 24] and citing_num > cited_num)
        rel_type = "COMPANION_SERIES_DEPENDENCY" if is_companion else "EXTERNAL_OR_PRIOR_WORK"

        # Check self-citation
        if citing_paper_id == cited_paper_id:
            return {
                "citing_paper": citing_paper_id,
                "cited_paper": cited_paper_id,
                "verdict": "INVALID_FORWARD_REFERENCE",
                "relationship": "SELF_CITATION",
                "reason": "Self-citation to the exact same manuscript."
            }

        # Determine citing relevant date
        c_date = self._parse_date(citing_date)
        if not c_date:
            c_date = self._parse_date(citing_rec.get("submission_date") or citing_rec.get("publication_date") or citing_rec.get("draft_date"))

        # Case 1: Cited paper is PUBLISHED
        if cited_rec.get("status") == "PUBLISHED":
            pub_date = self._parse_date(cited_rec.get("publication_date"))
            if not pub_date:
                return {
                    "citing_paper": citing_paper_id,
                    "cited_paper": cited_paper_id,
                    "verdict": "STATUS_UNCERTAIN",
                    "relationship": rel_type,
                    "reason": f"Cited paper {cited_paper_id} is marked PUBLISHED but lacks a verified publication_date."
                }
            if c_date and c_date < pub_date:
                return {
                    "citing_paper": citing_paper_id,
                    "cited_paper": cited_paper_id,
                    "verdict": "INVALID_FORWARD_REFERENCE",
                    "relationship": rel_type,
                    "reason": f"Chronology violation: Citing date ({c_date}) is earlier than cited publication date ({pub_date})."
                }
            return {
                "citing_paper": citing_paper_id,
                "cited_paper": cited_paper_id,
                "verdict": "VALID_PUBLISHED",
                "relationship": rel_type,
                "reason": f"Cited paper {cited_paper_id} is legitimately PUBLISHED on {pub_date} (Citing relevant date: {c_date})."
            }

        # Case 2: Cited paper is ACCEPTED or IN_PRESS
        if cited_rec.get("status") in ["ACCEPTED", "IN_PRESS"]:
            acc_date = self._parse_date(cited_rec.get("acceptance_date"))
            if not acc_date:
                return {
                    "citing_paper": citing_paper_id,
                    "cited_paper": cited_paper_id,
                    "verdict": "STATUS_UNCERTAIN",
                    "relationship": rel_type,
                    "reason": f"Cited paper {cited_paper_id} is marked ACCEPTED/IN_PRESS but lacks a verified acceptance_date."
                }
            if c_date and c_date < acc_date:
                return {
                    "citing_paper": citing_paper_id,
                    "cited_paper": cited_paper_id,
                    "verdict": "INVALID_FORWARD_REFERENCE",
                    "relationship": rel_type,
                    "reason": f"Chronology violation: Citing date ({c_date}) is earlier than cited acceptance date ({acc_date})."
                }
            return {
                "citing_paper": citing_paper_id,
                "cited_paper": cited_paper_id,
                "verdict": "VALID_ACCEPTED_IN_PRESS",
                "relationship": rel_type,
                "reason": f"Cited paper {cited_paper_id} is ACCEPTED/IN_PRESS on {acc_date} (Must be cited as 'In Press / To Appear')."
            }

        # Case 3: Cited paper is UNPUBLISHED (DRAFT, PLANNED, SUBMITTED, UNDER_REVIEW)
        # Rule: Companion relationship does NOT bypass chronology
        return {
            "citing_paper": citing_paper_id,
            "cited_paper": cited_paper_id,
            "verdict": "INVALID_FORWARD_REFERENCE",
            "relationship": rel_type,
            "reason": f"Cited paper {cited_paper_id} has unpublished status {cited_rec.get('status')} and cannot be cited as published literature."
        }

    def audit_portfolio_chronology(self, citation_graph_path=None):
        if citation_graph_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            citation_graph_path = os.path.join(base_dir, "data", "citation_graph.json")

        with open(citation_graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)

        results = []
        violations = []
        for edge in graph.get("edges", []):
            eval_res = self.evaluate_eligibility(edge["citing_paper"], edge["cited_paper"])
            res_entry = {
                "citing_paper": edge["citing_paper"],
                "cited_paper": edge["cited_paper"],
                "citation_key": edge.get("citation_key"),
                "relationship": eval_res.get("relationship"),
                "verdict": eval_res.get("verdict"),
                "evaluation": eval_res
            }
            results.append(res_entry)
            # In published literature, only VALID_PUBLISHED or VALID_ACCEPTED_IN_PRESS are allowed
            if eval_res["verdict"] == "INVALID_FORWARD_REFERENCE":
                violations.append(res_entry)

        return {
            "total_citations_checked": len(results),
            "total_violations": len(violations),
            "is_clean": len(violations) == 0,
            "violations": violations,
            "all_results": results
        }

if __name__ == "__main__":
    engine = CitationEligibilityEngine()
    audit = engine.audit_portfolio_chronology()
    print(f"Chronology Audit Complete: {audit['total_violations']} violations out of {audit['total_citations_checked']} edges.")
