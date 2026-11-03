import json

from lab02_contract_rag.chunking import chunk_contract
from lab02_contract_rag.reporting import json_safe, write_evidence
from lab02_contract_rag.retrieval import retrieve


def test_evidence_report_includes_version_and_source(tmp_path) -> None:
    markdown = "# V2\n\nContract Version: v2\n\n## Endpoint\n\nPUT updates settlement status.\n"
    evidence = retrieve(chunk_contract("synthetic://v2.md", markdown), "PUT status", "v2")

    write_evidence(tmp_path, "PUT status", "v2", evidence)

    payload = json.loads((tmp_path / "lab02-evidence.json").read_text())
    report = (tmp_path / "lab02-evidence.md").read_text()
    assert payload["evidence"][0]["contract_version"] == "v2"
    assert payload["evidence"][0]["source_uri"] == "synthetic://v2.md"
    assert "| v2 | Endpoint | synthetic://v2.md |" in report


def test_json_safe_does_not_stringify_unknown_provider_objects():
    class ProviderValue:
        def __str__(self):
            return "must-not-be-rendered"

    assert json_safe({"usage": ProviderValue()}) == {
        "usage": {"unavailable_value_type": "ProviderValue"}
    }
