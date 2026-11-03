"""Unit checks for the dashboard's visible evidence-selection semantics."""

from lab02_contract_rag.dashboard import candidate_selection


def test_candidate_selection_marks_only_cited_chunks():
    rows, by_chunk = candidate_selection(
        {
            "citations": [{"chunk_id": "selected"}],
            "candidates": [
                {"chunk_id": "closer", "rank_value": 0.31},
                {"chunk_id": "selected", "rank_value": 0.44},
            ],
        }
    )

    assert by_chunk["selected"]["rank_value"] == 0.44
    assert [row["selected_as_evidence"] for row in rows] == [False, True]
