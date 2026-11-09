"""Read-only readiness by default; paid acceptance uses the separate CLI."""

import os
from pathlib import Path

import pytest


@pytest.mark.skipif(
    os.getenv("RUN_OCI_INTEGRATION_TESTS") != "true", reason="OCI integration is opt-in"
)
def test_assigned_adb_readiness():
    from getpass import getpass

    from lab03_payment_agent.live import LiveBackend, Settings

    settings = Settings.load(Path(os.environ["LAB03_SESSION_FILE"]))
    backend = LiveBackend(settings, getpass("Database password: "), getpass("Wallet password: "))
    try:
        assert backend.readiness()["identity_verified"]
    finally:
        backend.close()
