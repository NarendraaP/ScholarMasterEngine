# ScholarMaster Research Series - Compilation Instructions

This directory contains the LaTeX source files for all 20 papers in the ScholarMaster Research Series.

## 📝 Prerequisites

You need a LaTeX distribution installed:
- **Mac**: MacTeX (`brew install --cask mactex`)
- **Linux**: TeX Live (`sudo apt install texlive-full`)
- **Windows**: MiKTeX or TeX Live

## 🚀 How to Compile

Run the provided script:

```bash
chmod +x compile_export.sh
./compile_export.sh
```

The compiled PDFs will be generated in the `pdfs/` directory.

## ⚠️ Missing Assets

The following images appear to be missing from the project and may cause compilation errors in **Paper 1**:
- `enrollment.png`
- `live_rec.png`
- `terminal.png`

**To fix:**
Please verify if these images exist elsewhere or are placeholders. You may need to provide them in the root of this directory before compiling Paper 1.

## 📂 Directory Structure

- `*.tex`: Paper source files
- `*.bib`: Bibliography files
- `benchmarks/`: Benchmark plots and figures
- `data/figures/`: Data visualization figures
- `compile_export.sh`: Compilation script

---
**Status**: Ready for External Compilation
**Generated**: 2026-02-18
