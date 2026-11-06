"""Opt-in OCI execution for the manifest-verified synthetic workshop corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from array import array
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from getpass import getpass
from pathlib import Path
from typing import Any

import oci
import oracledb

from .corpus import LAB_ROOT, load_corpus
from .demo import DEFAULT_QUESTION
from .evidence import citations, section_facet
from .models import ContractChunk, RetrievedEvidence
from .participant import (
    artifact_directory,
    participant_id,
    participant_schema,
    validate_database_session,
)
from .private_session import add_session_file_argument, load_participant_session
from .reporting import write_result

TABLE_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_$#]{0,29}$")


@dataclass(frozen=True)
class LiveLab02Settings:
    compartment_id: str
    embedding_model_id: str
    chat_model_id: str
    db_user: str
    db_dsn: str
    wallet_dir: str
    vector_dimension: int
    table_name: str
    top_k: int
    oci_config_profile: str
    oci_config_file: str | None
    region: str = "us-chicago-1"
    max_cosine_distance: float = 0.0
    set_output_dimensions: bool = False
    participant_id: str = "p001"


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value or value.startswith("<"):
        raise RuntimeError(f"Configure {name} before live execution")
    return value


def positive_integer(value: str, variable_name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{variable_name} must be an integer") from exc
    if parsed < 1:
        raise RuntimeError(f"{variable_name} must be greater than zero")
    return parsed


def validated_table_name(table_name: str) -> str:
    if not TABLE_NAME_PATTERN.fullmatch(table_name):
        raise RuntimeError("Table must be an uppercase Oracle simple identifier")
    return table_name


def settings_from_environment(*, require_calibration: bool = True) -> LiveLab02Settings:
    # Preparation placeholder; query acceptance always requires frozen calibration.
    threshold = 1.0
    if not math.isfinite(threshold) or not 0 < threshold < 2:
        raise ValueError("Calibrated cosine threshold must be between zero and two")
    top_k = positive_integer(os.getenv("LAB02_TOP_K", "3"), "LAB02_TOP_K")
    if top_k > 3:
        raise ValueError("Workshop top_k cannot exceed three")
    settings = LiveLab02Settings(
        compartment_id=required_environment("OCI_COMPARTMENT_ID"),
        embedding_model_id=required_environment("OCI_EMBEDDING_MODEL_ID"),
        chat_model_id=required_environment("OCI_CHAT_MODEL_ID"),
        db_user=required_environment("ADB_USERNAME"),
        db_dsn=required_environment("ADB_CONNECT_STRING"),
        wallet_dir=required_environment("ADB_WALLET_DIR"),
        vector_dimension=positive_integer(
            required_environment("LAB02_VECTOR_DIMENSION"), "LAB02_VECTOR_DIMENSION"
        ),
        table_name=validated_table_name(required_environment("LAB02_CONTRACT_TABLE")),
        top_k=top_k,
        oci_config_profile=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT"),
        oci_config_file=os.getenv("OCI_CONFIG_FILE"),
        region=os.getenv("OCI_REGION", "us-chicago-1"),
        max_cosine_distance=threshold,
        set_output_dimensions=os.getenv("LAB02_SET_OUTPUT_DIMENSIONS", "false").lower() == "true",
        participant_id=participant_id(required_environment("LAB02_PARTICIPANT_ID")),
    )
    if settings.db_user.upper() != participant_schema(settings.participant_id):
        raise ValueError("ADB_USERNAME must match the assigned Lab 2 participant schema")
    if not Path(settings.wallet_dir).is_dir():
        raise ValueError("Wallet directory is unavailable")
    if require_calibration:
        from dataclasses import replace

        from .calibration import validate_calibration

        threshold = validate_calibration(
            Path(required_environment("LAB02_CALIBRATION_FILE")),
            region=settings.region,
            model_id=settings.embedding_model_id,
            dimension=settings.vector_dimension,
        )
        settings = replace(settings, max_cosine_distance=threshold)
    return settings


def create_inference_client(settings: LiveLab02Settings) -> Any:
    kwargs = {"profile_name": settings.oci_config_profile}
    if settings.oci_config_file:
        kwargs["file_location"] = settings.oci_config_file
    config = oci.config.from_file(**kwargs)
    config["region"] = settings.region
    signer = None
    if config.get("security_token_file"):
        token = Path(config["security_token_file"]).expanduser().read_text().strip()
        key = oci.signer.load_private_key_from_file(config["key_file"], config.get("pass_phrase"))
        signer = oci.auth.signers.SecurityTokenSigner(token, key)
    options = {"timeout": (10, 30), "retry_strategy": oci.retry.NoneRetryStrategy()}
    if signer:
        options["signer"] = signer
    return oci.generative_ai_inference.GenerativeAiInferenceClient(config, **options)


def create_database_connection(
    settings: LiveLab02Settings,
    *,
    database_password: str | None = None,
    wallet_password: str | None = None,
) -> oracledb.Connection:
    if settings.db_user.upper() != participant_schema(settings.participant_id):
        raise ValueError("Refusing a shared or mismatched database username")
    connection = oracledb.connect(
        user=settings.db_user,
        password=database_password
        if database_password is not None
        else getpass("ADB schema password: "),
        dsn=settings.db_dsn,
        config_dir=settings.wallet_dir,
        wallet_location=settings.wallet_dir,
        wallet_password=wallet_password
        if wallet_password is not None
        else getpass("ADB wallet password: "),
    )
    connection.call_timeout = 5000
    try:
        validate_database_session(connection, settings.participant_id)
    except Exception:
        connection.close()
        raise
    return connection


def create_database_pool(
    settings: LiveLab02Settings,
    *,
    database_password: str | None = None,
    wallet_password: str | None = None,
) -> Any:
    """Create a one-connection pool for one local participant process only."""
    if settings.db_user.upper() != participant_schema(settings.participant_id):
        raise ValueError("Refusing a shared or mismatched database username")
    return oracledb.create_pool(
        user=settings.db_user,
        password=database_password
        if database_password is not None
        else getpass("ADB schema password: "),
        dsn=settings.db_dsn,
        config_dir=settings.wallet_dir,
        wallet_location=settings.wallet_dir,
        wallet_password=wallet_password
        if wallet_password is not None
        else getpass("ADB wallet password: "),
        min=0,
        max=1,
        increment=1,
        timeout=600,
        ping_interval=60,
    )


def acquire_database_connection(pool: Any, settings: LiveLab02Settings) -> oracledb.Connection:
    """Acquire and validate a participant-scoped connection from a local pool."""
    connection = pool.acquire()
    connection.call_timeout = 5000
    try:
        validate_database_session(connection, settings.participant_id)
    except Exception:
        connection.close()
        raise
    return connection


def embed_texts(
    client: Any, settings: LiveLab02Settings, inputs: list[str], input_type: str
) -> list[list[float]]:
    if input_type not in {"SEARCH_DOCUMENT", "SEARCH_QUERY"} or not inputs:
        raise ValueError("Invalid embedding input")
    kwargs = dict(
        inputs=inputs,
        input_type=input_type,
        truncate="NONE",
        compartment_id=settings.compartment_id,
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=settings.embedding_model_id
        ),
    )
    if settings.set_output_dimensions:
        kwargs["output_dimensions"] = settings.vector_dimension
    response = client.embed_text(oci.generative_ai_inference.models.EmbedTextDetails(**kwargs))
    vectors = response.data.embeddings
    if len(vectors) != len(inputs) or any(
        len(v) != settings.vector_dimension or not all(math.isfinite(x) for x in v) or not any(v)
        for v in vectors
    ):
        raise RuntimeError("Embedding count, dimension or values are invalid")
    return vectors


def embedding_fingerprint(chunk: ContractChunk, settings: LiveLab02Settings) -> tuple:
    return (
        chunk.content_hash,
        settings.embedding_model_id,
        settings.vector_dimension,
        chunk.embedding_input_hash,
    )


def existing_chunk_hashes(cursor, table_name: str) -> dict:
    cursor.execute(
        f"SELECT chunk_id, content_hash, embedding_model_id, embedding_dimension, "
        f"embedding_input_hash FROM {validated_table_name(table_name)}"
    )
    return {str(row[0]): tuple(row[1:]) for row in cursor}


def chunks_to_insert(
    chunks: list[ContractChunk], existing_hashes: dict, settings: LiveLab02Settings | None = None
) -> list[ContractChunk]:
    missing = []
    for chunk in chunks:
        current = existing_hashes.get(chunk.chunk_id)
        expected = embedding_fingerprint(chunk, settings) if settings else chunk.content_hash
        if current is None:
            missing.append(chunk)
        elif current != expected:
            raise RuntimeError("Refusing to replace existing chunk; content or embedding differs")
    return missing


def insert_chunks(
    cursor,
    table_name: str,
    chunks: list[ContractChunk],
    embeddings: list[list[float]],
    settings: LiveLab02Settings,
) -> None:
    if len(chunks) != len(embeddings):
        raise RuntimeError("Chunk and embedding counts differ")
    statement = f"""
        INSERT INTO {validated_table_name(table_name)} (
            chunk_id, corpus_id, api_name, contract_version, data_classification,
            content_hash, embedding_model_id, embedding_dimension, embedding_input_hash,
            metadata_json, embedding
        ) VALUES (:chunk_id, :corpus_id, :api_name, :contract_version, :data_classification,
                  :content_hash, :embedding_model_id, :embedding_dimension, :embedding_input_hash,
                  :metadata_json, :embedding)
    """
    rows = []
    for chunk, vector in zip(chunks, embeddings, strict=True):
        if len(vector) != settings.vector_dimension:
            raise ValueError("Vector dimension mismatch")
        metadata = asdict(chunk)
        metadata.update(
            embedding_model_id=settings.embedding_model_id,
            embedding_dimension=settings.vector_dimension,
            loaded_at=datetime.now(UTC).isoformat(),
        )
        metadata.pop("embedding")
        rows.append(
            dict(
                chunk_id=chunk.chunk_id,
                corpus_id=chunk.corpus_id,
                api_name=chunk.api_name,
                contract_version=chunk.contract_version,
                data_classification=chunk.data_classification,
                content_hash=chunk.content_hash,
                embedding_model_id=settings.embedding_model_id,
                embedding_dimension=settings.vector_dimension,
                embedding_input_hash=chunk.embedding_input_hash,
                metadata_json=json.dumps(metadata),
                embedding=array("f", vector),
            )
        )
    cursor.executemany(statement, rows)


def retrieve_evidence(
    cursor,
    table_name: str,
    contract_version: str,
    query_embedding: list[float],
    top_k: int,
    settings: LiveLab02Settings,
    corpus_id="contracts-baseline-02-es",
):
    if not 1 <= top_k <= 3 or contract_version not in {"v1", "v2"}:
        raise ValueError("Invalid retrieval scope")
    if len(query_embedding) != settings.vector_dimension or not all(
        math.isfinite(x) for x in query_embedding
    ):
        raise ValueError("Query vector does not match the embedding space")
    cursor.execute(
        f"""
        SELECT metadata_json, VECTOR_DISTANCE(embedding, :query_embedding, COSINE) AS distance
        FROM {validated_table_name(table_name)}
        WHERE contract_version = :contract_version AND corpus_id = :corpus_id
          AND api_name = :api_name AND data_classification = 'synthetic'
          AND embedding_model_id = :model_id AND embedding_dimension = :dimension
        ORDER BY VECTOR_DISTANCE(embedding, :query_embedding, COSINE), chunk_id
        FETCH EXACT FIRST {top_k} ROWS ONLY
    """,
        query_embedding=array("f", query_embedding),
        contract_version=contract_version,
        corpus_id=corpus_id,
        api_name="disbursement",
        model_id=settings.embedding_model_id,
        dimension=settings.vector_dimension,
    )
    evidence = []
    approved = {c.chunk_id: c for c in load_corpus()}
    for raw, distance in cursor:
        raw = raw.read() if hasattr(raw, "read") else raw
        chunk = ContractChunk(**json.loads(raw))
        if (
            chunk.contract_version != contract_version
            or chunk.corpus_id != corpus_id
            or chunk.api_name != "disbursement"
            or chunk.data_classification != "synthetic"
            or chunk.embedding_model_id != settings.embedding_model_id
            or chunk.embedding_dimension != settings.vector_dimension
            or chunk.embedding_input_hash != hashlib.sha256(chunk.content.encode()).hexdigest()
        ):
            raise ValueError("Stored metadata conflicts with retrieval scope")
        original = approved.get(chunk.chunk_id)
        stored = asdict(chunk)
        reference = asdict(original) if original else {}
        for field in ("embedding", "embedding_model_id", "embedding_dimension", "loaded_at"):
            stored.pop(field, None)
            reference.pop(field, None)
        if stored != reference:
            raise ValueError("Stored evidence differs from the frozen source manifest")
        if math.isfinite(distance) and distance <= settings.max_cosine_distance:
            evidence.append(RetrievedEvidence(chunk, float(distance), "vector", "cosine_distance"))
    return evidence


def retrieve_section_coverage(
    cursor,
    table_name: str,
    contract_version: str,
    facets: set[str],
    existing_chunk_ids: set[str],
    settings: LiveLab02Settings,
    corpus_id="contracts-baseline-02-es",
):
    """Retrieve only missing requested facets using strict stored metadata filters.

    This is not an approximate-search substitute: it is a bounded structural
    completion after the initial vector candidates. It is used only when a
    required facet has no vector candidate, and remains limited to the active
    corpus, API, version, classification and embedding space.
    """

    if not facets or contract_version not in {"v1", "v2"}:
        return []
    cursor.execute(
        f"""
        SELECT metadata_json
        FROM {validated_table_name(table_name)}
        WHERE contract_version = :contract_version AND corpus_id = :corpus_id
          AND api_name = :api_name AND data_classification = 'synthetic'
          AND embedding_model_id = :model_id AND embedding_dimension = :dimension
        ORDER BY chunk_id
    """,
        contract_version=contract_version,
        corpus_id=corpus_id,
        api_name="disbursement",
        model_id=settings.embedding_model_id,
        dimension=settings.vector_dimension,
    )
    approved = {c.chunk_id: c for c in load_corpus()}
    evidence = []
    for (raw,) in cursor:
        raw = raw.read() if hasattr(raw, "read") else raw
        chunk = ContractChunk(**json.loads(raw))
        if (
            chunk.contract_version != contract_version
            or chunk.corpus_id != corpus_id
            or chunk.api_name != "disbursement"
            or chunk.data_classification != "synthetic"
            or chunk.embedding_model_id != settings.embedding_model_id
            or chunk.embedding_dimension != settings.vector_dimension
            or chunk.embedding_input_hash != hashlib.sha256(chunk.content.encode()).hexdigest()
        ):
            raise ValueError("Stored metadata conflicts with retrieval scope")
        original = approved.get(chunk.chunk_id)
        stored = asdict(chunk)
        reference = asdict(original) if original else {}
        for field in ("embedding", "embedding_model_id", "embedding_dimension", "loaded_at"):
            stored.pop(field, None)
            reference.pop(field, None)
        if stored != reference:
            raise ValueError("Stored evidence differs from the frozen source manifest")
        if chunk.chunk_id not in existing_chunk_ids and section_facet(chunk.section) in facets:
            evidence.append(
                RetrievedEvidence(
                    chunk,
                    0.0,
                    "structural_section_coverage",
                    "facet_coverage",
                )
            )
    return evidence


def grounded_prompt(question: str, evidence: list[RetrievedEvidence]) -> str:
    system = (LAB_ROOT / "prompts/rag_system.txt").read_text(encoding="utf-8")
    return (
        system
        + "\nUNTRUSTED INPUT JSON:\n"
        + json.dumps({"question": question, "evidence": citations(evidence)}, ensure_ascii=False)
    )


def generate_grounded_answer(client, settings, question, evidence) -> dict:
    models = oci.generative_ai_inference.models
    request = models.GenericChatRequest(
        messages=[
            models.SystemMessage(
                content=[
                    models.TextContent(
                        text=(LAB_ROOT / "prompts/rag_system.txt").read_text(encoding="utf-8")
                    )
                ]
            ),
            models.UserMessage(
                content=[
                    models.TextContent(
                        text=json.dumps(
                            {"question": question, "evidence": citations(evidence)},
                            ensure_ascii=False,
                        )
                    )
                ]
            ),
        ],
        temperature=0,
        max_completion_tokens=1200,
    )
    details = oci.generative_ai_inference.models.ChatDetails(
        compartment_id=settings.compartment_id,
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=settings.chat_model_id
        ),
        chat_request=request,
    )
    response = client.chat(details).data.chat_response
    choices = getattr(response, "choices", None) or []
    content = getattr(getattr(choices[0], "message", None), "content", None) if choices else None
    text = "".join(
        item.text for item in (content or []) if isinstance(getattr(item, "text", None), str)
    )
    if not text:
        raise ValueError("Model returned no text content")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("Model output must be a JSON object")
    usage = getattr(response, "usage", None)
    payload["provider_usage"] = oci.util.to_dict(usage) if usage else None
    return payload


def main() -> None:
    """Execute only real OCI operations or explicitly identified application controls."""
    from .execution import control_result, execute_live

    parser = argparse.ArgumentParser(description=__doc__)
    add_session_file_argument(parser)
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--contract-version")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--ingest-only", action="store_true")
    parser.add_argument("--confirm-live-inference", action="store_true")
    parser.add_argument("--confirm-synthetic-load", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab02"))
    args = parser.parse_args()
    load_participant_session(args.session_file)
    if not args.ingest_only:
        assigned = os.getenv("LAB02_PARTICIPANT_ID")
        if assigned:
            result = control_result(args.question, assigned, args.contract_version, args.compare)
            if result:
                write_result(
                    artifact_directory(args.output_dir, assigned, result["run_id"]), result
                )
                print(f"STATUS {result['status']}; ORIGIN application_control")
                return
    if not args.confirm_live_inference:
        parser.error("Paid calls require --confirm-live-inference after budget approval")
    try:
        settings = settings_from_environment(require_calibration=not args.ingest_only)
        result = execute_live(
            settings,
            args.question,
            confirm_inference=True,
            confirm_load=args.confirm_synthetic_load,
            ingest_only=args.ingest_only,
            version=args.contract_version,
            compare=args.compare,
            output_root=args.output_dir,
        )
        print(f"STATUS {result['status']}")
        print(f"OCI_EXECUTED {result['cloud_executed']}")
        report_path = (
            args.output_dir / settings.participant_id / result["run_id"] / "lab02-evidence.json"
        )
        print(f"EVIDENCE_REPORT {report_path}")
        if result["status"] == "error":
            raise SystemExit(1)
    except Exception:
        raise SystemExit("OCI execution failed; inspect private preflight configuration") from None


if __name__ == "__main__":
    main()
