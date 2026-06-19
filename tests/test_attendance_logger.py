from modules.attendance_logger import AttendanceManager
import os
import pandas as pd
import pytest

def test_logger():
    print("🧪 Testing Attendance Manager...")
    # Initialize Manager
    manager = AttendanceManager()
    
    # Clear existing file for test
    if os.path.exists(manager.attendance_path):
        os.remove(manager.attendance_path)
        # Re-init to clear cache
        manager = AttendanceManager()

    # Test 1: Mark Attendance
    print("Test 1: Marking S101...")
    # Context data required by mark_present
    context_data = {
        "subject": "CS101",
        "room": "Lab 1"
    }
    result = manager.mark_present("S101", context_data, user_role="Admin")
    
    if result == "Marked Present":
        print("✅ Marked S101")
    else:
        pytest.fail(f"❌ Failed to mark S101: {result}")

    # Test 2: Duplicate Check
    print("Test 2: Marking S101 again (Duplicate)...")
    result = manager.mark_present("S101", context_data, user_role="Admin")
    
    if result == "Already Logged":
        print("✅ Duplicate correctly rejected")
    else:
        pytest.fail(f"❌ Duplicate logic failed: {result}")

    # Test 3: Verify File
    print("Test 3: Verifying CSV content...")
    df = pd.read_csv(manager.attendance_path)
    if len(df) == 1 and df.iloc[0]['student_id'] == "S101":
        print("✅ CSV content correct")
    else:
        pytest.fail(f"❌ CSV content incorrect: {df}")

if __name__ == "__main__":
    test_logger()
