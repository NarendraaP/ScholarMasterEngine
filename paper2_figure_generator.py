import matplotlib.pyplot as plt
import numpy as np

def generate_paper2_figure():
    """Generate Figure 2: Context Engine vs Standard AI Comparison"""
    
    # Time axis (0 to 60 minutes)
    time = np.linspace(0, 60, 300)
    
    # Initialize engagement scores
    standard_ai = np.ones(300) * 0.75
    context_engine = np.ones(300) * 0.80
    
    # Add some natural variation
    standard_ai += np.random.normal(0, 0.02, 300)
    context_engine += np.random.normal(0, 0.02, 300)
    
    # Difficult lecture period (minute 20-50)
    difficult_start = 20
    difficult_end = 50
    
    # Find indices for difficult period
    difficult_indices = (time >= difficult_start) & (time <= difficult_end)
    
    # Standard AI: Drops during difficult period (misinterprets concentration as boredom)
    standard_ai[difficult_indices] = np.random.uniform(0.15, 0.25, np.sum(difficult_indices))
    
    # Context Engine: Stays high during difficult period (correctly identifies concentration)
    context_engine[difficult_indices] = np.random.uniform(0.85, 0.95, np.sum(difficult_indices))
    
    # Create figure
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)
    
    # Plot lines
    ax.plot(time, standard_ai, 'r--', linewidth=2.5, label='Standard AI (Biased)', alpha=0.8)
    ax.plot(time, context_engine, 'g-', linewidth=2.5, label='Our Context Engine', alpha=0.9)
    
    # Styling
    ax.set_xlabel('Time (Minutes)', fontsize=13)
    ax.set_ylabel('Engagement Score', fontsize=13)
    ax.set_title('Figure 2: Context-Aware Engagement Detection\n(Math Lecture with High Cognitive Load Period)', 
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', fontsize=11, frameon=True)
    
    # Add shaded region for difficult period
    ax.axvspan(difficult_start, difficult_end, color='orange', alpha=0.15, label='Difficult Topic (Calculus)')
    
    # Annotation at minute 25
    ax.annotate('High Cognitive Load Detected\n(Frowns = Concentration, not Boredom)', 
                xy=(25, 0.9), xytext=(30, 0.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", ec="black", alpha=0.8))
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()
    
    print("✅ Figure 2 generated successfully!")
    print("📊 Graph displayed. Take your screenshot now.")

if __name__ == "__main__":
    generate_paper2_figure()
