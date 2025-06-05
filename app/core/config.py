"""Application configuration"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Healthcare Kiosk"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: str = "sqlite:///./kiosk.db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-encryption-key-here-32-bytes"
    
    # Session Management
    session_timeout_seconds: int = 120
    idle_timeout_seconds: int = 120
    
    # Hardware Devices
    printer_port: str = "/dev/ttyUSB0"
    card_reader_port: str = "/dev/ttyUSB1"
    cash_acceptor_port: str = "/dev/ttyUSB2"
    enable_hardware: bool = False
    
    # Language Settings
    default_language: str = "ko"
    supported_languages: List[str] = ["ko", "en", "zh", "vi"]
    
    # TTS Configuration
    tts_enabled: bool = True
    tts_voice: str = "ko-KR-Wavenet-A"
    tts_speed: float = 1.0
    
    # Payment Gateway
    payment_gateway_url: str = "https://api.payment.example.com"
    payment_api_key: str = "your-payment-api-key"
    payment_merchant_id: str = "your-merchant-id"
    
    # EMR Integration
    emr_api_url: str = "https://emr.hospital.example.com/api"
    emr_api_key: str = "your-emr-api-key"
    emr_sync_interval_minutes: int = 5
    
    # Admin Settings
    admin_password: str = "admin123"
    admin_nfc_card_id: str = "0123456789"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    enable_monitoring: bool = False
    
    # Backup
    backup_path: str = "/var/backups/kiosk"
    backup_retention_days: int = 30
    
    # UI Settings
    ui_font_size_min: int = 12
    ui_font_size_max: int = 24
    ui_font_size_default: int = 16
    ui_contrast_mode: bool = False
    ui_colorblind_mode: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Department locations mapping
DEPARTMENT_LOCATIONS = {
    "internal_medicine": "2층 201호",
    "surgery": "3층 301호",
    "pediatrics": "1층 101호",
    "obstetrics": "4층 401호",
    "orthopedics": "2층 202호",
    "dermatology": "1층 102호",
    "psychiatry": "5층 501호",
    "emergency": "응급실 (별관)"
}

# Symptom to department mapping
SYMPTOM_DEPARTMENT_MAP = {
    "발열": ["internal_medicine", "pediatrics"],
    "기침": ["internal_medicine", "pediatrics"],
    "두통": ["internal_medicine", "psychiatry"],
    "복통": ["internal_medicine", "surgery"],
    "관절통": ["orthopedics", "internal_medicine"],
    "피부발진": ["dermatology"],
    "우울감": ["psychiatry"],
    "임신": ["obstetrics"],
    "골절": ["orthopedics", "emergency"],
    "호흡곤란": ["emergency", "internal_medicine"]
}

# Certificate templates
CERTIFICATE_TEMPLATES = {
    "diagnosis": """
진단서

환자명: {patient_name}
생년월일: {birthdate}
진단명: {diagnosis}
발급일: {issue_date}

담당의사: {doctor_name}
의료기관: 보건소
""",
    "treatment": """
진료확인서

환자명: {patient_name}
생년월일: {birthdate}
진료일: {treatment_date}
진료내용: {treatment_content}

담당의사: {doctor_name}
의료기관: 보건소
""",
    "vaccination": """
예방접종증명서

환자명: {patient_name}
생년월일: {birthdate}
접종일: {vaccination_date}
백신명: {vaccine_name}
차수: {dose_number}

담당의사: {doctor_name}
의료기관: 보건소
"""
}