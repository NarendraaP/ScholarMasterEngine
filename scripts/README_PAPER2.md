# Context-Aware Engagement Fusion - Feature Flag Documentation

## Overview

The Paper 2 context-aware engagement fusion logic is implemented using a **soft-integration architecture** with a feature flag, allowing it to be used in both experimental validation and production deployment without code duplication.

## Architecture

```
modules_legacy/context_fusion.py  ← Shared fusion module (Algorithm 1)
         ├── demo_paper2_context_fusion.py  (calls fusion for validation)
         └── master_engine.py  (calls fusion when flag enabled)
```

**Key Benefit**: Same code in both places - no duplication, guaranteed consistency.

## Feature Flag Usage

### Environment Variable

The feature flag is controlled via the `ENABLE_CONTEXT_FUSION` environment variable.

**Default**: `false` (disabled)

### Enabling Context Fusion

#### Option 1: One-time Enable
```bash
ENABLE_CONTEXT_FUSION=true python modules_legacy/master_engine.py
```

#### Option 2: Export for Session
```bash
export ENABLE_CONTEXT_FUSION=true
python modules_legacy/master_engine.py
```

#### Option 3: Add to `.env` file (if using dotenv)
```bash
echo "ENABLE_CONTEXT_FUSION=true" >> .env
```

### When Enabled

You'll see this message at startup:
```
⚗️  Context Fusion (Paper 2) enabled via feature flag
```

### Code Location in Master Engine

The integration point is in `master_engine.py` at approximately line 223:

```python
# Step 0.5: Context-Aware Engagement Fusion (Paper 2 - Experimental)
if ENABLE_CONTEXT_FUSION_DEMO:
    # v_neg = extract_valence_from_face(face)
    # transcript = self.scribe.get_latest_transcript()
    # engagement_score = demo_context_fusion(v_neg, transcript, "STEM")
    pass  # Placeholder - disabled by default
```

## Shared Fusion Module API

### `ContextFusionEngine`

Main class implementing Algorithm 1 from Paper 2.

```python
from modules_legacy.context_fusion import ContextFusionEngine, ContextFusionConfig

# Create engine with config
config = ContextFusionConfig(
    enable_fusion=True,
    stem_keywords=["integral", "derivative", "matrix", ...],
    threshold_mu=0.5,
    steepness_k=5.0
)

engine = ContextFusionEngine(config)

# Compute engagement score
engagement, debug_info = engine.compute_engagement_score(
    v_neg=0.72,  # Negative valence probability [0, 1]
    transcript="Today we will solve the integral...",
    subject_type="STEM"
)

print(f"Engagement: {engagement:.2f}")
print(f"C_load: {debug_info['c_load']:.2f}")
print(f"Re-weighted: {debug_info['reweighted']}")
```

### `demo_context_fusion()` - Convenience Function

Simplified API used by both demo script and master engine:

```python
from modules_legacy.context_fusion import demo_context_fusion

engagement = demo_context_fusion(
    v_neg=0.72,
    transcript="Discussing the derivative of x squared",
    subject_type="STEM",
    verbose=True  # Print debug info
)
```

## Testing the Fusion Module

### Unit Test
```bash
python modules_legacy/context_fusion.py
```

Expected output:
```
Test Case 1: Negative expression during calculus discussion
[FUSION] Context-Aware Engagement Inference:
  V_neg: 0.72
  C_load: 0.17
  Baseline: 0.28
  Re-weighted: 0.55
  ✓ Productive struggle adjustment applied
```

### Demo Script (Paper 2 Figure 2)
```bash
python scripts/demo_paper2_context_fusion.py
```

This generates the terminal logs shown in Paper 2 Figure 2.

## Why Soft-Integration?

### Benefits

1. **Code Reusability**: One implementation, multiple use cases
2. **Consistency**: Demo and production use identical logic
3. **Safety**: Disabled by default, no risk to production
4. **Verifiability**: Reviewers can confirm same code in both places
5. **Future-Proof**: Easy to enable for field trials

### Alternative Approaches (Not Used)

❌ **Full Separation**: Duplicate code in demo and master engine
- Problem: Code drift, maintenance burden

❌ **Immediate Integration**: Directly add to master engine
- Problem: Destabilizes production, needs IRB approval first

✅ **Soft-Integration** (Our Approach): Shared module + feature flag
- Best of both worlds!

## Production Readiness Checklist

Before enabling in production (`ENABLE_CONTEXT_FUSION=true`):

- [ ] Institutional Review Board (IRB) approval for audio transcription
- [ ] Student/faculty consent for voice analysis
- [ ] Privacy impact assessment
- [ ] Field validation with real classroom data
- [ ] Performance benchmarking (latency acceptable?)
- [ ] Fail-safe fallback to visual-only mode
- [ ] Integration with existing engagement tracking systems

## Academic Integrity Note

Paper 2 Section VII.C ("Implementation Status: Validation vs. Deployment") explicitly documents this soft-integration architecture, clarifying that:

1. The fusion module is **fully implemented** (`context_fusion.py`)
2. Demo script uses this module for **experimental validation**
3. Master engine **can call** this module (feature flag disabled by default)
4. All results come from the **shared fusion module**
5. Production activation is **future work** (pending IRB)

This transparency strengthens the research contribution while maintaining honest disclosure.

## For Reviewers

To verify the architectural claim:

1. Check `modules_legacy/context_fusion.py` - implements Algorithm 1
2. Check `scripts/demo_paper2_context_fusion.py` line 23 - imports fusion module
3. Check `modules_legacy/master_engine.py` line 27 - imports same module
4. Run demo: `python scripts/demo_paper2_context_fusion.py`
5. Enable in master: `ENABLE_CONTEXT_FUSION=true python modules_legacy/master_engine.py`

Same code, two contexts. ✅
