"""Certificate API endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.core.database import get_session
from app.core.models import (
    CertificateCreate, CertificateResponse, CertificateType,
    PaymentMethod
)
from app.services.certificate import CertificateService

router = APIRouter()


@router.post("/issue", response_model=CertificateResponse)
async def issue_certificate(
    certificate: CertificateCreate,
    payment_method: Optional[PaymentMethod] = None,
    session: Session = Depends(get_session)
):
    """Issue new certificate"""
    service = CertificateService(session)
    
    # Prepare payment info if payment method provided
    payment_info = None
    if payment_method:
        payment_info = {
            "method": payment_method.value,
            "transaction_id": f"CERT_{certificate.patient_id}_{certificate.type.value}"
        }
    
    try:
        cert = service.issue_certificate(certificate, payment_info)
        return cert
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Certificate issuance failed")


@router.get("/types")
async def get_certificate_types():
    """Get available certificate types with fees"""
    return {
        "types": [
            {
                "id": CertificateType.DIAGNOSIS.value,
                "name": "진단서",
                "description": "의료 진단 내용을 증명하는 서류",
                "fee": 20000,
                "processing_time": "즉시 발급"
            },
            {
                "id": CertificateType.TREATMENT.value,
                "name": "진료확인서",
                "description": "진료 받은 사실을 확인하는 서류",
                "fee": 10000,
                "processing_time": "즉시 발급"
            },
            {
                "id": CertificateType.VACCINATION.value,
                "name": "예방접종증명서",
                "description": "예방접종 내역을 증명하는 서류",
                "fee": 5000,
                "processing_time": "즉시 발급"
            }
        ]
    }


@router.get("/patient/{patient_id}", response_model=List[CertificateResponse])
async def get_patient_certificates(
    patient_id: int,
    session: Session = Depends(get_session)
):
    """Get all certificates for a patient"""
    service = CertificateService(session)
    
    try:
        certificates = service.get_patient_certificates(patient_id)
        return certificates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{certificate_id}")
async def download_certificate(
    certificate_id: int,
    session: Session = Depends(get_session)
):
    """Download certificate PDF"""
    service = CertificateService(session)
    
    certificate = service.verify_certificate(certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if not certificate.file_path:
        raise HTTPException(status_code=404, detail="Certificate file not found")
    
    return FileResponse(
        certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate_id}.pdf"
    )


@router.post("/reprint/{certificate_id}")
async def reprint_certificate(
    certificate_id: int,
    session: Session = Depends(get_session)
):
    """Reprint existing certificate"""
    service = CertificateService(session)
    
    try:
        file_path = service.reprint_certificate(certificate_id)
        return {
            "status": "success",
            "message": "Certificate reprinted successfully",
            "file_path": file_path
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Reprint failed")


@router.get("/verify/{certificate_id}")
async def verify_certificate(
    certificate_id: int,
    session: Session = Depends(get_session)
):
    """Verify certificate authenticity"""
    service = CertificateService(session)
    
    certificate = service.verify_certificate(certificate_id)
    if not certificate:
        return {
            "valid": False,
            "message": "Certificate not found"
        }
    
    return {
        "valid": True,
        "certificate_id": certificate.id,
        "type": certificate.type.value,
        "issued_at": certificate.issued_at,
        "doctor_name": certificate.doctor_name
    }