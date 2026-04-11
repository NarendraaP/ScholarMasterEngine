# CANONICAL CONSTRAINTS

**Document Type**: Immutable Constraint Specification  
**Authority**: ARCHITECTURE_CANONICAL.md v2.0.0 (Elite Reference)  
**Companion**: CANONICAL_GLOSSARY.md v1.0.0, APPENDIX_THEOREMS.tex  
**Scope**: Papers 1–19, ScholarMasterEngine  
**Alignment**: Paper 17 (Architectural Irreversibility), Paper 18 (Runtime Enforcement), Paper 19 (Formal Logic)  
**Status**: LOCKED

---

> [!IMPORTANT]
> This document defines the **immutable architectural constraints** of the ScholarMaster System. For formal mathematical definitions, proofs, and attacker models ($A_0$-$A_5$), refer to the **Unified Formal Appendix** (`docs/papers/APPENDIX_THEOREMS.tex`).

---

> [!IMPORTANT]
> All invariants codify existing runtime behavior as implemented in `core/canonical_layers.py`, `core/layer_contracts.py`, `core/privacy_led.py`, `utils/watchdog.py`, `modules/fl_coordinator.py`, `modules/federated_learning/privacy_accountant.py`, and `infrastructure/indexing/faiss_face_index.py`. No invariant introduces new functionality or extends existing scope.

---

## Failure Severity Classification

Every invariant violation is classified into exactly one of the following fail-state classes. These classes are **not equivalent** — each produces a distinct system response with a distinct scope of impact. This taxonomy is exhaustive.

### Fail-State Classes

| Class | Action | Scope | System Behavior | Recovery | Example Triggers |
|-------|--------|-------|-----------------|----------|------------------|
| **HARD HALT** | Process termination | Entire system | All processing stops. No output. Operator intervention required. | Manual restart. System re-initializes in PRIVACY mode (INV-15). | LED state `UNKNOWN`, fail-open detected |
| **FRAME HALT** | Drop current frame | Single frame | Current frame's pipeline terminates. Other frames unaffected. | Automatic on next frame. | TTL exceeded (`FrameDestructionError`) |
| **OUTPUT SUPPRESS** | Block all L6 emission | All output | Pipeline continues internally but no data reaches L6/L7. | Automatic when valid state restored. | Governance unreachable, watchdog failure, federation deletion pending |
| **EVENT REJECT** | Reject single payload | Single event | Individual event or payload rejected. Other events unaffected. | Immediate — next event proceeds independently. | Forbidden field in payload, oversized skeleton, unconsented enrollment |
| **CONTRIBUTION REJECT** | Block federation contribution | Single campus | Campus contribution rejected. Other campuses unaffected. | Automatic when consent verified or campus re-joins. | Missing consent, campus withdrawing |
| **INFO** | Log only | None | Operational metric recorded. No data flow impact. Audit trail only. | Not applicable. | Threshold monitoring, staleness statistics |

### Invariant-to-Fail-State Assignment

Invariants are classified into two enforcement categories:

**Runtime-Enforced Invariants** — Violations are detectable and handled at runtime by application code.

| Invariant | Fail-State Class | Specific Trigger | Specific Action |
|-----------|-----------------|------------------|-----------------|
| INV-01 | FRAME HALT | `FRAME_TTL_MS` exceeded | `FrameDestructionError` raised, frame dropped, watchdog logs |
| INV-02 | EVENT REJECT | Embedding in L4→L5 transition | `LayerBoundaryViolation`, event dropped |
| INV-05 | OUTPUT SUPPRESS | Software watchdog thread fails to start | TTL enforcement remains active; output blocked until watchdog restart |
| INV-06 | EVENT REJECT | Unknown field in governance payload | `GovernanceState.REJECTED`, event logged and dropped |
| INV-08 | HARD HALT | Fail-open behavior detected | Watchdog escalation → hardware reset as last resort |
| INV-09 | EVENT REJECT | Persistent storage attempted in L1–L4 | `LayerBoundaryViolation` via `FORBIDDEN_OUTPUTS` |
| INV-10 | EVENT REJECT | Skeleton dims > 34 | `ValueError` at `L3Output` construction; frame still destroyed |
| INV-11 | EVENT REJECT | Enrollment without consent | Operation rejected, embedding not stored |
| INV-12 | OUTPUT SUPPRESS | Deletion propagation failure | Federation output blocked until propagation confirmed |
| INV-13 | OUTPUT SUPPRESS | Forbidden data in L8 payload | `LayerBoundaryViolation`; federation blocked |
| INV-15 | HARD HALT | Privacy LED cannot be set at boot | System halts per ARCHITECTURE_CANONICAL.md §6.5 |

**Structural (Governance) Invariants** — Guaranteed by code structure and immutability. Cannot be violated at runtime without source modification. Enforcement relies on development governance (code review, CI, document lock), not runtime detection.

| Invariant | Fail-State Class | Structural Guarantee | Governance Enforcement |
|-----------|-----------------|---------------------|------------------------|
| INV-03 | HARD HALT | TTL constants are `class` attributes, not configuration | Code review + CI: no setter for `FRAME_TTL_MS` |
| INV-04 | HARD HALT | No `import socket` / `import requests` in L1–L4 | CI lint: forbidden import check on `core/` |
| INV-07 | HARD HALT | `FORBIDDEN_OUTPUTS` is an allowlist; no denylist API exists | Code review: no `deny`/`block` method signatures |
| INV-14 | HARD HALT | TTL enforcement is inline in `finally` block; no on/off switch | Code review + CI: no `disable_ttl` function |

---

## INV-01: Raw Sensor Non-Persistence

No raw sensor data may persist beyond the L3 transformation boundary.

### Formal Definition

∀ raw buffer b ∈ {RGB frame, audio waveform}, ∃ t_destroy such that:  
0 < t_destroy − t_create ≤ TTL(b)  
∧ ∀ t > t_destroy: addressable(b, t) = false

Where:
- TTL(frame) = 33ms, TTL(audio) = 3000ms
- `addressable(b, t)` := reachable via live Python-level references at time t. This is **not** a claim about hardware memory zeroing — deallocated pages may persist in the CPython allocator's free list or in physical DRAM until overwritten by subsequent allocations.

After t_destroy, no live Python reference to the original raw input exists. The transformation f: ℝ^N → ℝ^≤34 is executed in a `try/finally` block where destruction (`del` + reference removal) is in the `finally` clause, guaranteeing execution regardless of extraction success or failure.

### Enforcement Mechanism

- `EdgeAbstraction.transform_frame_to_skeleton()` invokes `_destroy_frame()` in its `finally` block.
- `_destroy_frame()` executes: `del frame`, `self._sensor._frame_buffer = None`.
- `EdgeAbstraction.transform_audio_to_features()` invokes `_destroy_audio()` in its `finally` block.
- `_destroy_audio()` executes: `del audio`, `self._sensor._audio_buffer = None`.
- The `_watchdog_loop()` daemon thread polls at 10ms intervals and logs violations for any buffer exceeding TTL while still referenced.

### Verification Mechanism

