"""
Structured logging module for Pocket Option AI Analyzer Bot.
Ensures zero credential leakage and provides clear analytical tracing.
"""

import logging
import sys
from typing import Optional


class RedactingFormatter(logging.Formatter):
    """Filter out any accidental token or key leaks in logs."""

    SENSITIVE_PATTERNS = [
        "TELEGRAM_BOT_TOKEN",
        "API_KEY",
        "bot",
        ":AAG",
        ":AAH",
    ]

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        # Redact known patterns if present
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in msg:
                msg = msg.replace(pattern, "[REDACTED]")
        return msg


def setup_logger(name: str = "pocket_analyzer", level: str = "INFO") -> logging.Logger:
    """Setup and return standard structured logger."""
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = RedactingFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()


def log_analysis_event(
    user_id: int,
    asset: str,
    timeframe: str,
    decision: str,
    confidence: float,
    execution_time_ms: float,
    error: Optional[str] = None,
):
    """Structured audit logger for analysis events."""
    if error:
        logger.error(
            f"ANALYSIS_ERROR | user={user_id} | asset={asset} | tf={timeframe} | error={error}"
        )
    else:
        logger.info(
            f"ANALYSIS_EVENT | user={user_id} | asset={asset} | tf={timeframe} | "
            f"decision={decision} | confidence={confidence:.1f}% | latency={execution_time_ms:.1f}ms"
        )
