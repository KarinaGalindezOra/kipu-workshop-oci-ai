"""The shared real OCI execution path for the participant CLI and dashboard.

No lexical retriever, fixture factory or model substitute is imported here.
Organizational approval is required in addition to per-request acknowledgements.
"""

import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from . import live_validation as live
from .agent import resolve_request, run_agent
from .corpus import load_corpus
from .evidence import requested_facets, section_facet
from .participant import artifact_directory, participant_id
from .reporting import write_result


def safe_failure_code(exc: Exception) -> str:
    """Return a non-secret category suitable for a participant evidence report."""
    status = getattr(exc, "status", None)
    if isinstance(status, int) and 100 <= status <= 599:
        return f"HTTP_{status}"
    return type(exc).__name__


def failure_kind(exc: Exception) -> str:
    """Classify a service failure without copying a provider error body."""
    status = getattr(exc, "status", None)
    if status == 429:
        return "rate_limited"
    if status in {401, 403}:
        return "authentication_or_authorization"
    return "service_error"


def control_result(question: str, assigned_id: str, version=None, compare=False):
    """Clarification and routing are application decisions, never model responses."""
    _, status, _ = resolve_request(question, version, compare)
    import re

    if status or re.search(r"transactions?|operational|metrics?|latency|records?", question, re.I):
        result = run_agent(question, lambda v, q: [], version=version, compare=compare)
        result.update(
            participant_id=participant_id(assigned_id),
            mode="oci",
            execution_origin="application_control",
            cloud_executed=False,
            service_trace=[],
            fixture_simulated=False,
        )
        result["request_controls"] = {"version": version, "compare": compare}
        return result
    return None


