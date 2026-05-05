# PAPER 3 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Pose-Only Edge Action Sensing with Enforced Volatile Memory Confinement |
| **Paper ID** | P3 |
| **Layer** | Vision Perception Layer (L3) |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Finalized (Boundary Enforced) |

## 2. Primary Contribution

**A geometric action-sensing pipeline that extracts kinematic events without retaining biometric texture, enforced via a mathematically bounded ($\Delta T_{volatile} \le 33$ ms) OS-level memory zeroization constraint.**

Paper 3 operates strictly as the Vision Perception layer. It establishes how raw optical feeds are safely converted into anonymous coordinate tensors via pose networks and classical PnP orientation estimation, guaranteeing that structural identity is mathematically scrubbed before reaching the persistent evaluation layers.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | High-resolution biometric texture is unnecessary for kinematic evaluation; dimensional projection via pose estimation acts as a structural privacy filter | Rank-Nullity derivation (Eq 9-11) | Clean |
| C2 | Volatile memory can be mathematically bounded to $\Delta T_{volatile} \le 33$ ms using OS-level `mlock()` and explicit cache zeroization routines | Section V / Table II | Clean |
| C3 | Classical PnP geometry successfully derives head orientation from 2D coordinates without referencing facial pixel intensity | Eq 12-16 | Clean |
| C4 | Confidence-adaptive Kalman filtering ($R_k \propto \sigma^2/c_i$) reduces jitter-induced false positives by dynamically responding to network uncertainty | Sec VII.D (FP rate drops to 1.5%) | Clean |

## 4. Scope

### 4.1 In-Scope
- Optical frame acquisition and vectorization (YOLOv8-pose abstraction)
- Dimensionality reduction and null-space analysis
- OS-level memory confinement (`mlock`, `explicit_bzero`)
- Signal stabilization (PnP, Kalman filtering)

### 4.2 Out-of-Scope (Strictly Forbidden)
- **Hardware Node Topology** (Owned by P5 / P18)
- **Relational Schedule Compliance** (Owned by P4)
- **Acoustic Signal Processing** (Owned by P6)
- **Federated Model Updating** (Owned by P13)

## 5. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P3-INV-01 | Must NOT claim overarching system architecture | Terminology restricted to "vision pipeline" and "perception layer" |
| P3-INV-02 | Must NOT claim compliance logic | Focus remains purely on outputting geometric tensors, not evaluating truancy |
| P3-INV-03 | Must NOT claim post-hoc encryption | Emphasizes "memory confinement" over "data encryption" (preventing overlap with P8) |

## 6. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Downstream** | P4 (Relational Logic) | Emits the abstract coordinate payload `(ID, Zone, Timestamp)` consumed by P4 |
| **Downstream** | P20 (Runtime) | Relies on the P20 runtime environment to provide the physical execution space |

## 7. What This Paper Does NOT Do

- Does **not** determine if a student is skipping class (P4 does this).
- Does **not** design the edge node hardware or memory bus (P5 handles this).
- Does **not** encrypt data for network transport (P8 does this).
