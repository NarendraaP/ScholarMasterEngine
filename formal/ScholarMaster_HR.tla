------------------------------ MODULE ScholarMaster_HR ------------------------------
(*
 * Higher-Rigor TLA+ Formal Specification for ScholarMaster Privacy Invariants
 * Paper 19 — Formal Threat Model & TCB Definition
 * Paper 3  — Privacy-Preserving Pose Detection (Cross-Paper Interaction)
 *
 * This upgraded model introduces:
 *   - Concurrency:      Multiple simultaneous frames (N configurable)
 *   - Bounded time:     Watchdog enforces zeroization within Delta ticks
 *   - Domain separation: Explicit High/Low information flow tracking
 *   - Adversary model:  A0-A3 extraction attempts as separate actions
 *   - Fair scheduler:   WF constraints on Tick and Zeroize
 *
 * Verified Properties (under SafeSpec):
 *   NoPersistence      — No raw frame reaches persistent disk
 *   BoundedZeroization — Raw frame lifetime <= Delta ticks
 *   NoExtraction       — A0-A3 adversary cannot extract raw data
 *   GovernanceGate     — Governance failure halts capture & clears raw
 *   HighLowSeparation  — Raw frames exist only in High domain
 *   EventuallyZeroized — Every raw frame is eventually zeroized (liveness)
 *
 * Counterexample Generation (under AdversarialSpec):
 *   IllegalDiskWrite   — Demonstrates NoPersistence violation trace
 *   AttackerAttempt    — Demonstrates NoExtraction violation trace
 *)

EXTENDS Naturals, FiniteSets, TLC

CONSTANT N                        \* Number of concurrent frame slots
ASSUME N \in Nat /\ N > 0

Frames == 1..N
Domains == {"High", "Low"}
Delta == 3                        \* Watchdog TTL bound (in ticks)

VARIABLES raw,                    \* Set of frames in volatile raw state
          processed,              \* Set of frames that have been processed
          zeroized,               \* Set of frames that have been zeroized
          age,                    \* Function: Frame -> Nat (ticks since capture)
          domain,                 \* Function: Frame -> {"High", "Low"}
          disk,                   \* Set of frames written to persistent storage
          governanceOK,           \* Boolean: governance module operational
          attackerExtract         \* Set of frames adversary has extracted

vars == <<raw, processed, zeroized, age, domain, disk, governanceOK, attackerExtract>>

\* ==========================================================================
\* Type Invariant (structural health check)
\* ==========================================================================
TypeOK ==
    /\ raw \subseteq Frames
    /\ processed \subseteq Frames
    /\ zeroized \subseteq Frames
    /\ age \in [Frames -> Nat]
    /\ domain \in [Frames -> Domains]
    /\ disk \subseteq Frames
    /\ governanceOK \in BOOLEAN
    /\ attackerExtract \subseteq Frames

\* ==========================================================================
\* Initial State
\* ==========================================================================
Init ==
    /\ raw = {}
    /\ processed = {}
    /\ zeroized = Frames               \* All frame slots begin clean
    /\ age = [f \in Frames |-> 0]
    /\ domain = [f \in Frames |-> "Low"] \* No data captured yet
    /\ disk = {}
    /\ governanceOK = TRUE
    /\ attackerExtract = {}

\* ==========================================================================
\* Legal System Actions
\* ==========================================================================

(* Capture: Sensor ingests a new frame into volatile High domain.
   Guarded by governance — if governance is down, no new capture. *)
Capture(f) ==
    /\ governanceOK = TRUE
    /\ f \notin raw
    /\ f \in zeroized                    \* Only capture into a clean slot
    /\ raw' = raw \cup {f}
    /\ zeroized' = zeroized \ {f}
    /\ processed' = processed
    /\ age' = [age EXCEPT ![f] = 0]
    /\ domain' = [domain EXCEPT ![f] = "High"]  \* Frame enters High domain
    /\ UNCHANGED <<disk, governanceOK, attackerExtract>>

(* Process: F_irreversible transforms raw frame to semantic metadata.
   The raw buffer still exists until explicitly zeroized. *)
Process(f) ==
    /\ f \in raw
    /\ f \notin processed
    /\ processed' = processed \cup {f}
    /\ UNCHANGED <<raw, zeroized, age, domain, disk, governanceOK, attackerExtract>>

(* Zeroize: TCB destroys raw buffer after processing.
   Frame transitions from High to Low domain (only metadata remains). *)
Zeroize(f) ==
    /\ f \in raw
    /\ f \in processed                   \* Must be processed before zeroize
    /\ raw' = raw \ {f}
    /\ processed' = processed \ {f}
    /\ zeroized' = zeroized \cup {f}
    /\ domain' = [domain EXCEPT ![f] = "Low"]  \* Metadata moves to Low
    /\ age' = [age EXCEPT ![f] = 0]
    /\ UNCHANGED <<disk, governanceOK, attackerExtract>>

(* Tick: Time advances for all active raw frames.
   Models the watchdog timer: any frame exceeding Delta is force-zeroized.
   This encodes MTL Property 1 (Bounded Temporal Exposure) and
   MTL Property 3 (Watchdog Fail-Closed Liveness) from Paper 19. *)
