import os
import json
import cv2
import pandas as pd
import faiss

def check_face_registry():
    """Check if face database is loaded."""
    print("\n1. Checking Face Registry...")
    print("-" * 60)
    
    index_file = "data/faiss_index.bin"
    identity_map_file = "data/identity_map.json"
    
    if os.path.exists(index_file):
        try:
            index = faiss.read_index(index_file)
            num_identities = index.ntotal
            
            if num_identities > 0:
                print(f"✅ Face Database Loaded: {num_identities} identities found")
                
                # Load identity map for additional info
                if os.path.exists(identity_map_file):
                    with open(identity_map_file, 'r') as f:
                        identity_map = json.load(f)
                    print(f"   Identity Map Size: {len(identity_map)} entries")
            else:
                print("❌ Face Database Empty: 0 identities found")
                print("   Run face enrollment to add students!")
        except Exception as e:
            print(f"❌ Error loading face database: {e}")
    else:
        print("❌ Face Database Not Found")
        print("   Expected: data/faiss_index.bin")

def check_mobile_connections():
    """Check mobile camera connections."""
    print("\n2. Checking Mobile Camera Connections...")
    print("-" * 60)
    
    config_file = "data/zones_config.json"
    
    if not os.path.exists(config_file):
        print("❌ zones_config.json not found")
        return
    
    with open(config_file, 'r') as f:
        cameras = json.load(f)
    
    print(f"Found {len(cameras)} camera configurations")
    
    for cam in cameras:
        cam_name = cam.get('zone', 'Unknown')
        cam_type = cam.get('type', 'unknown')
        cam_source = cam.get('source')
        
        if cam_type == 'mobile':
            print(f"\n   Testing {cam_name} ({cam_source})...")
            
            try:
                # Try to connect
                cap = cv2.VideoCapture(cam_source)
                
                if cap.isOpened():
                    # Try to read one frame
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        print(f"   ✅ Cam [{cam_name}] Online (Frame: {frame.shape[1]}x{frame.shape[0]})")
                    else:
                        print(f"   ⚠️  Cam [{cam_name}] Connected but no frame received")
                else:
                    print(f"   ❌ Cam [{cam_name}] Unreachable (Check IP: {cam_source})")
                
                cap.release()
                
            except Exception as e:
                print(f"   ❌ Cam [{cam_name}] Error: {e}")
        else:
            print(f"   ⏭️  Skipping {cam_name} (type: {cam_type})")

def check_logic_links():
    """Check schedule and student database."""
    print("\n3. Checking Logic Links (Schedule & Student DB)...")
    print("-" * 60)
    
    # Check Timetable
    timetable_file = "data/timetable.csv"
    if os.path.exists(timetable_file):
        try:
            df = pd.read_csv(timetable_file)
            num_classes = len(df)
            print(f"✅ Schedule Loaded: {num_classes} classes found")
            
            if num_classes > 0:
                # Show sample
                print(f"   Columns: {', '.join(df.columns.tolist())}")
        except Exception as e:
            print(f"❌ Error loading schedule: {e}")
    else:
        print("❌ Schedule Not Found (data/timetable.csv)")
    
    # Check Students DB
    students_file = "data/students.json"
    if os.path.exists(students_file):
        try:
            with open(students_file, 'r') as f:
                students = json.load(f)
            num_students = len(students)
            print(f"✅ Student DB Loaded: {num_students} students found")
            
            # Count enrolled
            enrolled = sum(1 for s in students.values() if s.get('status') == 'Enrolled')
            print(f"   Enrolled Students: {enrolled}/{num_students}")
        except Exception as e:
            print(f"❌ Error loading student DB: {e}")
    else:
        print("❌ Student DB Not Found (data/students.json)")

def main():
    print("=" * 60)
    print("🔍 ScholarMaster System Health Check")
    print("=" * 60)
    
    check_face_registry()
    check_mobile_connections()
    check_logic_links()
    
    print("\n" + "=" * 60)
    print("🎉 System Health Check Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("   1. If any cameras are unreachable, verify IP addresses")
    print("   2. If face database is empty, run enrollment via admin_panel.py")
    print("   3. When ready, start the demo with: python multi_stream_simulation.py")
    print()

if __name__ == "__main__":
    main()
