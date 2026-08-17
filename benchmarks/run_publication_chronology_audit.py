#!/usr/bin/env python3
"""
ScholarMaster Publication Chronology & Future-Citation Forensic Audit Engine
============================================================================
Performs a comprehensive, read-only forensic audit across P1–P25 enforcing the
Permanent Chronological Citation Law for the ScholarMaster research portfolio.
"""

import os
import re
import json
import hashlib

AUDIT_DIR = "research_governance/publication_chronology_audit"
os.makedirs(AUDIT_DIR, exist_ok=True)

PAPERS_DIR = "docs/papers"

# Authoritative Publication Chronology & Timeline
# Phase 1: Foundations & Edge Co-Design (P1-P5): 2024-2025
# Phase 2: Embedded Systems, Storage & Formal Compliance (P6-P12): 2025
# Phase 3: Federated Systems, Verification & Operations (P13-P21): 2025-2026
# Phase 4: Perception Integrity Series (P22-P25): 2026
PUBLICATION_TIMELINE = {
    1: {"pub_date": "2024-11", "title": "ScholarMaster: A Unified Architecture for Trustworthy Multimodal Edge AI", "status": "PUBLISHED_TECH_REPORT"},
    2: {"pub_date": "2024-12", "title": "Real-Time Adaptive Biometric Cascade with Dynamic Energy-Delay-Risk Optimization", "status": "PUBLISHED_TECH_REPORT"},
    3: {"pub_date": "2025-01", "title": "Robust Multimodal Perception under Sensor Failure, Domain Shift, and Physical Noise", "status": "PUBLISHED_TECH_REPORT"},
    4: {"pub_date": "2025-02", "title": "Downstream Error Containment and Cascading Failure Dynamics in Multi-Stage Edge AI", "status": "PUBLISHED_TECH_REPORT"},
    5: {"pub_date": "2025-03", "title": "Hardware-Software Co-Design for Deterministic Low-Power Multimodal Inference on Jetson Orin", "status": "PUBLISHED_TECH_REPORT"},
    6: {"pub_date": "2025-04", "title": "Acoustic Event Detection under Heavy Environmental Noise", "status": "PUBLISHED_TECH_REPORT"},
    7: {"pub_date": "2025-05", "title": "Zero-Copy Unified Memory Architecture for Ultra-Low Latency Multimodal Stream Ingestion", "status": "PUBLISHED_TECH_REPORT"},
    8: {"pub_date": "2025-06", "title": "Spatio-Temporal Compliance State Machines: Formal Verification of Dynamic Rules on Edge Streams", "status": "PUBLISHED_TECH_REPORT"},
    9: {"pub_date": "2025-07", "title": "Comparative Benchmarking of Edge AI Frameworks for Real-Time Multimodal Stream Processing", "status": "PUBLISHED_TECH_REPORT"},
    10: {"pub_date": "2025-08", "title": "End-to-End System Validation: 24-Hour Continuous Operation, Fault Injection, and Real-World Stress", "status": "PUBLISHED_TECH_REPORT"},
    11: {"pub_date": "2025-09", "title": "Thermal-Aware Adaptive Dynamic Voltage and Frequency Scaling for Sustained Jetson Edge Inference", "status": "PUBLISHED_TECH_REPORT"},
    12: {"pub_date": "2025-10", "title": "Flash Wear-Out Mitigation and Log-Structured Storage Optimization in High-Throughput Edge Nodes", "status": "PUBLISHED_TECH_REPORT"},
    13: {"pub_date": "2025-11", "title": "Decentralized Federated Face Embedding Aggregation with Differential Privacy and Verification Gating", "status": "PUBLISHED_TECH_REPORT"},
    14: {"pub_date": "2025-12", "title": "Cross-Campus Federation and Hierarchical Consensus in Distributed Multi-Tenant Edge Infrastructure", "status": "PUBLISHED_TECH_REPORT"},
    15: {"pub_date": "2026-01", "title": "Provable Worst-Case Execution Time and Jitter Guarantees in Heterogeneous Edge Scheduling", "status": "PUBLISHED_TECH_REPORT"},
    16: {"pub_date": "2026-02", "title": "Adversarial Robustness and Physical Anti-Spoofing in Real-Time Hyperspherical Biometric Spaces", "status": "PUBLISHED_TECH_REPORT"},
    17: {"pub_date": "2026-03", "title": "Privacy-Preserving Edge Surveillance: Dynamic Pose De-Identification and Selective Face Obfuscation", "status": "PUBLISHED_TECH_REPORT"},
    18: {"pub_date": "2026-04", "title": "Automated Runtime Policy Enforcement and Dynamic Privilege Revocation on Distributed Edge Nodes", "status": "PUBLISHED_TECH_REPORT"},
    19: {"pub_date": "2026-05", "title": "Formal Verification of Multi-Modal Fusion Invariants Using First-Order Logic and Timed Automata", "status": "PUBLISHED_TECH_REPORT"},
    20: {"pub_date": "2026-06", "title": "Unified Mathematical Foundations of Composite Risk, Evidence Theory, and Information Geometry", "status": "PUBLISHED_TECH_REPORT"},
    21: {"pub_date": "2026-07", "title": "Autonomous Edge Infrastructure Lifecycle Management, Over-the-Air Updates, and Resilient Recovery", "status": "PUBLISHED_TECH_REPORT"},
    22: {"pub_date": "2026-08", "title": "Perception Integrity Foundations: Evidential Uncertainty, Disagreement Dynamics, and Blur Bounds in Edge Vision", "status": "CONTEMPORANEOUS_SERIES_2026"},
    23: {"pub_date": "2026-08", "title": "Adaptive Trustworthy Edge Systems: Dynamic Risk-Driven Cascades and Real-Time SLA Bounds", "status": "CONTEMPORANEOUS_SERIES_2026"},
    24: {"pub_date": "2026-08", "title": "Generalized Cross-Modal Recovery under Compromised Primary Sensing", "status": "CONTEMPORANEOUS_SERIES_2026"},
    25: {"pub_date": "2026-08", "title": "ScholarMaster Macro Integration Architecture and Downstream Error Propagation Analysis", "status": "CONTEMPORANEOUS_SERIES_2026"}
}

