import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_truancy_figure():
    # 16:9 Aspect Ratio (approx 1920x1080 if dpi=120)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    
    # Black background simulating dark/CCTV feed
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis('off')

    # --- Draw Stick Figure (Cyan) ---
    # Center approx (960, 540)
    center_x, center_y = 960, 540
    
    # Head
    head = patches.Circle((center_x, center_y + 150), 50, color='cyan', fill=True)
    ax.add_patch(head)
    
    # Body
    ax.plot([center_x, center_x], [center_y + 100, center_y - 100], color='cyan', linewidth=5)
    
    # Arms
    ax.plot([center_x - 100, center_x + 100], [center_y + 50, center_y + 50], color='cyan', linewidth=5)
    
    # Legs
    ax.plot([center_x, center_x - 70], [center_y - 100, center_y - 300], color='cyan', linewidth=5)
    ax.plot([center_x, center_x + 70], [center_y - 100, center_y - 300], color='cyan', linewidth=5)

    # --- Red Bounding Box ---
    # x, y (bottom-left), width, height
    rect_x = center_x - 150
    rect_y = center_y - 320
    rect_w = 300
    rect_h = 550
    
    bbox = patches.Rectangle((rect_x, rect_y), rect_w, rect_h, linewidth=4, edgecolor='red', facecolor='none')
    ax.add_patch(bbox)
    
    # --- Box Label ---
    ax.text(rect_x, rect_y + rect_h + 10, 'ALERT: TRUANCY (ID: 9402)', 
            color='white', fontsize=14, fontweight='bold', 
            bbox=dict(facecolor='red', edgecolor='red', alpha=0.8))

    # --- Overlays ---
    # Top Left
    ax.text(50, 1030, 'CAM_04: CANTEEN | LIVE FEED', 
            color='#00ff00', fontsize=20, fontfamily='monospace', fontweight='bold')
    
    # Bottom Right
    ax.text(1400, 50, 'SCHEDULE CONFLICT: MATH-302', 
            color='red', fontsize=24, fontfamily='monospace', fontweight='bold',
            bbox=dict(facecolor='black', edgecolor='red', linewidth=2))

    # Save
    output_path = 'benchmarks/Fig_Truancy.png'
    plt.savefig(output_path, dpi=120, bbox_inches='tight', facecolor='black')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    generate_truancy_figure()
