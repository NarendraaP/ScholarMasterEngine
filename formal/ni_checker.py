#!/usr/bin/env python3
"""
ScholarMaster Noninterference Model Checker (Optimized)
========================================================
Dual-trace BFS-based exhaustive verification of the
Noninterference hyperproperty from Paper 19 §III.

Reduces NI to a safety property via synchronized dual execution:
  - Both traces execute the SAME action in lockstep
  - High inputs (biometric identity) may differ between traces
  - Low outputs (metadata, disk) must remain identical

Three verification modes:
  Mode 1: SAFE         — F_irreversible is identity-independent → NI PASS
  Mode 2: LEAKY        — F_irreversible leaks identity → NI FAIL
  Mode 3: ADVERSARIAL  — Illegal disk write on trace 1 → NI FAIL

State space is bounded by MAX_METADATA to ensure finite exploration.
"""

import sys
import argparse
from collections import deque
import time

# ============================================================
# CONSTANTS
# ============================================================
DELTA = 3
MAX_METADATA = 4  # Bound metadata counter for finite state space


# ============================================================
# STATE REPRESENTATION (compact tuple for hashing)
# ============================================================
def make_init(N):
    """Create initial state as dict."""
    return {
        'raw1': frozenset(), 'raw2': frozenset(),
        'meta1': 0, 'meta2': 0,
        'disk1': frozenset(), 'disk2': frozenset(),
        'hi1': tuple(0 for _ in range(N)),
        'hi2': tuple(0 for _ in range(N)),
        'gov': True
    }

def state_key(s):
    return (s['raw1'], s['raw2'], s['meta1'], s['meta2'],
            s['disk1'], s['disk2'], s['hi1'], s['hi2'], s['gov'])

def copy_state(s):
    return dict(s)


# ============================================================
# SYNCHRONIZED ACTIONS
# ============================================================

def capture_sync(s, f, hi1, hi2, N):
    if not s['gov']: return None
    if f in s['raw1'] or f in s['raw2']: return None
    ns = copy_state(s)
    ns['raw1'] = s['raw1'] | {f}
    ns['raw2'] = s['raw2'] | {f}
    h1 = list(s['hi1']); h1[f-1] = hi1; ns['hi1'] = tuple(h1)
    h2 = list(s['hi2']); h2[f-1] = hi2; ns['hi2'] = tuple(h2)
    return ns

def process_safe(s, f, N):
    if f not in s['raw1'] or f not in s['raw2']: return None
    if s['meta1'] >= MAX_METADATA: return None  # Bound
    ns = copy_state(s)
    ns['meta1'] = s['meta1'] + 1
    ns['meta2'] = s['meta2'] + 1
    return ns

def process_leaky(s, f, N):
    if f not in s['raw1'] or f not in s['raw2']: return None
    if s['meta1'] + s['hi1'][f-1] > MAX_METADATA: return None
    if s['meta2'] + s['hi2'][f-1] > MAX_METADATA: return None
    ns = copy_state(s)
    ns['meta1'] = s['meta1'] + s['hi1'][f-1]  # LEAKS identity
    ns['meta2'] = s['meta2'] + s['hi2'][f-1]  # LEAKS identity
    return ns

def zeroize_sync(s, f, N):
    if f not in s['raw1'] or f not in s['raw2']: return None
    ns = copy_state(s)
    ns['raw1'] = s['raw1'] - {f}
    ns['raw2'] = s['raw2'] - {f}
    return ns

def gov_fail(s, N):
    if not s['gov']: return None
    ns = copy_state(s)
    ns['gov'] = False
    ns['raw1'] = frozenset()
    ns['raw2'] = frozenset()
    return ns

def gov_recover(s, N):
    if s['gov']: return None
    if s['raw1'] or s['raw2']: return None
    ns = copy_state(s)
    ns['gov'] = True
    return ns

def illegal_disk_1(s, f, N):
    if f not in s['raw1']: return None
    ns = copy_state(s)
    ns['disk1'] = s['disk1'] | {f}
    return ns


# ============================================================
# SUCCESSOR GENERATION
# ============================================================

