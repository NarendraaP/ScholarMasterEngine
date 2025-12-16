import matplotlib.pyplot as plt
import numpy as np

def generate_benchmark_figure():
    # Data
    backends = ['CPU\n(ONNX Runtime)', 'GPU\n(Metal/MPS)', 'Neural Engine\n(CoreML)']
    fps_values = [5.2, 28.6, 33.1]
    colors = ['#7f8c8d', '#2980b9', '#8e44ad'] # Grey, Blue, Purple
    
    # Setup Figure (Professional Style)
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    # Create Bars
    bars = ax.bar(backends, fps_values, color=colors, width=0.6)
    
    # Add Value Labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height} FPS',
                ha='center', va='bottom', fontsize=12, fontweight='bold', color='black')
        
    # Styling
    ax.set_title("Hardware Acceleration Benchmarks (ScholarMaster Pipeline)", fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel("Throughput (Frames Per Second)", fontsize=12)
    ax.set_ylim(0, 40) # Add some headroom
    
    # Grid tweaks
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(False)
    
    # Add annotation for improvement
    improvement = fps_values[2] / fps_values[0]
    ax.text(1.3, 35, f"CoreML is {improvement:.1f}x Faster than CPU", 
            fontsize=12, fontweight='bold', color='#8e44ad',
            bbox=dict(facecolor='white', edgecolor='#8e44ad', boxstyle='round,pad=0.5'))

    # Save
    output_path = 'benchmarks/Fig_Benchmark.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    generate_benchmark_figure()
