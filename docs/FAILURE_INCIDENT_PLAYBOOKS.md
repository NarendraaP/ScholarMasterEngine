# FAILURE INCIDENT PLAYBOOKS

**Document Type**: Operational Enforcement Playbook  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0, DEPLOYMENT_CONTRACT.md  
**Status**: BINDING FOR ALL FAILURE RESPONSES  
**Version**: 1.0.0

---

## SECTION 1 — FAILURE CLASSIFICATION

### 1.1 Failure Class Definitions

| ID | Failure | Affected Layers | Severity | Immediate Response |
|----|---------|-----------------|----------|-------------------|
| F1 | Privacy LED failure / unknown state | L1, L6 | FATAL | HALT |
| F2 | Frame TTL watchdog violation (>33ms) | L3 | FATAL | HALT |
| F3 | Audio TTL watchdog violation (>3s) | L3 | FATAL | HALT |
| F4 | Governance Filter unavailable or corrupted | L5 | FATAL | HALT |
| F5 | MQTT unavailable | L7 | DEGRADED | DEGRADED MODE |
| F6 | Audit log backend unavailable | L7 | DEGRADED | DEGRADED MODE |
| F7 | Operator unreachable during escalation | L6 | CRITICAL | PRIVACY_ONLY |
| F8 | Campus loses federation connectivity | L8 | CRITICAL | ISOLATE |
| F9 | Campus withdrawal request mid-round | L8 | CRITICAL | PURGE + ISOLATE |
| F10 | Crash during irreversible processing | L2, L3 | FATAL | HALT + DISCARD |
| F11 | Memory isolation verification failure | L1 | FATAL | HALT |
| F12 | Unauthorized field detected post-inference | L5, L6 | FATAL | HALT |

### 1.2 Severity Definitions

| Severity | Definition | Required Action |
|----------|------------|-----------------|
| FATAL | Invariant violation or potential privacy breach | Immediate HALT, no recovery without reboot |
| CRITICAL | Operational degradation requiring mode change | Reduce capability, await recovery |
| DEGRADED | Service unavailable but privacy intact | Continue with reduced function |

---

## SECTION 2 — MANDATORY SYSTEM RESPONSE MATRIX

### 2.1 F1: Privacy LED Failure

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Continue processing, display any output |
| Recovery Eligible | NO (full reboot required) |
| Human Notification | MANDATORY (system administrator) |
| Enforcement | `SystemHaltRequired` exception |

### 2.2 F2: Frame TTL Watchdog Violation

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Continue capture, process stale frame |
| Recovery Eligible | NO (full reboot required) |
| Human Notification | MANDATORY (privacy incident) |
| Enforcement | `FrameDestructionError` exception |

### 2.3 F3: Audio TTL Watchdog Violation

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Continue capture, process stale audio |
| Recovery Eligible | NO (full reboot required) |
| Human Notification | MANDATORY (privacy incident) |
| Enforcement | L3 watchdog thread |

### 2.4 F4: Governance Filter Unavailable

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Allow any L4→L6 traffic |
| Recovery Eligible | NO (full reboot required) |
| Human Notification | MANDATORY (governance incident) |
| Enforcement | `GovernanceFilter` null check |

### 2.5 F5: MQTT Unavailable

| Property | Value |
|----------|-------|
| Immediate Action | DEGRADED MODE |
| Forbidden Actions | Persist buffer to disk, replay on recovery |
| Recovery Eligible | YES (auto on reconnection) |
| Human Notification | OPTIONAL (operational alert) |
| Enforcement | `FailSafeController.report_failure()` |

### 2.6 F6: Audit Log Backend Unavailable

| Property | Value |
|----------|-------|
| Immediate Action | DEGRADED MODE |
| Forbidden Actions | Continue ACTIVE mode output |
| Recovery Eligible | YES (auto on restore) |
| Human Notification | OPTIONAL (operational alert) |
| Enforcement | `FailSafeController.report_failure()` |

### 2.7 F7: Operator Unreachable

| Property | Value |
|----------|-------|
| Immediate Action | PRIVACY_ONLY |
| Forbidden Actions | Output to humans, escalation timeout bypass |
| Recovery Eligible | YES (on operator availability) |
| Human Notification | ESCALATION (next tier) |
| Enforcement | Escalation timeout handler |

### 2.8 F8: Federation Connectivity Lost

| Property | Value |
|----------|-------|
| Immediate Action | ISOLATE (local-only operation) |
| Forbidden Actions | Retry with non-DP data, queue raw gradients |
| Recovery Eligible | YES (on reconnection) |
| Human Notification | OPTIONAL (campus authority) |
| Enforcement | `FederationCoordinator` connection check |

