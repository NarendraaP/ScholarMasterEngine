# OPERATOR MANUAL

**Document Type**: Operational Procedures  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0 (IMMUTABLE)  
**Companion**: DEPLOYMENT_CONTRACT.md, FAILURE_INCIDENT_PLAYBOOKS.md  
**Status**: BINDING  
**Version**: 1.0.0

---

## SECTION A — OPERATOR ROLE DEFINITION

### A.1 Operator Authority

| Authority | Scope |
|-----------|-------|
| **Monitor** | View system health, skeleton outputs, aggregate metrics. |
| **Acknowledge** | Respond to escalations, confirm alerts. |
| **Configure** | Adjust alert thresholds within governance bounds. |
| **Report** | Flag incidents, request audits. |

### A.2 Operator Limitations

| Limitation | Enforcement |
|------------|-------------|
| **Cannot access raw data** | Data does not exist (L3 destroys). |
| **Cannot bypass governance** | `GovernanceFilter` is mandatory. |
| **Cannot disable LED** | `PrivacyLEDController` halts on failure. |
| **Cannot modify allowlist** | Requires Governance Authority role. |
| **Cannot export data** | No export API exists. |

### A.3 Explicit Limits of Authority
Operators are authorized to:
- Observe skeleton-only visualizations.
- Acknowledge escalated events.
- Respond within defined timeout windows.

Operators are **NOT authorized** to:
- Access, view, or export any raw sensor data.
- Modify system configuration beyond thresholds.
- Override governance decisions.
- Continue operation after invariant failure.

---

## SECTION B — NORMAL OPERATIONS

### B.1 Monitoring System State

| Metric | Location | Interpretation |
|--------|----------|----------------|
| **System Mode** | Dashboard header | ACTIVE, PRIVACY_ONLY, DEGRADED, HALTED |
| **LED State** | Physical indicator / Dashboard | GREEN = Privacy, RED = Active |
| **Watchdog** | Health panel | ACTIVE = OK, INACTIVE = HALT required |
| **Governance Queue** | Alert panel | Pending escalations |

### B.2 Acknowledging Alerts
When an alert escalates to operator:
1. View alert details (skeleton + event type).
2. Assess context (zone, time, classification).
3. Select action: APPROVE, DROP, or ESCALATE_FURTHER.
4. Confirm decision. Decision is logged.

### B.3 Viewing Skeleton-Only Outputs
Operators view:
- Skeleton overlays (≤34 keypoints per body).
- Zone occupancy counts.
- Engagement scores (aggregate).
- Compliance indicators (binary).

Operators **NEVER** view:
- RGB video frames.
- Facial images.
- Audio waveforms.
- Individual identity information.

### B.4 Responding to Escalations
Escalations require operator response within timeout:
- **Default timeout**: 60 seconds.
- **Timeout action**: System defaults to DROP.
- **Escalation logged**: Decision or timeout recorded.

---

## SECTION C — PRIVACY & TRUST INDICATORS

### C.1 Privacy LED States

| LED Color | State | Meaning |
|-----------|-------|---------|
| **GREEN** | PRIVACY | System processing, no identification. |
| **RED** | ACTIVE | System processing with identity lookup. |
| **OFF** | OFF | System halted or powered down. |
| **UNKNOWN** | UNKNOWN | System HALTS (invalid state). |

### C.2 LED Guarantees
- LED state **always reflects** actual system mode.
- LED **cannot be silenced** without system HALT.
- LED **must be visible** to occupants of monitored space.

### C.3 Skeleton Display Guarantees
- All human-visible outputs are **skeleton-only**.
- No RGB pixels are ever displayed.
- Skeletons are **non-identifying**.

### C.4 What Operators Should NEVER See
If an operator sees any of the following, **report immediately**:
- Facial images.
- RGB video.
- Student names (unhashed).
- Audio waveforms.
- Location trajectories.

Seeing any of these indicates a **critical system failure**.

---

## SECTION D — FAILURE RESPONSE (REFERENCE-ONLY)

### D.1 Automatic System Responses
The system responds to failures automatically:

| Failure | Automatic Response |
|---------|-------------------|
| Camera failure | Enter PRIVACY_ONLY mode |
| Network failure | Buffer locally, no backlog replay |
| Governance failure | Block L6 output |
| LED failure | HALT immediately |
| Watchdog failure | HALT immediately |

### D.2 Required Operator Acknowledgments

| Event | Required Action |
|-------|-----------------|
| Recovery from PRIVACY_ONLY | Acknowledge before ACTIVE |
| System restart | Acknowledge initial state |
| Escalation timeout | Review decision log |

### D.3 What Operators Must NOT Attempt

| Forbidden Action | Reason |
|------------------|--------|
| Force restart to clear alerts | Violates audit integrity |
| Disable watchdog | Violates irreversibility |
| Modify LED behavior | Violates trust indicator |
| Continue after HALT | Violates safety protocol |

---

## SECTION E — FORBIDDEN OPERATOR ACTIONS

The following actions are **FORBIDDEN**. Attempting them may trigger automatic license termination.

| # | Forbidden Action | Consequence |
|---|------------------|-------------|
| 1 | **Attempting to access raw data** | Data does not exist. Attempt logged as violation. |
| 2 | **Bypassing governance** | Attempt blocked. Logged as security incident. |
| 3 | **Silencing indicators** | LED controller halts system. |
| 4 | **Restarting to clear logs** | Logs are append-only. Restart does not clear. |
| 5 | **Continuing after invariant failure** | System refuses to operate. |
| 6 | **Sharing operator credentials** | Logged actions attributed incorrectly. |
| 7 | **Ignoring escalations** | Timeout logged. Repeated timeouts flagged. |
| 8 | **Modifying configuration without authority** | Configuration locked. Requires Governance Authority. |

---

## SECTION F — AUDIT & ACCOUNTABILITY

### F.1 Logged Operator Actions

| Action | Logged Data |
|--------|-------------|
| Login | Timestamp, operator ID |
| Alert acknowledgment | Decision, timestamp, alert ID |
| Escalation response | Decision, reasoning (if provided), timestamp |
| Configuration change | Parameter, old value, new value, timestamp |
| System mode transition | Acknowledgment, timestamp |

### F.2 Audit Process
- **Periodic review**: Institution reviews governance logs quarterly.
- **Incident review**: Triggered by anomaly detection or complaint.
- **External audit**: Ethics board or funding agency request.

### F.3 Operator Responsibility Boundaries

| Operator is responsible for | Operator is NOT responsible for |
|-----------------------------|--------------------------------|
| Timely escalation response | System architectural guarantees |
| Accurate decision recording | Hardware failure |
| Reporting anomalies | Governance policy definition |
| Maintaining credentials | Federation coordination |

### F.4 Accountability Limits
Operators are accountable for:
- Their logged decisions.
- Timeouts on their watch.
- Reported vs. unreported anomalies.

Operators are NOT accountable for:
- Architectural enforcement (system responsibility).
- Data the system does not provide.
- Actions taken by system automatically.

---

**Document Version**: 1.0.0  
**Generated**: 2026-02-07  
**Authority**: ARCHITECTURE_CANONICAL.md v1.0.0  
**Status**: BINDING
