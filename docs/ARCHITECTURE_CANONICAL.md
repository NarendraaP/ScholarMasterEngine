# ARCHITECTURE_CANONICAL.md

**Document Type**: Immutable Canonical Specification  
**Version**: 1.0.0  
**Effective Date**: 2026-02-07  
**Authority**: Human Governance Only

---

## 1. Purpose & Scope

ScholarMaster is a privacy-governed, federated, human-in-the-loop Edge AI system for academic institution analytics.

### 1.1 Definitions

- **Architecture**: The formal structure and invariants defined in this document
- **Implementation**: Code that must conform to this architecture
- **Enforcement**: Runtime and CI mechanisms that verify conformance

### 1.2 Separation Principle

Architecture, implementation, and enforcement are distinct concerns:
- Architecture defines what must be true
- Implementation realizes the architecture
- Enforcement verifies implementation conforms to architecture

### 1.3 Supremacy

This document is superior to all implementation artifacts. Conflicts must resolve in favor of this document.

---

## 2. Canonical Runtime Layers

The system consists of exactly eight (8) layers with hard boundaries. Data flows unidirectionally from L1 to L8. Bypass of any layer is prohibited.

| Layer ID | Name | Description | Allowed Outputs | Forbidden Outputs |
|----------|------|-------------|-----------------|-------------------|
| L1 | Physical Substrate | Hardware, power, enclosure | Operational signals | None |
| L2 | Sensor Acquisition | Camera, microphone capture | Raw frames, audio buffers | Persistent storage writes |
| L3 | Edge Abstraction | Irreversible transformation boundary | Skeleton keypoints, audio features | Raw frames, waveforms, embeddings |
| L4 | Local Inference | Pose estimation, audio classification | Symbolic events, anonymous metrics | Identity tokens, biometric vectors |
| L5 | Governance & Compliance Filter | ST-CSF validation, policy enforcement | Approved events only | Unapproved inference outputs |
| L6 | Human Interface & Transparency | AR visualization, privacy LED | Visual alerts, skeleton overlays | Raw imagery, identifiable data |
| L7 | Ephemeral Memory Zone | RAM-only volatile storage | Timestamped event stream | Persistent writes of biometric data |
| L8 | Federated Adaptation & Coordination | FL aggregation, global coordination | Model updates, gradient summaries | Raw data, embeddings, identifiers |

### 2.1 L1 — Physical Substrate

- **Inputs**: Electrical power, physical environment
- **Outputs**: Operational status signals
- **Invariants**: Hardware must support volatile memory isolation
- **Destruction Requirements**: None
- **Bypass Prohibition**: Physical layer cannot be virtualized without equivalent isolation guarantees

### 2.2 L2 — Sensor Acquisition

- **Inputs**: Physical light (camera), sound waves (microphone)
- **Outputs**: Raw frame buffers, raw audio buffers (to L3 only)
- **Invariants**: Sensors must output to volatile memory exclusively
- **Destruction Requirements**: Raw buffers must not persist beyond L3 boundary
- **Bypass Prohibition**: No sensor output may reach L4+ without L3 transformation

### 2.3 L3 — Edge Abstraction (Irreversible Boundary)

- **Inputs**: Raw frames, raw audio from L2
- **Outputs**: Skeleton keypoints (34 dimensions max), audio feature vectors
- **Invariants**: 
  - Raw frame lifetime must not exceed 33ms
  - Audio waveform lifetime must not exceed 3 seconds
  - Transformation must be lossy and irreversible
  - Compression ratio must exceed 1000:1
- **Destruction Requirements**: 
  - Raw frames must be destroyed via explicit memory deallocation
  - Audio buffers must be overwritten before reuse
- **Bypass Prohibition**: No raw sensor data may transit to L4

### 2.4 L4 — Local Inference

- **Inputs**: Skeleton keypoints, audio features from L3
- **Outputs**: Symbolic events (hand raise, attention, audio anomaly)
- **Invariants**: 
  - Face embeddings (512-dim) must not be created
  - Identity linking must not occur
  - Output must be anonymous and zone-scoped
