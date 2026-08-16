# ScholarMaster Final Mathematical Sanity Gate V2 Report (P22–P25)

**Audit Execution Date**: 2026-08-15  
**Governance Framework**: `SROS Version 2.1 — RATIFIED`, `SEOP Version 2.0 — RATIFIED`, `SROS-004 Single-Owner Law`  
**Execution Mode**: **READ-ONLY AUDIT** (0 Manuscript Files Modified)  
**Audit Gate Status**: ⚠️ **FINAL_STATUS = VERIFICATION_REQUIRED** (P24 Fisher global bound narrowed to local infinitesimal expansion; P25 ArcFace and Lipschitz claims conditioned with explicit assumptions)  
**Manuscript Modification Status**: **BLOCKED**  

---

## 1. Executive Summary & Critical Finding: P24 Fisher–Rao Claim

An independent mathematical check was conducted on the claim $d_{\mathcal{M}}^2(P_m, P_c) \le 8 \,\mathrm{JSD}(P_m \parallel P_c)$ in Paper 24:

### Key Finding:
1. **The global inequality $d_{FR}^2(P, Q) \le 8 \,\mathrm{JSD}(P \parallel Q)$ FAILS GLOBALLY**:
   - **Counterexample**: Let $P = (1, 0)$ and $Q = (0, 1)$ on the discrete simplex $\Delta^1$.
   - The exact Fisher-Rao geodesic distance is $d_{FR}(P, Q) = 2\arccos(0) = \pi \implies d_{FR}^2 = \pi^2 \approx 9.8696$.
   - The Jensen-Shannon Divergence is $\mathrm{JSD}(P \parallel Q) = \ln(2) \approx 0.6931 \implies 8 \,\mathrm{JSD} = 8\ln(2) \approx 5.5452$.
   - Since $9.8696 > 5.5452$ (violation ratio $= 1.7798$), the global inequality is **MATHEMATICALLY INVALID**.
2. **The relationship is valid strictly as an INFINITESIMAL / LOCAL EQUIVALENCE**:
   $$\lim_{Q \to P} \frac{d_{FR}^2(P, Q)}{\mathrm{JSD}(P \parallel Q)} = 8 \implies ds_{FR}^2 = 8 \,\mathrm{JSD}(P \parallel P + dP) + \mathcal{O}(\|dP\|^3)$$
3. **Core P24 Contribution is Unaffected**:
   - P24's core contribution rests entirely on symmetric $\mathrm{JSD} \in [0, \ln 2]$ boundedness, Pinsker total variation bounds $\frac{1}{2}\|P - Q\|_{TV}^2 \le \mathrm{JSD}(P \parallel Q) \le \ln(2)\|P - Q\|_{TV}$, exponential trust gradients, and empirical multi-modal consensus recovery ($1.0000$).
   - Fisher-Rao geodesic geometry was supplementary theoretical context.

---

## 2. Granular Mathematical Audit of Disputed Claims

| Claim ID | Paper | Core Mathematical Claim | Forensic Status | Final Verdict | Recommended Action |
|:---:|:---:|---|---|:---:|---|
| **CHK-P24-GEO** | **P24** | $d_{FR}^2 \le 8 \,\mathrm{JSD}$ (Global) | **FAILS GLOBALLY** (Counterexample $\pi^2 > 8\ln 2$) | `METRIC_CONFLATION_ERROR` | Replace global inequality with local expansion: $ds_{FR}^2 = 8\,\mathrm{JSD} + \mathcal{O}(\|dP\|^3)$ and retain global Pinsker bounds. |
| **CHK-P25-ARC** | **P25** | $\|\mathbf{g}_i - \mathbf{g}_j\|_2 \ge 2\sin(m) \approx 0.9589$ | **VALID CONDITIONALLY** (Exact chord formula for $\theta_{ij} \ge 2m$) | `VALID_WITH_EXPLICIT_ASSUMPTION` | State explicit assumption: enrolled gallery prototypes achieve ArcFace target margin $\theta_{ij} \ge 2m$. |
| **CHK-P25-LIP** | **P25** | $\mathrm{Lip}(f_2) = 0$ on unsafe inputs | **VALID RESTRICTED** (Constant mapping to $\bot$ on $\mathcal{X}_{quar}$) | `VALID_WITH_EXPLICIT_ASSUMPTION` | Explicitly state domain restriction; distinguish from unconstrained discontinuous classifier. |

---

## 3. Discrepancy Forensic Ledger & Exact Formulas

```
===================================================================================================
1. P24 FISHER-RAO GEODESIC METRIC AUDIT
===================================================================================================
• Claim: d_M^2(P_m, P_c) <= 8 JSD(P_m || P_c) as a global inequality.
• Exact Fisher-Rao Geodesic Distance: d_FR(P, Q) = 2 arccos( sum_k sqrt(P_k Q_k) ).
• Counterexample: P=(1,0), Q=(0,1) -> d_FR^2 = pi^2 = 9.869604, 8 JSD = 8 ln 2 = 5.545177.
  9.869604 <= 5.545177 is FALSE (fails by factor of 1.7798).
• Valid Local Asymptotic Result: ds_FR^2 = 8 JSD(P || P+dP) + O(||dP||^3) as dP -> 0.
• Valid Global Total Variation Bound: 1/2 ||P - Q||_TV^2 <= JSD(P || Q) <= ln(2) ||P - Q||_TV (Pinsker).
• Verdict: METRIC_CONFLATION_ERROR (Global inequality narrowed to infinitesimal expansion).

===================================================================================================
2. P25 ARCFACE CENTROID SEPARATION CHORD BOUND
===================================================================================================
• Claim: ||g_i - g_j||_2 >= 2 sin(m) approx 0.9589 for m = 0.5 rad.
• Proof: On S^{D-1}, ||g_i - g_j||_2 = sqrt(2 - 2 cos theta_ij) >= sqrt(2 - 2 cos(2m)) = 2 sin(m).
• Value for m=0.5 rad: 2 * sin(0.5) = 0.958851077... rounding to 0.9589.
• Conditionality: ArcFace loss penalizes theta_y + m >= theta_j. In zero-loss equilibrium, theta_ij >= 2m.
• Verdict: VALID_WITH_EXPLICIT_ASSUMPTION (Valid for gallery centroids satisfying theta_ij >= 2m).

===================================================================================================
3. P25 FAIL-CLOSED QUARANTINE DOMAIN LIPSCHITZ BOUND
===================================================================================================
• Claim: Lip(f_2) = 0 on unsafe inputs under fail-closed quarantine.
• Proof: Constant map f: X_quar -> {bot} has derivative and Lipschitz constant exactly 0.
• Boundary Containment: Intercepts uncertified inputs before Layer 2, preventing Voronoi crossings.
• Verdict: VALID_WITH_EXPLICIT_ASSUMPTION (Restricted to quarantine sub-domain X_quar).
===================================================================================================
```

---

## 4. Final Governance Gate Conclusion

- **Mathematical Inconsistencies Identified**: 1 (P24 Global Fisher-Rao inequality narrowed to local infinitesimal expansion)
- **Conditional Assumptions Clarified**: 2 (P25 ArcFace $\theta_{ij} \ge 2m$ assumption and P25 quarantine domain restriction)
- **Core Empirical Evidence**: **100% Intact & Verified** (`master_validation_suite_results.json`)
- **Manuscript Modifications**: **0** (Strict Read-Only Enforcement Maintained)
- **Gate Status**: ⚠️ **FINAL_STATUS = VERIFICATION_REQUIRED** | **MANUSCRIPT_MODIFICATION = BLOCKED**
