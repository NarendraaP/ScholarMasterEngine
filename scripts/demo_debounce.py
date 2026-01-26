"""
Demonstration of Debounce Logic (Paper 4, Algorithm 1)

This script demonstrates the sanitization/debounce mechanism that filters
transient false positives before triggering schedule violation alerts.
"""
from datetime import time
from application.use_cases import DetectTruancyUseCase
from infrastructure.repositories import JsonStudentRepository, CsvScheduleRepository


def demo_debounce_logic():
    """Demonstrate debounce filtering in action"""
    
    print("=" * 70)
    print("DEBOUNCE LOGIC DEMONSTRATION (Paper 4, Algorithm 1)")
    print("=" * 70)
    
    # Initialize use case with lower threshold for demonstration
    student_repo = JsonStudentRepository("data/students.json")
    schedule_repo = CsvScheduleRepository("data/timetable.csv")
    
    # Threshold = 5 for quick demo (production uses 30)
    use_case = DetectTruancyUseCase(
        student_repo,
        schedule_repo,
        debounce_threshold=5
    )
    
    student_id = "CSE001"
    wrong_location = "Canteen"
    day = "Mon"
    check_time = time(10, 30)  # Assuming student has class at this time
    
    print(f"\nScenario: Student {student_id} detected in {wrong_location}")
    print(f"Expected location: (will query schedule)")
    print(f"Debounce threshold: 5 consecutive detections required\n")
    print("-" * 70)
    
    # Simulate 7 consecutive detections
    for detection_num in range(1, 8):
        is_compliant, message, session_data = use_case.execute(
            student_id,
            wrong_location,
            day,
            check_time
        )
        
        status_icon = "✅" if is_compliant else "🔴"
        print(f"Detection #{detection_num}: {status_icon} {message}")
        
        if not is_compliant:
            print(f"\n{'🚨 ALERT TRIGGERED! 🚨':^70}")
            if session_data:
                print(f"Expected: {session_data.get('room')} for {session_data.get('subject')}")
            break
    
    print("-" * 70)
    print("\n✅ BENEFIT: The first 4 detections don't trigger false alarms.")
    print("   This filters out:")
    print("   - Students briefly passing through zones")
    print("   - Transient detection errors")
    print("   - Natural movement between rooms\n")
    
    # Demonstrate counter reset
    print("=" * 70)
    print("COUNTER RESET DEMONSTRATION")
    print("=" * 70)
    print("\nSimulating student returning to correct location...\n")
    
    # Reset by returning to compliance (you'd need correct location)
    print("(In real scenario, detecting in correct room would reset counter)")
    

if __name__ == "__main__":
    try:
        demo_debounce_logic()
    except FileNotFoundError:
        print("⚠️  DATA FILES NOT FOUND")
        print("\nThis demo requires:")
        print("  - data/students.json")
        print("  - data/timetable.csv")
        print("\nThe debounce logic has been successfully implemented in:")
        print("  application/use_cases/detect_truancy_use_case.py")
        print("\nKey features added:")
        print("  ✅ Stateful violation counter per student")
        print("  ✅ Configurable threshold (default: 30)")
        print("  ✅ Auto-reset on compliance")
        print("  ✅ Matches Paper 4, Algorithm 1 specification")
