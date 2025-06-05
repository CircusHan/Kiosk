"""State Machine for Kiosk Screen Navigation"""

import logging
from enum import Enum, auto
from typing import Optional, Dict, Any, Callable
from transitions import Machine
from transitions.extensions import GraphMachine

logger = logging.getLogger(__name__)


class KioskState(Enum):
    """Kiosk screen states"""
    HOME = auto()
    RECEPTION = auto()
    RECEPTION_PATIENT_INPUT = auto()
    RECEPTION_APPOINTMENT_CHECK = auto()
    RECEPTION_SYMPTOM_SELECT = auto()
    RECEPTION_DEPARTMENT_SELECT = auto()
    RECEPTION_CONFIRM = auto()
    RECEPTION_COMPLETE = auto()
    
    PAYMENT = auto()
    PAYMENT_PATIENT_INPUT = auto()
    PAYMENT_AMOUNT_CHECK = auto()
    PAYMENT_METHOD_SELECT = auto()
    PAYMENT_PROCESS = auto()
    PAYMENT_COMPLETE = auto()
    
    CERTIFICATE = auto()
    CERTIFICATE_TYPE_SELECT = auto()
    CERTIFICATE_PATIENT_INPUT = auto()
    CERTIFICATE_PAYMENT = auto()
    CERTIFICATE_PRINT = auto()
    CERTIFICATE_COMPLETE = auto()
    
    ADMIN = auto()
    ADMIN_AUTH = auto()
    ADMIN_MENU = auto()
    
    ERROR = auto()
    TIMEOUT = auto()


