#!/bin/bash
set -e

# ScholarMaster Research Series - Export Compilation Script
# Usage: ./compile_export.sh

mkdir -p pdfs

echo "=========================================="
echo "📚 Compiling ScholarMaster Papers"
echo "=========================================="

compile() {
    local tex_file=$1
    local output_name=$2
    echo "Processing: $output_name..."
    pdflatex -interaction=nonstopmode -output-directory=pdfs "$tex_file" > /dev/null 2>&1
    pdflatex -interaction=nonstopmode -output-directory=pdfs "$tex_file" > /dev/null 2>&1
    if [ -f "pdfs/${tex_file%.*}.pdf" ]; then
        mv "pdfs/${tex_file%.*}.pdf" "pdfs/${output_name}.pdf"
        echo "✅ Created: pdfs/${output_name}.pdf"
    else
        echo "❌ Failed: $tex_file"
    fi
}

# --- Stratum I: Physics ---
compile "paper5_corrected.tex" "Paper5_Hardware"
compile "paper6_corrected.tex" "Paper6_Acoustic"
compile "paper11_corrected.tex" "Paper11_MLOps"
compile "paper12_corrected.tex" "Paper12_Flash"

# --- Stratum II: Logic ---
compile "paper1_corrected.tex" "Paper1_Biometric"
compile "paper2_corrected.tex" "Paper2_Context"
compile "paper3_corrected.tex" "Paper3_Pose"
compile "paper4_corrected.tex" "Paper4_Compliance"
compile "paper17_corrected.tex" "Paper17_Irreversibility"

# --- Stratum III: Verification ---
compile "paper7_corrected.tex" "Paper7_Rules"
compile "paper8_corrected.tex" "Paper8_Trust"
compile "paper9_corrected.tex" "Paper9_Orchestration"
compile "paper10_corrected.tex" "Paper10_Validation"
compile "paper15_corrected.tex" "Paper15_AR"
compile "paper18_corrected.tex" "Paper18_Runtime"
compile "paper19_corrected.tex" "Paper19_ThreatModel"

# --- Stratum IV: Society & Unified ---
compile "paper13_corrected.tex" "Paper13_IntraFL"
compile "paper14_corrected.tex" "Paper14_InterFL"
compile "paper16_corrected.tex" "Paper16_Sociology"
compile "paper20_unified_model.tex" "Paper20_UnifiedModel"

echo "=========================================="
echo "🎉 Done! PDFs are in the 'pdfs' directory."
echo "Note: If compilation failed, check 'README_COMPILATION.md' for missing images."
