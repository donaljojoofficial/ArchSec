import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "path": record.pathname,
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)

def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    # Clear existing handlers to avoid duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Ensure Django logs are also captured
    django_logger = logging.getLogger('django')
    django_logger.handlers.clear()
    django_logger.addHandler(handler)
    django_logger.setLevel(logging.INFO)