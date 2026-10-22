from lab01_agent_memory.models import Guideline, MemoryScope
from lab01_agent_memory.store import ScopedMemoryStore


def test_memory_is_isolated_by_team_scope() -> None:
    store = ScopedMemoryStore()
    team_one = MemoryScope("team-01", "agent", "thread")
    team_two = MemoryScope("team-02", "agent", "thread")
    store.add_guideline(team_one, Guideline("payment-rule", "Use idempotency keys.", ("payment",)))

    assert [item.identifier for item in store.search(team_one, "payment")] == ["payment-rule"]
    assert store.search(team_two, "payment") == []
