# CANONICAL GLOSSARY

**Document Type**: Immutable Terminology Specification  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0  
**Scope**: Papers 1–18, ScholarMasterEngine  
**Alignment**: Paper 17 (Architectural Irreversibility), Paper 18 (Runtime Enforcement of Architectural Irreversibility)  
**Status**: LOCKED

---

> [!IMPORTANT]
> All definitions in this document reflect **existing implementation only** as codified in the canonical eight-layer architecture (L1–L8), the runtime enforcement mechanisms in `core/canonical_layers.py`, and the hardware watchdog in `utils/watchdog.py`. No definition introduces new functionality, extends existing scope, or projects future capability.

---

## 1. Architectural Irreversibility

**Formal Definition**  
A system design property in which data transformations at the L3 (Edge Abstraction) boundary are destructive by construction. Raw sensor inputs (RGB frames, audio waveforms) are reduced to low-dimensional abstractions (skeleton keypoints ≤34 dimensions, spectral features) via a non-injective mapping f: ℝ^6,000,000 → ℝ^~100. The original signal is deallocated immediately after transformation. No inverse mapping exists.

**Runtime Enforcement Mechanism**  
- `EdgeAbstraction.transform_frame_to_skeleton()` in `core/canonical_layers.py` performs extraction and invokes `_destroy_frame()` within the same call.
- Frame buffer is set to `None` and `del` is called on the raw data object.
- Destruction is time-verified: if elapsed time exceeds `FRAME_TTL_MS` (33ms), a `FrameDestructionError` is raised and the system halts.

**Boundary Constraints**  
- Applies exclusively at the L2→L3 boundary.
- Compression ratio must exceed 1000:1.
- Raw data types (`RGB`, `AudioWaveform`) are structurally prohibited from appearing in L4+ function signatures.

**Explicit Non-Claims**  
- Does not claim resistance to physical cold-boot attacks on DRAM.
- Does not claim protection against hardware-level backdoors.
- Does not claim irreversibility beyond the defined operational space of the L3 transformation.

---

## 2. Execution Window

**Formal Definition**  
The bounded temporal interval during which raw sensor data exists in volatile memory. For video frames, this interval is ≤33ms (one frame interval at 30 FPS). For audio waveforms, this interval is ≤3000ms. Outside this window, the raw data must not exist in any addressable memory.

**Runtime Enforcement Mechanism**  
- `EdgeAbstraction.FRAME_TTL_MS = 33` and `EdgeAbstraction.AUDIO_TTL_SECONDS = 3` define the upper bounds.
- `SensorAcquisition.get_frame_age_ms()` and `SensorAcquisition.get_audio_age_seconds()` compute elapsed time against creation timestamps.
- The TTL enforcement loop runs at 10ms intervals; the independent watchdog loop runs at 100ms intervals.

**Boundary Constraints**  
- Execution window values are compile-time constants, not configuration parameters.
- Applies to L1/L2 volatile memory buffers exclusively.
- No extension mechanism exists; TTL values are not operator-adjustable.

**Explicit Non-Claims**  
- Does not guarantee sub-microsecond precision; enforcement granularity is bounded by the TTL loop interval (10ms).
- Does not account for clock skew in multi-node deployments beyond the local monotonic clock source.

---

## 3. Identity Event

**Formal Definition**  
A symbolic output emitted by L4 (Local Inference) representing a classified behavioral state (e.g., `HAND_RAISE`, `ATTENTION_LOSS`, `AUDIO_ANOMALY`). Identity events are anonymous: they carry `zone_id`, `timestamp`, `event_type`, and `severity`, but contain no biometric vectors, face embeddings, or linkable identifiers.

**Runtime Enforcement Mechanism**  
- `LocalInference` in `core/canonical_layers.py` validates all output payloads against the allowlist defined in ARCHITECTURE_CANONICAL.md §4.4.
- Permitted fields: `zone_id` (string), `timestamp` (float), `event_type` (enum), `severity` (float 0.0–1.0), `skeleton_keypoints` (array[34]), `audio_class` (enum).
- Unknown or prohibited fields trigger rejection at the L4/L5 boundary.

**Boundary Constraints**  
- Identity events must originate from L3 abstractions only; no path exists from L2 raw data to L4 output.
- Face embeddings (512-dim) are prohibited in L4 memory space (INV-02 per ARCHITECTURE_CANONICAL.md §2.4).
- Temporal patterns in identity events must not be linkable across sessions.

