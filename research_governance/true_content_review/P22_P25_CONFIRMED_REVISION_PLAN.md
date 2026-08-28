# SCHOLARMASTER — P22–P25 CONFIRMED REVISION PLAN

**Date**: 2026-08-29  
**Status**: Confirmed Pre-Submission Revision Plan (NO MANUSCRIPT MODIFICATIONS YET)  
**Governance Standard**: Verified Falsification Pass  

---

## 1. Governance Policy & Scope of Changes

This plan defines the **exact, verified modifications** required to make Papers 22, 23, 24, and 25 completely unassailable to hostile reviewers.

### Governing Invariants:
1. **NO NEW EXPERIMENTS REQUIRED**: The existing 2,000-frame benchmarks and hardware telemetry across ARM64 edge nodes fully support properly scoped claims.
2. **NO INVENTED METRICS OR DATA**: Every number cited must originate from verified manuscript tables and logs.
3. **ACCURATE THEORETICAL POSITIONING**: Theorems must be positioned as formal analytical properties bounding edge cyber-physical parameters rather than over-claiming standard textbook statistics as newly discovered mathematics.
4. **FAIL-CLOSED AVAILABILITY TRANSPARENCY**: All fail-closed gating claims ($\text{EAF} = 0.0000$) must transparently report the associated pass/quarantine rates.

---

## 2. Paper 22: Confirmed Revision Plan

### A. Confirmed Mandatory Revisions:
1. **P22.1 (Re-frame Theorem 1 - Dirichlet Variance Bound)**:
   - *Location*: Section III-B, lines 131–138.
   - *Change*: Recast Theorem 1 from a standalone mathematical breakthrough into an *analytical variance upper bound* that guarantees asymptotic Dirichlet evidence contraction ($\mathcal{O}(1/S)$) under edge SLA constraints.
   - *Rationale*: Acknowledges the standard Beta marginal variance derivation while maintaining its formal role in bounding vacuity.
2. **P22.2 (Define Multi-Branch Architecture - Branch A / Branch B)**:
   - *Location*: Section III-D, line 207 and Algorithm 1, line 232.
   - *Change*: Add explicit definition: *"where Branch A ($p_A$) denotes the primary deep classification backbone and Branch B ($p_B$) denotes the auxiliary spatial feature head operating on downsampled feature maps."*
   - *Rationale*: Eliminates the reproducibility gap identified in peer review.
3. **P22.3 (Qualify AUROC = 1.0000 Claim)**:
   - *Location*: Abstract, line 30; Section I, line 66; Section IV-C1, line 291.
   - *Change*: Clarify that $\text{AUROC} = 1.0000$ is achieved on the *curated 2,000-frame edge benchmark suite under severe synthetic corruptions*, preserving the empirical telemetry without over-generalizing to open-world unconstrained distributions.
   - *Rationale*: Protects the paper against instant rejection for claiming universal perfection.
4. **P22.4 (Add SNGP and DUQ Citations)**:
   - *Location*: Section II-A, line 76; Bibliography.
   - *Change*: Add citations to SNGP (Liu et al., NeurIPS 2020) and DUQ (van Amersfoort et al., ICML 2020) as single-pass deterministic uncertainty baselines.

### B. Optional Revisions:
* Add a brief remark in Section V-A noting rolling-shutter geometric distortion vs global-shutter optical blur.

### C. Rejected Recommendations:
* *Demanding public ImageNet-O / CIFAR-10 OOD benchmarks*: Rejected. P22 is an edge cyber-physical vision systems paper evaluated on ARM64 hardware with physical optical blur and multi-branch agreement; generic image classification benchmarks do not measure physical edge blur and keypoint kinematics.

---

## 3. Paper 23: Confirmed Revision Plan

### A. Confirmed Mandatory Revisions:
1. **P23.1 (Re-frame Theorem 1 - Zero Duality Gap)**:
   - *Location*: Section III-B, lines 128–139.
   - *Change*: Frame Theorem 1 as *establishing convex continuum duality for the edge cascade formulation*, rigorously proving that randomized routing over $L^\infty$ exhibits zero duality gap for linear risk-resource trade-offs.
   - *Rationale*: Defends the theoretical formulation while acknowledging that linear functionals on convex sets satisfy strong duality under Slater's condition.
2. **P23.2 (Clarify 373.3 FPS as Instantaneous Service Capacity)**:
   - *Location*: Abstract, line 30; Section I, line 55; Section IV-C1, line 288.
   - *Change*: Clarify that $373.3\text{ FPS}$ represents *maximum instantaneous processing capacity* ($2.679\text{ ms}$ service time), ensuring that continuous $30\text{--}60\text{ FPS}$ video ingestion experiences near-zero queueing delay ($\rho \le 0.16$).
   - *Rationale*: Prevents confusion between batch throughput and streaming camera ingestion rates.
3. **P23.3 (Clarify Energy as Normalized Complexity Index)**:
   - *Location*: Section III-A, lines 97–98; Section III-D, line 196; Table II.
   - *Change*: Ensure consistent terminology: *"normalized computational energy index (proportional to FLOP complexity and memory access)"*.
4. **P23.4 (Document Unified Memory Context Invariant)**:
   - *Location*: Section IV-A, line 246; Section V-B.
   - *Change*: Add 2 sentences confirming that primary ($M_1$) and secondary ($M_2$) models reside persistently in unified memory, sharing a single execution stream to eliminate dynamic GPU context reload overhead.

### B. Optional Revisions:
* Add a conceptual accuracy-latency Pareto frontier diagram if space allows.

### C. Rejected Recommendations:
* *Forcing a $D/G/1$ queueing derivation*: Rejected. The $M/G/1$ Pollaczek-Khinchine model is explicitly presented and proven to be a *conservative theoretical upper bound* using Kingman's approximation ($C_a^2 \approx 0 < 1$).

