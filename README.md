# 🎓 ScholarMaster Research Series

**Edge-Native Privacy-Preserving Smart Campus Intelligence**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Papers](https://img.shields.io/badge/research-9%20papers-green.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-Edge%20First-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> A comprehensive research platform demonstrating the integration of biometric identification, privacy-preserving analytics, and immutable audit trails for institutional-scale deployments.

---

## 📄 Research Contributions

This repository implements the complete **ScholarMaster Research Series** (Papers 1-9), addressing the "Deployment Gap" between algorithmic SOTA and institutional reality.

### Core Papers

| Paper | Title | Key Contribution |
|:---:|---|---|
| **1** | Scalable Biometric Identification using HNSW | Sub-logarithmic search at N=100k identities |
| **2** | Context-Aware Engagement Analysis | Multi-modal false negative reduction |
| **3** | Privacy-Preserving Pose Heuristics | Zero-retention volatile memory processing |
| **4** | Schedule Compliance via ST-CSF | Spatiotemporal constraint satisfaction |
| **5** | UMA Thermal Benchmarking | Unified memory vs discrete GPU analysis |
| **6** | Acoustic Anomaly Detection | Spectral gating for privacy-first audio |
| **7** | Rule-Based Spatiotemporal Reasoning | Prolog-style academic logic engine |
| **8** | Cryptographic Provenance | Merkle-DAG + GDPR crypto-shredding |
| **9** | System-Level Adversarial Validation | **Capstone integration & Pareto analysis** |

**Full Paper PDFs**: See `docs/papers/` (Post-publication)

---

## 🏗️ System Architecture

### Three-Tier Design

```
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECTURE C: "Unified" (main_unified.py) - SOTA         │
│  │                                                           │
│  ├─ Sensing: InsightFace + HNSW (Paper 1) + FFT (Paper 6) │
│  ├─ Logic: ST-CSF Compliance (Paper 4, 7)                  │
│  ├─ Privacy: Pose-Only Engagement (Paper 3)                │
│  ├─ Audit: Merkle DAG + ZKP (Paper 8)                      │
│  └─ Infrastructure: Power Profiling (Paper 5)              │
└─────────────────────────────────────────────────────────────┘
          ▲
          │ Pareto-Dominant (Speed + Privacy + Trust)
          │
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECTURE B: "Naive Edge" (main_integrated_system.py)   │
│  - Baseline: Haar + SQLite + Linear Search                 │
│  - Purpose: Comparative failure analysis (Paper 9)          │
└─────────────────────────────────────────────────────────────┘
          ▲
          │
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECTURE A: "Legacy" (main.py)                         │
│  - Multi-camera orchestration (V1 system)                   │
│  - Status: Reference implementation                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### System Requirements
- **Hardware**: Apple M2+ / Intel i7+ / NVIDIA GPU (CUDA 11.8+)
- **Memory**: 16GB RAM (recommended for 100k gallery)
- **Python**: 3.12+
- **OS**: macOS / Linux / Windows (WSL2)

### Installation

```bash
# Clone repository
git clone https://github.com/NarendraaP/ScholarMasterEngine.git
cd ScholarMasterEngine

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models (InsightFace, YOLOv8-Pose)
python scripts/download_models.py
```

### Running the SOTA System

```bash
# Option 1: Unified SOTA System (Paper 9)
python main_unified.py

# Option 2: Admin Dashboard (Streamlit UI)
streamlit run admin_panel.py

# Option 3: REST API Server
python -m api.main
# Visit: http://localhost:8000/docs
```

---

## 📊 Performance Benchmarks

### Comparative Analysis (Paper 9)

| Architecture | Latency (ms) | Accuracy | Privacy | Thermal Stability |
|---|:---:|:---:|:---:|:---:|
| **Cloud (AWS Rekognition)** | 450 ± 120 | 99.5% (closed-set) | ❌ Transmission | N/A |
| **Naive Edge (Arch B)** | 55 ± 2 | 92.1% (closed-set) | ❌ SQL Logs | 85°C @ 14min |
| **Unified (Arch C)** | **28 ± 1.2** | **99.82% (open-set, 20% unknown)** | ✅ Volatile | **62°C stable** |

**Target Metrics** (Apple M2, N=100k):
- End-to-End Latency: **28ms** (33 FPS sustained)
- Open-Set Identification Rate (OSIR): **99.82%**
- Unknown Rejection Rate (UIRR): **99.91%**
- Merkle Root Computation: **<100ms** per 100 events

**See**: `benchmarks/` for full stress test results.

---

## 🔬 Research Validation

### Reproducing Paper Results

Each paper has a corresponding validation script:

```bash
# Paper 1: HNSW Scalability Test
python benchmarks/benchmark_face_recognition.py --gallery_size 100000

# Paper 3: Privacy Metrics (Zero Retention)
python benchmarks/test_secure_memory.py

# Paper 5: Thermal Profiling
python scripts/power_profiler.sh --duration 3600

# Paper 6: Acoustic SNR Analysis
python benchmarks/test_audio_snr.py

# Paper 8: Blockchain Integrity Audit
python benchmarks/test_merkle_performance.py

# Paper 9: Full System Stress Test
python benchmarks/stress_test.py --duration 3600
```

---

## 🔐 Privacy & Security Features

### Zero-Knowledge Implementations

1. **Volatile Memory Processing** (Paper 3)
   - Frame data wiped via `secure_wipe()` after vectorization
   - No persistent visual storage

2. **Cryptographic Shredding** (Paper 8)
   - GDPR "Right to be Forgotten" via key destruction
   - `KeyManagementService` prototype in `main_unified.py`

3. **Zero-Knowledge Proofs** (Paper 8)
   - Fiat-Shamir NIZK for attendance verification
   - `ZeroKnowledgeProver` class demonstrates protocol

4. **STFT Spectral Gating** (Paper 6)
   - Privacy-preserving audio analysis
   - Human voice isolation without speech recognition

---

## 📁 Repository Structure

```
ScholarMasterEngine/
├── main_unified.py           # 🌟 SOTA integrated system (Papers 1-9)
├── main_integrated_system.py # Baseline comparison (Paper 9)
├── main.py                   # Legacy multi-camera system
│
├── modules_legacy/           # Core modules for all architectures
│   ├── face_registry.py      # InsightFace + HNSW (Paper 1)
│   ├── privacy_analytics.py  # Pose-only engagement (Paper 3)
│   ├── audio_sentinel.py     # FFT spectral analysis (Paper 6)
│   ├── scheduler.py          # ST-CSF logic (Paper 4, 7)
│   ├── context_manager.py    # Compliance engine (Paper 7)
│   └── safety_rules.py       # Violence/sleep detection
│
├── chaincode/                # Hyperledger Fabric smart contract (Paper 8)
│   └── smart_contract.go     # Attendance asset management
│
├── benchmarks/               # Performance validation scripts
├── scripts/                  # Utilities & profiling tools
├── docs/                     # Architecture documentation
│   └── papers/               # Research papers (post-publication)
│
├── domain/                   # Clean Architecture (DDD)
├── application/              # Use cases layer
├── infrastructure/           # Adapters (FAISS, InsightFace, etc.)
├── di/                       # Dependency injection
└── api/                      # RESTful API (FastAPI)
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Specific modules
pytest tests/test_face_recognition.py -v
pytest tests/test_privacy_analytics.py -v
pytest tests/test_blockchain.py -v

# With coverage
pytest --cov=modules_legacy --cov=domain --cov-report=html
```

### Integration Tests

```bash
# Full system integration (60 seconds)
python tests/integration/test_full_system.py

# Multi-threaded stress test
python tests/integration/test_concurrency.py
```

---

## 🎯 Key Technical Highlights

### Innovation Points

✅ One of the **first** system-level adversarial stress tests at institutional scale (N=100k, 30 FPS)  
✅ Demonstrates **Pareto-dominant** privacy + speed + trust architecture  
✅ Novel **GDPR-compliant blockchain** implementation via crypto-shredding  
✅ Comprehensive **cross-layer failure mode** exposition (Paper 9)

### Engineering Excellence

- **Clean Architecture** with Domain-Driven Design (DDD)
- **SOLID Principles** throughout codebase
- **Dependency Injection** via custom container
- **Type Safety** with Python 3.12+ type hints
- **Atomic Operations** via RCU pattern (attendance logging)

---

## 📚 Documentation

### Primary Documents

- **System Architecture**: [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md)
- **API Reference**: `http://localhost:8000/docs` (when running API)
- **Audit Reports**: `.gemini/antigravity/brain/*/` (adversarial validation logs)
- **Contributing Guide**: [`CONTRIBUTING.md`](CONTRIBUTING.md)

### Research Artifacts

Each paper includes:
- LaTeX source (post-publication)
- Adversarial audit report (validation against SOTA)
- Implementation checklist (code alignment proof)

---

## 🔌 API Usage Examples

### REST API (FastAPI)

```bash
# Start API server
python -m api.main

# Register student
curl -X POST "http://localhost:8000/api/students/register" \
  -F "image=@student_photo.jpg" \
  -F "student_id=CS2024001" \
  -F "name=John Doe"

# Recognize face
curl -X POST "http://localhost:8000/api/students/recognize" \
  -F "image=@query_face.jpg"

# Mark attendance (with context)
curl -X POST "http://localhost:8000/api/attendance/mark" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "CS2024001",
    "subject": "Data Structures",
    "room": "Lab-101"
  }'
```

### Python SDK

```python
from di.container import get_container

# Get dependency injection container
container = get_container()

# Use case: Register student
success, message = container.register_student.execute(
    image=face_img,
    student_id="CS2024001",
    name="John Doe",
    department="Computer Science",
    program="UG",
    year=2,
    section="A"
)

# Use case: Recognize student
student_id, confidence = container.face_recognizer.recognize(query_img)
print(f"Recognized: {student_id} (confidence: {confidence:.2f})")
```

---

## 🛠️ Development

### Adding New Features

Following Clean Architecture principles:

1. **Define Domain Interface**: `domain/interfaces/i_new_feature.py`
2. **Create Use Case**: `application/use_cases/new_feature_use_case.py`
3. **Implement Adapter**: `infrastructure/adapters/new_feature_adapter.py`
4. **Wire Dependencies**: Update `di/container.py`
5. **Add Tests**: `tests/test_new_feature.py`
6. **Document**: Update relevant `docs/` files

### Code Quality Standards

- **Linting**: `flake8 .` (PEP 8 compliance)
- **Type Checking**: `mypy modules_legacy/ domain/ application/`
- **Test Coverage**: Minimum 85% for new code
- **Documentation**: Docstrings for all public APIs

---

## 🌐 Deployment

### Production Checklist

- [ ] Configure environment variables (`.env` from `.env.example`)
- [ ] Set up SSL certificates for API
- [ ] Configure role-based access control (RBAC)
- [ ] Initialize FAISS index with production gallery
- [ ] Set up external logging (e.g., ELK stack)
- [ ] Configure backup strategy for attendance logs
- [ ] Test disaster recovery procedures

### Docker Deployment (Optional)

```bash
# Build image
docker build -t scholarmaster:latest .

# Run container
docker run -d \
  -p 8501:8501 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  scholarmaster:latest
```

---

## 👥 Authors & Acknowledgments

**Principal Investigator**  
Narendra Babu P - Department of Computer Science, Swarnandhra College of Engineering and Technology

**Acknowledgments**
- InsightFace (Jiankang Deng et al.) for face recognition models
- Ultralytics for YOLOv8-Pose
- Hyperledger Fabric for blockchain framework
- FastAPI & Streamlit communities

---

## 📄 License

This project is licensed under the MIT License - see [`LICENSE`](LICENSE) file for details.

**Citation** (Post-publication):
```bibtex
@misc{narendra2026scholarmaster,
  author = {Narendra Babu P},
  title = {ScholarMaster: Edge-Native Privacy-Preserving Smart Campus Intelligence},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/NarendraaP/ScholarMasterEngine}
}
```

---

## 🚦 Project Status

✅ **Research Complete** - All 9 papers validated & code-aligned  
✅ **Deployment-Ready Reference Implementation** - SOTA design passes adversarial stress tests  
✅ **Open Source** - MIT licensed, contributions welcome

**Last Updated**: January 2026  
**Version**: 1.0.0 (Gold Master)

---

**For questions or collaboration**: Contact via GitHub Issues or [email@domain.com]