- `tests/test_canonical_architecture.py`: Asserts `_frame_buffer is None` after transformation.
- `tests/test_irreversibility.py`: Validates destruction timing and non-reconstructability.
- `tests/test_layer_contracts.py`: `UPSTREAM_FORBIDDEN[Layer.L4_INFERENCE]` includes `raw_frame` and `audio_buffer`; `LayerBoundaryEnforcer.validate_transition()` raises `LayerBoundaryViolation` on prohibited data types.

### Fail Condition

**Severity: CRITICAL → HALT.** If frame destruction time exceeds `FRAME_TTL_MS` (33ms), `_destroy_frame()` raises `FrameDestructionError`. The calling function returns `None`, halting pipeline progression for that frame. The watchdog thread logs the violation independently.

### Non-Claim Boundary

- Does not guarantee physical memory zeroing at the hardware level; Python `del` removes the reference but the OS may defer page reclamation.
- Does not protect against a cold-boot DRAM extraction attack during the 0–33ms execution window.
- Does not claim that garbage collection timing is deterministic on the target OS.

---

## INV-02: Face Embedding Prohibition in L4+

Face embeddings (512-dimensional biometric vectors) are prohibited in L4+ memory space.

### Formal Definition

∀ t, ∀ v ∈ {face_embedding, biometric_vector, identity_token}: v ∉ memory_space(Lk, t) for k ∈ {4, 5, 6, 7, 8}. L4 inference operates on skeleton keypoints (≤34 dimensions) and spectral audio features only. No inference path produces, receives, or stores identity-bearing vectors.

### Enforcement Mechanism

- `FORBIDDEN_OUTPUTS[Layer.L4_INFERENCE]` = `{identity_token, biometric_vector, face_embedding}` in `core/layer_contracts.py`.
- `UPSTREAM_FORBIDDEN[Layer.L5_GOVERNANCE]` includes `face_embedding`, `biometric_vector`, `embedding`.
- `L4Output.__post_init__()` enforces `is_anonymous = True`; construction with `is_anonymous=False` raises `ValueError`.
- `LayerBoundaryEnforcer.validate_transition()` rejects transitions carrying forbidden data types.

### Verification Mechanism

- `tests/test_layer_contracts.py`: `test_raw_frame_blocked_at_l4` injects `raw_frame` into L3→L4 transition and asserts `LayerBoundaryViolation`.
- `tests/test_layer_contracts.py`: `test_embedding_blocked_at_l5` injects `face_embedding` into L4→L5 transition and asserts `LayerBoundaryViolation`.
- `tests/test_layer_contracts.py`: `test_non_anonymous_rejected` constructs `L4Output(is_anonymous=False)` and asserts `ValueError`.

### Fail Condition

**Severity: MAJOR → OUTPUT BLOCK.** `LayerBoundaryViolation` raised at transition boundary. Event is rejected. Violation is logged to the enforcer's `_violations` list for audit retrieval via `get_violations()`. All output is suppressed until the next structurally valid event.

### Non-Claim Boundary

- Does not prevent face embeddings from existing in L2/L3 during consent-gated enrollment workflows (enrollment is a distinct operational path with its own consent gate).
- Does not claim that the type system prevents all conceivable encoding of identity information in ≤34-dimensional vectors.
- Does not enforce this constraint via hardware memory isolation or memory tagging.

---

## INV-03: Compile-Time TTL Constants

Execution window TTL values are compile-time constants, not runtime-configurable parameters.

### Formal Definition

`FRAME_TTL_MS = 33` and `AUDIO_TTL_SECONDS = 3` are class-level constants in `EdgeAbstraction`. No setter method, configuration file, environment variable, or operator command can modify these values at runtime. Formally: ∀ system state S: FRAME_TTL_MS(S) = 33 ∧ AUDIO_TTL_SECONDS(S) = 3.

### Enforcement Mechanism

- `EdgeAbstraction.FRAME_TTL_MS = 33` defined as class attribute in `core/canonical_layers.py` line 153.
- `EdgeAbstraction.AUDIO_TTL_SECONDS = 3` defined as class attribute in `core/canonical_layers.py` line 154.
- No `set_ttl()`, no configuration loader, no environment variable reader exists for these values.
- Values are referenced directly in `_destroy_frame()`, `_destroy_audio()`, and `_watchdog_loop()`.

### Verification Mechanism

- `tests/test_canonical_architecture.py`: `assert l3_setup.FRAME_TTL_MS == 33`.
- `tests/test_canonical_architecture.py`: `assert l3_setup.AUDIO_TTL_SECONDS == 3`.
- Structural: `grep -r "set_ttl\|TTL_MS\s*=" core/` returns only the class-level constant definition.

### Fail Condition

**Severity: CRITICAL → HALT.** Not applicable at runtime — these values cannot be altered without source code modification and redeployment. Source code modification is outside the software threat model.

### Non-Claim Boundary

- Does not prevent a developer from modifying the source constant and redeploying a new binary.
- Does not claim that these TTL values are the theoretical minimum achievable on all hardware platforms.
- Does not guarantee sub-millisecond enforcement precision; the enforcement loop polls at 10ms intervals.

---

## INV-04: Network Air-Gap for L1–L4

L1–L4 layers have no external network connectivity.

### Formal Definition

∀ layer L ∈ {L1, L2, L3, L4}: network_sockets(L) = ∅. No code path in L1–L4 opens a TCP/UDP socket, makes an HTTP request, or transmits data to any external host. Network I/O is structurally absent from the `PhysicalSubstrate`, `SensorAcquisition`, `EdgeAbstraction`, and local inference module APIs.

### Enforcement Mechanism

- `PhysicalSubstrate` exposes only `get_operational_status()` and lifecycle methods — no network calls.
- `SensorAcquisition` captures to in-process buffers only — no network output.
- `EdgeAbstraction` transforms and destroys — no network output.
- `GovernanceFilter` (L5) operates in-process on event dictionaries — no network output.
- L8 `FederationCoordinator.contribute_gradient()` is the sole external-facing data path, gated by consent.

### Verification Mechanism

- Structural: no `import socket`, `import requests`, or `import urllib` in L1–L4 modules.
- `tests/test_layer_contracts.py`: Validates that no transition from L1–L4 carries data to an external endpoint.
- Code review: `PhysicalSubstrate`, `SensorAcquisition`, `EdgeAbstraction` have zero network dependencies.

### Fail Condition

**Severity: CRITICAL → HALT.** No runtime fail condition exists because the capability is structurally absent. Adding network I/O to L1–L4 requires source code modification.

### Non-Claim Boundary

- Does not enforce network isolation at the OS/firewall level; deployment must configure `iptables` or equivalent.
- Does not prevent a root-level adversary from attaching a network socket to the process.
- Does not apply to L7 (audit logging) or L8 (federation), which have controlled, consent-gated network access.

---

## INV-05: Watchdog Failure Domain Independence

The watchdog subsystem provides tiered failure isolation from the monitored inference process.

### Formal Definition

Two isolation tiers are defined:

**Software watchdog (partial isolation):**  
crash(main_thread) ⇏ crash(watchdog_thread) — thread-level isolation.  
crash(process) ⇒ crash(watchdog_thread) — process-wide termination kills both.

**Hardware watchdog (full isolation):**  
crash(process) ⇏ crash(hardware_watchdog) — silicon-level isolation.  
The hardware timer operates in a separate failure domain. Process-wide `SIGKILL`, segfault, or total software hang cannot prevent the hardware watchdog from firing.