def execute_live(
    settings: live.LiveLab02Settings,
    question: str,
    *,
    confirm_inference: bool,
    confirm_load: bool = False,
    ingest_only: bool = False,
    version=None,
    compare=False,
    database_password: str | None = None,
    wallet_password: str | None = None,
    output_root: Path | None = None,
    connection_factory: Callable[[], object] | None = None,
) -> dict:
    assigned_id = participant_id(settings.participant_id)
    if settings.db_user.upper() != live.participant_schema(assigned_id):
        raise ValueError("Participant identity does not match the database user")
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError("Question must contain 1-4000 characters")
    result = None if ingest_only else control_result(question, assigned_id, version, compare)
    if result is not None:
        if output_root:
            write_result(artifact_directory(output_root, assigned_id, result["run_id"]), result)
        return result
    if not confirm_inference:
        raise ValueError("Explicit inference acknowledgement is required before OCI access")
    if not ingest_only and not 0 < settings.max_cosine_distance < 2:
        raise ValueError("Query execution requires frozen calibration")
    stage = "preflight"
    telemetry = {
        "document_embedding_calls": 0,
        "query_embedding_calls": 0,
        "chat_calls": 0,
        "tokens": None,
        "inserted_chunks": 0,
    }
    trace = []
    cache = {}
    started = time.perf_counter()

    def operation(name, callback):
        begin = time.perf_counter()
        item = {
            "service_operation": name,
            "status": "attempted",
            "started_at": datetime.now(UTC).isoformat(),
        }
        trace.append(item)
        try:
            value = callback()
            item["status"] = "succeeded"
            return value
        except Exception as exc:
            item["status"] = "failed"
            item["failure_kind"] = failure_kind(exc)
            item["safe_error_code"] = safe_failure_code(exc)
            raise
        finally:
            item["duration_ms"] = round((time.perf_counter() - begin) * 1000, 3)

    try:
        chunks = operation("local_corpus_load", load_corpus)
        client = operation("oci_client_create", lambda: live.create_inference_client(settings))
        stage = "database_connect"
        if connection_factory is None:
            connection = operation(
                "adb_connect",
                lambda: live.create_database_connection(
                    settings,
                    database_password=database_password,
                    wallet_password=wallet_password,
                ),
            )
        else:
            connection = operation("adb_connection_acquire", connection_factory)
        with connection as connection:
            with connection.cursor() as cursor:
                trace.append({"service_operation": "adb_session_identity", "status": "succeeded"})
                stage = "corpus_readiness"
                existing = operation(
                    "adb_corpus_read",
                    lambda: live.existing_chunk_hashes(cursor, settings.table_name),
                )
                missing = live.chunks_to_insert(chunks, existing, settings)
                if missing and not confirm_load:
                    raise ValueError(
                        "Corpus is incomplete; explicit synthetic-load approval is required"
                    )
                if missing:
                    stage = "document_embeddings"
                    telemetry["document_embedding_calls"] += 1
                    vectors = operation(
                        "oci_document_embeddings",
                        lambda: live.embed_texts(
                            client, settings, [c.content for c in missing], "SEARCH_DOCUMENT"
                        ),
                    )
                    stage = "ingest"
                    operation(
                        "adb_insert",
                        lambda: live.insert_chunks(
                            cursor, settings.table_name, missing, vectors, settings
                        ),
                    )
                    operation("adb_commit", connection.commit)
                    telemetry["inserted_chunks"] = len(missing)
                if ingest_only:
                    result = run_agent("Which contract version?", lambda v, q: [])
                    result.update(
                        status="ingested",
                        question="Preparar el corpus sintético",
                        limitations=["Durante la ingesta no se solicitó una respuesta del modelo."],
                    )
                else:

                    def retriever(target, query):
                        if query not in cache:
                            telemetry["query_embedding_calls"] += 1
                            cache[query] = operation(
                                "oci_query_embedding",
                                lambda: live.embed_texts(client, settings, [query], "SEARCH_QUERY")[
                                    0
                                ],
                            )
                        items = operation(
                            "adb_vector_search",
                            lambda: live.retrieve_evidence(
                                cursor,
                                settings.table_name,
                                target,
                                cache[query],
                                settings.top_k,
                                settings,
                            ),
                        )
                        facets, _ = requested_facets(query)
                        covered = {
                            section_facet(item.chunk.section)
                            for item in items
                            if section_facet(item.chunk.section) is not None
                        }
                        missing_facets = facets - covered
                        if missing_facets:
                            items.extend(
                                operation(
                                    "adb_section_coverage",
                                    lambda: live.retrieve_section_coverage(
                                        cursor,
                                        settings.table_name,
                                        target,
                                        missing_facets,
                                        {item.chunk.chunk_id for item in items},
                                        settings,
                                    ),
                                )
                            )
                        return items

                    def generator(query, evidence):
                        telemetry["chat_calls"] += 1
                        payload = operation(
                            "oci_chat",
                            lambda: live.generate_grounded_answer(
                                client, settings, query, evidence
                            ),
                        )
                        telemetry["tokens"] = payload.pop("provider_usage", None)
                        return payload

                    result = run_agent(
                        question,
                        retriever,
                        version=version,
                        compare=compare,
                        generator=generator,
                        require_oci_retrieval=True,
                    )
    except Exception:
        result = run_agent("Which contract version?", lambda v, q: [])
        result.update(
            status="error",
            question=question,
            error_stage=stage,
            answer="",
            limitations=[
                "OCI execution failed. Check private setup, approvals and service health."
            ],
        )
    result.update(
        participant_id=assigned_id,
        mode="oci",
        execution_origin="oci_services",
        cloud_executed=any(t["status"] == "succeeded" for t in trace),
        service_trace=trace,
        telemetry=telemetry,
        fixture_simulated=False,
        executed_at=datetime.now(UTC).isoformat(),
    )
    result["request_controls"] = {"version": version, "compare": compare}
    result["timings_ms"]["total"] = round((time.perf_counter() - started) * 1000, 3)
    if output_root:
        write_result(artifact_directory(output_root, assigned_id, result["run_id"]), result)
    return result
