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


def test_dotenv_session_is_cross_platform_and_password_free():
    rendered = MODULE.render_dotenv_session(
        participant="p002",
        profile_name="KWS2_P002",
        compartment_id="ocid1.compartment.oc1..example",
        wallet_dir=Path("/private/wallet"),
        connect_alias="kws2rag_tp",
        calibration_file=Path("/private/calibration.json"),
        development_measurements_file=Path("/private/measurements.json"),
        report_root=Path("/private/artifacts"),
    )

    assert "LAB02_PARTICIPANT_ID=p002" in rendered
    assert "ADB_USERNAME=KHIPU_L2_P002" in rendered
    assert "OCI_CONFIG_FILE" not in rendered
    assert "PASSWORD" not in rendered
    assert "TOKEN" not in rendered


def test_portable_powershell_session_uses_the_participant_home_directory():
    rendered = MODULE.render_session(
        participant="p002",
        config_file=Path("C:/facilitator/config"),
        profile_name="KWS2_P002",
        compartment_id="ocid1.compartment.oc1..example",
        portable=True,
    )

    assert "$env:OCI_CONFIG_FILE = Join-Path $HOME '.oci\\config'" in rendered
    assert "$env:ADB_WALLET_DIR = Join-Path $HOME '.khipu\\lab02\\wallet'" in rendered
    assert "C:/facilitator/config" not in rendered
