# SCHOLARMASTER CITATION SYNCHRONIZATION & GOVERNANCE POLICY

## 1. Core Principle
```text
RESEARCH PLAN ≠ PUBLICATION STATE ≠ CITATION ELIGIBILITY ≠ CITATION RELEVANCE ≠ CITATION NECESSITY ≠ ACTUAL CITATION
```

## 2. Hard Invariants
1. **Published ≠ Cite Everywhere**: A publication becoming citation-eligible does not grant permission to insert citations into unrelated manuscripts.
2. **Chronology Integrity**: If Paper A finalized at date T_A and Paper B published at T_B > T_A, Paper A citing Paper B remains an `INVALID_FORWARD_CITATION` even after Paper B is published.
3. **Safe Automation vs Human Review**:
   - **Safe Automation**: Updating BibTeX keys, DOIs, venues, volume/pages in `.bib` files or approved bibliography blocks.
   - **Human Review Required**: Inserting new citations into scientific prose, modifying text, changing Related Work, or modifying claims.
4. **No Paper-Number Heuristics**: Paper number or research plan position is strictly organizational and never serves as proof of scientific relevance.

## 3. The 3-Question Decision Process
For every candidate citation pair (A -> B):
- **Question A (Chronology)**: Is B published/accepted and T_A >= T_B?
- **Question B (Relevance)**: Does an explicit Research Plan Graph edge or declared interface contract exist?
- **Question C (Necessity & Presence)**: Does manuscript A already cite B, or is human review required for new text modification?
