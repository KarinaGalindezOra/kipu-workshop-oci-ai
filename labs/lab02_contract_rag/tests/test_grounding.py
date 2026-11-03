from lab02_contract_rag.grounding import attach_evidence
from lab02_contract_rag.models import ContractChunk, RetrievedEvidence


def test_application_attaches_retrieved_metadata_to_answer() -> None:
    chunk = ContractChunk(
        chunk_id="v2-status",
        contract_version="v2",
        source_uri="synthetic://contracts/v2.md",
        section="Settlement status endpoint",
        content="PUT updates settlement status.",
        content_hash="test-hash",
    )
    evidence = [RetrievedEvidence(chunk=chunk, score=1)]

    envelope = attach_evidence("PUT updates settlement status.", evidence)

    assert envelope["answer"] == "PUT updates settlement status."
    assert envelope["sufficient_evidence"] is False
    assert envelope["support_assessment"] == "unverified_legacy_attachment"
    assert envelope["evidence"] == [
        {
            "chunk_id": "v2-status",
            "contract_version": "v2",
            "source_uri": "synthetic://contracts/v2.md",
            "section": "Settlement status endpoint",
            "content_hash": "test-hash",
        }
    ]


def test_missing_evidence_forces_insufficiency_response() -> None:
    envelope = attach_evidence("Invented answer", [])

    assert envelope == {
        "answer": "Insufficient evidence.",
        "sufficient_evidence": False,
        "evidence": [],
    }
