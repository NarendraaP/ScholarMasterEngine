# ScholarMaster Project Manifest (v1.0 Freeze)

**Project Root:** `/opt/scholarmaster` (Production) or `.` (Development)
**Entry Point:** `src/main.py`

## 📂 Core Modules
| File | Role | Paper |
| :--- | :--- | :--- |
| `main.py` | Unified System Orchestrator | P1, P9 |
| `modules_legacy/st_csf.py` | Spatiotemporal Logic Layer | P4, P7 |
| `modules_legacy/context_fusion.py` | Context-Aware Fusion | P2 |
| `modules_legacy/trust_layer.py` | Immutable Audit Log | P8 |
| `infrastructure/acoustic/anomaly_detector.py` | Acoustic Sentinel | P6 |

## 🛠️ Deployment & Tools
| File | Role | Paper |
| :--- | :--- | :--- |
| `scripts/deploy/install_service.sh` | Systemd Installer Script | P11 |
| `config/systemd/scholarmaster.service` | Systemd Unit File | P11 |
| `benchmarks/uptime_monitor.py` | Stability Telemetry | P11 |
| `tools/feedback_server.py` | Ground Truth Collection | P11 |

## 📊 Verification & Audit
| File | Role | Status |
| :--- | :--- | :--- |
| `MASTER_AUDIT_VERDICT.md` | Executive Summary of System Audit | ✅ Ready |
| `paper4_audit_report.md` | Audit of Schedule Adherence Logic | ✅ Ready |
| `paper2_audit_report.md` | Audit of Context Fusion Logic | ✅ Ready |
| `paper3_audit_report.md` | Audit of Privacy Architecture | ✅ Ready |
| `docs/papers/*.tex` | Source LaTeX for Papers 1-11 | ✅ Drafted |

## ⚠️ Notes for Reviewers
1.  **Legacy Folder:** `modules_legacy/` contains the working implementations of P1-P5 code.
2.  **Deprecated:** Older experiments (`main_event_driven.py`, etc.) are archived in `deprecated/`.
3.  **Data:** Logs are stored in `data/`.