- **Destruction Requirements**: Intermediate inference tensors must be deallocated after use
- **Bypass Prohibition**: Inference outputs must not reach L6 without L5 approval

### 2.5 L5 — Governance & Compliance Filter

- **Inputs**: Inference events from L4
- **Outputs**: Approved events with governance attestation
- **Invariants**: 
  - All outputs must pass ST-CSF validation
  - Event ordering must be: INFERENCE_COMPLETE → COMPLIANCE_CHECKED → APPROVED_FOR_OUTPUT
  - Allowlist-only filtering (denylist prohibited)
- **Destruction Requirements**: Rejected events must be logged and discarded
- **Bypass Prohibition**: No inference output may reach L6 or L8 without L5 approval

### 2.6 L6 — Human Interface & Transparency

- **Inputs**: Approved events from L5
- **Outputs**: AR overlays, skeleton visualizations, privacy LED state
- **Invariants**: 
  - Privacy LED must indicate system state at boot
  - Only skeleton data may be visualized (no RGB imagery)
  - Operator acknowledgment must be recorded
- **Destruction Requirements**: Rendered frames must not be recorded
- **Bypass Prohibition**: Human interface must not display unapproved data

### 2.7 L7 — Ephemeral Memory Zone

- **Inputs**: Approved events from L5, L6 acknowledgments
- **Outputs**: Time-bounded event stream
- **Invariants**: 
  - All storage must be RAM-only
  - Event TTL must not exceed session duration
  - No writes to persistent storage of biometric-derived data
- **Destruction Requirements**: Memory must be zeroed on session end
- **Bypass Prohibition**: No path may write biometric data to persistent storage

### 2.8 L8 — Federated Adaptation & Coordination

- **Inputs**: Aggregated gradients from campus nodes
- **Outputs**: Model updates, global coordination signals
- **Invariants**: 
  - Campus sovereignty must be preserved
  - Gradient payloads must contain no raw data, embeddings, or identifiers
  - Consent must be verified before gradient contribution
- **Destruction Requirements**: Withdrawn campus gradients must be purged from global model
- **Bypass Prohibition**: No raw data may leave campus boundary

---

## 3. Irreversibility Invariants

These invariants are system laws. Violation constitutes architectural failure.

### 3.1 Frame Lifetime Constraint

- Raw frames must exist for less than 33ms (one frame interval at 30 FPS)
- Frame destruction must occur via explicit `del` or equivalent memory deallocation
- Destruction must be verified, not assumed

### 3.2 Audio Waveform Destruction

- Audio waveforms must exist for less than 3 seconds
- Ring buffer must overwrite previous samples
- No audio file writes permitted

### 3.3 Embedding TTL Requirements

- If face embeddings are created (permitted only for enrollment), TTL must be enforced
- Session-scoped embeddings must be destroyed at session end
- Cross-session embedding persistence requires explicit consent

### 3.4 Identity Reconstruction Prohibition

- No combination of outputs from L3+ may enable identity reconstruction
- Skeleton keypoints (34 dimensions) must be insufficient for biometric identification
- Temporal patterns must not be linkable across sessions

### 3.5 One-Way Data Reduction

- L3 transformation must be mathematically irreversible
- Original signal cannot be reconstructed from transformed output
- Compression must be lossy with ratio exceeding 1000:1

---

## 4. Governance Enforcement Model

### 4.1 Mandatory Governance Gate

- L5 is a mandatory transit point between L4 and L6
- No inference output may bypass L5
- L5 failure must block all downstream output

### 4.2 Required Event Ordering

All compliant event flows must follow this sequence:
1. `INFERENCE_COMPLETE` — Inference layer produces output
2. `COMPLIANCE_CHECKED` — Governance layer validates output
3. `APPROVED_FOR_OUTPUT` — Output cleared for human interface

Events arriving out of order must be rejected.

### 4.3 Denylist Prohibition

- Denylist-based filtering is prohibited
- All cross-boundary data must be allowlist-validated
- Unknown fields must be rejected, not ignored

### 4.4 Allowlist Data Contracts

