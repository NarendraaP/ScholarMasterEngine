# 04_DELEGATION_OPERATING_PROTOCOL.md
## SCHOLARMASTER AGENT PROTOCOL — DELEGATION OPERATING PROTOCOL

**Protocol Code:** `DOP-001`  
**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SOM-001 Operating Mode`  
**Target Scope:** Autonomous task delegation, work item classification, subagent selection, dependency resolution, execution DAG management, parallel execution, synchronization, escalation, retry logic, blocking rules, error handling, performance guidelines, acceptance tests, and machine instructions.

---

## 1. WORK ITEM CLASSIFICATION

Every task submitted to the system is categorized into one of 6 primary Work Item Classes:

| Class Code | Work Item Class Title | Scope & Target Subsystem | Primary Responsible Agent |
|---|---|---|---|
| **WIC-01** | **System Architecture & Design** | 8-Layer Stack, Invariant Contracts (`INV-01..15`), L3 Boundary | `Architecture_Agent` |
| **WIC-02** | **Algorithmic Science & Math** | FAISS Search (`ALG-01`), ST-CSF (`ALG-03`), Merkle Tree (`ALG-07`) | `Algorithm_Agent` |
| **WIC-03** | **Software Implementation** | Codebase (`core/`, `main.py`, `api/`, `admin_panel.py`) | `Implementation_Agent` |
| **WIC-04** | **Empirical Benchmarks & Logs**| Test Rigs (`EXP-01..10`), Benchmark JSON Logs, Hardware Node Tests | `Experiment_Agent` |
| **WIC-05** | **Visual & Diagram Engineering**| 16 PGF/TikZ Figures (`VIS-01..16`), Visual Style Guide (SROS-008) | `Visual_Engineering_Agent` |
| **WIC-06** | **Editorial & Thesis Governance**| Dissertation LaTeX (`project_report.tex`), 21-Paper Suite (`P1..P21`) | `Editorial_Governance_Agent` |

---

## 2. AGENT SELECTION

The Orchestrator Agent evaluates incoming work items using the deterministic selection function:

$$\mathbf{AgentSelect}(W) = \arg\max_{A \in \mathcal{A}} \text{DomainMatchScore}(W, A)$$

### Subagent Roster & Capability Matrix:
- **`01_Orchestrator_Agent`:** Master task dispatcher, execution DAG manager, and final release gatekeeper.
- **`02_Strategic_Planning_Agent`:** Project manager, backlog owner, priority classifier, and critical path analyzer.
- **`03_Thesis_Architecture_Agent`:** Architecture blueprint author, layer invariant verifier, and structural designer.
- **`04_Algorithmic_Science_Agent`:** Pseudocode author, theoretical complexity verifier ($O$-notation), math balance auditor.
- **`05_Software_Engineering_Agent`:** Python code developer (`core/`), thread synchronization engineer, REST API developer.
- **`06_Empirical_Research_Agent`:** Benchmark test execution harness engineer, raw JSON log validator, hardware test lead.
- **`07_Visual_Engineering_Agent`:** PGF/TikZ diagram author, visual style guide auditor (SROS-008), contrast verifier.
- **`08_Editorial_Governance_Agent`:** Dissertation editor, 21-paper portfolio manager, bibliography auditor, consistency checker.

---

## 3. DEPENDENCY RESOLUTION

Dependencies between delegated tasks are resolved using topological sorting over the dependency graph:

$$\mathcal{G} = (\mathcal{V}_{\text{Tasks}}, \mathcal{E}_{\text{Dependencies}})$$

- **Rule 1 (Upstream Lock):** A downstream task $T_j$ cannot be delegated until all ancestor tasks $\text{Ancestors}(T_j)$ achieve `COMPLETED` status.
- **Rule 2 (Cycle Prohibition):** Any detected cycle $\mathcal{C} \subset \mathcal{E}$ triggers an immediate hard error (`ERR-CYCLE-DETECTED`) and halts delegation.

---

## 4. EXECUTION DAG

The master execution workflow operates as a strict Directed Acyclic Graph (DAG):

```
       [WIC-01: Architecture]
                │
                ▼
       [WIC-02: Algorithms & Math]
                │
                ▼
       [WIC-03: Implementation]
           ┌────┴────┐
           ▼         ▼
[WIC-04: Exps]    [WIC-05: Diagrams]
           └────┬────┘
                ▼
       [WIC-06: Thesis & Papers]
                │
                ▼
    [Master System Freeze]
