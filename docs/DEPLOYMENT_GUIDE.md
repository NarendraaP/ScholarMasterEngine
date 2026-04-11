# DEPLOYMENT GUIDE

**Document Type**: Installation & Deployment Procedure  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Companion**: DEPLOYMENT_CONTRACT.md, FAILURE_INCIDENT_PLAYBOOKS.md  
**Status**: BINDING  
**Version**: 1.0.0

---

## SECTION A — SUPPORTED DEPLOYMENT MODEL

### A.1 Deployment Architecture
ScholarMasterEngine operates under a **single supported deployment model**:

| Property | Requirement |
|----------|-------------|
| **Location** | On-premise, within institutional campus perimeter. |
| **Hardware** | Campus-owned, campus-controlled hardware. |
| **Keys** | Cryptographic keys generated and held by institution. |
| **Vendor Access** | **NONE**. No remote access, no telemetry, no vendor SSH. |

### A.2 Unsupported Deployments
The following deployments are **NOT SUPPORTED** and will not function:

| Deployment Type | Status |
|-----------------|--------|
| Cloud-hosted (AWS, GCP, Azure) | UNSUPPORTED |
| Vendor-managed SaaS | UNSUPPORTED |
| Multi-tenant shared hardware | UNSUPPORTED |
| Containerized cloud orchestration | UNSUPPORTED |

---

## SECTION B — PRE-DEPLOYMENT CHECKLIST (HARD GATES)

Deployment **MUST FAIL** if any of the following checks fail. These are non-negotiable preconditions.

| # | Check | Verification Command | FAIL Condition |
|---|-------|---------------------|----------------|
| 1 | Privacy LED initializes | `GET /health/led` returns `{"state": "PRIVACY"}` | LED OFF or UNKNOWN |
| 2 | Volatile memory verification | `pytest tests/test_irreversibility.py` passes | Any test failure |
| 3 | Governance allowlist loads | `GET /health/governance` returns `{"allowlist_loaded": true}` | Allowlist missing |
| 4 | L3 watchdog active | `GET /health/watchdog` returns `{"frame_watchdog": "ACTIVE"}` | Watchdog inactive |
| 5 | Health endpoints respond | `GET /health` returns HTTP 200 | Timeout or error |
| 6 | Operator acknowledgment channel | MQTT or WebSocket to operator panel reachable | Connection refused |

### B.1 Hard Gate Enforcement
- If **ANY** check fails, deployment **MUST NOT proceed**.
- System will remain in **HALTED** state until all checks pass.
- No override mechanism exists.

---

## SECTION C — INSTALLATION FLOW

### C.1 Bootstrap Sequence

```
STEP 1: Hardware Power On
         └── BIOS/UEFI initializes
         └── Secure Boot verifies firmware signature

STEP 2: OS Boot
         └── Read-only root filesystem mounts
         └── Encrypted data partition unlocks (LUKS)

STEP 3: Service Initialization
         └── PrivacyLEDController.boot(LEDState.PRIVACY)
         └── EdgeAbstraction.start_watchdog()
         └── GovernanceFilter.load_allowlist()
         └── FailSafeController.initialize()

STEP 4: Health Check
         └── All endpoints respond
         └── System enters PRIVACY_ONLY mode

STEP 5: Operator Acknowledgment
         └── Operator sees PRIVACY LED
         └── Operator acknowledges via panel
         └── System transitions to ACTIVE mode
```

### C.2 Configuration Loading
Configuration is loaded from:
- `/etc/scholar/config.yaml` (main configuration)
- `/etc/scholar/allowlist.json` (governance allowlist)
- `/etc/scholar/consent.db` (consent registry)

**Constraint**: Configuration files are validated at boot. Invalid configuration → HALT.

### C.3 First-Run Verification
On first deployment, the following must complete:
1. Initial consent registry created (empty).
2. Audit log initialized with genesis entry.
3. LED state logged as PRIVACY.
4. Operator prompted to acknowledge.

### C.4 ACTIVE Mode Transition
System transitions from PRIVACY_ONLY to ACTIVE **ONLY** when:
- Operator explicitly acknowledges.
- LED transitions from GREEN to RED.
- Acknowledgment is logged.

---

## SECTION D — ENVIRONMENT CONSTRAINTS

### D.1 Supported Hardware

| Component | Requirement |
|-----------|-------------|
| **CPU** | x86_64 or ARM64 with TrustZone |
| **RAM** | Minimum 8GB (volatile processing) |
| **Storage** | SSD with LUKS encryption |
| **GPU** | Optional (CoreML/CUDA for acceleration) |
| **Network** | Ethernet (isolated VLAN preferred) |
| **LED** | Hardware GPIO or USB-controlled indicator |

### D.2 Unsupported Configurations

| Configuration | Status | Reason |
|---------------|--------|--------|
| **Swap enabled** | UNSUPPORTED | Raw data may persist to disk |
| **Network-attached storage** | UNSUPPORTED | Persistence risk |
| **Shared memory between VMs** | UNSUPPORTED | Isolation violation |
| **Hypervisor without memory isolation** | UNSUPPORTED | Cross-VM leakage |

### D.3 Network Assumptions
- Intranet connectivity to cameras, MQTT broker, operator panel.
- Outbound Federation (if enabled): HTTPS to coordinator only.
- No inbound connections from external networks.

---

## SECTION E — POST-DEPLOYMENT VERIFICATION

### E.1 Required Tests

| Test | Command | Pass Condition |
|------|---------|----------------|
| Irreversibility | `pytest tests/test_irreversibility.py` | All pass |
| Governance | `pytest tests/test_governance_filter.py` | All pass |
| Layer Contracts | `pytest tests/test_layer_contracts.py` | All pass |
| Fail-Safe | `pytest tests/test_failsafe_dropout.py` | All pass |
| Canonical Architecture | `pytest tests/test_canonical_architecture.py` | All pass |

### E.2 Observable Signals

| Signal | Expected State |
|--------|----------------|
| Privacy LED | GREEN (PRIVACY) or RED (ACTIVE) |
| Watchdog | ACTIVE (visible in logs) |
| Health endpoint | HTTP 200 |
| Audit log | Genesis entry present |

### E.3 Logs to Inspect

| Log | Location | Check For |
|-----|----------|-----------|
| Boot log | `/var/log/scholar/boot.log` | "Boot sequence complete" |
| LED log | `/var/log/scholar/led.log` | Initial state transition |
| Governance log | `/var/log/scholar/governance.log` | Allowlist loaded |

### E.4 Immediate HALT Conditions
System must be **HALTED IMMEDIATELY** if:
- Privacy LED reports OFF or UNKNOWN.
- Watchdog fails to initialize.
- Governance allowlist missing.
- Any pre-deployment check fails post-boot.

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0  
**Status**: BINDING
