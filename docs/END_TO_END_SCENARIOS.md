# ScholarMasterEngine - End-to-End Scenarios

**Purpose**: Detailed flow documentation for primary institutional use cases  
**Version**: 1.0  
**Last Updated**: January 27, 2026

---

## Overview

This document provides **step-by-step walkthroughs** of the four core institutional scenarios that ScholarMasterEngine handles. Each scenario shows:
- Complete data flow from sensor input to audit trail
- All modules involved with exact method calls
- Decision points and branching logic
- Privacy compliance checkpoints
- Sample data payloads

---

## Scenario A: Student Entry & Compliance Validation

### Context

**Time**: Monday, 10:00 AM  
**Location**: Main Entrance → Lab-1  
**Student**: S101 (Name: John Doe, UG Year 1, Section A, CS Department)  
**Expected**: Data Structures class in Lab-1 (10:00-11:00, Teacher: Ms. Davis)

### Step-by-Step Flow

#### 1. Face Detection & Recognition

```
[VIDEO THREAD - 30 FPS]

Frame captured (640x480 BGR)
    ↓
InsightFace.get(frame)
  → Detects face: bbox=[120, 80, 320, 380]
  → Extracts embedding: [512-dim float array]
    ↓
FaceRegistry.search_face(embedding)
  → FAISS IndexFlatL2.search(embedding, k=1)
  → Returns: (found=True, match_id="S101", distance=0.23)
    ↓
Adaptive threshold check:
  gallery_size = len(student_ids) = 1250
  τ(N) = 0.75 + 0.00001 * log(1250) = 0.75071
  confidence = 1 - (distance / 2) = 0.885
  → 0.885 > 0.75071 ✅ ACCEPT
```

**Code Location**: [`main_unified.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main_unified.py#L416-L440)

**Modules Involved**:
- `FaceRegistry` ([`modules_legacy/face_registry.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/face_registry.py))
- FAISS (`infrastructure/indexing/faiss_face_index.py`)

#### 2. Student Information Retrieval

```
student_id = "S101"
    ↓
Load data/students.json
{
  "S101": {
    "name": "John Doe",
    "program": "UG",
    "year": 1,
    "section": "A",
    "dept": "Computer Science",
    "privacy_hash": "a3f7b9c2d1e4..."
  }
}
```

**Privacy Note**: `name` used only for display, `privacy_hash` used for all logging.

#### 3. Timetable Compliance Check

```
ContextEngine.check_compliance(
    student_id="S101",
    current_zone="Main Entrance",  # ⚠️ Wrong location!
    day="Mon",
    time_str="10:00"
)
    ↓
get_expected_location("S101", "Mon", "10:00")
  → Filter timetable.csv:
     day='Mon' AND program='UG' AND year=1 AND section='A' AND dept='Computer Science'
  → Time check: 10:00 in range [10:00, 11:00)
  → Found: {"room": "Lab-1", "subject": "Data Structures", "teacher": "Ms. Davis"}
    ↓
Comparison:
  current_zone = "Main Entrance"
  expected_room = "Lab-1"
  → NOT EQUAL ❌
    ↓
Return: (
    is_compliant = False,
    message = "TRUANCY: Expected in Lab-1 for Data Structures",
    expected_data = {"room": "Lab-1", "subject": "Data Structures", ...}
)
```

