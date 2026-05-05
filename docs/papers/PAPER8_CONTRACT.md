# PAPER 8 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | A Cryptographic Provenance Model with Erasure-Compatible Immutability |
| **Paper ID** | P8 |
| **Layer** | Trust (L7 — Audit & Provenance) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Corrected (CC v3.0 aligned) |

## 2. Primary Contribution

**A Cryptographic Provenance Layer (CPL) that separates attestation from disclosure via a dual-layer model: encrypted payloads remain off-chain while batched Merkle roots are committed to a permissioned ledger. Erasure-Compatible Immutability is achieved through Per-Identity Symmetric Key (PISK) cryptographic shredding.**

Paper 8 provides the trust substrate. It stores only hash commitments on-chain, never raw data.

## 3. Core Claims

| # | Claim | Evidence | CC Flag |
|---|---|---|---|
| C1 | Cryptographic hashes of events provide tamper-evident audit trails | Merkle-tree integrity verification (§IV) | Clean |
| C2 | Immutability is achieved within the bounds of the chosen ledger implementation | Append-only ledger design (§III) | Clean — hedged; not claiming absolute immutability |
| C3 | GDPR Right-to-Erasure is supported via cryptographic shredding (key destruction) | Erasure protocol (§V) | Clean — "GDPR-aligned technical controls," not "GDPR-compliant" |
| C4 | Asynchronous ledger writes decouple audit latency (~350 ms) from real-time admission decisions (~28 ms) | Architecture (§III) | Clean |

## 4. Scope

### 4.1 In-Scope
- Immutable append-only ledger design
- Merkle-tree integrity verification
- Cryptographic shredding for erasure support
- Asynchronous write buffering (decoupled from real-time path)
- Bounded buffer for network partition tolerance
- Consensus re-synchronization protocol

### 4.2 Out-of-Scope
- New blockchain protocol design (uses existing primitives)
- Biometric data storage (only hashes are stored)
- Privacy enforcement at sensing layer (Paper 3)
- Real-time admission decisions (Paper 1, Paper 4)
- Formal legal compliance certification

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P8-INV-01 | Only cryptographic hashes and metadata SHALL be stored in the ledger — never raw biometric data | Hash-only write path; no raw data serializer |
| P8-INV-02 | Ledger writes MUST NOT block the real-time admission path | Asynchronous write queue; admission path decoupled |
| P8-INV-03 | Buffered records during network partition MUST be cryptographically sealed and bounded | Fixed-size buffer (10K transactions); overflow sealed to local append-only storage |
| P8-INV-04 | Key destruction MUST render associated records unrecoverable for erasure requests | Cryptographic shredding protocol |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P1 (Identity) | Admission events to be logged |
| **Upstream** | P4 (Compliance) | Compliance decisions to be logged |
| **Upstream** | P6 (Acoustic) | Safety events to be logged |
| **Upstream** | P9 (Orchestrator) | All governance events routed through orchestrator |
| **Downstream** | P10 (Validation) | Trust layer validated under adversarial load |
| **Downstream** | P14 (Cross-Campus FL) | Campus audit logs for federated governance |

## 7. Verification Requirements

- Merkle-tree integrity check passes for all committed blocks
- Asynchronous write latency ≤ 500 ms under normal operation
- Buffer does not exceed 10K transactions during 5-minute network partition
- Cryptographic shredding renders target records unrecoverable
- Zero raw biometric data present in any ledger entry

## 8. What This Paper Does NOT Do

- Does **not** propose a new blockchain protocol
- Does **not** store raw biometric data or images
- Does **not** make real-time admission decisions (defers to Paper 1/4)
- Does **not** constitute formal legal compliance — provides "GDPR-aligned technical controls"

## 9. Verified Implementation Components (v2.4.0 Audit)

| Component | Source File | Status |
|---|---|---|
| **Immutable Ledger** | `modules_legacy/trust_layer.py` | ✅ Verified (SHA-256 Hash Chain) |
| **Tamper Detection** | `modules_legacy/trust_layer.py` | ✅ Verified (`verify_integrity` method) |
| **Genesis Block** | `modules_legacy/trust_layer.py` | ✅ Verified (Bootstrapping Logic) |

