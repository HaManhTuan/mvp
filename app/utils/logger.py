import os
import sys
import contextvars
from loguru import logger
from app.config.settings import settings

# Create a context variable to store request ID
request_id_var = contextvars.ContextVar("request_id", default=None)

# Remove default logger
logger.remove()

# Enhanced log format with request ID
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[request_id]}</cyan> | <blue>{extra[context]}</blue> | <level>{message}</level>"

# Configure console output
logger.add(
    sys.stdout,
    format=log_format,
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Configure file output if path is set
if settings.LOG_FILE_PATH:
    # Ensure log directory exists
    os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
    
    # Add file logger
    logger.add(
        settings.LOG_FILE_PATH,
        serialize=True,
        level=settings.LOG_LEVEL,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated logs
    )

def set_request_id(id_value):
    """Set the request ID for the current context"""
    if id_value:
        request_id_var.set(id_value)

def get_request_id():
    """Get the request ID for the current context"""
    return request_id_var.get()

# Create a function to get logger
def get_logger(name=None):
    """Get a logger with an optional name and current request ID"""
    request_id = get_request_id() or "no-request-id"
    return logger.bind(context=name, request_id=request_id)
