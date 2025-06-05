"""Internationalization support module"""

import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path
from babel import Locale
from babel.support import Translations

logger = logging.getLogger(__name__)


class I18nManager:
    """Manage translations and localization"""
    
    def __init__(self, locale_dir: str = "locale"):
        self.locale_dir = Path(locale_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_locale = "ko"
        self.fallback_locale = "ko"
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        # Create locale directory if it doesn't exist
        self.locale_dir.mkdir(exist_ok=True)
        
        # Load default translations
        self._load_default_translations()
        
        # Load custom translations from JSON files
        for lang_file in self.locale_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                logger.info(f"Loaded translations for {lang_code}")
            except Exception as e:
                logger.error(f"Failed to load translations for {lang_code}: {e}")
    
    def _load_default_translations(self):
        """Load default translations"""
        self.translations = {
            "ko": {
                # Common
                "app_title": "보건소 키오스크",
                "welcome": "환영합니다",
                "select_service": "서비스를 선택해주세요",
                "back": "뒤로",
                "cancel": "취소",
                "confirm": "확인",
                "next": "다음",
                "print": "출력",
                "close": "닫기",
                
                # Main menu
                "reception": "접수",
                "payment": "수납",
                "certificate": "증명서 발급",
                
                # Reception
                "reception_title": "진료 접수",
                "enter_patient_info": "환자 정보를 입력해주세요",
                "name": "이름",
                "birthdate": "생년월일",
                "phone": "전화번호",
                "check_appointment": "예약 확인",
                "select_symptoms": "증상을 선택해주세요",
                "select_department": "진료과를 선택해주세요",
                "queue_number": "대기번호",
                "estimated_wait": "예상 대기시간",
                "location": "위치",
                
                # Symptoms
                "fever": "발열",
                "cough": "기침",
                "headache": "두통",
                "stomachache": "복통",
                "joint_pain": "관절통",
                "skin_rash": "피부발진",
                "depression": "우울감",
                "pregnancy": "임신",
                "fracture": "골절",
                "breathing_difficulty": "호흡곤란",
                
                # Departments
                "internal_medicine": "내과",
                "surgery": "외과",
                "pediatrics": "소아과",
                "obstetrics": "산부인과",
                "orthopedics": "정형외과",
                "dermatology": "피부과",
                "psychiatry": "정신건강의학과",
                "emergency": "응급실",
                
                # Payment
                "payment_title": "진료비 수납",
                "payment_amount": "결제 금액",
                "select_payment_method": "결제 방법을 선택해주세요",
                "cash": "현금",
                "card": "카드",
                "qr_payment": "QR 결제",
                "payment_processing": "결제 처리중...",
                "payment_complete": "결제가 완료되었습니다",
                "receipt": "영수증",
                
                # Certificate
                "certificate_title": "증명서 발급",
                "select_certificate_type": "증명서 종류를 선택해주세요",
                "diagnosis_certificate": "진단서",
                "treatment_certificate": "진료확인서",
                "vaccination_certificate": "예방접종증명서",
                "certificate_fee": "발급 수수료",
                "printing": "출력중...",
                
                # Accessibility
                "font_size": "글자 크기",
                "high_contrast": "고대비 모드",
                "voice_guide": "음성 안내",
                "help": "도움말",
                "emergency_help": "긴급 도움 요청",
                
                # Messages
                "please_wait": "잠시만 기다려주세요",
                "error_occurred": "오류가 발생했습니다",
                "try_again": "다시 시도해주세요",
                "timeout_warning": "곧 초기 화면으로 돌아갑니다",
                "thank_you": "감사합니다"
            },
            "en": {
                # Common
                "app_title": "Health Center Kiosk",
                "welcome": "Welcome",
                "select_service": "Please select a service",
                "back": "Back",
                "cancel": "Cancel",
                "confirm": "Confirm",
                "next": "Next",
                "print": "Print",
                "close": "Close",
                
                # Main menu
                "reception": "Reception",
                "payment": "Payment",
                "certificate": "Certificate",
                
                # Reception
                "reception_title": "Medical Reception",
                "enter_patient_info": "Please enter patient information",
                "name": "Name",
                "birthdate": "Date of Birth",
                "phone": "Phone Number",
                "check_appointment": "Check Appointment",
                "select_symptoms": "Please select symptoms",
                "select_department": "Please select department",
                "queue_number": "Queue Number",
                "estimated_wait": "Estimated Wait Time",
                "location": "Location",
                
                # Symptoms
                "fever": "Fever",
                "cough": "Cough",
                "headache": "Headache",
                "stomachache": "Stomachache",
                "joint_pain": "Joint Pain",
                "skin_rash": "Skin Rash",
                "depression": "Depression",
                "pregnancy": "Pregnancy",
                "fracture": "Fracture",
                "breathing_difficulty": "Breathing Difficulty",
                
                # Departments
                "internal_medicine": "Internal Medicine",
                "surgery": "Surgery",
                "pediatrics": "Pediatrics",
                "obstetrics": "Obstetrics",
                "orthopedics": "Orthopedics",
                "dermatology": "Dermatology",
                "psychiatry": "Psychiatry",
                "emergency": "Emergency",
                
                # Payment
                "payment_title": "Medical Payment",
                "payment_amount": "Payment Amount",
                "select_payment_method": "Please select payment method",
                "cash": "Cash",
                "card": "Card",
                "qr_payment": "QR Payment",
                "payment_processing": "Processing payment...",
                "payment_complete": "Payment completed",
                "receipt": "Receipt",
                
                # Certificate
                "certificate_title": "Certificate Issuance",
                "select_certificate_type": "Please select certificate type",
                "diagnosis_certificate": "Medical Certificate",
                "treatment_certificate": "Treatment Certificate",
                "vaccination_certificate": "Vaccination Certificate",
                "certificate_fee": "Issuance Fee",
                "printing": "Printing...",
                
                # Accessibility
                "font_size": "Font Size",
                "high_contrast": "High Contrast Mode",
                "voice_guide": "Voice Guide",
                "help": "Help",
                "emergency_help": "Emergency Help",
                
                # Messages
                "please_wait": "Please wait",
                "error_occurred": "An error occurred",
                "try_again": "Please try again",
                "timeout_warning": "Returning to home screen soon",
                "thank_you": "Thank you"
            },
            "zh": {
                # Common
                "app_title": "保健所自助服务机",
                "welcome": "欢迎",
                "select_service": "请选择服务",
                "back": "返回",
                "cancel": "取消",
                "confirm": "确认",
                "next": "下一步",
                "print": "打印",
                "close": "关闭",
                
                # Main menu
                "reception": "挂号",
                "payment": "缴费",
                "certificate": "证明书",
                
                # Add more Chinese translations...
            },
            "vi": {
                # Common
                "app_title": "Kiosk Trung tâm Y tế",
                "welcome": "Chào mừng",
                "select_service": "Vui lòng chọn dịch vụ",
                "back": "Quay lại",
                "cancel": "Hủy",
                "confirm": "Xác nhận",
                "next": "Tiếp theo",
                "print": "In",
                "close": "Đóng",
                
                # Main menu
                "reception": "Đăng ký",
                "payment": "Thanh toán",
                "certificate": "Giấy chứng nhận",
                
                # Add more Vietnamese translations...
            }
        }
        
        # Save default translations to files
        for lang, trans in self.translations.items():
            lang_file = self.locale_dir / f"{lang}.json"
            if not lang_file.exists():
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(trans, f, ensure_ascii=False, indent=2)
    
    def set_locale(self, locale_code: str):
        """Set current locale"""
        if locale_code in self.translations:
            self.current_locale = locale_code
            logger.info(f"Locale set to {locale_code}")
        else:
            logger.warning(f"Locale {locale_code} not found, using fallback")
            self.current_locale = self.fallback_locale
    
    def get(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """Get translated string"""
        locale = locale or self.current_locale
        
        # Try to get translation
        if locale in self.translations and key in self.translations[locale]:
            text = self.translations[locale][key]
        elif self.fallback_locale in self.translations and key in self.translations[self.fallback_locale]:
            text = self.translations[self.fallback_locale][key]
        else:
            logger.warning(f"Translation not found for key: {key}")
            text = key
        
        # Format with kwargs if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception as e:
                logger.error(f"Failed to format translation: {e}")
        
        return text
    
    def get_available_locales(self) -> list:
        """Get list of available locales"""
        return list(self.translations.keys())
    
    def add_translation(self, locale: str, key: str, value: str):
        """Add or update a translation"""
        if locale not in self.translations:
            self.translations[locale] = {}
        
        self.translations[locale][key] = value
        
        # Save to file
        lang_file = self.locale_dir / f"{locale}.json"
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations[locale], f, ensure_ascii=False, indent=2)


# Global i18n instance
i18n = I18nManager()


# Convenience function
def _(key: str, **kwargs) -> str:
    """Shorthand for translation"""
    return i18n.get(key, **kwargs)