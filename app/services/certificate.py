"""Certificate issuance service"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from sqlmodel import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.models import (
    Patient, Certificate, CertificateCreate, CertificateType,
    Payment, PaymentMethod
)
from app.core.config import CERTIFICATE_TEMPLATES, get_settings
from app.services.payment import PaymentService

logger = logging.getLogger(__name__)
settings = get_settings()


class CertificateService:
    """Handle certificate issuance logic"""
    
    def __init__(self, session: Session):
        self.session = session
        self.output_dir = Path("static/certificates")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Setup Korean fonts for PDF generation"""
        try:
            # Register Korean font (NanumGothic)
            font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Korean', font_path))
            else:
                logger.warning("Korean font not found, using default font")
        except Exception as e:
            logger.error(f"Failed to register Korean font: {e}")
    
    def issue_certificate(
        self,
        certificate_data: CertificateCreate,
        payment_info: Optional[Dict] = None
    ) -> Certificate:
        """Issue new certificate"""
        # Verify patient
        patient = self.session.get(Patient, certificate_data.patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {certificate_data.patient_id} not found")
        
        # Process payment if required
        if payment_info:
            payment_service = PaymentService(self.session)
            payment = payment_service.process_payment(
                patient_id=certificate_data.patient_id,
                amount=self._get_certificate_fee(certificate_data.type),
                method=PaymentMethod(payment_info["method"]),
                transaction_data=payment_info
            )
            logger.info(f"Payment processed for certificate: {payment.id}")
        
        # Create certificate record
        certificate = Certificate(**certificate_data.dict())
        self.session.add(certificate)
        self.session.commit()
        self.session.refresh(certificate)
        
        # Generate PDF
        pdf_path = self._generate_certificate_pdf(certificate, patient)
        certificate.file_path = str(pdf_path)
        
        self.session.add(certificate)
        self.session.commit()
        
        logger.info(f"Issued {certificate.type} certificate {certificate.id} for patient {patient.name}")
        return certificate
    
    def _get_certificate_fee(self, cert_type: CertificateType) -> float:
        """Get certificate issuance fee"""
        fees = {
            CertificateType.DIAGNOSIS: 20000,
            CertificateType.TREATMENT: 10000,
            CertificateType.VACCINATION: 5000
        }
        return fees.get(cert_type, 10000)
    
    def _generate_certificate_pdf(self, certificate: Certificate, patient: Patient) -> Path:
        """Generate certificate PDF"""
        filename = f"{certificate.type.value}_{certificate.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=30*mm,
            bottomMargin=30*mm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            leading=20,
            spaceAfter=10
        )
        
        # Build content
        story = []
        
        # Title
        title_map = {
            CertificateType.DIAGNOSIS: "진 단 서",
            CertificateType.TREATMENT: "진료확인서",
            CertificateType.VACCINATION: "예방접종증명서"
        }
        title = Paragraph(title_map[certificate.type], title_style)
        story.append(title)
        story.append(Spacer(1, 20*mm))
        
        # Certificate number
        cert_no = Paragraph(f"<b>증명서 번호:</b> {certificate.id}", normal_style)
        story.append(cert_no)
        story.append(Spacer(1, 10*mm))
        
        # Patient information table
        patient_data = [
            ['환자 정보', ''],
            ['성명', patient.name],
            ['생년월일', patient.birthdate.strftime('%Y년 %m월 %d일')],
            ['연락처', patient.phone]
        ]
        
        patient_table = Table(patient_data, colWidths=[60*mm, 100*mm])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 15*mm))
        
        # Certificate content
        content_title = Paragraph("<b>증명 내용</b>", normal_style)
        story.append(content_title)
        
        content_text = Paragraph(certificate.content, normal_style)
        story.append(content_text)
        story.append(Spacer(1, 20*mm))
        
        # Footer
        footer_text = f"""
        위와 같이 증명합니다.<br/><br/>
        발급일자: {certificate.issued_at.strftime('%Y년 %m월 %d일')}<br/>
        담당의사: {certificate.doctor_name}<br/>
        의료기관: {settings.app_name}<br/>
        """
        footer = Paragraph(footer_text, normal_style)
        story.append(footer)
        
        # Official seal placeholder
        story.append(Spacer(1, 15*mm))
        seal_text = "[직인]"
        seal = Paragraph(seal_text, ParagraphStyle(
            'Seal',
            parent=styles['Normal'],
            fontSize=14,
            alignment=2  # Right align
        ))
        story.append(seal)
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Generated certificate PDF: {filepath}")
        return filepath
    
    def get_patient_certificates(self, patient_id: int) -> list:
        """Get all certificates for a patient"""
        certificates = self.session.query(Certificate).filter(
            Certificate.patient_id == patient_id
        ).order_by(Certificate.issued_at.desc()).all()
        
        return certificates
    
    def verify_certificate(self, certificate_id: int) -> Optional[Certificate]:
        """Verify certificate authenticity"""
        certificate = self.session.get(Certificate, certificate_id)
        if certificate:
            logger.info(f"Certificate {certificate_id} verified")
        else:
            logger.warning(f"Certificate {certificate_id} not found")
        
        return certificate
    
    def reprint_certificate(self, certificate_id: int) -> Optional[str]:
        """Reprint existing certificate"""
        certificate = self.session.get(Certificate, certificate_id)
        if not certificate:
            raise ValueError(f"Certificate {certificate_id} not found")
        
        patient = self.session.get(Patient, certificate.patient_id)
        if not patient:
            raise ValueError(f"Patient not found for certificate {certificate_id}")
        
        # Regenerate PDF
        pdf_path = self._generate_certificate_pdf(certificate, patient)
        
        logger.info(f"Reprinted certificate {certificate_id}")
        return str(pdf_path)