"""Unit tests for the participant vector-table bootstrap contract."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[4] / "platform" / "bootstrap" / "create_lab02_participant_table.py"
SPEC = importlib.util.spec_from_file_location("lab02_participant_table_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_table_statements_keep_scope_and_synthetic_constraints():
    create_table, create_index = MODULE.table_statements(1536)

    assert "VECTOR(1536, FLOAT32)" in create_table
    assert "contract_version IN ('v1', 'v2')" in create_table
    assert "data_classification = 'synthetic'" in create_table
    assert "lab02_contract_scope_ix" in create_index


def test_table_statements_reject_invalid_dimension():
    with pytest.raises(ValueError, match="positive"):
        MODULE.table_statements(0)
