"""
Logging sanitization utilities to prevent LogRecord conflicts
"""
from typing import Mapping, Dict, Any

# Complete set of reserved fields from LogRecord (Python 3.11+)
_RESERVED = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
    "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
    "relativeCreated", "thread", "threadName", "process", "processName", "message",
    "asctime", "stacklevel", "taskName"
}


def safe_extra(d: Mapping, prefix: str = "payload_") -> Dict[str, Any]:
    """
    Sanitize dictionary for logging extra parameter by prefixing reserved fields.
    
    Args:
        d: Dictionary to sanitize
        prefix: Prefix to add to reserved field names
        
    Returns:
        Sanitized dictionary safe for logging extra parameter
    """
    if not d:
        return {}
        
    out = {}
    for k, v in d.items():
        # Prefix reserved field names to avoid conflicts
        key = k if k not in _RESERVED else f"{prefix}{k}"
        out[key] = v
    return out