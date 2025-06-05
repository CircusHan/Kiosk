"""Logging configuration"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """Setup application logging"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Console formatter
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON format
    file_handler = RotatingFileHandler(
        log_dir / f"kiosk_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # JSON formatter
    json_formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        timestamp=True
    )
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized with level: {log_level}")


class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class SecureLogger:
    """Logger that masks sensitive information"""
    
    SENSITIVE_PATTERNS = [
        "password", "token", "key", "secret",
        "card_number", "phone", "birthdate"
    ]
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _mask_sensitive(self, message: str) -> str:
        """Mask sensitive information in log messages"""
        masked = message
        
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in masked.lower():
                # Simple masking - in production use regex
                parts = masked.split('=')
                if len(parts) > 1:
                    masked = f"{parts[0]}=***MASKED***"
        
        return masked
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(self._mask_sensitive(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(self._mask_sensitive(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(self._mask_sensitive(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(self._mask_sensitive(message), *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(self._mask_sensitive(message), *args, **kwargs)


def get_logger(name: str) -> SecureLogger:
    """Get a secure logger instance"""
    return SecureLogger(logging.getLogger(name))