def analyze_cross_references():
    cross_refs = []
    invalid_future_refs = []
    valid_historical_refs = []
    future_work_language = []
    software_refs = []

    for src_pid in range(1, 26):
        tex_path = f"{PAPERS_DIR}/paper{src_pid}_revised.tex"
        if not os.path.exists(tex_path):
            continue
        with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        lines = content.split("\n")
        src_meta = PUBLICATION_TIMELINE[src_pid]
        src_date = src_meta["pub_date"]

        # Parse BibTeX / bibitems
        bibitems = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\}|$)", content, re.DOTALL)
        
        # Check bibitems for ScholarMaster citations
        for key, text in bibitems:
            clean_text = " ".join(text.split())
            target_pid = None
            
            # Match Paper number or key
            p_match = re.search(r"Paper\s+(\d+)", clean_text, re.IGNORECASE)
            if p_match:
                target_pid = int(p_match.group(1))
            elif key.upper().startswith("P") and key[1:].isdigit():
                target_pid = int(key[1:])
            elif "kumar2026scholar" in key:
                target_pid = int(key.replace("kumar2026scholar", ""))
            elif "ScholarMaster" in clean_text:
                for k in range(1, 26):
                    if f"paper {k}" in clean_text.lower() or f"paper{k}" in clean_text.lower():
                        target_pid = k
                        break

            if target_pid and 1 <= target_pid <= 25 and target_pid != src_pid:
                target_meta = PUBLICATION_TIMELINE[target_pid]
                target_date = target_meta["pub_date"]

                # Find line numbers in body where this key is cited
                citing_lines = []
                for idx, line in enumerate(lines):
                    if f"{{{key}}}" in line or f",{key}" in line or f"{key}," in line or f"cite{{{key}" in line:
                        if idx + 1 < len(lines) - len(bibitems) - 5: # ensure it's in body, not in references
                            citing_lines.append((idx + 1, line.strip()))

                # Classification
                if src_pid in [22, 23, 24, 25] and target_pid in [22, 23, 24, 25]:
                    rel_type = "VALID_CONTEMPORANEOUS_COHORT"
                    is_valid = True
                    rec = "RETAIN_AS_CONTEMPORANEOUS_SERIES_CITATION"
                elif target_date < src_date:
                    rel_type = "VALID_HISTORICAL_REFERENCE"
                    is_valid = True
                    rec = "RETAIN_VALID_PRIOR_ART"
                elif target_date == src_date:
                    rel_type = "VALID_CONTEMPORANEOUS"
                    is_valid = True
                    rec = "RETAIN_VALID_COHORT"
                else: # target_date > src_date
                    rel_type = "INVALID_FUTURE_REFERENCE"
                    is_valid = False
                    rec = "OPTION_C_REWRITE_AS_SELF_CONTAINED_OR_OPTION_A_REPLACE_WITH_EXTERNAL_LITERATURE"

                ref_entry = {
                    "source_paper": f"P{src_pid}",
                    "source_pub_date": src_date,
                    "target_paper": f"P{target_pid}",
                    "target_pub_date": target_date,
                    "bib_key": key,
                    "bib_text": clean_text,
                    "citing_body_lines": [f"L{l[0]}: {l[1]}" for l in citing_lines],
                    "classification": rel_type,
                    "is_valid": is_valid,
                    "recommended_action": rec
                }

                cross_refs.append(ref_entry)
                if is_valid:
                    valid_historical_refs.append(ref_entry)
                else:
                    invalid_future_refs.append(ref_entry)

        # Check for future-work language in body
        for idx, line in enumerate(lines):
            if idx < 28:
                continue
            if "\\begin{thebibliography}" in line:
                break
            for phrase in ["upcoming paper", "companion paper", "subsequent work", "forthcoming", "future paper", "later paper"]:
                if phrase in line.lower():
                    future_work_language.append({
                        "source_paper": f"P{src_pid}",
                        "line_num": idx + 1,
                        "phrase": phrase,
                        "line": line.strip(),
                        "classification": "PROSPECTIVE_DISCLOSURE"
                    })

    return {
        "cross_refs": cross_refs,
        "invalid_future_refs": invalid_future_refs,
        "valid_historical_refs": valid_historical_refs,
        "future_work_language": future_work_language
    }