```

---

## 5. PARALLEL EXECUTION

- **Independent Branch Concurrency:** Tasks residing in independent DAG branches (e.g., `WIC-04: Empirical Benchmarks` and `WIC-05: Visual Diagrams`) MAY execute concurrently across separate subagent worker contexts.
- **Worker Isolation:** Parallel subagents MUST operate in isolated scratch spaces (`scratch/subagent_<id>/`) to prevent concurrent file write collisions.

---

## 6. SYNCHRONIZATION

- **Synchronization Barrier:** When parallel tasks converge (e.g., merging `WIC-04` and `WIC-05` results into `WIC-06: Thesis`), the Orchestrator enforces a strict Synchronization Barrier.
- **State Checksum:** Before unblocking downstream execution, the Orchestrator verifies that all converging tasks match the expected git commit checksum.

---

## 7. ESCALATION

If a subagent encounters an unresolvable failure or policy violation, it triggers an immediate Escalation Cascade:

```
[Subagent Execution Failure]
           │
           ▼ (Retry limit exceeded)
[Escalate to Strategic Planning Agent (02)]
           │
           ▼ (Critical Path Blocked)
[Escalate to Orchestrator Agent (01)]
           │
           ▼ (System Invariant Violation)
[Trigger Fail-Closed Lockdown & Notify SPB]
```

---

## 8. RETRY LOGIC

- **Max Retries:** 3 automatic retry attempts per task.
- **Backoff Strategy:** Exponential backoff ($t_{\text{wait}} = 2^k \times 500\text{ms}$ for attempt $k \in \{1, 2, 3\}$).
- **Retry Condition:** Retries are executed ONLY for transient failures (e.g., subagent timeout, temporary file lock). Deterministic syntax or invariant errors skip retry and escalate immediately.

---

## 9. BLOCKING RULES

1. **Rule B1 (Invariant Failure):** Any violation of Layer 3 RAM zeroization (`INV-01..15`) immediately blocks all downstream task delegations.
2. **Rule B2 (Build Failure):** A failed syntax check or broken Python import in `core/` blocks all test and deployment tasks.
3. **Rule B3 (Un-committed Changes):** A task cannot be delegated if the working directory contains un-committed dirty changes.

---

## 10. ERROR HANDLING

### Canonical Error Codes:
- `ERR-001 (AGENT_SELECTION_FAILED)`: No suitable subagent found for work item class.
- `ERR-002 (DEPENDENCY_CYCLE)`: Circular dependency detected in execution DAG.
- `ERR-003 (INVARIANT_BREACH)`: Layer boundary invariant violated during task execution.
- `ERR-004 (BENCHMARK_TIMEOUT)`: Empirical benchmark execution exceeded maximum runtime cap.
- `ERR-005 (VERIFICATION_FAILED)`: Artifact failed mandatory acceptance test suite.

---

## 11. PERFORMANCE GUIDELINES

- **Delegation Overhead Cap:** Task classification and subagent dispatch MUST complete within $\le 200\text{ms}$.
- **Parallel Speedup:** Multi-subagent execution MUST achieve at least $\ge 2.5\times$ speedup over sequential execution for independent task branches.
- **Resource Limits:** Total subagent CPU usage MUST NOT exceed 80% host capacity to preserve system stability.

---

## 12. ACCEPTANCE TESTS

Every delegation workflow must pass 5 formal protocol acceptance tests:
1. **DAG Validity Test:** Execution graph is verified as a valid DAG with 0 cycles.
2. **Subagent Mapping Test:** 100% of tasks are correctly mapped to authorized subagents.
3. **Barrier Sync Test:** Downstream tasks remain blocked until all upstream dependencies succeed.
4. **Retry & Escalation Test:** Fault injection demonstrates correct exponential backoff and escalation.
5. **Git Lineage Test:** Final delegated outputs are committed with full SROS governance metadata.

---

## 13. MACHINE INSTRUCTIONS

```yaml
protocol_name: "Delegation_Operating_Protocol"
protocol_id: "04_delegation_operating_protocol"
operating_mode: "SOM-001"
delegation_rules:
  - "Enforce strict DAG order; never dispatch downstream tasks prematurely."
  - "Enforce worker isolation for parallel execution."
  - "Immediately escalate Layer 3 RAM zeroization invariant breaches."
  - "Verify checksums at every synchronization barrier."
  - "Limit automatic retries to maximum 3 attempts with exponential backoff."
```
