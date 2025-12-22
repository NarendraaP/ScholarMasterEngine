"""
FastAPI REST API Layer

Provides HTTP endpoints for the ScholarMasterEngine.
Demonstrates scalability and modern API design.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
from typing import Optional

from di.container import get_container, DIContainer

# Initialize FastAPI
app = FastAPI(
    title="ScholarMaster API",
    description="REST API for AI-powered campus monitoring",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for container
def get_di_container() -> DIContainer:
    """Get DI container instance"""
    return get_container()


# Request/Response Models
class RegisterStudentRequest(BaseModel):
    student_id: str
    name: str
    role: str = "Student"
    department: str
    program: str
    year: int
    section: str


class RegisterStudentResponse(BaseModel):
    success: bool
    message: str
    student_id: Optional[str] = None


class AttendanceRequest(BaseModel):
    student_id: str
    subject: str
    room: str
    is_truant: bool = False


class AttendanceResponse(BaseModel):
    success: bool
    message: str


class StudentInfoResponse(BaseModel):
    id: str
    name: str
    department: str
    program: str
    year: int
    section: str
    class_identifier: str


# Health check endpoint
@app.get("/")
def root():
    """API root endpoint"""
    return {
        "service": "ScholarMaster API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Student Registration Endpoint
@app.post("/api/students/register", response_model=RegisterStudentResponse)
async def register_student(
    image: UploadFile = File(...),
    request: RegisterStudentRequest = Depends(),
    container: DIContainer = Depends(get_di_container)
):
    """
    Register a new student with biometric data.
    
    - **image**: Face image file (JPEG, PNG)
    - **student_id**: Unique student identifier
    - **name**: Student name
    - **department**: Department code (e.g., "CS")
    - **program**: "UG" or "PG"
    - **year**: Year (1-4)
    - **section**: Section ("A", "B", "C")
    """
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Call use case
        success, message = container.register_student.execute(
            image=img,
            student_id=request.student_id,
            name=request.name,
            role=request.role,
            department=request.department,
            program=request.program,
            year=request.year,
            section=request.section
        )
        
        if success:
            return RegisterStudentResponse(
                success=True,
                message=message,
                student_id=request.student_id
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Attendance Marking Endpoint
@app.post("/api/attendance/mark", response_model=AttendanceResponse)
def mark_attendance(
    request: AttendanceRequest,
    container: DIContainer = Depends(get_di_container)
):
    """
    Mark attendance for a student.
    
    - **student_id**: Student identifier
    - **subject**: Subject name
    - **room**: Room/location
    - **is_truant**: True if student is in wrong location
    """
    try:
        success, message = container.mark_attendance.execute(
            student_id=request.student_id,
            subject=request.subject,
            room=request.room,
            is_truant=request.is_truant
        )
        
        if success:
            return AttendanceResponse(success=True, message=message)
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Student Recognition Endpoint
@app.post("/api/students/recognize")
async def recognize_student(
    image: UploadFile = File(...),
    container: DIContainer = Depends(get_di_container)
):
    """
    Recognize a student from face image.
    
    - **image**: Face image file (JPEG, PNG)
    
    Returns student information if recognized.
    """
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Call use case
        found, student_id, student_data = container.recognize_student.execute(img)
        
        if found:
            return {
                "recognized": True,
                "student": student_data
            }
        else:
            return {
                "recognized": False,
                "message": "Student not recognized"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Student Info
@app.get("/api/students/{student_id}", response_model=StudentInfoResponse)
def get_student(
    student_id: str,
    container: DIContainer = Depends(get_di_container)
):
    """
    Get student information by ID.
    
    - **student_id**: Student identifier
    """
    student = container.get_student_repository().get_by_id(student_id)
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return StudentInfoResponse(
        id=student.id,
        name=student.name,
        department=student.department,
        program=student.program,
        year=student.year,
        section=student.section,
        class_identifier=student.get_class_identifier()
    )


# List All Students
@app.get("/api/students")
def list_students(container: DIContainer = Depends(get_di_container)):
    """Get list of all registered students"""
    students = container.get_student_repository().get_all()
    
    return {
        "count": len(students),
        "students": [
            {
                "id": s.id,
                "name": s.name,
                "department": s.department,
                "class": s.get_class_identifier()
            }
            for s in students
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ScholarMaster API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