| Tier | Isolation Level | Survives Thread Deadlock | Survives Process Crash | Survives Kernel Panic |
|------|----------------|-------------------------|----------------------|----------------------|
| Hardware (`/dev/watchdog`) | Full | ✅ | ✅ | ✅ |
| Software (daemon thread) | Partial | ✅ | ❌ | ❌ |

### Enforcement Mechanism

- Software watchdog: `EdgeAbstraction._watchdog_loop()` runs as a `daemon=True` thread, polling frame ages at 10ms intervals. Thread isolation ensures the watchdog continues executing even if the main processing path is blocked or deadlocked.
- Hardware watchdog: `HardwareWatchdog` in `utils/watchdog.py` writes heartbeats to `/dev/watchdog`. If the application hangs and fails to write within the timeout window, the hardware watchdog timer forces a system reset — independent of all software state.
- Governance watchdog: `modules_legacy/governance.py` tracks per-module heartbeat timestamps; timeout triggers transition to `DEGRADED` or `SAFE` state.
- Defense-in-depth: TTL enforcement in `_destroy_frame()` is the primary protection (inline in `finally` block). The watchdog is a secondary monitor. Neither depends on the other.

### Verification Mechanism

- `tests/test_canonical_architecture.py`: Validates that the watchdog thread starts and runs independently of the main processing thread.
- Manual: Hardware watchdog behavior verified on target hardware (Raspberry Pi, Jetson).

### Fail Condition

**Fail-State: OUTPUT SUPPRESS.** If the software watchdog thread itself fails to start, `start_watchdog()` logs the failure. TTL enforcement in `_destroy_frame()` remains active as primary protection (defense-in-depth). If the hardware watchdog device is unavailable, `HardwareWatchdog.start()` logs a warning and continues without hardware protection. Output is suppressed until software watchdog recovery or manual restart. Hardware watchdog is deployment-dependent and treated as defense-in-depth; its absence does not constitute an invariant violation and does not trigger OUTPUT SUPPRESS.

### Non-Claim Boundary

- The software watchdog provides **partial** failure isolation only — it does not survive process-wide termination signals (`SIGKILL`, segfault).
- Hardware watchdog provides **full** failure isolation but requires specific device support (`/dev/watchdog`) and may not be available on all deployment platforms.
- Does not claim real-time scheduling guarantees for the watchdog thread on general-purpose OS kernels.
- The invariant does not claim that both tiers are always active simultaneously; hardware watchdog is deployment-dependent.

---

## INV-06: Allowlist-Only Governance

The governance gate must operate in allowlist mode only.

### Formal Definition

∀ event payload P: fields(P) ⊆ ALLOWED_FIELDS. The governance filter accepts events containing only fields that are explicitly listed in the allowlist. Any field not in the allowlist causes the event to be rejected. Formally: ∀ f ∈ fields(P): f ∉ ALLOWED_FIELDS ⇒ reject(P).

ALLOWED_FIELDS = `{zone_id, timestamp, event_type, severity, skeleton_keypoints, audio_class, event_id, source_paper, is_valid, reason}`.

### Enforcement Mechanism

- `GovernanceFilter.ALLOWED_FIELDS` defined as a class-level `set` in `core/canonical_layers.py`.
- `GovernanceFilter.compliance_check()` computes `invalid_fields = set(payload.keys()) - self.ALLOWED_FIELDS`. If `invalid_fields` is non-empty, the event is rejected with state `GovernanceState.REJECTED`.
- Unknown fields trigger rejection, not silent omission.

### Verification Mechanism

- `tests/test_governance_filter.py`: Injects payloads with forbidden fields and asserts rejection.
- `tests/test_layer_contracts.py`: `test_output_forbidden_fields` verifies `LayerBoundaryEnforcer.check_output_constraints()` rejects forbidden outputs.

### Fail Condition

**Severity: MINOR → REJECT.** Event payload containing any field outside `ALLOWED_FIELDS` → `GovernanceState.REJECTED`. The event is logged with reason `Forbidden fields: {invalid_fields}` and does not proceed to L6. Other events are unaffected.

### Non-Claim Boundary

- Does not claim that the allowlist is the minimal sufficient set; the allowlist may contain more fields than strictly necessary.
- Does not enforce semantic validation of allowlisted field values (e.g., severity range is validated by `L4Output.__post_init__()`).
- Does not prevent overly permissive allowlist configuration within the permitted schema.

---

## INV-07: Denylist Prohibition

Denylist-based filtering is architecturally prohibited. No mechanism exists to define, configure, or invoke denylist filtering.

### Formal Definition

¬∃ function f in the governance module such that f implements pattern `if field ∈ denylist: reject`. All filtering is implemented as the complement of an allowlist: `if field ∉ allowlist: reject`. Formally: ¬∃ D ⊂ FieldNames such that GovernanceFilter uses D as a rejection criterion.

### Enforcement Mechanism

- `GovernanceFilter.compliance_check()` uses set-difference against `ALLOWED_FIELDS` (allowlist complement).
- No `DENIED_FIELDS`, `DENYLIST`, `BLOCKLIST`, or equivalent data structure exists anywhere in the governance pipeline.
- ARCHITECTURE_CANONICAL.md §4.3 designates denylist prohibition as an architectural invariant.

### Verification Mechanism

- Structural: `grep -r "denylist\|deny_list\|blocklist\|block_list\|DENIED" core/` returns no governance-related matches.
- `tests/test_governance_filter.py`: Validates that unknown fields are rejected by allowlist complement, not matched against a denylist.

### Fail Condition

**Severity: CRITICAL → HALT.** Not applicable at runtime — the capability does not exist. Introducing a denylist requires source code modification, which would trigger architectural review.

### Non-Claim Boundary

- Does not prevent a developer from adding a denylist in a future code change (architectural governance process must block this).
- Does not claim that allowlist-only filtering and denylist filtering are semantically non-equivalent in all theoretical models; the constraint is an architectural choice, not a mathematical necessity.

---

## INV-08: Fail-Closed on Invariant Violation

All invariant violations trigger fail-closed behavior. The system halts or suppresses output rather than continuing with degraded privacy.

### Formal Definition

∀ invariant I: violation(I) ⇒ (system_halt ∨ output_suppression). No invariant violation causes the system to continue normal operation with reduced privacy guarantees. Formally: ¬∃ invariant I such that violation(I) ∧ continued_output = true ∧ privacy_guarantee < baseline.

### Enforcement Mechanism

- CRITICAL violations → `FrameDestructionError`, `LayerBoundaryViolation`, `ValueError` → pipeline HALT.
- MAJOR violations → output suppression, event DROP, audit log entry.
- MINOR violations → individual event REJECT, pipeline continues for other events.
- INFO events → audit log only, no privacy impact.
- Privacy LED state `UNKNOWN` → system halt (ARCHITECTURE_CANONICAL.md §6.5).
- Governance gate unreachable → all L4→L6 traffic blocked.
- Watchdog heartbeat missed → `SIGKILL` (hardware) or state transition to `SAFE` (software).

### Verification Mechanism

