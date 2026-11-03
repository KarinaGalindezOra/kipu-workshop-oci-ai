from dataclasses import replace
from unittest.mock import MagicMock

from lab02_contract_rag import live_validation as live
from lab02_contract_rag.local_pool import LocalParticipantPool


def settings():
    return live.LiveLab02Settings(
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


def test_pool_is_created_once_and_does_not_keep_password_fields(monkeypatch):
    database_pool = MagicMock()
    connection = MagicMock()
    database_pool.acquire.return_value = connection
    create = MagicMock(return_value=database_pool)
    monkeypatch.setattr(live, "create_database_pool", create)
    monkeypatch.setattr(live, "acquire_database_connection", lambda pool, _: pool.acquire())
    holder = LocalParticipantPool(settings())

    assert (
        holder.acquire(database_password="db-password", wallet_password="wallet-password")
        is connection
    )
    assert holder.acquire(database_password=None, wallet_password=None) is connection
    assert create.call_count == 1
    assert "password" not in holder.__dict__


def test_pool_rejects_a_different_participant_target():
    holder = LocalParticipantPool(settings())
    assert not holder.matches(replace(settings(), participant_id="p002", db_user="KHIPU_L2_P002"))


def test_pool_close_releases_only_the_local_pool():
    database_pool = MagicMock()
    holder = LocalParticipantPool(settings(), pool=database_pool)
    holder.close()
    database_pool.close.assert_called_once_with(force=True)
    assert not holder.ready
