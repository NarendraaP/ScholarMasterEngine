# Deployment & Operations Contract (DOC)

**Status**: REQUIRED FOR ANY DEPLOYMENT  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Scope**: Edge Nodes, Campus Aggregators, Federation Coordinator  
**Version**: 1.0

---

## 1. Purpose

This document defines the non-negotiable conditions under which ScholarMasterEngine may:

- **Start**
- **Continue running**
- **Enter degraded operation**
- **Shut down safely**

> [!CAUTION]
> The system is not permitted to operate outside the constraints defined here.

---

## 2. Roles & Authority Model

### 2.1 Defined Roles

| Role | Authority | Limitations |
|------|-----------|-------------|
| **Operator** | Acknowledge escalations, view outputs | Cannot override governance |
| **Campus Authority** | Grant/revoke consent, join/withdraw federation | Cannot bypass irreversibility |
| **Federation Coordinator** | Aggregate DP gradients | Cannot request raw data |
| **System** | Autonomous enforcement | Cannot relax privacy under any condition |

> [!IMPORTANT]
> **Rule**: No role may assume responsibilities outside this table.

---

## 3. Mandatory Startup Preconditions (HARD GATES)

The system **MUST NOT START** unless all conditions pass.

### 3.1 Hardware & Memory

- [ ] Volatile memory isolation verified (L1)
- [ ] No writable persistent buffers for raw frames/audio
- [ ] Memory watchdog initialized

**Failure → HALT**

### 3.2 Privacy Signaling

- [ ] Privacy LED initialized successfully
- [ ] LED state must be one of:
  - `PRIVACY`
  - `ACTIVE`
- [ ] LED failure or unknown state is fatal

**Failure → HALT**

### 3.3 Governance Layer

- [ ] L5 Governance Filter loaded
- [ ] Allowlist validated
- [ ] Event ordering enforced:

```
INFERENCE_COMPLETE
  → COMPLIANCE_CHECKED
    → APPROVED_FOR_OUTPUT
```

**Failure → HALT**

### 3.4 Irreversibility Watchdogs

- [ ] Frame TTL watchdog (<33ms) active
- [ ] Audio TTL watchdog (<3s) active
- [ ] Destruction callbacks registered

**Failure → HALT**

### 3.5 Operator Presence (if required)

If escalation is enabled:
- [ ] Operator acknowledgment loop must be reachable

**Failure → DEGRADED (no output)**

---

## 4. Allowed Operating Modes

### 4.1 ACTIVE

| Enabled | Forbidden |
|---------|-----------|
| Full L1–L8 flow | Any raw data persistence |
| Human outputs | Governance bypass |
| Federation (if consented) | |

### 4.2 PRIVACY_ONLY

| Enabled | Triggered by |
|---------|--------------|
| L1–L4 processing | Operator unavailable |
| No human output | Partial network failure |
| No federation | |

### 4.3 DEGRADED

| Enabled | Triggered by |
|---------|--------------|
| Sensing + irreversibility only | MQTT unavailable |
| Logging disabled | Audit backend unavailable |
| Outputs suppressed | |

### 4.4 HALTED

| Enabled | Triggered by |
|---------|--------------|
| Nothing | LED failure |
| | Irreversibility failure |
| | Governance corruption |
| | Memory invariant violation |

---

## 5. Non-Negotiable Fail-Safe Rules

The system **MUST**:

| # | Rule | Violation Consequence |
|---|------|----------------------|
| 1 | ❌ Never display RGB imagery | IMMEDIATE HALT |
| 2 | ❌ Never persist raw frames or audio | IMMEDIATE HALT |
| 3 | ❌ Never replay buffered raw data after crash | IMMEDIATE HALT |
| 4 | ❌ Never bypass governance under failure | IMMEDIATE HALT |
| 5 | ❌ Never downgrade privacy in DEGRADED mode | IMMEDIATE HALT |
| 6 | ❌ Never contribute to federation without consent | IMMEDIATE HALT |
| 7 | ❌ Never continue if Privacy LED state is unknown | IMMEDIATE HALT |

---

## 6. Crash & Recovery Semantics

### On crash:

1. Volatile memory is assumed compromised
2. All raw buffers are discarded
3. No state replay is allowed

### Recovery requires:

1. Full reboot
2. All startup preconditions re-verified

---

## 7. Deployment Acceptance Checklist

> [!WARNING]
> Deployment is **INVALID** unless all are true:

- [ ] Privacy LED verified
- [ ] Irreversibility tests passing
- [ ] Governance allowlist locked
- [ ] Failure handlers registered
- [ ] Consent registry reachable
- [ ] Operator escalation path tested
- [ ] Federation consent verified (if enabled)

---

## 8. Contract Authority

This document is **binding**.

- Operators may not override it
- Tools may not reinterpret it
- Any conflict with runtime behavior is treated as a **system defect**

---

**Document Version**: 1.0  
**Effective Date**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)
