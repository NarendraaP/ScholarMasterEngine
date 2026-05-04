# PAPER 11 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Lifecycle Hardening of Immutable Edge Appliances under Power and Connectivity Instability |
| **Paper ID** | P11 |
| **Layer** | Infrastructure (L6 — Production MLOps) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Corrected (CC v3.0 aligned) |

## 2. Primary Contribution

**An immutable edge deployment architecture designed to improve corruption resistance and autonomous recovery under unstable power and connectivity conditions. Operationalizes an Appliance Invariance Model via OverlayFS, Blue/Green OTA updates, and hardware watchdog integration to guarantee lifecycle stability.**

Paper 11 transforms the research prototype into an immutable, deployable appliance capable of surviving power loss and recovering from failures autonomously without traditional package-manager mutation.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Appliance Invariance Model restricts runtime mutations to volatile memory or versioned containers | Architecture (§III) | Clean |
| C2 | Read-only OverlayFS architecture eliminates boot-blocking filesystem corruption under power loss | Test results (0/50 corruptions) (§X) | Clean |
| C3 | Hardware watchdog tied to liveness ensures recovery from scheduler exhaustion | Validation (§X) | Clean |
| C4 | Blue/Green OTA deployment enables deterministic cutovers and automated rollbacks | State machine (§V) | Clean |
| C5 | Defense-in-depth security via TPM-backed ZTP, mTLS, and Secure Boot | Architecture (§VIII) | Clean |
| C6 | Priority-aware queue ejection prevents OOM during network partitions | Logic (§VII) | Clean |

## 4. Scope

### 4.1 In-Scope
- Immutable OS architecture (OverlayFS with read-only LowerDir and volatile UpperDir)
- Appliance Invariance Model ($H_{persistent}(t) = H_0$)
- Hardware watchdog timer (WDT) integration for OS-level liveness
- Blue/Green containerized OTA updates with deterministic rollback
- Zero-Touch Provisioning (TPM, mTLS, Secure Boot)
- Partition-tolerant priority-aware telemetry queue
- Empirical validation of power-loss resilience (n=50 test)

### 4.2 Out-of-Scope
- AI model design or training (Papers 1–3)
- System-level validation protocol (Paper 10 — P11 deploys, P10 validates)
- Flash storage endurance (Paper 12)
- Federated learning (Papers 13, 14)
- AR interface (Paper 15)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P11-INV-01 | Host filesystem MUST be mounted read-only during normal operation | OverlayFS LowerDir configuration |
| P11-INV-02 | Runtime logs and container writes MUST target volatile memory | tmpfs mounts for `/var/log` and Docker layers |
| P11-INV-03 | Hardware watchdog MUST trigger on liveness failure (not just process presence) | Integration with `/dev/watchdog` |
| P11-INV-04 | OTA updates MUST support atomic rollback on validation failure | Blue/Green container state machine |
| P11-INV-05 | Telemetry MUST use mTLS and prioritize data during partition recovery | Local SQLite buffer with priority ejection |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P5 (Hardware) | Hardware platform specification |
| **Upstream** | P9 (Orchestrator) | Orchestration control plane hosts deployments |
| **Upstream** | P10 (Validation) | Validation results inform deployment readiness |
| **Downstream** | P12 (Flash) | Storage endurance requirements for deployment medium |
| **Downstream** | P13 (FL) | Federated updates delivered via OTA pipeline |
| **Downstream** | P14 (Cross-Campus FL) | Multi-campus OTA coordination |

## 7. Verification Requirements

- OverlayFS active with `/` mounted as read-only LowerDir
- Temporary writes correctly mapped to `tmpfs` UpperDir
- 0% corruption rate across induced power-loss tests (n=50)
- Watchdog successfully forces hardware reboot upon induced kernel/scheduler freeze
- OTA state machine successfully rolls back a poisoned container deployment

## 8. What This Paper Does NOT Do

- Does **not** design AI models or training pipelines
- Does **not** perform system-level adversarial validation (defers to Paper 10)
- Does **not** address SD card lifespan or flash wear (defers to Paper 12)
- Does **not** implement federated aggregation (defers to Paper 13/14)
- Uptime claims are scoped to the specific 39-node trial deployment

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Health Check** | `benchmarks/uptime_monitor.py` | ✅ Verified (99.9% Uptime Logic) |
| **Crash Recovery** | `benchmarks/uptime_monitor.py` | ✅ Verified (Simulated MTTR) |
| **Docker Logic** | `benchmarks/cold_boot_latency.py` | ✅ Verified (Container Lifecycle) |