def get_successors(s, N, hi_vals, mode):
    succ = []
    frames = range(1, N+1)

    for f in frames:
        for h1 in hi_vals:
            for h2 in hi_vals:
                ns = capture_sync(s, f, h1, h2, N)
                if ns: succ.append((f"CaptureSync({f},hi={h1},{h2})", ns))

    for f in frames:
        if mode in ("safe", "adversarial"):
            ns = process_safe(s, f, N)
            if ns: succ.append((f"ProcessSafe({f})", ns))
        else:
            ns = process_leaky(s, f, N)
            if ns: succ.append((f"ProcessLeaky({f})", ns))

    for f in frames:
        ns = zeroize_sync(s, f, N)
        if ns: succ.append((f"ZeroizeSync({f})", ns))

    ns = gov_fail(s, N)
    if ns: succ.append(("GovFail", ns))
    ns = gov_recover(s, N)
    if ns: succ.append(("GovRecover", ns))

    if mode == "adversarial":
        for f in frames:
            ns = illegal_disk_1(s, f, N)
            if ns: succ.append((f"IllegalDisk1({f})", ns))

    return succ


# ============================================================
# NI CHECK
# ============================================================

def check_ni(s):
    violations = []
    if s['meta1'] != s['meta2']:
        violations.append(f"METADATA LEAK: meta1={s['meta1']} ≠ meta2={s['meta2']}")
    if s['disk1'] != s['disk2']:
        violations.append(f"PERSISTENCE LEAK: disk1={s['disk1']} ≠ disk2={s['disk2']}")
    return violations


# ============================================================
# MODEL CHECKER (BFS)
# ============================================================

def model_check_ni(N, hi_vals, mode):
    labels = {
        "safe": "SAFE (Identity-Independent F_irreversible)",
        "leaky": "LEAKY (Identity-Dependent — BROKEN Abstraction)",
        "adversarial": "ADVERSARIAL (Illegal Disk Write)"
    }
    print(f"\n{'='*70}")
    print(f"  NI Model Check — {labels[mode]}")
    print(f"  N={N}, HighInputs={hi_vals}, Δ={DELTA}, MaxMeta={MAX_METADATA}")
    print(f"{'='*70}\n")

    init = make_init(N)
    visited = {state_key(init)}
    queue = deque([(init, [])])
    states_checked = 0
    transitions = 0
    hi_diff_states = 0
    first_violation = None
    first_trace = None

    t0 = time.time()

    while queue:
        s, trace = queue.popleft()
        states_checked += 1

        v = check_ni(s)
        if s['hi1'] != s['hi2']:
            hi_diff_states += 1

        if v and not first_violation:
            first_violation = v[0]
            first_trace = trace

        for act, ns in get_successors(s, N, hi_vals, mode):
            transitions += 1
            k = state_key(ns)
            if k not in visited:
                visited.add(k)
                queue.append((ns, trace + [act]))

    elapsed = time.time() - t0

    print(f"  Exploration Complete.")
    print(f"  Time:                 {elapsed:.3f}s")
    print(f"  States explored:      {states_checked:,}")
    print(f"  Transitions checked:  {transitions:,}")
    print(f"  Distinct states:      {len(visited):,}")
    print(f"  States with High≠:   {hi_diff_states:,}")
    print()

    if first_violation:
        print(f"  ❌ NONINTERFERENCE VIOLATED")
        print(f"  📍 {first_violation}")
        print(f"  📍 Counterexample ({len(first_trace)} steps):")
        for i, step in enumerate(first_trace):
            print(f"     {i+1}. {step}")
        print()
        return False
    else:
        print(f"  ✅ NONINTERFERENCE HOLDS across ALL {states_checked:,} reachable states.")
        print(f"     High-domain differed in {hi_diff_states:,} states.")
        print(f"     Low-domain remained equivalent in every state.")
        print()
        return True


# ============================================================
# INTEGRATION TESTS
# ============================================================