Permitted fields in cross-layer payloads:
- `zone_id`: String, campus zone identifier
- `timestamp`: Float, Unix epoch
- `event_type`: Enum, defined event types only
- `severity`: Float, 0.0–1.0
- `skeleton_keypoints`: Array[34], normalized coordinates
- `audio_class`: Enum, defined audio categories only

All other fields are prohibited.

---

## 5. Federation & Sovereignty Model

### 5.1 Campus as Sovereign Unit

- Each campus is an autonomous federation member
- Campus retains full control over local data
- No external authority may compel data disclosure

### 5.2 Join Semantics

- Campus must explicitly join federation
- Join requires consent attestation
- Join does not transfer data ownership

### 5.3 Withdraw Semantics

- Campus may withdraw at any time
- Withdrawal must trigger gradient purge from global model
- Withdrawal must complete within one federation round
- Withdrawal must not require justification

### 5.4 Gradient Consent Requirement

- Gradient contribution requires explicit consent
- Consent must be verifiable
- Consent revocation must propagate within one round

### 5.5 Right-to-be-Forgotten Propagation

- Individual deletion requests must propagate to federation
- Global model must be updated to exclude deleted contributions
- Propagation must complete within defined SLA

### 5.6 Global Coordinator Responsibilities

- Aggregate gradients without accessing raw data
- Enforce consent verification
- Process withdrawal requests
- Maintain federation membership registry

---

## 6. Trust & Transparency Requirements

### 6.1 Privacy LED States

| State | Meaning | Visual Indicator |
|-------|---------|------------------|
| OFF | System inactive | No light |
| PRIVACY | Pose-only mode (anonymous) | Green |
| ACTIVE | Face recognition enabled | Red |

- Privacy LED must be set at system boot
- Failure to set LED must halt system
- LED state must be accurate

### 6.2 Skeleton-Only Visualization

- Human interface must display skeleton overlays only
- RGB imagery must never be displayed
- Skeleton must be rendered on black or neutral background

### 6.3 Audit Visibility Requirements

- All governance decisions must be logged
- Logs must be accessible to authorized auditors
- Log integrity must be cryptographically verifiable

### 6.4 Operator Acknowledgment Loops

- Critical alerts must require operator acknowledgment
- Acknowledgment must be logged
- Unacknowledged alerts must escalate

### 6.5 Visibility Failure Behavior

- If Privacy LED cannot be set: System must halt
- If skeleton cannot be rendered: System must fall back to text-only
- If audit log unavailable: System must operate in degraded mode with local logging

---

## 7. Failure Semantics

Privacy must be preserved during failure. Fail-safe defaults apply.

### 7.1 MQTT Failure

- If MQTT unavailable: Buffer events locally
- Buffer must be ephemeral (RAM-only)
- Buffer overflow must drop oldest events
- No persistent queue writes

### 7.2 Governance Failure

- If L5 unavailable: Block all L4→L6 traffic
- No inference output may bypass governance during failure
- System must indicate governance failure to operator

### 7.3 Storage Failure

- If persistent storage fails: Continue with ephemeral operation
- Ephemeral operation must not compromise privacy
- Session data loss is acceptable; privacy violation is not

### 7.4 Crash Recovery

- On crash: Assume all volatile data destroyed
- On restart: Initialize to PRIVACY mode
- On restart: Require operator acknowledgment before ACTIVE mode

### 7.5 Partial Subsystem Availability

- Degraded operation must preserve privacy invariants
- Functionality may be reduced
- Privacy must not be reduced

---

## 8. Compliance & Enforcement Readiness

### 8.1 Document Immutability

This document is **IMMUTABLE**. Modifications require human governance approval through defined change control processes.

### 8.2 Implementation Subordination

All implementations are subordinate to this document. Implementation convenience does not justify architectural deviation.

### 8.3 Deviation as Failure

Any deviation from this architecture is a compliance failure. Deviations must be:
- Logged
- Reported
- Remediated

### 8.4 Tool Authority

Tools (including AI assistants) may:
- Verify compliance against this document
- Report violations

Tools may not:
- Modify this document
- Reinterpret requirements
- Weaken constraints

---

## Document Control

| Property | Value |
|----------|-------|
| Status | Canonical Architecture Locked |
| Modification Authority | Human governance only |
| Tool Authority | Verification-only |
