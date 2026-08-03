# SCHOLARMASTER MASTER PRESENTATION STORYBOARD REGISTRY
## Storyboard Blueprints for M.Tech Thesis Defense and 21 Individual Papers

**Governance Alignment:** `SROS Version 2.1 — FROZEN`, `SEOP Version 2.0 — RATIFIED`, `SROS-010 Presentation Standards`

---

## 1. M.TECH MASTER THESIS DEFENSE STORYBOARD (25 SLIDES)

```
================================================================================
          M.TECH THESIS DEFENSE STORYBOARD BLUEPRINT (25 SLIDES)
================================================================================
```

| Slide # | Section Title | Primary Slide Content / Visual Element | Key Technical Message / Oral Anchor |
|---|---|---|---|
| **Slide 01** | Title & Institutional Metadata | Project Title, Candidate (Polisetti Narendra), Guide, SCET/JNTUK Logos | Sets formal academic tone and institutional alignment. |
| **Slide 02** | Executive Opening | High-level summary, 8-layer stack infographic, key achievement metrics | Hooks the committee with $99.2\%$ OSIR and $33\text{ms}$ volatile RAM TTL. |
| **Slide 03** | The Problem Statement | Surveillance paradigm shift, continuous video risks, biometric leakage | Identifies CCTV passive surveillance limitations in schools. |
| **Slide 04** | Research Motivation | GDPR Article 25 (Privacy by Design), legal liabilities of child biometrics | Frames privacy as a mandatory structural requirement. |
| **Slide 05** | Research Gaps in Literature | Table comparing RFID, CCTV, Differential Privacy, HE vs. ScholarMaster | Proves existing methods fail on latency ($>1\text{s}$) or accuracy. |
| **Slide 06** | Core Engineering Objectives | 5 bulleted core objectives (Decoupled architecture, ST-CSF, Merkle ledger) | Defines clear, measurable engineering targets. |
| **Slide 07** | The Canonical L1--L8 Architecture | TikZ Layer Stack Diagram (L1 Substrate to L8 Federation) | Introduces the 8-layer stack and one-way interface contracts. |
| **Slide 08** | L3 Destruction Boundary | Concentric Onion Boundary Diagram, 33ms TTL RAM overwrite | Explains why raw face pixels can NEVER reach non-volatile disk. |
| **Slide 09** | Open-Set Biometric Engine | InsightFace ArcFace loss formula, FAISS 512-D vector search | Explains hyperspherical margin separation ($m=0.50$, $s=64$). |
| **Slide 10** | Anonymous Pose & Acoustic Sensing | YOLOv8-pose skeleton diagram, FFT acoustic spectrum graphs | Details identity-free behavior and non-semantic noise tracking. |
| **Slide 11** | ST-CSF Compliance Engine | ST-CSF timetable matching formula, velocity bound ($v_i \le v_{\max}$) | Explains automated truancy detection and teleportation filtering. |
| **Slide 12** | Cryptographic Merkle Audit Ledger | SHA-256 binary hash tree diagram, append-only verification | Demonstrates tamper-evident, non-repudiable audit trails. |
| **Slide 13** | Software Architecture & Tech Stack | Component Architecture Diagram (core, modules, Streamlit, FastAPI) | Maps Python 3.10 stack, PyTorch, FAISS, and OpenCV. |
| **Slide 14** | Multi-Threaded Engine Architecture | Flowchart of 5 concurrent daemon threads with `threading.Lock` | Shows real-time multi-threaded synchronization without queues. |
| **Slide 15** | Hardware & Physical Deployment | Physical Deployment Topology (Jetson Orin Nano, IP cameras, LAN) | Details edge hardware confinement ($\le 2.0\text{GB}$ RAM, $\le 4.5\text{GB}$ VRAM). |
| **Slide 16** | Experimental Setup & EDA | Monte Carlo trajectory split (80% Train, 10% Val, 10% Test) | Describes the 52,203-epoch evaluation dataset. |
| **Slide 17** | Open-Set Identification Results | Accuracy curves (OSIR vs UIRR), threshold scaling $\tau(N)$ | Shows $99.2\%$ OSIR and $99.5\%$ UIRR scaling up to 100k gallery. |
| **Slide 18** | ST-CSF Truancy & Velocity Results | Truancy confusion matrix, false alert reduction bar chart | Demonstrates $98.2\%$ F1-score and $85\%$ false alert reduction. |
| **Slide 19** | Execution Timing & Latency Floor | Pipeline Execution Timing Diagram ($14.5\text{ms}$ vs $33.0\text{ms}$ floor) | Proves real-time 30 FPS capability on edge hardware. |
| **Slide 20** | Hardware Stability & Thermal Profiling | 24-hour thermal curve ($85^\circ\text{C}$ safe mode scaling), flash wear IOPS | Proves edge hardware endurance ($0.02\text{ MB/s}$ write IOPS). |
| **Slide 21** | Summary of Key Contributions | Summary matrix of 7 core system contributions | Re-enforces scientific novelty and systems implementation. |
| **Slide 22** | System Limitations | Transparent discussion of lighting (<50 lux) & occlusion | Demonstrates academic honesty and reviewer awareness. |
| **Slide 23** | Future Directions | LMS integration, INT8 quantization, mobile self-service app | Maps future research extensions post-M.Tech. |
| **Slide 24** | Conclusion | Final takeaway statement, privacy-utility resolution | Concludes that privacy and surveillance utility can co-exist. |
| **Slide 25** | Questions & Discussion | Acknowledgments, Q&A invite, repository & paper DOIs | Opens floor for committee Q&A. |

