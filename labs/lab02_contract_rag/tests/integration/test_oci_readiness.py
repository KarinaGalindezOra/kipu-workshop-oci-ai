"""Explicitly opt-in read-only connectivity check. No inference or resource mutation."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_OCI_INTEGRATION_TESTS") != "true",
    reason="OCI integration is disabled by default",
)


def test_prepared_vector_table_is_readable():
    from dotenv import load_dotenv
    from lab02_contract_rag.live_validation import (
        create_database_connection,
        settings_from_environment,
    )

    load_dotenv()
    settings = settings_from_environment()
    with create_database_connection(settings) as connection, connection.cursor() as cursor:
        cursor.execute(f"SELECT embedding_dimension FROM {settings.table_name} WHERE 1=0")
