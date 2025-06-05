"""Accessibility utilities"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AccessibilitySettings:
    """User accessibility preferences"""
    font_size: int = 16
    high_contrast: bool = False
    color_blind_mode: str = "none"  # none, protanopia, deuteranopia, tritanopia
    voice_enabled: bool = True
    voice_speed: float = 1.0
    button_size: str = "normal"  # small, normal, large
    touch_vibration: bool = True
    auto_read_screen: bool = True
    simplified_ui: bool = False


class AccessibilityManager:
    """Manage accessibility features"""
    
    def __init__(self):
        self.settings = AccessibilitySettings()
        self._color_filters = {
            "protanopia": self._protanopia_filter,
            "deuteranopia": self._deuteranopia_filter,
            "tritanopia": self._tritanopia_filter
        }
    
    def update_settings(self, **kwargs):
        """Update accessibility settings"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
                logger.info(f"Updated accessibility setting: {key}={value}")
    
    def get_font_size(self, base_size: int) -> int:
        """Calculate adjusted font size"""
        multiplier = self.settings.font_size / 16.0
        return int(base_size * multiplier)
    
    def get_button_size(self, base_width: int, base_height: int) -> tuple:
        """Calculate adjusted button size"""
        size_multipliers = {
            "small": 0.8,
            "normal": 1.0,
            "large": 1.3
        }
        multiplier = size_multipliers.get(self.settings.button_size, 1.0)
        return (int(base_width * multiplier), int(base_height * multiplier))
    
    def apply_color_filter(self, color: str) -> str:
        """Apply color blind filter to color"""
        if self.settings.color_blind_mode == "none":
            return color
        
        filter_func = self._color_filters.get(self.settings.color_blind_mode)
        if filter_func:
            return filter_func(color)
        
        return color
    
    def _protanopia_filter(self, color: str) -> str:
        """Filter for red-blind (protanopia)"""
        # Simplified filter - in production use proper color transformation
        return color.replace("#ff0000", "#d4d400").replace("#00ff00", "#0066ff")
    
    def _deuteranopia_filter(self, color: str) -> str:
        """Filter for green-blind (deuteranopia)"""
        return color.replace("#00ff00", "#ffff00").replace("#ff0000", "#cc6600")
    
    def _tritanopia_filter(self, color: str) -> str:
        """Filter for blue-blind (tritanopia)"""
        return color.replace("#0000ff", "#ff00ff").replace("#ffff00", "#ff6666")
    
    def get_contrast_colors(self) -> Dict[str, str]:
        """Get high contrast color scheme"""
        if self.settings.high_contrast:
            return {
                "background": "#000000",
                "foreground": "#FFFFFF",
                "primary": "#FFFF00",
                "secondary": "#00FFFF",
                "success": "#00FF00",
                "error": "#FF0000",
                "border": "#FFFFFF"
            }
        else:
            return {
                "background": "#FFFFFF",
                "foreground": "#2C3E50",
                "primary": "#3498DB",
                "secondary": "#2ECC71",
                "success": "#27AE60",
                "error": "#E74C3C",
                "border": "#BDC3C7"
            }
    
    def format_for_screen_reader(self, text: str, context: str = "") -> str:
        """Format text for screen reader"""
        if context:
            return f"{context}. {text}"
        return text
    
    def get_aria_labels(self, screen: str) -> Dict[str, str]:
        """Get ARIA labels for screen elements"""
        labels = {
            "home": {
                "title": "홈 화면",
                "reception_button": "접수하기 버튼",
                "payment_button": "수납하기 버튼",
                "certificate_button": "증명서 발급하기 버튼"
            },
            "reception": {
                "title": "접수 화면",
                "name_input": "이름 입력란",
                "birthdate_input": "생년월일 입력란",
                "phone_input": "전화번호 입력란",
                "next_button": "다음 단계로 진행하기 버튼"
            }
        }
        return labels.get(screen, {})


# Global accessibility manager
accessibility = AccessibilityManager()