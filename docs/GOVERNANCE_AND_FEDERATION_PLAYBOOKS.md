# GOVERNANCE AND FEDERATION PLAYBOOKS

**Document Type**: Enforcement Playbook  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0, DEPLOYMENT_CONTRACT.md  
**Scope**: L5 Governance, L8 Federation  
**Status**: BINDING  
**Version**: 1.0.0

---

## SECTION 1 — GOVERNANCE AUTHORITY MODEL (L5)

### 1.1 L5 Approval Authority

| Category | L5 May Approve | Condition |
|----------|---------------|-----------|
| Skeleton keypoints | YES | ≤34 points, no RGB |
| Engagement score | YES | Aggregated, no individual identity |
| Compliance status | YES | Binary (compliant/non-compliant) |
| Zone occupancy count | YES | Anonymous count only |
| Acoustic dB level | YES | No speech content |
| Posture classification | YES | Category only (e.g., "seated") |

### 1.2 L5 Forbidden Approvals

| Category | L5 Must REJECT | Reason |
|----------|---------------|--------|
| Raw RGB frame | ALWAYS | Irreversibility violation |
| Raw audio waveform | ALWAYS | Irreversibility violation |
| Face embedding | ALWAYS | Identity reconstruction risk |
| Biometric vector | ALWAYS | PII |
| Student name | ALWAYS | Direct identifier |
| Student ID (unhashed) | ALWAYS | Direct identifier |
| Location trajectory | ALWAYS | Tracking risk |
| Voice sample | ALWAYS | Biometric |

### 1.3 L5 Mandatory Escalation

| Condition | Action |
|-----------|--------|
| Field not in ALLOWED_FIELDS and not in PII_FIELDS | ESCALATE |
| Confidence score below threshold | ESCALATE |
| Multiple individuals in frame | ESCALATE |
| Anomaly detection triggered | ESCALATE |
| Operator-defined keywords present | ESCALATE |

**RULE**: If payload is ambiguous → ESCALATE. Never auto-approve ambiguous payloads.

### 1.4 L5 Unconditional DROP

| Condition | Action | Logging |
|-----------|--------|---------|
| Field in FORBIDDEN_OUTPUTS | DROP | Log field name only |
| Payload fails allowlist check | DROP | Log rejection reason |
| PII field not redactable | DROP | Log field type |
| Sequence violation detected | DROP | Log sequence state |

### 1.5 Transformation Rules

| Transform | Input | Output | Condition |
|-----------|-------|--------|-----------|
| REDACT | PII field present | `[REDACTED:{hash}]` | Field in PII_FIELDS |
| AGGREGATE | Individual count | Zone total | Privacy threshold (min 5) |
| ANONYMIZE | Student ID | Privacy hash | Always for external output |
| SUPPRESS | Low-confidence inference | Empty | Confidence < threshold |

---

## SECTION 2 — GOVERNANCE EVENT ORDERING (HARD CONSTRAINT)

### 2.1 Valid Sequence

```
INFERENCE_COMPLETE
    │
    ▼
COMPLIANCE_CHECKED
    │
    ▼
APPROVED_FOR_OUTPUT
    │
    ├──► HUMAN_OUTPUT (L6)
    │
    └──► FEDERATION (L8)
```

### 2.2 Illegal Sequences

| Sequence | Violation | Response |
|----------|-----------|----------|
| INFERENCE_COMPLETE → HUMAN_OUTPUT | Skipped COMPLIANCE_CHECKED | HALT |
| INFERENCE_COMPLETE → FEDERATION | Skipped COMPLIANCE_CHECKED | HALT |
| COMPLIANCE_CHECKED → FEDERATION (without APPROVED_FOR_OUTPUT) | Skipped approval | HALT |
| APPROVED_FOR_OUTPUT → INFERENCE_COMPLETE | Out of order | HALT |
| Any event before INFERENCE_COMPLETE | Premature | DROP |

### 2.3 Blocking Behavior

| Violation Type | Immediate Action | Recovery |
|----------------|------------------|----------|
| Skipped state | Block pipeline | HALT, reboot required |
| Out-of-order | Block pipeline | HALT, reboot required |
| Duplicate state | Log warning | Continue (idempotent) |

### 2.4 Logging Requirements

| Event | Must Log | Must NOT Log |
|-------|----------|--------------|
| Sequence transition | Timestamp, event type | Payload content |
| Sequence violation | Violation type, expected vs actual | Any inference data |
| Pipeline block | Block reason | User-identifying info |

---

## SECTION 3 — CONSENT MODEL

