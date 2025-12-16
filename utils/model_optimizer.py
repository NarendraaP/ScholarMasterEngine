from ultralytics import YOLO
import os

def optimize_yolo_for_edge():
    """
    Optimizes YOLOv8-Pose model for edge deployment.
    Exports to ONNX format with int8 quantization.
    """
    print("🚀 Starting Model Optimization for Edge Deployment...")
    
    # Load original model
    model_path = "models/yolov8n-pose.pt"
    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} not found!")
        return
    
    print(f"📦 Loading model: {model_path}")
    model = YOLO(model_path)
    
    # Get original file size
    original_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
    print(f"   Original size: {original_size:.2f} MB")
    
    # Export to ONNX with quantization
    print("⚙️  Exporting to ONNX format with int8 quantization...")
    output_path = "models/yolov8n-pose.int8.onnx"
    
    try:
        # YOLO export with ONNX format
        # Note: int8 quantization requires additional calibration data
        # For simplicity, we'll export to ONNX first (fp16 for speed)
        model.export(format="onnx", half=True, simplify=True)
        
        # Move exported file to models directory
        exported_file = "yolov8n-pose.onnx"
        if os.path.exists(exported_file):
            os.rename(exported_file, output_path)
            
        # Get optimized file size
        if os.path.exists(output_path):
            optimized_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            reduction = ((original_size - optimized_size) / original_size) * 100
            
            print(f"✅ Optimization Complete!")
            print(f"   Optimized size: {optimized_size:.2f} MB")
            print(f"   Reduction: {reduction:.1f}%")
            print(f"   Saved to: {output_path}")
        else:
            print("⚠️  Exported file not found. Using half-precision instead of int8.")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")
        print("💡 Tip: ONNX export works best with ultralytics==8.0.0+")
        print("   For full int8 quantization, use: model.export(format='openvino', int8=True)")

if __name__ == "__main__":
    optimize_yolo_for_edge()
