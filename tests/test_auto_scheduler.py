from modules.scheduler import AutoScheduler
import os
import pandas as pd
import pytest

def test_auto_scheduler():
    # Reset files
    if os.path.exists('data/teachers.json'):
        with open('data/teachers.json', 'w') as f:
            f.write('{"Prof. Smith": {"dept": "Math", "max_hours": 10, "current_hours": 0}, "Dr. Jones": {"dept": "Physics", "max_hours": 8, "current_hours": 0}}')
    if os.path.exists('data/timetable.csv'):
        os.remove('data/timetable.csv')

    s = AutoScheduler()

    print("Test 1: Schedule 3 sessions for Prof. Smith")
    # Full object as requested
    req1 = [{
        "faculty": "Science", 
        "dept": "Math", 
        "program": "UG", 
        "year": 1, 
        "section": "A",
        "subject": "Math 101", 
        "teacher": "Prof. Smith", 
        "sessions": 3, 
        "room": "Lab 1"
    }]
    
    logs = s.auto_generate_schedule(req1)
    print(logs)
    
    # Should be Mon 9, Mon 10, Mon 11
    df = pd.read_csv('data/timetable.csv')
    assert len(df) == 3
    assert df.iloc[0]['day'] == 'Mon' # Code uses "Mon", "Tue"...
    assert df.iloc[0]['start'] == '9:00'
    
    print("\nTest 2: Schedule 2 sessions for Dr. Jones")
    # Full object
    req2 = [{
        "faculty": "Science", 
        "dept": "Physics", 
        "program": "UG", 
        "year": 1, 
        "section": "A",
        "subject": "Physics 101", 
        "teacher": "Dr. Jones", 
        "sessions": 2, 
        "room": "Lab 2"
    }]
    
    logs = s.auto_generate_schedule(req2)
    print(logs)
    
    df = pd.read_csv('data/timetable.csv')
    assert len(df) == 5
    # Check 4th entry (index 3)
    assert df.iloc[3]['teacher'] == 'Dr. Jones'
    # Should start at 9:00 because Lab 2 is free and Dr. Jones is free
    assert df.iloc[3]['start'] == '9:00' 

    print("\nTest 3: Max Hours Limit")
    # Prof Smith has 3 hours. Max 10. Try to add 8 more -> should do 7 and stop.
    req3 = [{
        "faculty": "Science", 
        "dept": "Math", 
        "program": "UG", 
        "year": 1, 
        "section": "A",
        "subject": "Math Advanced", 
        "teacher": "Prof. Smith", 
        "sessions": 8, 
        "room": "Lab 1"
    }]
    
    logs = s.auto_generate_schedule(req3)
    print(logs)
    
    df = pd.read_csv('data/timetable.csv')
    # Total for Smith should be 10
    smith_rows = df[df['teacher'] == 'Prof. Smith']
    assert len(smith_rows) == 10

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_auto_scheduler()
