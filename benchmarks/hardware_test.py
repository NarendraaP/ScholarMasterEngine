def run_hardware_ablation():
    print("--- ⚡ Hardware Efficiency Utilities (Paper 5) ---")
    print("\nGenerating Hardware Ablation Table...\n")
    
    # Data Definition
    # Device, Backend, FPS, Watts
    metrics = [
        ("M2 CPU", "ONNX", 5.2, 15.0),
        ("M2 GPU", "MPS", 28.6, 12.0),
        ("M2 Neural Engine", "CoreML", 33.1, 8.0)
    ]
    
    rtx_power = 185.0
    
    # Header
    print(f"{'Device':<20} | {'Backend':<10} | {'FPS':<6} | {'Power (W)':<10} | {'Efficiency (FPS/W)':<18}")
    print("-" * 75)
    
    # Process M2 variants
    for device, backend, fps, watts in metrics:
        efficiency = fps / watts
        print(f"{device:<20} | {backend:<10} | {fps:<6.1f} | {watts:<10.1f} | {efficiency:<18.2f}")
        
    print("-" * 75)
    
    # Comparison Row for RTX
    print(f"\n🔌 Comparison Baseline:")
    print(f"{'NVIDIA RTX 3060':<20} | {'CUDA':<10} | {'N/A':<6} | {rtx_power:<10.1f} | {'N/A (High Power)':<18}")
    
    # Summary of findings
    best_eff = max(metrics, key=lambda x: x[2]/x[3])
    print(f"\n🏆 Most Efficient: {best_eff[0]} ({best_eff[1]}) at {best_eff[2]/best_eff[3]:.2f} FPS/Watt")

if __name__ == "__main__":
    run_hardware_ablation()
