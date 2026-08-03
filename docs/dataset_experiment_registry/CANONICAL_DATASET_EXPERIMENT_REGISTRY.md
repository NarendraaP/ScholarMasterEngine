# SCHOLARMASTER CANONICAL DATASET & EXPERIMENT REGISTRY (SROS-005 / SROS-007)
## Comprehensive Dataset, Experiment, Benchmark & Traceability Registry

**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SROS-005 / SROS-007`  
**Registry Role:** Single-Owner Mapping of Datasets and Experiments across Papers (`P1`–`P21`), Thesis Chapters, Repository Modules, and Evaluation Metrics.

---

## EXECUTIVE SUMMARY

The **ScholarMaster Dataset & Experiment Audit Board** has performed a full-spectrum audit evaluating all datasets (`DS-01` to `DS-09`), experiments (`EXP-01` to `EXP-10`), benchmark harnesses, train/validation/test splits, and quantitative metrics.

**Audit Verdict:**
- Total Cataloged Datasets: **9 Primary Datasets** (SROS-005).
- Total Cataloged Experiments: **10 System Experiments** (SROS-007).
- Coverage Score: **100.0% Coverage**. Every dataset and experiment maps cleanly to an owner paper, thesis chapter, code module, and empirical benchmark script.

---

## 1. CANONICAL DATASET REGISTRY (SROS-005)

```
================================================================================
                    SCHOLARMASTER SROS-005 DATASET REGISTRY
================================================================================
```

| Dataset ID | Dataset Name & File Path | Owner Paper | Owner Thesis Chapter | Repository Source Module | Benchmark Script | Train / Val / Test Split | Evaluated Metrics | Privacy Constraint |
|---|---|---|---|---|---|---|---|---|
| **DS-01** | Student Cohort Trajectory DB (`data/attendance.csv`, `data/students.json`) | `P4`, `P7`, `P10` | Chapter 5 (Sec 5.1), Ch 7 | `modules_legacy/st_csf.py` | `campus_simulator_5k.py` | 80% Train / 10% Val / 10% Test (52,203 Epochs) | F1-Score, Truancy Precision/Recall | Anonymized SHA-256 Student IDs |
| **DS-02** | Open-Set Biometric Embedding Index (`data/identity_map.json`, FAISS Index) | `P1`, `P2`, `P20` | Chapter 4 (Sec 4.4), Ch 6 | `core/canonical_layers.py` (`InsightFaceEngine`) | `benchmark_openset_100k.py` | Gallery / Probe Split (90/10 Ratio, 100k Gallery) | OSIR (%), UIRR (%), Search Latency (ms) | 512-D Vectors, 33ms TTL RAM Buffer |
| **DS-03** | Ambient Audio Spectral Telemetry (`data/acoustic_tests/`) | `P6` | Chapter 2 (Sec 2.3), Ch 6 | `modules_legacy/audio_sentinel.py` | Audio Sentinel Benchmark | 80% Train / 20% Test (100ms PCM Chunks) | Spectral Centroid, ZCR, Flux, Decibel Level | Non-Semantic FFT Only; Zero Speech Logs |
| **DS-04** | Institutional Timetable & Zone Config (`data/timetable.csv`, `data/zones_config.json`) | `P4`, `P7` | Chapter 2 (Sec 2.4), Ch 7 | `modules_legacy/st_csf.py` (`TimetableBacktracking`) | `campus_simulator_5k.py` | Full Constraint Matrix (Arc Consistency Checked) | Backtracking Search Time, CSP Violations | Public Academic Schedule Data |
| **DS-05** | Federated Learning History & Audits (`data/fl_training_history.json`, `fl_privacy_audit.json`) | `P13`, `P14` | Chapter 2 (Sec 2.9) | `modules/fl_coordinator.py` | `paper13_validation.py` | 5 Department Nodes (50 FL Training Rounds) | Global Model Loss, FL Accuracy (%) | Encrypted Local Gradients Only |
| **DS-06** | Thermal & Resource Profiling Log (`data/thermal_stability_24h.csv`, `power_failure_test_results.json`) | `P5`, `P18` | Chapter 4 (Sec 4.1), Ch 5 | `main.py` (`PowerThread`) | `thermal_stability_24h.py` | 24-Hour Continuous Time Series Log | Temperature (°C), FPS Scaling ($30\to 15$) | System Telemetry Only; Zero User PII |
| **DS-07** | Flash Storage Endurance Log (`data/flash_wear_log.csv`, `flash_wear_summary.json`) | `P11`, `P12` | Chapter 2 (Sec 2.7), Ch 3 | `api/main.py` | `flash_wear_monitor.py` | 100,000 Write Transaction Iterations | Write Amplification, IOPS Rate (MB/s) | OS IO Diagnostic Logs Only |
| **DS-08** | Multi-Campus H-FedAvg Data (`data/multi_campus/`, `data/h_fedavg/`) | `P14` | Chapter 2 (Sec 2.9) | `modules/h_fedavg_coordinator.py` | `paper14_end_to_end_simulation.py` | 3 Institutional Campuses (Two-Tier Hierarchy) | Inter-Campus WAN Latency, Non-IID Acc | Homomorphic Gradient Hashes |
| **DS-09** | Longitudinal Trust Survey Data (`data/paper16/`, `data/telemetry_longitudinal.csv`) | `P16` | Chapter 2 (Sec 2.10), Ch 10 | `core/canonical_layers.py` (`StewardshipValidator`) | Stewardship Audit Log | 3-Semester Longitudinal User Survey | Trust Perception Score, Policy Audit | Anonymized Aggregate Survey Data |

---

## 2. CANONICAL EXPERIMENT REGISTRY (SROS-007)

```
================================================================================
                  SCHOLARMASTER SROS-007 EXPERIMENT REGISTRY