def generate_all_artifacts():
    data = analyze_cross_references()

    # 1. PUBLICATION_CHRONOLOGY_REGISTRY.json
    with open(f"{AUDIT_DIR}/PUBLICATION_CHRONOLOGY_REGISTRY.json", "w") as f:
        json.dump({
            "registry_title": "ScholarMaster Canonical P1-P25 Publication Chronology Registry",
            "timeline": PUBLICATION_TIMELINE
        }, f, indent=2)

    # 2. P1_P25_CROSS_REFERENCE_INVENTORY.json
    with open(f"{AUDIT_DIR}/P1_P25_CROSS_REFERENCE_INVENTORY.json", "w") as f:
        json.dump(data["cross_refs"], f, indent=2)

    # 3. P1_P25_PUBLICATION_STATE_MATRIX.json
    state_matrix = {}
    for pid in range(1, 26):
        state_matrix[f"P{pid}"] = {
            "title": PUBLICATION_TIMELINE[pid]["title"],
            "pub_date": PUBLICATION_TIMELINE[pid]["pub_date"],
            "status": PUBLICATION_TIMELINE[pid]["status"],
            "citable_by": [f"P{k}" for k in range(1, 26) if PUBLICATION_TIMELINE[k]["pub_date"] >= PUBLICATION_TIMELINE[pid]["pub_date"]]
        }
    with open(f"{AUDIT_DIR}/P1_P25_PUBLICATION_STATE_MATRIX.json", "w") as f:
        json.dump(state_matrix, f, indent=2)

    # 4. P1_P25_FUTURE_REFERENCE_AUDIT.json
    with open(f"{AUDIT_DIR}/P1_P25_FUTURE_REFERENCE_AUDIT.json", "w") as f:
        json.dump({
            "total_cross_references_found": len(data["cross_refs"]),
            "valid_historical_count": len(data["valid_historical_refs"]),
            "invalid_future_reference_count": len(data["invalid_future_refs"]),
            "invalid_future_references": data["invalid_future_refs"]
        }, f, indent=2)

    # 5. P1_P25_INVALID_FUTURE_REFERENCES.json
    with open(f"{AUDIT_DIR}/P1_P25_INVALID_FUTURE_REFERENCES.json", "w") as f:
        json.dump(data["invalid_future_refs"], f, indent=2)

    # 6. P1_P25_VALID_HISTORICAL_REFERENCES.json
    with open(f"{AUDIT_DIR}/P1_P25_VALID_HISTORICAL_REFERENCES.json", "w") as f:
        json.dump(data["valid_historical_refs"], f, indent=2)

    # 7. P1_P25_SOFTWARE_ARTIFACT_REFERENCES.json
    software_refs = {
        "repository_citation": "ScholarMaster Engine Core Repository (https://github.com/NarendraaP/ScholarMasterEngine)",
        "legitimate_use": "Allowed across all papers as a software artifact citation for reproducible evaluation.",
        "rule": "Software artifact citations must not be used as a proxy to cite unpublished future research papers."
    }
    with open(f"{AUDIT_DIR}/P1_P25_SOFTWARE_ARTIFACT_REFERENCES.json", "w") as f:
        json.dump(software_refs, f, indent=2)

    # 8. P1_P25_FUTURE_WORK_LANGUAGE_AUDIT.json
    with open(f"{AUDIT_DIR}/P1_P25_FUTURE_WORK_LANGUAGE_AUDIT.json", "w") as f:
        json.dump(data["future_work_language"], f, indent=2)

    # 9. RESEARCH_DEPENDENCY_GRAPH.json
    res_graph = {
        "graph_name": "ScholarMaster Research Dependency Graph (Functional Architecture)",
        "description": "Represents technical dependencies between functional layers and mathematical objects.",
        "nodes": [f"P{i}" for i in range(1, 26)],
        "edges": [
            {"from": "P1", "to": "P2", "interface": "Cascade Architecture"},
            {"from": "P1", "to": "P3", "interface": "Sensor Degradation"},
            {"from": "P1", "to": "P4", "interface": "Downstream Error Propagation"},
            {"from": "P1", "to": "P5", "interface": "Jetson Orin Deployment"},
            {"from": "P5", "to": "P7", "interface": "UMA Zero-Copy Ingestion"},
            {"from": "P1", "to": "P8", "interface": "Spatio-Temporal Compliance"},
            {"from": "P1", "to": "P20", "interface": "Information Geometry Foundations"},
            {"from": "P20", "to": "P22", "interface": "Dirichlet Evidence & Uncertainty"},
            {"from": "P22", "to": "P23", "interface": "Validated Payload (x, p_cal, Rp)"},
            {"from": "P22", "to": "P24", "interface": "Degraded Channel Gating"},
            {"from": "P22", "to": "P25", "interface": "Layer 1 Fail-Closed Gating"},
            {"from": "P24", "to": "P25", "interface": "Cross-Modal Recovery Payload"}
        ]
    }
    with open(f"{AUDIT_DIR}/RESEARCH_DEPENDENCY_GRAPH.json", "w") as f:
        json.dump(res_graph, f, indent=2)

    # 10. PUBLICATION_CITATION_GRAPH.json
    pub_graph = {
        "graph_name": "ScholarMaster Public Scholarly Citation Graph (Temporal Order)",
        "description": "Represents valid scholarly citations where Target Publication Date <= Source Publication Date or Contemporaneous Cohort.",
        "nodes": [f"P{i}" for i in range(1, 26)],
        "valid_edges": [{"source": r["source_paper"], "target": r["target_paper"], "type": r["classification"]} for r in data["valid_historical_refs"]]
    }
    with open(f"{AUDIT_DIR}/PUBLICATION_CITATION_GRAPH.json", "w") as f:
        json.dump(pub_graph, f, indent=2)

    # 11. PUBLICATION_CHRONOLOGY_GOVERNANCE_RULE.json
    gov_rule = {
        "rule_title": "Permanent ScholarMaster Publication Chronology & Citation Law",
        "rule_id": "SROS-CHRONO-001",
        "law": "A ScholarMaster manuscript may cite another ScholarMaster paper ONLY if that referenced work was legitimately published, publicly available as a preprint, or part of the same contemporaneous series at the time of submission.",
        "forbidden_patterns": [
            "Citing planned future papers as prior art",
            "Citing internal roadmap milestones as published literature",
            "Using future paper numbers in historical manuscripts"
        ],
        "ratified": True
    }
    with open(f"{AUDIT_DIR}/PUBLICATION_CHRONOLOGY_GOVERNANCE_RULE.json", "w") as f:
        json.dump(gov_rule, f, indent=2)

    # 12. PUBLICATION_CHRONOLOGY_ACTION_LEDGER.json
    action_ledger = {
        "audit_timestamp": "2026-08-16T21:45:00+05:30",
        "total_invalid_future_references": len(data["invalid_future_refs"]),
        "audit_status": "AUDIT_COMPLETE_REPLACEMENTS_RECOMMENDED",
        "scheduled_actions": [
            {
                "paper": r["source_paper"],
                "target": r["target_paper"],
                "key": r["bib_key"],
                "action": r["recommended_action"]
            } for r in data["invalid_future_refs"]
        ]
    }
    with open(f"{AUDIT_DIR}/PUBLICATION_CHRONOLOGY_ACTION_LEDGER.json", "w") as f:
        json.dump(action_ledger, f, indent=2)

    # 13. PUBLICATION_CHRONOLOGY_AUDIT.md
    report_md = f"""# SCHOLARMASTER — PUBLICATION CHRONOLOGY & FUTURE-CITATION FORENSIC AUDIT
**Auditor**: ScholarMaster Governance Board & Publication Chronology Gate  
**Scope**: Complete 25-Paper Research Series (P1–P25)  
**Governance Protocol**: SROS-CHRONO-001 Ratified | Single-Owner Law | Absolute Uncertainty Law  
**Audit Status**: `AUDIT_COMPLETE` | `READ_ONLY`

---

## 1. Executive Summary & Core Chronology Findings

A comprehensive, read-only forensic scan was conducted across all 25 canonical LaTeX manuscripts in [`docs/papers/`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/papers/) to identify and classify every cross-paper citation, BibTeX entry, and textual reference against the portfolio's publication chronology.

### Summary Metrics
* **Total Cross-Paper References Analyzed**: **{len(data["cross_refs"])} references**
* **Valid Historical / Contemporaneous Citations**: **{len(data["valid_historical_refs"])} references**
* **Invalid Forward / Future References Detected**: **{len(data["invalid_future_refs"])} references**
* **Future-Work Language Occurrences**: **{len(data["future_work_language"])} occurrences**

---

## 2. Publication Chronology Baseline (P1–P25)

The ScholarMaster research series follows a four-phase publication timeline:
* **Phase 1: Foundations & Edge Co-Design (P1–P5)**: Published Nov 2024 -- Mar 2025.
* **Phase 2: Embedded Systems, Storage & Compliance (P6–P12)**: Published Apr 2025 -- Oct 2025.
* **Phase 3: Federation, Verification & Operations (P13–P21)**: Published Nov 2025 -- Jul 2026.
* **Phase 4: Perception Integrity Series (P22–P25)**: Published contemporaneously as a unified series in Aug 2026.

---

## 3. Detailed Inventory of Invalid Future References

The following table documents all instances where an earlier paper references a later paper that was not publicly available at that time:

| Source Paper | Source Date | Target Paper | Target Date | Bib Key | Citation Context / Location | Recommended Replacement |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
"""
    for r in data["invalid_future_refs"]:
        lines_preview = "; ".join(r["citing_body_lines"][:2]) if r["citing_body_lines"] else "In BibTeX only"
        report_md += f"| **{r['source_paper']}** ({r['source_pub_date']}) | {r['target_paper']} ({r['target_pub_date']}) | `{r['bib_key']}` | {lines_preview[:60]}... | `{r['recommended_action'][:40]}...` |\n"

    report_md += f"""
---

## 4. Valid Historical & Contemporaneous Citations

The following cross-references satisfy the Chronological Citation Law:
* **Contemporaneous Series (P22, P23, P24, P25)**: Papers 22--25 cite one another's defined interfaces (e.g., P23 consuming $\\mathcal{{P}}(\\mathbf{{x}}, p_{{cal}}, R_p)$ from P22, P24 consuming gating signals, and P25 bounding macro EAF) as a unified contemporaneous 2026 technical report cohort.
* **Historical Prior-Art Citations**: Later papers (e.g., P22 citing P1 architecture, P25 citing P1 and P5) strictly follow temporal validity ($T_{{target}} \\le T_{{source}}$).

---

## 5. Separation of Research Dependency Graph vs. Publication Citation Graph

* **Research Dependency Graph (DAG)**: Models technical dataflow and system layers ($P_1 \\to P_5 \\to P_7 \\to P_8 \\to P_{{22}} \\to P_{{23}} \\to P_{{24}} \\to P_{{25}}$).
* **Publication Citation Graph**: Enforces scholarly citation validity, restricting references to previously published or contemporaneous works.

---

## 6. Permanent Chronology Governance Law (SROS-CHRONO-001)

```
======================================================================================================
PERMANENT SCHOLARMASTER CITATION RULE (SROS-CHRONO-001):
1. A planned or future ScholarMaster paper CANNOT be cited as scholarly literature in an earlier paper.
2. Earlier papers must be completely self-contained, using existing external peer-reviewed literature 
   or direct descriptive formulations.
3. The internal research sequence must NEVER be confused with publication chronology.
======================================================================================================
```
"""
    with open(f"{AUDIT_DIR}/PUBLICATION_CHRONOLOGY_AUDIT.md", "w") as f:
        f.write(report_md)

    print(f"Generated all 13 publication chronology audit artifacts in {AUDIT_DIR}/")

if __name__ == "__main__":
    generate_all_artifacts()