- `tests/test_failsafe_dropout.py`: Simulates subsystem failures and asserts fail-closed behavior.
- `tests/test_canonical_architecture.py`: Validates that TTL violations raise `FrameDestructionError`.
- `tests/test_layer_contracts.py`: Validates that boundary violations raise `LayerBoundaryViolation`.

### Fail Condition

**Severity: CRITICAL → HALT.** This invariant IS the meta-fail-condition. If fail-closed behavior itself fails (e.g., an exception is caught and silently suppressed), the violation propagates to the watchdog, which triggers hardware reset as a last resort.

### Non-Claim Boundary

- Does not guarantee that all exception paths are covered; unhandled exceptions in custom integrations may bypass fail-closed semantics.
- Does not claim zero-downtime operation; fail-closed explicitly trades availability for privacy.
- Does not claim that the system can self-recover after HALT; operator intervention is required for restart.

---

## INV-09: Volatile-Only Processing for L1–L4

All raw sensor data and intermediate inference tensors in L1–L4 reside exclusively in volatile memory (RAM).

### Formal Definition

∀ d ∈ data(L1 ∪ L2 ∪ L3 ∪ L4): storage_class(d) = VOLATILE. No file handle, database connection, or persistent queue is opened for raw data types within L1–L4. All buffers are in-process Python objects (`Optional[Any]`) or NumPy arrays in heap memory. Formally: ∀ t, ∀ d ∈ raw_data: ¬∃ path p on disk such that write(d, p) occurs in L1–L4.

### Enforcement Mechanism

- `SensorAcquisition.__init__()`: `_frame_buffer: Optional[Any] = None`, `_audio_buffer: Optional[Any] = None` — in-process memory only.
- `EdgeAbstraction` operates on these buffers and destroys them via `del` + null assignment.
- `FORBIDDEN_OUTPUTS[Layer.L2_SENSOR]` = `{persistent_storage}` — prevents L2 from writing to disk.
- No `open()`, `write()`, `sqlite3.connect()`, or database ORM call exists in L1–L4 code paths.

### Verification Mechanism

- `tests/test_irreversibility.py`: Validates that no disk artifacts are created during frame processing.
- `tests/test_canonical_architecture.py`: Validates volatile buffer lifecycle.
- Structural: no file I/O imports (`open`, `pathlib.Path.write_*`) in L1–L4 processing paths.

### Fail Condition

**Severity: CRITICAL → HALT.** If an L1–L4 component attempts persistent storage, `FORBIDDEN_OUTPUTS` enforcement in `LayerBoundaryEnforcer.check_output_constraints()` raises `LayerBoundaryViolation`.

### Non-Claim Boundary

- Does not enforce `mlock()` or `MADV_DONTDUMP` at the Python level; these require C-level extensions and `CAP_IPC_LOCK` capability.
- Does not prevent the OS from swapping process memory to disk (deployment must set `vm.swappiness=0`).
- Does not prevent crash dumps from containing process memory (deployment must configure `coredump_filter`).

---

## INV-10: Density Constraint on L3 Output

L3 output dimensionality is capped at 34 keypoints. This cap, combined with the non-injective mapping and absence of auxiliary channels, makes pixel-space reconstruction structurally underdetermined.

### Formal Definition

∀ skeleton s output by L3: dims(s) ≤ 34. Let N = input frame element count (pixels × channels) and M = output skeleton element count (≤ 34). The compression invariant is:

N / M ≥ MIN_COMPRESSION_RATIO (where MIN_COMPRESSION_RATIO = 1000)

This is resolution-dependent by construction — the check is against the actual input N, not a fixed resolution constant:

| Input Resolution | N (pixels × channels) | Bits In | Bits Out (34 × 32b) | Compression Ratio | Channel Capacity Reduction |
|-----------------|----------------------|---------|---------------------|-------------------|---------------------------|
| 1920×1080 (1080p) | 6,220,800 | 49,766,400 | 1,088 | 5,718:1 | 45,740:1 |
| 1280×720 (720p) | 2,764,800 | 22,118,400 | 1,088 | 2,541:1 | 20,330:1 |
| 640×480 (VGA) | 921,600 | 7,372,800 | 1,088 | 847:1 | 6,776:1 |

**Minimum bound**: At VGA (640×480), the compression ratio is ≈ 847:1 which is below the `MIN_COMPRESSION_RATIO = 1000` threshold. This means **VGA input is rejected** by the compression ratio check. The minimum supported resolution is approximately 740×480 (ratio ≥ 1000:1).

The compression ratio is enforced as `input_elements / output_elements ≥ MIN_COMPRESSION_RATIO`. This is resolution-aware by construction — the check is against the actual input, not a fixed constant.

The inverse image f⁻¹(y) for any valid skeleton y is an uncountably infinite set.

**Information-Theoretic Basis**: By the data processing inequality (Cover & Thomas 1991), H(X|Y) ≥ H(X) − H(Y). At 1080p, the channel capacity reduction of 45,740:1 yields near-maximal conditional entropy. Reconstruction requires recovering ≈ 49.8M bits from 1,088 bits — a structurally underdetermined inverse problem. Three conditions must hold simultaneously for non-reconstructability:

1. **Density constraint**: dims(output) ≤ 34 (this invariant)
2. **Non-injectivity**: f is many-to-one; the kernel ker(f) is infinite-dimensional
3. **No auxiliary channel**: raw frame destroyed (INV-01), no side-channel file written, no network socket in L1–L4 (INV-04)

All three are structurally enforced. Violation of any one weakens the non-reconstructability claim.

**Why 34 keypoints**: 34 corresponds to the MediaPipe BlazePose topology (33 body landmarks + 1 root). This is a pose-estimation industry standard that encodes only body joint positions (x, y, z, visibility per joint). Facial features, skin texture, clothing texture, body surface geometry, and background content are discarded at L3.

### Enforcement Mechanism

- `EdgeAbstraction.MAX_SKELETON_DIMS = 34` — class constant in `core/canonical_layers.py`.
- `EdgeAbstraction.transform_frame_to_skeleton()` checks: `if len(skeleton) > self.MAX_SKELETON_DIMS: raise ValueError`.
- `L3Output.__post_init__()` checks: `if len(self.skeleton_keypoints) > 34: raise ValueError`.
- `EdgeAbstraction.MIN_COMPRESSION_RATIO = 1000` enforces minimum compression **against actual input dimensions**, not a fixed resolution assumption.

### Verification Mechanism

- `tests/test_layer_contracts.py`: `test_skeleton_max_34_dims` constructs `L3Output` with 34 keypoints and asserts success.
- `tests/test_layer_contracts.py`: `test_skeleton_exceeds_34_rejected` constructs `L3Output` with 35 keypoints and asserts `ValueError`.
- `tests/test_canonical_architecture.py`: Validates compression ratio ≥ 1000:1.

### Fail Condition

**Fail-State: EVENT REJECT.** Skeleton with >34 dimensions → `ValueError` at `L3Output` construction or within `transform_frame_to_skeleton()`. Input with compression ratio < 1000:1 → rejected at the compression check. The frame is still destroyed (in the `finally` block) in either case.

### Non-Claim Boundary

