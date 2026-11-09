"""Participant operations must remain scoped, recoverable and free of model calls."""

import json
from types import SimpleNamespace

import pytest
from lab03_payment_agent.participant import (
    direct_tool_test,
    main,
    private_output,
    validate_exercise_sql,
    validate_role,
)

VALID_SQL = """CREATE OR REPLACE FUNCTION FIND_RELATED_REQUESTS(p_payment_id VARCHAR2)
RETURN CLOB AUTHID CURRENT_USER IS l_payload CLOB;
BEGIN
 SELECT JSON_OBJECT('requests' VALUE '[]' FORMAT JSON RETURNING CLOB) INTO l_payload FROM dual;
 RETURN WS3_TRACE('find_related_requests',p_payment_id,l_payload);
END;
/
"""


def test_completed_single_exercise_is_accepted():
    assert validate_exercise_sql(VALID_SQL).endswith("END;")


@pytest.mark.parametrize(
    "source",
    [
        VALID_SQL + "\nDROP TABLE WS3_REQUESTS;",
        VALID_SQL.replace("CURRENT_USER", "DEFINER"),
        VALID_SQL.replace("FIND_RELATED_REQUESTS", "OTHER_FUNCTION"),
        VALID_SQL.replace("FROM dual", "FROM dual; EXECUTE IMMEDIATE 'select 1 from dual'"),
        VALID_SQL + "\n-- TODO: unfinished",
        VALID_SQL + VALID_SQL,
    ],
)
def test_unsafe_or_unfinished_exercise_is_rejected(source):
    with pytest.raises(ValueError):
        validate_exercise_sql(source)


def test_private_outputs_never_overwrite_evidence(tmp_path):
    target = tmp_path / "existing.json"
    target.write_text("retained")
    with pytest.raises(ValueError, match="new private output"):
        private_output(target)
    assert target.read_text() == "retained"


@pytest.mark.parametrize("text", ["", "TODO: add rules", "x" * 4001])
def test_incomplete_or_unbounded_role_is_rejected(text):
    with pytest.raises(ValueError):
        validate_role(text)


def test_invalid_install_is_rejected_before_passwords_or_database(tmp_path, monkeypatch):
    sql = tmp_path / "exercise.sql"
    sql.write_text("TODO: implement the function")
    monkeypatch.setattr(
        "sys.argv",
        ["participant", "install-tool", "--session-file", "missing.env", "--sql-file", str(sql)],
    )
    with pytest.raises(ValueError, match="TODOs"):
        main()


class ToolCursor:
    def __init__(self, result, stored):
        self.result = result
        self.stored = stored
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self, sql, **values):
        self.statements.append((sql, values))

    def callfunc(self, name, return_type, values):
        assert name == "FIND_RELATED_REQUESTS"
        assert values == ["PAY-104"]
        return json.dumps(self.result)

    def fetchall(self):
        return self.stored

    def fetchone(self):
        return (1,)


@pytest.mark.parametrize("wrong", [False, True])
def test_direct_tool_test_compares_stored_facts_and_always_releases_its_lock(wrong):
    stored = [("R-1", "key", "hash")]
    result = {
        "requests": [
            {
                "request_id": "wrong" if wrong else "R-1",
                "idempotency_key": "key",
                "payload_hash": "hash",
            }
        ]
    }
    cursor = ToolCursor(result, stored)
    backend = SimpleNamespace(
        connection=SimpleNamespace(cursor=lambda: cursor, commit=lambda: None)
    )
    if wrong:
        with pytest.raises(ValueError, match="stored requests"):
            direct_tool_test(backend, "PAY-104")
    else:
        report = direct_tool_test(backend, "PAY-104")
        assert report["inference_calls"] == 0
        assert report["agent_executed"] is False
    assert cursor.statements[-1][0].startswith("delete from WS3_ACTIVE")
    assert all(values.get("p", "PAY-104") == "PAY-104" for _, values in cursor.statements)
