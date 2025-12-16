import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_hand_raise_figure():
    # 4:3 Aspect Ratio (Computer Vision Standard)
    fig, ax = plt.subplots(figsize=(12, 9), dpi=120)
    
    # Black background simulating Debug/Vector feed
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 900)
    ax.axis('off')

    # --- Draw Stick Figure (Cyan) ---
    # Center approx (600, 450)
    center_x, center_y = 600, 400
    
    # Head
    head_y = center_y + 150
    head = patches.Circle((center_x, head_y), 50, color='cyan', fill=False, linewidth=3)
    ax.add_patch(head)
    
    # Body
    neck_y = head_y - 50
    hip_y = center_y - 150
    ax.plot([center_x, center_x], [neck_y, hip_y], color='cyan', linewidth=3, marker='o', markersize=8)
    
    # Shoulders
    shoulder_y = neck_y - 20
    shoulder_width = 80
    ax.plot([center_x - shoulder_width, center_x + shoulder_width], 
            [shoulder_y, shoulder_y], color='cyan', linewidth=3, marker='o', markersize=8)
    
    # Left Arm (Neutral/Down)
    l_shoulder_x = center_x - shoulder_width
    l_elbow_x, l_elbow_y = l_shoulder_x - 30, shoulder_y - 100
    l_wrist_x, l_wrist_y = l_elbow_x - 10, l_elbow_y - 80
    
    ax.plot([l_shoulder_x, l_elbow_x], [shoulder_y, l_elbow_y], color='cyan', linewidth=3, marker='o', markersize=8)
    ax.plot([l_elbow_x, l_wrist_x], [l_elbow_y, l_wrist_y], color='cyan', linewidth=3, marker='o', markersize=8)
    
    # Right Arm (RAISED HIGH!) -> Wrist Y > Ear Y (in plot coords, Y increases up)
    # So Wrist Y should be GREATER than Head Y
    r_shoulder_x = center_x + shoulder_width
    r_elbow_x, r_elbow_y = r_shoulder_x + 60, shoulder_y + 80
    r_wrist_x, r_wrist_y = r_elbow_x - 20, r_elbow_y + 120 # Way up high!
    
    ax.plot([r_shoulder_x, r_elbow_x], [shoulder_y, r_elbow_y], color='cyan', linewidth=3, marker='o', markersize=8)
    ax.plot([r_elbow_x, r_wrist_x], [r_elbow_y, r_wrist_y], color='cyan', linewidth=3, marker='o', markersize=8)

    # Legs (Just sitting/standing neutral)
    l_hip_x = center_x - 30
    r_hip_x = center_x + 30
    knee_y = hip_y - 100
    foot_y = knee_y - 100
    
    # Hips connection
    ax.plot([center_x, l_hip_x], [hip_y, hip_y-20], color='cyan', linewidth=3)
    ax.plot([center_x, r_hip_x], [hip_y, hip_y-20], color='cyan', linewidth=3)
    
    # Legs
    ax.plot([l_hip_x, l_hip_x-20], [hip_y-20, knee_y], color='cyan', linewidth=3, marker='o', markersize=8)
    ax.plot([r_hip_x, r_hip_x+20], [hip_y-20, knee_y], color='cyan', linewidth=3, marker='o', markersize=8)
    ax.plot([l_hip_x-20, l_hip_x-20], [knee_y, foot_y], color='cyan', linewidth=3, marker='o', markersize=8)
    ax.plot([r_hip_x+20, r_hip_x+20], [knee_y, foot_y], color='cyan', linewidth=3, marker='o', markersize=8)

    # --- Logic Annotation ---
    # Draw arrow from Right Wrist to Right Ear level
    # Ear level approx head_y
    ax.annotate(r'$Y_{wrist} > Y_{ear}$', 
                 xy=(r_wrist_x, r_wrist_y), xytext=(r_wrist_x + 50, r_wrist_y),
                 arrowprops=dict(facecolor='lime', shrink=0.05, ec='lime'),
                 fontsize=12, fontweight='bold', color='lime')

    # --- Bounding Box (Upper Body) ---
    bbox_x, bbox_y = center_x - 150, hip_y - 20
    bbox_w, bbox_h = 300, (r_wrist_y - bbox_y) + 20
    
    bbox = patches.Rectangle((bbox_x, bbox_y), bbox_w, bbox_h, linewidth=2, edgecolor='cyan', facecolor='none', linestyle='--')
    ax.add_patch(bbox)
    
    # --- Box Label ---
    ax.text(bbox_x, bbox_y + bbox_h + 10, 'ACTION: HAND_RAISE (Conf: 0.98)', 
            color='#00ff00', fontsize=14, fontweight='bold', fontfamily='monospace',
            bbox=dict(facecolor='black', edgecolor='#00ff00', alpha=0.9))

    # --- Overlays ---
    # Bottom Left
    ax.text(20, 20, 'MODE: PRIVACY_SAFE | VECTOR_STREAM_ONLY', 
            color='white', fontsize=16, fontfamily='monospace', fontweight='bold', alpha=0.8)
    
    # Save
    output_path = 'benchmarks/Fig_HandRaise.png'
    plt.savefig(output_path, dpi=120, bbox_inches='tight', facecolor='black')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    generate_hand_raise_figure()