- Does not claim that 34 keypoints is the theoretical minimum for pose inference tasks; alternative topologies may use fewer.
- Does not claim that 34-dimensional data is inherently non-identifying in all contexts (e.g., gait analysis on a population of N < 10 may yield re-identification risk).
- Does not provide formal proof of reconstruction impossibility; the claim is information-theoretic (data processing inequality) and structural (no auxiliary channel), not proven via formal verification tools.
- The 1000:1 minimum ratio implies a minimum input resolution. Sub-VGA inputs are rejected, which is a deployment constraint.

---

## INV-11: Consent-Gated Embedding Enrollment

Consent verification is required before face embedding enrollment.

### Formal Definition

∀ embedding e enrolled in FAISS index: consent(e.subject) = verified ∧ consent(e.subject) ≠ expired. Consent is per-operation; blanket consent for future operations does not exist. Formally: enroll(e) requires consent(e.subject) = true at time of enrollment.

### Enforcement Mechanism

- `FaissFaceIndex.add_embedding_safe()` in `infrastructure/indexing/faiss_face_index.py` requires a consent parameter. Enrollment without consent raises an error or returns failure.
- `FaissFaceIndex.DEFAULT_TTL_SECONDS = 3600` enforces session-scoped TTL on enrolled embeddings.
- `FaissFaceIndex.purge_expired_embeddings()` removes embeddings that have exceeded their TTL.

### Verification Mechanism

- `tests/test_face_registry.py`: Tests enrollment with and without consent.
- `tests/test_identity_mgmt.py`: Tests identity management consent flows.
- `tests/test_canonical_architecture.py`: Validates TTL enforcement on embeddings.

### Fail Condition

**Severity: MINOR → REJECT.** Enrollment attempt without consent → operation rejected, embedding not stored. Expired embeddings are purged by TTL enforcement; access to a purged embedding returns no match.

### Non-Claim Boundary

- Does not validate that the consenting party has informed understanding of the enrollment purpose.
- Does not claim consent records are cryptographically immutable.
- Does not prevent an operator with direct database access from manually inserting an embedding outside the system API.

---

## INV-12: Federation Deletion Propagation

Individual deletion requests must propagate to the federation and cause the global model to be updated.

### Formal Definition

∀ deletion_request(campus_id, individual_id): process(request) ⇒ global_model_version incremented ∧ individual contributions excluded from future aggregation rounds. Propagation must complete within one federation round (the defined SLA).

### Enforcement Mechanism

- `FederationCoordinator.process_deletion_request(campus_id, individual_id)` increments `_global_model_version` and logs the deletion.
- Campus withdrawal triggers `_purge_campus_gradients(campus_id)` which deletes all stored gradient contributions via `del self._gradient_contributions[campus_id]` and increments the global model version.
- `FederationCoordinator.revoke_consent()` adds the campus to `_withdrawal_pending`, blocking further contributions.

### Verification Mechanism

- `tests/test_federation_dp.py`: Tests deletion request processing and model version increment.
- `tests/test_canonical_architecture.py`: Tests withdrawal and gradient purge.

### Fail Condition

**Severity: MAJOR → OUTPUT BLOCK.** If the federation coordinator is unreachable, deletion requests take effect locally (campus stops contributing). Federation output is blocked until deletion propagation is confirmed. Campus withdrawal completes even if the coordinator cannot be contacted.

### Non-Claim Boundary

- Does not claim that deletion fully reverses a trained model's learned parameters attributable to a specific individual; gradient influence is distributed across aggregation rounds and cannot be deterministically separated.
- Does not guarantee real-time deletion propagation; bounded by federation round duration.
- Does not claim deletion from audit logs; audit log immutability is a separate concern.

---

## INV-13: Federation Payload Restrictions

Federation payloads must contain no raw data, embeddings, or identifiers. Only DP-protected gradient summaries are permitted.

### Formal Definition

∀ payload p transmitted via L8: type(p) = gradient_summary ∧ {raw_frame, audio_buffer, embedding, identity, biometric_vector} ∩ contents(p) = ∅. Payloads are gradient vectors only, clipped and noised before transmission.

### Enforcement Mechanism

- `FORBIDDEN_OUTPUTS[Layer.L8_FEDERATION]` = `{raw_data, embedding, identifier}` in `core/layer_contracts.py`.
- `UPSTREAM_FORBIDDEN[Layer.L8_FEDERATION]` = `{raw_frame, audio_buffer, embedding, identity, biometric_vector}`.
- `FederationCoordinator.contribute_gradient()` requires verified consent and rejects contributions from withdrawing campuses.
- `HierarchicalFedAvgCoordinator` operates on `np.ndarray` gradient vectors with sample counts — no identity-bearing fields in its API.

### Verification Mechanism

- `tests/test_federation_dp.py`: Validates gradient payloads and DP noise application.
- `tests/test_layer_contracts.py`: `LayerBoundaryEnforcer` blocks forbidden types from entering L8.
- `tests/test_canonical_architecture.py`: Validates federation consent flow.

### Fail Condition

**Severity: MAJOR → OUTPUT BLOCK.** `LayerBoundaryViolation` raised if forbidden data types are detected in an L8-bound transition. Gradient contribution rejected if consent is missing or campus is withdrawing. Federation output blocked until compliant payload submitted.

### Non-Claim Boundary

- Does not claim that gradient summaries are immune to gradient inversion attacks; DP noise mitigates but does not eliminate this risk (see DP Boundary Specification below).
- Does not claim payload inspection covers all possible steganographic encoding of identity information.
- Does not enforce encrypted transport; deployment must configure TLS on federation channels.

---

## INV-14: TTL Enforcement Non-Disableable

The TTL enforcement loop cannot be disabled by configuration, operator command, or runtime parameter.

### Formal Definition

∀ system state S: ttl_enforcement_active(S) = true. No API endpoint, configuration key, environment variable, or operator command exists such that ttl_enforcement_active can be set to false. Formally: ¬∃ action a available to operator such that execute(a) ⇒ ttl_enforcement_active = false.

### Enforcement Mechanism

- `EdgeAbstraction._watchdog_loop()` is started by `CanonicalRuntimeEngine.start()` via `self.L3_edge.start_watchdog()`.
- `_watchdog_running` is set to `True` and controlled only by `start_watchdog()` / `stop_watchdog()`, which are lifecycle methods tied to engine start/stop.
- TTL checking is embedded in `_destroy_frame()` and `_destroy_audio()` — it is part of the destruction path, not a separate configurable toggle.
- No `disable_ttl()`, `set_ttl_enabled(False)`, or `SKIP_TTL_CHECK` exists.

### Verification Mechanism

- `tests/test_canonical_architecture.py`: Validates that TTL constants are checked during every frame destruction.
- Structural: `grep -r "disable.*ttl\|skip.*ttl\|ttl.*enabled" core/` returns no matches.

### Fail Condition

**Severity: CRITICAL → HALT.** Not applicable at runtime — the capability to disable does not exist. TTL enforcement is embedded in the destruction code path, which executes in a `finally` block regardless of processing outcome.

### Non-Claim Boundary

- Does not prevent `stop_watchdog()` from being called when the engine is stopped (this is intended lifecycle behavior, not a bypass; the engine itself has stopped processing).
- Does not claim that TTL enforcement survives process crash; post-crash, volatile memory is lost by OS semantics (which is the desired outcome).
- Does not prevent a code-level modification from removing the TTL check (source modification is outside threat model).

