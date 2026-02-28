"""
Task 8.4: Error recovery — retry decorator & resume helpers.
"""

import asyncio
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Errors that may succeed on retry (rate-limits, timeouts, network)."""


class PermanentError(Exception):
    """Errors that will never succeed on retry (bad data, missing file)."""


def with_retry(func: Callable, max_retries: int = 3, base_delay: float = 2.0) -> Any:
    """
    Synchronous retry wrapper with exponential back-off.

    Retries on TransientError; re-raises everything else immediately.
    """
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except TransientError as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = base_delay * attempt
                logger.warning("Transient error on attempt %d/%d — retrying in %.1fs: %s", attempt, max_retries, wait, exc)
                time.sleep(wait)
            else:
                logger.error("Transient error persisted after %d attempts: %s", max_retries, exc)
        except PermanentError:
            raise
        except Exception as exc:
            # Unknown errors are treated as permanent
            raise PermanentError(str(exc)) from exc

    raise PermanentError(f"Failed after {max_retries} retries: {last_exc}")


def classify_transient_error(exc: Exception) -> bool:
    """Heuristic: does *exc* look like a transient error?"""
    msg = str(exc).lower()
    transient_keywords = ["429", "rate limit", "timeout", "timed out", "connection", "temporarily unavailable", "503"]
    return any(kw in msg for kw in transient_keywords)


def build_error_report(step: str, error_msg: str) -> dict:
    """Produce a user-friendly error report dict."""
    suggestions = {
        "extract": "Check that the uploaded files are valid PDF or images.",
        "classify": "Wait a few minutes and try again — the AI may have been rate-limited.",
        "validate": "Review the validation errors and correct mapped data.",
        "generate": "Ensure the CMA template file exists and the data is complete.",
    }
    return {
        "step": step,
        "message": error_msg,
        "retriable": step in ("classify", "extract"),
        "suggestion": suggestions.get(step, "Contact support if this persists."),
    }