**Code Location**: [`modules_legacy/context_manager.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/context_manager.py#L121-L139)

#### 4. Truancy Alert Generation

```
is_compliant = False
    ↓
trigger_alert(
    alert_type="Warning",
    message="Truancy: S101 detected in Main Entrance. Expected in Lab-1 for Data Structures",
    location="Main Entrance"
)
    ↓
Create alert object:
{
  "timestamp": "2026-01-27T10:00:15.342Z",
  "type": "Warning",
  "msg": "Truancy: S101 detected in Main Entrance. Expected in Lab-1 for Data Structures",
  "zone": "Main Entrance"
}
    ↓
Atomic write to data/alerts.json:
  1. Load existing alerts
  2. Append new alert
  3. Write to temp file: alerts.json.tmp
  4. os.replace(temp, final)  # Atomic operation
```

**Code Location**: [`master_engine.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/master_engine.py#L524-L562)

#### 5. Alert Dispatch

```
[NOTIFICATION DISPATCHER - Polling every 2s]

NotificationDispatcher._check_new_alerts()
  → Load data/alerts.json
  → Filter: timestamp > last_checked_timestamp
  → New alert found!
    ↓
_dispatch(alert)
  → Print structured log:
     🔔 DISPATCHING ALERT [Warning]
        - Zone: Main Entrance
        - Message: Truancy: S101 detected...
        - Time: 2026-01-27T10:00:15.342Z
  → (In production: Send SMS/Email via Twilio/SendGrid)
    ↓
Recipients (determined by alert type "Warning"):
  ✉️ Class Teacher: Ms. Davis
  ✉️ HOD: Computer Science Department
  ✉️ Admin

Admin Panel Alert Center updates on next refresh.
```

**Code Location**: [`notification_service.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/notification_service.py#L71-L86)

#### 6. Privacy-Preserving Audit Log

```
Create AttendanceEvent:
{
  "student_id": "S101",  # Real ID (for internal use)
  "timestamp": 1706342415.342,
  "zone": "Main Entrance",
  "confidence": 0.885,
  "engagement_score": 0.0,  # Not yet in class
  "audio_level_db": 35.2,
  "is_valid": False,  # Non-compliant
  "violation_reason": "TRUANCY: Expected in Lab-1 for Data Structures"
}
    ↓
SimplifiedAuditLog.append_event(event)
  → Hash event: SHA256(JSON.dumps(event, sort_keys=True))
    event_hash = "7a3f9b2c..."
  → Append to self.events list
  → Check: len(events) % 100 == 0?
    → NO (event #47) → Skip Merkle tree build
    ↓
Return: event_hash = "7a3f9b2c..."
```

**Code Location**: [`main_unified.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main_unified.py#L89-L111)

**Privacy Transformation** (for session_log.csv):
```
anon_id = context_engine.get_anon_id("S101")
  → privacy_hash = "a3f7b9c2d1e4..."

Log entry (data/session_log.csv):
timestamp,anon_id,event_type,zone
2026-01-27T10:00:15,a3f7b9c2d1e4,Truancy,Main Entrance

✅ No student name
✅ No real ID
✅ Anonymous hash only
```

### Scenario Outcome

**System Actions**:
- ✅ Student identified (S101)
- ❌ Truancy detected (wrong location)
- 🔔 Alert sent to Class Teacher, HOD, Admin
- 📝 Audit event logged (non-compliant)
- 🔒 Privacy-preserving log entry created

**Next Steps** (Human-in-the-Loop):
- Class Teacher investigates (Admin Panel Alert Center)
- Possible actions:
  - **Confirm**: Student was indeed absent/truant → Mark violation
  - **Dismiss**: Student had permission (medical, event) → False positive

---

## Scenario B: Faculty Absence Detection

### Context

**Time**: Monday, 10:00 AM  
**Location**: Lab-1 (scheduled class active)  
**Expected Faculty**: Ms. Davis (Data Structures, CS Department)  
**Actual**: NO faculty face detected after 2-minute grace period

### Step-by-Step Flow

#### 1. Period Start & Timetable Query

```
[COMPLIANCE THREAD - 5s interval]

current_time = datetime.now()  # 2026-01-27 10:02:00
current_zone = "Lab-1"
    ↓
ContextEngine.get_class_context(
    zone="Lab-1",
    day="Mon",
    time_str="10:02"
)
    ↓
Filter timetable.csv:
  day='Mon' AND room='Lab-1'
  → Match found:
     {
       "start": "10:00",
       "end": "11:00",
       "subject": "Data Structures",
       "teacher": "Ms. Davis",
       "dept": "Computer Science",
       "program": "UG",
       "year": 1,
       "section": "A"
     }
    ↓
Time check: 10:02 in range [10:00, 11:00)?
  → YES ✅
    ↓
Return: True (Lecture Mode Active)
```

**Code Location**: [`context_manager.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/context_manager.py#L91-L119)

#### 2. Faculty Presence Verification

```
[VIDEO THREAD - 30 FPS]

expected_teacher = "Ms. Davis"
grace_period = 120  # seconds (2 minutes)
period_start_time = "10:00:00"
current_time = "10:02:00"
    ↓
Check elapsed time:
  elapsed = current_time - period_start_time = 120s
  → Grace period expired ⏰
    ↓
Scan detected faces in current_zone="Lab-1":
  faces = InsightFace.get(frame)  # Returns list of Face objectsfor face in faces:
    embedding = face.embedding
    found, faculty_id = FaceRegistry.search_face(embedding)
    
    if found:
        # Check if this is Ms. Davis
        faculty_record = load_faculty_record(faculty_id)
        if faculty_record["name"] == "Ms. Davis":
            faculty_present = True
            break
    ↓
Result: faculty_present = False ❌
```

**Note**: Current implementation is **IMPLICIT**. This logic is not in a dedicated module but can be inferred from existing components.

**Proposed Module**: `faculty_tracker.py` (future enhancement)

#### 3. Faculty Absence Alert

```
faculty_present = False
elapsed > grace_period
lecture_mode = True
    ↓
trigger_alert(
    alert_type="Warning",
    message="Faculty Absence - Ms. Davis, Data Structures, Lab-1",
    location="Lab-1"
)
    ↓
Alert payload:
{
  "timestamp": "2026-01-27T10:02:00.123Z",
  "type": "Warning",
  "msg": "Faculty Absence - Ms. Davis, Data Structures, Lab-1",
  "zone": "Lab-1",
  "expected_faculty": "Ms. Davis",  # Additional metadata
  "subject": "Data Structures"
}
    ↓
Atomic write to data/alerts.json
```

#### 4. Alert Routing (Role-Based)

```
alert_type = "Warning"
subject_dept = "Computer Science"  # From timetable
    ↓
Determine recipients:
  1. HOD (Computer Science) → Dr. Smith
  2. Admin → admin@institution.edu
  3. Class Teacher (if different from faculty) → [Skip if same]
    ↓
NotificationDispatcher dispatches to:
  ✉️ Dr. Smith (HOD-CS)
  ✉️ Admin
```

**Code Location**: [`notification_service.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/notification_service.py#L71-L86)

#### 5. Admin Panel Visibility

```
Admin opens Alert Center tab (admin_panel.py L582)
    ↓
Poll data/alerts.json
    ↓
Display alert:
  🟡 WARNING | 2026-01-27 10:02:00 | Lab-1
  Reason: Faculty Absence - Ms. Davis, Data Structures, Lab-1
    ↓
Actions available:
  [✅ Confirm] → Mark Ms. Davis as absent, log to HR system
  [❌ Dismiss] → Faculty arrived late, false alarm
```

**Code Location**: [`admin_panel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/admin_panel.py#L582-L645)

### Scenario Outcome

**System Actions**:
- ✅ Lecture mode detected (via timetable)
- ⏰ Grace period elapsed (2 minutes)
- ❌ Faculty absent (no face match for Ms. Davis)
- 🔔 Alert sent to HOD, Admin
- 📝 Incident logged for HR review

**Human Response**:
- HOD investigates (possible sick leave, traffic)
- Substitute teacher assigned if needed
- Faculty notified of absence marking

---

## Scenario C: Lecture Validation & Quality Monitoring

### Context

**Time**: Monday, 10:15 AM (15 minutes into class)  
**Location**: Lab-1  
**Expected**: Data Structures lecture (Faculty: Ms. Davis, Students: ~35)  
**Goal**: Validate that a genuine lecture is occurring

### Step-by-Step Flow

#### 1. Faculty Presence Confirmation

```
[VIDEO THREAD]

frames = camera.read() # 30 FPS
    ↓
faces= InsightFace.get(frame)
    ↓
For each face:
  embedding = face.embedding
  found, person_id = FaceRegistry.search_face(embedding)
  
  if found:
    person_record = load_record(person_id)
    if person_record["role"] == "Faculty":
      faculty_present = True
      faculty_id = person_id  # "F_DAVIS_001"
        ↓
Result: faculty_present = True ✅
        faculty_id = "F_DAVIS_001" (Ms. Davis)
```

#### 2. Student Count Verification

```
[VIDEO THREAD + POSE DETECTION]

YOLOv8 Pose Detection:
  results = pose_model(frame)
  keypoints_list = results[0].keypoints.data
  student_count_camera = len(keypoints_list)  # 34 people detected
    ↓
Attendance Log Query:
  today = "2026-01-27"
  subject = "Data Structures"  # From timetable
  
  df = AttendanceManager.get_attendance(subject="Data Structures")
  df_today = df[df['date'] == today]
  student_count_log = len(df_today)  # 35 students marked present
    ↓
Comparison:
  |student_count_camera - student_count_log| = |34 - 35| = 1
  tolerance = 2  # Allow ±2 margin
  → Within tolerance ✅
```

**Code Location**: [`master_engine.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/master_engine.py#L414-L444)

#### 3. Audio Activity Monitoring

```
[AUDIO THREAD - 100ms chunks]

AudioSentinel.extract_features(audio_chunk)
  → FFT analysis
  → Features:
     {
       "db": 58.3,  # dB level
       "spectral_centroid": 2800 Hz,  # Human voice range
       "zero_crossing_rate": 0.18  # Voice activity indicator
     }
    ↓
Context-aware validation:
  is_lecture_mode = True  # From get_class_context()
  
  Expected range for lecture:
    - Min: 50 dB (teacher speaking)
    - Max: 70 dB (normal lecture)
    
  Actual: 58.3 dB
    → Within range ✅
    ↓
Speech activity detected: zero_crossing_rate > 0.15
  → YES ✅ (Teacher speaking)
```

**Code Location**: [`audio_sentinel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/audio_sentinel.py), [`master_engine.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/master_engine.py#L499-L523)

#### 4. Lecture Validation Decision

```
ALL criteria validated:
  ✅ Faculty present (Ms. Davis)
  ✅ Student count matches (34 ≈ 35)
  ✅ Audio activity normal (58.3 dB, speech detected)
    ↓
Conclusion: VALID LECTURE ✅
    ↓
Log metadata (privacy-preserving):
{
  "timestamp": "2026-01-27T10:15:00",
  "subject": "Data Structures",
  "faculty_id": "F_DAVIS_001",  # Not name
  "student_count": 34,
  "avg_audio_db": 58.3,
  "zone": "Lab-1",
  "is_valid_lecture": True
}
    ↓
Save to: data/lecture_quality_log.csv (anonymized)
```

**Privacy Compliance**:
- ❌ NO student names logged
- ❌ NO audio recordings stored
- ✅ ONLY metadata (counts, dB levels, timestamps)
- ✅ Faculty identified by ID, not name in logs

#### 5. Optional: Lecture Scribe (if enabled)

```
IF config["enable_lecture_scribe"] == True:
    
    LectureScribe.transcribe_latest()
      → Whisper model (local, no cloud)
      → Transcript: "Today we'll cover binary search trees..."
        ↓
    Save transcript:
      {
        "timestamp": "2026-01-27T10:15:00",
        "subject": "Data Structures",
        "snippet": "Today we'll cover binary search trees...",  # First 100 chars
        "word_count": 450
      }
        ↓
    Privacy: NO full audio stored, only text summary
```

**Note**: Disabled by default (privacy-sensitive feature)

**Code Location**: [`scribe.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/scribe.py)

### Scenario Outcome (Valid Lecture)

**System Actions**:
- ✅ Lecture validated (all criteria met)
- 📝 Quality metadata logged
- ✅ NO alerts generated (system operating normally)

### Alternative Outcome (Invalid Lecture)

**If Faculty Missing**:
```
faculty_present = False
  → Alert: "Unsupervised Class - Lab-1, Data Structures"
  → Recipients: HOD, Admin, Security
```

**If Silence Detected**:
```
audio_db < 30 dB (sustained 2 minutes)
  → Alert: "Potential Class Skip - No audio activity in Lab-1"
  → Recipients: HOD, Class Teacher
```

**If Excessive Noise**:
```
audio_db > 70 dB (lecture mode threshold exceeded)
  → Alert: "Disturbance during lecture - Lab-1"
  → Recipients: Security, Class Teacher
```

---

## Scenario D: Noise/Disturbance Alert During Lecture

### Context

**Time**: Monday, 10:30 AM (mid-lecture)  
**Location**: Lecture Hall A  
**Mode**: Lecture Mode (strict noise monitoring)  
**Event**: Students start loud conversation during explanation

### Step-by-Step Flow

#### 1. Audio Monitoring (Continuous)

```
[AUDIO THREAD - 10 Hz sampling]

AudioSentinel running in background:
  sample_rate = 44100 Hz
  chunk_duration = 0.1 s  # 100ms chunks
  
  While running:
    audio_chunk = sounddevice.rec(duration * sample_rate)
    sounddevice.wait()
      ↓
    Process chunk:
      FFT analysis → Extract features
```

**Code Location**: [`main_unified.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/main_unified.py#L606-L640) (audio_thread)

#### 2. Spectral Analysis (Privacy-Preserving)

```
audio_data = numpy.array (4410 samples, float32)
    ↓
FFT (Fast Fourier Transform):
  frequencies = numpy.fft.rfft(audio_data)
  magnitudes = numpy.abs(frequencies)
    ↓
Calculate dB level:
  rms = sqrt(mean(audio_data^2))
  db = 20 * log10(rms) + 60  # Normalization
  → db = 72.5 dB ⚠️
    ↓
Extract voice features (NO speech recognition):
  spectral_centroid = weighted_mean_frequency(magnitudes)
    → 2900 Hz (human voice range: 85-255 Hz fundamental, harmonics up to 4kHz)
  
  zero_crossing_rate = count_zero_crossings(audio_data) / len(audio_data)
    → 0.22 (high ZCR = voice activity)
```

**Code Location**: [`audio_sentinel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/audio_sentinel.py)

**Privacy**: Only spectral features extracted, NO speech-to-text, NO conversation content.

#### 3. Context-Aware Threshold Check

```
is_lecture_mode = ContextEngine.get_class_context("Lecture Hall A", "Mon", "10:30")
  → Returns: True (class active)
    ↓
Determine threshold:
  IF is_lecture_mode:
    threshold_db = 40  # Strict (whisper level)
  ELSE:
    threshold_db = 80  # Relaxed (shout level)
    ↓
Actual threshold: 40 dB (lecture mode)
Actual audio level: 72.5 dB
    ↓
Comparison: 72.5 > 40 → VIOLATION ❌
```

**Code Location**: [`master_engine.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/master_engine.py#L499-L523)

#### 4. Sustained Detection (Debounce)

```
Noise violation detected (72.5 dB > 40 dB)
    ↓
Check sustained duration:
  violation_start_time = time.time()  # First detection
  
  WHILE audio_db > threshold:
    update_violation_timer()
    
    IF elapsed_time > 5.0s:  # 5-second threshold
      trigger_alert()  # Confirmed sustained disturbance
      BREAK
    
    SLEEP(0.1s)  # Next chunk
```

**Rationale**: Prevent false alerts from brief noise spikes (door slam, cough, etc.)

#### 5. Alert Generation

```
Sustained violation confirmed (>5s)
    ↓
trigger_alert(
    alert_type="Warning",
    message="Disturbance: Talking detected during lecture - 72.5 dB",
    location="Lecture Hall A"
)
    ↓
Alert payload:
{
  "timestamp": "2026-01-27T10:30:05.789Z",
  "type": "Warning",
  "msg": "Disturbance: Talking detected during lecture - 72.5 dB",
  "zone": "Lecture Hall A",
  "audio_db": 72.5,
  "threshold": 40,
  "duration_s": 5.2
}
    ↓
Atomic write to data/alerts.json
```

#### 6. Alert Routing & Escalation

```
alert_type = "Warning"
zone = "Lecture Hall A"
    ↓
Query timetable for current class:
  subject = "Linear Algebra"
  teacher = "Dr. Johnson"
  dept = "Mathematics"
    ↓
Determine recipients (escalation tier):
  
  Tier 1 (Immediate):
    ✉️ Security (live monitoring station)
    
  Tier 2 (After 30s sustained):
    ✉️ Class Teacher (Dr. Johnson)
    ✉️ HOD (Mathematics)
    
  Tier 3 (Admin notification):
    ✉️ Admin (if issue persists >2 min)
```

**Code Location**: [`notification_service.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/notification_service.py)

#### 7. Admin Panel Display

```
Admin/Security opens Alert Center tab
    ↓
Alert displayed:
  🟡 WARNING | 2026-01-27 10:30:05 | Lecture Hall A
  Reason: Disturbance: Talking detected during lecture - 72.5 dB
  Duration: 5.2s (ongoing...)
    ↓
Real-time updates:
  - Audio level graph (last 30s)
  - Zone camera preview (if configured)
  - Escalation timer
    ↓
Actions:
  [✅ Confirm] → Security dispatched, incident logged
  [❌ Dismiss] → False alarm (mic malfunction, external noise)
  [🔇 Mute Alerts] → Temporary disable for this zone (maintenance)
```

**Code Location**: [`admin_panel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/admin_panel.py#L582-L645)

### Scenario Outcome

**System Actions**:
- ✅ Noise violation detected (72.5 dB > 40 dB threshold)
- ⏱️ Sustained detection confirmed (5s duration)
- 🔔 Alert sent to Security, Class Teacher, HOD
- 📝 Incident logged with audio metadata (NOT recording)
- 🔒 Privacy maintained (NO speech content captured)

**Human Response**:
- Security reviews alert (Admin Panel Alert Center)
- Possible actions:
  - Send message to Dr. Johnson (via internal system)
  - Dispatch personnel to Lecture Hall A
  - Monitor remotely (if noise subsides, dismiss alert)

**Privacy Compliance**:
- ❌ NO audio recording stored
- ❌ NO speech-to-text transcription
- ✅ ONLY dB level + spectral features logged
- ✅ No identification of WHO was talking

---

## Cross-Scenario Integration Points

### Shared Data Sources

1. **`data/timetable.csv`** - Used by ALL scenarios
   - Student compliance (Scenario A)
   - Faculty absence (Scenario B)
   - Lecture validation (Scenario C)
   - Context-aware thresholds (Scenario D)

2. **`data/students.json`** - Student identity mapping
   - Face recognition → Student ID (Scenario A, C)
   - Privacy hash for logging (All scenarios)

3. **`data/alerts.json`** - Central alert queue
   - Written by: All scenarios
   - Read by: NotificationDispatcher, Admin Panel

### Module Overlap

| Module | Scenario A | Scenario B | Scenario C | Scenario D |
|--------|:----------:|:----------:|:----------:|:----------:|
| `FaceRegistry` | ✅ | ✅ | ✅ | - |
| `ContextEngine` | ✅ | ✅ | ✅ | ✅ |
| `AttendanceManager` | ✅ | - | ✅ | - |
| `AudioSentinel` | - | - | ✅ | ✅ |
| `NotificationDispatcher` | ✅ | ✅ | ✅ | ✅ |
| `SimplifiedAuditLog` | ✅ | ✅ | ✅ | ✅ |

---

## Testing Scenarios

### Reproducibility Guide

**Scenario A (Truancy)**:
```bash
# 1. Add student to registry
python scripts/enroll_student.py --id S101 --name "John Doe"

# 2. Add timetable entry
echo "Mon,10:00,11:00,Technology,Computer Science,UG,1,A,Data Structures,Ms. Davis,Lab-1" >> data/timetable.csv

# 3. Run system
python main_unified.py

# 4. Present face at "Main Entrance" (not Lab-1) at 10:00 AM
# Expected: Truancy alert in data/alerts.json
```

**Scenario D (Noise)**:
```bash
# 1. Set lecture mode in timetable
echo "Mon,10:30,11:30,Arts,Mathematics,UG,2,B,Linear Algebra,Dr. Johnson,Lecture Hall A" >> data/timetable.csv

# 2. Run system
python main_unified.py

# 3. Play loud audio near microphone (>40 dB) for >5s
# Expected: Disturbance alert in data/alerts.json
```

---

**Related Documentation**:
- [INSTITUTIONAL_BEHAVIORS.md](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/INSTITUTIONAL_BEHAVIORS.md) - Feature details
- [SYSTEM_ARCHITECTURE_V2.md](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/SYSTEM_ARCHITECTURE_V2.md) - Technical architecture

**Document Version**: 1.0  
**Maintainer**: Narendra P (@NarendraaP)  
**Last Review**: January 27, 2026