---

## INV-15: Privacy Mode Restart Default

System restart always initializes in Privacy Mode.

### Formal Definition

∀ restart event R: post_state(R) = PRIVACY_MODE ∧ face_recognition(R) = DISABLED ∧ LED_state(R) = GREEN. Transition from PRIVACY to ACTIVE mode requires explicit operator acknowledgment recorded in the audit log. Formally: ¬∃ automatic_transition : PRIVACY → ACTIVE.

### Enforcement Mechanism

- `CanonicalRuntimeEngine.__init__()` initializes all layers from L1 through L8 in default (PRIVACY) state — no active face recognition.
- ARCHITECTURE_CANONICAL.md §7.4: "On restart: Initialize to PRIVACY mode. Require operator acknowledgment before ACTIVE mode."
- `PrivacyLEDController` initializes LED to `PRIVACY` state (green) at boot.
- No auto-escalation path exists from PRIVACY to ACTIVE mode without operator interaction.
- No persistent state file carries "last active mode" across restarts.

### Verification Mechanism

- `tests/test_canonical_architecture.py`: Validates default initialization state.
- `tests/test_audit_deficiencies.py`: Validates LED state at boot is PRIVACY (green).

### Fail Condition

**Severity: CRITICAL → HALT.** If Privacy LED cannot be set at boot (e.g., hardware fault), system halts per INV-08 and ARCHITECTURE_CANONICAL.md §6.5. If operator attempts ACTIVE mode without acknowledgment, the transition is blocked.

### Non-Claim Boundary

- Does not persist state across power cycles; restart always returns to PRIVACY mode regardless of prior state (this is the desired invariant).
- Does not claim that PRIVACY mode disables all inference — anonymous skeleton-based inference continues.
- Does not claim that the operator acknowledgment mechanism is resistant to social engineering.

---

## Non-Persistence Boundary Position Lock

### Formal Definition

The non-persistence boundary is architecturally fixed at L3 (Edge Abstraction). No configuration, deployment option, or operator command can relocate the boundary to L4, L5, or any other layer.

∀ system configuration C: persistence_boundary(C) = L3. Raw sensor data destruction occurs at L3 and solely at L3. Data persisting beyond L3 has already been irreversibly transformed. This position lock ensures that:

1. L1–L2 are capture-only (volatile buffers)
2. L3 is destroy-and-transform (irreversible boundary)
3. L4+ operates on skeleton/feature data only (post-boundary)

### Enforcement Mechanism

- `EdgeAbstraction` (L3) is the only class with destruction methods (`_destroy_frame()`, `_destroy_audio()`).
- No destruction API exists in L1, L2, L4, L5, L6, L7, or L8.
- `CanonicalRuntimeEngine.process_frame()` executes L3 before any downstream processing — the pipeline structurally forces L3 transit.
- `UPSTREAM_FORBIDDEN` in `core/layer_contracts.py` blocks raw data from entering L4+, making the boundary position implicit in the transition matrix.

### Verification Mechanism

- `tests/test_layer_contracts.py`: Forward flow from L3→L4 requires `skeleton` type; `raw_frame` is forbidden.
- `tests/test_irreversibility.py`: End-to-end verification that raw frames are destroyed at L3.
- Structural: `_destroy_frame()` and `_destroy_audio()` exist only in `EdgeAbstraction`.

### Non-Claim Boundary

- Does not prevent future architectural changes from adding a secondary boundary (would require governance approval and violate document lock).
- The boundary is enforced by code structure and `UPSTREAM_FORBIDDEN`, not by a formal position constant (the constraint is structural, not declarative).

---

## Temporal Safety Property

The following formal temporal invariant governs all raw sensor buffer lifetimes. This elevates the TTL mechanism from a procedural implementation detail to a mathematical safety property.

### Formal Statement

```
∀ raw_buffer b ∈ {RGB_frame, audio_waveform}:
    created(b) = t₀ →
    ∃ t_destroy such that:
        t₀ < t_destroy ≤ t₀ + TTL(b)
        ∧ ∀ t > t_destroy : addressable(b, t) = false
```

Where:
- TTL(RGB_frame) = 33ms (`EdgeAbstraction.FRAME_TTL_MS`)
- TTL(audio_waveform) = 3000ms (`EdgeAbstraction.AUDIO_TTL_SECONDS`)
- `addressable(b, t)` := reachable via live Python-level references at time t (not a claim about hardware memory zeroing; see INV-01 Formal Definition)
- `created(b)` = timestamp at which the sensor acquisition function stores the buffer

### Interpretation

This property guarantees that every raw sensor buffer has a **bounded lifetime**. The destruction event t_destroy is not optional — it is structurally forced by the `finally` block in `transform_frame_to_skeleton()` and `transform_audio_to_features()`. The watchdog independently monitors for violations of this bound.

### Relationship to Invariants

| Component | Role in Temporal Property |
|-----------|---------------------------|
| INV-01 | Enforces t_destroy via `_destroy_frame()` / `_destroy_audio()` |
| INV-03 | Guarantees TTL(b) is a compile-time constant |
| INV-14 | Guarantees TTL enforcement cannot be disabled |
| Watchdog (INV-05) | Independent monitor that detects t > t₀ + TTL(b) violations |

---

## Invariant Trace Matrix

Each invariant traces deterministically from its formal definition through the enforcing code, to the validating test, and to the originating paper section.

