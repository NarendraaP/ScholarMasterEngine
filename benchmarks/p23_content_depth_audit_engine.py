#!/usr/bin/env python3
"""
ScholarMaster P23 Content Depth Audit Engine
============================================
Measures exact PDF bounding-box area integration, body vs ref words,
section-by-section breakdown, and mathematical/empirical completeness for Paper 23.
"""

import os
import sys
import json
import hashlib
import fitz  # PyMuPDF
import re

TEX_PATH = "docs/papers/paper23_revised.tex"
PDF_PATH = "docs/papers/paper23_revised.pdf"
RAW_JSON = "benchmarks/master_validation_suite_results.json"

PAGE_WIDTH = 612.0
PAGE_HEIGHT = 792.0
TOTAL_PAGE_AREA = PAGE_WIDTH * PAGE_HEIGHT
STANDARD_EFFECTIVE_PAGE_AREA = 335664.0  # IEEE 2-column effective content area
WORD_STANDARD_PER_PAGE = 750.0

def get_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def analyze_p23_pdf():
    doc = fitz.open(PDF_PATH)
    total_physical_pages = len(doc)
    
    page_metrics = []
    total_body_area = 0.0
    total_ref_area = 0.0
    total_body_words = 0
    total_ref_words = 0
    
    ref_started = False
    
    for page_idx in range(total_physical_pages):
        page = doc[page_idx]
        text_instances = page.get_text("blocks")
        
        page_body_area = 0.0
        page_ref_area = 0.0
        page_body_words = 0
        page_ref_words = 0
        
        for block in text_instances:
            bbox = fitz.Rect(block[:4])
            text = block[4]
            block_area = bbox.width * bbox.height
            words = len(text.split())
            
            if "References" in text or "REFERENCES" in text or ref_started:
                ref_started = True
                page_ref_area += block_area
                page_ref_words += words
            else:
                page_body_area += block_area
                page_body_words += words
                
        total_body_area += page_body_area
        total_ref_area += page_ref_area
        total_body_words += page_body_words
        total_ref_words += page_ref_words
        
        page_metrics.append({
            "page_number": page_idx + 1,
            "body_words": page_body_words,
            "ref_words": page_ref_words,
            "body_area_pt2": round(page_body_area, 2),
            "ref_area_pt2": round(page_ref_area, 2),
            "area_occupancy_pct": round(((page_body_area + page_ref_area) / STANDARD_EFFECTIVE_PAGE_AREA) * 100, 2)
        })
        
    doc.close()
    
    with open(TEX_PATH, "r", encoding="utf-8") as f:
        tex_content = f.read()
        
    tex_lines = len(tex_content.splitlines())
    tex_words = len(tex_content.split())
    
    # Section level analysis
    section_patterns = [
        ("Abstract", r"\\begin\{abstract\}(.*?)\\end\{abstract\}"),
        ("1. Introduction", r"\\section\{Introduction\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("2. Related Work & Adaptive Inference Taxonomy", r"\\section\{Related Work.*?Adaptive Inference Taxonomy\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("3. Constrained Optimization & Queueing Formulations", r"\\section\{Constrained Optimization.*?Queueing Formulations\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("4. Empirical Evaluation & Performance Telemetry", r"\\section\{Empirical Evaluation.*?Performance Telemetry\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("5. Failure Boundaries & Overload Containment", r"\\section\{Failure Boundaries.*?Overload Containment\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("6. Conclusion", r"\\section\{Conclusion\}(.*?)(?=\\section|\\begin\{thebibliography\}|$)"),
        ("References", r"\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}")
    ]
    
    section_breakdown = []
    for title, pattern in section_patterns:
        match = re.search(pattern, tex_content, re.DOTALL)
        if match:
            raw_sec_text = match.group(1)
            # clean latex commands for word estimation
            clean_sec_text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', ' ', raw_sec_text)
            clean_sec_text = re.sub(r'[\$\&\\_\{\}\^]', ' ', clean_sec_text)
            words = len(clean_sec_text.split())
            section_breakdown.append({
                "section": title,
                "words": words,
                "effective_pages_words": round(words / WORD_STANDARD_PER_PAGE, 2)
            })
            
    res = {
        "tex_sha256": get_sha256(TEX_PATH),
        "pdf_sha256": get_sha256(PDF_PATH),
        "raw_json_sha256": get_sha256(RAW_JSON) if os.path.exists(RAW_JSON) else None,
        "physical_pdf_pages": total_physical_pages,
        "total_tex_lines": tex_lines,
        "total_tex_words": tex_words,
        "body_words": total_body_words,
        "ref_words": total_ref_words,
        "total_pdf_words": total_body_words + total_ref_words,
        "effective_body_pages_area": round(total_body_area / STANDARD_EFFECTIVE_PAGE_AREA, 2),
        "effective_ref_pages_area": round(total_ref_area / STANDARD_EFFECTIVE_PAGE_AREA, 2),
        "effective_total_pages_area": round((total_body_area + total_ref_area) / STANDARD_EFFECTIVE_PAGE_AREA, 2),
        "effective_body_pages_words": round(total_body_words / WORD_STANDARD_PER_PAGE, 2),
        "effective_ref_pages_words": round(total_ref_words / WORD_STANDARD_PER_PAGE, 2),
        "page_details": page_metrics,
        "section_breakdown": section_breakdown
    }
    return res

if __name__ == "__main__":
    res = analyze_p23_pdf()
    print(json.dumps(res, indent=2))
