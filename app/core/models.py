"""Database models and Pydantic schemas"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, EmailStr, validator


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    QR = "qr"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CertificateType(str, Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    VACCINATION = "vaccination"


class Department(str, Enum):
    INTERNAL_MEDICINE = "internal_medicine"
    SURGERY = "surgery"
    PEDIATRICS = "pediatrics"
    OBSTETRICS = "obstetrics"
    ORTHOPEDICS = "orthopedics"
    DERMATOLOGY = "dermatology"
    PSYCHIATRY = "psychiatry"
    EMERGENCY = "emergency"


# Database Models
class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    birthdate: datetime
    phone: str = Field(index=True)
    email: Optional[str] = None
    card_uid: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    appointments: List["Appointment"] = Relationship(back_populates="patient")
    payments: List["Payment"] = Relationship(back_populates="patient")
    certificates: List["Certificate"] = Relationship(back_populates="patient")


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    department: Department
    doctor_name: Optional[str] = None
    appointment_time: datetime
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    queue_number: Optional[int] = None
    symptoms: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: Patient = Relationship(back_populates="appointments")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    amount: Decimal = Field(decimal_places=2)
    method: PaymentMethod
    transaction_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    receipt_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: Patient = Relationship(back_populates="payments")


class Certificate(SQLModel, table=True):
    __tablename__ = "certificates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    type: CertificateType
    content: str
    doctor_name: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = None
    
    # Relationships
    patient: Patient = Relationship(back_populates="certificates")


class DeviceLog(SQLModel, table=True):
    __tablename__ = "device_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_type: str
    event: str
    level: str = Field(default="INFO")
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic Schemas for API
class PatientCreate(BaseModel):
    name: str
    birthdate: datetime
    phone: str
    email: Optional[EmailStr] = None
    card_uid: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    birthdate: datetime
    phone: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_id: int
    department: Department
    doctor_name: Optional[str] = None
    appointment_time: datetime
    symptoms: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    department: Department
    doctor_name: Optional[str]
    appointment_time: datetime
    status: AppointmentStatus
    queue_number: Optional[int]
    symptoms: Optional[str]
    
    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    patient_id: int
    amount: Decimal
    method: PaymentMethod
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    patient_id: int
    amount: Decimal
    method: PaymentMethod
    transaction_id: Optional[str]
    approved_at: Optional[datetime]
    receipt_number: Optional[str]
    
    class Config:
        from_attributes = True


class CertificateCreate(BaseModel):
    patient_id: int
    type: CertificateType
    content: str
    doctor_name: str


class CertificateResponse(BaseModel):
    id: int
    patient_id: int
    type: CertificateType
    doctor_name: str
    issued_at: datetime
    file_path: Optional[str]
    
    class Config:
        from_attributes = True


class QueueTicket(BaseModel):
    """Queue ticket response model"""
    queue_number: int
    department: str
    estimated_wait_time: int  # in minutes
    current_number: int
    location: str