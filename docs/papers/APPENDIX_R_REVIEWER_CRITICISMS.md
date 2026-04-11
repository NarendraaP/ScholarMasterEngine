# Appendix R — Anticipated Reviewer Criticisms and Formal Responses

---

## R1. CPython Allocator Behavior and Memory Zeroization

### Anticipated Criticism

> *"del does not zero memory. CPython may retain freed objects in allocator pools. Therefore, raw data may remain recoverable in RAM."*

### Formal Response

**Correct.**

The system does not claim hardware-level zeroization.

The invariant (**INV-01**) guarantees:

- Removal of all live Python-level references
- Bounded lifetime ≤ 33 ms (frame) / 3 s (audio)
- Structural destruction via `finally` block

It **does not** claim:

- Immediate overwriting of freed memory pages
- Protection against cold-boot DRAM extraction
- Resistance to privileged kernel-level memory scraping

This is explicitly bounded in:

- **INV-01 Non-Claim Boundary**
- **TCB Declaration** (RAM volatility assumption)

### Architectural Position

The security model is:

> **Reference non-persistence + volatility assumption**

Not:

> Cryptographic memory erasure

This distinction is intentional and documented.

---

## R2. High Differential Privacy Budget (ε ≈ 95.97)

### Anticipated Criticism

> *"An ε of 95.97 is extremely high. This does not represent strong individual-level DP protection."*

### Formal Response

**Correct.**

The DP guarantee is:

> **(95.97, 10⁻⁵)-DP** under linear composition for 10 rounds.

This is:

- A **structural upper bound**
- A **legally bounded privacy envelope**
- **Not** a claim of strong indistinguishability

The architecture explicitly states:

- DP applies to **federation channel only**
- Skeleton inference path is separate (INV-02, INV-10)
- No claim of "strong DP" or "privacy-preserving ML" beyond the formal bound

The DP boundary section explicitly classifies this as:

> **Structural boundedness**, not maximal statistical privacy.

---

## R3. Structural vs Runtime Invariants

### Anticipated Criticism

> *"Some invariants are not enforced at runtime but by code structure. This is weaker."*

### Formal Response

Invariants are intentionally split into:

| Category | Enforcement Mechanism |
|---|---|
| **Runtime-Enforced** | Watchdog, health checks, TTL daemons, GovernanceFilter |
| **Structural (Governance)** | Code architecture, type system, module boundaries |

Structural invariants (INV-03, INV-04, INV-07, INV-14) cannot be violated without **source modification**.

The threat model explicitly **excludes**:

- Malicious developer with repository write access
- Compromised CI pipeline
- Modified interpreter or kernel

Those are **governance-level risks**, not runtime risks.

This separation is **deliberate and transparent**.

---

## R4. Lack of Secure Boot / Measured Boot

### Anticipated Criticism

> *"Boot chain integrity is assumed but not enforced. A compromised kernel could violate invariants."*

### Formal Response

**Correct.**

The architecture does **not** implement:

- Secure Boot
- TPM attestation
- Measured boot
- Binary signing enforcement

Boot integrity is declared as a **TCB assumption**, not a guarantee.

The system's guarantees hold:

> **If and only if** the TCB assumptions are valid.

This boundary is explicitly documented to prevent overclaiming.

---

## R5. No Hardware-Level Memory Zeroization

### Anticipated Criticism

> *"There is no `memset_s`, `mlock`, or hardware-backed memory scrub."*

### Formal Response

**Correct.**

The architecture relies on:

- Bounded lifetime
- Reference destruction
- Volatile-only storage
- Optional deployment hardening (`mlock`, `CAP_IPC_LOCK`, swap disabled)

Zeroization is **not** implemented because:

- It requires C-level extensions
- It is platform-dependent
- It exceeds the defined software threat model

This is declared in:

- **INV-01 Non-Claim**
- **INV-09 Non-Claim**
- **OS Hardening Section**

---

## R6. Gradient Inversion Risk in Federated Learning

### Anticipated Criticism

> *"σ = 0.5 may not eliminate gradient inversion attacks."*

### Formal Response

**Correct.**

The DP mechanism:

- Clips gradients at $C = 1.0$
- Adds Gaussian noise ($\sigma = 0.5$)
- Tracks $\varepsilon$ cumulatively

It **mitigates** but does **not prove elimination** of inversion attacks.

This is explicitly acknowledged in:

> **DP Non-Claim Boundary.**

The system does not market itself as inversion-proof.

---

## R7. 34-Keypoint Non-Reconstructability Claim

### Anticipated Criticism

> *"34 keypoints do not mathematically prove identity irrecoverability."*

### Formal Response

**Correct.**

The claim is:

- **Structural underdetermination**
- **Information-theoretic compression bound**
- **Absence of auxiliary channels**

It is **not**:

- A formal impossibility proof under all priors
- A cryptographic guarantee

The non-reconstructability claim requires **three simultaneous conditions**:

| # | Condition | Invariant |
|---|---|---|
| 1 | Density constraint | INV-10 |
| 2 | Raw destruction | INV-01 |
| 3 | No side channel | INV-04 |

Violation of **any** condition weakens the claim — which is documented.

---

## R8. Allowlist Governance May Be Over-Permissive

### Anticipated Criticism

> *"The allowlist could include fields that are privacy-sensitive."*

### Formal Response

**Correct.**

The invariant guarantees:

- Unknown fields are **rejected**
- Filtering is **complement-of-allowlist only**

It does **not** guarantee:

- That the allowlist is **minimal**

This is a **governance review responsibility**, not a runtime guarantee.

---

## Meta-Position

This appendix exists to prevent:

- Overclaim interpretation
- Misaligned threat model assumptions
- Reviewer speculation about unstated guarantees

The architecture makes **bounded claims**. It does **not** claim:

| ✗ Non-Claim |
|---|
| Absolute security |
| Perfect DP |
| Hardware zeroization |
| Secure boot |
| Immunity to malicious maintainers |

It **does** claim:

| ✓ Bounded Claim |
|---|
| Structural irreversibility |
| Bounded memory lifetime |
| Allowlist governance |
| Fail-closed enforcement |
| Transparent TCB declaration |
