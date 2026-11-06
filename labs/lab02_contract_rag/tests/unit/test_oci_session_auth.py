"""Tests for the participant OCI CLI authentication bootstrap."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "authenticate_oci_session.py"
SPEC = importlib.util.spec_from_file_location("lab02_oci_session_auth", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_authentication_command_uses_participant_profile_name():
    command = MODULE.authenticate_command(
        config_file=Path("/private/config"),
        profile_name="KWS2_P002",
        region="us-chicago-1",
        minutes=60,
    )

    assert "--profile-name" in command
    assert command[command.index("--profile-name") + 1] == "KWS2_P002"
    assert "--profile" not in command
    assert command[command.index("--region") + 1] == "us-chicago-1"


def test_validation_command_uses_security_token_profile():
    command = MODULE.validate_command(
        config_file=Path("/private/config"), profile_name="KWS2_P002"
    )

    assert command[:2] == ["oci", "--config-file"]
    assert command[command.index("--profile") + 1] == "KWS2_P002"
    assert command[command.index("--auth") + 1] == "security_token"
