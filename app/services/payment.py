"""Payment processing service"""

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, List
from sqlmodel import Session, select
from app.core.models import (
    Patient, Payment, PaymentCreate, PaymentMethod,
    Appointment, AppointmentStatus
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PaymentService:
    """Handle payment processing logic"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def process_payment(
        self,
        patient_id: int,
        amount: Decimal,
        method: PaymentMethod,
        transaction_data: Optional[Dict] = None
    ) -> Payment:
        """Process payment transaction"""
        # Verify patient
        patient = self.session.get(Patient, patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Create payment record
        payment = Payment(
            patient_id=patient_id,
            amount=amount,
            method=method,
            transaction_id=transaction_data.get("transaction_id") if transaction_data else None
        )
        
        # Process based on payment method
        try:
            if method == PaymentMethod.CASH:
                payment = self._process_cash_payment(payment, transaction_data)
            elif method == PaymentMethod.CARD:
                payment = self._process_card_payment(payment, transaction_data)
            elif method == PaymentMethod.QR:
                payment = self._process_qr_payment(payment, transaction_data)
            else:
                raise ValueError(f"Unsupported payment method: {method}")
            
            # Save payment record
            self.session.add(payment)
            self.session.commit()
            self.session.refresh(payment)
            
            logger.info(f"Payment {payment.id} processed successfully for patient {patient.name}")
            return payment
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            raise
    
    def _process_cash_payment(
        self,
        payment: Payment,
        transaction_data: Optional[Dict]
    ) -> Payment:
        """Process cash payment"""
        # In real system, this would interface with cash acceptor hardware
        payment.approved_at = datetime.utcnow()
        payment.receipt_number = self._generate_receipt_number()
        
        # Log cash received
        if transaction_data:
            received = transaction_data.get("received_amount", 0)
            change = Decimal(str(received)) - payment.amount
            logger.info(f"Cash payment: received {received}, change {change}")
        
        return payment
    
    def _process_card_payment(
        self,
        payment: Payment,
        transaction_data: Optional[Dict]
    ) -> Payment:
        """Process card payment"""
        # In real system, this would call payment gateway API
        if not transaction_data or "card_number" not in transaction_data:
            raise ValueError("Card information required")
        
        # Mock payment gateway call
        card_last4 = transaction_data["card_number"][-4:]
        payment.transaction_id = f"CARD_{uuid.uuid4().hex[:8]}_{card_last4}"
        payment.approved_at = datetime.utcnow()
        payment.receipt_number = self._generate_receipt_number()
        
        logger.info(f"Card payment approved: {payment.transaction_id}")
        return payment
    
    def _process_qr_payment(
        self,
        payment: Payment,
        transaction_data: Optional[Dict]
    ) -> Payment:
        """Process QR code payment"""
        # In real system, this would verify QR payment with provider
        if not transaction_data or "qr_code" not in transaction_data:
            raise ValueError("QR code required")
        
        # Mock QR payment verification
        payment.transaction_id = f"QR_{uuid.uuid4().hex[:8]}"
        payment.approved_at = datetime.utcnow()
        payment.receipt_number = self._generate_receipt_number()
        
        logger.info(f"QR payment verified: {payment.transaction_id}")
        return payment
    
    def _generate_receipt_number(self) -> str:
        """Generate unique receipt number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[:4].upper()
        return f"RCP-{timestamp}-{random_suffix}"
    
    def get_pending_payments(self, patient_id: int) -> List[Dict]:
        """Get pending payments for patient"""
        # Get today's appointments
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        appointments = self.session.exec(
            select(Appointment).where(
                Appointment.patient_id == patient_id,
                Appointment.appointment_time >= today_start,
                Appointment.status.in_([
                    AppointmentStatus.COMPLETED,
                    AppointmentStatus.IN_PROGRESS
                ])
            )
        ).all()
        
        pending_payments = []
        for appointment in appointments:
            # Check if already paid
            existing_payment = self.session.exec(
                select(Payment).where(
                    Payment.patient_id == patient_id,
                    Payment.created_at >= appointment.appointment_time
                )
            ).first()
            
            if not existing_payment:
                # Calculate amount based on department
                amount = self._calculate_consultation_fee(appointment.department)
                pending_payments.append({
                    "appointment_id": appointment.id,
                    "department": appointment.department.value,
                    "amount": amount,
                    "description": f"진료비 - {appointment.department.value}"
                })
        
        return pending_payments
    
    def _calculate_consultation_fee(self, department) -> Decimal:
        """Calculate consultation fee by department"""
        # Mock fee calculation
        base_fees = {
            "internal_medicine": 15000,
            "surgery": 25000,
            "pediatrics": 12000,
            "obstetrics": 20000,
            "orthopedics": 18000,
            "dermatology": 15000,
            "psychiatry": 30000,
            "emergency": 50000
        }
        return Decimal(str(base_fees.get(department.value, 15000)))
    
    def get_payment_history(
        self,
        patient_id: int,
        limit: int = 10
    ) -> List[Payment]:
        """Get payment history for patient"""
        payments = self.session.exec(
            select(Payment).where(
                Payment.patient_id == patient_id
            ).order_by(
                Payment.created_at.desc()
            ).limit(limit)
        ).all()
        
        return payments
    
    def refund_payment(
        self,
        payment_id: int,
        reason: str
    ) -> Payment:
        """Process payment refund"""
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if not payment.approved_at:
            raise ValueError("Cannot refund unapproved payment")
        
        # Create refund record (negative amount)
        refund = Payment(
            patient_id=payment.patient_id,
            amount=-payment.amount,
            method=payment.method,
            transaction_id=f"REFUND_{payment.transaction_id}",
            approved_at=datetime.utcnow(),
            receipt_number=self._generate_receipt_number()
        )
        
        self.session.add(refund)
        self.session.commit()
        
        logger.info(f"Refund processed for payment {payment_id}: {reason}")
        return refund
    
    def generate_receipt(self, payment_id: int) -> Dict:
        """Generate receipt data for payment"""
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        patient = self.session.get(Patient, payment.patient_id)
        
        receipt = {
            "receipt_number": payment.receipt_number,
            "date": payment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "patient_name": patient.name,
            "amount": float(payment.amount),
            "method": payment.method.value,
            "transaction_id": payment.transaction_id,
            "hospital_name": settings.app_name,
            "items": []  # Would be populated with actual service items
        }
        
        return receipt