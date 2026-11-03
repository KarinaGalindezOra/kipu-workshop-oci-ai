"""Read-only peer probe. Requires administrator attestation that the peer table exists."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_OCI_INTEGRATION_TESTS") != "true"
    or os.getenv("LAB02_PEER_TABLE_READY") != "true",
    reason="Requires explicit OCI opt-in and administrator-confirmed peer table",
)


def test_other_participant_table_is_inaccessible():
    from dotenv import load_dotenv
    from lab02_contract_rag.live_validation import (
        create_database_connection,
        settings_from_environment,
    )
    from lab02_contract_rag.participant import assert_peer_access_denied, participant_id

    load_dotenv()
    settings = settings_from_environment(require_calibration=False)
    peer = participant_id(os.environ["LAB02_PEER_PARTICIPANT_ID"])
    assert peer != settings.participant_id
    with create_database_connection(settings) as connection:
        assert_peer_access_denied(connection, peer, settings.table_name)
