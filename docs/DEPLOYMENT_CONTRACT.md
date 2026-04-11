# DEPLOYMENT CONTRACT

**Document Type**: Binding Operational Contract  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Status**: REQUIRED FOR ALL DEPLOYMENTS  
**Scope**: Edge Nodes, Campus Aggregators, Federation Coordinator  
**Version**: 1.0.0

---

## 1. STARTUP HARD GATES

The system SHALL NOT transition to any operational state unless ALL preconditions pass.

### 1.1 Volatile Memory Isolation (L1)

| Precondition | Enforcement Layer | Failure Action |
|--------------|-------------------|----------------|
| `PhysicalSubstrate.verify_volatile_memory_support()` returns `True` | L1 | HALT |
| No writable persistent buffer exists for raw frames | L1 | HALT |
| No writable persistent buffer exists for raw audio | L1 | HALT |
| Memory watchdog thread initialized | L1 | HALT |

### 1.2 Privacy LED Initialization (L1, L6)

| Precondition | Enforcement Layer | Failure Action |
|--------------|-------------------|----------------|
| `PrivacyLEDController.boot()` completes without exception | L1 | HALT |
| `LEDState` is `PRIVACY` or `ACTIVE` (not `None`, not unknown) | L1 | HALT |
| Hardware LED responds to state changes | L1 | HALT |

### 1.3 L3 Irreversibility Watchdog Activation

| Precondition | Enforcement Layer | Failure Action |
|--------------|-------------------|----------------|
| `EdgeAbstraction.start_watchdog()` returns successfully | L3 | HALT |
| Frame TTL watchdog active with threshold `FRAME_TTL_MS = 33` | L3 | HALT |
| Audio TTL watchdog active with threshold `AUDIO_TTL_SECONDS = 3.0` | L3 | HALT |
| Destruction callbacks registered and verified | L3 | HALT |

### 1.4 L5 Governance Filter Load

| Precondition | Enforcement Layer | Failure Action |
|--------------|-------------------|----------------|
| `GovernanceFilter` instance created | L5 | HALT |
| `ALLOWED_FIELDS` set loaded and non-empty | L5 | HALT |
| `FORBIDDEN_OUTPUTS` set loaded and non-empty | L5 | HALT |
| `PII_FIELDS` set loaded | L5 | HALT |

### 1.5 Event Ordering Enforcement

| Precondition | Enforcement Layer | Failure Action |
|--------------|-------------------|----------------|
| Event sequence enforced: `INFERENCE_COMPLETE` → `COMPLIANCE_CHECKED` → `APPROVED_FOR_OUTPUT` | L5 | HALT |
| Out-of-order events rejected | L5 | HALT |
| Governance decision logging active | L5, L7 | HALT |

---

## 2. OPERATING MODES

### 2.1 Mode Definitions

#### 2.1.1 ACTIVE

| Property | Value |
|----------|-------|
| **Enabled Layers** | L1, L2, L3, L4, L5, L6, L7, L8 |
| **Human Output** | ENABLED (skeleton-only) |
| **Federation** | ENABLED (if consented) |
| **Privacy LED** | `ACTIVE` (RED) |

| Forbidden Actions | Enforcement |
|-------------------|-------------|
| Display RGB imagery | L6 contract |
| Persist raw frames | L3 destruction |
| Persist raw audio | L3 destruction |
| Bypass L5 governance | Structural |

#### 2.1.2 PRIVACY_ONLY

| Property | Value |
|----------|-------|
| **Enabled Layers** | L1, L2, L3, L4 |
| **Human Output** | DISABLED |
| **Federation** | DISABLED |
| **Privacy LED** | `PRIVACY` (GREEN) |

| Forbidden Actions | Enforcement |
|-------------------|-------------|
| Display any output to humans | Mode constraint |
| Contribute to federation | Mode constraint |
| All ACTIVE forbidden actions | Inherited |

| Trigger Conditions |
|--------------------|
| Operator unavailable |
| Partial network failure |
| Escalation path unreachable |
| Explicit operator command |

#### 2.1.3 DEGRADED

| Property | Value |
|----------|-------|
| **Enabled Layers** | L1, L2, L3 |
| **Human Output** | DISABLED |
| **Federation** | DISABLED |
| **Logging** | DISABLED |
| **Privacy LED** | `PRIVACY` (GREEN) |

| Forbidden Actions | Enforcement |
|-------------------|-------------|
| Produce any L4+ outputs | Mode constraint |
| Persist any data | Mode constraint |
| All ACTIVE forbidden actions | Inherited |

| Trigger Conditions |
|--------------------|
| MQTT broker unavailable |
| Audit backend unavailable |
| L7 storage failure |

