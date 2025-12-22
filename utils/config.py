"""
Configuration management using environment variables with sensible defaults.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))
MODELS_PATH = os.getenv("MODELS_PATH", str(BASE_DIR / "models"))

# Database files
STUDENTS_DB = os.path.join(DATA_PATH, os.getenv("STUDENTS_DB", "students.json"))
ATTENDANCE_DB = os.path.join(DATA_PATH, os.getenv("ATTENDANCE_DB", "attendance.csv"))
TIMETABLE_DB = os.path.join(DATA_PATH, os.getenv("TIMETABLE_DB", "timetable.csv"))
ALERTS_DB = os.path.join(DATA_PATH, os.getenv("ALERTS_DB", "alerts.json"))
SESSION_LOG = os.path.join(DATA_PATH, os.getenv("SESSION_LOG", "session_log.csv"))

# FAISS Index
FAISS_INDEX_PATH = os.path.join(DATA_PATH, os.getenv("FAISS_INDEX_PATH", "face_index.faiss"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# Face Recognition
FACE_RECOGNITION_MODEL = os.getenv("FACE_RECOGNITION_MODEL", "buffalo_l")
FACE_SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD", "0.5"))

# Audio Sentinel
AUDIO_THRESHOLD_DB = int(os.getenv("AUDIO_THRESHOLD_DB", "70"))
SCREAMING_DURATION_SEC = int(os.getenv("SCREAMING_DURATION_SEC", "2"))

# Performance
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

# Security
SESSION_TIMEOUT_MIN = int(os.getenv("SESSION_TIMEOUT_MIN", "30"))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))

# Development
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENABLE_PROFILING = os.getenv("ENABLE_PROFILING", "false").lower() == "true"


def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        DATA_PATH,
        MODELS_PATH,
        os.path.dirname(LOG_FILE) if LOG_FILE else "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
ensure_directories()