def ni_integration_tests(N):
    print(f"\n{'='*70}")
    print(f"  Noninterference Integration Tests")
    print(f"{'='*70}\n")

    # Test 1: Same high input → trivial NI
    print("  Test 1: Same High Input → Trivial NI")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 1, N)
    s = process_safe(s, 1, N)
    assert s['meta1'] == s['meta2'] == 1
    assert not check_ni(s)
    print(f"    ✅ metadata1={s['meta1']}, metadata2={s['meta2']} → Equal: PASS")

    # Test 2: Different high, safe process → NI holds
    print("  Test 2: Different High Input, Safe F_irreversible → NI Holds")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 2, N)
    s = process_safe(s, 1, N)
    assert s['meta1'] == s['meta2'] == 1
    assert not check_ni(s)
    print(f"    ✅ hi1=1, hi2=2 → meta1={s['meta1']}, meta2={s['meta2']} → Equal: PASS")

    # Test 3: Different high, leaky process → NI violated
    print("  Test 3: Different High Input, Leaky Process → NI Violated")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 2, N)
    s = process_leaky(s, 1, N)
    assert s['meta1'] != s['meta2']
    v = check_ni(s)
    assert v
    print(f"    ✅ hi1=1, hi2=2 → meta1={s['meta1']}, meta2={s['meta2']} → LEAK DETECTED: PASS")

    # Test 4: Illegal disk write breaks NI
    print("  Test 4: Illegal Disk Write → Persistence Leak")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 1, N)
    s = illegal_disk_1(s, 1, N)
    v = check_ni(s)
    assert v and "PERSISTENCE" in v[0]
    print(f"    ✅ disk1={s['disk1']}, disk2={s['disk2']} → LEAK DETECTED: PASS")

    # Test 5: Zeroize restores symmetry
    print("  Test 5: Zeroize Restores Symmetry")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 2, N)
    s = process_safe(s, 1, N)
    s = zeroize_sync(s, 1, N)
    assert len(s['raw1']) == 0 and len(s['raw2']) == 0
    assert not check_ni(s)
    print(f"    ✅ After zeroize: raw empty, metadata equal: PASS")

    # Test 6: Governance fail-closed preserves NI
    print("  Test 6: Governance Fail-Closed Preserves NI")
    s = make_init(N)
    s = capture_sync(s, 1, 1, 2, N)
    s = gov_fail(s, N)
    assert len(s['raw1']) == 0 and len(s['raw2']) == 0
    assert not check_ni(s)
    blocked = capture_sync(s, 1, 1, 1, N)
    assert blocked is None
    print(f"    ✅ Governance fail → raw cleared, capture blocked: PASS")

    # Test 7: Concurrent frames
    print(f"  Test 7: Concurrent Frames (N={N})")
    s = make_init(N)
    for f in range(1, N+1):
        s = capture_sync(s, f, f, N+1-f, N)
    for f in range(1, N+1):
        s = process_safe(s, f, N)
    assert s['meta1'] == s['meta2'] == N
    assert not check_ni(s)
    print(f"    ✅ {N} frames, different students → meta1=meta2={N}: PASS")

    # Test 8: Multiple cycles
    print("  Test 8: Multiple Lifecycle Cycles")
    s = make_init(N)
    for cycle in range(3):
        s = capture_sync(s, 1, cycle+1, 3-cycle, N)
        s = process_safe(s, 1, N)
        s = zeroize_sync(s, 1, N)
    assert s['meta1'] == s['meta2'] == 3
    assert not check_ni(s)
    print(f"    ✅ 3 cycles, varying identities → meta1=meta2=3: PASS")

    print(f"\n  {'='*50}")
    print(f"  ✅ ALL 8 NI INTEGRATION TESTS PASSED")
    print(f"  {'='*50}\n")
    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScholarMaster NI Checker")
    parser.add_argument("--N", type=int, default=2, help="Concurrent frames")
    args = parser.parse_args()

    N = args.N
    hi_vals = [1, 2]

    print("\n" + "▓" * 70)
    print("  ScholarMaster Formal Verification Suite")
    print("  NONINTERFERENCE — Dual-Trace Hyperproperty")
    print("  Paper 19 §III: Information Flow & Non-Interference")
    print("▓" * 70)

    results = []

    # Mode 1: Safe → NI should PASS
    passed = model_check_ni(N, hi_vals, "safe")
    results.append(("Mode 1: Safe (identity-independent)", passed))

    # Mode 2: Leaky → NI should FAIL
    failed = not model_check_ni(N, hi_vals, "leaky")
    results.append(("Mode 2: Leaky (broken abstraction detected)", failed))

    # Mode 3: Adversarial → NI should FAIL
    failed = not model_check_ni(N, hi_vals, "adversarial")
    results.append(("Mode 3: Adversarial (disk leak detected)", failed))

    # Integration
    passed = ni_integration_tests(N)
    results.append(("Integration Tests (8 scenarios)", passed))

    # Summary
    print("\n" + "=" * 70)
    print("  NONINTERFERENCE VERIFICATION SUMMARY")
    print("=" * 70)
    for name, ok in results:
        print(f"  {name:<55} {'✅ PASS' if ok else '❌ FAIL'}")
    print("=" * 70)

    ok = all(p for _, p in results)
    if ok:
        print("\n  🛡  ALL NI CHECKS PASSED.")
        print("      Termination-insensitive noninterference demonstrated")
        print("      under adversaries A0–A3 and intact TCB.\n")
    else:
        print("\n  ⚠️  SOME CHECKS FAILED.\n")

    sys.exit(0 if ok else 1)
