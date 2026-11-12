"""Builder safety and native registration boundaries without OCI access."""

import json
import re
from types import SimpleNamespace

import pytest
from lab03_payment_agent.agent_builder import TEAM, AgentBlueprint, register


def blueprint():
    return AgentBlueprint(
        "Investigate O'Brien's synthetic payment.",
        "Use approved evidence and observed read-only tools.",
    )


def fake_backend(monkeypatch, existing=False, fail_at=None):
    monkeypatch.delenv("LAB03_RECOVERY_REVIEW_FILE", raising=False)
    calls = []
    created = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql, **bindings):
            available_views = {
                "USER_CLOUD_AI_PROFILES",
                "USER_AI_AGENT_TOOLS",
                "USER_AI_AGENTS",
                "USER_AI_AGENT_TASKS",
                "USER_AI_AGENT_TEAMS",
            }
            referenced = re.findall(r"\bfrom\s+([A-Z_]+)", sql, re.IGNORECASE)
            if any(view.upper() not in available_views for view in referenced):
                raise RuntimeError(
                    "ORA-00942: view is not available in the verified database contract"
                )
            self.sql, self.bindings = sql, bindings
            calls.append((sql, bindings))
            if "CREATE_" in sql:
                if fail_at == len(created):
                    raise RuntimeError("Synthetic registration failure")
                created.append(bindings["name"])

        def fetchone(self):
            if "USER_CLOUD_AI_PROFILES" in self.sql:
                return (1,)
            return (int(existing or self.bindings.get("name") in created),)

    backend = SimpleNamespace(
        identity="WS3_P002",
        settings=SimpleNamespace(db_user="WS3_P002"),
        readiness=lambda **kwargs: {"schema_ready": True},
        connection=SimpleNamespace(cursor=Cursor, commit=lambda: None),
    )
    return backend, calls, created


def test_native_creation_uses_six_bound_objects_and_no_model_calls(monkeypatch):
    backend, calls, created = fake_backend(monkeypatch)
    definition = blueprint()
    receipt = register(backend, definition, definition.fingerprint)
    assert len(created) == 6 and receipt["team"] == TEAM
    assert receipt["agent_runs"] == receipt["embedding_calls"] == 0
    creation = [(sql, bindings) for sql, bindings in calls if "CREATE_" in sql]
    assert all(":attributes" in sql and "O'Brien" not in sql for sql, _ in creation)
    assert "O'Brien" in json.loads(creation[3][1]["attributes"])["role"]
    assert "O''Brien" in definition.sql()
    assert not any("DROP_" in sql or "RUN_TEAM" in sql for sql, _ in calls)


def test_changed_design_requires_new_human_approval(monkeypatch):
    backend, calls, _ = fake_backend(monkeypatch)
    definition = blueprint()
    with pytest.raises(ValueError, match="exact previewed"):
        register(backend, definition, "previous-design-hash")
    assert not calls


@pytest.mark.parametrize(
    "tools",
    [
        ("get_payment", "execute_sql"),
        ("get_payment",),
        ("get_payment", "get_payment_events", "find_related_requests", "http"),
    ],
)
def test_builder_cannot_add_arbitrary_capabilities(tools):
    with pytest.raises(ValueError, match="fixed read-only"):
        AgentBlueprint(
            "Investigate the synthetic payment.", "Use approved procedural guidance.", tools
        ).sql()


def test_existing_objects_are_never_overwritten(monkeypatch):
    backend, calls, created = fake_backend(monkeypatch, existing=True)
    definition = blueprint()
    with pytest.raises(ValueError, match="already exists"):
        register(backend, definition, definition.fingerprint)
    assert not created and not any("CREATE_" in sql for sql, _ in calls)


def test_partial_creation_is_reported_without_cleanup_or_retry(monkeypatch):
    backend, calls, created = fake_backend(monkeypatch, fail_at=3)
    definition = blueprint()
    with pytest.raises(RuntimeError):
        register(backend, definition, definition.fingerprint)
    assert backend.last_builder_objects == created and len(created) == 3
    assert not any("DROP" in sql for sql, _ in calls)


def test_sql_preview_preserves_long_unicode_json_without_oversized_literals():
    import re

    definition = AgentBlueprint("Investigate synthetic payments.", "O'Brien " + "🧭" * 1400)
    preview = definition.sql()
    for statement, (_, _, expected) in zip(preview.splitlines()[3:9], definition.objects()):
        parts = re.findall(r"TO_CLOB\('((?:[^']|'')*)'\)", statement)
        assert parts and all(len(part.encode("utf-8")) < 4000 for part in parts)
        assert json.loads("".join(part.replace("''", "'") for part in parts)) == expected
