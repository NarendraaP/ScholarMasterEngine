import sys

def calc_lifespan(daily_writes_gb: float, waf: float, capacity_gb: float, pe_cycles: int) -> float:
    """
    Paper 12: Eq (1) Lifespan Model
    L = (Capacity * Cycles) / (Daily_Writes * WAF * 365)
    """
    total_endurance_gb = capacity_gb * pe_cycles
    daily_wear_gb = daily_writes_gb * waf
    days_to_failure = total_endurance_gb / daily_wear_gb
    return days_to_failure / 365.0

def run_endurance_simulation():
    print("="*80)
    print("Paper 12: SD Card Lifespan Projection Model")
    print("="*80)
    
    # 32GB Samsung EVO+
    CAPACITY = 32.0 
    
    # 1. Baseline Scenario (Naive Ext4 + CFQ + No ZRAM)
    # 4.2GB daily writes, WAF=12.43 (from Table II/IV)
    bw_v = 4.2
    bw_waf = 12.43
    mlc_cycles = 3000
    
    base_lifespan = calc_lifespan(bw_v, bw_waf, CAPACITY, mlc_cycles)
    
    print(f"[BASELINE] Ext4 + CFQ + Default Page Cache (MLC - 3000 P/E)")
    print(f"  -> Daily Writes: {bw_v} GB")
    print(f"  -> WAF: {bw_waf}")
    print(f"  -> Projected Lifespan: {base_lifespan:.2f} years ({base_lifespan*12:.1f} months)\n")
    
    # 2. Optimized Scenario (F2FS + NOOP + ZRAM + PageCache Tuning)
    # 0.8GB daily writes, WAF=2.1 (from Table IV/V)
    opt_v = 0.8
    opt_waf = 2.1
    
    opt_lifespan_mlc = calc_lifespan(opt_v, opt_waf, CAPACITY, mlc_cycles)
    
    print(f"[OPTIMIZED] F2FS + NOOP + ZRAM (MLC - 3000 P/E)")
    print(f"  -> Daily Writes: {opt_v} GB")
    print(f"  -> WAF: {opt_waf}")
    print(f"  -> Projected Lifespan: {opt_lifespan_mlc:.2f} years ({opt_lifespan_mlc*12:.1f} months)")
    print(f"  -> Improvement Factor: {opt_lifespan_mlc/base_lifespan:.1f}x\n")
    
    # 3. Pessimistic TLC Scenario
    tlc_cycles = 2000
    opt_lifespan_tlc = calc_lifespan(opt_v, opt_waf, CAPACITY, tlc_cycles)
    
    print(f"[STRESS TEST] F2FS + NOOP + ZRAM (TLC Pessimistic - 2000 P/E)")
    print(f"  -> Projected Lifespan: {opt_lifespan_tlc:.2f} years ({opt_lifespan_tlc*12:.1f} months)")
    if opt_lifespan_tlc > 3.0:
        print("  -> EVALUATION: PASS (Exceeds 3-year hardware refresh cycle)")
    else:
        print("  -> EVALUATION: FAIL (Sub-3 year replacement required)")
        
    print("="*80)

if __name__ == "__main__":
    run_endurance_simulation()
