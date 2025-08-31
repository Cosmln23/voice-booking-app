import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(debug: bool = False) -> None:
    """Setup structured JSON logging"""
    
    # Set log level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create JSON formatter
    formatter = JSONFormatter()
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Disable uvicorn default logging to avoid duplicates
    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with extra data support"""
    return logging.getLogger(name)