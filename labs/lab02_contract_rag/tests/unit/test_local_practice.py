from lab02_contract_rag.local_practice import corpus_inspection, local_case_result


def test_local_inspection_returns_the_frozen_nine_chunks() -> None:
    inspection = corpus_inspection()

    assert inspection["network_access"] is False
    assert inspection["chunk_count"] == 9
    assert {chunk["contract_version"] for chunk in inspection["chunks"]} == {"v1", "v2"}


def test_local_practice_keeps_comparison_evidence_separate_by_version() -> None:
    result = local_case_result("T08", "p001")

    assert result["status"] == "answered"
    assert result["practice_mode"] == "local_lexical_retrieval"
    assert {source["contract_version"] for source in result["citations"]} == {"v1", "v2"}
    assert all(candidate["method"] == "lexical" for candidate in result["candidates"])
