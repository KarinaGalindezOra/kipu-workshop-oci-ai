"""Ephemeral ADB pooling for one participant's local dashboard process."""

from dataclasses import dataclass
from typing import Any

from . import live_validation as live


def pool_identity(settings: live.LiveLab02Settings) -> tuple[str, str, str, str]:
    """Return non-secret settings that bind a pool to one participant target."""
    return (
        settings.participant_id,
        settings.db_user,
        settings.db_dsn,
        settings.wallet_dir,
    )


@dataclass
class LocalParticipantPool:
    """A one-connection pool that never retains plaintext password fields."""

    settings: live.LiveLab02Settings
    pool: Any | None = None

    @property
    def ready(self) -> bool:
        return self.pool is not None

    def matches(self, settings: live.LiveLab02Settings) -> bool:
        return pool_identity(self.settings) == pool_identity(settings)

    def acquire(
        self,
        *,
        database_password: str | None,
        wallet_password: str | None,
    ) -> Any:
        if self.pool is None:
            self.pool = live.create_database_pool(
                self.settings,
                database_password=database_password,
                wallet_password=wallet_password,
            )
        return live.acquire_database_connection(self.pool, self.settings)

    def close(self) -> None:
        if self.pool is not None:
            self.pool.close(force=True)
            self.pool = None