**Explicit Non-Claims**  
- Does not claim that identity events are differentially private.
- Does not claim that aggregate patterns of identity events cannot reveal group-level information.
- Does not claim identity events are free from inference bias inherent in the underlying model.

---

## 4. Retrieval Context

**Formal Definition**  
The set of variables available to the L5 Governance Gate when evaluating whether an inference output may transit to L6 (Human Interface). Retrieval context includes: current time, campus zone, active policy configuration, operator authentication state, and event sensitivity score.

**Runtime Enforcement Mechanism**  
- `GovernanceFilter` in `core/canonical_layers.py` loads the active policy via `LoadActivePolicy(Context)` at each evaluation.
- The governance gate checks: (a) event type membership in the policy allowlist, (b) sensitivity threshold compliance, (c) human acknowledgment status for high-severity events.
- If any retrieval context component is unavailable (e.g., policy engine unreachable), all output is blocked (fail-closed).

**Boundary Constraints**  
- Retrieval context is scoped to the current session and current campus zone.
- No historical retrieval context (from prior sessions) is accessible.
- Retrieval context does not include raw sensor data or biometric vectors.

**Explicit Non-Claims**  
- Does not claim retrieval context is tamper-proof against a root-level adversary.
- Does not claim completeness; retrieval context is limited to the fields defined in the active policy schema.

---

## 5. Volatile Processing

**Formal Definition**  
The operational constraint requiring that all raw sensor data (L1/L2) and intermediate inference tensors (L4) reside exclusively in volatile memory (RAM). No raw data may be written to persistent storage (disk, flash, swap, crash dumps) at any point in the processing pipeline.

**Runtime Enforcement Mechanism**  
- `SensorAcquisition.__init__()` initializes frame and audio buffers in process memory only.
- `EphemeralMemoryZone` (L7) enforces RAM-only storage with session-scoped TTL and explicit zeroing on session end.
- Swap is disabled (`vm.swappiness=0`). Crash dump exclusion is enforced via `MADV_DONTDUMP` on sensor buffers. No file handles are opened for raw data paths.
- `PhysicalSubstrate.verify_volatile_memory_support()` validates hardware isolation at boot.

**Boundary Constraints**  
- Volatile processing applies to layers L1 through L4 and L7.
- L7 (Ephemeral Memory Zone) stores approved events in RAM only; event TTL does not exceed session duration.
- L8 (Federation) transmits only DP-protected gradient summaries; raw data never enters federation payloads.

**Explicit Non-Claims**  
- Does not claim protection against DRAM remanence attacks after power removal.
- Does not claim that the operating system kernel cannot access volatile buffers through privileged operations.

---

## 6. Non-Persistence Boundary

**Formal Definition**  
The architectural demarcation at which data transitions from volatile to non-volatile form. In ScholarMasterEngine, **no raw sensor data or biometric vectors cross this boundary**. The only data that may persist is: (a) governance-approved event metadata (L7, RAM-only during session; audit logs in L7 if persistent logging is enabled), (b) cryptographically attested audit records, (c) DP-protected gradient summaries (L8).

**Runtime Enforcement Mechanism**  
- `EdgeAbstraction._destroy_frame()` enforces destruction before any downstream processing can persist the data.
- `GovernanceFilter.process_event()` validates that only allowlisted, sanitized fields reach output ports.
- Layer contract tests (`tests/test_layer_contracts.py`) verify that raw data types do not appear in L4+ payloads.

**Boundary Constraints**  
- The non-persistence boundary is located at the L3 transformation output.
- No configuration parameter can move this boundary to a later layer.
- Audit logs (L7) record governance decisions, not raw data or reconstructable representations.

**Explicit Non-Claims**  
- Does not claim that audit log metadata cannot be correlated with external data sources.
- Does not guarantee that no persistent artifact exists on hardware after system decommissioning without explicit secure deletion procedures.

---

## 7. Enforcement Layer

**Formal Definition**  
The set of runtime mechanisms that verify and enforce architectural invariants during system operation. The enforcement layer is not a single software module; it is distributed across: the L3 destruction watchdog, the L5 governance gate, the L7 ephemeral memory zone, the hardware watchdog (`utils/watchdog.py`), and the boot-time invariant checker (`PhysicalSubstrate.verify_volatile_memory_support()`).

