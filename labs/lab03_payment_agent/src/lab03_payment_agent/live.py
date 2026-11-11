"""Real ADB/OCI adapters. Constructors connect only after explicit UI/CLI action."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from lab02_contract_rag.models import RetrievedEvidence
from lab02_contract_rag.private_session import load_participant_session

from .domain import CORPUS, Memory, Request, chunk
from .oci_profile import profile_user
from .response_format import parse_final_response


@dataclass(frozen=True)
class Settings:
    participant: str
    db_user: str
    memory_owner: str
    wallet_dir: str
    dsn: str
    region: str
    compartment: str
    embedding_model: str
    chat_model: str
    threshold: float
    expected_tenancy: str
    expected_user: str
    profile: str = "DEFAULT"
    chat_api_format: str = "COHERE"

    @classmethod
    def load(cls, path: Path, *, require_calibration: bool = True) -> Settings:
        from dotenv import dotenv_values

        load_participant_session(path)
        values = dotenv_values(path)

        def required(key):
            value = values.get(key, "")
            if not value or value.startswith("<"):
                raise ValueError(f"Configure {key}")
            return value

        p = required("LAB03_PARTICIPANT_ID").lower()
        if not re.fullmatch(r"p(?:00[1-9]|01[0-5])", p):
            raise ValueError("Participant must be p001 through p015")
        user, owner = f"WS3_{p.upper()}", f"WS3M_{p.upper()}"
        threshold = float(required("LAB03_MAX_COSINE_DISTANCE")) if require_calibration else 1.0
        if not math.isfinite(threshold) or not 0 < threshold < 2:
            raise ValueError("A pilot-calibrated cosine threshold is required")
        api_format = values.get("OCI_CHAT_API_FORMAT", "COHERE")
        if api_format not in {"COHERE", "GENERIC"}:
            raise ValueError("OCI_CHAT_API_FORMAT must be COHERE or GENERIC")
        return cls(
            p,
            user,
            owner,
            required("LAB03_WALLET_DIR"),
            required("LAB03_DB_DSN"),
            required("OCI_REGION"),
            required("OCI_PROJECT_COMPARTMENT_OCID"),
            required("OCI_EMBEDDING_MODEL_ID"),
            required("OCI_CHAT_MODEL_ID"),
            threshold,
            required("OCI_EXPECTED_TENANCY_OCID"),
            required("OCI_EXPECTED_USER_OCID"),
            required("OCI_CONFIG_PROFILE"),
            api_format,
        )


def read_lob(value):
    return value.read() if hasattr(value, "read") else value


class LiveBackend:
    def __init__(self, settings: Settings, password: str, wallet_password: str):
        import oracledb
        from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
        from oracleagentmemory.core.dbsearch import SearchStrategy

        self.settings = settings
        self.metrics = {}
        self.pool = oracledb.create_pool(
            user=settings.db_user,
            password=password,
            dsn=settings.dsn,
            config_dir=settings.wallet_dir,
            wallet_location=settings.wallet_dir,
            wallet_password=wallet_password,
            min=1,
            max=1,
            increment=1,
        )
        self.connection = self.pool.acquire()
        self.connection.call_timeout = 120000
        with self.connection.cursor() as cursor:
            cursor.execute("select sys_context('USERENV','SESSION_USER') from dual")
            self.identity = cursor.fetchone()[0]
        if self.identity != settings.db_user:
            self.close()
            raise ValueError("Authenticated schema differs from assigned participant")
        try:
            self.memory = OracleAgentMemory(
                connection=self.connection,
                schema_policy=SchemaPolicy.REQUIRE_EXISTING,
                schema_owner=settings.memory_owner,
                memory_store_id="WS3MEM",
                search_strategy=SearchStrategy.KEYWORD,
                memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
            )
        except Exception:
            self.close()
            raise

    def close(self):
        from contextlib import suppress

        with suppress(Exception):
            self.connection.close()
        with suppress(Exception):
            self.pool.close(force=True)

    def readiness(self, *, reviewed_stopped_runs: frozenset[str] = frozenset()) -> dict:
        with self.connection.cursor() as c:
            c.execute("select TEAM_EXEC_ID from USER_AI_AGENT_TEAM_HISTORY where state='RUNNING'")
            if any(str(r[0]) not in reviewed_stopped_runs for r in c.fetchall()):
                raise ValueError(
                    "A native team run is still RUNNING; inspect server state before retry"
                )
            for table in ("WS3_PAYMENTS", "WS3_REQUESTS", "WS3_EVENTS", "WS3_CHUNKS", "WS3_WRITES"):
                c.execute(f"select count(*) from {table}")
                c.fetchone()
            c.execute("select count(*) from WS3_ACTIVE")
            if c.fetchone()[0]:
                raise ValueError(
                    "A previous investigation is active; verify server execution before recovery"
                )
            c.execute(
                "select count(*) from user_errors where name in ('GET_PAYMENT','GET_PAYMENT_EVENTS','FIND_RELATED_REQUESTS','WS3_TRACE')"
            )
            if c.fetchone()[0]:
                raise ValueError("Tool compilation errors")
            c.execute("select count(*) from user_ai_agent_teams where agent_team_name='WS3_TEAM'")
            if not c.fetchone()[0]:
                raise ValueError("Agent team missing")
        return {
            "identity_verified": True,
            "schema_ready": True,
            "mode": "live",
            "paid_inference_executed": False,
        }

    def embed(self, text: str, *, input_type: str = "SEARCH_QUERY") -> list[float]:
        from .recovery import ensure_paid_execution_allowed

        ensure_paid_execution_allowed(self.settings)
        import oci

        config = oci.config.from_file(profile_name=self.settings.profile)
        if (
            config.get("tenancy") != self.settings.expected_tenancy
            or profile_user(config) != self.settings.expected_user
        ):
            raise ValueError("OCI profile does not match the assigned tenant and participant")
        config["region"] = self.settings.region
        # Security-token profiles must use their token signer, never silently API-key auth.
        signer = None
        if config.get("security_token_file"):
            signer = oci.auth.signers.SecurityTokenSigner(
                Path(config["security_token_file"]).read_text().strip(),
                oci.signer.load_private_key_from_file(
                    config["key_file"], config.get("pass_phrase")
                ),
            )
        client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config,
            **({"signer": signer} if signer else {}),
            timeout=(10, 60),
            retry_strategy=oci.retry.NoneRetryStrategy(),
        )
        details = oci.generative_ai_inference.models.EmbedTextDetails(
            compartment_id=self.settings.compartment,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=self.settings.embedding_model
            ),
            inputs=[text],
            input_type=input_type,
            truncate="NONE",
        )
        vector = client.embed_text(details).data.embeddings[0]
        self.metrics["embedding_calls"] = self.metrics.get("embedding_calls", 0) + 1
        if not vector or not all(math.isfinite(x) for x in vector):
            raise ValueError("Invalid embedding")
        return vector

    def memories(self, query: str) -> list[Memory]:
        records = self.memory.search(
            query,
            user_id=self.identity,
            exact_user_match=True,
            record_types=["guideline"],
            max_results=10,
        )
        result = []
        for record in records:
            matched = getattr(record, "record", record)
            metadata = getattr(matched, "metadata", {}) or {}
            result.append(
                Memory(
                    str(metadata.get("identifier", "unknown")),
                    record.content,
                    str(metadata.get("version", "unknown")),
                    str(metadata.get("source_run", "seed")),
                    metadata.get("approved") == "true",
                )
            )
        return result

    def retrieve(self, request: Request) -> list[RetrievedEvidence]:
        from .recovery import claim_recovery_investigation

        claim_recovery_investigation(self.settings)
        vector = json.dumps(self.embed("payment idempotency " + request.question))
        with self.connection.cursor() as c:
            c.execute(
                """select chunk_id, contract_version, content, content_hash,
                       vector_distance(embedding, to_vector(:v), COSINE) distance
                       from WS3_CHUNKS where corpus_id=:corpus and api_name='payments'
                       and contract_version=:version and embedding_model=:model
                       and embedding_dimension=:dimension
                       order by distance fetch first 3 rows only""",
                v=vector,
                corpus=CORPUS,
                version=request.version,
                model=self.settings.embedding_model,
                dimension=len(json.loads(vector)),
            )
            rows = c.fetchall()
        self.metrics["rag_candidate_count"] = len(rows)
        self.metrics["rag_distance_threshold"] = self.settings.threshold
        self.metrics["rag_best_distance"] = min((row[4] for row in rows), default=None)
        result = []
        manifest_path = Path(__file__).resolve().parents[2] / "data" / "contracts.json"
        approved = {c["id"]: c for c in json.loads(manifest_path.read_text())}
        for identifier, version, content, content_hash, distance in rows:
            if distance <= self.settings.threshold:
                item = chunk(identifier, version, read_lob(content))
                canonical = approved.get(identifier)
                if (
                    item.content_hash != content_hash
                    or not canonical
                    or canonical["text"] != item.content
                    or canonical["version"] != version
                ):
                    raise ValueError("Stored evidence changed")
                result.append(RetrievedEvidence(item, distance, "vector", "cosine_distance"))
        self.metrics["rag_accepted_count"] = len(result)
        return result

    def run(self, request: Request, context: dict, run_id: str) -> tuple[dict, list[dict]]:
        import sys
        from contextlib import suppress

        import oracledb

        from .recovery import ensure_paid_execution_allowed, reviewed_stopped_runs

        ensure_paid_execution_allowed(self.settings)
        self.readiness(reviewed_stopped_runs=reviewed_stopped_runs(self.settings))
        self.last_observations = []
        self.metrics["select_ai_runs"] = self.metrics.get("select_ai_runs", 0) + 1
        self.metrics["provider_inference_calls"] = None

        with self.connection.cursor() as c:
            # A committed singleton prevents concurrent runs across local processes.
            c.execute(
                "insert into WS3_ACTIVE(slot,run_id,payment_id) values(1,:r,:p)",
                r=run_id,
                p=request.payment_id,
            )
            self.connection.commit()
        try:
            prompt = json.dumps(
                {"request": request.__dict__, "context": context, "run_id": run_id},
                ensure_ascii=False,
            )
            with self.connection.cursor() as c:
                conversation = c.callfunc("DBMS_CLOUD_AI.CREATE_CONVERSATION", str)
                output = c.var(oracledb.DB_TYPE_CLOB)
                previous_timeout = self.connection.call_timeout
                self.metrics["native_call_timeout_ms"] = 300000
                self.metrics["native_call_completed"] = False
                try:
                    self.connection.call_timeout = 300000
                    c.execute(
                        """begin :answer := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
                        team_name=>'WS3_TEAM', user_prompt=>:prompt, params=>:params); end;""",
                        answer=output,
                        prompt=prompt,
                        params=json.dumps({"conversation_id": conversation}),
                    )
                    self.metrics["native_call_completed"] = True
                finally:
                    with suppress(Exception):
                        self.connection.call_timeout = previous_timeout
                raw = read_lob(output.getvalue())
                c.execute(
                    "select tool_name,payment_id,payload from WS3_TOOL_LOG where run_id=:r order by logged_at",
                    r=run_id,
                )
                observations = [
                    {
                        "run_id": run_id,
                        "name": n,
                        "payment_id": p,
                        "result": json.loads(read_lob(v)),
                    }
                    for n, p, v in c.fetchall()
                ]
            self.metrics["native_response_characters"] = len(raw)
            try:
                parsed = parse_final_response(raw)
                self.metrics["native_response_format"] = type(parsed).__name__
            except json.JSONDecodeError:
                self.metrics["native_response_format"] = "non_json"
                raise
            return parsed, observations
        finally:
            failure_in_flight = sys.exception() is not None
            # Tool traces survive a failed/timeout model call and remain reviewable.
            with suppress(Exception), self.connection.cursor() as c:
                c.execute(
                    "select tool_name,payment_id,payload from WS3_TOOL_LOG where run_id=:r order by logged_at",
                    r=run_id,
                )
                self.last_observations = [
                    {
                        "run_id": run_id,
                        "name": n,
                        "payment_id": p,
                        "result": json.loads(read_lob(v)),
                    }
                    for n, p, v in c.fetchall()
                ]
            # If the connection was lost, readiness reports the stale lock for facilitator review.
            try:
                with self.connection.cursor() as c:
                    c.execute("delete from WS3_ACTIVE where run_id=:r", r=run_id)
                self.connection.commit()
            except Exception:
                self.metrics["active_lock_cleanup_failed"] = True
                if not failure_in_flight:
                    raise

    def put_once(self, key: str, kind: str, payload: dict) -> dict:
        encoded = json.dumps(payload, sort_keys=True)
        with self.connection.cursor() as c:
            c.execute("select payload,status from WS3_WRITES where write_key=:k", k=key)
            row = c.fetchone()
            if row:
                if read_lob(row[0]) != encoded:
                    raise ValueError("Idempotency collision")
                if row[1] == "DONE":
                    return {"write_key": key, "status": "already_saved"}
            else:
                c.execute(
                    "insert into WS3_WRITES(write_key,kind,payload,status) values(:k,:t,:p,'PENDING')",
                    k=key,
                    t=kind,
                    p=encoded,
                )
                self.connection.commit()
            # Lock serializes retries, including separate dashboard processes.
            c.execute("select status from WS3_WRITES where write_key=:k for update wait 3", k=key)
            if c.fetchone()[0] == "DONE":
                self.connection.rollback()
                return {"write_key": key, "status": "already_saved"}
            if kind == "memory":
                records = self.memory.list_memories(user_id=self.identity, limit=100)
                existing = any(
                    (getattr(r, "metadata", {}) or {}).get("write_key") == key for r in records
                )
                if not existing:
                    from uuid import UUID

                    self.memory.add_memory(
                        payload["content"],
                        memory_type="guideline",
                        memory_id=str(UUID(key[:32])),
                        user_id=self.identity,
                        agent_id="ws3-payment-agent",
                        metadata={
                            **{k: str(v) for k, v in payload.items() if k != "content"},
                            "approved": "true",
                            "write_key": key,
                            "synthetic": "true",
                        },
                    )
            c.execute("update WS3_WRITES set status='DONE' where write_key=:k", k=key)
            self.connection.commit()
        return {"write_key": key, "status": "saved"}


def write_report(result, root: Path, identity: str) -> Path:
    target = root / identity / result.run_id
    target.mkdir(parents=True, exist_ok=True)
    (target / "evidence.json").write_text(json.dumps(result.as_dict(), indent=2), encoding="utf-8")
    (target / "evidence.md").write_text(
        f"# Payment investigation\n\nMode: {result.execution_mode}\n\nStatus: {result.status}\n\n"
        f"{result.answer}\n\nReview evidence.json for tool observations and sources.\n",
        encoding="utf-8",
    )
    return target


def write_receipt(root: Path, identity: str, run_id: str, kind: str, payload: dict) -> Path:
    """Persist confirmation/recovery evidence without accepting arbitrary path components."""
    from uuid import UUID

    if not re.fullmatch(r"WS3_P(?:00[1-9]|01[0-5])", identity):
        raise ValueError("Invalid evidence identity")
    if kind not in {"case_confirmation", "memory_confirmation", "memory_recovery"}:
        raise ValueError("Unknown receipt kind")
    target = root / identity / str(UUID(run_id))
    target.mkdir(parents=True, exist_ok=True)
    file = target / (kind + ".json")
    file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return file
