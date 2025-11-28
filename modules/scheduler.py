import pandas as pd
import os
import json

class AutoScheduler:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.timetable_path = os.path.join(data_dir, "timetable.csv")
        self.teachers_path = os.path.join(data_dir, "teachers.json")
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        self.slots = [(f"{h}:00", f"{h+1}:00") for h in range(9, 17)] 
        
        # Added 'faculty' to columns
        self.columns = ["day", "start", "end", "faculty", "dept", "program", "year", "section", "subject", "teacher", "room"]
        self._load_data()

    def _load_data(self):
        # Load or create timetable
        if os.path.exists(self.timetable_path):
            self.timetable = pd.read_csv(self.timetable_path)
            # Ensure columns exist
            if not set(self.columns).issubset(self.timetable.columns):
                # Recreate if schema changed
                self.timetable = pd.DataFrame(columns=self.columns)
        else:
            self.timetable = pd.DataFrame(columns=self.columns)
            self.timetable.to_csv(self.timetable_path, index=False)

        # Load teachers
        if os.path.exists(self.teachers_path):
            with open(self.teachers_path, "r") as f:
                self.teachers = json.load(f)
        else:
            self.teachers = {}

    def auto_generate_schedule(self, subjects_needed):
        """
        subjects_needed: list of dicts 
        [{
            "faculty": "Technology",
            "dept": "Computer Science",
            "program": "UG",
            "year": 1,
            "section": "A",
            "subject": "Data Structures",
            "teacher": "Ms. Davis",
            "sessions": 3,
            "room": "Lab 1"
        }]
        """
        scheduled_classes = []
        self._load_data() # Refresh

        for item in subjects_needed:
            faculty = item.get("faculty", "Unknown") # Handle potential missing key if old code calls it
            dept = item["dept"]
            program = item["program"]
            year = item["year"]
            section = item["section"]
            subject = item["subject"]
            teacher_name = item["teacher"]
            sessions_needed = item["sessions"]
            room = item["room"]
            
            if teacher_name not in self.teachers:
                print(f"Warning: Teacher {teacher_name} not found.")
                continue

            sessions_scheduled = 0
            
            for day in self.days:
                if sessions_scheduled >= sessions_needed:
                    break
                
                for start, end in self.slots:
                    if sessions_scheduled >= sessions_needed:
                        break

                    if self._is_slot_available(day, start, end, faculty, dept, program, year, section, teacher_name, room):
                        # Schedule it
                        new_row = {
                            "day": day,
                            "start": start,
                            "end": end,
                            "faculty": faculty,
                            "dept": dept,
                            "program": program,
                            "year": year,
                            "section": section,
                            "subject": subject,
                            "teacher": teacher_name,
                            "room": room
                        }
                        self.timetable = pd.concat([self.timetable, pd.DataFrame([new_row])], ignore_index=True)
                        
                        # Update teacher hours
                        self.teachers[teacher_name]["current_hours"] += 1
                        sessions_scheduled += 1
                        scheduled_classes.append(new_row)
            
            if sessions_scheduled < sessions_needed:
                print(f"Could not schedule all sessions for {subject}. Scheduled {sessions_scheduled}/{sessions_needed}")

        # Save updates
        # Save updates
        self.save_data()

        return pd.DataFrame(scheduled_classes)

    def save_data(self):
        # 1. Save timetable to a temp file
        temp_tt_path = f"{self.timetable_path}.tmp"
        self.timetable.to_csv(temp_tt_path, index=False)
        # Atomic swap
        os.replace(temp_tt_path, self.timetable_path)

        # 2. Save teachers to a temp file
        temp_teachers_path = f"{self.teachers_path}.tmp"
        with open(temp_teachers_path, "w") as f:
            json.dump(self.teachers, f, indent=4)
        # Atomic swap
        os.replace(temp_teachers_path, self.teachers_path)

    def _is_slot_available(self, day, start, end, faculty, dept, program, year, section, teacher_name, room):
        slot_mask = (self.timetable["day"] == day) & (self.timetable["start"] == start)

        # 1. Room Conflict
        room_busy = not self.timetable[slot_mask & (self.timetable["room"] == room)].empty
        if room_busy:
            return False

        # 2. Teacher Conflict
        teacher_busy = not self.timetable[slot_mask & (self.timetable["teacher"] == teacher_name)].empty
        if teacher_busy:
            return False

        # 3. Section Conflict: (Faculty, Dept, Program, Year, Section)
        # Assuming Section A in CS is different from Section A in Math, so we check full hierarchy
        section_busy = not self.timetable[
            slot_mask & 
            (self.timetable["faculty"] == faculty) &
            (self.timetable["dept"] == dept) &
            (self.timetable["program"] == program) &
            (self.timetable["year"] == year) &
            (self.timetable["section"] == section)
        ].empty
        if section_busy:
            return False

        # 4. Teacher Max Hours
        teacher_info = self.teachers.get(teacher_name)
        if teacher_info:
            if teacher_info["current_hours"] >= teacher_info["max_hours"]:
                return False
        
        return True
