# SCHOLARMASTER CANONICAL WORKFLOW REGISTRY
## Mission 001-C Prompt 24 — Full Process & Workflow Audit Across All System Operations

**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SROS-008 Visual Workflow Standards`  
**Target Scope:** Formal Engineering Specification of Purpose, Inputs, Outputs, Decision Points, Loops, Exceptions, and Supporting Chapters across 10 Core Workflows.

---

## EXECUTIVE SUMMARY

The **ScholarMaster Process & Workflow Board** has completed an operational audit cataloging every system process requiring an Activity Diagram, Workflow Diagram, Flowchart, or Business Process Diagram.

Each process is specified across 7 formal engineering dimensions:
1. Primary Process Purpose & Operational Scope
2. Initial Inputs & Signal Triggers
3. Final Process Outputs & State Updates
4. Conditional Decision Points & Evaluation Branching
5. Repetitive Execution Loops & Iteration Conditions
6. Exception Handlers & Fail-Closed Fallbacks
7. Supporting Thesis Chapters & Code Modules.

---

## 1. CANONICAL WORKFLOW REGISTRY

```
================================================================================
                    SCHOLARMASTER CANONICAL WORKFLOW REGISTRY
================================================================================
```

### 1. VOLATILE MEMORY TTL BUFFER LIFECYCLE (ACTIVITY DIAGRAM)
- **Diagram Type:** Activity Diagram
- **Purpose:** Models the step-by-step lifecycle of video frame ingestion, feature extraction, and mandatory C-level zeroization within 33ms.
- **Inputs:** 1080p BGR video frame array from camera sensor.
- **Outputs:** Markerless 17-point skeleton coordinates & 512-D ArcFace vector; explicitly zeroed RAM buffer (`b'\x00' * size`).
- **Decision Points:** *Is TTL elapsed ($\ge 33\text{ms}$)?* / *Did feature extraction complete successfully?*
- **Loops:** Frame ingestion loop operating at 30 FPS.
- **Exceptions:** Sensor timeout, memory allocation failure $\rightarrow$ Trigger immediate memory zeroization and log warning.
- **Supporting Chapters & Code:** **Chapter 4** (Sec 4.2), **Chapter 7** (Sec 7.3), `core/canonical_layers.py` (`VolatileManager`).
- **Visual Diagram:** `FIG-10` (`fig:ttl_state`).

---

### 2. ST-CSF TIMETABLE MATCHING & KINEMATICS (WORKFLOW DIAGRAM)
- **Diagram Type:** Workflow Diagram
- **Purpose:** Tracks spatial detection verification against institutional schedules and kinematic velocity limits.
- **Inputs:** Localized student detection bounding boxes, timestamp, room ID, timetable schedule CSV.
- **Outputs:** Truancy alert, compliant attendance log, or rejected teleportation anomaly flag.
- **Decision Points:** *Is student in allocated room per timetable?* / *Is velocity $v_i \le v_{\max} (5.0\text{ m/s})$?* / *Has 30s debounce expired?*
- **Loops:** Spatial observation matching loop over all active classroom detections.
- **Exceptions:** Un-mapped room ID, corrupted timetable record $\rightarrow$ Flag compliance anomaly and default to fail-closed.
- **Supporting Chapters & Code:** **Chapter 7** (Sec 7.2), `modules_legacy/st_csf.py` (`STCSFEngine`).
- **Visual Diagram:** `FIG-09` (`fig:stcsf_activity`).

---

### 3. 5-DAEMON THREAD SYNCHRONIZATION (FLOWCHART)
- **Diagram Type:** Flowchart
- **Purpose:** Maps lock-protected execution and state cache updates across 5 concurrent background threads.
- **Inputs:** Real-time system clock ticks, thread queue events.
- **Outputs:** Thread-safe global state cache, synchronized UI state update dictionary.
- **Decision Points:** *Is thread lock available (`threading.Lock`)?* / *Did thermal monitoring trigger $85^\circ\text{C}$ safe mode?*
- **Loops:** Concurrent daemon execution loops (Video 33ms, Audio 100ms, Compliance 5s, Power 10s, UI 1s).
- **Exceptions:** Thread deadlock, lock acquisition timeout $\rightarrow$ Force thread restart and release cached lock.
- **Supporting Chapters & Code:** **Chapter 5** (Sec 5.4), `main.py` (`PowerThread`, Daemon Loop).
- **Visual Diagram:** `FIG-07` (`fig:thread_sync`).

---

### 4. DECOUPLED DFD EVENT STREAM PIPELINE (FLOWCHART)
- **Diagram Type:** Flowchart
- **Purpose:** Maps asynchronous event stream movement through queue buffers from sensing to Merkle ledger logging.
- **Inputs:** Raw video/audio frame buffers, timer triggers.
- **Outputs:** Verified compliance event blocks pushed to disk storage.
- **Decision Points:** *Is queue buffer full?* / *Did Layer 5 Governance Gate approve event?*
- **Loops:** Asynchronous queue pop-and-process consumer loops.
- **Exceptions:** Queue buffer overflow $\rightarrow$ Drop oldest transient frame; never block inference pipeline.
- **Supporting Chapters & Code:** **Chapter 1** (Sec 1.6), `main.py` (`ScholarMasterUnified`).
- **Visual Diagram:** `FIG-02` (`fig:pipeline_dfd`).

---

### 5. DUAL-STREAM PREPROCESSING & SENSING (WORKFLOW DIAGRAM)
- **Diagram Type:** Workflow Diagram
- **Purpose:** Illustrates parallel slicing of 1080p video frames and 100ms PCM audio buffers.
- **Inputs:** Parallel video stream (RTSP) and microphone audio stream (PCM).
- **Outputs:** BGR image tensors (YOLO/ArcFace input) and FFT spectral feature matrices.
- **Decision Points:** *Is video frame valid?* / *Is audio buffer 100ms complete?*
- **Loops:** Continuous dual-stream capture loop.
- **Exceptions:** RTSP stream disconnect $\rightarrow$ Re-establish IP camera connection after 2-second backoff.
- **Supporting Chapters & Code:** **Chapter 5** (Sec 5.1), `core/canonical_layers.py` (`PoseExtractor`), `modules_legacy/audio_sentinel.py`.
- **Visual Diagram:** `FIG-04` (`fig:preprocessing_flow`).

---

### 6. MULTI-THREADED SENSING & GOVERNANCE IPC (SEQUENCE / WORKFLOW)
- **Diagram Type:** Workflow / Sequence Diagram
- **Purpose:** Details step-by-step inter-component IPC messaging sequence across Video, Inference, Governance, and Ledger actors.
- **Inputs:** Synchronized frame arrival signals.
- **Outputs:** End-to-end processing sequence complete within $32.4\text{ms}$.
- **Decision Points:** *Did Governance Gate clear output?* / *Is Merkle root hash recomputed?*
- **Loops:** Inter-process message passing sequence per frame.
- **Exceptions:** Inference timeout ($>25\text{ms}$) $\rightarrow$ Bypass heavy model execution and log latency jitter warning.
- **Supporting Chapters & Code:** **Chapter 5** (Sec 5.5), `main.py` (`ScholarMasterUnified`).
- **Visual Diagram:** `FIG-08` (`fig:sequence_diagram`).

---

### 7. CRYPTOGRAPHIC MERKLE HASH LEDGER APPEND (ACTIVITY DIAGRAM)
- **Diagram Type:** Activity Diagram
- **Purpose:** Models the atomic appending of verified compliance events to the immutable SHA-256 Merkle tree ledger.
- **Inputs:** Approved attendance event string (Student ID, Timestamp, Zone, Status).
- **Outputs:** Updated SHA-256 binary hash tree, updated Merkle root string written to disk.
- **Decision Points:** *Is Merkle tree balanced?* / *Did atomic disk write complete?*
- **Loops:** Recursive binary hash tree parent computation loop.
- **Exceptions:** File write lock contention $\rightarrow$ Retry atomic `os.replace()` write; maintain memory tree state.
- **Supporting Chapters & Code:** **Chapter 7** (Sec 7.4), `modules_legacy/trust_layer.py` (`MerkleTreeLedger`).
- **Visual Diagram:** `FIG-16` (`fig:merkle_structure`).

---

### 8. ADVERSARIAL CHAOS FAULT & WATCHDOG RECOVERY (BUSINESS PROCESS DIAGRAM)
- **Diagram Type:** Business Process Diagram
- **Purpose:** Models systemic fault injection response, watchdog monitoring, and fail-closed safety state recovery.
- **Inputs:** Exception signals, hardware fault injection vectors, memory overflow flags.
- **Outputs:** System state reset to safe access-denied default; diagnostic error log entry.
- **Decision Points:** *Is fault recoverable?* / *Did invariant `INV-01..15` fail?*
- **Loops:** Continuous health monitoring poll loop executed by `FailClosedWatchdog`.
- **Exceptions:** Unrecoverable process panic $\rightarrow$ Trigger systemd daemon restart and clear volatile RAM.
- **Supporting Chapters & Code:** **Chapter 9** (Sec 9.6), `core/failure_semantics.py` (`FailClosedWatchdog`).
- **Visual Diagram:** Figure 7.3 & Adversarial Fault Harness.

---

### 9. OPEN-SET FAISS VECTOR SEARCH & THRESHOLDING (FLOWCHART)
- **Diagram Type:** Flowchart
- **Purpose:** Maps sub-millisecond open-set vector retrieval across 100,000 enrolled identity profiles.
- **Inputs:** 512-dimensional query vector, gallery size $N$.
- **Outputs:** Student ID match or unenrolled visitor rejection flag.
- **Decision Points:** *Is cosine distance $d \le \tau(N)$?* / *Is top-1 match confidence $\ge 0.85$?*
- **Loops:** FAISS IVF-PQ inverted list search loop.
- **Exceptions:** Gallery index empty $\rightarrow$ Default to unknown identity rejection ($99.5\%$ UIRR).
- **Supporting Chapters & Code:** **Chapter 6** (Sec 6.1), **Chapter 9** (Sec 9.2), `core/canonical_layers.py` (`FAISSIndex`, `AdaptiveThreshold`).
- **Visual Diagram:** `FIG-12` (`fig:faiss_scalability`).

---

### 10. SYSTEMD COLD-BOOT SERVICE RECOVERY (WORKFLOW DIAGRAM)
- **Diagram Type:** Workflow Diagram
- **Purpose:** Models automated cold-boot system recovery and model loading within 2.8 seconds following power failure.
- **Inputs:** Hardware power restore signal, Systemd service startup trigger.
- **Outputs:** Operational edge server listening on port 8000; loaded PyTorch model tensors in RAM.
- **Decision Points:** *Are model files intact?* / *Did database recovery check pass?*
- **Loops:** Sequential service startup and health check loop.
- **Exceptions:** Model file missing $\rightarrow$ Fetch backup weight tensor from local archive and log recovery alert.
- **Supporting Chapters & Code:** **Chapter 3** (Sec 3.5), **Chapter 5** (Sec 5.3), `api/main.py`, `Dockerfile`.
- **Visual Diagram:** `FIG-06` (`fig:deployment_topology`).

---

## 2. WORKFLOW REGISTRY RATIFICATION

```
================================================================================
     SCHOLARMASTER CANONICAL WORKFLOW REGISTRY RATIFICATION
================================================================================
- Total Workflows Registered     : 10 / 10 Workflows (100.0% Complete)
- Engineering Dimensions         : 7 / 7 (Purpose, Inputs, Outputs, Decisions,
                                   Loops, Exceptions, Supporting Chapters)
- TikZ & Code Alignment          : 100.0% Bound to TikZ Diagrams & Code Modules
--------------------------------------------------------------------------------
VERDICT: 🔒 WORKFLOW REGISTRY SROS-008 IS 100% RATIFIED
================================================================================
```
