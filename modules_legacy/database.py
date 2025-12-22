from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Database Setup
DB_PATH = "sqlite:///data/campus.db"
Base = declarative_base()

# --- Models ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)

class Student(Base):
    __tablename__ = 'students'
    id = Column(String, primary_key=True) # Student ID is string (e.g., "S101")
    name = Column(String, nullable=False)
    dept = Column(String)
    section = Column(String)
    privacy_hash = Column(String)

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    day = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    teacher = Column(String)
    room = Column(String)

class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    student_id = Column(String)
    event_type = Column(String, nullable=False) # e.g., "Attendance", "Security", "Truancy"
    details = Column(Text)

# --- Engine & Session ---

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize on import (safe for SQLite)
init_db()