**Runtime Enforcement Mechanism**  
- **Primary**: TTL enforcement loop at 10ms interval (`EdgeAbstraction._watchdog_loop()`).
- **Secondary**: Independent watchdog process at 100ms interval (or hardware watchdog at configurable interval via `HardwareWatchdog`).
- **Tertiary**: Forced zeroization on buffer deallocation.
- **Quaternary**: Boot-time verification of empty buffer state before accepting new data.

**Boundary Constraints**  
- Enforcement layer mechanisms cannot be disabled by operator configuration.
- Failure of any enforcement mechanism triggers fail-closed behavior (system halt or output suppression).
- Enforcement layer operates within the software threat model; it does not cover hypervisor-level inspection or hardware backdoors.

**Explicit Non-Claims**  
- Does not claim formal verification of enforcement correctness (runtime assertion-based, not TLA+ proven).
- Does not claim enforcement under adversary modification of the deployed binary.

---

## 8. Runtime Termination Condition

**Formal Definition**  
A system state in which one or more architectural invariants cannot be verified, triggering immediate process termination or output suppression. The system employs kill-on-violation semantics: invariant breach results in `SIGKILL` (or equivalent halt), not graceful degradation.

**Runtime Enforcement Mechanism**  
- TTL exceeded → `FrameDestructionError` raised → system halt.
- Zeroization verification failed → immediate halt.
- Governance gate unreachable → all L4→L6 traffic blocked.
- Watchdog heartbeat missed → `SIGKILL` issued to main process.
- Privacy LED state `UNKNOWN` → system halt.

**Boundary Constraints**  
- Runtime termination is non-negotiable; no "override" or "emergency bypass" mode exists.
- Restart after termination requires explicit operator acknowledgment.
- On restart, the system initializes to PRIVACY mode (skeleton-only, no face recognition).

**Explicit Non-Claims**  
- Does not claim that SIGKILL guarantees zero data residue in all kernel memory regions.
- Does not claim that termination latency is bounded to a specific sub-millisecond value.

---

## 9. Density Constraint

**Formal Definition**  
The maximum dimensionality of data representations permitted at each layer boundary. At L3, output is constrained to ≤34 keypoints × 2 coordinates + confidence values (~100 scalar values). This constraint ensures that the information density of post-transformation data is insufficient for identity reconstruction.

**Runtime Enforcement Mechanism**  
- `EdgeAbstraction.transform_frame_to_skeleton()` outputs a fixed-dimension keypoint array.
- Layer contract tests (`tests/test_layer_contracts.py`, `tests/test_irreversibility.py`) verify maximum representation dimensionality.
- The `ALLOWED_FIELDS` in the L4/L5 boundary contract restrict payload structure to the defined schema.

**Boundary Constraints**  
- Skeleton keypoints are capped at 34 dimensions per ARCHITECTURE_CANONICAL.md §2.3.
- Audio features are reduced to spectral vectors that discard linguistic content.
- No intermediate representation between L3 and L4 may exceed the defined dimensionality.

**Explicit Non-Claims**  
- Does not claim that 34 keypoints are the theoretical minimum for the system's inference tasks.
- Does not claim that density constraints alone prevent re-identification in all contexts (complementary destruction and non-persistence constraints are required).

---

## 10. Open-Set Gate

**Formal Definition**  
The allowlist-based filtering mechanism at L5 (Governance) that determines which event types and fields may transit to downstream layers. The gate operates on an explicit allowlist; any event type or field not on the allowlist is rejected. Denylist-based filtering is architecturally prohibited.

**Runtime Enforcement Mechanism**  
- `GovernanceFilter.process_event()` checks `Event.Type ∈ Policy.AllowList` before any further processing.
- Unknown fields in event payloads trigger immediate rejection.
- The allowlist is defined in operator-configurable policy, but the set of configurable fields is itself constrained to `ALLOWED_FIELDS` (ARCHITECTURE_CANONICAL.md §4.4).

**Boundary Constraints**  
- Allowlist changes do not and cannot weaken privacy, governance, or irreversibility guarantees.
- Allowlist is scoped to event types and payload fields; it cannot authorize transmission of raw data types.
- Denylist prohibition is an architectural invariant, not a policy choice.

**Explicit Non-Claims**  
- Does not claim that the allowlist covers all possible benign event types.
- Does not claim that allowlist misconfiguration (overly broad) cannot result in unnecessary information disclosure within the permitted field schema.

---

## 11. TTL Enforcement

