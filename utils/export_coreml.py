from ultralytics import YOLO
import os

def export_to_coreml():
    """
    Exports YOLOv8-Pose to CoreML format optimized for Apple M2 Neural Engine.
    Uses FP16 precision and baked NMS for maximum performance.
    """
    print("🍎 Exporting YOLO to CoreML for Apple M2 Neural Engine...")
    
    model_path = "models/yolov8n-pose.pt"
    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} not found!")
        return
    
    print(f"📦 Loading model: {model_path}")
    model = YOLO(model_path)
    
    # Get original file size
    original_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
    print(f"   Original size: {original_size:.2f} MB")
    
    try:
        print("⚙️  Exporting to CoreML format...")
        print("   - FP16 precision (half=True) for Neural Engine")
        print("   - Baked NMS (nms=True) for faster inference")
        
        # Export to CoreML
        # half=True: FP16 precision, perfect for M2 GPU/Neural Engine
        # nms=True: Bakes Non-Maximum Suppression into the model
        model.export(format='coreml', half=True, nms=True)
        
        # CoreML models are exported as .mlpackage directory
        coreml_path = "yolov8n-pose.mlpackage"
        
        if os.path.exists(coreml_path):
            # Calculate directory size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(coreml_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            coreml_size = total_size / (1024 * 1024)  # MB
            reduction = ((original_size - coreml_size) / original_size) * 100
            
            print("✅ Export Success: yolov8n-pose.mlpackage created.")
            print(f"   CoreML size: {coreml_size:.2f} MB")
            print(f"   Size change: {reduction:+.1f}%")
            print("\n🚀 Performance Benefits:")
            print("   - Optimized for Apple M2 Neural Engine")
            print("   - FP16 acceleration (2x faster)")
            print("   - Baked NMS (eliminates post-processing overhead)")
            print("   - Lower power consumption")
            print("\n💡 To use: Update master_engine.py will auto-detect this model")
        else:
            print("⚠️  CoreML export completed but file not found")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")
        print("💡 Tips:")
        print("   - Ensure ultralytics is up to date: pip install -U ultralytics")
        print("   - CoreML export requires macOS")
        print("   - On non-Mac systems, use ONNX export instead")

if __name__ == "__main__":
    export_to_coreml()
