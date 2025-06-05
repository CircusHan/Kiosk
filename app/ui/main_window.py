"""Main UI window for kiosk application"""

import sys
import logging
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget, QLabel,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor

from app.core.config import get_settings
from app.state_machine import state_machine, KioskState
from app.i18n import i18n
from app.ui.screens.home import HomeScreen
from app.ui.screens.reception import ReceptionScreen
from app.ui.screens.payment import PaymentScreen
from app.ui.screens.certificate import CertificateScreen
from app.ui.widgets.accessibility import AccessibilityBar
from app.utils.tts import TTSManager

logger = logging.getLogger(__name__)
settings = get_settings()


class MainWindow(QMainWindow):
    """Main kiosk window"""
    
    # Signals
    timeout_warning = Signal()
    session_timeout = Signal()
    
    def __init__(self):
        super().__init__()
        self.tts = TTSManager()
        self.idle_timer = QTimer()
        self.warning_timer = QTimer()
        self.current_font_size = settings.ui_font_size_default
        
        self.init_ui()
        self.setup_state_machine()
        self.setup_timers()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle(i18n.get("app_title"))
        self.setWindowState(Qt.WindowFullScreen)
        
        # Set minimum size for windowed mode
        self.setMinimumSize(1024, 768)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Accessibility bar
        self.accessibility_bar = AccessibilityBar()
        self.accessibility_bar.font_size_changed.connect(self.change_font_size)
        self.accessibility_bar.contrast_toggled.connect(self.toggle_contrast)
        self.accessibility_bar.voice_toggled.connect(self.toggle_voice)
        self.accessibility_bar.help_requested.connect(self.show_help)
        main_layout.addWidget(self.accessibility_bar)
        
        # Screen container
        self.screen_stack = QStackedWidget()
        main_layout.addWidget(self.screen_stack, 1)
        
        # Initialize screens
        self.screens = {
            KioskState.HOME: HomeScreen(),
            KioskState.RECEPTION: ReceptionScreen(),
            KioskState.PAYMENT: PaymentScreen(),
            KioskState.CERTIFICATE: CertificateScreen()
        }
        
        # Add screens to stack
        for screen in self.screens.values():
            self.screen_stack.addWidget(screen)
            # Connect common signals
            if hasattr(screen, 'back_pressed'):
                screen.back_pressed.connect(self.go_back)
            if hasattr(screen, 'user_activity'):
                screen.user_activity.connect(self.reset_idle_timer)
        
        # Set initial screen
        self.screen_stack.setCurrentWidget(self.screens[KioskState.HOME])
        
        # Apply default styling
        self.apply_default_style()
    
    def setup_state_machine(self):
        """Setup state machine callbacks"""
        # Register state callbacks
        state_machine.register_state_callback(
            KioskState.HOME.name,
            lambda sm: self.show_screen(KioskState.HOME)
        )
        state_machine.register_state_callback(
            KioskState.RECEPTION.name,
            lambda sm: self.show_screen(KioskState.RECEPTION)
        )
        state_machine.register_state_callback(
            KioskState.PAYMENT.name,
            lambda sm: self.show_screen(KioskState.PAYMENT)
        )
        state_machine.register_state_callback(
            KioskState.CERTIFICATE.name,
            lambda sm: self.show_screen(KioskState.CERTIFICATE)
        )
        
        # Connect home screen navigation
        home_screen = self.screens[KioskState.HOME]
        home_screen.reception_clicked.connect(
            lambda: self.navigate_to(KioskState.RECEPTION)
        )
        home_screen.payment_clicked.connect(
            lambda: self.navigate_to(KioskState.PAYMENT)
        )
        home_screen.certificate_clicked.connect(
            lambda: self.navigate_to(KioskState.CERTIFICATE)
        )
    
    def setup_timers(self):
        """Setup idle and warning timers"""
        # Idle timer
        self.idle_timer.timeout.connect(self.on_idle_timeout)
        self.idle_timer.setInterval(settings.idle_timeout_seconds * 1000)
        self.idle_timer.start()
        
        # Warning timer (shows 30 seconds before timeout)
        self.warning_timer.timeout.connect(self.show_timeout_warning)
        self.warning_timer.setInterval((settings.idle_timeout_seconds - 30) * 1000)
        self.warning_timer.start()
    
    def show_screen(self, state: KioskState):
        """Show screen for given state"""
        if state in self.screens:
            self.screen_stack.setCurrentWidget(self.screens[state])
            self.reset_idle_timer()
            
            # Announce screen change
            if self.tts.is_enabled:
                screen_name = i18n.get(state.name.lower())
                self.tts.speak(f"{screen_name} 화면입니다")
    
    def navigate_to(self, state: KioskState):
        """Navigate to a new state"""
        try:
            # Trigger state transition
            if state == KioskState.RECEPTION:
                state_machine.select_reception()
            elif state == KioskState.PAYMENT:
                state_machine.select_payment()
            elif state == KioskState.CERTIFICATE:
                state_machine.select_certificate()
            
            # State machine callbacks will handle screen change
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            self.show_error("화면 전환 중 오류가 발생했습니다")
    
    @Slot()
    def go_back(self):
        """Go back to home screen"""
        state_machine.go_back()
    
    @Slot()
    def reset_idle_timer(self):
        """Reset idle timer on user activity"""
        self.idle_timer.stop()
        self.idle_timer.start()
        self.warning_timer.stop()
        self.warning_timer.start()
    
    @Slot()
    def on_idle_timeout(self):
        """Handle idle timeout"""
        logger.info("Session timeout due to inactivity")
        self.session_timeout.emit()
        
        # Clear any sensitive data
        state_machine.clear_context()
        
        # Return to home
        state_machine.reset_to_home()
        
        # Show message
        if self.tts.is_enabled:
            self.tts.speak("시간 초과로 초기 화면으로 돌아갑니다")
    
    @Slot()
    def show_timeout_warning(self):
        """Show timeout warning"""
        self.timeout_warning.emit()
        
        # Show warning message
        msg = QMessageBox(self)
        msg.setWindowTitle("알림")
        msg.setText("30초 후 초기 화면으로 돌아갑니다")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        
        # Auto close after 5 seconds
        QTimer.singleShot(5000, msg.close)
        msg.exec()
    
    @Slot(int)
    def change_font_size(self, size: int):
        """Change application font size"""
        self.current_font_size = size
        font = QFont()
        font.setPointSize(size)
        QApplication.instance().setFont(font)
        
        # Update all screens
        for screen in self.screens.values():
            if hasattr(screen, 'update_font_size'):
                screen.update_font_size(size)
    
    @Slot(bool)
    def toggle_contrast(self, enabled: bool):
        """Toggle high contrast mode"""
        if enabled:
            self.apply_high_contrast_style()
        else:
            self.apply_default_style()
    
    @Slot(bool)
    def toggle_voice(self, enabled: bool):
        """Toggle voice guidance"""
        self.tts.set_enabled(enabled)
        if enabled:
            self.tts.speak("음성 안내를 시작합니다")
        else:
            self.tts.speak("음성 안내를 종료합니다")
    
    @Slot()
    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h2>도움말</h2>
        <p>이 키오스크는 다음 서비스를 제공합니다:</p>
        <ul>
        <li><b>접수</b>: 진료 예약 확인 및 순번표 발급</li>
        <li><b>수납</b>: 진료비 결제</li>
        <li><b>증명서 발급</b>: 각종 의료 증명서 발급</li>
        </ul>
        <p>도움이 필요하시면 직원을 호출해 주세요.</p>
        """
        
        QMessageBox.information(self, "도움말", help_text)
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "오류", message)
        if self.tts.is_enabled:
            self.tts.speak(f"오류: {message}")
    
    def apply_default_style(self):
        """Apply default application style"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    
    def apply_high_contrast_style(self):
        """Apply high contrast style"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
                color: white;
            }
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid white;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
            QPushButton:pressed {
                background-color: #999999;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: black;
                color: white;
                border: 2px solid white;
            }
        """)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup
        self.tts.cleanup()
        state_machine.clear_context()
        event.accept()


def run_ui():
    """Run the UI application"""
    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    
    # Set default font
    font = QFont()
    font.setPointSize(settings.ui_font_size_default)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())