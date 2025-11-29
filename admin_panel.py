import streamlit as st
import pandas as pd
import json
import os
from modules.scheduler import AutoScheduler
from modules.auth import Authenticator
from modules.analytics import AnalyticsEngine
from utils.license_manager import check_license
from utils.hasher import hash_password
import time

st.set_page_config(page_title="Scholar Master Admin", layout="wide")

# --- License Check ---
if not check_license():
    st.error("❌ Invalid or Missing License Key. Please contact support.")
    st.stop()


# --- Authentication & Session State ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['name'] = None

auth = Authenticator()

if not st.session_state['logged_in']:
    st.title("🔐 Login to Scholar Master")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            role, name = auth.verify_user(username, password)
            if role:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.session_state['name'] = name
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.info("Default Users: admin/123, smith/123, john/123")

else:
    # --- Sidebar: User Info & Logout ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state['name']}**")
        st.caption(f"Role: {st.session_state['role']}")
        st.markdown("---")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.session_state['username'] = None
            st.session_state['name'] = None
            st.rerun()

    # --- Role Based Views ---
    role = st.session_state['role']

    if role == "Super Admin":
        st.title("🎓 Scholar Master Engine - University Management")
        
        # Create Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Scheduler", "📊 Analytics", "👥 User Management", "👤 Biometric Enrollment"])

        
        with tab1:
            st.subheader("Auto-Scheduler Module")

            # Initialize Scheduler
            scheduler = AutoScheduler(data_dir="data")

            # Load teachers data
            teachers_file = "data/teachers.json"
            if os.path.exists(teachers_file):
                with open(teachers_file, "r") as f:
                    teachers_data = json.load(f)
            else:
                st.error("Teachers data file not found!")
                teachers_data = {}

            # Load rooms data
            rooms_file = "data/rooms.json"
            if os.path.exists(rooms_file):
                with open(rooms_file, "r") as f:
                    rooms_data = json.load(f)
            else:
                rooms_data = {}

            # Get all unique faculties and departments for dropdowns
            all_faculties = sorted(list(set(t.get("faculty", "Unknown") for t in teachers_data.values())))

            # --- UI Section 1: Target Class (Students) ---
            st.markdown("### 1. Target Class (Students)")
            st.info("Select the class of students you want to schedule.")

            col1, col2, col3 = st.columns(3)
            with col1:
                student_program = st.selectbox("Program", ["UG", "PG"])
            with col2:
                student_faculty = st.selectbox("Student Faculty", all_faculties, key="stud_fac")

            # Filter Student Depts based on Student Faculty
            stud_faculty_teachers = {name: info for name, info in teachers_data.items() if info.get("faculty") == student_faculty}
            available_stud_depts = sorted(list(set(t["dept"] for t in stud_faculty_teachers.values())))

            with col3:
                if available_stud_depts:
                    student_dept = st.selectbox("Student Department", available_stud_depts, key="stud_dept")
                else:
                    st.warning(f"No depts in {student_faculty}")
                    student_dept = None

            col4, col5 = st.columns(2)
            with col4:
                student_year = st.selectbox("Year", [1, 2, 3, 4])
            with col5:
                student_section = st.selectbox("Section", ["A", "B", "C"])


            # --- UI Section 2: Instructor & Subject ---
            st.markdown("---")
            st.markdown("### 2. Instructor & Subject")
            st.info("Select the teacher and subject. You can choose a teacher from a different Faculty/Dept.")

            col6, col7 = st.columns(2)
            with col6:
                # Teaching Faculty (Defaults to Student Faculty for convenience, but selectable)
                try:
                    default_fac_index = all_faculties.index(student_faculty)
                except:
                    default_fac_index = 0
                teaching_faculty = st.selectbox("Teaching Faculty", all_faculties, index=default_fac_index, key="teach_fac")

            # Filter Teaching Depts
            teach_faculty_teachers = {name: info for name, info in teachers_data.items() if info.get("faculty") == teaching_faculty}
            available_teach_depts = sorted(list(set(t["dept"] for t in teach_faculty_teachers.values())))

            with col7:
                if available_teach_depts:
                    try:
                        default_dept_index = available_teach_depts.index(student_dept) if student_dept in available_teach_depts else 0
                    except:
                        default_dept_index = 0
                    teaching_dept = st.selectbox("Teaching Department", available_teach_depts, index=default_dept_index, key="teach_dept")
                else:
                    st.warning(f"No depts in {teaching_faculty}")
                    teaching_dept = None

            # Select Subject (Filtered by Teaching Dept)
            if teaching_dept:
                dept_teachers = {name: info for name, info in teach_faculty_teachers.items() if info["dept"] == teaching_dept}
                available_subjects = sorted(list(set(subj for t in dept_teachers.values() for subj in t["subjects"])))
                
                if available_subjects:
                    selected_subject = st.selectbox("Subject", available_subjects)
                else:
                    st.warning(f"No subjects found for {teaching_dept}")
                    selected_subject = None
            else:
                selected_subject = None

            # Select Teacher (Flexible from Teaching Dept)
            if selected_subject:
                teacher_options = {}
                sorted_teachers = sorted(dept_teachers.keys(), key=lambda t: selected_subject not in dept_teachers[t]["subjects"])
                
                for t_name in sorted_teachers:
                    t_info = teachers_data[t_name]
                    is_expert = selected_subject in t_info["subjects"]
                    expert_badge = "⭐" if is_expert else ""
                    label = f"{expert_badge} {t_name} (Workload: {t_info['current_hours']}/{t_info['max_hours']} hrs)"
                    teacher_options[label] = t_name
                
                if teacher_options:
                    selected_teacher_label = st.selectbox("Teacher", list(teacher_options.keys()))
                    selected_teacher_name = teacher_options[selected_teacher_label]
                else:
                    st.warning("No teachers found.")
                    selected_teacher_name = None
            else:
                selected_teacher_name = None


            # --- UI Section 3: Logistics (Rooms & Sessions) ---
            st.markdown("---")
            st.markdown("### 3. Logistics")

            col8, col9 = st.columns(2)

            with col8:
                session_type = st.radio("Session Type", ["Lecture", "Lab"], horizontal=True)

            # Room Selection Logic
            selected_room = None

            if session_type == "Lecture":
                # Get all lecture halls
                lecture_halls = [r_name for r_name, r_info in rooms_data.items() if r_info.get("type") == "Lecture"]
                
                # Find room fixed to the student section
                fixed_room = next((r_name for r_name, r_info in rooms_data.items() 
                                if r_info.get("type") == "Lecture" and r_info.get("fixed_to") == student_section), None)
                
                # Determine default index
                default_index = 0
                if fixed_room and fixed_room in lecture_halls:
                    default_index = lecture_halls.index(fixed_room)
                    st.info(f"Default Lecture Hall for Section {student_section}: **{fixed_room}**")
                
                if lecture_halls:
                    selected_room = st.selectbox("Select Lecture Hall", lecture_halls, index=default_index)
                else:
                    st.warning("No Lecture Halls defined.")
                    selected_room = None

            else: # Lab
                # Filter for Lab rooms
                lab_rooms = [r_name for r_name, r_info in rooms_data.items() if r_info.get("type") == "Lab"]
                if lab_rooms:
                    selected_room = st.selectbox("Select Lab", lab_rooms)
                else:
                    st.warning("No Labs defined in rooms.json")
                    selected_room = None

            with col9:
                num_sessions = st.number_input("Number of Sessions", min_value=1, max_value=5, value=3)

            # Action Button
            if st.button("Auto-Schedule Class"):
                if selected_teacher_name and selected_subject and student_dept and selected_room:
                    st.info(f"Scheduling {selected_subject} ({session_type}) for {student_faculty}/{student_dept} {student_program}-{student_year} ({student_section}) with {selected_teacher_name} in {selected_room}...")
                    
                    subjects_needed = [
                        {
                            "faculty": student_faculty,
                            "dept": student_dept,
                            "program": student_program,
                            "year": student_year,
                            "section": student_section,
                            "subject": selected_subject,
                            "teacher": selected_teacher_name,
                            "sessions": num_sessions,
                            "room": selected_room
                        }
                    ]
                    
                    # Run Scheduler
                    newly_scheduled = scheduler.auto_generate_schedule(subjects_needed)
                    
                    if not newly_scheduled.empty:
                        st.success("Schedule Generated Successfully!")
                        st.write("### Newly Scheduled Classes")
                        st.dataframe(newly_scheduled)
                        
                        st.write("### Full Timetable")
                        full_timetable = pd.read_csv("data/timetable.csv")
                        st.dataframe(full_timetable)
                    else:
                        st.warning("No classes could be scheduled. Check constraints (Room, Teacher, Section availability).")
                else:
                    if not selected_room:
                        st.error("Room selection failed. Please check configuration.")
                    else:
                        st.error("Please ensure all selections are made.")

            # Display current teacher status
            st.markdown("---")
            st.subheader("All Teachers Status")
            # --- FINAL UI POLISH ---
            st.markdown("---")
            st.subheader("📊 Faculty Workload Analytics")

            # Convert JSON to a clean DataFrame
            workload_list = []
            for name, info in teachers_data.items():
                # Calculate percentage (avoid div by zero)
                util = (info['current_hours'] / info['max_hours']) * 100 if info['max_hours'] > 0 else 0
                
                workload_list.append({
                    "Faculty Name": name,
                    "Department": info.get('dept', 'N/A'),
                    "Subjects": ", ".join(info.get('subjects', [])),
                    "Workload": f"{info['current_hours']} / {info['max_hours']} hrs",
                    "Utilization": f"{util:.1f}%"
                })

            df_workload = pd.DataFrame(workload_list)

            # Display as an interactive table
            st.dataframe(
                df_workload, 
                use_container_width=True, 
                column_config={
                    "Utilization": st.column_config.ProgressColumn(
                        "Utilization", 
                        format="%.1f%%", 
                        min_value=0, 
                        max_value=100
                    )
                }
            )
        
        with tab2:
            st.subheader("📊 Student Engagement Analytics")
            
            analytics = AnalyticsEngine()
            
            # Engagement Score Chart
            st.markdown("### Engagement Score by Subject")
            engagement_df = analytics.get_engagement_metrics()
            if not engagement_df.empty:
                st.bar_chart(engagement_df, x="Subject", y="Engagement Score")
            else:
                st.info("No engagement data available.")
                
            # Emotion Trends Chart
            st.markdown("### Emotion Trends over Time")
            trends_df = analytics.get_emotion_trends()
            if not trends_df.empty:
                # Pivot for chart: index=timestamp, columns=emotion, values=count (or just raw points)
                # For a simple line chart of counts per emotion over time, we might need aggregation.
                # Let's just plot the raw occurrences for now or a simple count if possible.
                # A better visualization for "Trends" is usually a line chart of emotion counts per time bucket.
                # Given the simplicity requested, let's just show the raw distribution over time or a scatter.
                # But the request asked for a Line Chart.
                # Let's aggregate by time (e.g., minute) and emotion.
                
                trends_agg = trends_df.groupby(['timestamp', 'emotion']).size().unstack(fill_value=0)
                st.line_chart(trends_agg)
            else:
                st.info("No trend data available.")

        with tab3:
            st.subheader("👥 User Management")
            
            # Load Users
            users_file = "data/users.json"
            if os.path.exists(users_file):
                with open(users_file, "r") as f:
                    users_db = json.load(f)
            else:
                users_db = {}
                
            # --- Add User ---
            with st.expander("Add New User"):
                with st.form("add_user_form"):
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        new_user = st.text_input("Username")
                        new_pass = st.text_input("Password", type="password")
                    with col_u2:
                        new_role = st.selectbox("Role", ["Super Admin", "Faculty Manager", "Faculty", "Student"])
                        new_dept = st.text_input("Department (Optional)")
                        
                    if st.form_submit_button("Create User"):
                        if new_user and new_pass:
                            if new_user in users_db:
                                st.error("User already exists!")
                            else:
                                h_pass, salt = hash_password(new_pass)
                                users_db[new_user] = {
                                    "password": f"{h_pass}:{salt}",
                                    "role": new_role,
                                    "name": new_user.capitalize(),
                                    "dept": new_dept
                                }
                                with open(users_file, "w") as f:
                                    json.dump(users_db, f, indent=4)
                                st.success(f"User {new_user} created!")
                                st.rerun()
                        else:
                            st.warning("Username and Password required.")

            # --- Bulk Import ---
            with st.expander("📂 Bulk Import Users"):
                st.info("Upload CSV with columns: `id` (username), `name`, `role`, `dept`")
                bulk_file = st.file_uploader("Upload User CSV", type=["csv"])
                if bulk_file:
                    if st.button("Process Import"):
                        df_bulk = pd.read_csv(bulk_file)
                        count = 0
                        for _, row in df_bulk.iterrows():
                            uid = str(row['id'])
                            if uid not in users_db:
                                h_pass, salt = hash_password("1234") # Default password
                                users_db[uid] = {
                                    "password": f"{h_pass}:{salt}",
                                    "role": row['role'],
                                    "name": row['name'],
                                    "dept": row.get('dept', '')
                                }
                                count += 1
                        
                        with open(users_file, "w") as f:
                            json.dump(users_db, f, indent=4)
                        st.success(f"Imported {count} users.")
                        st.rerun()

            # --- User List ---
            st.markdown("### Existing Users")
            
            # Convert to DF for display (hide password)
            user_list = []
            for u, d in users_db.items():
                user_list.append({
                    "Username": u,
                    "Name": d.get("name"),
                    "Role": d.get("role"),
                    "Dept": d.get("dept", "-")
                })
            
            if user_list:
                st.dataframe(pd.DataFrame(user_list), use_container_width=True)
                
                # Delete User
                del_user = st.selectbox("Select User to Delete", [u["Username"] for u in user_list])
                if st.button("Delete User", type="primary"):
                    if del_user == st.session_state['username']:
                        st.error("Cannot delete yourself!")
                    else:
                        del users_db[del_user]
                        with open(users_file, "w") as f:
                            json.dump(users_db, f, indent=4)
                        st.success(f"Deleted {del_user}")
                        st.rerun()

        with tab4:
            st.subheader("👤 Biometric Enrollment")
            
            from modules.face_registry import FaceRegistry
            import numpy as np
            import cv2
            
            registry = FaceRegistry()
            
            # RBAC for Enrollment
            # Super Admin sees all, Faculty Manager sees only their dept
            # Since this is Super Admin block, we see all.
            # But we want to reuse this logic for Faculty Manager.
            # For now, I will implement it here for Super Admin.
            
            enroll_tab1, enroll_tab2 = st.tabs(["📝 Single Enrollment", "📸 Kiosk Mode"])
            
            with enroll_tab1:
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_id = st.text_input("User ID / Student ID")
                    e_name = st.text_input("Full Name")
                    e_role = st.selectbox("Role", ["Student", "Faculty", "Staff"])
                    e_dept = st.text_input("Department")
                
                with col_e2:
                    e_img_file = st.file_uploader("Upload Photo", type=["jpg", "png"])
                    e_cam = st.camera_input("Take Photo")
                
                if st.button("Enroll User"):
                    img = None
                    if e_img_file:
                        file_bytes = np.asarray(bytearray(e_img_file.read()), dtype=np.uint8)
                        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    elif e_cam:
                        file_bytes = np.asarray(bytearray(e_cam.read()), dtype=np.uint8)
                        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    
                    if img is not None and e_id and e_name:
                        success, msg = registry.register_face(img, e_id, e_name, e_role, e_dept)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Missing Data or Image")

            with enroll_tab2:
                st.info("Kiosk Mode: Designed for rapid enrollment.")
                k_id = st.text_input("Enter ID to Enroll", key="kiosk_id")
                k_name = st.text_input("Enter Name", key="kiosk_name")
                k_dept = st.text_input("Department", key="kiosk_dept")
                
                k_cam = st.camera_input("Kiosk Camera", key="kiosk_cam_real")
                
                if k_cam and k_id and k_name:
                    if st.button("Enroll Now"):
                        file_bytes = np.asarray(bytearray(k_cam.read()), dtype=np.uint8)
                        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        success, msg = registry.register_face(img, k_id, k_name, "Student", k_dept)
                        if success:
                            st.success(msg)
                            # Optional: Clear fields? Streamlit makes this hard without rerun
                        else:
                            st.error(msg)

    elif role == "Faculty Manager":
        st.title("👤 Biometric Enrollment (Manager)")
        
        from modules.face_registry import FaceRegistry
        import numpy as np
        import cv2
        registry = FaceRegistry()
        
        # Get Manager's Dept
        users_file = "data/users.json"
        manager_dept = "Unknown"
        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                u_db = json.load(f)
                manager_dept = u_db.get(st.session_state['username'], {}).get("dept", "Unknown")
        
        st.info(f"Managing Enrollment for Department: **{manager_dept}**")
        
        enroll_tab1, enroll_tab2 = st.tabs(["📝 Single Enrollment", "📸 Kiosk Mode"])
        
        with enroll_tab1:
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_id = st.text_input("User ID")
                e_name = st.text_input("Full Name")
                e_role = st.selectbox("Role", ["Student", "Faculty"])
                # Locked Dept
                st.text_input("Department", value=manager_dept, disabled=True)
            
            with col_e2:
                e_cam = st.camera_input("Take Photo")
            
            if st.button("Enroll User"):
                if e_cam and e_id and e_name:
                    file_bytes = np.asarray(bytearray(e_cam.read()), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    success, msg = registry.register_face(img, e_id, e_name, e_role, manager_dept)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Missing info")

        with enroll_tab2:
            st.markdown("### 📸 Kiosk Mode")
            k_id = st.text_input("ID", key="m_k_id")
            k_name = st.text_input("Name", key="m_k_name")
            
            k_cam = st.camera_input("Camera", key="m_k_cam")
            
            if k_cam and k_id and k_name:
                if st.button("Enroll"):
                    file_bytes = np.asarray(bytearray(k_cam.read()), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    success, msg = registry.register_face(img, k_id, k_name, "Student", manager_dept)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    elif role == "Faculty":
        st.title("👨‍🏫 Faculty Portal")
        st.write(f"Welcome, {st.session_state['name']}")
        
        timetable_file = "data/timetable.csv"
        if os.path.exists(timetable_file):
            df = pd.read_csv(timetable_file)
            # Filter for the logged-in teacher
            my_classes = df[df['Teacher'] == st.session_state['name']]
            
            if not my_classes.empty:
                st.subheader("My Class Schedule")
                st.dataframe(my_classes, use_container_width=True)
            else:
                st.info("You have no classes scheduled yet.")
        else:
            st.info("No timetable has been generated yet.")

    elif role == "Student":
        st.title("📚 Student Portal")
        st.write(f"Welcome, {st.session_state['name']}")
        
        timetable_file = "data/timetable.csv"
        if os.path.exists(timetable_file):
            df = pd.read_csv(timetable_file)
            st.subheader("Full University Timetable")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No timetable has been generated yet.")

