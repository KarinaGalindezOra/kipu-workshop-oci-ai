"""Tests for password-free participant session rendering."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[4] / "platform" / "bootstrap" / "create_lab02_private_session.py"
SPEC = importlib.util.spec_from_file_location("lab02_private_session", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_rendered_session_binds_participant_without_passwords():
    rendered = MODULE.render_session(
        participant="p001",
        config_file=Path("C:/private/config"),
        profile_name="TEST_PROFILE",
        compartment_id="ocid1.compartment.oc1..example",
    )

    assert "KHIPU_L2_P001" in rendered
    assert "cohere.embed-v4.0" in rendered
    assert "xai.grok-4.7" in rendered
    assert "$env:ADB_PASSWORD" not in rendered
    assert "$env:ADB_WALLET_PASSWORD" not in rendered
    assert "OCI_COMPARTMENT_ID = 'ocid1.compartment.oc1..example'" in rendered


def test_cli_error_classification_uses_safe_labels():
    assert MODULE.classify_cli_error("ConfigFileNotFound") == "config_file_not_found"
    assert MODULE.classify_cli_error("NotAuthenticated") == "not_authenticated"
    assert MODULE.classify_cli_error("unexpected") == "unclassified"