| Invariant | Code File | Function / Constant | Test File | Test Function | Paper Section |
|-----------|-----------|---------------------|-----------|---------------|---------------|
| INV-01 | `core/canonical_layers.py` | `EdgeAbstraction._destroy_frame()` | `tests/test_irreversibility.py` | `test_frame_ttl` | Paper 17 §3.2 |
| INV-01 | `core/canonical_layers.py` | `EdgeAbstraction._watchdog_loop()` | `tests/test_canonical_architecture.py` | `test_watchdog_independence` | Paper 18 §4.1 |
| INV-02 | `core/layer_contracts.py` | `FORBIDDEN_OUTPUTS[L4_INFERENCE]` | `tests/test_layer_contracts.py` | `test_embedding_blocked_at_l5` | Paper 17 §3.3 |
| INV-02 | `core/layer_contracts.py` | `L4Output.__post_init__()` | `tests/test_layer_contracts.py` | `test_non_anonymous_rejected` | Paper 17 §3.3 |
| INV-03 | `core/canonical_layers.py` | `EdgeAbstraction.FRAME_TTL_MS = 33` | `tests/test_canonical_architecture.py` | `test_ttl_constants` | Paper 17 §3.1 |
| INV-03 | `core/canonical_layers.py` | `EdgeAbstraction.AUDIO_TTL_SECONDS = 3` | `tests/test_canonical_architecture.py` | `test_ttl_constants` | Paper 17 §3.1 |
| INV-04 | `core/canonical_layers.py` | `PhysicalSubstrate`, `SensorAcquisition` | `tests/test_layer_contracts.py` | `test_forward_flow_allowed` | Paper 17 §2.1 |
| INV-05 | `core/canonical_layers.py` | `EdgeAbstraction.start_watchdog()` | `tests/test_canonical_architecture.py` | `test_watchdog_independence` | Paper 18 §4.1 |
| INV-05 | `utils/watchdog.py` | `HardwareWatchdog.start()` | Manual verification | Hardware test | Paper 18 §4.2 |
| INV-06 | `core/canonical_layers.py` | `GovernanceFilter.compliance_check()` | `tests/test_governance_filter.py` | `test_forbidden_fields_rejected` | Paper 18 §5.1 |
| INV-06 | `core/canonical_layers.py` | `GovernanceFilter.ALLOWED_FIELDS` | `tests/test_layer_contracts.py` | `test_output_forbidden_fields` | Paper 18 §5.1 |
| INV-07 | `core/canonical_layers.py` | `GovernanceFilter.compliance_check()` | `tests/test_governance_filter.py` | `test_allowlist_complement` | Paper 18 §5.2 |
| INV-08 | `core/canonical_layers.py` | `FrameDestructionError` | `tests/test_failsafe_dropout.py` | `test_fail_closed` | Paper 18 §6.1 |
| INV-08 | `core/canonical_layers.py` | `GovernanceState.REJECTED` | `tests/test_canonical_architecture.py` | `test_governance_reject` | Paper 18 §6.1 |
| INV-09 | `core/canonical_layers.py` | `SensorAcquisition.__init__()` | `tests/test_irreversibility.py` | `test_volatile_storage` | Paper 17 §3.2 |
| INV-09 | `core/layer_contracts.py` | `FORBIDDEN_OUTPUTS[L2_SENSOR]` | `tests/test_layer_contracts.py` | `test_output_forbidden_fields` | Paper 17 §3.2 |
| INV-10 | `core/canonical_layers.py` | `EdgeAbstraction.MAX_SKELETON_DIMS = 34` | `tests/test_layer_contracts.py` | `test_skeleton_max_34_dims` | Paper 17 §3.4 |
| INV-10 | `core/layer_contracts.py` | `L3Output.__post_init__()` | `tests/test_layer_contracts.py` | `test_skeleton_exceeds_34_rejected` | Paper 17 §3.4 |
| INV-11 | `infrastructure/indexing/faiss_face_index.py` | `add_embedding_safe()` | `tests/test_face_registry.py` | `test_consent_enrollment` | Paper 18 §7.1 |
| INV-12 | `core/canonical_layers.py` | `FederationCoordinator.process_deletion_request()` | `tests/test_federation_dp.py` | `test_deletion_propagation` | Paper 18 §8.1 |
| INV-12 | `core/canonical_layers.py` | `FederationCoordinator._purge_campus_gradients()` | `tests/test_canonical_architecture.py` | `test_withdrawal_purge` | Paper 18 §8.1 |
| INV-13 | `core/layer_contracts.py` | `FORBIDDEN_OUTPUTS[L8_FEDERATION]` | `tests/test_layer_contracts.py` | `test_federation_forbidden` | Paper 18 §8.2 |
| INV-13 | `core/layer_contracts.py` | `UPSTREAM_FORBIDDEN[L8_FEDERATION]` | `tests/test_federation_dp.py` | `test_payload_validation` | Paper 18 §8.2 |
| INV-14 | `core/canonical_layers.py` | `EdgeAbstraction._destroy_frame()` (embedded TTL) | `tests/test_canonical_architecture.py` | `test_ttl_enforcement` | Paper 17 §3.1 |
| INV-15 | `core/canonical_layers.py` | `CanonicalRuntimeEngine.__init__()` | `tests/test_canonical_architecture.py` | `test_default_privacy_mode` | Paper 18 §7.4 |
| INV-15 | `core/privacy_led.py` | `PrivacyLEDController.__init__()` | `tests/test_audit_deficiencies.py` | `test_led_boot_state` | Paper 18 §6.5 |

---

## Trusted Computing Base Declaration

The Trusted Computing Base (TCB) consists of the minimal set of components whose correct operation is **necessary and sufficient** for invariant preservation. Components outside the TCB may fail without compromising privacy guarantees. If any TCB component is compromised, one or more invariants may be violated.

### Trusted Components

**The following components are explicitly trusted:**

1. **Linux kernel memory isolation** — Process memory is private; other user-space processes cannot read sensor buffers. Required by INV-01, INV-09.
2. **CPython memory model** — `del` removes the last reference; reference counting triggers deallocation. `finally` blocks execute regardless of exception state. Required by INV-01, INV-08.
3. **`/dev/watchdog` driver correctness** — Kernel watchdog driver correctly fires reset after timeout. Required by INV-05 (hardware tier).
4. **Monotonic clock source** — `time.monotonic()` or equivalent provides non-decreasing timestamps with ≤10ms jitter. Required by INV-01, INV-03, INV-14.
5. **Boot chain integrity** — The kernel, Python interpreter, and application code loaded at boot have not been tampered with. Required by all invariants (implicit). This is an **assumption, not an enforcement** — no measured/signed boot is implemented.
6. **RAM volatility** — Physical RAM loses contents on power loss. DRAM refresh ceases → data decay. Required by INV-01, INV-09.
7. **Hardware watchdog timer** — Silicon timer fires independently of all software state. Required by INV-05 (hardware tier).

### TCB Component Map

| Component | Layer | TCB Role | Trust Assumption | Invariants Dependent |
|-----------|-------|----------|------------------|---------------------|
| `core/canonical_layers.py` | Application | L1–L8 implementation, destruction, governance | `finally`-block + `del` semantics correct | INV-01–15 |
| `core/layer_contracts.py` | Application | Boundary enforcement, forbidden data maps | `FORBIDDEN_OUTPUTS` and `UPSTREAM_FORBIDDEN` maps are complete and correct | INV-02, INV-04, INV-09, INV-13 |
| `core/privacy_led.py` | Application | Visual system state indicator | Hardware LED connected and functional | INV-15 |
| `utils/watchdog.py` | Application | Hardware watchdog binding | `/dev/watchdog` device exists, kernel driver loaded | INV-05 |
| CPython 3.x runtime | Runtime | Object lifecycle, GC, exception handling | Reference counting deterministic; GC collects cycles | INV-01, INV-08, INV-09 |
| Linux kernel ≥ 4.x | OS | Process isolation, memory management, clock | Memory cleared on exit; `CLOCK_MONOTONIC` available | INV-01, INV-03, INV-09, INV-14 |
| DRAM hardware | Hardware | Volatile storage | Contents lost on power loss within JEDEC refresh specs | INV-01, INV-09 |
| Watchdog silicon timer | Hardware | Independent timeout | Fires regardless of software state | INV-05 |

### Kernel Assumptions

| Assumption | Required For | Impact If Violated |
|------------|-------------|-------------------|
| `del` removes object reference and triggers deallocation | INV-01, INV-09 | Raw data may persist in deallocated pages |
| Process exit clears all process memory pages | INV-01, INV-09, INV-15 | Post-crash memory may contain raw data |
| `daemon=True` threads terminate with parent process | INV-05 (software tier) | Orphaned watchdog threads |
| `CLOCK_MONOTONIC` available and non-decreasing | INV-01, INV-03, INV-14 | TTL enforcement accuracy degraded |
| `/dev/watchdog` timeout < 60s | INV-05 (hardware tier) | Hang detection delay exceeds acceptable bound |
| `fork()` / `exec()` do not leak parent file descriptors | INV-04 | Potential network socket inheritance |

