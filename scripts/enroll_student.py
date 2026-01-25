#!/usr/bin/env python3
"""
Student Enrollment Script for ScholarMaster
================================================================================
Quick script to register students for face recognition testing

Usage:
    python scripts/enroll_student.py

Follow prompts to capture student photo and register in FAISS index.

Author: Narendra P
Date: January 27, 2026 (Day 1 - Integration Sprint)
================================================================================
"""

import cv2
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules_legacy.face_registry import FaceRegistry


def capture_photo():
    """Capture photo from webcam"""
    print("\n📸 Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Cannot open camera")
        return None
    
    print("✅ Camera opened successfully")
    print("\n📋 Instructions:")
    print("  - Look directly at camera")
    print("  - Ensure good lighting")
    print("  - Press 's' to capture")
    print("  - Press 'q' to cancel")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display frame
        cv2.imshow('Capture Photo (Press S to capture, Q to cancel)', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print("\n✅ Photo captured!")
            cap.release()
            cv2.destroyAllWindows()
            return frame
        elif key == ord('q'):
            print("\n❌ Cancelled")
            cap.release()
            cv2.destroyAllWindows()
            return None
    
    cap.release()
    cv2.destroyAllWindows()
    return None


def main():
    """Main enrollment flow"""
    print("=" * 80)
    print("SCHOLARMASTER - STUDENT ENROLLMENT")
    print("=" * 80)
    
    # Initialize Face Registry
    print("\n[1/5] Initializing Face Recognition System...")
    try:
        registry = FaceRegistry()
        print("✅ Face recognition initialized")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return
    
    # Get student details
    print("\n[2/5] Enter Student Details:")
    student_id = input("  Student ID (e.g., S101): ").strip()
    name = input("  Name: ").strip()
    dept = input("  Department (e.g., CS): ").strip()
    
    # Capture photo
    print("\n[3/5] Capturing Photo...")
    photo = capture_photo()
    
    if photo is None:
        print("\n❌ Enrollment cancelled - no photo captured")
        return
    
    # Register in system
    print("\n[4/5] Registering student...")
    try:
        success, message = registry.register_face(
            image_array=photo,
            user_id=student_id,
            name=name,
            role="Student",
            dept=dept,
            user_role="Admin"  # Bypass RBAC for testing
        )
        
        if success:
            print(f"✅ {message}")
            print("\n[5/5] Enrollment Complete!")
            print(f"\n📊 Student Details:")
            print(f"  ID:         {student_id}")
            print(f"  Name:       {name}")
            print(f"  Department: {dept}")
            print(f"  Index Size: {registry.index.ntotal} students")
        else:
            print(f"❌ {message}")
    
    except Exception as e:
        print(f"❌ Error during registration: {e}")
    
    print("\n" + "=" * 80)
    print("Enrollment session complete. Run again to add more students.")
    print("=" * 80)


if __name__ == "__main__":
    main()
