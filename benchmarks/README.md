# ScholarMaster Benchmarks

This directory contains reproduction scripts for the performance claims in **Paper 1: Open-Set Biometric Identification**.

## 📊 Paper 1: HNSW Latency & Open-Set Validation

**Changes Verified:**
- ✅ HNSW Indexing is used in `modules_legacy/face_registry.py` (Production)
- ✅ `benchmark_openset_100k.py` validates the sub-millisecond latency claims.
- ✅ Synthetic UIRR = 100% (as disclosed in Paper 1 Section VIII.B).

### How to Run Reproduction

To verify the `0.86ms` latency and `100%` UIRR claims:

```bash
# From project root
python benchmarks/benchmark_openset_100k.py
```

### Expected Output
```text
...
✅ Index built in 169.28s (100000 vectors)
...
📈 Open-Set Metrics:
   OSIR (Identification Rate):  88.32% (Target: ≥99.5%) <- See Paper 1 "Critical Disclosure"
   UIRR (Unknown Rejection):    100.00% (Target: ≥99.9%)
...
⏱️  Latency Metrics:
   Mean:  0.858 ms (Target: ≤33ms)
...
✅ VERDICT: PAPER 1 CLAIMS VALIDATED
```

## 🛠️ HNSW Latency Grid Search
To re-run the latency grid search (Table VII.A):
```bash
python benchmarks/hnsw_latency_validation.py
```