### OS Guarantees Required

| Guarantee | Configuration Required | Invariants Dependent |
|-----------|----------------------|---------------------|
| No swap of sensor buffers | `vm.swappiness=0` or `mlock()` on buffers | INV-01, INV-09 |
| No core dumps of sensor data | `coredump_filter = 0x00` or `MADV_DONTDUMP` | INV-01, INV-09 |
| Network namespace isolation (optional) | `iptables` or network namespace for L1–L4 | INV-04 |
| Watchdog device availability | `modprobe bcm2835_wdog` or equivalent | INV-05 |

### Required Capabilities

| Capability | Purpose | Required By |
|------------|---------|-------------|
| `CAP_IPC_LOCK` | `mlock()` to prevent swapping of raw buffers | INV-01, INV-09 (deployment hardening) |
| `CAP_SYS_RAWIO` | Hardware watchdog access via `/dev/watchdog` | INV-05 (hardware tier) |
| `CAP_NET_ADMIN` | Network namespace isolation for L1–L4 | INV-04 (deployment hardening) |

> [!WARNING]
> Capabilities are deployment-level hardening requirements. The architecture enforces invariants at the application level without them. These capabilities provide defense-in-depth against OS-level bypass.

> [!CAUTION]
> **Boot chain integrity is assumed, not enforced.** No measured boot, secure boot, or code signing is implemented. A compromised kernel or modified Python interpreter can violate any invariant. This is explicitly outside the software threat model.

---

## Differential Privacy Boundary Specification

### DP Budget Invariant

The following DP budget constraint is treated as a system invariant, equivalent in authority to INV-01 through INV-15:

```
∀ federation session S with T rounds:
    ε_cumulative(S) = Σ_{t=1}^{T} ε_round(t)
    ∧ ε_cumulative(S) is tracked by PrivacyAccountant
    ∧ ε_cumulative(S) is validated against ε_target = 95.97
    ∧ ∀ gradient g contributed in round t:
        ‖g‖₂ ≤ C  (enforced by L2-norm clipping)
        ∧ noise(g) ~ N(0, σ²C²I)  (Gaussian mechanism)
```

**Fail-State: OUTPUT SUPPRESS.** If `PrivacyAccountant.validate_budget()` returns `is_valid = False` (budget mismatch > tolerance), federation output is flagged for review. The system does not halt (DP validation is a post-hoc audit), but the discrepancy is recorded in the training history.

### DP Parameters (As Implemented)

All values below are taken directly from `modules/fl_coordinator.py` and `modules/federated_learning/privacy_accountant.py`. No values are invented.

| Parameter | Symbol | Value | Source | Invariant Role |
|-----------|--------|-------|--------|----------------|
| Noise multiplier | σ | 0.5 | `FedAvgCoordinator.__init__(privacy_sigma=0.5)` | Determines per-round ε |
| Gradient clipping norm | C | 1.0 | `FedAvgCoordinator.__init__(clipping_norm=1.0)` | Bounds sensitivity |
| Failure probability | δ | 10⁻⁵ | `PrivacyAccountant.__init__(delta=1e-5)` | DP failure probability |
| Sampling ratio | q | 1.0 | Full participation (worst case) | Amplification factor |
| Target ε (10 rounds) | ε_target | 95.97 | `PrivacyAccountant.validate_budget(target_epsilon=95.97)` | Paper 13 validated bound |
| Composition method | — | Linear | `ε_cumulative += delta_epsilon` per round | Upper bound (conservative) |
| Staleness decay | γ | 0.5 | `HierarchicalFedAvgCoordinator.__init__(staleness_gamma=0.5)` | Aggregation dampening |
| Staleness bound | τ_max | 2 epochs | `np.random.randint(0, 3)` in simulation | Max contribution lag |
| Aggregation weight | α(τ) | 1/(1+τ)^γ | `compute_staleness_weight(staleness)` | Staleness dampening |

### Formal DP Guarantee

Per-round privacy cost (moments accountant, Abadi et al. 2016 — Paper 13 Equation 4):

```
ε_round = (q × √(2 × ln(1/δ))) / σ
```

Cumulative budget (linear composition, conservative upper bound):

```
ε_T = Σ_{t=1}^{T} ε_round_t
```

For the default parameters (σ=0.5, q=1.0, δ=10⁻⁵, T=10):

```
ε_10 ≈ 95.97, providing a (95.97, 10⁻⁵)-DP guarantee
```

The system tracks ε cumulatively via `PrivacyAccountant.update_budget()` and validates against the Paper 13 target via `PrivacyAccountant.validate_budget(target_epsilon=95.97, tolerance=1.0)`.

### Gradient Clipping Enforcement

```
∀ gradient g before DP noise addition:
    ‖g‖₂ > C ⇒ g ← g × (C / ‖g‖₂)
```

Implemented in `FedAvgCoordinator.apply_differential_privacy()`:

```python
grad_norm = np.linalg.norm(gradients)
if grad_norm > self.C:
    gradients = gradients * (self.C / grad_norm)
```

Clipping bounds the L2 sensitivity of the gradient query to C = 1.0, which is required for the Gaussian mechanism's (ε, δ)-DP guarantee to hold.

### Staleness-Aware Aggregation Constraint

∀ campus update u with staleness τ = current_epoch − base_epoch:

- Staleness weight: α(τ) = 1 / (1 + τ)^γ where γ = 0.5
- Combined weight: w = α(τ) × (n_campus / n_total)
- Stale updates are geometrically down-weighted, preventing outdated contributions from dominating aggregation.
- τ_max = 2 epochs: updates older than 2 epochs are accepted but heavily dampened (α(2) = 1/√3 ≈ 0.577).

### DP Non-Claim Boundary

- ε = 95.97 is a **high privacy budget**; the architecture does not claim strong individual-level DP protection. The DP guarantee is included for structural boundedness and legal compliance alignment (GDPR Art. 25, DPDP §4), not as a claim of high-strength statistical indistinguishability.
- **Linear composition** is used (not advanced composition or Rényi DP); actual privacy loss may be lower under tighter accounting. This is a deliberately conservative upper bound.
- Gradient inversion attacks (Zhu et al. 2019) are **mitigated but not provably eliminated** at σ = 0.5.
- The DP guarantee applies to the **federation aggregation channel only** — not to local on-device inference, which operates on anonymous skeletons (INV-02, INV-10).
- No composition limit is enforced beyond cumulative tracking; the system does not automatically halt at a budget threshold.

---

## Document Control

| Property | Value |
|----------|-------|
| Version | 2.3.0 |
| Status | LOCKED |
| Generated | 2026-02-12 |
| Authority | ARCHITECTURE_CANONICAL.md v1.0.0 |
| Companion | CANONICAL_GLOSSARY.md v1.0.0 |
| Alignment | Paper 17, Paper 18 |
| Invariant Count | 15 (INV-01 through INV-15) |
| Supplementary Sections | 6 (Fail-State Taxonomy, Non-Persistence Boundary, Temporal Safety Property, Trace Matrix, TCB, DP Boundary) |
| Modification Authority | Human governance only |
