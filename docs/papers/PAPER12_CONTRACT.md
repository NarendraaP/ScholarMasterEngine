# PAPER 12 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Flash Endurance Engineering for Edge AI: Extending SD Card Lifespan from Months to Years Through Kernel-Level Optimization |
| **Paper ID** | P12 |
| **Layer** | Infrastructure (L1 — Storage Durability) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A kernel-level optimization stack (ZRAM, F2FS, page cache tuning, OverlayFS) that extends SD card lifespan from 2.7 months (default ext4) to 8.1 years projected lifetime under continuous edge AI inference workloads, while maintaining read performance and system stability.**

Paper 12 solves a critical production constraint: SD cards in edge AI devices fail rapidly under ML inference write patterns unless write amplification is aggressively controlled at the OS level.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Default ext4 journal writes cause SD card failure in 2.7 months at 30 FPS inference | SMART/health monitoring data (§VII) | Clean |
| C2 | F2FS + ZRAM reduces write amplification factor from 14.2× to 1.8× | SMART WAF measurement (§VIII) | Clean |
| C3 | OverlayFS read-only root eliminates OS-layer writes entirely | Architecture (§V) | Clean |
| C4 | Combined optimization stack extends projected lifespan to 8.1 years | TBW analysis from endurance data (§IX) | Clean — "projected" based on observed wear rate |
| C5 | Page cache tuning (dirty_ratio, swappiness) reduces 89% of unnecessary flushes | Kernel parameter analysis (§VI) | Clean |

## 4. Scope

### 4.1 In-Scope
- SD card failure analysis under ML inference workloads
- Filesystem selection (ext4 vs F2FS vs Btrfs)
- ZRAM compressed swap configuration
- Page cache parameter tuning
- OverlayFS read-only root filesystem
- Endurance testing and lifespan projection
- Write amplification factor measurement

### 4.2 Out-of-Scope
- AI model design or inference optimization
- Production deployment workflow (Paper 11)
- System-level integration testing (Paper 10)
- Hardware platform selection (Paper 5)
- Network or security architecture

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P12-INV-01 | OS root partition MUST be mounted read-only via OverlayFS | Boot configuration; remount-ro verification |
| P12-INV-02 | Application-layer writes MUST be directed to wear-leveled partitions with F2FS | Mount point configuration; no ext4 for write-heavy paths |
| P12-INV-03 | Swap MUST use ZRAM (compressed RAM) — no swap-to-flash | Kernel configuration; no swap partition on SD card |
| P12-INV-04 | dirty_ratio and dirty_background_ratio MUST be tuned to minimize flush frequency | Kernel sysctl configuration at boot |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P5 (Hardware) | Hardware platform determines SD card type and interface |
| **Upstream** | P11 (MLOps) | Deployment infrastructure requires durable storage |
| **Downstream** | P10 (Validation) | Longitudinal burn-in validates storage durability |
| **Downstream** | P18 (Crash Safety) | P18 crash recovery relies on P12's filesystem resilience |

## 7. Verification Requirements

- Write amplification factor ≤ 2.0× under sustained inference workload
- SMART health indicators remain above 70% after 30-day accelerated endurance test
- OverlayFS root verified read-only (no writes to base layer during 7-day test)
- ZRAM utilization confirmed — zero bytes written to flash swap
- F2FS garbage collection operates within expected overhead bounds

## 8. What This Paper Does NOT Do

- Does **not** propose new filesystem algorithms
- Does **not** optimize AI inference performance (only storage endurance)
- Does **not** evaluate SSDs or eMMC — scoped to SD cards
- Lifespan projections are based on observed wear rates and TBW ratings; actual lifespan depends on specific SD card quality and workload variance

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **WAF Monitor** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (Write Amplification Analysis) |
| **ZRAM/F2FS Check** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (Kernel Config Detection) |
| **Lifespan Proj** | `benchmarks/flash_wear_monitor.py` | ✅ Verified (TBW Formula) |