Tick ==
    /\ raw /= {}                          \* Only tick when frames are active
    /\ LET expired == {f \in raw : age[f] + 1 > Delta} IN
       /\ raw' = raw \ expired
       /\ zeroized' = zeroized \cup expired
       /\ processed' = processed \ expired
       /\ domain' = [f \in Frames |->
            IF f \in expired THEN "Low" ELSE domain[f]]
       /\ age' = [f \in Frames |->
            IF f \in raw /\ f \notin expired THEN age[f] + 1
            ELSE IF f \in expired THEN 0
            ELSE age[f]]
       /\ UNCHANGED <<disk, governanceOK, attackerExtract>>

(* GovernanceFail: Fail-closed semantics.
   Governance module fails — system emergency-zeroizes ALL raw frames.
   This is the formal encoding of MTL Property 2 (Governance Non-Bypass)
   combined with Theorem 4 (Fail-Closed State Reachability). *)
GovernanceFail ==
    /\ governanceOK = TRUE
    /\ governanceOK' = FALSE
    /\ zeroized' = zeroized \cup raw      \* Emergency zeroize all raw
    /\ processed' = processed \ raw
    /\ domain' = [f \in Frames |->
         IF f \in raw THEN "Low" ELSE domain[f]]
    /\ age' = [f \in Frames |->
         IF f \in raw THEN 0 ELSE age[f]]
    /\ raw' = {}                           \* All raw frames destroyed
    /\ UNCHANGED <<disk, attackerExtract>>

(* GovernanceRecover: Resume operations after remediation.
   Only possible when all raw frames have been safely cleared. *)
GovernanceRecover ==
    /\ governanceOK = FALSE
    /\ raw = {}                            \* Safe to resume
    /\ governanceOK' = TRUE
    /\ UNCHANGED <<raw, processed, zeroized, age, domain, disk, attackerExtract>>

\* ==========================================================================
\* Adversarial Actions (for counterexample generation)
\* ==========================================================================

(* A3 adversary attempts to write raw frame to persistent disk *)
IllegalDiskWrite(f) ==
    /\ f \in raw
    /\ disk' = disk \cup {f}
    /\ UNCHANGED <<raw, processed, zeroized, age, domain, governanceOK, attackerExtract>>

(* A0-A3 adversary attempts to extract raw frame from volatile memory *)
AttackerAttempt(f) ==
    /\ f \in raw
    /\ attackerExtract' = attackerExtract \cup {f}
    /\ UNCHANGED <<raw, processed, zeroized, age, domain, disk, governanceOK>>

\* ==========================================================================
\* Behavioral Specifications
\* ==========================================================================

(* Safe system — only legal transitions (represents correct TCB behavior) *)
SafeNext ==
    \/ \E f \in Frames : Capture(f)
    \/ \E f \in Frames : Process(f)
    \/ \E f \in Frames : Zeroize(f)
    \/ Tick
    \/ GovernanceFail
    \/ GovernanceRecover

(* Adversarial system — includes illegal actions for counterexample demo *)
AdversarialNext ==
    \/ SafeNext
    \/ \E f \in Frames : IllegalDiskWrite(f)
    \/ \E f \in Frames : AttackerAttempt(f)

(* SafeSpec: Verification target — all invariants should PASS.
   WF_vars(Tick) ensures time always advances (scheduler fairness K3).
   WF_vars(Zeroize(f)) ensures frames are zeroized when eligible. *)
SafeSpec ==
    Init /\ [][SafeNext]_vars
         /\ WF_vars(Tick)
         /\ \A f \in Frames : WF_vars(Zeroize(f))

(* AdversarialSpec: Attack demonstration — invariants WILL be violated.
   TLC produces counterexample traces showing exact attack paths. *)
AdversarialSpec ==
    Init /\ [][AdversarialNext]_vars

\* ==========================================================================
\* Safety Invariants (State Predicates — checked by TLC as INVARIANT)
\* ==========================================================================

(* INV-A / Paper 19 Theorem 1: No raw frame ever reaches persistent disk *)
NoPersistence ==
    disk = {}

(* INV-TTL / Paper 19 Theorem 2: Raw frame lifetime bounded by Delta *)
BoundedZeroization ==
    \A f \in Frames : f \in raw => age[f] <= Delta

(* INV-EXTRACT / Paper 19 Eq. 2: A0-A3 cannot extract raw data *)
NoExtraction ==
    attackerExtract = {}

(* INV-GOV / Paper 19 Theorem 3: Governance failure => no raw frames *)
GovernanceGate ==
    governanceOK = FALSE => raw = {}

(* INV-FLOW / Paper 19 Sec. III: Raw frames exist only in High domain *)
HighLowSeparation ==
    \A f \in Frames : f \in raw => domain[f] = "High"

(* Derived: No High-domain data on persistent disk *)
NoHighToDisk ==
    \A f \in Frames : f \in disk => domain[f] = "Low"

\* ==========================================================================
\* Temporal Properties (checked by TLC as PROPERTY)
\* ==========================================================================

(* Liveness / Paper 19 MTL Property 1: Every raw frame is eventually zeroized *)
EventuallyZeroized ==
    \A f \in Frames : [](f \in raw => <>(f \in zeroized))

=============================================================================
\* Modification History
\* Created 2026-02-19 — Higher-Rigor Paper 19 Formal Verification Artifact
\* ScholarMaster Research Series
=============================================================================