**Formal Definition**  
The runtime mechanism that assigns a maximum lifetime to each raw data buffer and destroys the buffer when the lifetime expires. Two TTL constants are defined: `FRAME_TTL_MS = 33` (video frames) and `AUDIO_TTL_SECONDS = 3` (audio waveforms). Buffers exceeding their TTL are zeroized and deallocated.

**Runtime Enforcement Mechanism**  
- `EdgeAbstraction._watchdog_loop()` runs continuously, polling buffer ages at 10ms intervals.
- If `buffer.age > TTL`, the buffer is zeroized (`memset` equivalent), deallocated, and the event is logged.
- A secondary independent watchdog (100ms interval) monitors for TTL violations that the primary loop may miss.
- If the primary enforcement loop fails to destroy a buffer within TTL, the watchdog issues termination.

**Boundary Constraints**  
- TTL values are compile-time constants in `core/canonical_layers.py`, not runtime-configurable.
- TTL enforcement applies to L2 raw buffers processed by L3.
- L7 session TTL is separate and operator-configurable but enforces RAM-only storage.

**Explicit Non-Claims**  
- Does not claim that TTL enforcement operates at real-time OS guarantees; enforcement is best-effort within the polling interval.
- Does not claim that TTL prevents an adversary who can pause the enforcement loop via kernel-level control.

---

## 12. Watchdog Termination

**Formal Definition**  
The mechanism by which an independent monitoring process (watchdog) terminates the main inference process upon detecting an invariant violation. The watchdog operates in a separate failure domain (distinct process, distinct memory space) and issues `SIGKILL` to the main process.

**Runtime Enforcement Mechanism**  
- Software watchdog: `EdgeAbstraction._watchdog_loop()` runs as a daemon thread; monitors frame ages and forces destruction on TTL violation.
- Hardware watchdog: `HardwareWatchdog` in `utils/watchdog.py` writes periodic heartbeats to `/dev/watchdog`. If the application hangs, the hardware watchdog timer triggers a forced system reset.
- Governance watchdog: `modules_legacy/governance.py` tracks per-module heartbeat timestamps; timeout triggers transition to `DEGRADED` or `SAFE` state.

**Boundary Constraints**  
- The watchdog cannot be disabled by the main process.
- Crash of the main process does not imply crash of the watchdog (INV-05).
- Hardware watchdog requires `CAP_IPC_LOCK` privileges and supported hardware (`/dev/watchdog` device).

**Explicit Non-Claims**  
- Does not claim that the software watchdog thread survives kernel panics.
- Does not claim that hardware watchdog is available on all deployment platforms.

---

## 13. Failure Degradation State

**Formal Definition**  
A system operating mode entered when a non-critical subsystem becomes unavailable (e.g., network partition, MQTT failure) but no privacy invariant is violated. In this state, the system continues local processing but suppresses all external output. Degradation preserves privacy at the cost of reduced functionality.

**Runtime Enforcement Mechanism**  
- MQTT failure → events buffered in RAM (ephemeral); no persistent queue writes.
- Network partition → L8 federation suspended; local inference continues.
- Storage failure → system operates ephemerally; session data loss accepted.
- Governance module timeout → system transitions to `DEGRADED` state; output ports disabled.
- State machine: `Normal → Degraded(Safe)` on network loss; `Degraded(Safe) → HALT` on TTL or watchdog failure.

**Boundary Constraints**  
- Degraded state is strictly more private than normal operation (output suppressed).
- Degraded state does not permit bypass of L3 or L5.
- Transition from degraded to normal requires restoration of the failed subsystem; no automatic recovery permits weaker invariants.

**Explicit Non-Claims**  
- Does not claim that all degraded states are recoverable without operator intervention.
- Does not claim that degraded operation maintains the same inference quality as normal operation.

---

## 14. Sovereign Node

**Formal Definition**  
A campus deployment unit that retains full autonomous control over its local data, inference models, and governance policies. Each sovereign node operates a complete L1–L8 stack independently. No external authority (including the federation coordinator) may compel a sovereign node to disclose raw data, modify local policy, or continue federation participation.

**Runtime Enforcement Mechanism**  
- `HierarchicalFedAvgCoordinator.register_campus()` requires explicit campus registration; no automatic enrollment.
- All federation communication is outbound-only from the sovereign node.
- Gradient payloads from L8 contain no raw data, embeddings, or identifiers (ARCHITECTURE_CANONICAL.md §2.8).
- L1–L4 layers have no external network connectivity (INV-04: Network Air-Gap).

