"""Domain models for workshop memory scopes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryScope:
    """Identifies memory that belongs to one workshop team and agent."""

    team_id: str
    agent_id: str
    thread_id: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("team_id", self.team_id),
            ("agent_id", self.agent_id),
            ("thread_id", self.thread_id),
        ):
            if not value or value.strip() != value:
                raise ValueError(f"{field_name} must be a non-empty trimmed string")

    @property
    def key(self) -> tuple[str, str, str]:
        """Return the store key used by the local deterministic adapter."""

        return (self.team_id, self.agent_id, self.thread_id)


@dataclass(frozen=True)
class Guideline:
    """A procedural instruction persisted as a memory guideline."""

    identifier: str
    content: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier:
            raise ValueError("identifier is required")
        if not self.content:
            raise ValueError("content is required")