### 3.1 Consent Types

| Type | Scope | Grantor | Duration |
|------|-------|---------|----------|
| Individual | Single student | Student/Guardian | Until revoked |
| Institutional | Campus-wide | Campus Authority | Academic term |
| Temporal | Time-bound | Any grantor | Specified period |
| Purpose-bound | Specific use | Any grantor | Until purpose complete |

### 3.2 Consent Assertion

| Consent Type | Assertion Method | Verification |
|--------------|------------------|--------------|
| Individual | Signed consent form → system entry | Hash in consent registry |
| Institutional | Campus Authority declaration | Campus certificate |
| Temporal | Start/end timestamps | Time comparison |
| Purpose-bound | Purpose code + consent hash | Registry lookup |

### 3.3 Consent Verification Points

| Layer | Verification | Failure Action |
|-------|--------------|----------------|
| L4 (Inference) | Individual consent for identity processing | Anonymous-only mode |
| L6 (Output) | Consent for visibility | Suppress output |
| L8 (Federation) | Institutional consent | Isolate campus |

### 3.4 Consent Revocation

| Revocation Type | Trigger | Propagation |
|-----------------|---------|-------------|
| Individual | Student/Guardian request | Immediate effect |
| Institutional | Campus Authority request | End of current cycle |
| Temporal | Expiry | Automatic |
| Purpose-bound | Purpose completion | Automatic |

### 3.5 Revocation Propagation

```
REVOCATION_RECEIVED
    │
    ▼
VERIFY_AUTHORITY
    │
    ▼
HALT_PROCESSING (for subject)
    │
    ▼
PURGE_PENDING_DATA
    │
    ▼
UPDATE_CONSENT_REGISTRY
    │
    ▼
PROPAGATE_TO_FEDERATION (if applicable)
```

**RULE**: Revocation MUST take effect BEFORE next inference cycle.

---

## SECTION 4 — FEDERATION PARTICIPATION PLAYBOOK (L8)

### 4.1 Campus Joining Federation

```
STEP 1: Campus Authority submits join request
STEP 2: Verify institutional consent
STEP 3: Verify DP capability (epsilon budget initialized)
STEP 4: Register campus in federation
STEP 5: Initialize gradient buffer
STEP 6: Log join event

DATA SHARED: Campus ID, DP parameters
FORBIDDEN: Any embeddings, features, identifiers
```

### 4.2 Campus Contributing Gradients

```
STEP 1: Receive gradient from local training
STEP 2: Verify is_dp_protected == True
STEP 3: Verify epsilon budget sufficient
STEP 4: Deduct epsilon from budget
STEP 5: Transmit gradient to coordinator
STEP 6: Discard local gradient copy
STEP 7: Log contribution (checksum only)

DATA SHARED: DP-protected gradient
FORBIDDEN: Raw gradient, embeddings, identifiers
```

### 4.3 Campus Temporarily Offline

```
STEP 1: Detect connection loss
STEP 2: Set federation state = ISOLATED
STEP 3: Continue local processing
STEP 4: Accumulate gradients locally (capped)
STEP 5: On reconnection: Contribute accumulated gradients
STEP 6: Resume normal participation

DATA SHARED: Accumulated DP gradients (on recovery)
FORBIDDEN: Queueing non-DP data
```

### 4.4 Campus Revoking Consent

```
STEP 1: Campus Authority submits revocation
STEP 2: Verify authority
STEP 3: Halt gradient contribution immediately
STEP 4: Notify federation coordinator
STEP 5: Await confirmation of gradient purge
STEP 6: Set federation state = WITHDRAWN
STEP 7: Continue local-only operation

DATA PURGED: All historical gradients from this campus
FORBIDDEN: Completing current round
```

### 4.5 Campus Permanent Withdrawal

```
STEP 1: Campus Authority submits withdrawal request
STEP 2: Verify authority
STEP 3: Halt all federation activity
STEP 4: Request gradient purge from coordinator
STEP 5: Await purge confirmation
STEP 6: Zero epsilon budget
STEP 7: Remove from federation registry
STEP 8: Log withdrawal (timestamp only)

DATA PURGED: All contributions, all checksums
NEVER RETAINED: Any trace of participation
```

### 4.6 Global Model Update Received

```
STEP 1: Receive encrypted model update
STEP 2: Verify coordinator signature
STEP 3: Verify model checksum
STEP 4: Apply update to local model
STEP 5: Log update application

DATA RECEIVED: Aggregated model weights
FORBIDDEN: Receiving individual campus contributions
```

