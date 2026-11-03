"""Tests for safe errors emitted by the participant schema bootstrap."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[4] / "platform" / "bootstrap" / "create_lab02_participant.py"
SPEC = importlib.util.spec_from_file_location("lab02_participant_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_safe_error_code_prefers_oracle_full_code():
    class Detail:
        full_code = "ORA-01031"
        code = 1031

    assert MODULE.safe_error_code(Exception(Detail())) == "ORA-01031"


def test_safe_error_code_does_not_require_provider_message():
    assert MODULE.safe_error_code(RuntimeError()) == "RuntimeError"


@pytest.mark.parametrize("password", ["Valid$Participant#2026", "Valid:Participant~2026"])
def test_password_validation_accepts_printable_ascii_without_quotes(password):
    MODULE.validate_participant_password(password)


@pytest.mark.parametrize(
    "password",
    ["too-short", "Invalid SpacePassword#2026", 'Invalid"QuotePassword#2026'],
)
def test_password_validation_rejects_unsafe_values(password):
    with pytest.raises(ValueError):
        MODULE.validate_participant_password(password)
