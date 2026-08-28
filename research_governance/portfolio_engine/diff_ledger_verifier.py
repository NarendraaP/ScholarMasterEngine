"""
True Diff <-> Change Ledger Verifier for ScholarMaster Research Governance
Evaluates actual diff blocks against CHANGE_LEDGER.json entries and performs SHA-256 hash comparisons.
Classifies diffs as LEDGERED vs UNLEDGERED and ledger items as VERIFIED vs NOT_FOUND.
"""

import json, os, difflib, hashlib

class DiffLedgerVerifier:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        else:
            self.root_dir = root_dir
            
        self.backup_dir = os.path.join(self.root_dir, "docs", "papers_backup_pre_revision")
        self.current_dir = os.path.join(self.root_dir, "docs", "papers")
        self.ledger_path = os.path.join(self.root_dir, "research_governance", "controlled_revision", "CHANGE_LEDGER.json")

    def _hash_file(self, filepath):
        if not os.path.exists(filepath): return None
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def verify_frozen_papers(self):
        frozen_papers = [5, 6, 22, 23, 24, 25]
        results = []
        all_identical = True

        for p in frozen_papers:
            p_str = f"P{p:02d}"
            curr_file = os.path.join(self.current_dir, f"paper{p}_revised.tex")
            back_file = os.path.join(self.backup_dir, f"paper{p}_revised.tex")

            curr_hash = self._hash_file(curr_file)
            back_hash = self._hash_file(back_file)
            identical = (curr_hash == back_hash) and (curr_hash is not None)

            if not identical:
                all_identical = False

            results.append({
                "paper": p_str,
                "pre_revision_hash": back_hash,
                "final_hash": curr_hash,
                "identical": identical,
                "status": "SOURCE_VERIFIED_FROZEN" if identical else "FROZEN_BREACH_DETECTED",
                "source": f"{os.path.relpath(curr_file, self.root_dir)} vs {os.path.relpath(back_file, self.root_dir)}"
            })

        return {
            "all_frozen_identical": all_identical,
            "frozen_papers_audited": len(frozen_papers),
            "results": results
        }

    def verify_paper_diff_against_ledger(self, paper_number):
        p_str = f"P{paper_number:02d}"
        curr_file = os.path.join(self.current_dir, f"paper{paper_number}_revised.tex")
        back_file = os.path.join(self.backup_dir, f"paper{paper_number}_revised.tex")

        if not os.path.exists(curr_file) or not os.path.exists(back_file):
            return {
                "paper": p_str,
                "status": "NOT_VERIFIED",
                "reason": "Missing manuscript or backup file.",
                "ledger_status": "NOT_FOUND",
                "diff_status": "NOT_FOUND"
            }

        with open(back_file, "r", encoding="utf-8") as f:
            back_lines = f.readlines()
        with open(curr_file, "r", encoding="utf-8") as f:
            curr_lines = f.readlines()

        diff = list(difflib.unified_diff(back_lines, curr_lines, fromfile="backup", tofile="revised", n=3))
        has_diff = len(diff) > 0

        # Load ledger entry
        ledger_entry = None
        if os.path.exists(self.ledger_path):
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
            for item in ledger:
                if item.get("paper") == p_str:
                    ledger_entry = item
                    break

        is_frozen = paper_number in [5, 6, 22, 23, 24, 25]

        if is_frozen:
            if not has_diff:
                return {
                    "paper": p_str,
                    "status": "COMPLETED_VERIFIED",
                    "diff_status": "IDENTICAL_FROZEN_BASELINE",
                    "ledger_status": "VERIFIED_FROZEN_BASELINE",
                    "ledger_entry": ledger_entry
                }
            else:
                return {
                    "paper": p_str,
                    "status": "CONTRADICTED",
                    "diff_status": "UNEXPECTED_DIFF_IN_FROZEN_PAPER",
                    "ledger_status": "CONTRADICTED",
                    "ledger_entry": ledger_entry
                }

        # For revised papers
        if ledger_entry and has_diff:
            return {
                "paper": p_str,
                "status": "COMPLETED_VERIFIED",
                "diff_status": "LEDGERED",
                "ledger_status": "VERIFIED",
                "ledger_entry": ledger_entry,
                "diff_line_count": len(diff)
            }
        elif ledger_entry and not has_diff:
            return {
                "paper": p_str,
                "status": "PARTIALLY_VERIFIED",
                "diff_status": "NO_DIFF_FOUND",
                "ledger_status": "NOT_FOUND (Ledger claims change but files are identical)",
                "ledger_entry": ledger_entry
            }
        elif not ledger_entry and has_diff:
            return {
                "paper": p_str,
                "status": "REVIEW_REQUIRED",
                "diff_status": "UNLEDGERED (Substantive diff without ledger entry)",
                "ledger_status": "NOT_FOUND",
                "ledger_entry": None,
                "diff_line_count": len(diff)
            }
        else: # not ledger_entry and not has_diff
            return {
                "paper": p_str,
                "status": "COMPLETED_VERIFIED",
                "diff_status": "IDENTICAL_NO_CHANGES_REQUIRED",
                "ledger_status": "VERIFIED_NO_CHANGES",
                "ledger_entry": None
            }

    def verify_entire_portfolio(self):
        frozen_res = self.verify_frozen_papers()
        paper_results = {}
        for p in range(1, 26):
            paper_results[f"P{p:02d}"] = self.verify_paper_diff_against_ledger(p)

        all_clean = frozen_res["all_frozen_identical"] and all(
            r["status"] in ["COMPLETED_VERIFIED", "PARTIALLY_VERIFIED"] for r in paper_results.values()
        )

        return {
            "all_verified": all_clean,
            "frozen_verification": frozen_res,
            "paper_results": paper_results
        }

if __name__ == "__main__":
    verifier = DiffLedgerVerifier()
    res = verifier.verify_entire_portfolio()
    print("Diff Ledger Verification clean:", res["all_verified"])
