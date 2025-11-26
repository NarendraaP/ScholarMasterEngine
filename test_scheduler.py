from modules.scheduler import SmartScheduler
import os

# Reset files for testing
if os.path.exists('data/teachers.json'):
    # Reset to initial state
    with open('data/teachers.json', 'w') as f:
        f.write('{"Prof. Smith": {"dept": "Math", "max_hours": 10, "assigned_hours": 0}, "Dr. Jones": {"dept": "Physics", "max_hours": 8, "assigned_hours": 0}, "Ms. Davis": {"dept": "CS", "max_hours": 12, "assigned_hours": 0}}')
if os.path.exists('data/timetable.csv'):
    os.remove('data/timetable.csv')

s = SmartScheduler()

# Test 1: Add valid class
print("Test 1: Add valid class")
success, msg = s.add_class("Monday", "09:00", "11:00", "Math 101", "Prof. Smith", "Zone A")
print(f"Result: {success}, {msg}")
assert success

# Test 2: Overlap Zone (Room Constraint)
print("\nTest 2: Overlap Zone")
success, msg = s.add_class("Monday", "10:00", "12:00", "Physics 101", "Dr. Jones", "Zone A")
print(f"Result: {success}, {msg}")
assert not success
assert "Zone A is already booked" in msg

# Test 3: Overlap Teacher (Faculty Constraint)
print("\nTest 3: Overlap Teacher")
success, msg = s.add_class("Monday", "10:00", "12:00", "Math 102", "Prof. Smith", "Zone B")
print(f"Result: {success}, {msg}")
assert not success
assert "Prof. Smith is already teaching" in msg

# Test 4: Workload Constraint
print("\nTest 4: Workload Constraint")
# Prof Smith has 2 hours assigned. Max 10.
# Add 9 hours -> 11 total > 10
success, msg = s.add_class("Tuesday", "09:00", "18:00", "Math Marathon", "Prof. Smith", "Zone C")
print(f"Result: {success}, {msg}")
assert not success
assert "Workload exceeded" in msg

print("\nAll tests passed!")
