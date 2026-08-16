# P25 Minimal Correction Diff Report (Voronoi Certified Domain Claim)

**Target File**: `docs/papers/paper25_revised.tex`  
**Target Section**: Section IV-B (Composite Lipschitz Chain Rule Analysis)  
**Pre-Edit SHA-256**: `eb1836d7a0383c3b11f20cf058fe26cd63e4f6c8301c4a861cb6047085bf819f`  
**Post-Edit SHA-256**: `ba128f0a2044cb6556ca54353206a65baa989d87028e7ab6914471061806ca44`  

---

```diff
@@ -138,7 +138,7 @@
 egin{equation}
 \mathrm{Lip}(\Phi) \le \prod_{l=1}^5 \mathrm{Lip}(f_l).
 \end{equation}
-In an unprotected pipeline, Theorem 1 demonstrates that $\mathrm{Lip}(f_2) 	o \infty$ across Voronoi boundaries, causing unbounded downstream perturbation. In contrast, under Layer 1 fail-closed gating, uncertified sensory inputs ($\mathcal{X}_{quar}$) are intercepted and mapped to a constant quarantine state ($ot$) with $\mathrm{Lip}(f_{gate}|_{\mathcal{X}_{quar}}) = 0$, while certified inputs are restricted to sub-manifolds $\mathcal{X}_{cert} = \{\mathbf{x} \mid R_p(\mathbf{x}) \le 0.70\}$ within Voronoi cell interiors, guaranteeing $\mathrm{EAF} = 0.0000$ on quarantined perturbations.
+In an unprotected pipeline, Theorem 1 demonstrates that $\mathrm{Lip}(f_2) 	o \infty$ across Voronoi boundaries, causing unbounded downstream perturbation. In contrast, under Layer 1 fail-closed gating, uncertified sensory inputs ($\mathcal{X}_{quar}$) are intercepted and mapped to a constant quarantine state ($ot$) with $\mathrm{Lip}(f_{gate}|_{\mathcal{X}_{quar}}) = 0$, preventing corrupted vector evaluation across Voronoi boundaries and achieving $\mathrm{EAF} = 0.0000$ on quarantined perturbations across the evaluated regimes.
 
 \section{Macro Empirical Results \& Containment Analysis}
 \subsection{Authoritative Empirical EAF Telemetry}
```
