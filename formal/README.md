# TLA+ Formal Verification — ScholarMaster Privacy Invariants

> **Paper 19 Artifact:** Mechanical model-checking of core memory safety invariants.

## Specifications

| Spec | Rigor | Features |
|---|---|---|
| `ScholarMaster_Invariants.tla` | Minimal | Single frame, basic lifecycle, 3 invariants |
| **`ScholarMaster_HR.tla`** | **Higher-Rigor** | **Concurrency, bounded time, domains, adversary, fairness** |

---

## Higher-Rigor Model (`ScholarMaster_HR`)

### State Variables

| Variable | Type | Meaning |
|---|---|---|
| `raw` | Set of Frames | Frames in volatile raw state (D_High) |
| `processed` | Set of Frames | Frames that have been through F_irreversible |
| `zeroized` | Set of Frames | Frames that have been securely destroyed |
| `age` | Frame → Nat | Ticks since capture (watchdog timer) |
| `domain` | Frame → {High, Low} | Information flow domain tracking |
| `disk` | Set of Frames | Frames written to persistent storage |
| `governanceOK` | Boolean | Governance module operational status |
| `attackerExtract` | Set of Frames | Frames adversary has extracted |

### Actions

| Action | Meaning | Paper 19 Mapping |
|---|---|---|
| `Capture(f)` | Sensor ingests frame into High domain | §IV State Transition |
| `Process(f)` | F_irreversible transforms frame | §III.3 Dimensionality Reduction |
| `Zeroize(f)` | TCB destroys raw buffer → Low domain | MTL Property 1 |
| `Tick` | Time advances; watchdog force-zeroizes expired frames | MTL Property 3 |
| `GovernanceFail` | Fail-closed: emergency zeroize all raw | MTL Property 2, Theorem 4 |
| `GovernanceRecover` | Resume after remediation | — |
| `IllegalDiskWrite(f)` | ⚠️ Adversarial: raw frame → disk | Counterexample |
| `AttackerAttempt(f)` | ⚠️ Adversarial: A0-A3 extraction | Counterexample |

### Verified Properties

| Property | Type | Paper 19 Mapping | Safe Mode |
|---|---|---|---|
| `NoPersistence` | Safety | Theorem 1 (INV-A) | ✅ PASS |
| `BoundedZeroization` | Safety | Theorem 2 (Δ ≤ 33ms) | ✅ PASS |
| `NoExtraction` | Safety | Eq. 2 (Threat Model) | ✅ PASS |
| `GovernanceGate` | Safety | Theorem 3 (INV-B) | ✅ PASS |
| `HighLowSeparation` | Safety | §III (Non-Interference) | ✅ PASS |
| `NoHighToDisk` | Safety | §III (Information Flow) | ✅ PASS |
| `EventuallyZeroized` | Liveness | MTL Property 1 | ✅ PASS |

---

## How To Run

### Option A: TLA+ Toolbox (GUI)
1. Install [TLA+ Toolbox](https://lamport.azurewebsites.net/tla/toolbox.html)
2. File → Open Spec → `ScholarMaster_HR.tla`
3. TLC Model Checker → New Model
4. Set **Specification** to `SafeSpec`, **Constant** `N = 3`
5. Add all invariants and `EventuallyZeroized` as a property
6. Run TLC → **Expected: All pass ✅**

### Option B: Command Line
```bash
# Requires Java 11+ and tla2tools.jar
# Download from https://github.com/tlaplus/tlaplus/releases

# Safe verification (should PASS all 7 invariants + liveness)
java -jar tla2tools.jar -config ScholarMaster_HR_Safe.cfg ScholarMaster_HR.tla

# Adversarial mode (produces COUNTEREXAMPLE traces)
java -jar tla2tools.jar -config ScholarMaster_HR_Adversarial.cfg ScholarMaster_HR.tla
```

---

## Two-Mode Verification Strategy

### Mode 1: `SafeSpec` — System Correctness
- Legal transitions only: `Capture → Process → Zeroize → Tick`
- Watchdog in `Tick` auto-zeroizes frames exceeding `Delta`
- `GovernanceFail` triggers emergency fail-closed zeroization
- Fairness: `WF_vars(Tick)` + `WF_vars(Zeroize(f))` for all frames
- **Expected: ALL invariants + liveness PASS ✅**

### Mode 2: `AdversarialSpec` — Attack Detection
- Adds `IllegalDiskWrite` and `AttackerAttempt` actions
- `NoPersistence` → **VIOLATED** (counterexample: Capture → IllegalDiskWrite)
- `NoExtraction` → **VIOLATED** (counterexample: Capture → AttackerAttempt)
- **Demonstrates invariants catch violations** — reviewer-grade evidence

---

## What This Does NOT Verify

| Out of Scope | Bounded By |
|---|---|
| Hardware DMA attacks | Paper 19 §II.5 (A₅) |
| Spectre / Rowhammer | Paper 19 §VI, Table I |
| Cold boot physics | Paper 19 §II.5 (A₅) |
| Kernel compromise | Paper 19 §II.4 (A₄) |

> Formal methods verify the **software model**.
> The threat model in Paper 19 bounds the **hardware domain**.

---

## Citable Statement for Paper 19

> *"The core memory lifecycle and governance invariants were modeled using TLA+ under bounded concurrent frame conditions (N ≤ 3). Model checking confirmed absence of persistence, bounded zeroization (Δ ≤ 3 ticks), governance-gate enforcement, and High/Low domain separation under all reachable states."*

---

## Files

```
formal/
├── ScholarMaster_Invariants.tla          # Minimal single-frame spec
├── ScholarMaster_Invariants_Safe.cfg     # TLC config (minimal, safe)
├── ScholarMaster_Invariants_Adversarial.cfg
├── ScholarMaster_HR.tla                  # Higher-rigor concurrent spec
├── ScholarMaster_HR_Safe.cfg             # TLC config (HR, safe — N=3)
├── ScholarMaster_HR_Adversarial.cfg      # TLC config (HR, adversarial — N=2)
└── README.md                             # This file
```
