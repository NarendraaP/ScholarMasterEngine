# LICENSING AND USAGE RESTRICTIONS

**Document Type**: Usage License / Governance Contract  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Companion**: PRODUCT_BOUNDARY_AND_NON_NEGOTIABLES.md  
**Status**: BINDING  
**Version**: 1.0.0

---

## SECTION 1 — LICENSE GRANT (LIMITED, CONDITIONAL)

### 1.1 Grant Type
ScholarMasterEngine is licensed under the following terms:

| Term | Definition |
|------|------------|
| **Non-Exclusive** | Multiple institutions may hold concurrent licenses. |
| **Non-Transferable** | License may not be sold, assigned, or sublicensed. |
| **Institution-Bound** | License is valid for the named institution only. |
| **Deployment-Bound** | License is valid for the registered hardware only. |

### 1.2 Conditional Validity
The license is valid **IF AND ONLY IF**:
- All architectural invariants (L1–L8) are preserved.
- `PRODUCT_BOUNDARY_AND_NON_NEGOTIABLES.md` is not violated.
- `DEPLOYMENT_CONTRACT.md` preconditions are satisfied.

### 1.3 Automatic Voiding
License is **AUTOMATICALLY VOID** if:
- Any invariant is bypassed, weakened, or removed.
- System is modified to enable prohibited uses.
- Architectural enforcement mechanisms are disabled.

---

## SECTION 2 — PERMITTED USES

The following uses are permitted under this license:

| Use Case | Description | Enforcing Layers |
|----------|-------------|------------------|
| **Academic Campuses** | Deployment within accredited educational institutions. | L1–L8 |
| **Educational Compliance** | Attendance, truancy detection, schedule adherence. | L4 (Inference), L5 (Governance) |
| **Safety Assistance** | Anomaly detection (distress, medical emergency indicators). | L4, L5, L6 |
| **Engagement Analytics** | Aggregate engagement scoring (pose-based, non-identifying). | L3, L4 |
| **Ethics-Approved Research** | Studies conducted under IRB/Ethics Board supervision. | L5 (Consent), L7 (Audit) |
| **Federation Participation** | DP gradient sharing with consented partner institutions. | L8 (Federation) |

### 2.1 Permitted Use Constraints
Each permitted use:
- MUST operate within skeleton-only output constraints (L6).
- MUST pass L5 governance approval for any human-visible output.
- MUST respect individual and institutional consent (L5).

---

## SECTION 3 — PROHIBITED USES (STRICT)

The following uses are **STRICTLY PROHIBITED**. These prohibitions are not policy preferences; they are **architectural impossibilities** enforced at runtime.

### 3.1 Surveillance or Policing

| Prohibition | Surveillance deployment for security/law enforcement. |
|-------------|-----------------------------------------------------|
| **Ethical Reason** | Violates privacy and dignity of monitored individuals. |
| **Architectural Reason** | System destroys identifying data (L3). No video storage. |
| **System Behavior** | Request for RGB output → BLOCKED. Request for historical footage → FAIL (data does not exist). |

### 3.2 Identity Tracking

| Prohibition | Continuous tracking of individual movement or behavior. |
|-------------|--------------------------------------------------------|
| **Ethical Reason** | Enables profiling and discrimination. |
| **Architectural Reason** | L3 outputs are non-invertible. No identity reconstruction. |
| **System Behavior** | Request for trajectory → FAIL (skeletons are session-ephemeral). |

### 3.3 Behavioral Profiling for Punishment

| Prohibition | Using engagement/behavior data for disciplinary action. |
|-------------|--------------------------------------------------------|
| **Ethical Reason** | Coerces behavior through fear, not education. |
| **Architectural Reason** | L5 governance blocks punitive escalation paths. |
| **System Behavior** | Punitive alert category → ESCALATE (requires human review, not automation). |

### 3.4 Commercial Data Extraction

| Prohibition | Monetizing anonymized or aggregate data. |
|-------------|------------------------------------------|
| **Ethical Reason** | Violates trust of monitored individuals. |
| **Architectural Reason** | No export path for raw or processed data to external systems. |
| **System Behavior** | Data export API → DOES NOT EXIST. |

### 3.5 Cloud-Hosted Data Aggregation

| Prohibition | Uploading any data to vendor or third-party cloud. |
|-------------|---------------------------------------------------|
| **Ethical Reason** | Destroys data sovereignty. |
| **Architectural Reason** | No cloud persistence module. Federation is DP-only. |
| **System Behavior** | Cloud API call → NETWORK REJECT. |

### 3.6 Law Enforcement Integration

