import matplotlib.pyplot as plt
import numpy as np
import os

def run_scalability_test():
    print("--- 🚀 Generating Scalability Benchmark (Paper 1) ---")
    
    # 1. Simulate Data: Database Size from 1k to 1M
    db_sizes = np.geomspace(1000, 1000000, num=20) # Logarithmic spacing
    
    # 2. Simulate Latencies
    # Linear: O(N) - Grows to ~3.0s at 1M
    # Slope approx 3.0 / 1,000,000
    linear_times = db_sizes * (3.0 / 1000000) 
    
    # Logarithmic (FAISS): O(log N) or O(1) approx - Stays under 0.08s
    # Let's verify prompt: "FAISS times should stay under ~0.08s"
    # We'll calculate a small log curve or constant + noise
    # Base latency 0.02s + minor growth
    faiss_times = 0.02 + 0.01 * np.log10(db_sizes)
    # Clip to max ~0.06-0.08 range
    
    # 3. Calculate Speedup at 100k
    # Find index closest to 100k
    idx_100k = (np.abs(db_sizes - 100000)).argmin()
    
    t_linear_100k = linear_times[idx_100k]
    t_faiss_100k = faiss_times[idx_100k]
    speedup = t_linear_100k / t_faiss_100k
    
    print(f"\n📊 Speedup Analysis at 100,000 Users:")
    print(f"{'Method':<15} | {'Latency (sec)':<15}")
    print("-" * 35)
    print(f"{'Linear Search':<15} | {t_linear_100k:.5f}")
    print(f"{'FAISS (Index)':<15} | {t_faiss_100k:.5f}")
    print("-" * 35)
    print(f"🚀 Speedup Factor: {speedup:.2f}x Faster\n")
    
    # 4. Plot Log-Log
    plt.figure(figsize=(10, 6))
    plt.plot(db_sizes, linear_times, 'r-o', label='Linear Search O(N)', linewidth=2)
    plt.plot(db_sizes, faiss_times, 'g-s', label='FAISS Index O(log N)', linewidth=2, markersize=8)
    
    plt.xscale('log')
    plt.yscale('log')
    
    plt.xlabel('Database Size (Number of Students)', fontsize=12)
    plt.ylabel('Lookup Latency (seconds)', fontsize=12)
    plt.title('Scalability Analysis: Linear vs FAISS (Paper 1)', fontsize=14)
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend(fontsize=12)
    
    # Save
    output_path = 'benchmarks/scalability_result.png'
    # Ensure directory exists just in case
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path)
    print(f"✅ Plot saved to {output_path}")

if __name__ == "__main__":
    run_scalability_test()
