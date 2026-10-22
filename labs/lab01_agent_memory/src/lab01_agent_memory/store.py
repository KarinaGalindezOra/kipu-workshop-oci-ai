"""Deterministic local adapter used before OCI Agent Memory integration."""

from collections import defaultdict

from .models import Guideline, MemoryScope


class ScopedMemoryStore:
    """Stores and searches guidelines within an exact workshop memory scope."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], list[Guideline]] = defaultdict(list)

    def add_guideline(self, scope: MemoryScope, guideline: Guideline) -> None:
        """Persist a guideline for one team, agent, and thread only."""

        self._records[scope.key].append(guideline)

    def search(self, scope: MemoryScope, query: str) -> list[Guideline]:
        """Return scoped matches using simple keyword overlap for the offline demo."""

        terms = {term.lower() for term in query.split() if term}
        matches: list[Guideline] = []
        for guideline in self._records[scope.key]:
            searchable = f"{guideline.identifier} {guideline.content} {' '.join(guideline.tags)}".lower()
            if any(term in searchable for term in terms):
                matches.append(guideline)
        return matches

    def count(self, scope: MemoryScope) -> int:
        """Return records visible to a scope."""

        return len(self._records[scope.key])
