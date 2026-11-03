import json
from dataclasses import asdict, replace
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from lab02_contract_rag.corpus import load_corpus
from lab02_contract_rag.live_validation import (
    LiveLab02Settings,
    chunks_to_insert,
    create_inference_client,
    embed_texts,
    embedding_fingerprint,
    generate_grounded_answer,
    insert_chunks,
    retrieve_evidence,
)


@pytest.fixture
def settings():
    return LiveLab02Settings(
        "placeholder",
        "embedding-model",
        "chat-model",
        "TEAM",
        "dsn",
        "wallet",
        2,
        "LAB02_CONTRACT_CHUNKS",
        3,
        "DEFAULT",
        None,
        max_cosine_distance=0.4,
    )


def test_embedding_request_never_truncates(settings):
    client = Mock()
    client.embed_text.return_value.data.embeddings = [[0.1, 0.2]]
    assert embed_texts(client, settings, ["content"], "SEARCH_DOCUMENT") == [[0.1, 0.2]]
    request = client.embed_text.call_args.args[0]
    assert request.truncate == "NONE" and request.input_type == "SEARCH_DOCUMENT"
    assert request.output_dimensions is None


@pytest.mark.parametrize("vectors", [[], [[1]], [[float("nan"), 1]], [[0, 0]]])
def test_bad_embedding_response_is_rejected(settings, vectors):
    client = Mock()
    client.embed_text.return_value.data.embeddings = vectors
    with pytest.raises(RuntimeError):
        embed_texts(client, settings, ["content"], "SEARCH_QUERY")


def test_configured_dimension_only_for_approved_models(settings):
    client = Mock()
    client.embed_text.return_value.data.embeddings = [[1, 2]]
    embed_texts(client, replace(settings, set_output_dimensions=True), ["text"], "SEARCH_QUERY")
    assert client.embed_text.call_args.args[0].output_dimensions == 2


def test_client_uses_explicit_region_and_no_automatic_retry(settings, monkeypatch):
    monkeypatch.setattr("oci.config.from_file", lambda **kw: {"region": "us-ashburn-1"})
    factory = Mock()
    monkeypatch.setattr("oci.generative_ai_inference.GenerativeAiInferenceClient", factory)
    create_inference_client(settings)
    assert factory.call_args.args[0]["region"] == "us-chicago-1"
    assert factory.call_args.kwargs["timeout"] == (10, 30)


def test_same_content_different_embedding_space_is_not_reused(settings):
    chunk = load_corpus()[0]
    old = (chunk.content_hash, "old-model", 2, chunk.embedding_input_hash)
    with pytest.raises(RuntimeError, match="Refusing"):
        chunks_to_insert([chunk], {chunk.chunk_id: old}, settings)
    assert (
        chunks_to_insert(
            [chunk], {chunk.chunk_id: embedding_fingerprint(chunk, settings)}, settings
        )
        == []
    )


def row(settings, *, distance=0.2, version="v2"):
    chunk = next(c for c in load_corpus() if c.contract_version == version)
    chunk = replace(
        chunk,
        embedding_model_id=settings.embedding_model_id,
        embedding_dimension=settings.vector_dimension,
    )
    metadata = asdict(chunk)
    return json.dumps(metadata), distance


def cursor_for(rows):
    cursor = Mock()
    cursor.__iter__ = Mock(return_value=iter(rows))
    return cursor


def test_exact_search_binds_all_scope_filters_and_reads_clobs(settings):
    raw, distance = row(settings)
    cursor = cursor_for([(SimpleNamespace(read=lambda: raw), distance)])
    items = retrieve_evidence(cursor, settings.table_name, "v2", [1, 2], 3, settings)
    statement = cursor.execute.call_args.args[0]
    binds = cursor.execute.call_args.kwargs
    assert "FETCH EXACT FIRST 3" in statement
    for field in ("corpus_id", "contract_version", "api_name", "model_id", "dimension"):
        assert field in binds
    assert "data_classification = 'synthetic'" in statement
    assert items[0].score_type == "cosine_distance"


def test_weak_vector_neighbor_is_not_evidence(settings):
    assert (
        retrieve_evidence(
            cursor_for([row(settings, distance=0.8)]),
            settings.table_name,
            "v2",
            [1, 2],
            3,
            settings,
        )
        == []
    )


def test_database_metadata_cannot_bypass_scope(settings):
    with pytest.raises(ValueError, match="scope"):
        retrieve_evidence(
            cursor_for([row(settings, version="v1")]),
            settings.table_name,
            "v2",
            [1, 2],
            3,
            settings,
        )


def test_insert_uses_native_float_vector_and_parameters(settings):
    cursor = Mock()
    insert_chunks(cursor, settings.table_name, load_corpus()[:1], [[1, 2]], settings)
    statement, rows = cursor.executemany.call_args.args
    assert ":metadata_json" in statement
    assert rows[0]["embedding"].typecode == "f"
    assert "INSERT INTO" in statement and "DELETE" not in statement


def test_grok_uses_generic_chat_messages_and_parses_first_text_choice(settings):
    client = Mock()
    client.chat.return_value.data.chat_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=[
                        SimpleNamespace(
                            text='{"status":"answered","claims":[],"limitations":[]}'
                        )
                    ]
                )
            )
        ],
        usage=None,
    )

    result = generate_grounded_answer(client, settings, "What is the v2 endpoint?", [])

    assert result["status"] == "answered"
    request = client.chat.call_args.args[0].chat_request
    assert request.api_format == "GENERIC"
    assert len(request.messages) == 2
    assert request.messages[0].role == "SYSTEM"
    assert request.messages[1].role == "USER"


def test_grok_response_without_text_is_rejected(settings):
    client = Mock()
    client.chat.return_value.data.chat_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=[]))], usage=None
    )
    with pytest.raises(ValueError, match="no text"):
        generate_grounded_answer(client, settings, "What is the v2 endpoint?", [])
