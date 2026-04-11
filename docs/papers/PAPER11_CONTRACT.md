# PAPER 11 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | From Lab to Lecture Hall: Production-Grade Edge MLOps Architecture for Privacy-Preserving Educational AI |
| **Paper ID** | P11 |
| **Layer** | Infrastructure (L6 — Production MLOps) |
| **Author** | Narendra Babu P |
| **Status** | Corrected (CC v2.3.0 aligned) |

## 2. Primary Contribution

**A production-grade MLOps architecture for deploying, monitoring, and maintaining edge AI systems at institutional scale — covering containerization, OTA model updates, reliability engineering, defense-in-depth security, observability, and data governance for a privacy-preserving educational AI deployment.**

Paper 11 transforms the research prototype (Papers 1–10) into a deployable production system with enterprise-grade reliability properties.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Containerized deployment (Docker + systemd) enables reproducible, atomic rollback | Deployment architecture (§III) | Clean |
| C2 | OTA model updates via differential patching reduce bandwidth by 92% vs full model transfer | OTA pipeline (§V); patch size analysis | Clean |
| C3 | 99.97% uptime over 90-day field trial (39 nodes) | Longitudinal data (§X) | Clean |
| C4 | Defense-in-depth security (not "Zero Trust") with mTLS, RBAC, and binary signing | Security architecture (§VIII) | Clean — "defense-in-depth," not "Zero-Trust" |
| C5 | Watchdog + health-check pipeline achieves MTTR < 45 seconds for crash recovery | Reliability engineering (§IV) | Clean |
| C6 | TCO 73% lower than equivalent cloud-based deployment over 5 years | Economic analysis (§XI) | Clean |

## 4. Scope

### 4.1 In-Scope
- Docker containerization with systemd orchestration
- OTA model update pipeline with differential patching
- Reliability engineering (watchdog, health checks, crash recovery)
- Defense-in-depth security architecture
- Full-stack observability (Prometheus, Grafana, MQTT telemetry)
- Data governance and GDPR-aligned regulatory controls
- Economic analysis (TCO vs cloud alternatives)

### 4.2 Out-of-Scope
- AI model design or training (Papers 1–3)
- System-level validation protocol (Paper 10 — P11 deploys, P10 validates)
- Flash storage endurance (Paper 12)
- Federated learning (Papers 13, 14)
- AR interface (Paper 15)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P11-INV-01 | All model updates MUST be cryptographically signed before deployment | Binary signing verification at node level |
| P11-INV-02 | Watchdog MUST restart crashed containers within 60 seconds | systemd watchdog with configurable timeout |
| P11-INV-03 | MQTT telemetry MUST use mTLS — no plaintext transport | Certificate enforcement at broker level |
| P11-INV-04 | OTA updates MUST support atomic rollback on verification failure | A/B partition strategy with fallback |
| P11-INV-05 | No raw biometric data SHALL transit the telemetry pipeline | GovernanceFilter (Paper 9) upstream of telemetry |

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

- Container deployment + rollback in < 120 seconds
- OTA differential patch size ≤ 10% of full model size
- Crash recovery (MTTR) < 60 seconds
- 90-day uptime ≥ 99.9% on field trial nodes
- mTLS enforcement: plaintext MQTT connections rejected
- No biometric data in any telemetry payload (audit check)

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

