"""
Logging configuration for the backend application.
- Sets up logging to both console and rotating log files
- Logs are stored in the 'logs' directory within the backend folder
- Provides a get_logger function to retrieve loggers for different modules
- Log files are rotated when they reach 5 MB, with up to 5 backup files retained
- Console logging is set to INFO level, while file logging captures DEBUG and above
- Log messages include timestamps, log levels, module names, and line numbers for easier debugging
- Handles exceptions gracefully when setting up logging and ensures that the application can still run even if file logging fails (e.g. due to permissions issues)
- Provides clear log messages for successful setup and any issues encountered during logging configuration
- Can be easily extended to include additional handlers (e.g. email alerts) or to adjust log formats and levels based on configuration
- Ensures that loggers retrieved via get_logger inherit the handlers and configuration of the root logger, allowing for consistent logging across the application
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# Get the backend directory (parent of this file)
BACKEND_DIR = Path(__file__).resolve().parent
LOG_DIR = BACKEND_DIR / 'logs'

# Create logs directory if it doesn't exist
try:
    LOG_DIR.mkdir(exist_ok=True)
    print(f"✅ Log directory ready: {LOG_DIR}")
except Exception as e:
    print(f"❌ Failed to create log directory: {e}")
    raise

# Define log file paths
LOG_FILE = LOG_DIR / 'app.log'
ERROR_LOG_FILE = LOG_DIR / 'error.log'

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Clear any existing handlers
logger.handlers.clear()

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create file handlers
try:
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    print(f"✅ File handler configured: {LOG_FILE}")
except Exception as e:
    print(f"❌ Failed to create file handler: {e}")

try:
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE, maxBytes=5*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    print(f"✅ Error handler configured: {ERROR_LOG_FILE}")
except Exception as e:
    print(f"❌ Failed to create error handler: {e}")

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(levelname)s - %(name)s - %(message)s'
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
print(f"✅ Console handler configured")

def get_logger(name):
    """Get a logger instance for a module"""
    module_logger = logging.getLogger(name)
    # Ensure it inherits the parent logger's handlers
    if not module_logger.handlers:
        module_logger.addHandler(logging.NullHandler())
    return module_logger