### 4.7 Federation Coordinator Unreachable

```
STEP 1: Detect connection failure
STEP 2: Set federation state = COORDINATOR_UNAVAILABLE
STEP 3: Buffer gradients locally (RAM-only, capped)
STEP 4: Continue local processing
STEP 5: Retry connection periodically
STEP 6: On recovery: Contribute buffered gradients
STEP 7: Buffer discarded if full (no persistence)

DATA BUFFERED: DP gradients (ephemeral)
FORBIDDEN: Persisting gradients to disk
```

### 4.8 Gradient Rejected by Coordinator

```
STEP 1: Receive rejection response
STEP 2: Log rejection reason
STEP 3: Discard rejected gradient
STEP 4: Notify campus authority (if policy-related)
STEP 5: Continue participation (unless consent issue)

DATA DISCARDED: Rejected gradient
FORBIDDEN: Retry with modified non-DP gradient
```

### 4.9 Consent Mismatch Detected Mid-Round

```
STEP 1: Coordinator reports consent mismatch
STEP 2: Halt contribution immediately
STEP 3: Verify local consent registry
STEP 4: If mismatch confirmed: Withdraw from round
STEP 5: If mismatch false: Report to coordinator
STEP 6: Re-verify consent before next round

DATA AFFECTED: Current round contribution (discarded)
FORBIDDEN: Continuing without consent verification
```

---

## SECTION 5 — RIGHT TO BE FORGOTTEN (RTBF) ENFORCEMENT

### 5.1 RTBF Scope

| Layer | Data Affected | Deletion Method |
|-------|---------------|-----------------|
| L7 (Audit) | Events referencing subject | Crypto-shredding |
| L5 (Governance) | Decisions involving subject | Record deletion |
| L8 (Federation) | Gradient contributions | Purge + recompute |

### 5.2 RTBF Processing

```
STEP 1: Receive RTBF request
STEP 2: Verify requestor authority
STEP 3: Identify all subject data:
         - Audit log entries
         - Governance decisions
         - Consent records
         - Federation contributions (if any)
STEP 4: Crypto-shred at L7 (delete encryption key)
STEP 5: Delete at L5 (remove records)
STEP 6: Request federation purge at L8
STEP 7: Await federation confirmation
STEP 8: Generate deletion certificate

MUST DELETE: All identifiable records
CANNOT RECONSTRUCT: Subject identity from remaining data
```

### 5.3 Crypto-Shredding Procedure

| Step | Action |
|------|--------|
| 1 | Identify subject's encryption key |
| 2 | Delete key from key management service |
| 3 | Encrypted records become unreadable |
| 4 | Log shredding event (subject hash only) |

### 5.4 Federation RTBF Propagation

```
RTBF_REQUEST
    │
    ▼
LOCAL_DELETION (L7, L5)
    │
    ▼
FEDERATION_PURGE_REQUEST
    │
    ▼
COORDINATOR_CONFIRMS_PURGE
    │
    ▼
DELETION_CERTIFICATE_ISSUED
```

**RULE**: RTBF must propagate across federation within ONE aggregation round.

### 5.5 Proof of Deletion

| Proof Element | Content |
|---------------|---------|
| Deletion timestamp | When deletion occurred |
| Scope | What was deleted |
| Certificate | Signed by system |
| Federation confirmation | If applicable |

---

## SECTION 6 — CONFLICT & MISUSE HANDLING

### 6.1 Governance Key Compromise

| Action | Response |
|--------|----------|
| Detection | Immediate HALT |
| Scope | All outputs blocked |
| Recovery | Key rotation required |
| Notification | Security administrator |

### 6.2 Conflicting Governance Decisions

| Conflict | Resolution |
|----------|------------|
| Allow vs Drop for same payload | DROP wins |
| Different operators approve/reject | First decision wins, log conflict |
| Escalation timeout + late approval | Late approval ignored |

**RULE**: In conflict, always choose the more restrictive option.

### 6.3 Operator Abuse or Negligence

| Scenario | Detection | Response |
|----------|-----------|----------|
| Repeated override attempts | Audit log pattern | Escalate to Campus Authority |
| Delayed acknowledgments | Timeout tracking | Automatic PRIVACY_ONLY |
| Unusual approval patterns | Statistical anomaly | Flag for review |

### 6.4 Malicious Federation Coordinator

| Attack | Detection | Response |
|--------|-----------|----------|
| Requests raw data | Request validation | REJECT + disconnect |
| Requests non-DP gradients | is_dp_protected check | REJECT + disconnect |
| Requests individual contributions | Request type check | REJECT + disconnect |
| Sends malformed updates | Checksum verification | REJECT update |

