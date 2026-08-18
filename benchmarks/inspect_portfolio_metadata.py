#!/usr/bin/env python3
"""
inspect_portfolio_metadata.py
Inspects all 25 ScholarMaster papers and aggregates full profiles.
"""
import os
import json
import re

def parse_paper(paper_num):
    tex_path = f"docs/papers/paper{paper_num}_revised.tex"
    if not os.path.exists(tex_path):
        return None
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Title extraction
    t_idx = text.find(r"\title{")
    if t_idx == -1:
        t_idx = text.find(r"\title [")
    if t_idx != -1:
        start = text.find("{", t_idx)
        depth, end = 0, start
        for j in range(start, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        raw_title = text[start+1:end].replace("\n", " ")
        raw_title = re.sub(r"\\thanks\{.*?\}", "", raw_title, flags=re.DOTALL)
        raw_title = re.sub(r"\s+", " ", raw_title).strip()
    else:
        raw_title = f"Paper {paper_num}"

    # Abstract extraction
    abs_start = text.find(r"\begin{abstract}")
    abs_end = text.find(r"\end{abstract}")
    abstract = ""
    if abs_start != -1 and abs_end != -1:
        abstract = text[abs_start + len(r"\begin{abstract}"):abs_end].replace("\n", " ").strip()
        abstract = re.sub(r"\s+", " ", abstract)

    # Keywords extraction
    kw_start = text.find(r"\begin{IEEEkeywords}")
    kw_end = text.find(r"\end{IEEEkeywords}")
    keywords = ""
    if kw_start != -1 and kw_end != -1:
        keywords = text[kw_start + len(r"\begin{IEEEkeywords}"):kw_end].replace("\n", " ").strip()
        keywords = re.sub(r"\s+", " ", keywords)

    # Sections extraction
    sections = re.findall(r"\\section\{([^}]+)\}", text)

    return {
        "paper_id": f"P{paper_num}",
        "paper_number": paper_num,
        "title": raw_title,
        "abstract": abstract,
        "keywords": keywords,
        "sections": sections,
        "line_count": len(text.splitlines()),
        "word_count": len(text.split())
    }

def main():
    results = {}
    for i in range(1, 26):
        data = parse_paper(i)
        if data:
            results[f"P{i}"] = data
            print(f"P{i:02d}: {data['title'][:60]}... ({data['word_count']} words, {len(data['sections'])} sections)")

    with open("research_governance/publication_readiness_audit/PARSED_PAPERS_METADATA.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Metadata written to PARSED_PAPERS_METADATA.json")

if __name__ == "__main__":
    main()