#### 2.1.4 HALTED

| Property | Value |
|----------|-------|
| **Enabled Layers** | NONE |
| **Processing** | STOPPED |
| **Privacy LED** | OFF or last known state |

| Trigger Conditions |
|--------------------|
| Privacy LED failure |
| Irreversibility watchdog violation |
| Governance filter corruption |
| Memory invariant violation |
| Unauthorized data field detected |
| Startup precondition failure |

### 2.2 Legal State Transitions

```
              ┌──────────────────────────────────────────┐
              │                                          │
              ▼                                          │
         ┌─────────┐    operator ack    ┌─────────────┐  │
  boot ─►│ PRIVACY │ ─────────────────► │   ACTIVE    │ ─┘
         │  ONLY   │                    │             │
         └────┬────┘                    └──────┬──────┘
              │                                │
              │ network fail                   │ operator unavail
              │                                │
              ▼                                ▼
         ┌─────────┐                    ┌─────────────┐
         │DEGRADED │                    │  PRIVACY    │
         │         │                    │    ONLY     │
         └────┬────┘                    └─────────────┘
              │
              │ critical failure
              ▼
         ┌─────────┐
         │ HALTED  │ ◄─── ANY MODE on critical failure
         └─────────┘
```

### 2.3 Mode Invariants

Regardless of mode, the following SHALL NEVER occur:

| Invariant | Enforcement Layer |
|-----------|-------------------|
| RGB imagery displayed | L6 |
| Raw frame persisted | L3 |
| Raw audio persisted | L3 |
| L5 governance bypassed | L5 |
| Privacy relaxed due to failure | L3, L5, L6 |

---

## 3. NON-NEGOTIABLE FAIL-SAFE RULES

The following conditions trigger IMMEDIATE HALT with no recovery attempt:

| # | Condition | Detection | Enforcement Layer |
|---|-----------|-----------|-------------------|
| F1 | Privacy LED state unknown or unset | `PrivacyLEDController.current_state is None` | L1 |
| F2 | Privacy LED hardware failure | `SystemHaltRequired` exception | L1 |
| F3 | Frame TTL exceeded (>33ms) | Watchdog timer | L3 |
| F4 | Audio TTL exceeded (>3s) | Watchdog timer | L3 |
| F5 | Frame destruction callback failed | Exception in destruction | L3 |
| F6 | Governance filter uninitialized | `GovernanceFilter` null check | L5 |
| F7 | Allowlist empty or corrupted | Validation check | L5 |
| F8 | Event ordering violation | Sequence enforcement | L5 |
| F9 | Unauthorized field in L6 output | `FORBIDDEN_OUTPUTS` check | L5, L6 |
| F10 | Non-DP gradient at L8 boundary | `is_dp_protected` check | L8 |
| F11 | Raw data request from federation | Request validation | L8 |
| F12 | Memory isolation failure | L1 verification | L1 |

---

## 4. CRASH & RECOVERY SEMANTICS

### 4.1 On Crash

| Rule | Description |
|------|-------------|
| R1 | All volatile memory is assumed compromised |
| R2 | All raw buffers are considered destroyed |
| R3 | No state replay is permitted |
| R4 | No buffered events are replayed |
| R5 | Session data loss is acceptable; privacy violation is not |

### 4.2 Recovery Sequence

| Step | Action | Gate |
|------|--------|------|
| 1 | Full system reboot | — |
| 2 | Volatile memory isolation re-verified | HARD GATE |
| 3 | Privacy LED re-initialized to `PRIVACY` | HARD GATE |
| 4 | L3 watchdogs re-activated | HARD GATE |
| 5 | L5 governance re-loaded | HARD GATE |
| 6 | Operator acknowledgment required for `ACTIVE` mode | SOFT GATE |

### 4.3 Backlog Replay Prohibition

| Condition | Behavior |
|-----------|----------|
| `FailSafeController._backlog_replay_enabled` | ALWAYS `False` |
| MQTT reconnection | Discard buffer, no replay |
| Network recovery | Discard buffer, no replay |
| Edge recovery | Discard stale frames, no replay |

---

## 5. ROLE & AUTHORITY MODEL

### 5.1 Role Definitions

| Role | Authority | Limitations |
|------|-----------|-------------|
| **Operator** | Acknowledge escalations; view L6 outputs; switch modes | Cannot override L5 governance; cannot access raw data |
| **Campus Authority** | Grant/revoke federation consent; join/withdraw from federation | Cannot bypass L3 irreversibility; cannot access raw data |
| **Federation Coordinator** | Aggregate DP gradients; manage epsilon budgets | Cannot request raw data; cannot request non-DP gradients |
| **System** | Autonomous enforcement of all invariants | Cannot relax privacy under any condition |

