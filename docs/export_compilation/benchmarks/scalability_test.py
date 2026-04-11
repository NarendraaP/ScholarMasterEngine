import time
import numpy as np
import faiss
import csv
import matplotlib.pyplot as plt
import os

def run_scalability_test():
    print("="*60)
    print("📈 Paper 1: Scalability Benchmark (Linear vs FAISS)")
    print("="*60)
    
    # Setup
    sizes = [100, 1000, 10000, 100000]
    dimension = 512
    results = []
    
    # Ensure output dir exists
    os.makedirs("benchmarks", exist_ok=True)
    
    print(f"{'N':<10} | {'Linear (s)':<15} | {'FAISS (s)':<15} | {'Speedup':<10}")
    print("-" * 60)
    
    for N in sizes:
        # Generate random vectors
        # Database: N vectors
        # Query: 1 vector
        db_vectors = np.random.random((N, dimension)).astype('float32')
        query_vector = np.random.random((1, dimension)).astype('float32')
        
        # --- 1. Linear Search (Brute Force) ---
        start_linear = time.time()
        
        # Simple Euclidean distance calculation for finding nearest neighbor
        # dist = ||a - b||^2
        min_dist = float('inf')
        nearest_idx = -1
        
        for i in range(N):
            diff = db_vectors[i] - query_vector[0]
            dist = np.dot(diff, diff)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
                
        end_linear = time.time()
        linear_time = end_linear - start_linear
        
        # --- 2. FAISS Search ---
        # Build Index
        start_faiss_build = time.time()
        index = faiss.IndexFlatL2(dimension)
        index.add(db_vectors)
        # Search
        D, I = index.search(query_vector, 1)
        end_faiss = time.time()
        
        # We count search time primarily, but for fair comparison with "system latency",
        # usually we care about the search part. However, linear search above didn't have "build" time.
        # But FAISS IndexFlatL2 is also brute force, just optimized C++.
        # Let's measure just the search time for FAISS to be comparable to the loop above?
        # Actually, the loop above is Python loop (very slow). 
        # A numpy vectorized linear search would be faster.
        # But the prompt asks for "Linear Search: Loop through array".
        # So we stick to the explicit loop or a simple numpy implementation.
        # Let's use the explicit loop as requested to show the "Naive" vs "Optimized" contrast often used in papers.
        # Or better, let's use a numpy vectorized approach for "Linear" to be a stronger baseline?
        # "Loop through array" implies explicit loop. I will stick to that to demonstrate the massive speedup.
        
        # FAISS Time: We'll count just the search time, as indexing is pre-computed in real systems.
        start_faiss_search = time.time()
        D, I = index.search(query_vector, 1)
        end_faiss_search = time.time()
        faiss_time = end_faiss_search - start_faiss_search
        
        # Avoid division by zero
        if faiss_time == 0: faiss_time = 1e-9
        
        speedup = linear_time / faiss_time
        
        print(f"{N:<10} | {linear_time:<15.6f} | {faiss_time:<15.6f} | {speedup:<10.1f}x")
        
        results.append({
            "N": N,
            "Linear Time (s)": linear_time,
            "FAISS Time (s)": faiss_time,
            "Speedup": speedup
        })
        
    print("-" * 60)
    
    # --- Save Results to CSV ---
    csv_file = "benchmarks/results_scalability.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["N", "Linear Time (s)", "FAISS Time (s)", "Speedup"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results saved to {csv_file}")
    
    # --- Generate Chart ---
    try:
        N_values = [r["N"] for r in results]
        linear_times = [r["Linear Time (s)"] for r in results]
        faiss_times = [r["FAISS Time (s)"] for r in results]
        
        plt.figure(figsize=(10, 6))
        plt.plot(N_values, linear_times, marker='o', label='Linear Search (Python Loop)', linestyle='--')
        plt.plot(N_values, faiss_times, marker='s', label='FAISS Optimized Search', linewidth=2)
        
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Database Size (N)')
        plt.ylabel('Search Time (seconds)')
        plt.title('Scalability: Linear Search vs FAISS (Log-Log Scale)')
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.legend()
        
        chart_file = "benchmarks/scalability_chart.png"
        plt.savefig(chart_file)
        print(f"✅ Chart saved to {chart_file}")
        
    except Exception as e:
        print(f"❌ Failed to generate chart: {e}")

if __name__ == "__main__":
    run_scalability_test()
