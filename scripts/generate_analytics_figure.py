import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def generate_figure():
    # Set style for professional/academic look
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create figure with GridSpec
    fig = plt.figure(figsize=(14, 10), dpi=300)
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])

    # --- Top Panel: Time-Series Graph ---
    ax1 = fig.add_subplot(gs[0, :])
    
    minutes = np.linspace(0, 60, 200)
    
    # Generate Synthetic Data
    # Base levels
    raw_sadness = np.random.normal(25, 3, 200)
    true_engagement = np.random.normal(60, 5, 200)
    
    # Spike between min 20-45 (Indices approx 66 to 150)
    spike_indices = (minutes >= 20) & (minutes <= 45)
    
    # Raw Visual Sadness spikes high (frowns)
    raw_sadness[spike_indices] = np.random.normal(85, 2, np.sum(spike_indices))
    
    # True Engagement stays high (concentration)
    true_engagement[spike_indices] = np.random.normal(90, 2, np.sum(spike_indices))
    
    # Plotting
    ax1.plot(minutes, raw_sadness, color='#e74c3c', linewidth=2.5, label='Raw Visual Sadness')
    ax1.plot(minutes, true_engagement, color='#2ecc71', linewidth=2.5, label='Context-Corrected Engagement')
    
    # Styling Top Panel
    ax1.set_title("Temporal Fusion: Correcting False Boredom Flags via Schedule Logic", fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel("Time (Minutes)", fontsize=12)
    ax1.set_ylabel("Intensity Score (0-100)", fontsize=12)
    ax1.set_xlim(0, 60)
    ax1.set_ylim(0, 100)
    ax1.legend(loc='upper right', frameon=True, fontsize=11)
    
    # Annotation
    ax1.annotate('Logic Correction:\nFrown = Concentration', 
                 xy=(30, 85), xytext=(35, 60),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=12, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9))
    
    # Shade the region
    ax1.axvspan(20, 45, color='gray', alpha=0.1, label='Difficult Proof Segment')


    # --- Bottom Left Panel: Bar Chart ---
    ax2 = fig.add_subplot(gs[1, 0])
    
    categories = ['Calculus', 'History', 'Physics', 'Literature']
    x = np.arange(len(categories))
    width = 0.35
    
    # Data
    visual_false_positives = [85, 20, 82, 15] # High for STEM (hard subjects cause frowns)
    cognitive_load = [90, 85, 88, 80]         # High for all (students are learning)
    
    rects1 = ax2.bar(x - width/2, visual_false_positives, width, label='Visual False Positives', color='#e74c3c')
    rects2 = ax2.bar(x + width/2, cognitive_load, width, label='Cognitive Load', color='#3498db')
    
    # Styling Bottom Left
    ax2.set_ylabel('Score', fontsize=12)
    ax2.set_title('Subject Comparison: Visual Bias vs True Load', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=11)
    ax2.legend(fontsize=10)
    ax2.set_ylim(0, 110)


    # --- Bottom Right Panel: Terminal/Log View ---
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Remove axes for terminal look
    ax3.set_axis_off()
    
    # Draw dark background
    ax3.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax3.transAxes, color='#1e1e1e', zorder=0))
    
    log_text = (
        "> [SYSTEM_INIT] Audio Scribe Module Loaded...\n"
        "> [STREAM_01] Connecting to mic_array_4...\n"
        "> [20:15:33] LISTENING...\n"
        "----------------------------------------\n"
        "> [DETECTED_PHRASE] Confidence: 0.99\n"
        "  \"...calculating the EIGENVECTOR of the...\"\n"
        "\n"
        "> [DETECTED_PHRASE] Confidence: 0.96\n"
        "  \"...take the partial DERIVATIVE with...\"\n"
        "----------------------------------------\n"
        "> [SENTIMENT_ANALYSIS] Neutral/Academic\n"
        "> [CONTEXT_QUERY] Schedule: 'MATH_402'\n"
        "\n"
        "> [DECISION_LOGIC]\n"
        "  VISUAL_EMOTION: 'Negative' (Frown)\n"
        "  AUDIO_CONTEXT: 'High Complexity'\n"
        "  >>> OVERRIDE APPLIED <<<\n"
        "\n"
        "> STATUS: CONTEXT_INFERENCE: HIGH_COGNITIVE_LOAD"
    )
    
    # Add text
    ax3.text(0.05, 0.95, log_text, transform=ax3.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace', color='#00ff00', weight='bold')
    
    ax3.set_title("Live System Logs (Simulated)", fontsize=14, fontweight='bold', color='black', pad=10)

    
    # Final Adjustments
    plt.tight_layout()
    
    # Save
    output_path = 'benchmarks/Fig_Analytics.png'
    plt.savefig(output_path, dpi=300)
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    generate_figure()
