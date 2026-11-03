from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from lab02_contract_rag import live_validation
from lab02_contract_rag.participant import (
    artifact_directory,
    assert_peer_access_denied,
    participant_id,
    participant_schema,
    validate_database_session,
)


@pytest.mark.parametrize("value", ["p000", "p1000", "../p001", "p01", "p001.x", "P001", None])
def test_participant_codes_are_closed_and_path_safe(value):
    with pytest.raises(ValueError):
        participant_id(value)


def test_individual_schema_and_output_mapping(tmp_path):
    assert participant_schema("p001") == "KHIPU_L2_P001"
    assert participant_schema("p002") == "KHIPU_L2_P002"
    assert artifact_directory(tmp_path, "p001", "run1") != artifact_directory(
        tmp_path, "p002", "run1"
    )
    with pytest.raises(ValueError):
        artifact_directory(tmp_path, "p001", "../../outside")


def connection_with_results(*rows):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.side_effect = rows
    return connection, cursor


def test_valid_individual_session_is_accepted():
    connection, cursor = connection_with_results(("KHIPU_L2_P001", "KHIPU_L2_P001"), None, None)
    validate_database_session(connection, "p001")
    assert cursor.execute.call_count == 3


@pytest.mark.parametrize(
    "identity,any_privilege,admin_role",
    [
        (("KHIPU_L2_P002", "KHIPU_L2_P002"), None, None),
        (("KHIPU_L2_P001", "KHIPU_L2_P002"), None, None),
        (("ADMIN", "ADMIN"), None, None),
        (("KHIPU_L2_P001", "KHIPU_L2_P001"), ("SELECT ANY TABLE",), None),
        (("KHIPU_L2_P001", "KHIPU_L2_P001"), None, ("DBA",)),
    ],
)
def test_shared_impersonated_or_privileged_sessions_are_rejected(
    identity, any_privilege, admin_role
):
    connection, _ = connection_with_results(identity, any_privilege, admin_role)
    with pytest.raises(ValueError):
        validate_database_session(connection, "p001")


@pytest.mark.parametrize("code", [942, 1031])
def test_known_peer_table_access_denial_is_accepted(code):
    connection, cursor = connection_with_results()
    cursor.execute.side_effect = Exception(SimpleNamespace(code=code))
    assert_peer_access_denied(connection, "p002", "LAB02_CONTRACT_CHUNKS")
    assert "KHIPU_L2_P002.LAB02_CONTRACT_CHUNKS" in cursor.execute.call_args.args[0]


def test_successful_peer_read_fails_isolation():
    connection, _ = connection_with_results()
    with pytest.raises(ValueError, match="can read"):
        assert_peer_access_denied(connection, "p002", "LAB02_CONTRACT_CHUNKS")


def test_network_error_is_not_reported_as_isolation_success():
    connection, cursor = connection_with_results()
    cursor.execute.side_effect = TimeoutError()
    with pytest.raises(ValueError, match="other than access denial"):
        assert_peer_access_denied(connection, "p002", "LAB02_CONTRACT_CHUNKS")


def test_failed_session_verification_closes_connection(monkeypatch):
    settings = live_validation.LiveLab02Settings(
        "placeholder",
        "model",
        "chat",
        "KHIPU_L2_P001",
        "dsn",
        "wallet",
        2,
        "CHUNKS",
        3,
        "DEFAULT",
        None,
    )
    connection, _ = connection_with_results(("KHIPU_L2_P002", "KHIPU_L2_P002"))
    monkeypatch.setattr(live_validation.oracledb, "connect", lambda **kw: connection)
    monkeypatch.setattr(live_validation, "getpass", lambda prompt: "not-a-real-password")
    with pytest.raises(ValueError):
        live_validation.create_database_connection(settings)
    connection.close.assert_called_once()
    with pytest.raises(ValueError, match="mismatched"):
        live_validation.create_database_connection(replace(settings, db_user="SHARED_TEAM"))


def test_settings_require_explicit_participant_and_matching_schema(monkeypatch, tmp_path):
    values = {
        "OCI_COMPARTMENT_ID": "placeholder",
        "OCI_EMBEDDING_MODEL_ID": "model",
        "OCI_CHAT_MODEL_ID": "chat",
        "ADB_USERNAME": "KHIPU_L2_P001",
        "ADB_CONNECT_STRING": "dsn",
        "ADB_WALLET_DIR": str(tmp_path),
        "LAB02_VECTOR_DIMENSION": "2",
        "LAB02_CONTRACT_TABLE": "CHUNKS",
        "LAB02_PARTICIPANT_ID": "p001",
        "OCI_REGION": "us-chicago-1",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    assert (
        live_validation.settings_from_environment(require_calibration=False).participant_id
        == "p001"
    )
    monkeypatch.setenv("ADB_USERNAME", "KHIPU_L2_P002")
    with pytest.raises(ValueError, match="assigned"):
        live_validation.settings_from_environment(require_calibration=False)
    monkeypatch.delenv("LAB02_PARTICIPANT_ID")
    with pytest.raises(RuntimeError, match="LAB02_PARTICIPANT_ID"):
        live_validation.settings_from_environment(require_calibration=False)
