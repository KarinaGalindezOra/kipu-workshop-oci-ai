"""CLI session assignment checks without real credentials or network calls."""

import base64
import json
import time

import pytest
from lab03_payment_agent.oci_profile import profile_user


def test_session_subject_without_config_user(tmp_path):
    body = (
        base64.urlsafe_b64encode(
            json.dumps({"sub": "synthetic-subject", "exp": time.time() + 60}).encode()
        )
        .decode()
        .rstrip("=")
    )
    token = tmp_path / "synthetic-token"
    token.write_text("header." + body + ".signature")
    assert profile_user({"security_token_file": str(token)}) == "synthetic-subject"


def test_expired_session_rejected(tmp_path):
    body = (
        base64.urlsafe_b64encode(json.dumps({"sub": "synthetic-subject", "exp": 1}).encode())
        .decode()
        .rstrip("=")
    )
    token = tmp_path / "synthetic-token"
    token.write_text("header." + body + ".signature")
    with pytest.raises(ValueError, match="expired"):
        profile_user({"security_token_file": str(token)})


def test_missing_profile_identity_rejected():
    with pytest.raises(ValueError, match="missing"):
        profile_user({})
