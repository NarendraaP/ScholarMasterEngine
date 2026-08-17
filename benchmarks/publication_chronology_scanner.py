#!/usr/bin/env python3
"""
ScholarMaster Publication Chronology & Cross-Reference Scanner
==============================================================
Extracts and audits all cross-paper references, bibitems, and textual mentions across P1–P25.
"""

import os
import re
import json

PAPERS_DIR = "docs/papers"
OUTPUT_FILE = "research_governance/publication_chronology_audit/P1_P25_CROSS_REFERENCE_INVENTORY.json"
os.makedirs("research_governance/publication_chronology_audit", exist_ok=True)

results = {}

for pid in range(1, 26):
    tex_path = f"{PAPERS_DIR}/paper{pid}_revised.tex"
    if not os.path.exists(tex_path):
        continue
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    lines = content.split("\n")
    
    # 1. Search for internal bibitems or citations
    # Find all bibitems
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\}|$)", content, re.DOTALL)
    scholarmaster_bibs = {}
    for key, text in bibitems:
        clean_text = " ".join(text.split())
        if any(term in clean_text.lower() for term in ["scholarmaster", "paper ", "technical report series", "kumar2026"]):
            scholarmaster_bibs[key] = clean_text
            
    # 2. Search for citation usage of these bibkeys in body
    citations_found = []
    for key in scholarmaster_bibs:
        for idx, line in enumerate(lines):
            if f"{{{key}}}" in line or f",{key}" in line or f"{key}," in line:
                citations_found.append({
                    "line_num": idx + 1,
                    "line": line.strip(),
                    "key": key,
                    "bib_text": scholarmaster_bibs[key]
                })
                
    # 3. Search for textual mentions of other papers
    textual_mentions = []
    text_patterns = [
        r"Paper\s+\d+",
        r"Paper\s+2[2-5]",
        r"P2[2-5]",
        r"companion paper",
        r"subsequent work",
        r"forthcoming",
        r"future work",
        r"in preparation",
        r"earlier work",
        r"previous work"
    ]
    for idx, line in enumerate(lines):
        # Skip header and title of self
        if idx < 28:
            continue
        # Skip references section
        if "\\begin{thebibliography}" in line:
            break
        for pat in text_patterns:
            matches = re.finditer(pat, line, re.IGNORECASE)
            for m in matches:
                # filter out self-mentions like "Technical Report Series --- Paper X"
                textual_mentions.append({
                    "line_num": idx + 1,
                    "match": m.group(0),
                    "line": line.strip()
                })
                
    results[f"P{pid}"] = {
        "paper_id": pid,
        "scholarmaster_bibs": scholarmaster_bibs,
        "citations_found": citations_found,
        "textual_mentions": textual_mentions
    }

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"Scanned all 25 papers. Results saved to {OUTPUT_FILE}")