**RULE**: Disconnect from coordinator on any violation. Await Campus Authority instructions.

### 6.5 Legal Request Exceeding Architectural Limits

| Request Type | System Response |
|--------------|-----------------|
| Raw frame request | REFUSE (data doesn't exist) |
| Audio waveform request | REFUSE (data doesn't exist) |
| Identity reconstruction | REFUSE (architecturally impossible) |
| Governance bypass order | REFUSE (non-bypassable) |
| Federation raw data | REFUSE (never transmitted) |

**BINDING RULE**: If a request violates ARCHITECTURE_CANONICAL.md, the system MUST REFUSE even if legally requested. The architecture makes compliance impossible, not discretionary.

---

## SECTION 7 — TEST & VERIFICATION MAPPING

### 7.1 Governance Rules

| Rule | Enforcing Module | Test | Invariant Protected |
|------|------------------|------|---------------------|
| Allowlist check | `GovernanceFilter.process_inference_output()` | `test_allowlist_enforced` | Only approved outputs |
| Forbidden outputs blocked | `FORBIDDEN_OUTPUTS` check | `test_forbidden_fields_blocked` | No PII leakage |
| PII redaction | `_apply_transforms()` | `test_pii_redacted` | Identity protection |
| Escalation on ambiguity | Escalation path | `test_ambiguous_escalated` | Human oversight |
| Sequence enforcement | State machine | `test_sequence_enforced` | Governance integrity |

### 7.2 Federation Rules

| Rule | Enforcing Module | Test | Invariant Protected |
|------|------------------|------|---------------------|
| DP-only gradients | `DPFederationCoordinator.contribute_dp_gradient()` | `test_dp_gradient_enforced` | Privacy at scale |
| Consent verification | `has_consent()` check | `test_consent_required` | Autonomy |
| Withdrawal purge | `withdraw_from_federation()` | `test_gradients_purged_on_withdrawal` | Right to withdraw |
| Epsilon budget | Budget tracking | `test_epsilon_budget_enforced` | DP guarantees |
| RTBF propagation | Deletion coordinator | `test_rtbf_propagates` | Right to be forgotten |

### 7.3 Cross-Cutting Rules

| Rule | Enforcing Module | Test | Invariant Protected |
|------|------------------|------|---------------------|
| No L5 bypass | Pipeline structure | `test_governance_mandatory` | All outputs governed |
| Revocation before inference | Consent check timing | `test_revocation_immediate` | Consent authority |
| Restrictive conflict resolution | Conflict handler | `test_drop_wins_conflict` | Safety default |

---

## SECTION 8 — CONSISTENCY CHECK

### 8.1 Irreversibility Check

| Question | Answer |
|----------|--------|
| Does any governance rule allow raw data output? | NO |
| Does any federation rule transmit non-DP data? | NO |
| Does any conflict resolution weaken irreversibility? | NO |

**Result**: IRREVERSIBILITY PRESERVED

### 8.2 L5 Bypass Check

| Question | Answer |
|----------|--------|
| Does any rule allow output without governance? | NO |
| Does any emergency mode bypass L5? | NO |
| Does any legal request bypass L5? | NO |

**Result**: L5 NON-BYPASSABLE

### 8.3 Federation Leakage Check

| Question | Answer |
|----------|--------|
| Can raw embeddings leave campus? | NO |
| Can identifiers leave campus? | NO |
| Can non-DP gradients leave campus? | NO |
| Can coordinator request raw data? | NO (REFUSE) |

**Result**: NO FEDERATION LEAKAGE

### 8.4 Power Limits Check

| Power | Explicit Limit |
|-------|----------------|
| L5 approval | ALLOWED_FIELDS only |
| Operator override | Cannot override governance |
| Campus Authority | Cannot bypass irreversibility |
| Federation Coordinator | Cannot request raw data |
| Legal request | Cannot violate architecture |

**Result**: ALL POWER EXPLICITLY LIMITED

---

## SECTION 9 — DOCUMENT AUTHORITY

This playbook is **BINDING**.

- All governance decisions MUST follow these rules
- All federation operations MUST follow these playbooks
- Deviation is a COMPLIANCE FAILURE
- Any conflict with ARCHITECTURE_CANONICAL.md is a DOCUMENT DEFECT

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0, DEPLOYMENT_CONTRACT.md  
**Consistency Check**: PASSED  
**Status**: VALID
