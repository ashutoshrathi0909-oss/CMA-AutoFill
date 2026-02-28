"""
Security utilities: rate limiting, input validation, filename sanitization.

Created as part of Phase 11 — Task 11.2 (Security Hardening).
"""

import os
import re
import uuid
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address


# ── Rate Limiter ─────────────────────────────────────────────────────────
def _get_rate_limit_key(request: Request) -> str:
    """Use authenticated user ID if available, otherwise fall back to IP."""
    # Check if user was injected by auth dependency
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_rate_limit_key,
    default_limits=["100/minute"],
)


# ── Input Validation Helpers ─────────────────────────────────────────────
def validate_uuid(value: str, param_name: str = "id") -> str:
    """Validate that a string is a valid UUID. Returns the string if valid."""
    try:
        uuid.UUID(value)
        return value
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid {param_name}: must be a valid UUID"
        )


def validate_pagination(page: int, per_page: int) -> tuple[int, int]:
    """Clamp pagination params to safe bounds."""
    page = max(1, page)
    per_page = max(1, min(per_page, 100))
    return page, per_page


# ── Filename Sanitization ────────────────────────────────────────────────
_UNSAFE_CHARS = re.compile(r'[^\w\-.\s]', re.ASCII)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded filename to prevent path traversal and injection.

    - Strips directory components (../../etc/passwd → passwd)
    - Removes non-ASCII and special characters
    - Collapses whitespace
    - Truncates to 255 chars
    """
    # Strip any directory components (handles both / and \\)
    filename = os.path.basename(filename)

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Remove unsafe characters (keep alphanumeric, dash, dot, underscore, space)
    filename = _UNSAFE_CHARS.sub('', filename)

    # Collapse whitespace and replace with underscore
    filename = re.sub(r'\s+', '_', filename.strip())

    # Ensure the file has a name (not just an extension)
    if not filename or filename.startswith('.'):
        filename = f"upload_{filename}"

    # Truncate to filesystem limit
    return filename[:255]


# ── CORS Configuration ───────────────────────────────────────────────────
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]