---

## 4. Paper 24: Confirmed Revision Plan

### A. Confirmed Mandatory Revisions:
1. **P24.1 (Attribute JSD Boundedness to Lin 1991)**:
   - *Location*: Section III-B, Theorem 1, lines 125–131.
   - *Change*: Explicitly attribute the bound in Theorem 1: *"Theorem 1 (JSD Information-Theoretic Bounds): Following the classical information-theoretic bounds of Jensen-Shannon Divergence (Lin, 1991), for any discrete probability distributions... $0 \le \mathrm{JSD} \le \ln 2$."* Center the original contribution on multi-channel consensus recovery and gradient dynamics.
   - *Rationale*: Prevents accusations of claiming a 1991 theorem as a new discovery.
2. **P24.2 (Qualify 100% Recovery Claim)**:
   - *Location*: Abstract, line 30; Section I, line 59; Table II, lines 304–307; Section V-C1, line 330.
   - *Change*: Replace unqualified "100% recovery" with: *"achieves complete state recovery ($1.0000$) under single-channel optical degradation by dynamically transferring 95.0% decision authority to intact secondary acoustic and pose channels."*
   - *Rationale*: Accurately describes the empirical result without implying that recovery is possible if secondary channels are also failing.
3. **P24.3 (Frame Proposition 1 as Operational Gradient Dynamics)**:
   - *Location*: Section III-E, lines 208–214.
   - *Change*: Frame Proposition 1 as the *analytical trust weight gradient dynamics* of the parameterized exponential weighting function.
4. **P24.4 (Add Remark on Noisy Secondary Modalities)**:
   - *Location*: Section V-C3, lines 335–340.
   - *Change*: Add 2 sentences explaining that under real-world conditions where secondary sensors have non-zero baseline error, consensus accuracy is bounded by the secondary sensor performance.

### B. Optional Revisions:
* Add clarification on software PLL phase error tolerance $\Delta t_{sync} = 16.6\text{ ms}$.

### C. Rejected Recommendations:
* *Demanding physical hardware clock jitter experiments*: Rejected. Section IV-B already states that Algorithm 1 is the formal reference specification while `ConsistencyChecker` is the production runtime.

---

## 5. Paper 25: Confirmed Revision Plan

### A. Confirmed Mandatory Revisions:
1. **P25.1 (Report Availability / Quarantine Trade-off with EAF = 0)**:
   - *Location*: Abstract, line 30; Section I, line 58; Table II, lines 278–285; Section V-C, line 309.
   - *Change*: In Section V-C and Table II, explicitly cite the Layer-1 pass rate ($78.4\%$) and quarantine rate ($21.6\%$), explaining that $\text{EAF} = 0.0000$ represents zero downstream error on admitted frames via the fail-closed safety-availability trade-off.
   - *Rationale*: Resolves the availability tautology criticism by making the safety vs availability trade-off explicit.
2. **P25.2 (Re-frame Voronoi Step Jump Discontinuity)**:
   - *Location*: Section III-B, Theorem 1, lines 129–135.
   - *Change*: Frame Theorem 1 as *proving that nearest-neighbor biometric metric retrieval introduces essential step jumps of magnitude $\ge 2\sin(m) \approx 0.9589$, formally demonstrating why classical continuous Lipschitz verification fails in deep retrieval and proving the necessity of domain partitioning ($\mathcal{X}_{cert} \cup \mathcal{X}_{quar}$)*.
   - *Rationale*: Connects the geometric step discontinuity directly to the failure of continuous Lipschitz theory and motivates the 5-layer firewall.
3. **P25.3 (Highlight Table III as Primary Empirical Centerpiece)**:
   - *Location*: Section V-B, lines 291–305; Section V-C1.
   - *Change*: Emphasize Table III (cross-layer compounding from $21.33\%$ identity error to $38.90\%$ compliance violation) as the core empirical finding that quantifies Data Cascades.

### B. Optional Revisions:
* Add a brief remark in Section V-C3 on Voronoi cell density scaling as gallery size $N \to \infty$.

### C. Rejected Recommendations:
* *Merging P25 into P22*: Rejected. P25 analyzes cross-layer error compounding across all 5 canonical layers and formulates the EAF condition number, which is distinct from P22's unimodal perception gate.

---

## 6. Execution Summary Table

| Paper | Target File | Confirmed Revision Items | Verification Status | Ready for Edit Pass? |
|:---:|:---|:---:|:---:|:---:|
| **P22** | `docs/papers/paper22_revised.tex` | Re-frame Thm 1; Define Branch A/B; Qualify AUROC=1.0000; Add SNGP/DUQ refs. | **VERIFIED** | Awaiting User Authorization |
| **P23** | `docs/papers/paper23_revised.tex` | Re-frame Thm 1 duality; Clarify 373 FPS service capacity; Clarify energy proxy; Document unified memory invariant. | **VERIFIED** | Awaiting User Authorization |
| **P24** | `docs/papers/paper24_revised.tex` | Attribute JSD bound to Lin (1991); Qualify 100% recovery to authority transfer; Re-frame Prop 1; Add noisy secondary sensor remark. | **VERIFIED** | Awaiting User Authorization |
| **P25** | `docs/papers/paper25_revised.tex` | Report pass/quarantine rate with EAF=0; Re-frame Voronoi theorem to explain Lipschitz failure; Highlight Table III cross-layer compounding. | **VERIFIED** | Awaiting User Authorization |

---

```text
REVISION_VERIFICATION = COMPLETE
CHANGE_PLAN_STATUS = CONFIRMED_AND_FROZEN
MANUSCRIPTS_MODIFIED = NONE (Zero Edits During Verification)
```
