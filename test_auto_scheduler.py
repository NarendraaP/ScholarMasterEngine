from modules.scheduler import AutoScheduler
import os
import pandas as pd

# Reset files
if os.path.exists('data/teachers.json'):
    with open('data/teachers.json', 'w') as f:
        f.write('{"Prof. Smith": {"dept": "Math", "max_hours": 10, "current_hours": 0}, "Dr. Jones": {"dept": "Physics", "max_hours": 8, "current_hours": 0}}')
if os.path.exists('data/timetable.csv'):
    os.remove('data/timetable.csv')

s = AutoScheduler()

print("Test 1: Schedule 3 sessions for Prof. Smith")
logs = s.auto_generate_schedule([{"subject": "Math 101", "teacher": "Prof. Smith", "sessions": 3}])
print(logs)
# Should be Mon 9, Mon 10, Mon 11 (if empty)
df = pd.read_csv('data/timetable.csv')
assert len(df) == 3
assert df.iloc[0]['day'] == 'Monday'
assert df.iloc[0]['start'] == '09:00'

print("\nTest 2: Schedule 2 sessions for Dr. Jones")
# Should skip Mon 9, 10, 11 and start at Mon 12
logs = s.auto_generate_schedule([{"subject": "Physics 101", "teacher": "Dr. Jones", "sessions": 2}])
print(logs)
df = pd.read_csv('data/timetable.csv')
assert len(df) == 5
# Check 4th entry (index 3)
assert df.iloc[3]['teacher'] == 'Dr. Jones'
assert df.iloc[3]['start'] == '12:00'

print("\nTest 3: Max Hours Limit")
# Prof Smith has 3 hours. Max 10. Try to add 8 more -> should do 7 and stop.
logs = s.auto_generate_schedule([{"subject": "Math Advanced", "teacher": "Prof. Smith", "sessions": 8}])
print(logs)
df = pd.read_csv('data/timetable.csv')
# Total for Smith should be 10
smith_rows = df[df['teacher'] == 'Prof. Smith']
assert len(smith_rows) == 10

print("\nAll tests passed!")