class KioskStateMachine:
    """State machine for managing kiosk screen flow"""
    
    states = [state.name for state in KioskState]
    
    def __init__(self):
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=KioskState.HOME.name,
            auto_transitions=False,
            send_event=True,
            before_state_change='log_transition'
        )
        
        # Store data between states
        self.context: Dict[str, Any] = {}
        
        # Define transitions
        self._define_transitions()
        
        # Callback handlers
        self.state_callbacks: Dict[str, Callable] = {}
    
    def _define_transitions(self):
        """Define all state transitions"""
        
        # Home transitions
        self.machine.add_transition('select_reception', KioskState.HOME.name, KioskState.RECEPTION.name)
        self.machine.add_transition('select_payment', KioskState.HOME.name, KioskState.PAYMENT.name)
        self.machine.add_transition('select_certificate', KioskState.HOME.name, KioskState.CERTIFICATE.name)
        self.machine.add_transition('admin_mode', KioskState.HOME.name, KioskState.ADMIN_AUTH.name)
        
        # Reception flow
        self.machine.add_transition('start_reception', KioskState.RECEPTION.name, KioskState.RECEPTION_PATIENT_INPUT.name)
        self.machine.add_transition('patient_identified', KioskState.RECEPTION_PATIENT_INPUT.name, KioskState.RECEPTION_APPOINTMENT_CHECK.name)
        self.machine.add_transition('has_appointment', KioskState.RECEPTION_APPOINTMENT_CHECK.name, KioskState.RECEPTION_CONFIRM.name)
        self.machine.add_transition('no_appointment', KioskState.RECEPTION_APPOINTMENT_CHECK.name, KioskState.RECEPTION_SYMPTOM_SELECT.name)
        self.machine.add_transition('symptoms_selected', KioskState.RECEPTION_SYMPTOM_SELECT.name, KioskState.RECEPTION_DEPARTMENT_SELECT.name)
        self.machine.add_transition('department_selected', KioskState.RECEPTION_DEPARTMENT_SELECT.name, KioskState.RECEPTION_CONFIRM.name)
        self.machine.add_transition('confirm_reception', KioskState.RECEPTION_CONFIRM.name, KioskState.RECEPTION_COMPLETE.name)
        self.machine.add_transition('reception_done', KioskState.RECEPTION_COMPLETE.name, KioskState.HOME.name)
        
        # Payment flow
        self.machine.add_transition('start_payment', KioskState.PAYMENT.name, KioskState.PAYMENT_PATIENT_INPUT.name)
        self.machine.add_transition('patient_verified', KioskState.PAYMENT_PATIENT_INPUT.name, KioskState.PAYMENT_AMOUNT_CHECK.name)
        self.machine.add_transition('amount_confirmed', KioskState.PAYMENT_AMOUNT_CHECK.name, KioskState.PAYMENT_METHOD_SELECT.name)
        self.machine.add_transition('method_selected', KioskState.PAYMENT_METHOD_SELECT.name, KioskState.PAYMENT_PROCESS.name)
        self.machine.add_transition('payment_success', KioskState.PAYMENT_PROCESS.name, KioskState.PAYMENT_COMPLETE.name)
        self.machine.add_transition('payment_done', KioskState.PAYMENT_COMPLETE.name, KioskState.HOME.name)
        
        # Certificate flow
        self.machine.add_transition('start_certificate', KioskState.CERTIFICATE.name, KioskState.CERTIFICATE_TYPE_SELECT.name)
        self.machine.add_transition('type_selected', KioskState.CERTIFICATE_TYPE_SELECT.name, KioskState.CERTIFICATE_PATIENT_INPUT.name)
        self.machine.add_transition('patient_confirmed', KioskState.CERTIFICATE_PATIENT_INPUT.name, KioskState.CERTIFICATE_PAYMENT.name)
        self.machine.add_transition('cert_payment_complete', KioskState.CERTIFICATE_PAYMENT.name, KioskState.CERTIFICATE_PRINT.name)
        self.machine.add_transition('print_complete', KioskState.CERTIFICATE_PRINT.name, KioskState.CERTIFICATE_COMPLETE.name)
        self.machine.add_transition('certificate_done', KioskState.CERTIFICATE_COMPLETE.name, KioskState.HOME.name)
        
        # Admin flow
        self.machine.add_transition('admin_authenticated', KioskState.ADMIN_AUTH.name, KioskState.ADMIN_MENU.name)
        self.machine.add_transition('admin_logout', KioskState.ADMIN_MENU.name, KioskState.HOME.name)
        
        # Back/Cancel transitions (from any state)
        for state in self.states:
            if state != KioskState.HOME.name:
                self.machine.add_transition('go_back', state, KioskState.HOME.name)
                self.machine.add_transition('cancel', state, KioskState.HOME.name)
        
        # Error handling
        for state in self.states:
            self.machine.add_transition('error', state, KioskState.ERROR.name)
            self.machine.add_transition('timeout', state, KioskState.TIMEOUT.name)
        
        # Error recovery
        self.machine.add_transition('recover', KioskState.ERROR.name, KioskState.HOME.name)
        self.machine.add_transition('reset', KioskState.TIMEOUT.name, KioskState.HOME.name)
    
    def log_transition(self, event):
        """Log state transitions"""
        logger.info(f"State transition: {self.state} -> {event.transition.dest} (trigger: {event.event.name})")
    
    def set_context(self, key: str, value: Any):
        """Set context data"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.context.get(key, default)
    
    def clear_context(self):
        """Clear all context data"""
        self.context.clear()
    
    def register_state_callback(self, state: str, callback: Callable):
        """Register callback for state entry"""
        self.state_callbacks[state] = callback
    
    def on_enter_state(self, state: str):
        """Called when entering a state"""
        if state in self.state_callbacks:
            self.state_callbacks[state](self)
    
    def get_available_transitions(self) -> list:
        """Get available transitions from current state"""
        return [t.name for t in self.machine.get_triggers(self.state)]
    
    def reset_to_home(self):
        """Reset state machine to home"""
        self.clear_context()
        self.state = KioskState.HOME.name
        logger.info("State machine reset to HOME")
    
    def export_graph(self, filename: str = "kiosk_state_diagram"):
        """Export state diagram (requires GraphMachine)"""
        try:
            graph_machine = GraphMachine(
                model=self,
                states=self.states,
                initial=KioskState.HOME.name,
                auto_transitions=False,
                title="Kiosk State Machine"
            )
            # Copy transitions
            for t in self.machine.get_transitions():
                graph_machine.add_transition(
                    t.trigger, t.source, t.dest
                )
            graph_machine.get_graph().draw(f'{filename}.png', prog='dot')
            logger.info(f"State diagram exported to {filename}.png")
        except Exception as e:
            logger.error(f"Failed to export state diagram: {e}")


# Global state machine instance
state_machine = KioskStateMachine()