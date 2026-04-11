------------------------------ MODULE ScholarMaster_NI ------------------------------
(*
 * Dual-Trace Noninterference Specification for ScholarMaster
 * Paper 19 — Formal Threat Model & TCB Definition
 *
 * This spec verifies the hyperproperty of Noninterference by reducing
 * it to a safety property via dual-execution synchronization.
 *
 * Design:
 *   Two executions run in lockstep with shared scheduling.
 *   High-domain inputs (biometric identity) may differ between traces.
 *   Low-domain observables (metadata, disk) must remain identical.
 *
 * Formally:
 *   High_1 ≠ High_2  ⇒  Low_1 = Low_2
 *   (Under A0-A3 adversaries and intact TCB)
 *
 * Three modes:
 *   SafeSpec          — Identity-independent F_irreversible → NI PASS
 *   LeakySpec         — Identity-dependent processing → NI FAIL (metadata leak)
 *   AdversarialSpec   — Illegal disk write → NI FAIL (persistence leak)
 *)

EXTENDS Naturals, FiniteSets, TLC

CONSTANT N                        \* Number of concurrent frame slots
CONSTANT HighInputs               \* Set of possible biometric identity values
ASSUME N \in Nat /\ N > 0

Frames == 1..N
Delta == 3

\* --------------------------------------------------------------------------
\* Execution Trace 1 (may contain Student A's biometric)
\* --------------------------------------------------------------------------
VARIABLES raw1, metadata1, disk1, highInput1

\* --------------------------------------------------------------------------
\* Execution Trace 2 (may contain Student B's biometric)
\* --------------------------------------------------------------------------
VARIABLES raw2, metadata2, disk2, highInput2

\* --------------------------------------------------------------------------
\* Shared (must be identical across traces — Low-domain control)
\* --------------------------------------------------------------------------
VARIABLE governanceOK

vars == <<raw1, metadata1, disk1, highInput1,
          raw2, metadata2, disk2, highInput2,
          governanceOK>>

\* ==========================================================================
\* Initial State — Both traces start identically
\* ==========================================================================
Init ==
    /\ raw1 = {}
    /\ raw2 = {}
    /\ metadata1 = 0
    /\ metadata2 = 0
    /\ disk1 = {}
    /\ disk2 = {}
    /\ highInput1 = [f \in Frames |-> 0]
    /\ highInput2 = [f \in Frames |-> 0]
    /\ governanceOK = TRUE

\* ==========================================================================
\* Synchronized Actions — Both traces execute the SAME operation
\* High inputs (hi1, hi2) may differ — this is the NI test variable
\* ==========================================================================

(* CaptureSync: Both traces capture the same frame slot f,
   but with potentially different biometric content (hi1 vs hi2).
   This models: same camera, same time, but different student in view. *)
CaptureSync(f, hi1, hi2) ==
    /\ governanceOK = TRUE
    /\ f \notin raw1
    /\ f \notin raw2
    /\ raw1' = raw1 \cup {f}
    /\ raw2' = raw2 \cup {f}
    /\ highInput1' = [highInput1 EXCEPT ![f] = hi1]
    /\ highInput2' = [highInput2 EXCEPT ![f] = hi2]
    /\ UNCHANGED <<metadata1, metadata2, disk1, disk2, governanceOK>>

(* ProcessSafeSync: F_irreversible is IDENTITY-INDEPENDENT.
   Both traces increment metadata by 1 regardless of who is in the frame.
   This models correct privacy-preserving abstraction. *)
ProcessSafeSync(f) ==
    /\ f \in raw1
    /\ f \in raw2
    /\ metadata1' = metadata1 + 1    \* Independent of highInput1[f]
    /\ metadata2' = metadata2 + 1    \* Independent of highInput2[f]
    /\ UNCHANGED <<raw1, raw2, disk1, disk2, highInput1, highInput2, governanceOK>>

(* ProcessLeakySync: BROKEN abstraction — metadata depends on identity.
   This models a flawed F_irreversible that leaks biometric identity. *)
ProcessLeakySync(f) ==
    /\ f \in raw1
    /\ f \in raw2
    /\ metadata1' = metadata1 + highInput1[f]  \* LEAKS identity
    /\ metadata2' = metadata2 + highInput2[f]  \* LEAKS identity
    /\ UNCHANGED <<raw1, raw2, disk1, disk2, highInput1, highInput2, governanceOK>>

(* ZeroizeSync: Both traces zeroize the same frame. *)
ZeroizeSync(f) ==
    /\ f \in raw1
    /\ f \in raw2
    /\ raw1' = raw1 \ {f}
    /\ raw2' = raw2 \ {f}
    /\ UNCHANGED <<metadata1, metadata2, disk1, disk2, highInput1, highInput2, governanceOK>>

(* GovernanceFailSync: Both traces fail governance simultaneously.
   Emergency zeroize on both sides. *)
GovernanceFailSync ==
    /\ governanceOK = TRUE
    /\ governanceOK' = FALSE
    /\ raw1' = {}
    /\ raw2' = {}
    /\ UNCHANGED <<metadata1, metadata2, disk1, disk2, highInput1, highInput2>>

\* ==========================================================================
\* Adversarial Actions (asymmetric — only one trace affected)
\* ==========================================================================

(* Illegal disk write on trace 1 only — breaks Low equivalence *)
IllegalDiskWrite1(f) ==
    /\ f \in raw1
    /\ disk1' = disk1 \cup {f}
    /\ UNCHANGED <<raw1, raw2, metadata1, metadata2, disk2, highInput1, highInput2, governanceOK>>

\* ==========================================================================
\* Behavioral Specifications
\* ==========================================================================

SafeNext ==
    \/ \E f \in Frames : \E hi1, hi2 \in HighInputs : CaptureSync(f, hi1, hi2)
    \/ \E f \in Frames : ProcessSafeSync(f)
    \/ \E f \in Frames : ZeroizeSync(f)
    \/ GovernanceFailSync

LeakyNext ==
    \/ \E f \in Frames : \E hi1, hi2 \in HighInputs : CaptureSync(f, hi1, hi2)
    \/ \E f \in Frames : ProcessLeakySync(f)
    \/ \E f \in Frames : ZeroizeSync(f)
    \/ GovernanceFailSync

AdversarialNext ==
    \/ SafeNext
    \/ \E f \in Frames : IllegalDiskWrite1(f)

SafeSpec == Init /\ [][SafeNext]_vars
LeakySpec == Init /\ [][LeakyNext]_vars
AdversarialSpec == Init /\ [][AdversarialNext]_vars

\* ==========================================================================
\* Noninterference Property
\* ==========================================================================

(* Low-domain equivalence: metadata and disk must be identical *)
LowEquivalent ==
    /\ metadata1 = metadata2
    /\ disk1 = disk2

(* High-domain: raw content may legitimately differ *)
HighMayDiffer ==
    \/ highInput1 /= highInput2

(* The core NI property: regardless of High differences, Low stays equal *)
NonInterference ==
    LowEquivalent

=============================================================================
\* Modification History
\* Created 2026-02-19 — Dual-Trace Noninterference Verification
\* ScholarMaster Research Series
=============================================================================
