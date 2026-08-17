#!/usr/bin/env python3
"""
ScholarMaster Compilation & Verification Engine
===============================================
Recompiles all 25 papers using pdflatex and verifies 0 errors across the portfolio.
"""

import os
import subprocess
import fitz

PAPERS_DIR = "docs/papers"

def compile_paper(pid):
    tex_file = f"paper{pid}_revised.tex"
    pdf_file = f"paper{pid}_revised.pdf"
    
    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file]
    res = subprocess.run(cmd, cwd=PAPERS_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if res.returncode != 0:
        print(f"❌ Error compiling P{pid}:")
        print("\n".join(res.stdout.split("\n")[-25:]))
        return False
        
    # Second pass for clean cross-references
    subprocess.run(cmd, cwd=PAPERS_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Check PDF with fitz
    doc = fitz.open(f"{PAPERS_DIR}/{pdf_file}")
    pages = len(doc)
    print(f"✅ P{pid} compiled successfully: {pages} pages.")
    return True

def compile_all():
    print("=" * 70)
    print("RECOMPILING AND VERIFYING ALL 25 PAPERS")
    print("=" * 70)
    
    success_count = 0
    for pid in range(1, 26):
        if compile_paper(pid):
            success_count += 1
            
    print(f"\nResult: {success_count}/25 papers compiled successfully with 0 errors.")
    return success_count == 25

if __name__ == "__main__":
    compile_all()