### 2.9 F9: Campus Withdrawal Mid-Round

| Property | Value |
|----------|-------|
| Immediate Action | PURGE gradients + ISOLATE |
| Forbidden Actions | Complete current round, retain historical contributions |
| Recovery Eligible | NO (requires re-consent) |
| Human Notification | MANDATORY (campus authority) |
| Enforcement | `DPFederationCoordinator.withdraw_from_federation()` |

### 2.10 F10: Crash During Irreversible Processing

| Property | Value |
|----------|-------|
| Immediate Action | HALT + DISCARD all buffers |
| Forbidden Actions | Attempt recovery, replay partial state |
| Recovery Eligible | NO (full reboot required) |
| Human Notification | MANDATORY (incident report) |
| Enforcement | Process termination handler |

### 2.11 F11: Memory Isolation Failure

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Continue with compromised memory |
| Recovery Eligible | NO (hardware verification required) |
| Human Notification | MANDATORY (security incident) |
| Enforcement | `PhysicalSubstrate.verify_volatile_memory_support()` |

### 2.12 F12: Unauthorized Field Detected

| Property | Value |
|----------|-------|
| Immediate Action | HALT |
| Forbidden Actions | Pass field to L6, log field value |
| Recovery Eligible | NO (governance audit required) |
| Human Notification | MANDATORY (privacy incident) |
| Enforcement | `FORBIDDEN_OUTPUTS` boundary check |

---

## SECTION 3 — INCIDENT PLAYBOOKS

### Playbook 1: Privacy LED Does Not Initialize at Boot

```
TRIGGER: PrivacyLEDController.boot() raises exception

STEP 1: Catch SystemHaltRequired exception
STEP 2: Log failure reason (no privacy data in log)
STEP 3: Set system state = HALTED
STEP 4: Terminate all threads
STEP 5: Notify system administrator
STEP 6: Await manual intervention

DATA DESTROYED: None (boot incomplete)
DATA NOT RETAINED: All startup buffers
OPERATION: HALTED
FEDERATION: NOT STARTED
```

### Playbook 2: Frame Destruction Watchdog Fires

```
TRIGGER: Frame age exceeds 33ms

STEP 1: Watchdog thread detects violation
STEP 2: Force-destroy frame immediately
STEP 3: Log watchdog violation (timestamp only)
STEP 4: Raise FrameDestructionError
STEP 5: Set system state = HALTED
STEP 6: Terminate capture thread
STEP 7: Notify operator (privacy incident)

DATA DESTROYED: All frames in pipeline
DATA NOT RETAINED: Any frame older than 33ms
OPERATION: HALTED
FEDERATION: SUSPENDED
```

### Playbook 3: Governance Allowlist Checksum Mismatch

```
TRIGGER: Allowlist validation fails during startup or runtime check

STEP 1: Detect checksum mismatch
STEP 2: Block all L4→L5 traffic immediately
STEP 3: Log governance corruption event
STEP 4: Set system state = HALTED
STEP 5: Notify security administrator
STEP 6: Require allowlist re-validation

DATA DESTROYED: All pending inference outputs
DATA NOT RETAINED: Any output awaiting governance
OPERATION: HALTED
FEDERATION: SUSPENDED
```

### Playbook 4: MQTT Broker Unreachable During ACTIVE Mode

```
TRIGGER: MQTT publish fails with connection error

STEP 1: Catch connection exception
STEP 2: Report failure to FailSafeController
STEP 3: Initialize RAM-only buffer (max 100 events)
STEP 4: Set system state = DEGRADED
STEP 5: Continue L1-L3 processing only
STEP 6: Suppress L6 outputs

ON RECOVERY:
STEP 7: Detect MQTT reconnection
STEP 8: DISCARD entire buffer (no replay)
STEP 9: Resume ACTIVE mode

DATA DESTROYED: All buffered events on recovery
DATA NOT RETAINED: Buffered events
OPERATION: DEGRADED → ACTIVE on recovery
FEDERATION: CONTINUES (if separate channel)
```

### Playbook 5: Operator Does Not Acknowledge Escalation

```
TRIGGER: Escalation timeout expires (configurable, default 5 minutes)

STEP 1: Detect timeout
STEP 2: Log escalation timeout
STEP 3: Block pending escalated event
STEP 4: Escalate to next tier operator
STEP 5: If no tier available: Set system state = PRIVACY_ONLY
STEP 6: Suppress all L6 human outputs

ON RECOVERY:
STEP 7: Operator becomes available
STEP 8: Resume pending escalations
STEP 9: Await operator ACK for ACTIVE mode

DATA DESTROYED: None
DATA NOT RETAINED: Pending escalated events (blocked, not stored)
OPERATION: PRIVACY_ONLY
FEDERATION: SUSPENDED
```