| Prohibition | Sharing data with police, security agencies, or courts. |
|-------------|--------------------------------------------------------|
| **Ethical Reason** | Transforms educational tool into surveillance apparatus. |
| **Architectural Reason** | Data does not exist. Request is technically unful fillable. |
| **System Behavior** | Legal demand for footage → REFUSE (provide deletion certificate). |

### 3.7 Employment Monitoring

| Prohibition | Monitoring faculty/staff for performance evaluation. |
|-------------|-----------------------------------------------------|
| **Ethical Reason** | Violates employment rights and labor agreements. |
| **Architectural Reason** | System is student-focused. Staff enrollment is opt-in. |
| **System Behavior** | Non-consented staff in frame → SKELETON ONLY, no inference. |

---

## SECTION 4 — MODIFICATION & FORK RESTRICTIONS

### 4.1 Source Code Modification
Modification is permitted **ONLY IF**:
- All L1–L8 invariants remain intact.
- `GovernanceFilter`, `EdgeAbstraction`, and `PrivacyLEDController` are not weakened.
- Modifications are disclosed to original licensor.

### 4.2 Forking
Forks are permitted **ONLY IF**:
- Fork retains all safeguards.
- Fork does not enable prohibited uses.
- Fork is clearly marked as derivative.

### 4.3 Research Extensions
Extensions for research are permitted **ONLY IF**:
- Ethics approval is obtained.
- Extensions do not bypass L3 or L5.
- Results are not used for prohibited purposes.

### 4.4 Mandatory Disclosures
Any modification MUST:
- Document changes in `CHANGELOG.md`.
- Update `VERIFICATION_AND_AUDIT_READINESS.md` with new test coverage.
- Notify original licensor within 30 days.

### 4.5 Prohibited Modifications
The following modifications void the license:
- Removal of `FRAME_TTL_MS` or `AUDIO_TTL_SECONDS` enforcement.
- Bypass of `GovernanceFilter.process_inference_output()`.
- Disabling of `PrivacyLEDController` halt conditions.
- Addition of raw data persistence paths.

---

## SECTION 5 — OPERATOR & INSTITUTION RESPONSIBILITIES

### 5.1 Institution Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Consent Management** | Maintain consent registry. Process RTBF requests within 72 hours. |
| **Hardware Integrity** | Ensure Privacy LED is functional. Report hardware failures. |
| **Audit Cooperation** | Provide access to audit logs upon legitimate request. |
| **Incident Disclosure** | Report architectural violations within 24 hours. |

### 5.2 Operator Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Training** | Complete operator certification before deployment. |
| **Escalation Handling** | Respond to escalations within defined timeout. |
| **No Override Attempts** | Do not attempt to bypass governance. |
| **State Accuracy** | Ensure Privacy LED reflects actual system state. |

### 5.3 Governance Authority Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Policy Definition** | Define allowlist within permitted bounds. |
| **Escalation Review** | Review and decide on escalated events. |
| **Federation Consent** | Grant or revoke federation participation. |
| **Audit Review** | Periodically review governance decision logs. |

---

## SECTION 6 — AUTOMATIC TERMINATION CONDITIONS

License terminates **AUTOMATICALLY** and **IMMEDIATELY** upon:

| Condition | Detection | Consequence |
|-----------|-----------|-------------|
| **Governance Bypass Attempt** | Audit log anomaly | License VOID |
| **Privacy LED Tampering** | Hardware/software mismatch | License VOID |
| **Raw Data Persistence** | Storage audit | License VOID |
| **Federation Misuse** | Non-DP gradient detection | License VOID |
| **Capability Misrepresentation** | Third-party complaint | License VOID |
| **Prohibited Use Deployment** | Audit finding | License VOID |

### 6.1 Termination Properties
- **Automatic**: No human decision required.
- **Non-Negotiable**: Cannot be appealed or delayed.
- **Logged**: Termination event recorded in immutable audit.

### 6.2 Post-Termination Obligations
Upon termination:
- System MUST be decommissioned.
- All audit logs MUST be preserved for 7 years.
- Federation participation MUST be withdrawn.

---

## SECTION 7 — ALIGNMENT STATEMENT

> "This license aligns with privacy-by-architecture principles.
> No contractual clause overrides technical enforcement.
> The system refuses operation outside its defined scope.
> Violation of architectural invariants voids the license automatically."

---

## SECTION 8 — CONTRADICTION CHECK

All licensing terms in this document derive from:
- `ARCHITECTURE_CANONICAL.md` (v1.0.0)
- `PRODUCT_BOUNDARY_AND_NON_NEGOTIABLES.md`
- `DEPLOYMENT_CONTRACT.md`

**Verification Status**: No contradictions detected.  
**License Status**: VALID

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0  
**Status**: BINDING
