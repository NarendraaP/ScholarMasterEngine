# ScholarMasterEngine - Institutional Behaviors Documentation

**Purpose**: Explicit documentation of all institutional intelligence behaviors  
**Version**: 1.0  
**Last Updated**: January 27, 2026

---

## Overview

This document surfaces **implicit institutional behaviors** that are implemented in ScholarMasterEngine but not explicitly documented. These are NOT new features—they are existing capabilities that need visibility.

---

## 1. Alert & Notification System 🔔

### Architecture

**Core Components**:
- **Alert Storage**: `data/alerts.json` (JSON array)
- **Dispatcher Service**: [`NotificationDispatcher`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/notification_service.py)
- **Trigger Function**: `ScholarMasterEngine.trigger_alert()` in [`master_engine.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/master_engine.py#L524-L562)

### Alert Flow

```
Event Detected → trigger_alert(type, message, zone)
    ↓
Create Alert Object:
{
  "timestamp": "2026-01-27T10:30:00",
  "type": "Warning" | "Critical" | "Security" | "Grooming",
  "msg": "Human-readable description",
  "zone": "Physical location (e.g., 'Lab-1', 'Main Entrance')"
}
    ↓
Atomic Write to data/alerts.json
    ↓
NotificationDispatcher (polling every 2s)
    ↓
Dispatch to Recipients (role-based)
    ↓
Admin Panel Alert Center Tab
```

### Alert Types & Recipients

| Alert Type | Trigger Conditions | Recipients | Escalation |
|------------|-------------------|------------|------------|
| **Security** | • Spoof attempt detected<br>• Unauthorized presence<br>• Crowd mismatch | • Security Team<br>• Admin | Immediate |
| **Warning** | • Truancy (wrong location)<br>• Disturbance during lecture<br>• Missing student<br>• Sleeping detected | • Class Teacher<br>• HOD<br>• Admin | After 30s sustained |
| **Critical** | • Violence detected<br>• Loud noise/scream<br>• Unsupervised class | •  Security<br>• HOD<br>• Admin | Immediate |
| **Grooming** | • Non-uniform detected | • Class Teacher<br>• HOD | After verification |

### Trigger Points in Code

**Location**: `modules_legacy/master_engine.py`

```python
# Line 209: Audio Alert
if self.audio_sentinel.alert_active:
    self.trigger_alert("Warning", "Loud Noise Detected", current_zone)

# Line 234: Spoof Attempt
if not is_live:
    self.trigger_alert("Security", "Spoof Attempt Detected", current_zone)

# Line 261: Truancy
if not is_compliant:
    self.trigger_alert("Warning", f"Truancy: {student_id} in {current_zone}", current_zone)

# Line 291: Violence
if is_violence:
    self.trigger_alert("Critical", v_msg, current_zone)

# Line 326: Uniform Violation
if not is_uniform_ok:
    self.trigger_alert("Grooming", f"No Uniform - {student_id}", current_zone)

# Line 376: Sleeping
if is_sleeping:
    self.trigger_alert("Warning", s_msg, current_zone)

# Line 408: Crowd Mismatch (Intruders)
if crowd_count > face_count + 2:
    self.trigger_alert("Security", mismatch_msg, current_zone)

# Line 440: Missing Student
if crowd_count < log_count:
    self.trigger_alert("Warning", "MISSING STUDENT: ...", current_zone)
```

### Admin Panel Integration

**File**: [`admin_panel.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/admin_panel.py#L582-L645)  
**Tab**: "🔔 Alert Center" (Tab 5)

**Functionality**:
- Polls `data/alerts.json` on page refresh
- Displays alerts with color-coded severity:
  - `Security` → 🔴 Red
  - `Critical` → 🔴 Red  
  - `Warning` → 🟡 Yellow
  - `Grooming` → 🟠 Orange
- **Human-in-the-Loop Actions**:
  - ✅ **Confirm**: Acknowledge alert (removes from queue)
  - ❌ **Dismiss**: Mark as false positive (removes from queue)

---

## 2. Timetable-Driven Intelligence 📅

### Purpose

The timetable is not just a schedule—it's the **ground truth** for:
- Who should be where and when
- Faculty assignment verification
- Lecture vs. break mode detection
- Classroom occupancy expectations

### Core Engine

**Module**: [`ContextEngine`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/context_manager.py)  
**Data Source**: `data/timetable.csv`

**CSV Structure**:
```csv
day,start,end,faculty,dept,program,year,section,subject,teacher,room
Mon,10:00,11:00,Technology,Computer Science,UG,1,A,Data Structures,Ms. Davis,Lab-1
```

### Key Methods

#### `get_expected_location(student_id, day, time_str)`

**Purpose**: Look up where a student should be

**Algorithm**:
1. Load student record from `data/students.json`
2. Extract: `program`, `year`, `section`, `dept`
3. Filter timetable by:
   - `day` = current day (e.g., "Mon")
   - `program` = student's program (e.g., "UG")
   - `year` = student's year (e.g., 1)
   - `section` = student's section (e.g., "A")
   - `dept` = student's department (e.g., "Computer Science")
4. Time range check: `start_time ≤ current_time < end_time`
5. Return: `{ "room": "Lab-1", "subject": "Data Structures", "teacher": "Ms. Davis" }`

**Return Value**:
- `None` if no class scheduled (free period)
- `Dict` with expected location if class active

#### `check_compliance(student_id, current_zone, day, time_str)`

**Purpose**: Validate student is in correct location

**Returns**: `(is_compliant: bool, message: str, expected_data: dict)`

**Decision Logic**:
```python
expected = get_expected_location(student_id, day, time_str)

if expected is None:
    return (True, "Free Period", None)  # No class scheduled

if current_zone == expected["room"]:
    return (True, "Compliant", expected)  # Correct location

else:
    return (False, f"TRUANCY: Expected in {expected['room']} for {expected['subject']}", expected)
```

#### `get_class_context(zone, day, time_str)`

**Purpose**: Determine if a classroom is in "Lecture Mode" or "Break Mode"

**Returns**: `bool` (True = Lecture Active, False = Break/Free)

**Usage**:
- **Strict Mode** (Lecture): Lower noise threshold (40dB), enable truancy detection
- **Relaxed Mode** (Break): Higher noise threshold (80dB), disable strict monitoring

**Implementation** (`master_engine.py` L506-512):
```python
if is_lecture_mode:
    # Lecture Mode: Strict (40dB = 0.4 threshold for whispering)
    if current_volume > 0.4:
        self.trigger_alert("Warning", "Disturbance: Talking detected during lecture", current_zone)
else:
    # Break Mode: Relaxed (80dB = 0.8 threshold for screaming only)
    if current_volume > 0.8:
        self.trigger_alert("Critical", "Loud Noise / Scream Detected", current_zone)
```

### Faculty Assignment Verification (Implicit)

**Current Implementation**: Not explicit (future enhancement)

**Existing Logic**:
- Timetable contains `teacher` field for each period
- `get_class_context()` can check if expected faculty is present
- **Proposed Enhancement**: Create dedicated `faculty_tracker.py` module

**How It Would Work** (based on existing data):
1. Period starts (e.g., Mon 10:00, Data Structures, Teacher: Ms. Davis)
2. System checks: Is faculty face detected in `zone="Lab-1"`?
3. If NO faculty after 2-minute grace period:
   - Trigger alert: "Faculty Absence - Ms. Davis, Data Structures, Lab-1"
4. Recipients: HOD (Computer Science), Admin

---

## 3. Lecture Capture & Monitoring 🎤

### Purpose

Monitor lecture quality and integrity WITHOUT violating privacy (Paper 3, Paper 6).

### Components

#### Audio Capture

**Module**: [`AudioSentinel`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/audio_sentinel.py)

**Method**: Spectral analysis (FFT) - **NO speech recognition**

**Privacy Compliance**:
- ✅ Audio buffer cleared after processing
- ✅ Only dB level and spectral features extracted
- ✅ No raw audio stored
- ❌ No speech-to-text (unless explicitly enabled via `LectureScribe`)

**Features Extracted**:
```python
{
  "db": 65.4,  # Decibel level
  "spectral_centroid": 2500.0,  # Hz (dominantfrequency)
  "zero_crossing_rate": 0.15  # Voice activity indicator
}
```

#### Speech Activity Detection

**Algorithm**: Short-Time Fourier Transform (STFT) with spectral gating

**Used For**:
- Lecture presence inference (teacher speaking)
- Disturbance detection (excessive noise during lecture)
- Silence detection (potential class skip)

**NOT Used For**:
- Speech recognition
- Individual voice identification
- Conversation content extraction

#### Lecture Scribe (Optional)

**Module**: [`LectureScribe`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/scribe.py)

**Technology**: OpenAI Whisper (if enabled)

**Privacy Considerations**:
- ⚠️ Disabled by default (privacy-sensitive)
- Uses local Whisper model (no cloud transmission)
- Transcripts stored as metadata only (no audio files)
- Requires explicit admin configuration

**Use Case**: Accessibility (automated lecture notes for students with hearing impairments)

### Lecture Validation Logic

**Location**: `master_engine.py` L385-396

**Criteria** (ALL must be true for valid lecture):
1. ✅ Faculty face identified in room
2. ✅ Student count > 0 (attendance log exists)
3. ✅ Audio activity in normal range (30-70 dB)

**Validation Outcomes**:
- **Valid Lecture**: Log metadata (timestamp, subject, faculty_id, student_count, avg_audio_db)
- **Missing Faculty**: Alert "Unsupervised class"
- **Silence Detected**: Alert "Potential class skip"
- **Excessive Noise**: Alert "Disturbance during lecture"

### Metadata Logged (Privacy-Preserving)

**File**: `data/session_log.csv`

**Columns**:
```csv
timestamp,date,subject,emotion,zone
2026-01-27T10:30:00,2026-01-27,Data Structures,Engaged,Lab-1
```

**NOT Logged**:
- ❌ Student names (only privacy_hash)
- ❌ Raw audio
- ❌ Speech transcripts (unless Scribe enabled)
- ❌ Face images

---

## 4. Multi-Actor RBAC Model 👥

### Role Hierarchy

```
Super Admin (Full System Access)
    │
    ├─ Faculty Manager (Department-Scoped)
    │   │
    │   └─ Faculty (Class-Scoped)
    │       │
    │       └─ Class Teacher (Student Alert Recipient)
    │
    ├─ Security (Alert Recipient Only)
    │
    ├─ Student (Self-Service Only)
    │
    └─ Non-Teaching Staff (Implicit in alerts)
```

### Role Definitions

#### 1. Super Admin

**Capabilities**:
- ✅ User provisioning (create/delete users)
- ✅ Full timetable management
- ✅ All alert visibility
- ✅ System configuration
- ✅ Biometric enrollment (all departments)
- ✅ Attendance modification
- ✅ Analytics (institution-wide)

**Admin Panel Access**: All 7 tabs

#### 2. Faculty Manager

**Capabilities**:
- ✅ Biometric enrollment (department-scoped)
- ✅ Timetable viewing (department-scoped)
- ✅ Analytics (department-scoped)
- ✅ Attendance logs (department-scoped)
- ❌ User provisioning (Super Admin only)
- ❌ System configuration

**Admin Panel Access**: 4 tabs (Enrollment, Analytics, Attendance, Alert Center)

**Department Scoping**: Set via `manager_dept` field in user record

#### 3. Faculty

**Capabilities**:
- ✅ Attendance logs (own classes only)
- ✅ Analytics (own classes only)
- ✅ Timetable viewing (own schedule)
- ❌ Biometric enrollment
- ❌ Alert management

**Admin Panel Access**: 2 tabs (Attendance, Analytics - filtered)

#### 4. Class Teacher

**Role**: Receive alerts for assigned class

**Capabilities**:
- ✅ Receive truancy alerts for class students
- ✅ Receive uniform violation alerts
- ✅ Receive engagement alerts (low participation)

**Assignment**: Via timetable `teacher` field

**Alert Routing** (implicit in system):
```python
# When truancy detected for student in Section A
expected_data = context_engine.check_compliance(...)
teacher = expected_data["teacher"]  # "Ms. Davis"
# Alert routed to Ms. Davis
```

#### 5. Student

**Capabilities**:
- ✅ View own attendance
- ❌ View others' attendance
- ❌ Modify any data
- ❌ Alert center access

**Admin Panel Access**: 1 tab (Attendance - self only)

#### 6. Security

**Capabilities**:
- ✅ Receive security alerts (spoof attempts, crowd mismatch, violence)
- ✅ Receive critical alerts (unsupervised class, loud noise)
- ❌ Administrative functions

**Implementation**: Not in admin panel (separate monitoring station)

#### 7. Non-Teaching Staff (Implicit)

**Examples**: Janitors, security guards, administrative staff

**Current Implementation**: Marked in alerts but no dedicated user accounts

**Future Enhancement**: Create "Staff" role with limited biometric enrollment

### RBAC Implementation

**Module**: [`auth.py`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/auth.py)

**Decorator**: `@requires_role(*allowed_roles)`

**Usage Example**:
```python
@requires_role('Super Admin', 'Faculty Manager')
def enroll_student_ui():
    # Only Super Admin and Faculty Manager can access
    ...
```

**Backend Validation**: `validate_role(allowed_roles, user_role)`

```python
# In FaceRegistry.register_face()
validate_role(['Admin', 'Faculty Manager'], user_role)
if user_role not in ['Admin', 'Faculty Manager']:
    raise PermissionError("Access Denied: ...")
```

---

## 5. Context-Aware Audio Monitoring 🔊

### Dual-Mode Thresholding

**Mode Detection**: `get_class_context(zone, day, time)`

#### Lecture Mode (Strict)

**Threshold**: 40 dB (whisper level)

**Rationale**: Maintain focus, minimize distractions

**Triggers**:
- Volume > 40 dB → "Warning: Disturbance - Talking detected during lecture"
- Sustained 30s → Escalate to Class Teacher, HOD

#### Break Mode (Relaxed)

**Threshold**: 80 dB (shout level)

**Rationale**: Allow normal conversation, only flag emergencies

**Triggers**:
- Volume > 80 dB → "Critical: Loud Noise / Scream Detected"
- Immediate escalation to Security, Admin

### Integration with Safety Detection

**Combined Logic** (`master_engine.py` L499-523):

```python
def check_audio(self, frame, current_zone, is_lecture_mode):
    current_volume = self.audio_sentinel.current_volume
    
    if is_lecture_mode:
        if current_volume > 0.4:  # 40dB
            self.trigger_alert("Warning", "Disturbance: Talking detected during lecture", current_zone)
    else:
        if current_volume > 0.8:  # 80dB
            self.trigger_alert("Critical", "Loud Noise / Scream Detected", current_zone)
```

---

## 6. Attendance Debounce Logic ⏱️

### Problem

Without debounce: If a student's face is detected 30 times per second (30 FPS), attendance would be logged 30 times.

### Solution

**Module**: [`AttendanceManager`](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/modules_legacy/attendance_logger.py)

**Method**: `mark_present(student_id, context_data, user_role)`

**Debounce Logic** (L73-81):
```python
# Check if already marked present for this subject today
today = datetime.date.today().isoformat()
df_today = self.df[
    (self.df['student_id'] == student_id) &
    (self.df['date'] == today) &
    (self.df['subject'] == context_data['subject'])
]

if not df_today.empty:
    return "Already Marked Present"  # Debounce: Prevent duplicate
```

**Key**: Unique constraint on `(student_id, date, subject)`

### Visual Feedback

**Location**: `master_engine.py` (attendance integration)

**Display**:
- ✅ Green overlay: "✅ ATTENDANCE SAVED" (2 seconds)
- 📝 Console log: `[ATTENDANCE] Logged: {student_id} for {subject}`

---

## 7. Safety Detection Ensemble 🛡️

### Violence Detection

**Method**: `SafetyEngine.detect_violence(keypoints_list)`

**Algorithm**:
1. **Inter-Person Distance Check**:
   - Calculate distance between all person pairs
   - If distance < 50px → Proximity violation
2. **Aggressive Posture Detection**:
   - Check arm angles (raised arms, striking pose)
   - Shoulder-elbow-wrist angle < 90° → Potential aggression
3. **Combine Signals**:
   - Proximity + Posture → High confidence violence

**Returns**: `(is_violent: bool, message: str)`

**Example Message**: "Proximity Violation AND Aggressive Posture"

### Sleep Detection

**Method**: `SafetyEngine.detect_sleeping(keypoints_list)`

**Algorithm**:
1. **Head-Down Posture**:
   - Nose keypoint Y-coordinate > shoulder Y-coordinate
   - Head tilt angle > 30°
2. **Sustained Duration**:
   - Sleep counter > 30 frames (1 second at 30 FPS)

**Returns**: `(is_sleeping: bool, message: str, indices: List[int])`

**False Positive Prevention**: 30-frame persistence counter

### Uniform Compliance

**Method**: `GroomingInspector.check_uniform(frame, keypoints)`

**Algorithm**:
1. Extract torso region (shoulders to hips)
2. Color analysis:
   - Expected uniform color range (configurable)
   - HSV color space comparison
3. Pattern detection (optional):
   - Logo detection via template matching

**Returns**: `(is_uniform_ok: bool, message: str)`

**Visual Indicator**: Orange bounding box around torso if non-compliant

---

## Summary: Institutional Intelligence Map

| Behavior | Trigger | Module | Output |
|----------|---------|--------|--------|
| **Student Entry** | Face detected → FAISS search | `FaceRegistry` | Student ID |
| **Compliance Check** | Student ID + Zone + Time | `ContextEngine` | Compliant / Truancy |
| **Attendance Log** | Compliant student | `AttendanceManager` | CSV entry (debounced) |
| **Faculty Absence** | Period start + No faculty | `ContextEngine` (implicit) | Alert to HOD/Admin |
| **Lecture Validation** | Faculty + Students + Audio | `AudioSentinel` + `ContextEngine` | Metadata log |
| **Disturbance Alert** | Audio > Threshold (context-aware) | `AudioSentinel` | Alert (Warning/Critical) |
| **Violence Detection** | Proximity + Posture | `SafetyEngine` | Security alert |
| **Sleep Detection** | Head-down > 30 frames | `SafetyEngine` | Warning alert |
| **Uniform Check** | Torso color analysis | `GroomingInspector` | Grooming alert |
| **Crowd Mismatch** | YOLO count ≠ Face count | `ScholarMasterEngine` | Security alert |

---

**Next**: See [END_TO_END_SCENARIOS.md](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/END_TO_END_SCENARIOS.md) for detailed flow walkthroughs.

**Document Version**: 1.0  
**Maintainer**: Narendra P (@NarendraaP)  
**Last Review**: January 27, 2026
