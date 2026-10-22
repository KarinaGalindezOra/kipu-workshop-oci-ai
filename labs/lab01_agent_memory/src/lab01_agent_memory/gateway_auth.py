"""Local-only signed identity adapter for the Lab 1 deployment gateway.

This module deliberately derives the team scope from a signed token.  The
deployment API must never trust a raw team identifier supplied by a browser.
The HMAC adapter is for the local rehearsal only; an OCI deployment will
replace it with the workshop's approved identity provider.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass

TEAM_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,31}$")


class TokenValidationError(ValueError):
    """Raised when a local workshop token cannot be trusted."""


@dataclass(frozen=True)
class TeamIdentity:
    """The identity derived by the server from a verified token."""

    team_id: str


def _encode(payload: dict[str, object]) -> str:
    """Encode a small JSON payload in URL-safe base64 without padding."""

    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).decode("ascii").rstrip("=")


def _decode(value: str) -> dict[str, object]:
    """Decode and validate the payload portion of a local token."""

    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise TokenValidationError("Token payload is invalid") from error
    if not isinstance(payload, dict):
        raise TokenValidationError("Token payload is invalid")
    return payload


def _validate_team_id(team_id: object) -> str:
    """Return a valid workshop team identifier."""

    if not isinstance(team_id, str) or not TEAM_ID_PATTERN.fullmatch(team_id):
        raise TokenValidationError("Token team identifier is invalid")
    return team_id


def _validate_secret(secret: str) -> None:
    """Reject weak local secrets before any token is issued or validated."""

    if len(secret) < 16:
        raise ValueError("LAB01_WORKSHOP_TOKEN_SECRET must contain at least 16 characters")


def issue_local_team_token(team_id: str, secret: str, ttl_seconds: int = 3600) -> str:
    """Issue a short-lived token for a single local-rehearsal team."""

    _validate_secret(secret)
    validated_team_id = _validate_team_id(team_id)
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be greater than zero")
    payload = {
        "aud": "lab01-local-gateway",
        "exp": int(time.time()) + ttl_seconds,
        "team_id": validated_team_id,
    }
    encoded_payload = _encode(payload)
    signature = hmac.new(
        secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256
    ).hexdigest()
    return f"{encoded_payload}.{signature}"


def verify_local_team_token(token: str, secret: str) -> TeamIdentity:
    """Verify a local-rehearsal token and return its server-derived identity."""

    _validate_secret(secret)
    try:
        encoded_payload, received_signature = token.split(".", maxsplit=1)
    except ValueError as error:
        raise TokenValidationError("Token format is invalid") from error
    expected_signature = hmac.new(
        secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(received_signature, expected_signature):
        raise TokenValidationError("Token signature is invalid")

    payload = _decode(encoded_payload)
    if payload.get("aud") != "lab01-local-gateway":
        raise TokenValidationError("Token audience is invalid")
    expires_at = payload.get("exp")
    if not isinstance(expires_at, int) or expires_at <= int(time.time()):
        raise TokenValidationError("Token has expired")
    return TeamIdentity(team_id=_validate_team_id(payload.get("team_id")))