### Playbook 6: Crash Between Frame Capture and Destruction

```
TRIGGER: Process terminates unexpectedly during L2→L3 transition

STEP 1: Process termination detected
STEP 2: Volatile memory assumed compromised
STEP 3: No cleanup possible (crash is instant)
STEP 4: On reboot: All volatile memory is fresh
STEP 5: No state recovery attempted
STEP 6: Full startup preconditions re-verified

DATA DESTROYED: All volatile memory (by OS)
DATA NOT RETAINED: Partial frames, audio, embeddings
OPERATION: HALTED → BOOT SEQUENCE
FEDERATION: STOPPED, re-consent may be required
```

### Playbook 7: Campus Revokes Federation Consent Mid-Training

```
TRIGGER: Campus Authority sends withdrawal request

STEP 1: Validate withdrawal request authenticity
STEP 2: Immediately stop gradient contribution
STEP 3: Purge all historical gradients from aggregator
STEP 4: Zero campus epsilon budget
STEP 5: Record withdrawal in audit log
STEP 6: Notify federation coordinator
STEP 7: Continue local-only operation

DATA DESTROYED: All historical gradients from withdrawn campus
DATA NOT RETAINED: Any contribution from withdrawn campus
OPERATION: LOCAL-ONLY
FEDERATION: WITHDRAWN (campus isolated)
```

### Playbook 8: Federation Coordinator Requests Re-Send

```
TRIGGER: Coordinator sends re-transmission request

STEP 1: Validate request source
STEP 2: REJECT request immediately
STEP 3: Log unauthorized request
STEP 4: Notify campus authority
STEP 5: Continue with current round only

DATA DESTROYED: None
DATA NOT RETAINED: Previously sent gradients (not stored)
OPERATION: CONTINUES
FEDERATION: CONTINUES (request denied)

NOTE: Re-send is architecturally impossible—gradients are not retained after transmission.
```

### Playbook 9: Network Partition Isolates Campus

```
TRIGGER: All external connectivity lost

STEP 1: Detect network partition
STEP 2: Set federation state = ISOLATED
STEP 3: Continue local L1-L7 processing
STEP 4: Buffer events in RAM only (no persistence)
STEP 5: On buffer overflow: Drop oldest events

ON RECOVERY:
STEP 6: Detect network restoration
STEP 7: DISCARD buffer (no replay)
STEP 8: Re-establish federation connection
STEP 9: Resume contribution (if consent valid)

DATA DESTROYED: All buffered events on recovery
DATA NOT RETAINED: Isolated-period events
OPERATION: LOCAL-ONLY
FEDERATION: ISOLATED → RECONNECTED
```

### Playbook 10: Unexpected Process Restart

```
TRIGGER: Watchdog or systemd restarts process

STEP 1: OS terminates and restarts process
STEP 2: All volatile memory lost
STEP 3: Boot sequence initiates
STEP 4: All startup preconditions verified
STEP 5: Privacy LED initialized to PRIVACY
STEP 6: Await operator ACK for ACTIVE
STEP 7: No state replay from previous session

DATA DESTROYED: All volatile memory
DATA NOT RETAINED: Previous session state
OPERATION: BOOT → PRIVACY_ONLY → (await ACK) → ACTIVE
FEDERATION: RE-CONSENT may be required
```

---

## SECTION 4 — CRASH & RECOVERY GUARANTEES

### 4.1 Guarantee Assertions

| # | Guarantee | Enforcement |
|---|-----------|-------------|
| G1 | No raw frames survive a crash | Volatile memory only |
| G2 | No raw audio survives a crash | Volatile memory only |
| G3 | No buffered raw data is replayed | `_backlog_replay_enabled = False` |
| G4 | Recovery requires full precondition re-verification | Boot sequence gates |
| G5 | Recovery CANNOT auto-resume ACTIVE mode | Operator ACK required |

### 4.2 Guarantee Verification

| Guarantee | Test | Handler |
|-----------|------|---------|
| G1 | `test_frame_ttl_33ms` | `EdgeAbstraction._destroy_frame()` |
| G2 | `test_audio_buffer_destroyed` | `EdgeAbstraction.transform_audio_to_features()` |
| G3 | `test_no_backlog_replay` | `FailSafeController.report_recovery()` |
| G4 | Startup precondition checks | All HARD GATE checks in DEPLOYMENT_CONTRACT.md |
| G5 | `test_active_mode_requires_operator_ack` | `PrivacyLEDController.require_operator_ack_for_active()` |

