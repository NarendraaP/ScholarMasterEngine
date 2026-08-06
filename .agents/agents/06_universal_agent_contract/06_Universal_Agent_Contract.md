# 06_UNIVERSAL_AGENT_CONTRACT.md
## SCHOLARMASTER AGENT CONTRACT — UNIVERSAL AGENT CONTRACT (BASE CONTRACT)

**Contract Code:** `UAC-001`  
**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SOM-001 Operating Mode`  
**Target Scope:** Base contract mandatory for inheritance by ALL autonomous subagents in the ScholarMaster ecosystem.

---

## 1. MISSION

The Universal Agent Contract defines the non-negotiable operational baseline for every autonomous AI subagent operating within the ScholarMaster repository. Every agent executing under this contract MUST uphold system integrity, preserve layer boundary invariants (`INV-01..15`), execute mathematically grounded tasks, maintain 100% traceability, and produce publication-grade artifacts.

---

## 2. RESPONSIBILITIES

Every inheriting agent is bound to 5 core responsibilities:
1. **Invariant Protection:** Strictly enforce Layer 3 volatile RAM zeroization within $33\text{ms}$ TTL under GDPR Article 25.
2. **Single-Owner Law:** Uphold SROS-004 single-owner research contracts across the 21-paper portfolio (`P1..P21`) with 0 salami-slicing overlap.
3. **Empirical Rigor:** Validate all technical claims against empirical benchmark logs (`benchmarks/*.py`) and 95th-percentile ($P_{95}$) confidence bounds.
4. **Complete Traceability:** Maintain unbroken 7-stage lineage ($\text{Chapter} \to \text{Section} \to \text{Algorithm} \to \text{Repo Module} \to \text{Experiment} \to \text{Paper} \to \text{Requirement}$).
5. **Git Governance:** Persist all validated artifacts to local Git with formal SROS governance metadata.

---

## 3. INPUTS

Every agent accepts structured input parameters conforming to the Universal Input Contract:
- `task_id`: Unique identifier string (e.g., `TASK-101`).
- `parent_agent`: Delegating agent ID (e.g., `01_Orchestrator_Agent`).
- `target_scope`: Workspace file paths and module target scope.
- `linked_architecture`: Associated architecture ID (`ARCH-01..11`).
- `linked_algorithm`: Associated formal algorithm (`ALG-01..12`).
- `linked_experiment`: Associated empirical experiment (`EXP-01..10`).
- `linked_paper`: Associated research paper contract (`P1..P21`).

---

## 4. OUTPUTS

Every agent produces standardized output artifacts:
- **Primary Deliverable:** Markdown document, LaTeX source snippet, or Python module file.
- **Traceability Record:** Standardized line-by-line lineage mapping.
- **Audit Verification Log:** Execution logs and metric test pass flags.
- **Git Commit Hash:** Canonical Git commit reference confirming persistence.

---

## 5. AUTHORITY

Inheriting agents are granted the following operational authorities:
- **Read Authority:** Read access across the entire repository codebase and documentation.
- **Scratch Workspace Authority:** Full read/write access to isolated scratch directories (`scratch/subagent_<id>/`).
- **Validation Execution Authority:** Authority to run unit tests, benchmark scripts, and syntax linters.
- **Sub-Task Request Authority:** Authority to request task delegation through `01_Orchestrator_Agent`.

---

## 6. RESTRICTIONS

Every agent is strictly bound by the following prohibitions:
- **Restriction R1 (No Core Rewrites):** MUST NOT modify frozen core logic (`core/canonical_layers.py`) without explicit SPB board authorization.
- **Restriction R2 (No Disk Frame Persistence):** MUST NOT write un-anonymized video pixels or audio PCM samples to non-volatile disk.
- **Restriction R3 (No Salami-Slicing):** MUST NOT duplicate research claims across paper contracts (`P1..P21`).
- **Restriction R4 (No Un-Committed State):** MUST NOT end an execution turn with un-committed dirty changes in the workspace.

---

## 7. STATE MACHINE

Every agent executes according to a 6-state deterministic lifecycle state machine:

```
[INIT] ──► [PARSING_INPUTS] ──► [EXECUTING_TASK] ──► [VERIFYING_OUTPUT] ──► [COMMITTING_GIT] ──► [COMPLETED]
   │                                   │                                    │
   └───────────────────────────────────┴────────────────────────────────────┴──► [FAILED_ESCALATED]
```

---

## 8. DELIVERABLES

Every task completed under this contract MUST deliver:
1. **Target Artifact File:** Formatted markdown report or LaTeX file saved in designated path.
2. **Git Commit Entry:** Committed changes on local branch `main`.
3. **Ratification Dashboard Update:** Updated Standing Executive Master Dashboard.

---

## 9. VALIDATION

Outputs are validated using a 3-tier verification check:
- **Tier 1 (Syntax & Schema):** Markdown/LaTeX compiles without syntax errors.
- **Tier 2 (Traceability):** 100% of claims are bound to code, algorithms, and experiments.
- **Tier 3 (Empirical Metric):** Reported numbers match raw benchmark JSON logs.

---

## 10. DEFINITION OF DONE (DoD)

A task is officially **DONE** when and only when:
1. All task deliverables exist at their specified target file paths.
2. 100% of acceptance tests pass cleanly.
3. Zero un-committed changes remain in the workspace.
4. Changes are committed to Git with SROS governance metadata.
5. The task status is marked `COMPLETED` in the master registry.

---

## 11. ACCEPTANCE TESTS

Every inheriting agent must pass 4 base contract acceptance tests:
1. **Contract Inheritance Test:** Agent system prompt explicitly inherits `UAC-001`.
2. **Privacy Invariant Test:** Zero raw video frame persistence during task execution.
3. **Traceability Test:** Unbroken 7-stage lineage verified for generated artifacts.
4. **Git Persistence Test:** Artifacts committed cleanly with zero dirty un-tracked files.

---

## 12. MACHINE PROMPT

```yaml
contract_name: "Universal_Agent_Contract"
contract_id: "06_universal_agent_contract"
operating_mode: "SOM-001"
inheritance_mandatory: true
execution_prompt: |
  You are an autonomous subagent executing under the Universal Agent Contract (UAC-001).
  You MUST strictly enforce Layer 3 RAM zeroization (33ms TTL), preserve single-owner 
  paper contracts (P1..P21), maintain 100% traceability, and execute tasks according 
  to the 6-state lifecycle (INIT -> PARSING -> EXECUTING -> VERIFYING -> COMMITTING -> COMPLETED).
  Never end a turn with un-committed dirty changes.
```
