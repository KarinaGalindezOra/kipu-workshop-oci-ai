from lab02_contract_rag.chunking import chunk_contract, contract_version


def test_chunk_contract_preserves_version_and_section_metadata() -> None:
    markdown = "# Sample\n\nContract Version: v2\n\n## Migration\n\nUse the new endpoint.\n"

    chunks = chunk_contract("synthetic://contracts/sample.md", markdown)

    assert contract_version(markdown) == "v2"
    assert len(chunks) == 1
    assert chunks[0].contract_version == "v2"
    assert chunks[0].section == "Migration"
    assert chunks[0].source_uri == "synthetic://contracts/sample.md"
    assert chunks[0].content_hash