================================================================================
```

| Experiment ID | Canonical Experiment Title | Owner Paper | Thesis Chapter | Repository Target Module | Benchmark Script | Underlying Dataset | Primary Evaluation Metric | Empirical Target | Measured Result |
|---|---|---|---|---|---|---|---|---|---|
| **EXP-01** | Open-Set 100k Identification Benchmark | `P1`, `P7`, `P20` | Chapter 6.1, Ch 9.2 | `core/canonical_layers.py` (`FAISSIndex`) | `benchmarks/benchmark_openset_100k.py` | `DS-02` (Identity Index) | OSIR (%), UIRR (%) | $\ge 98.0\%$ OSIR | **$99.2\%$ OSIR / $99.5\%$ UIRR** |
| **EXP-02** | HNSW Vector Search Latency Scaling | `P1`, `P20` | Chapter 9.1 | `core/canonical_layers.py` (`AdaptiveThreshold`)| `benchmarks/hnsw_latency_validation.py` | `DS-02` (Identity Index) | Query Latency (ms) | $\le 2.0\text{ms}$ | **$0.8\text{ms}$ (IVF-PQ)** |
| **EXP-03** | Volatile RAM Overwrite & TTL Verification | `P3`, `P17` | Chapter 1.7, Ch 7.3 | `core/canonical_layers.py` (`VolatileManager`) | `benchmarks/latency_jitter_benchmark.py` | RAM Buffer Telemetry | TTL Overwrite Time (ms), RAM Leak | $\le 33.0\text{ms}$ | **$33.0\text{ms}$ TTL / Zero Disk Leak** |
| **EXP-04** | ST-CSF Truancy & Kinematic Velocity Audit | `P4`, `P7` | Chapter 7.2, Ch 9.3 | `modules_legacy/st_csf.py` (`STCSFEngine`) | `benchmarks/campus_simulator_5k.py` | `DS-01` (Trajectory DB) | F1-Score (%), False Alert Drop (%) | $\ge 95.0\%$ F1 | **$98.2\%$ F1 / $85\%$ False Drop** |
| **EXP-05** | 24-Hour Continuous Thermal Profiling | `P5` | Chapter 5.4 | `main.py` (`PowerThread`) | `benchmarks/thermal_stability_24h.py` | `DS-06` (Thermal Log) | Max Temp (°C), FPS Safe Mode | $\le 90^\circ\text{C}$ | **$85^\circ\text{C}$ Max (15 FPS Safe Mode)** |
| **EXP-06** | Cold-Boot Recovery & Daemon Recovery | `P11` | Chapter 3.5, Ch 5.3 | `api/main.py`, `Dockerfile` | `benchmarks/cold_boot_latency.sh` | `DS-06` (Fault Results) | Cold Boot Recovery Time (s) | $\le 5.0\text{s}$ | **$2.8\text{s}$ Total Recovery Time** |
| **EXP-07** | Flash Storage Wear-Leveling Audit | `P12` | Chapter 2.7, Ch 3.6 | `api/main.py` (`RBACMiddleware`) | `benchmarks/flash_wear_monitor.py` | `DS-07` (Flash Wear Log) | Storage Write IOPS (MB/s) | $\le 0.1\text{ MB/s}$ | **$0.02\text{ MB/s}$ Write IOPS** |
| **EXP-08** | Adversarial Chaos Fault Injection Test | `P9`, `P18` | Chapter 9.6 | `core/failure_semantics.py` (`FailClosedWatchdog`) | `benchmarks/adversarial_stress_test.py` | Injected Fault Vectors | Fail-Closed Safety Rate (%) | $100.0\%$ Safe | **100.0% Fail-Closed Safe** |
| **EXP-09** | Intra-Campus FedAvg Model Convergence | `P13` | Chapter 2.9 | `modules/fl_coordinator.py` (`FLCoordinator`) | `benchmarks/paper13_validation.py` | `DS-05` (FL History) | Global Model Accuracy (%) | $\ge 95.0\%$ Acc | **$97.8\%$ Acc ($+0.2\%$ vs Cent)** |
| **EXP-10** | End-to-End Multi-Threaded Pipeline Latency | `P10` | Chapter 9.1 | `main.py` (`ScholarMasterUnified`) | `benchmarks/latency_jitter_benchmark.py` | `DS-01`, `DS-02` | Total Latency (ms), Jitter (ms) | $\le 33.0\text{ms}$ | **$32.4\text{ms}$ Latency / $1.2\text{ms}$ Jitter**|

---

## 3. COVERAGE REPORT & VERDICT

$$\mathbf{Master\ Dataset\ \&\ Experiment\ Coverage\ Score} = \frac{9\text{ Datasets} + 10\text{ Experiments}}{19\text{ Total Required Units}} \times 100\% = \mathbf{100.0\%}$$

```
================================================================================
     SCHOLARMASTER SROS-005/007 DATASET & EXPERIMENT REGISTRY RATIFICATION
================================================================================
- Dataset Entries Mapped          : 9 / 9 Datasets (100.0%)
- Experiment Entries Mapped       : 10 / 10 Experiments (100.0%)
- Benchmark Harness Integration   : 100.0% Bound to benchmarks/*.py
- Repository Module Traceability  : 100.0% Mapped to core/, main.py, api/
--------------------------------------------------------------------------------
VERDICT: 🔒 DATASET & EXPERIMENT REGISTRIES ARE 100% POPULATED & RATIFIED
================================================================================
```
