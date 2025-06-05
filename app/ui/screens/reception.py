"""Reception screen UI"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget,
    QGridLayout, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal

from app.i18n import i18n
from app.state_machine import state_machine


class ReceptionScreen(QWidget):
    """Reception service screen"""
    
    # Signals
    back_pressed = Signal()
    user_activity = Signal()
    
    def __init__(self):
        super().__init__()
        self.patient_data = {}
        self.selected_symptoms = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        self.back_btn = QPushButton("← " + i18n.get("back"))
        self.back_btn.setFixedWidth(150)
        self.back_btn.clicked.connect(self.back_pressed.emit)
        header_layout.addWidget(self.back_btn)
        
        # Title
        title = QLabel(i18n.get("reception_title"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title, 1)
        
        # Spacer
        header_layout.addWidget(QWidget(), 0)
        
        layout.addLayout(header_layout)
        
        # Content stack
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack, 1)
        
        # Create sub-screens
        self.patient_input_widget = self.create_patient_input()
        self.symptom_select_widget = self.create_symptom_select()
        self.department_select_widget = self.create_department_select()
        self.confirmation_widget = self.create_confirmation()
        
        # Add to stack
        self.content_stack.addWidget(self.patient_input_widget)
        self.content_stack.addWidget(self.symptom_select_widget)
        self.content_stack.addWidget(self.department_select_widget)
        self.content_stack.addWidget(self.confirmation_widget)
    
    def create_patient_input(self) -> QWidget:
        """Create patient information input screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(i18n.get("enter_patient_info"))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("font-size: 24px; color: #34495e; margin-bottom: 30px;")
        layout.addWidget(instructions)
        
        # Form container
        form_container = QWidget()
        form_container.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_container)
        
        # Name input
        name_label = QLabel(i18n.get("name"))
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        form_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("홍길동")
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                padding: 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(20)
        
        # Birthdate input
        birthdate_label = QLabel(i18n.get("birthdate"))
        birthdate_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        form_layout.addWidget(birthdate_label)
        
        self.birthdate_input = QLineEdit()
        self.birthdate_input.setPlaceholderText("1990-01-01")
        self.birthdate_input.setStyleSheet(self.name_input.styleSheet())
        form_layout.addWidget(self.birthdate_input)
        form_layout.addSpacing(20)
        
        # Phone input
        phone_label = QLabel(i18n.get("phone"))
        phone_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        form_layout.addWidget(phone_label)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("010-1234-5678")
        self.phone_input.setStyleSheet(self.name_input.styleSheet())
        form_layout.addWidget(self.phone_input)
        
        # Center form
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(form_container)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        layout.addStretch()
        
        # Next button
        self.next_btn = QPushButton(i18n.get("next"))
        self.next_btn.setFixedHeight(60)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.next_btn.clicked.connect(self.on_patient_info_next)
        layout.addWidget(self.next_btn)
        
        return widget
    
    def create_symptom_select(self) -> QWidget:
        """Create symptom selection screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(i18n.get("select_symptoms"))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("font-size: 24px; color: #34495e; margin-bottom: 30px;")
        layout.addWidget(instructions)
        
        # Symptoms grid
        symptoms_container = QWidget()
        symptoms_layout = QGridLayout(symptoms_container)
        symptoms_layout.setSpacing(20)
        
        symptoms = [
            "fever", "cough", "headache", "stomachache",
            "joint_pain", "skin_rash", "depression", "pregnancy",
            "fracture", "breathing_difficulty"
        ]
        
        self.symptom_checkboxes = {}
        for i, symptom in enumerate(symptoms):
            checkbox = QCheckBox(i18n.get(symptom))
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 20px;
                    padding: 10px;
                }
                QCheckBox::indicator {
                    width: 30px;
                    height: 30px;
                }
            """)
            self.symptom_checkboxes[symptom] = checkbox
            symptoms_layout.addWidget(checkbox, i // 2, i % 2)
        
        # Center symptoms
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(symptoms_container)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        layout.addStretch()
        
        # Next button
        self.symptom_next_btn = QPushButton(i18n.get("next"))
        self.symptom_next_btn.setFixedHeight(60)
        self.symptom_next_btn.setStyleSheet(self.next_btn.styleSheet())
        self.symptom_next_btn.clicked.connect(self.on_symptom_next)
        layout.addWidget(self.symptom_next_btn)
        
        return widget
    
    def create_department_select(self) -> QWidget:
        """Create department selection screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(i18n.get("select_department"))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("font-size: 24px; color: #34495e; margin-bottom: 30px;")
        layout.addWidget(instructions)
        
        # Departments grid
        dept_container = QWidget()
        dept_layout = QGridLayout(dept_container)
        dept_layout.setSpacing(20)
        
        departments = [
            "internal_medicine", "surgery", "pediatrics", "obstetrics",
            "orthopedics", "dermatology", "psychiatry", "emergency"
        ]
        
        self.department_buttons = {}
        for i, dept in enumerate(departments):
            btn = QPushButton(i18n.get(dept))
            btn.setFixedSize(200, 100)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ecf0f1;
                }
                QPushButton:pressed {
                    background-color: #d5dbdb;
                }
            """)
            btn.clicked.connect(lambda checked, d=dept: self.on_department_selected(d))
            self.department_buttons[dept] = btn
            dept_layout.addWidget(btn, i // 4, i % 4)
        
        # Center departments
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(dept_container)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        layout.addStretch()
        
        return widget
    
    def create_confirmation(self) -> QWidget:
        """Create confirmation screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Success message
        success_label = QLabel("✓ 접수가 완료되었습니다!")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #27ae60;
            margin: 40px;
        """)
        layout.addWidget(success_label)
        
        # Queue info box
        info_box = QGroupBox()
        info_box.setStyleSheet("""
            QGroupBox {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 15px;
                padding: 30px;
                font-size: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        
        self.queue_number_label = QLabel()
        self.queue_number_label.setAlignment(Qt.AlignCenter)
        self.queue_number_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(self.queue_number_label)
        
        self.location_label = QLabel()
        self.location_label.setAlignment(Qt.AlignCenter)
        self.location_label.setStyleSheet("font-size: 24px; color: #34495e; margin-top: 20px;")
        info_layout.addWidget(self.location_label)
        
        self.wait_time_label = QLabel()
        self.wait_time_label.setAlignment(Qt.AlignCenter)
        self.wait_time_label.setStyleSheet("font-size: 20px; color: #7f8c8d; margin-top: 10px;")
        info_layout.addWidget(self.wait_time_label)
        
        # Center info box
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(info_box)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        layout.addStretch()
        
        # Complete button
        self.complete_btn = QPushButton("홈으로 돌아가기")
        self.complete_btn.setFixedHeight(60)
        self.complete_btn.setStyleSheet(self.next_btn.styleSheet())
        self.complete_btn.clicked.connect(self.back_pressed.emit)
        layout.addWidget(self.complete_btn)
        
        return widget
    
    def on_patient_info_next(self):
        """Handle patient info next button"""
        # Validate inputs
        if not all([self.name_input.text(), self.birthdate_input.text(), self.phone_input.text()]):
            return
        
        self.patient_data = {
            "name": self.name_input.text(),
            "birthdate": self.birthdate_input.text(),
            "phone": self.phone_input.text()
        }
        
        # Move to symptom selection
        self.content_stack.setCurrentWidget(self.symptom_select_widget)
        self.user_activity.emit()
    
    def on_symptom_next(self):
        """Handle symptom selection next button"""
        # Get selected symptoms
        self.selected_symptoms = [
            symptom for symptom, checkbox in self.symptom_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not self.selected_symptoms:
            return
        
        # Move to department selection
        self.content_stack.setCurrentWidget(self.department_select_widget)
        self.user_activity.emit()
    
    def on_department_selected(self, department: str):
        """Handle department selection"""
        # Show confirmation with mock data
        self.queue_number_label.setText(f"대기번호: {42}")
        self.location_label.setText(f"위치: {i18n.get(department)} - 2층 201호")
        self.wait_time_label.setText("예상 대기시간: 약 15분")
        
        self.content_stack.setCurrentWidget(self.confirmation_widget)
        self.user_activity.emit()