---

## 2. 21 INDIVIDUAL PAPER PRESENTATION STORYBOARD REGISTRY

| Paper ID | Target Venue | Slide Count | Core Visual Asset | Strategic Oral Anchor |
|---|---|---|---|---|
| **P1** | IEEE TPAMI | 12 Slides | Figure 9.1 (Timing) | Retrospective 100k open-set retrieval & synthesis. |
| **P2** | IEEE TIM | 10 Slides | Figure 5.2 (Component) | Asymmetric multi-modal vector fusion without pixels. |
| **P3** | ACM TOPS | 10 Slides | Figure 7.3 (TTL State) | Pose-only 33ms volatile RAM destruction boundary. |
| **P4** | JSA | 10 Slides | Figure 7.2 (Activity) | Kinematic velocity filtering ($v_i \le v_{\max}$) & logic. |
| **P5** | IEEE Access | 10 Slides | Figure 5.4 (Daemon Map) | Thermal safe mode scaling ($30 \to 15\text{ FPS}$) at $85^\circ\text{C}$. |
| **P6** | IEEE Sensors J. | 10 Slides | Figure 5.2 (Component) | Non-semantic FFT Centroid/ZCR/Flux tracking. |
| **P7** | Computers & Sec. | 12 Slides | Figure 7.2 (Activity) | $98.2\%$ F1 truancy detection & 85% false alert drop. |
| **P8** | IEEE TDSC | 10 Slides | Figure 5.5 (Sequence) | Cryptographic SHA-256 Merkle hash chain ledger. |
| **P9** | ACM TAAS | 10 Slides | Figure 1.2 (Pipeline) | Non-bypassable fail-closed governance gate. |
| **P10** | IEEE IoT-J | 12 Slides | Figure 9.1 (Timing) | 5-daemon thread sync & $32.4\text{ms}$ pipeline latency. |
| **P11** | Middleware Conf | 10 Slides | Figure 5.3 (Deployment) | Systemd daemon isolation & $2.8\text{s}$ cold boot. |
| **P12** | IEEE TNSM | 10 Slides | Figure 5.3 (Deployment) | 7-Role RBAC gateway & $0.02\text{ MB/s}$ flash wear. |
| **P13** | Adaptive Behavior | 10 Slides | Figure 1.1 (Layer Stack) | Intra-campus FedAvg model weight updates. |
| **P14** | IEEE IoT-J | 12 Slides | Figure 1.1 (Layer Stack) | Cross-campus hierarchical H-FedAvg scaling. |
| **P15** | ACM CHI Workshops| 10 Slides | Figure 4.1 (Use Case) | Glassmorphic UI & composite engagement score $E$. |
| **P16** | AI & Society | 10 Slides | Figure 1.1 (Layer Stack) | 3-semester longitudinal user trust & stewardship. |
| **P17** | AI & Society | 12 Slides | Figure 1.3 (Onion) | Structural privacy & canonical `INV-01..15` stack. |
| **P18** | IEEE Systems J. | 12 Slides | Figure 7.3 (TTL State) | 475-fault chaos testing & zero residue proof. |
| **P19** | JCS / ESORICS | 10 Slides | Figure 5.3 (Deployment) | Jetson Orin Nano RAM confinement ($\le 2.0\text{GB}$). |
| **P20** | IEEE TPDS | 10 Slides | Figure 9.1 (Timing) | Dynamic threshold scaling $\tau(N) = \tau_{\text{base}} + \alpha\log N$. |
| **P21** | Formal Aspects Comput.| 12 Slides | Figure 7.2 (Activity) | Timed automata model checking & Hoare logic. |
