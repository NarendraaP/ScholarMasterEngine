"""
Structured Logging Configuration

Provides production-ready logging with:
- JSON formatting
- Log levels
- Contextual information
- Performance tracking
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for easy parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'student_id'):
            log_data['student_id'] = record.student_id
        if hasattr(record, 'subject'):
            log_data['subject'] = record.subject
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(level: str = "INFO", json_format: bool = True):
    """
    Configure application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use JSON formatter; else use standard format
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Create logger instance
logger = logging.getLogger("scholar_master")


# Helper functions for common logging patterns
def log_student_action(action: str, student_id: str, **kwargs):
    """Log student-related actions"""
    logger.info(action, extra={"student_id": student_id, **kwargs})


def log_performance(operation: str, duration_ms: float, **kwargs):
    """Log performance metrics"""
    logger.info(
        f"Performance: {operation}",
        extra={"duration_ms": duration_ms, **kwargs}
    )


def log_error(message: str, error: Exception, **kwargs):
    """Log errors with context"""
    logger.error(message, exc_info=error, extra=kwargs)


# Usage examples (for documentation)
"""
Example Usage:

from utils.logging_config import logger, log_student_action, log_performance

# Basic logging
logger.info("System started")
logger.warning("High load detected", extra={"stream_count": 10})

# Student actions
log_student_action("registration", "S101", department="CS", year=1)

# Performance metrics
import time
start = time.time()
# ... do work ...
duration_ms = (time.time() - start) * 1000
log_performance("face_recognition", duration_ms, fps=30)

# Errors
try:
    # ... code ...
except Exception as e:
    log_error("Failed to mark attendance", e, student_id="S101")
"""
