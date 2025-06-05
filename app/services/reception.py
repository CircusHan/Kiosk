"""Reception service logic"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlmodel import Session, select, func
from app.core.models import (
    Patient, Appointment, AppointmentCreate, AppointmentStatus,
    Department, QueueTicket
)
from app.core.config import DEPARTMENT_LOCATIONS, SYMPTOM_DEPARTMENT_MAP

logger = logging.getLogger(__name__)


class ReceptionService:
    """Handle reception-related business logic"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """Create new appointment"""
        # Verify patient exists
        patient = self.session.get(Patient, appointment_data.patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {appointment_data.patient_id} not found")
        
        # Create appointment
        appointment = Appointment(**appointment_data.dict())
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        
        logger.info(f"Created appointment {appointment.id} for patient {patient.name}")
        return appointment
    
    def check_in_appointment(self, patient_id: int, appointment_id: int) -> QueueTicket:
        """Check in for existing appointment"""
        # Get appointment
        appointment = self.session.get(Appointment, appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.patient_id != patient_id:
            raise ValueError("Appointment does not belong to this patient")
        
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise ValueError(f"Appointment is already {appointment.status}")
        
        # Update status and assign queue number
        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.queue_number = self._get_next_queue_number(appointment.department)
        
        self.session.add(appointment)
        self.session.commit()
        
        # Create queue ticket
        queue_status = self.get_queue_status(appointment.department)
        
        ticket = QueueTicket(
            queue_number=appointment.queue_number,
            department=appointment.department.value,
            estimated_wait_time=queue_status["wait_time"],
            current_number=queue_status["current"],
            location=DEPARTMENT_LOCATIONS.get(appointment.department.value, "Unknown")
        )
        
        logger.info(f"Checked in appointment {appointment_id}, queue number: {appointment.queue_number}")
        return ticket
    
    def create_walk_in_appointment(
        self,
        patient_id: int,
        symptoms: List[str],
        department: Optional[Department] = None
    ) -> Appointment:
        """Create walk-in appointment"""
        # Verify patient
        patient = self.session.get(Patient, patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Auto-select department if not provided
        if not department:
            department = self.recommend_department(symptoms)
        
        # Create appointment
        appointment_data = AppointmentCreate(
            patient_id=patient_id,
            department=department,
            appointment_time=datetime.now(),
            symptoms=", ".join(symptoms)
        )
        
        appointment = self.create_appointment(appointment_data)
        
        # Auto check-in for walk-ins
        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.queue_number = self._get_next_queue_number(department)
        
        self.session.add(appointment)
        self.session.commit()
        
        logger.info(f"Created walk-in appointment {appointment.id} for patient {patient.name}")
        return appointment
    
    def recommend_department(self, symptoms: List[str]) -> Department:
        """Recommend department based on symptoms"""
        department_scores = {}
        
        for symptom in symptoms:
            if symptom in SYMPTOM_DEPARTMENT_MAP:
                for dept in SYMPTOM_DEPARTMENT_MAP[symptom]:
                    if dept not in department_scores:
                        department_scores[dept] = 0
                    department_scores[dept] += 1
        
        if department_scores:
            # Return department with highest score
            recommended = max(department_scores, key=department_scores.get)
            return Department(recommended)
        else:
            # Default to internal medicine
            return Department.INTERNAL_MEDICINE
    
    def get_queue_status(self, department: Department) -> Dict:
        """Get current queue status for department"""
        # Get current appointments
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        # Count waiting appointments
        waiting_query = select(func.count(Appointment.id)).where(
            Appointment.department == department,
            Appointment.status == AppointmentStatus.CHECKED_IN,
            Appointment.appointment_time >= today_start
        )
        waiting_count = self.session.exec(waiting_query).one()
        
        # Get current number being served
        current_query = select(Appointment).where(
            Appointment.department == department,
            Appointment.status == AppointmentStatus.IN_PROGRESS,
            Appointment.appointment_time >= today_start
        ).order_by(Appointment.queue_number)
        
        current_appointment = self.session.exec(current_query).first()
        current_number = current_appointment.queue_number if current_appointment else 0
        
        # Estimate wait time (15 minutes per patient)
        estimated_wait = waiting_count * 15
        
        return {
            "current": current_number,
            "waiting": waiting_count,
            "wait_time": estimated_wait
        }
    
    def _get_next_queue_number(self, department: Department) -> int:
        """Get next queue number for department"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        # Get max queue number for today
        max_query = select(func.max(Appointment.queue_number)).where(
            Appointment.department == department,
            Appointment.appointment_time >= today_start
        )
        
        max_number = self.session.exec(max_query).one()
        return (max_number or 0) + 1
    
    def get_patient_appointments(
        self,
        patient_id: int,
        date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get patient appointments"""
        query = select(Appointment).where(Appointment.patient_id == patient_id)
        
        if date:
            start = date.replace(hour=0, minute=0, second=0)
            end = start + timedelta(days=1)
            query = query.where(
                Appointment.appointment_time >= start,
                Appointment.appointment_time < end
            )
        
        query = query.order_by(Appointment.appointment_time.desc())
        appointments = self.session.exec(query).all()
        
        return appointments
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel appointment"""
        appointment = self.session.get(Appointment, appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel appointment with status {appointment.status}")
        
        appointment.status = AppointmentStatus.CANCELLED
        self.session.add(appointment)
        self.session.commit()
        
        logger.info(f"Cancelled appointment {appointment_id}")
        return True
    
    def update_appointment_status(
        self,
        appointment_id: int,
        status: AppointmentStatus
    ) -> Appointment:
        """Update appointment status"""
        appointment = self.session.get(Appointment, appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = status
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        
        logger.info(f"Updated appointment {appointment_id} status to {status}")
        return appointment