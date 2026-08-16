#!/usr/bin/env python3
"""
Pre-Edit Verification Script for ScholarMaster Math Correction Execution
"""
import hashlib
import json

def get_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

files_to_hash = {
    "paper24_tex": "docs/papers/paper24_revised.tex",
    "paper25_tex": "docs/papers/paper25_revised.tex",
    "paper22_tex": "docs/papers/paper22_revised.tex",
    "paper23_tex": "docs/papers/paper23_revised.tex",
    "master_validation_json": "benchmarks/master_validation_suite_results.json"
}

hashes = {k: {"path": v, "sha256": get_sha256(v)} for k, v in files_to_hash.items()}
print("PRE-EDIT SHA256 HASHES:")
print(json.dumps(hashes, indent=2))

with open("benchmarks/pre_edit_hashes.json", "w") as f:
    json.dump(hashes, f, indent=2)
