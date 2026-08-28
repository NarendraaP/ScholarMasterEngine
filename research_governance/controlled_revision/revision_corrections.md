# SCHOLARMASTER — AUDIT DISCREPANCY & REVISION CORRECTIONS

**Date**: 2026-08-29  
**Purpose**: Document discrepancies between initial automated audit findings and actual manuscript ground truth, recording verified decisions.

---

### Discrepancy 1: P01 In-Text vs Bibliography Forward Citations
* **Audit Finding**: Audit reported P01 cited P22 and P25 in text.
* **Actual Manuscript State**: `b22`, `b25`, `kumar2026scholar22`, and `kumar2026scholar25` were present as unreferenced bibliography items at the end of `paper1_revised.tex`, but were not cited anywhere in the body text (`\cite{...}`).
* **Decision**: Cleanly remove the unreferenced bibliography items from `paper1_revised.tex`.
* **Reason**: Prevents invalid forward citations from appearing in the published bibliography while ensuring zero in-text broken links.

---

### Discrepancy 2: P10 In-Text vs Bibliography Forward Citation
* **Audit Finding**: Audit reported P10 cited P22.
* **Actual Manuscript State**: `kumar2026scholar22` was present as an unreferenced `ibitem` at line 496 of `paper10_revised.tex`, not cited in body text.
* **Decision**: Cleanly remove `ibitem{kumar2026scholar22}` from `paper10_revised.tex`.
* **Reason**: Eliminates chronology violation with zero text disruption.

---

### Discrepancy 3: P11 In-Text Citation Typo (`b17` vs `b18`)
* **Audit Finding**: Audit reported missing citation `b17` in P11.
* **Actual Manuscript State**: Text at line 140 cited `\cite{b4, b12, b17}`, but `b18` in the bibliography was `S. Kuppusamy et al., Diplomat: Using Delegations to Protect Community Repositories (USENIX NSDI 2016)`.
* **Decision**: Correct in-text citation key from `b17` to `b18`.
* **Reason**: Resolves unresolved citation reference in LaTeX.

---

### Discrepancy 4: P13 Missing Citation Key `b21`
* **Audit Finding**: Audit reported missing citation `b21` in P13.
* **Actual Manuscript State**: Text cited `Gal and Ghahramani \cite{b21}`, but bibliography was missing the specific 2016 ICML reference.
* **Decision**: Add `ibitem{b21} Y. Gal and Z. Ghahramani, Dropout as a Bayesian approximation... (ICML 2016)`.
* **Reason**: Completes required peer-reviewed reference.

---

### Discrepancy 5: P15 User Study Cohort Size
* **Audit Finding**: Audit cited $N=24$ participants based on sister paper references.
* **Actual Manuscript State**: `paper15_revised.tex` explicitly evaluated $N=20$ participants in Section IX Limitations (Line 439).
* **Decision**: Reframe Abstract to state "controlled 20-participant staged incident response user study" for exact internal consistency.
* **Reason**: Maintains 100% factual integrity without fabricating participant numbers.
