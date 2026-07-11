"""
Structured logging configuration for Shakespeare Translator.

Emits JSON-formatted logs to console and a rotating file, with a
request ID attached via contextvars so log lines can be correlated
to a single HTTP request.
"""

import json
import logging
import logging.handlers
import sys
from contextvars import ContextVar
from pathlib import Path

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "bardify.log"


class RequestIdFilter(logging.Filter):
    """Injects the current request ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with console + rotating file JSON handlers."""
    LOG_DIR.mkdir(exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = JSONFormatter()
    request_filter = RequestIdFilter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_filter)
    root.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(request_filter)
    root.addHandler(file_handler)


def log_extra(**fields) -> dict:
    """Helper to attach structured extra fields to a log call.

    Usage: logger.info("transform complete", extra=log_extra(style=style, tokens=42))
    """
    return {"extra_fields": fields}
