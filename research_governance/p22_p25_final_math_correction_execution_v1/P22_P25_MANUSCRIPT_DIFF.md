# ScholarMaster Manuscript Diff Report (P24 & P25 Corrections)

**Execution Date**: 2026-08-15  
**Scope**: P24 and P25 Only  

---

## 1. Diff for `docs/papers/paper24_revised.tex`

```diff
@@ -106,12 +106,12 @@
 \end{proof}
 
 egin{corollary}[Total Variation Metric Bounds]
+\label{cor:tv_bounds}
 By Pinsker's inequality applied to the mixture distribution, the total variation distance $\|P_m - P_c\|_{TV} = rac{1}{2}\sum_k |P_m(k) - P_c(k)|$ satisfies:
 egin{equation}
 rac{1}{2} \|P_m - P_c\|_{TV}^2 \le \mathrm{JSD}(P_m \parallel P_c) \le \ln(2) \|P_m - P_c\|_{TV}.
 \end{equation}
 \end{corollary}
 
-\subsection{Fisher Information Metric Geometry}
-On the statistical manifold endowed with the Fisher information metric tensor $g_{ij}(P) = \sum_k rac{1}{P(k)} rac{\partial P(k)}{\partial 	heta_i} rac{\partial P(k)}{\partial 	heta_j}$, the infinitesimal Bhattacharyya distance coincides with the Riemannian geodesic distance:
-egin{equation}
-d_{\mathcal{M}}^2(P_m, P_c) = 8 \left(1 - \sum_k \sqrt{P_m(k) P_c(k)}ight) \le 8 \cdot \mathrm{JSD}(P_m \parallel P_c).
-\end{equation}
-This confirms that the JSD metric provides a continuous, curvature-aware measure of sensory drift on the probability simplex $\Delta^K$.
+\subsection{Infinitesimal Fisher Information Geometry}
+On the interior of the categorical probability simplex endowed with the Fisher information metric tensor $g_{ij}(P) = \sum_k rac{1}{P(k)} rac{\partial P(k)}{\partial 	heta_i} rac{\partial P(k)}{\partial 	heta_j}$, the infinitesimal squared Riemannian distance satisfies:
+egin{equation}
+ds_{FR}^2 = 8 \cdot \mathrm{JSD}(P_m \parallel P_m + dP) + \mathcal{O}(\|dP\|^3).
+\end{equation}
+This confirms that the JSD metric locally reflects Riemannian curvature under small perturbations, while global sensory authority reweighting is strictly governed by the bounded divergence range $[0, \ln 2]$ and Corollary~ef{cor:tv_bounds}.
```

---

## 2. Diff for `docs/papers/paper25_revised.tex`

```diff
@@ -98,7 +98,7 @@
 \end{proof}
 
 egin{corollary}[ArcFace Margin Separation Bound]
-Under additive angular margin loss $\mathcal{L}_{ArcFace}$ with angular margin parameter $m = 0.5	ext{ rad}$, the geodesic distance between target identity centroids satisfies $	heta_{ij} \ge 2m$, bounding the jump discontinuity from below:
+For enrolled gallery biometric prototypes on the unit hypersphere $\mathbb{S}^{D-1}$ satisfying the ArcFace target angular separation condition $	heta_{ij} \ge 2m$ (under angular margin parameter $m = 0.5	ext{ rad}$), the Euclidean distance between adjacent class centroids satisfies:
 egin{equation}
 \|\mathbf{g}_i - \mathbf{g}_j\|_2 = \sqrt{2 - 2\cos 	heta_{ij}} \ge 2\sin(m) pprox 0.9589.
 \end{equation}
@@ -137,7 +137,7 @@
 egin{equation}
 \mathrm{Lip}(\Phi) \le \prod_{l=1}^5 \mathrm{Lip}(f_l).
 \end{equation}
-In an unprotected pipeline, Theorem 1 demonstrates that $\mathrm{Lip}(f_2) 	o \infty$ across Voronoi boundaries, causing unbounded downstream perturbation. In contrast, under Layer 1 fail-closed gating, the domain of $f_2$ is restricted to certified low-risk sub-manifolds $\mathcal{X}_{cert} = \{\mathbf{x} \mid R_p(\mathbf{x}) \le 0.70\}$, strictly bounding $\mathrm{Lip}(f_2)$ and guaranteeing $	ext{EAF} = 0.0$.
+In an unprotected pipeline, Theorem 1 demonstrates that $\mathrm{Lip}(f_2) 	o \infty$ across Voronoi boundaries, causing unbounded downstream perturbation. In contrast, under Layer 1 fail-closed gating, uncertified sensory inputs ($\mathcal{X}_{quar}$) are intercepted and mapped to a constant quarantine state ($ot$) with $\mathrm{Lip}(f_{gate}|_{\mathcal{X}_{quar}}) = 0$, while certified inputs are restricted to sub-manifolds $\mathcal{X}_{cert} = \{\mathbf{x} \mid R_p(\mathbf{x}) \le 0.70\}$ within Voronoi cell interiors, guaranteeing $\mathrm{EAF} = 0.0000$ on quarantined perturbations.
```
