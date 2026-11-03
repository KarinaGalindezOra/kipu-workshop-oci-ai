from lab02_contract_rag.chunking import chunk_contract
from lab02_contract_rag.retrieval import retrieve


def test_retrieval_filters_to_requested_contract_version_before_ranking() -> None:
    v1 = "# V1\n\nContract Version: v1\n\n## Status\n\nPATCH uses payment_status.\n"
    v2 = (
        "# V2\n\nContract Version: v2\n\n## Migration\n\n"
        "PUT uses status and rejects payment_status.\n"
    )
    chunks = chunk_contract("synthetic://v1.md", v1) + chunk_contract("synthetic://v2.md", v2)

    results = retrieve(chunks, "How does v2 use status?", contract_version="v2")

    assert results
    assert all(item.chunk.contract_version == "v2" for item in results)
    assert results[0].chunk.section == "Migration"
