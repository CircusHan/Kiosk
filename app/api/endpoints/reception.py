"""Reception API endpoints"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.models import (
    Patient, Appointment, AppointmentCreate, AppointmentResponse,
    PatientCreate, PatientResponse, QueueTicket, AppointmentStatus, Department
)
from app.core.config import DEPARTMENT_LOCATIONS, SYMPTOM_DEPARTMENT_MAP
from app.services.reception import ReceptionService

router = APIRouter()


@router.post("/check-in", response_model=QueueTicket)
async def check_in(
    patient_id: int,
    appointment_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Check in for appointment and get queue ticket"""
    service = ReceptionService(session)
    
    try:
        if appointment_id:
            # Check in with existing appointment
            ticket = service.check_in_appointment(patient_id, appointment_id)
        else:
            # Walk-in without appointment
            raise HTTPException(
                status_code=400,
                detail="Please create an appointment first"
            )
        
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/walk-in", response_model=AppointmentResponse)
async def create_walk_in(
    patient_id: int,
    symptoms: List[str],
    department: Optional[Department] = None,
    session: Session = Depends(get_session)
):
    """Create walk-in appointment"""
    service = ReceptionService(session)
    
    try:
        # Auto-select department if not provided
        if not department:
            department = service.recommend_department(symptoms)
        
        # Create appointment for walk-in
        appointment_data = AppointmentCreate(
            patient_id=patient_id,
            department=department,
            appointment_time=datetime.now(),
            symptoms=", ".join(symptoms)
        )
        
        appointment = service.create_appointment(appointment_data)
        return appointment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/appointments/{patient_id}", response_model=List[AppointmentResponse])
async def get_patient_appointments(
    patient_id: int,
    date: Optional[datetime] = Query(None),
    session: Session = Depends(get_session)
):
    """Get patient appointments"""
    query = select(Appointment).where(Appointment.patient_id == patient_id)
    
    if date:
        start = date.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        query = query.where(
            Appointment.appointment_time >= start,
            Appointment.appointment_time < end
        )
    
    appointments = session.exec(query).all()
    return appointments


@router.get("/queue-status/{department}")
async def get_queue_status(
    department: Department,
    session: Session = Depends(get_session)
):
    """Get current queue status for department"""
    service = ReceptionService(session)
    status = service.get_queue_status(department)
    
    return {
        "department": department,
        "current_number": status["current"],
        "waiting_count": status["waiting"],
        "estimated_wait_time": status["wait_time"],
        "location": DEPARTMENT_LOCATIONS.get(department, "Unknown")
    }


@router.post("/patient", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session)
):
    """Create new patient record"""
    # Check if patient already exists
    existing = session.exec(
        select(Patient).where(Patient.phone == patient.phone)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Patient with this phone number already exists"
        )
    
    db_patient = Patient(**patient.dict())
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    
    return db_patient


@router.get("/patient/search")
async def search_patient(
    phone: Optional[str] = None,
    card_uid: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Search patient by phone or card UID"""
    if not phone and not card_uid:
        raise HTTPException(
            status_code=400,
            detail="Provide either phone number or card UID"
        )
    
    query = select(Patient)
    
    if phone:
        query = query.where(Patient.phone == phone)
    elif card_uid:
        query = query.where(Patient.card_uid == card_uid)
    
    patient = session.exec(query).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientResponse.from_orm(patient)


@router.get("/departments")
async def get_departments():
    """Get list of all departments with locations"""
    departments = []
    for dept in Department:
        departments.append({
            "id": dept.value,
            "name": dept.value.replace("_", " ").title(),
            "location": DEPARTMENT_LOCATIONS.get(dept.value, "Unknown")
        })
    return departments


@router.get("/symptoms")
async def get_symptoms():
    """Get list of symptoms with recommended departments"""
    return SYMPTOM_DEPARTMENT_MAP