#!/usr/bin/env python3
"""
ScholarMaster P22 Manuscript Content Depth & Scientific Development Audit Engine
================================================================================
Generates all 9 governance artifacts in research_governance/p22_content_depth_audit/
"""

import os
import json
import hashlib
import re
import fitz  # PyMuPDF

AUDIT_DIR = "research_governance/p22_content_depth_audit"
os.makedirs(AUDIT_DIR, exist_ok=True)

TEX_PATH = "docs/papers/paper22_revised.tex"
PDF_PATH = "docs/papers/paper22_revised.pdf"
RAW_JSON_PATH = "benchmarks/master_validation_suite_results.json"

def get_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def analyze_latex_and_pdf():
    tex_sha = get_sha256(TEX_PATH)
    pdf_sha = get_sha256(PDF_PATH)
    raw_sha = get_sha256(RAW_JSON_PATH)

    # Read .tex source
    with open(TEX_PATH, "r") as f:
        tex_content = f.read()

    tex_lines = tex_content.splitlines()
    total_tex_lines = len(tex_lines)
    tex_chars = len(tex_content)
    tex_words = len(tex_content.split())

    # PyMuPDF Analysis
    doc = fitz.open(PDF_PATH)
    n_pages = len(doc)
    page_data = []
    
    total_body_words = 0
    total_ref_words = 0
    total_body_area_pt2 = 0.0
    total_ref_area_pt2 = 0.0
    printable_page_area_pt2 = 504.0 * 666.0  # 335,664 pt^2

    for p_idx, page in enumerate(doc):
        text = page.get_text()
        words = text.split()
        word_count = len(words)
        
        # Bounding box of text
        rects = page.get_text("blocks")
        page_content_area = 0.0
        is_ref_page = False
        
        for r in rects:
            # r is (x0, y0, x1, y1, text, block_no, block_type)
            bx0, by0, bx1, by1, btext = r[0], r[1], r[2], r[3], r[4]
            block_area = (bx1 - bx0) * (by1 - by0)
            page_content_area += block_area
            if "References" in btext or "REFERENCES" in btext:
                is_ref_page = True

        if p_idx >= 3 and is_ref_page:
            total_ref_words += word_count
            total_ref_area_pt2 += page_content_area
        else:
            total_body_words += word_count
            total_body_area_pt2 += page_content_area

        page_data.append({
            "page_number": p_idx + 1,
            "word_count": word_count,
            "content_area_pt2": round(page_content_area, 2),
            "area_occupancy_pct": round((page_content_area / printable_page_area_pt2) * 100, 2),
            "contains_references": is_ref_page
        })

    effective_body_pages_area = round(total_body_area_pt2 / printable_page_area_pt2, 2)
    effective_ref_pages_area = round(total_ref_area_pt2 / printable_page_area_pt2, 2)
    effective_total_pages_area = round((total_body_area_pt2 + total_ref_area_pt2) / printable_page_area_pt2, 2)

    effective_body_pages_words = round(total_body_words / 750.0, 2)
    effective_ref_pages_words = round(total_ref_words / 750.0, 2)

    return {
        "tex_sha256": tex_sha,
        "pdf_sha256": pdf_sha,
        "raw_json_sha256": raw_sha,
        "physical_pdf_pages": n_pages,
        "total_tex_lines": total_tex_lines,
        "total_tex_words": tex_words,
        "body_words": total_body_words,
        "ref_words": total_ref_words,
        "total_words": total_body_words + total_ref_words,
        "effective_body_pages_area": effective_body_pages_area,
        "effective_ref_pages_area": effective_ref_pages_area,
        "effective_total_pages_area": effective_total_pages_area,
        "effective_body_pages_words": effective_body_pages_words,
        "effective_ref_pages_words": effective_ref_pages_words,
        "page_details": page_data
    }

print("Running analysis...")
metrics = analyze_latex_and_pdf()
print(json.dumps(metrics, indent=2))
