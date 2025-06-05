"""Home screen UI"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon

from app.i18n import i18n


class ServiceButton(QPushButton):
    """Custom service button with icon and animation"""
    
    def __init__(self, text: str, icon_path: str = None):
        super().__init__(text)
        self.setMinimumSize(250, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style
        self.setStyleSheet("""
            ServiceButton {
                background-color: #ffffff;
                border: 3px solid #3498db;
                border-radius: 20px;
                padding: 30px;
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            ServiceButton:hover {
                background-color: #ecf0f1;
                border-color: #2980b9;
                transform: scale(1.05);
            }
            ServiceButton:pressed {
                background-color: #d5dbdb;
                transform: scale(0.98);
            }
        """)
        
        # Add icon if provided
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(self.size() * 0.5)
    
    def enterEvent(self, event):
        """Animate on hover"""
        super().enterEvent(event)
        # Could add animation here
    
    def leaveEvent(self, event):
        """Reset on leave"""
        super().leaveEvent(event)


class HomeScreen(QWidget):
    """Main home screen"""
    
    # Signals
    reception_clicked = Signal()
    payment_clicked = Signal()
    certificate_clicked = Signal()
    user_activity = Signal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Welcome message
        welcome_label = QLabel(i18n.get("welcome"))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        layout.addWidget(welcome_label)
        
        # Service selection label
        select_label = QLabel(i18n.get("select_service"))
        select_label.setAlignment(Qt.AlignCenter)
        select_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                color: #34495e;
                padding: 10px;
            }
        """)
        layout.addWidget(select_label)
        
        # Add spacer
        layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        
        # Service buttons container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(40)
        
        # Reception button
        self.reception_btn = ServiceButton(i18n.get("reception"))
        self.reception_btn.clicked.connect(self.on_reception_clicked)
        button_layout.addWidget(self.reception_btn)
        
        # Payment button
        self.payment_btn = ServiceButton(i18n.get("payment"))
        self.payment_btn.clicked.connect(self.on_payment_clicked)
        button_layout.addWidget(self.payment_btn)
        
        # Certificate button
        self.certificate_btn = ServiceButton(i18n.get("certificate"))
        self.certificate_btn.clicked.connect(self.on_certificate_clicked)
        button_layout.addWidget(self.certificate_btn)
        
        layout.addWidget(button_container)
        
        # Add bottom spacer
        layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        
        # Language selector
        lang_container = QWidget()
        lang_layout = QHBoxLayout(lang_container)
        lang_layout.setAlignment(Qt.AlignCenter)
        
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet("font-size: 18px; color: #7f8c8d;")
        lang_layout.addWidget(lang_label)
        
        # Language buttons
        for lang_code, lang_name in [("ko", "한국어"), ("en", "English"), 
                                     ("zh", "中文"), ("vi", "Tiếng Việt")]:
            lang_btn = QPushButton(lang_name)
            lang_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #bdc3c7;
                    border-radius: 15px;
                    padding: 5px 15px;
                    font-size: 16px;
                    color: #7f8c8d;
                }
                QPushButton:hover {
                    border-color: #3498db;
                    color: #3498db;
                }
            """)
            lang_btn.clicked.connect(lambda checked, lc=lang_code: self.change_language(lc))
            lang_layout.addWidget(lang_btn)
        
        layout.addWidget(lang_container)
    
    def on_reception_clicked(self):
        """Handle reception button click"""
        self.user_activity.emit()
        self.reception_clicked.emit()
    
    def on_payment_clicked(self):
        """Handle payment button click"""
        self.user_activity.emit()
        self.payment_clicked.emit()
    
    def on_certificate_clicked(self):
        """Handle certificate button click"""
        self.user_activity.emit()
        self.certificate_clicked.emit()
    
    def change_language(self, lang_code: str):
        """Change UI language"""
        i18n.set_locale(lang_code)
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI with new language"""
        # Update labels
        self.findChild(QLabel, "welcome_label").setText(i18n.get("welcome"))
        self.findChild(QLabel, "select_label").setText(i18n.get("select_service"))
        
        # Update buttons
        self.reception_btn.setText(i18n.get("reception"))
        self.payment_btn.setText(i18n.get("payment"))
        self.certificate_btn.setText(i18n.get("certificate"))
    
    def update_font_size(self, size: int):
        """Update font sizes when accessibility setting changes"""
        # Update label fonts proportionally
        welcome_size = int(size * 3)
        select_size = int(size * 2)
        button_size = int(size * 1.5)
        
        # Apply to widgets
        for label in self.findChildren(QLabel):
            font = label.font()
            if "welcome" in label.objectName():
                font.setPointSize(welcome_size)
            else:
                font.setPointSize(select_size)
            label.setFont(font)
        
        for button in self.findChildren(ServiceButton):
            font = button.font()
            font.setPointSize(button_size)
            button.setFont(font)