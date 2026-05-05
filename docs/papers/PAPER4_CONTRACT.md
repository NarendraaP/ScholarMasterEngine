# PAPER 4 CONTRACT

## 1. Identity

| Field | Value |
|---|---|
| **Title** | Real-Time Schedule Compliance via Spatiotemporal Predicate Evaluation and Relational Lookup |
| **Paper ID** | P4 |
| **Layer** | Data Fusion / Relational Evaluation Layer |
| **Author** | Dr. S. Suresh Kumar |
| **Status** | Finalized (Boundary Enforced) |

## 2. Primary Contribution

**A relational predicate model (CPEM) and temporal debounce filter (PCVF) that evaluates real-time physical presence events against statically scheduled database records using optimized PostgreSQL queries.**

Paper 4 operates strictly as the logical bridge between incoming sensory events and static database records. It focuses entirely on defining schedule compliance mathematically as a streaming predicate, and optimizing the relational database queries (PostgreSQL partitioning, composite indexing, connection pooling) necessary to evaluate those predicates under burst campus traffic.

## 3. Core Claims

| # | Claim | Evidence | Boundary Check |
|---|---|---|---|
| C1 | Schedule compliance can be evaluated continuously as a relational predicate (CPEM) over streaming event tuples | Eq 1-2 | Clean |
| C2 | A temporal low-pass filter (PCVF) effectively suppresses spurious multi-zone detections and transient sensor noise | Eq 4-6 / Alg 1 | Clean |
| C3 | Relational schema partitioning and composite temporal indexing dramatically reduce search space for rapid schedule lookup | Listing 1 / Section VI | Clean |
| C4 | Transaction-level connection pooling prevents latency spikes ($T_{conn}$) during thundering herd transition events | Figure 3 | Clean |

## 5. Scope

### 5.1 In-Scope
- CPEM formalization (Mathematical formulation of schedule adherence)
- PCVF temporal filtering algorithms and state machines
- PostgreSQL database optimization (Partitioning, Indexing)
- Relational query latency profiling and connection pooling analysis

### 5.2 Out-of-Scope (Strictly Forbidden)
- **Message Broker & Middleware Architecture** (Owned by P18)
- **Container / Worker Execution Flow** (Owned by P20)
- **Stream Algorithm Jitter / Migration** (Owned by P7)

## 6. Enforcement Invariants

| ID | Invariant | Enforcement |
|---|---|---|
| P4-INV-01 | Must NOT claim system architecture | Rewrote "layered middleware architecture" to "layered evaluation pipeline" |
| P4-INV-02 | Must NOT claim stream execution logic | Kept focus on relational database lookups rather than stateful stream topologies |
| P4-INV-03 | Must NOT claim edge perception | Treat incoming edge data as an abstract opaque tuple `(ID, Zone, Timestamp)` |

## 7. Upstream / Downstream Dependencies

| Direction | Paper | Interface |
|---|---|---|
| **Upstream** | P3, P6 (Perception) | Consumes resolved `(ID, Zone, Timestamp)` tuples blindly |
| **Downstream** | P20 (Runtime) | Relies on the Runtime to physically execute the workers that run these queries |

## 8. What This Paper Does NOT Do

- Does **not** design the publish-subscribe broker or define system-wide messaging topologies.
- Does **not** evaluate complex streaming states like moving average drift or lazy migration (that is P7).
- Does **not** detect people (that is P3 and P6).
