#!/usr/bin/env python3
"""
Model Optimization Script for Paper 5 (Hardware Acceleration).
Exports YOLOv8n-pose to CoreML with INT8 quantization for Apple Neural Engine.
"""

from ultralytics import YOLO
import os

def export_to_coreml():
    """
    Export YOLOv8n-pose to CoreML format with INT8 quantization.
    This enables hardware acceleration on Apple Neural Engine (M1/M2).
    """
    print("=" * 60)
    print("🚀 YOLOv8n-pose CoreML Export (INT8 Quantization)")
    print("=" * 60)
    
    # Load the PyTorch model
    print("\n1. Loading YOLOv8n-pose.pt...")
    model = YOLO("models/yolov8n-pose.pt")
    print("   ✅ Model loaded")
    
    # Export to CoreML with INT8 quantization
    print("\n2. Exporting to CoreML (INT8)...")
    print("   This may take a few minutes...")
    
    try:
        model.export(
            format='coreml',
            int8=True,      # INT8 quantization for smaller size and faster inference
            nms=True        # Include NMS in the model
        )
        print("   ✅ Export complete!")
        print("\n📦 Output: yolov8n-pose.mlpackage/")
        print("🎯 This model will run on Apple Neural Engine for 3-5x speedup")
        
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        print("\n💡 Note: CoreML export requires macOS and coremltools.")
        print("   Install with: pip install coremltools")
        return False
    
    return True

if __name__ == "__main__":
    success = export_to_coreml()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Optimization Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Run master_engine.py - it will auto-detect the CoreML model")
        print("2. Expect 3-5x speedup on M1/M2 chips")
        print("=" * 60)
