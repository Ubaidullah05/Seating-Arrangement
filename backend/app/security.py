"""
Authentication utilities for the Exam Seating Planner.

- Password hashing: PBKDF2-HMAC-SHA256 (stdlib, no external dependencies)
- Session tokens: HMAC-SHA256 signed payload (stdlib, no external dependencies)
- Strict credential format validators:
    * Students  : register number = exactly 16 digits, password = DOB in DD/MM/YYYY
    * Faculty   : institutional email ending @jerusalemengg.ac.in
"""
import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from datetime import datetime
from typing import Any, Dict, Optional

from backend.app.config import AUTH_SECRET_KEY, AUTH_TOKEN_TTL_SECONDS

# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------
PBKDF2_ITERATIONS = 260_000
_PBKDF2_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    )
    return f"{_PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        algorithm, iterations_s, salt, expected_hex = hashed.split("$")
        if algorithm != _PBKDF2_PREFIX:
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations_s)
        )
        return hmac.compare_digest(dk.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Signed session tokens (HMAC-SHA256)
# ---------------------------------------------------------------------------
def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(payload: Dict[str, Any], ttl_seconds: Optional[int] = None) -> str:
    ttl = ttl_seconds if ttl_seconds is not None else AUTH_TOKEN_TTL_SECONDS
    body = dict(payload)
    body["exp"] = int(time.time()) + int(ttl)
    body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
    encoded = _b64encode(body_json.encode("utf-8"))
    signature = hmac.new(
        AUTH_SECRET_KEY.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256
    ).hexdigest()
    return f"{encoded}.{signature}"


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Return the payload if the token is authentic and unexpired, else None."""
    try:
        encoded, signature = token.rsplit(".", 1)
    except ValueError:
        return None
    expected = hmac.new(
        AUTH_SECRET_KEY.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    try:
        payload = json.loads(_b64decode(encoded))
    except (ValueError, json.JSONDecodeError):
        return None
    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return None
    return payload


# ---------------------------------------------------------------------------
# Strict credential format validators
# ---------------------------------------------------------------------------
REGISTER_NO_RE = re.compile(r"^\d{16}$")
# Strict DD/MM/YYYY: two-digit day, two-digit month, four-digit year, slashes only.
DOB_RE = re.compile(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$")
# Institutional email: anything @jerusalemengg.ac.in (single @, no spaces).
FACULTY_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@jerusalemengg\.ac\.in$")


def is_valid_register_no(value: str) -> bool:
    return bool(REGISTER_NO_RE.match((value or "").strip().lstrip("'")))


def is_strict_ddmmyyyy(value: str) -> bool:
    """True only for a real calendar date written exactly as DD/MM/YYYY."""
    s = (value or "").strip()
    if not DOB_RE.match(s):
        return False
    try:
        datetime.strptime(s, "%d/%m/%Y")
    except ValueError:
        return False
    return True


def is_faculty_email(value: str) -> bool:
    return bool(FACULTY_EMAIL_RE.match((value or "").strip()))


# Default faculty credentials (single ACOE account)
DEFAULT_FACULTY_EMAIL = "acoe@jerusalemengg.ac.in"
DEFAULT_FACULTY_PASSWORD = "acoe@123"
