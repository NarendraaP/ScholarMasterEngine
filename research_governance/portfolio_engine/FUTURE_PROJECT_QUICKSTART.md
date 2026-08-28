# RESEARCH PORTFOLIO GOVERNANCE ENGINE — QUICKSTART GUIDE

This guide explains how to initialize and operate the Governance Engine for new or expanding research projects.

---

## 1. Initializing a New Project

To use the governance engine for a new research portfolio:
```bash
# 1. Clone the portfolio engine directory into your research workspace
mkdir -p research_governance/portfolio_engine/data

# 2. Run full portfolio audit to verify registry integrity
python3 -m research_governance.portfolio_engine full-audit
```

---

## 2. Registering a New Research Paper (e.g. P26)

To onboard a new prospective research paper without modifying existing papers:
```bash
python3 -m research_governance.portfolio_engine register-paper \
  --paper P26 \
  --title "Zero-Knowledge Spatial Verification for Privacy-Preserving Sensing" \
  --area "Edge Cryptography / Privacy" \
  --type "SECURITY" \
  --venue "IEEE Transactions on Information Forensics and Security"
```

---

## 3. Recording a Publication Event & Propagating State

When a paper gets accepted or published:
```bash
# Step 1: Simulate the state transition in dry-run mode
python3 -m research_governance.portfolio_engine propagate-publication \
  --paper P06 \
  --status PUBLISHED \
  --date 2026-09-15 \
  --venue "IEEE Transactions on Signal Processing" \
  --doi "10.1109/TSP.2026.10006" \
  --dry-run

# Step 2: If dry-run output is verified, execute live propagation
python3 -m research_governance.portfolio_engine propagate-publication \
  --paper P06 \
  --status PUBLISHED \
  --date 2026-09-15 \
  --venue "IEEE Transactions on Signal Processing" \
  --doi "10.1109/TSP.2026.10006"
```

---

## 4. Auditing Chronology and Multi-Paper Invariants

Run the automated chronology and consistency suites anytime before submitting papers:
```bash
# Audit citation chronology
python3 -m research_governance.portfolio_engine audit-chronology

# Run full portfolio consistency check
python3 -m research_governance.portfolio_engine full-audit
```

---

## 5. Generating the Master Research Portfolio Plan

To regenerate the LaTeX master planning document:
```bash
python3 -m research_governance.portfolio_engine generate-master-plan
```

---

## 6. Governing Scientific Decisions

Remember the core governance principles:
* **Publication $\neq$ Automatic Citation**: Publication makes a paper *eligible*, but citation requires *scientific relevance*.
* **Relevance $\neq$ Automatic File Edit**: Potential citations generate a recommendation report; human author approval is required before updating manuscripts.
* **Accepted $\neq$ Published**: Accepted papers are cited as *In Press / To Appear* until formal volume/page numbers are registered.
