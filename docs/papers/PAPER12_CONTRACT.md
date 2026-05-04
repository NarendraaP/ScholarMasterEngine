# PAPER 12 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Flash Endurance Engineering for Write-Intensive Embedded Workloads: Extending SD Card Lifespan Through Kernel-Level Optimization |
| **Paper ID** | P12 |
| **Layer** | Infrastructure (L1 — Storage Durability) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Revised (Boundary-Softened v3.0) |

## 2. Primary Contribution

**A kernel-level optimization stack (ZRAM, F2FS, page cache tuning, NOOP scheduling) that reduces Write Amplification Factor from 12.43 to 2.10 (83% reduction) under sustained write-intensive embedded workloads. Daily physical writes decrease from 4.2GB to 0.8GB. JEDEC-aligned projections (with 10% de-rating) extend analytical SD card lifespan from ~6 months to ~15.65 years (MLC) or ~5.22 years (pessimistic TLC).**

Paper 12 addresses a critical infrastructure constraint: SD cards in embedded edge devices fail rapidly under continuous write workloads unless write amplification is aggressively controlled at the OS level.

## 3. Core Claims

| # | Claim | Evidence | Status |
|---|---|---|---|
| C1 | Default Ext4 configuration produces WAF of 12.43 under sustained workload | eBPF/blktrace measurement, 168 hourly samples (§VII) | Clean |
| C2 | F2FS + ZRAM + cache tuning + NOOP reduces WAF to 2.10 | 95% CI: [2.07, 2.13] (§VII Table 3) | Clean |
| C3 | Daily physical writes reduced from 4.2GB to 0.8GB (80% reduction) | Cumulative optimization measurements (§VII Table 2) | Clean |
| C4 | Projected MLC lifespan extends to ~15.65 years (with 10% de-rating) | JEDEC JESD218-aligned model, Eq. 3 (§III) | Clean — "projected" with explicit de-rating justification |
| C5 | Pessimistic TLC (1000 P/E) still yields ~5.22 years (62.6 months) | Same model, conservative P/E assumption (§VII) | Clean |
| C6 | F2FS reduces p99 tail latency from 124ms to 18ms under aged conditions | 100K random writes at 85% fill (§VII.4) | Clean |

## 4. Scope

### 4.1 In-Scope
- WAF characterization for continuous embedded write workloads
- ZRAM compressed swap configuration
- VFS page cache tuning (dirty_ratio, dirty_expire_centisecs)
- NOOP/none I/O scheduler selection under blk-mq
- Filesystem comparison (Ext4 vs F2FS) with JBD2 journal analysis
- JEDEC-aligned lifespan projection with 10% de-rating factor
- FTL GC modeling (Desnoyers framework, over-provisioning analysis)
- Tail latency / GC spike analysis under filesystem aging
- Host-side write serialization theory ($B_{eff} \approx \lambda \cdot \tau_{flush}$)

### 4.2 Out-of-Scope
- AI model design or inference optimization (workload context only)
- Production deployment workflow (Paper 11)
- System-level integration testing (Paper 10)
- Hardware platform selection (Paper 5)
- System architecture design (Paper 18/20)
- Runtime enforcement or orchestration (Paper 18/20)
- Federated learning or drift adaptation (Paper 13/14)
- Privacy or DP mechanisms (Paper 8)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P12-INV-01 | Application writes MUST target F2FS partitions (no Ext4 for write-heavy paths) | Mount configuration; partition layout |
| P12-INV-02 | Swap MUST use ZRAM (compressed RAM) — no swap-to-flash | Kernel configuration; no swap partition on SD card |
| P12-INV-03 | dirty_ratio and dirty_expire_centisecs MUST be tuned per §IV specifications | Kernel sysctl configuration at boot |
| P12-INV-04 | I/O scheduler MUST be NOOP/none under blk-mq | Block device configuration |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P5 (Hardware) | Hardware platform determines SD card type and interface |
| **Upstream** | P11 (Deployment) | Deployment infrastructure requires durable storage |
| **Downstream** | P10 (Validation) | Longitudinal burn-in validates storage durability |
| **Downstream** | P18 (Crash Safety) | P18 crash recovery relies on P12's filesystem resilience |

## 7. Verification Requirements

- Write amplification factor ≤ 2.5× under sustained write workload
- Daily physical writes ≤ 1.0 GB under standard workload profile
- ZRAM utilization confirmed — zero bytes written to flash swap
- F2FS garbage collection operates within expected overhead bounds
- p99 write latency ≤ 25ms under 85% disk utilization

## 8. What This Paper Does NOT Do

- Does **not** propose new filesystem algorithms (uses existing F2FS)
- Does **not** optimize AI/ML inference performance (only storage endurance)
- Does **not** define system architecture or orchestration (P18/P20 domain)
- Does **not** contain learning, adaptation, or federation logic (P13/P14 domain)
- Does **not** modify FTL firmware (host-side only)
- Lifespan projections include explicit 10% de-rating and are qualified as analytical upper bounds

## 9. Verified Implementation Components (v3.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **WAF Monitor** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (Write Amplification Analysis) |
| **ZRAM/F2FS Check** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (Kernel Config Detection) |
| **Lifespan Proj** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (JEDEC Formula — note: impl uses C×S without de-rating) |

## 10. LOCK STATEMENT

```
PAPER 12 LOCK — v3.0
Layer: Infrastructure (L1 — Storage Durability)
Owns: WAF characterization for write-intensive embedded workloads, ZRAM swap
  compression, VFS page-cache tuning (dirty_ratio/dirty_expire_centisecs),
  NOOP I/O scheduling under blk-mq, F2FS vs Ext4 filesystem comparison,
  JBD2 journal penalty analysis, Wandering Tree / NAT solution evaluation,
  hot/cold data separation analysis, JEDEC-aligned lifespan projection
  (with 10% de-rating), host-side write serialization theory, FTL GC
  modeling (Desnoyers), tail latency suppression under filesystem aging.
Consumes: Hardware platform specs from P5, deployment requirements from P11.
Provides: Storage durability guarantees consumed by P10 (validation),
  filesystem resilience layer consumed by P18 (crash safety).
Forbidden: System architecture design (P18/P20), runtime orchestration (P20),
  ML model training/adaptation (P13/P14), formal verification (P21),
  privacy/DP mechanisms (P8), event routing, watchdog enforcement.
```

---

**Contract Status**: BINDING
**Version**: 3.0
**Generated**: 2026-02-10
**Updated**: 2026-05-04
**CC Audit**: Passed (zero boundary violations, zero overclaims)
**Authority**: Paper 12 LaTeX Source (`docs/papers/paper12_revised.tex`)