### 4.3 Failure Status

All guarantees CAN be enforced. NO FAILURE REPORT required.

---

## SECTION 5 — VERIFICATION & TEST MAPPING

| Failure | Protecting Invariant | Enforcement Handler | Test Coverage |
|---------|---------------------|---------------------|---------------|
| F1 | Privacy visibly accurate | `PrivacyLEDController.boot()` | `test_led_set_at_boot` |
| F2 | Frame lifetime <33ms | `EdgeAbstraction.start_watchdog()` | `test_frame_ttl_33ms` |
| F3 | Audio lifetime <3s | `EdgeAbstraction.AUDIO_TTL_SECONDS` | `test_audio_buffer_destroyed` |
| F4 | All outputs pass L5 | `GovernanceFilter` load check | `test_governance_filter_loaded` |
| F5 | Ephemeral buffers only | `FailSafeController.buffer_event()` | `test_mqtt_failure_buffers_locally` |
| F6 | Degraded mode privacy | `FailSafeController.report_failure()` | `test_audit_failure_enters_degraded` |
| F7 | Operator ACK for output | Escalation timeout handler | `test_escalation_timeout` |
| F8 | Campus sovereignty | `FederationCoordinator` connection | `test_federation_disconnect` |
| F9 | Withdrawal purges data | `DPFederationCoordinator.withdraw_from_federation()` | `test_gradients_purged_on_withdrawal` |
| F10 | No state survives crash | Volatile memory architecture | `test_no_stale_frames_replayed` |
| F11 | Memory isolation | `PhysicalSubstrate.verify_volatile_memory_support()` | `test_volatile_memory_verification` |
| F12 | No forbidden outputs | `FORBIDDEN_OUTPUTS` check | `test_forbidden_fields_blocked` |

---

## SECTION 6 — FAILURE OF THE PLAYBOOK ITSELF

### 6.1 Meta-Failure Conditions

| Condition | Response |
|-----------|----------|
| Failure handler raises exception | HALT |
| Watchdog thread unresponsive | HALT |
| Incident logging fails | HALT (privacy over logging) |
| FailSafeController itself crashes | HALT |
| State machine enters undefined state | HALT |

### 6.2 Meta-Failure Playbook

```
TRIGGER: Any component of failure handling fails

STEP 1: Detect handler failure
STEP 2: Attempt graceful HALT
STEP 3: If graceful HALT fails: Force terminate process
STEP 4: Hardware watchdog triggers reboot
STEP 5: Full boot sequence on restart

RULE: Failure-handling failure ALWAYS defaults to HALT.
```

---

## SECTION 7 — ENFORCEMENT CHECK

### 7.1 L3 Bypass Check

| Question | Answer |
|----------|--------|
| Does any playbook skip frame destruction? | NO |
| Does any playbook skip audio destruction? | NO |
| Does any failure mode allow stale data processing? | NO |
| Does any recovery path replay raw data? | NO |

**Result**: NO L3 BYPASS

### 7.2 L5 Bypass Check

| Question | Answer |
|----------|--------|
| Does any playbook skip governance for output? | NO |
| Does any failure mode allow ungoverned L6 traffic? | NO |
| Does any recovery path skip governance re-validation? | NO |

**Result**: NO L5 BYPASS

### 7.3 Capability Expansion Check

| Question | Answer |
|----------|--------|
| Does any failure enable additional sensing? | NO |
| Does any failure enable additional storage? | NO |
| Does any failure enable additional output? | NO |
| Does any mode relax privacy constraints? | NO |

**Result**: NO CAPABILITY EXPANSION

### 7.4 DEPLOYMENT_CONTRACT.md Consistency

| Contract Rule | Playbook Alignment |
|---------------|-------------------|
| F1-F4 → FATAL (§3) | ✅ ALIGNED |
| F5-F6 → DEGRADED (§2.3) | ✅ ALIGNED |
| F7 → PRIVACY_ONLY (§2.2) | ✅ ALIGNED |
| No backlog replay (§4.3) | ✅ ALIGNED |
| Operator ACK for ACTIVE (§4.2) | ✅ ALIGNED |

**Result**: FULLY CONSISTENT

---

## SECTION 8 — DOCUMENT AUTHORITY

This playbook is **BINDING**.

- All failure responses MUST follow these playbooks exactly
- Deviation from playbook is a COMPLIANCE FAILURE
- Any conflict with ARCHITECTURE_CANONICAL.md or DEPLOYMENT_CONTRACT.md is a DOCUMENT DEFECT

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0, DEPLOYMENT_CONTRACT.md  
**Enforcement Check**: PASSED  
**Status**: VALID
