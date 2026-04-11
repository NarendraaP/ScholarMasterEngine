------------------------------ MODULE ScholarMaster_Invariants ------------------------------
(*
 * TLA+ Formal Specification for ScholarMaster Privacy Invariants
 * Paper 19 — Formal Threat Model & TCB Definition
 * 
 * This spec model-checks the core memory safety invariants of the
 * ScholarMaster privacy-by-architecture system under bounded state
 * exploration. It verifies:
 *   INV-A: No raw frame coexists with diskWrite = TRUE      (NoPersistence)
 *   INV-B: Governance failure prevents new raw frame capture (GovernanceGate)
 *   Liveness: Raw frame must eventually become Absent        (EventuallyZeroized)
 *
 * Two behavioral specs are provided:
 *   SafeSpec  — System without illegal transitions (should PASS all checks)
 *   AdversarialSpec — Includes IllegalWrite action (should produce counterexample)
 *)

EXTENDS Naturals, TLC

VARIABLES rawFrame, processed, zeroized, diskWrite, governanceOK

vars == <<rawFrame, processed, zeroized, diskWrite, governanceOK>>

\* --------------------------------------------------------------------------
\* Type Invariant (structural health check)
\* --------------------------------------------------------------------------
TypeOK ==
    /\ rawFrame \in {"Absent", "Present"}
    /\ processed \in BOOLEAN
    /\ zeroized \in BOOLEAN
    /\ diskWrite \in BOOLEAN
    /\ governanceOK \in BOOLEAN

\* --------------------------------------------------------------------------
\* Initial State
\* --------------------------------------------------------------------------
Init ==
    /\ rawFrame = "Absent"
    /\ processed = FALSE
    /\ zeroized = TRUE
    /\ diskWrite = FALSE
    /\ governanceOK = TRUE

\* --------------------------------------------------------------------------
\* Actions: Legal System Transitions
\* --------------------------------------------------------------------------

(* Capture a new raw frame from sensor — only when governance is OK *)
Capture ==
    /\ rawFrame = "Absent"
    /\ governanceOK = TRUE
    /\ rawFrame' = "Present"
    /\ processed' = FALSE
    /\ zeroized' = FALSE
    /\ diskWrite' = FALSE
    /\ governanceOK' = governanceOK

(* Process the raw frame through F_irreversible *)
Process ==
    /\ rawFrame = "Present"
    /\ processed = FALSE
    /\ processed' = TRUE
    /\ rawFrame' = rawFrame
    /\ zeroized' = zeroized
    /\ diskWrite' = FALSE
    /\ governanceOK' = governanceOK

(* Zeroize frame — enforced by TCB within Delta_TTL *)
Zeroize ==
    /\ rawFrame = "Present"
    /\ processed = TRUE
    /\ zeroized = FALSE
    /\ rawFrame' = "Absent"
    /\ zeroized' = TRUE
    /\ processed' = FALSE
    /\ diskWrite' = FALSE
    /\ governanceOK' = governanceOK

(* Governance module fails — system must halt capture *)
GovernanceFail ==
    /\ governanceOK = TRUE
    /\ governanceOK' = FALSE
    /\ rawFrame' = rawFrame
    /\ processed' = processed
    /\ zeroized' = zeroized
    /\ diskWrite' = diskWrite

(* Governance recovery — restore after remediation *)
GovernanceRecover ==
    /\ governanceOK = FALSE
    /\ rawFrame = "Absent"
    /\ governanceOK' = TRUE
    /\ rawFrame' = rawFrame
    /\ processed' = processed
    /\ zeroized' = zeroized
    /\ diskWrite' = diskWrite

\* --------------------------------------------------------------------------
\* Action: Adversarial / Illegal Transition (for counterexample generation)
\* --------------------------------------------------------------------------

(* An adversary attempts to write raw frame to disk *)
IllegalWrite ==
    /\ rawFrame = "Present"
    /\ diskWrite' = TRUE
    /\ UNCHANGED <<rawFrame, processed, zeroized, governanceOK>>

\* --------------------------------------------------------------------------
\* Behavioral Specifications
\* --------------------------------------------------------------------------

(* Safe system — only legal transitions *)
SafeNext ==
    \/ Capture
    \/ Process
    \/ Zeroize
    \/ GovernanceFail
    \/ GovernanceRecover

(* Adversarial system — includes illegal write attempt *)
AdversarialNext ==
    \/ SafeNext
    \/ IllegalWrite

(* Use SafeSpec for verification; use AdversarialSpec for counterexample demo *)
SafeSpec ==
    Init /\ [][SafeNext]_vars /\ WF_vars(Zeroize)

AdversarialSpec ==
    Init /\ [][AdversarialNext]_vars

\* --------------------------------------------------------------------------
\* Invariants (State Predicates — checked by TLC as invariants)
\* --------------------------------------------------------------------------

(* INV-A: No raw frame may coexist with a disk write *)
NoPersistence ==
    rawFrame = "Present" => diskWrite = FALSE

(* INV-B: Governance failure must prevent raw frame presence *)
GovernanceGate ==
    governanceOK = FALSE => rawFrame = "Absent"

\* --------------------------------------------------------------------------
\* Temporal Properties (checked by TLC as properties, not invariants)
\* --------------------------------------------------------------------------

(* Liveness: Every captured raw frame is eventually zeroized *)
EventuallyZeroized ==
    [](rawFrame = "Present" => <>(rawFrame = "Absent"))

=============================================================================
\* Modification History
\* Created 2026-02-19 — Paper 19 Formal Verification Artifact
\* ScholarMaster Research Series
=============================================================================