**Boundary Constraints**  
- Sovereignty applies per campus; a campus cannot be partially sovereign.
- The global coordinator aggregates gradients without accessing raw data.
- No gradient contribution occurs without explicit consent attestation.

**Explicit Non-Claims**  
- Does not claim sovereignty against a state actor with physical access to campus hardware.
- Does not claim that sovereignty prevents information leakage through gradient inversion attacks (addressed separately by differential privacy budgets in L8).

---

## 15. Federation Membership

**Formal Definition**  
The state of a sovereign node that has explicitly joined the L8 federation for the purpose of contributing DP-protected gradient summaries to a shared model. Federation membership is voluntary, revocable, and does not transfer data ownership.

**Runtime Enforcement Mechanism**  
- Join: `HierarchicalFedAvgCoordinator.register_campus(campus_id, num_samples)` registers a campus with sample count for weighted averaging.
- Participate: `aggregate_campus_updates()` processes only registered campuses' gradient contributions with staleness-aware weighting.
- Withdraw: campus may withdraw at any time; withdrawal triggers gradient purge from the global model; must complete within one federation round; requires no justification.

**Boundary Constraints**  
- Membership does not grant the coordinator access to campus-local data, models, or logs.
- Gradient payloads are the only data transmitted; payloads must pass DP validation before transmission.
- Non-participating campuses operate identically in L1–L7; L8 is inactive.

**Explicit Non-Claims**  
- Does not claim that withdrawal fully removes a campus's influence from a model trained over multiple rounds with that campus's contributions.
- Does not claim that federation membership provides equal benefit to all participants regardless of data volume.

---

## 16. Consent Verification

**Formal Definition**  
The runtime check ensuring that specific data operations (face embedding enrollment, federation gradient contribution, cross-session embedding persistence) are authorized by explicit, verifiable consent from the data subject or institutional authority.

**Runtime Enforcement Mechanism**  
- `FaissFaceIndex.add_embedding_safe()` in `infrastructure/indexing/faiss_face_index.py` requires a consent parameter; enrollment without consent is rejected.
- Federation gradient contribution requires consent attestation before transmission (ARCHITECTURE_CANONICAL.md §5.4).
- Consent revocation propagates within one federation round.

**Boundary Constraints**  
- Consent is required per-operation, not blanket.
- Consent state is verifiable at runtime; unverifiable consent blocks the operation.
- Consent does not override architectural invariants (e.g., consenting to raw data persistence is not possible because the system cannot persist raw data).

**Explicit Non-Claims**  
- Does not claim that consent verification validates informed understanding by the consenting party.
- Does not claim that consent records are immutable beyond the integrity guarantees of the audit log.

---

## 17. Deletion Request Processing

**Formal Definition**  
The mechanism by which a data subject's request to remove their data from the system is executed. In ScholarMasterEngine, deletion operates on: (a) enrolled face embeddings in the FAISS index, (b) session-scoped identity events, and (c) contributed federation gradients. Deletion of raw sensor data is not applicable because raw sensor data does not persist.

**Runtime Enforcement Mechanism**  
- `FaissFaceIndex.remove_student()` removes a student's embedding from the FAISS index and purges associated metadata.
- Session-scoped data in L7 (`EphemeralMemoryZone`) is automatically destroyed at session end via `clear_all()` with explicit zeroing.
- Federation: individual deletion requests propagate to the global model; the global model must be updated to exclude deleted contributions (ARCHITECTURE_CANONICAL.md §5.5); propagation must complete within defined SLA.

**Boundary Constraints**  
- Deletion applies only to data that persists; raw sensor data is already destroyed within the execution window.
- Deletion of audit log entries is subject to separate retention policies; audit logs record governance decisions, not biometric data.
- Deletion does not extend to aggregate statistics that cannot be disaggregated to an individual.

**Explicit Non-Claims**  
- Does not claim that deletion from a trained federated model fully reverses the model's learned parameters attributable to a specific individual.
- Does not claim real-time deletion propagation; propagation is bounded by federation round duration.

---

## Document Control

| Property | Value |
|----------|-------|
| Version | 1.0.0 |
| Status | LOCKED |
| Generated | 2026-02-12 |
| Authority | ARCHITECTURE_CANONICAL.md v1.0.0 |
| Alignment | Paper 17, Paper 18 |
| Modification Authority | Human governance only |
