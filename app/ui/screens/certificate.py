"""Certificate screen UI (placeholder)"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from app.i18n import i18n


class CertificateScreen(QWidget):
    """Certificate issuance screen"""
    
    # Signals
    back_pressed = Signal()
    user_activity = Signal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Placeholder
        label = QLabel(i18n.get("certificate_title"))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 48px; color: #2c3e50;")
        layout.addWidget(label)
        
        info = QLabel("증명서 발급 화면 구현 예정")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 24px; color: #7f8c8d;")
        layout.addWidget(info)