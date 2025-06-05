"""Payment API endpoints"""

from typing import List, Dict
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_session
from app.core.models import PaymentCreate, PaymentResponse, PaymentMethod
from app.services.payment import PaymentService

router = APIRouter()


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    patient_id: int,
    amount: float,
    method: PaymentMethod,
    transaction_data: Dict = None,
    session: Session = Depends(get_session)
):
    """Process payment transaction"""
    service = PaymentService(session)
    
    try:
        payment = service.process_payment(
            patient_id=patient_id,
            amount=Decimal(str(amount)),
            method=method,
            transaction_data=transaction_data
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment processing failed")


@router.get("/pending/{patient_id}")
async def get_pending_payments(
    patient_id: int,
    session: Session = Depends(get_session)
):
    """Get pending payments for patient"""
    service = PaymentService(session)
    
    try:
        pending = service.get_pending_payments(patient_id)
        return {
            "patient_id": patient_id,
            "pending_payments": pending,
            "total_amount": sum(p["amount"] for p in pending)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{patient_id}", response_model=List[PaymentResponse])
async def get_payment_history(
    patient_id: int,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Get payment history for patient"""
    service = PaymentService(session)
    
    try:
        payments = service.get_payment_history(patient_id, limit)
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refund/{payment_id}", response_model=PaymentResponse)
async def refund_payment(
    payment_id: int,
    reason: str,
    session: Session = Depends(get_session)
):
    """Process payment refund"""
    service = PaymentService(session)
    
    try:
        refund = service.refund_payment(payment_id, reason)
        return refund
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Refund processing failed")


@router.get("/receipt/{payment_id}")
async def get_receipt(
    payment_id: int,
    session: Session = Depends(get_session)
):
    """Get payment receipt"""
    service = PaymentService(session)
    
    try:
        receipt = service.generate_receipt(payment_id)
        return receipt
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods")
async def get_payment_methods():
    """Get available payment methods"""
    return {
        "methods": [
            {
                "id": PaymentMethod.CASH.value,
                "name": "현금",
                "icon": "cash",
                "enabled": True
            },
            {
                "id": PaymentMethod.CARD.value,
                "name": "카드",
                "icon": "credit-card",
                "enabled": True
            },
            {
                "id": PaymentMethod.QR.value,
                "name": "QR 결제",
                "icon": "qr-code",
                "enabled": True
            }
        ]
    }