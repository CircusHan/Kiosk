"""Accessibility control widgets"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider,
    QLabel, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from app.i18n import i18n


class AccessibilityBar(QWidget):
    """Accessibility controls toolbar"""
    
    # Signals
    font_size_changed = Signal(int)
    contrast_toggled = Signal(bool)
    voice_toggled = Signal(bool)
    help_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.high_contrast = False
        self.voice_enabled = True
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Style
        self.setStyleSheet("""
            AccessibilityBar {
                background-color: #ecf0f1;
                border-bottom: 2px solid #bdc3c7;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 10px;
                margin: 0 5px;
            }
            QToolButton:hover {
                background-color: #d5dbdb;
            }
            QToolButton:pressed {
                background-color: #bdc3c7;
            }
            QToolButton:checked {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Font size controls
        font_label = QLabel(i18n.get("font_size"))
        layout.addWidget(font_label)
        
        # Decrease font button
        self.font_decrease_btn = QToolButton()
        self.font_decrease_btn.setText("A-")
        self.font_decrease_btn.setToolTip("글자 크기 줄이기")
        self.font_decrease_btn.clicked.connect(self.decrease_font)
        layout.addWidget(self.font_decrease_btn)
        
        # Font size slider
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setMinimum(12)
        self.font_slider.setMaximum(24)
        self.font_slider.setValue(16)
        self.font_slider.setFixedWidth(150)
        self.font_slider.valueChanged.connect(self.on_font_size_changed)
        layout.addWidget(self.font_slider)
        
        # Increase font button
        self.font_increase_btn = QToolButton()
        self.font_increase_btn.setText("A+")
        self.font_increase_btn.setToolTip("글자 크기 늘리기")
        self.font_increase_btn.clicked.connect(self.increase_font)
        layout.addWidget(self.font_increase_btn)
        
        # Add separator
        layout.addSpacing(20)
        
        # High contrast toggle
        self.contrast_btn = QToolButton()
        self.contrast_btn.setText(i18n.get("high_contrast"))
        self.contrast_btn.setCheckable(True)
        self.contrast_btn.setToolTip("고대비 모드 켜기/끄기")
        self.contrast_btn.toggled.connect(self.toggle_contrast)
        layout.addWidget(self.contrast_btn)
        
        # Voice guide toggle
        self.voice_btn = QToolButton()
        self.voice_btn.setText(i18n.get("voice_guide"))
        self.voice_btn.setCheckable(True)
        self.voice_btn.setChecked(True)
        self.voice_btn.setToolTip("음성 안내 켜기/끄기")
        self.voice_btn.toggled.connect(self.toggle_voice)
        layout.addWidget(self.voice_btn)
        
        # Add stretch
        layout.addStretch()
        
        # Emergency help button
        self.help_btn = QPushButton(i18n.get("emergency_help"))
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.help_btn.clicked.connect(self.help_requested.emit)
        layout.addWidget(self.help_btn)
    
    def decrease_font(self):
        """Decrease font size"""
        current = self.font_slider.value()
        if current > self.font_slider.minimum():
            self.font_slider.setValue(current - 2)
    
    def increase_font(self):
        """Increase font size"""
        current = self.font_slider.value()
        if current < self.font_slider.maximum():
            self.font_slider.setValue(current + 2)
    
    def on_font_size_changed(self, value: int):
        """Handle font size change"""
        self.font_size_changed.emit(value)
    
    def toggle_contrast(self, checked: bool):
        """Toggle high contrast mode"""
        self.high_contrast = checked
        self.contrast_toggled.emit(checked)
    
    def toggle_voice(self, checked: bool):
        """Toggle voice guidance"""
        self.voice_enabled = checked
        self.voice_toggled.emit(checked)