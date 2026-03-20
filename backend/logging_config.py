"""
Logging configuration for the backend application.
- Configures the ROOT logger so all child loggers (backend.app, backend.db, etc.)
  automatically write to the rotating file handlers.
- Console handler writes to stderr to keep stdout clean for MCP stdio transport.
- Log files: backend/logs/app.log (DEBUG+), backend/logs/error.log (ERROR+)
"""
import logging
import logging.handlers
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
LOG_DIR = BACKEND_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"

_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def _setup_root_logger():
    root = logging.getLogger()
    # Only configure once
    if getattr(root, "_app_configured", False):
        return
    root.setLevel(logging.DEBUG)

    # Rotating file handler — all levels
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)
    root.addHandler(fh)

    # Rotating file handler — errors only
    eh = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    eh.setLevel(logging.ERROR)
    eh.setFormatter(_FORMATTER)
    root.addHandler(eh)

    # Console → stderr (never pollutes stdout / MCP stdio)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
    root.addHandler(ch)

    root._app_configured = True


_setup_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Handlers are on the root logger, so everything propagates automatically."""
    return logging.getLogger(name)

