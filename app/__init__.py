"""Healthcare Kiosk Application Package

배리어-프리 보건소 키오스크 시스템
디지털 취약계층을 위한 접근성 높은 의료 서비스 키오스크
"""

__version__ = "1.0.0"
__author__ = "Healthcare Kiosk Team"
__description__ = "Barrier-free healthcare kiosk for digital vulnerable groups"
__license__ = "MIT"

# Core imports for easy access
from .core import get_settings
from .i18n import i18n, _
from .state_machine import state_machine, KioskState

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "__license__",
    "get_settings",
    "i18n",
    "_",
    "state_machine",
    "KioskState"
]