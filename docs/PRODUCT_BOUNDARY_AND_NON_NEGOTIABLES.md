# PRODUCT BOUNDARY AND NON-NEGOTIABLES

**Document Type**: Product Definition / Contractual Boundary  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Status**: BINDING  
**Scope**: ScholarMasterEngine System Identity  
**Version**: 1.0.0

---

## SECTION 1 — PRODUCT DEFINITION (POSITIVE SCOPE)

### 1.1 Deployment Model
ScholarMasterEngine is a **privately deployed, edge-isolated institutional system**.
- **Installation**: On-premise hardware owned by the Institution.
- **Connectivity**: Local Campus Intranet (primary), Federation (optional, outbound-only).
- **Updates**: Cryptographically signed firmware packages; no auto-update from cloud.

### 1.2 Ownership Model
- **Hardware**: Institution.
- **Data**: Institution (Audit Logs), Ephemeral (Memory).
- **Identity Registry**: Institution (Hashed).
- **Model Weights**: Shared Federation (if participating).
- **Vendor Access**: **NONE**. The vendor retains no rights to access, view, or monetize system data.

### 1.3 Control Model
- **Operator**: Designated Institutional Staff (via L5 Governance).
- **Administrator**: Institutional IT (Hardware/Network).
- **Subject**: Student/Faculty (via Consent & RTBF).
- **Automated Steward**: L5 Governance Filter (enforces invariant rules).

### 1.4 Data Locality Model
- **Raw Sensor Data**: **Volatile Memory ONLY** (L1/L2). Destroyed within milliseconds.
- **Inference Metadata**: Local Encrypted Storage (L7).
- **Federation Contributions**: **Differential Privacy Gradients ONLY** (L8).
- **Cloud Storage**: **NONE**. System has no cloud persistence layer.

---

## SECTION 2 — NON-NEGOTIABLE ARCHITECTURAL INVARIANTS

The following invariants are **architecturally enforced** and cannot be altered by configuration, policy, or operator command.

| Invariant | Source | Enforcement Mechanism | Violation Consequence |
|-----------|--------|-----------------------|-----------------------|
| **Irreversible L3 Boundary** | P3, P6 | `EdgeAbstraction` destruction watchdog | **IMMEDIATE HALT** |
| **Mandatory L5 Governance** | P4, P8 | `GovernanceFilter` mandatory pipeline gate | **DROP PACKET** |
| **Skeleton-Only Output** | P15, P16 | `L6Output` structural type constraint | **BLOCK RENDER** |
| **DP-Only Federation** | P12, P14 | `DPFederationCoordinator` type check | **REFUSE TRANSMIT** |
| **Fail-Safe Privacy** | Arch 7.0 | `FailSafeController` default-deny logic | **HALT PROCESSING** |
| **No Raw Persistence** | P3, P10 | Volatile memory isolation verification | **SYSTEM CRASH** |
| **No Cloud Centralization** | P12 | Absence of cloud upload modules | **NETWORK ERROR** |

---

## SECTION 3 — EXPLICIT PRODUCT REFUSALS

ScholarMasterEngine explicitly **REFUSES** to perform the following functions. These are not "unsupported features"; they are **anti-features** explicitly blocked by architecture.

### 3.1 Facial Recognition for Surveillance
- **Refusal**: The system WILL NOT identify individuals from static images or video feeds for security/surveillance purposes.
- **Enforcement**: Ingestion pipeline rejects non-live streams. Identification logic requires L3 skeleton/embedding transformation which destroys visual likeness.
- **Guarantee**: Identity Reconstruction is mathematically impossible from L3 artifacts.

### 3.2 Raw Video/Audio Storage
- **Refusal**: The system WILL NOT record, buffer to disk, or export raw camera or microphone data.
- **Enforcement**: `EdgeAbstraction` enforces <33ms TTL for frames and <3s for audio. No write access to persistent storage for these data types.
- **Guarantee**: "Replay" of events is impossible because the data does not exist.

### 3.3 Emergency Privacy Downgrade
- **Refusal**: The system WILL NOT carry a "Break Glass" or "Emergency Mode" that disables privacy filters.
- **Enforcement**: Compiling a version without L5/L3 enforcement requires distinct cryptographic signing keys not present on deployment hardware.
- **Guarantee**: Privacy invariants hold even during crisis, active shooter, or medical emergency scenarios.

### 3.4 Cloud-Hosted Analytics
- **Refusal**: The system WILL NOT upload metadata to a vendor-controlled cloud for "value-add" analytics.
- **Enforcement**: Outbound network traffic is restricted to Federation Protocol (DP Gradients) only.
- **Guarantee**: Institution retains absolute data sovereignty.

### 3.5 Silent Monitoring
- **Refusal**: The system WILL NOT operate in a "Stealth Mode" where processing occurs without indicators.
- **Enforcement**: `PrivacyLEDController` halts system if LED state is OFF or UNKNOWN.
- **Guarantee**: If the system is watching, the LED is ON (Green/Red).

### 3.6 Vendor Access to Data
- **Refusal**: The vendor WILL NOT have a "backdoor", research access, or support login to view live data.
- **Enforcement**: No remote shell or debug ports exposed on production interface.
- **Guarantee**: Defining "Support" as "Access" is contractually and technically prohibited.

---

## SECTION 4 — SUPPORTED VARIABILITY (SAFE CONFIGURATION)

The following aspects MAY vary per deployment without violating invariants.

| Configurable Aspect | Scope of Variability | Constraints |
|---------------------|----------------------|-------------|
| **Campus Policies** | Allowlist items (e.g., "Phone Use" vs "Sleep") | Must be within `ALLOWED_FIELDS` enum |
| **Alert Thresholds** | Sensitivity (e.g., Duration for "Truancy") | Cannot bypass L5 |
| **Operator Roles** | Who receives escalations | Must be authenticated users |
| **UI Language** | Localization strings | No semantic change |
| **Deployment Scale** | Number of nodes | Must verify hardware isolation |
| **Federation Partner**| Which coordinator to join | Must support DP protocol |

**Explicit Statement**: Changing these configurations DOES NOT and CANNOT weaken privacy, governance, or irreversibility guarantees.

---

## SECTION 5 — PRODUCT IDENTITY STATEMENT

> "ScholarMasterEngine is **NOT** a surveillance product.
> It is **NOT** an analytics SaaS.
> It **IS** a privacy-by-architecture institutional system
> whose guarantees are **enforced at runtime** and **cannot be disabled**."

---

## SECTION 6 — BOUNDARY JUSTIFICATION

All boundaries defined herein are direct consequences of `ARCHITECTURE_CANONICAL.md`:
- **Refusals** are negative constraints derived from positive architectural invariants.
- **Non-Negotiables** are structural properties of the L1-L8 layer model.
- **Variability** is limited to parameters exposed by the Governance Layer (L5).

**Verification**:
- `tests/test_layer_contracts.py`: Verifies L3/L5 boundaries.
- `tests/test_governance_filter.py`: Verifies configuration safety.
- `tests/test_audit_deficiencies.py`: Verifies LED and compression refusal constants.

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0  
**Status**: VALID
