import hashlib
import json
from dataclasses import replace

import pytest
from lab02_contract_rag.agent import resolve_request, run_agent, validate_generation
from lab02_contract_rag.corpus import LAB_ROOT, load_corpus
from lab02_contract_rag.evaluation import evaluate
from lab02_contract_rag.grounding import attach_evidence
from lab02_contract_rag.retrieval import retrieve


@pytest.fixture
def chunks():
    return load_corpus()


def test_full_frozen_acceptance_matrix():
    cases = json.loads((LAB_ROOT / "data/evaluation/acceptance_questions.json").read_text())
    report = evaluate(cases)
    assert report["acceptance_pass"]
    assert len(report["cases"]) == 20
    assert report["cloud_validation"] == "not_run"
    assert report["human_relevance_review_required"]


def test_manifest_and_source_locations(chunks):
    assert len(chunks) == 9
    for chunk in chunks:
        name = chunk.source_uri.rsplit("/", 1)[1]
        lines = (LAB_ROOT / "data" / name).read_text().splitlines()
        selected = "\n".join(lines[chunk.line_start - 1 : chunk.line_end])
        assert chunk.section in selected and chunk.content in selected
        assert hashlib.sha256(chunk.content.encode()).hexdigest() == chunk.content_hash
        assert chunk.embedding is None and chunk.loaded_at is None


def test_manifest_rejects_modified_source(tmp_path):
    for name in ("contract_v1.md", "contract_v2.md", "corpus_manifest.json"):
        (tmp_path / name).write_bytes((LAB_ROOT / "data" / name).read_bytes())
    with (tmp_path / "contract_v2.md").open("ab") as target:
        target.write(b"\nchanged")
    with pytest.raises(ValueError, match="manifest"):
        load_corpus(tmp_path)


@pytest.mark.parametrize(
    "question,version,status",
    [
        ("How do I update status?", None, "needs_clarification"),
        ("In v2, what endpoint?", "v1", "needs_clarification"),
        ("In v3, what endpoint?", None, "insufficient_evidence"),
        ("How many transactions?", None, "structured_data_required"),
        ("In v2, what SLA is guaranteed?", None, "insufficient_evidence"),
    ],
)
def test_nonanswer_paths_do_not_call_generator(question, version, status):
    def forbidden(*args):
        pytest.fail("A nonanswer request must not call retrieval or generation")

    assert run_agent(question, forbidden, version=version, generator=forbidden)["status"] == status


def test_partial_answer_does_not_claim_complete_support(chunks):
    result = run_agent(
        "In v2, describe the endpoint and SLA availability.", lambda v, q: retrieve(chunks, q, v)
    )
    assert result["status"] == "partial"
    assert result["claims"] and not result["sufficient_evidence"]
    assert "99.9" not in result["answer"]


def test_wrong_scope_is_an_error(chunks):
    wrong = retrieve(chunks, "idempotency header", "v1")
    result = run_agent("In v2, what idempotency header?", lambda v, q: wrong)
    assert result["status"] == "error" and not result["claims"]
    assert result["error_stage"] == "retrieve"


def test_nonempty_irrelevant_candidates_do_not_mean_support(chunks):
    unrelated = retrieve(chunks, "idempotency header", "v2")[:1]
    result = run_agent("In v2, what error for an invalid status?", lambda v, q: unrelated)
    assert result["candidates"]
    assert result["status"] == "insufficient_evidence"
    assert not result["sufficient_evidence"]


def test_provider_abstention_with_nonempty_results(chunks):
    result = run_agent(
        "In v2, what idempotency header?",
        lambda v, q: retrieve(chunks, q, v),
        generator=lambda q, e: {"status": "insufficient_evidence", "claims": []},
    )
    assert result["status"] == "insufficient_evidence"
    assert result["candidates"] and not result["sufficient_evidence"]
    assert (
        attach_evidence("Insufficient evidence.", retrieve(chunks, "status", "v2"))[
            "sufficient_evidence"
        ]
        is False
    )


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"status": "answered", "claims": []},
        {"status": "answered", "claims": [{"text": "Invented SLA", "evidence_ids": ["E1"]}]},
        {"status": "answered", "claims": [{"text": "Supported.", "evidence_ids": ["E9"]}]},
        {"status": "insufficient_evidence", "claims": [{"text": "Contradiction"}]},
    ],
)
def test_generation_rejects_malformed_or_unsupported_claims(payload):
    with pytest.raises(ValueError):
        validate_generation(payload, [{"evidence_id": "E1", "excerpt": "Supported."}])


def test_changed_content_hash_fails_closed(chunks):
    item = retrieve(chunks, "idempotency header", "v2")[0]
    changed = replace(item, chunk=replace(item.chunk, content="Changed content"))
    result = run_agent("In v2, what idempotency header?", lambda v, q: [changed])
    assert result["status"] == "error"


def test_filters_exclude_old_corpus_and_other_api(chunks):
    invalid = [replace(c, corpus_id="old") for c in chunks]
    invalid += [replace(c, api_name="another-api") for c in chunks]
    assert not retrieve(invalid, "status", "v2")


def test_comparison_resolves_two_independent_versions():
    versions, status, _ = resolve_request("Compare idempotency headers")
    assert versions == ["v1", "v2"] and status is None


def test_exceptions_do_not_expose_provider_details():
    def fail(*args):
        raise RuntimeError("SECRET_PASSWORD=private-value")

    result = run_agent("In v2, what endpoint?", fail)
    assert result["status"] == "error"
    assert "private-value" not in json.dumps(result)