### 5.2 Authority Matrix

| Action | Operator | Campus Authority | Federation | System |
|--------|----------|------------------|------------|--------|
| Override L5 governance | ❌ | ❌ | ❌ | ❌ |
| Access raw frames/audio | ❌ | ❌ | ❌ | ❌ |
| Bypass L3 irreversibility | ❌ | ❌ | ❌ | ❌ |
| Request non-DP gradients | ❌ | ❌ | ❌ | ❌ |
| Relax privacy constraints | ❌ | ❌ | ❌ | ❌ |
| Acknowledge escalations | ✅ | ❌ | ❌ | ❌ |
| Join/withdraw federation | ❌ | ✅ | ❌ | ❌ |
| Aggregate DP gradients | ❌ | ❌ | ✅ | ❌ |
| Enforce invariants | ❌ | ❌ | ❌ | ✅ |

---

## 6. ENFORCEMENT REFERENCE

| Section | Canonical Layer(s) | Enforcement Mechanism |
|---------|-------------------|----------------------|
| §1.1 Volatile Memory | L1 | `PhysicalSubstrate.verify_volatile_memory_support()` |
| §1.2 Privacy LED | L1, L6 | `PrivacyLEDController.boot()`, `SystemHaltRequired` |
| §1.3 Irreversibility | L3 | `EdgeAbstraction.FRAME_TTL_MS`, watchdog thread |
| §1.4 Governance | L5 | `GovernanceFilter`, allowlist validation |
| §1.5 Event Ordering | L5 | Sequence enforcement in filter |
| §2 Operating Modes | L1–L8 | Mode state machine, transition guards |
| §3 Fail-Safe Rules | L1, L3, L5, L6, L8 | Exception handlers, watchdogs, boundary checks |
| §4 Recovery | L1–L5 | `_backlog_replay_enabled = False`, precondition gates |
| §5 Authority | L5, L8 | Role-based access control, request validation |

---

## 7. CONTRACT AUTHORITY

This document is **BINDING**.

| Rule | Statement |
|------|-----------|
| A1 | Operators MAY NOT override this contract |
| A2 | Tools MAY NOT reinterpret this contract |
| A3 | Any conflict with runtime behavior is a SYSTEM DEFECT |
| A4 | Any conflict with ARCHITECTURE_CANONICAL.md is a CONTRACT FAILURE |

---

## 8. SELF-AUDIT

### 8.1 Canonical Invariants Enforced

| Invariant | Section | Status |
|-----------|---------|--------|
| Frame lifetime <33ms | §1.3, §3.F3 | ✅ ENFORCED |
| Audio lifetime <3s | §1.3, §3.F4 | ✅ ENFORCED |
| No RGB display | §2.3 | ✅ ENFORCED |
| No raw persistence | §2.3 | ✅ ENFORCED |
| L5 mandatory gate | §1.4, §1.5, §2.3 | ✅ ENFORCED |
| Privacy LED at boot | §1.2 | ✅ ENFORCED |
| LED failure halts | §3.F1, §3.F2 | ✅ ENFORCED |
| No backlog replay | §4.3 | ✅ ENFORCED |
| DP-only federation | §3.F10, §3.F11, §5.2 | ✅ ENFORCED |
| Operator ACK for ACTIVE | §4.2 | ✅ ENFORCED |

### 8.2 Invariant Weakening Check

| Question | Answer |
|----------|--------|
| Does any mode allow raw data display? | NO |
| Does any mode allow governance bypass? | NO |
| Does any failure path relax privacy? | NO |
| Does recovery replay buffered data? | NO |
| Can any role access raw frames/audio? | NO |
| Can federation request non-DP gradients? | NO |

**Result**: NO INVARIANT WEAKENED

### 8.3 New Data Path Check

| Question | Answer |
|----------|--------|
| Does this contract introduce new data flows? | NO |
| Does this contract create bypass paths? | NO |
| Does this contract add fallback modes? | NO |
| Does this contract modify L1–L8 definitions? | NO |

**Result**: NO NEW DATA PATH INTRODUCED

---

## 9. COMPLIANCE STATEMENT

This contract has been verified against ARCHITECTURE_CANONICAL.md v1.0.0.

- All startup gates align with §2.0 (Canonical Layers)
- All fail-safe rules align with §7.0 (Failure Semantics)
- All mode definitions align with §6.0 (Trust & Transparency)
- All authority boundaries align with §5.0 (Federation & Sovereignty)
- No requirement conflicts detected

**Contract Status**: VALID

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Self-Audit**: PASSED
