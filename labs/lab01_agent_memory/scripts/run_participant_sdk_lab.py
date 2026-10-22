"""Run the Lab 1 participant exercise against Oracle AI Agent Memory in ADB."""

from __future__ import annotations

import argparse
import base64
import configparser
import json
import os
from collections.abc import Sequence
from getpass import getpass
from pathlib import Path
from typing import Any

import oci
import oracledb
from lab01_agent_memory.inference import (
    InferenceSettings,
    OciCohereInferenceClient,
    run_token_comparison,
)
from lab01_agent_memory.participant_lab import load_bundle
from lab01_agent_memory.sdk_exercise import (
    AgentMemoryAdapter,
    build_team_scopes,
    run_memory_exercise,
    run_sdk_exercise,
)
from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
from oracleagentmemory.core.dbsearch import SearchStrategy


def required_environment(name: str) -> str:
    """Read one required non-secret connection setting."""

    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class OracleSdkAdapter(AgentMemoryAdapter):
    """Adapt the verified Oracle SDK calls to the workshop exercise contract."""

    def __init__(self, memory: OracleAgentMemory) -> None:
        self._memory = memory

    def list_memories(self, *, user_id: str, limit: int) -> Sequence[Any]:
        return self._memory.list_memories(user_id=user_id, limit=limit)

    def add_memory(
        self,
        content: str,
        *,
        memory_type: str,
        user_id: str,
        agent_id: str,
        metadata: dict[str, str],
    ) -> Any:
        return self._memory.add_memory(
            content,
            memory_type=memory_type,
            user_id=user_id,
            agent_id=agent_id,
            metadata=metadata,
        )

    def search(
        self, query: str, *, user_id: str, record_types: list[str]
    ) -> Sequence[Any]:
        # Passing the concrete user ID asks the Oracle SDK for that exact
        # participant/team scope. It keeps the scope visible in the exercise
        # and avoids introducing a second, implicit agent/thread filter.
        return self._memory.search(
            query,
            user_id=user_id,
            exact_user_match=True,
            record_types=record_types,
            max_results=10,
        )


def create_runtime_memory() -> tuple[OracleSdkAdapter, Any]:
    """Open a TLS/mTLS pool as the participant application database user."""

    wallet_dir = required_environment("LAB01_WALLET_DIR")
    schema_owner = required_environment("LAB01_MEMORY_SCHEMA_OWNER")
    memory_store_id = required_environment("LAB01_MEMORY_STORE_ID")
    if schema_owner.casefold() == memory_store_id.casefold():
        raise RuntimeError(
            "LAB01_MEMORY_SCHEMA_OWNER must be the memory owner schema, not the memory store "
            "ID. Check the private participant session file."
        )
    password = getpass("Application database password: ")
    wallet_password = getpass("Wallet password: ")
    pool = oracledb.create_pool(
        user=required_environment("LAB01_DB_USER"),
        password=password,
        dsn=required_environment("LAB01_DB_DSN"),
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=wallet_password,
        min=1,
        max=1,
        increment=1,
    )
    memory = OracleAgentMemory(
        connection=pool,
        schema_policy=SchemaPolicy.REQUIRE_EXISTING,
        schema_owner=schema_owner,
        memory_store_id=memory_store_id,
        search_strategy=SearchStrategy.KEYWORD,
        memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
    )
    return OracleSdkAdapter(memory), pool


def create_inference_client() -> OciCohereInferenceClient:
    """Create the native OCI Inference client from the participant's OCI profile."""

    config_file = os.getenv("OCI_CONFIG_FILE")
    profile = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    if not config_file:
        config = oci.config.from_file(profile_name=profile)
        client = oci.generative_ai_inference.GenerativeAiInferenceClient(config)
        return OciCohereInferenceClient(client)

    try:
        config = oci.config.from_file(file_location=config_file, profile_name=profile)
    except oci.exceptions.InvalidConfig:
        config = load_session_token_config(config_file, profile)

    if "security_token_file" not in config:
        client = oci.generative_ai_inference.GenerativeAiInferenceClient(config)
        return OciCohereInferenceClient(client)

    token = Path(config["security_token_file"]).read_text(encoding="utf-8").strip()
    private_key = oci.signer.load_private_key_from_file(config["key_file"])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    return OciCohereInferenceClient(
        oci.generative_ai_inference.GenerativeAiInferenceClient(config, signer=signer)
    )


def load_session_token_config(config_file: str, profile: str) -> dict[str, str]:
    """Load a CLI session profile whose token already carries the user identity.

    OCI CLI can create a valid security-token profile without a ``user`` entry.
    The Python SDK requires that entry during local config validation, so this
    function derives it locally from the signed token's subject claim. Nothing
    is persisted or printed.
    """

    parser = configparser.ConfigParser()
    read_files = parser.read(config_file, encoding="utf-8")
    if not read_files or profile not in parser:
        raise RuntimeError(f"OCI profile '{profile}' was not found in the configured session file.")
    config = {key: value for key, value in parser[profile].items()}
    token_file = config.get("security_token_file")
    if not token_file:
        raise RuntimeError("OCI session profile is missing security_token_file.")
    token_parts = Path(token_file).read_text(encoding="utf-8").strip().split(".")
    if len(token_parts) != 3:
        raise RuntimeError("OCI session token is not a valid JWT.")
    payload = token_parts[1] + "=" * (-len(token_parts[1]) % 4)
    subject = json.loads(base64.urlsafe_b64decode(payload))["sub"]
    if not isinstance(subject, str) or not subject.startswith("ocid1.user."):
        raise RuntimeError("OCI session token does not contain a valid user subject.")
    config["user"] = subject
    return config


def inference_settings() -> InferenceSettings:
    """Load the approved, non-secret Lab 1 inference configuration."""

    return InferenceSettings(
        compartment_id=required_environment("OCI_COMPARTMENT_ID"),
        model_id=required_environment("LAB01_CHAT_MODEL_ID"),
        max_output_tokens=int(os.getenv("LAB01_MAX_OUTPUT_TOKENS", "120")),
    )


def print_step(number: int, label: str, message: str) -> None:
    """Print a concise, participant-facing marker for the real exercise."""

    print(f"LAB01_STEP {number}/4 {label}: {message}")


def run_preflight(*, team_code: str, participant_code: str) -> None:
    """Validate local database and inference-client setup without model inference."""

    print("LAB01_PREFLIGHT_START")
    memory, pool = create_runtime_memory()
    try:
        scopes = build_team_scopes(team_code, participant_code)
        memory.list_memories(user_id=scopes.individual, limit=1)
    finally:
        pool.close()
    create_inference_client()
    print("LAB01_PREFLIGHT_DATABASE_ACCESS True")
    print("LAB01_PREFLIGHT_MEMORY_STORE_ACCESS True")
    print("LAB01_PREFLIGHT_INFERENCE_CLIENT_READY True")
    print("LAB01_PREFLIGHT_COMPLETE")


def parse_args() -> argparse.Namespace:
    """Parse the non-secret exercise inputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path, help="Synthetic team bundle JSON")
    parser.add_argument("--team-code", required=True, help="Assigned team code, for example T01")
    parser.add_argument(
        "--participant-code", required=True, help="Assigned participant code, for example P01"
    )
    parser.add_argument(
        "--publish-to-team-scope",
        action="store_true",
        help="Also publish the synthetic procedures to the team's shared scope",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        help="Safe JSON evidence path; do not use a credentials directory",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Validate database and local OCI client setup without model inference",
    )
    parser.add_argument(
        "--memory-exercise",
        choices=("payment-idempotency", "contract-compatibility"),
        help=(
            "Persist and retrieve one selected synthetic procedure through ADB without making "
            "any OCI Generative AI inference request"
        ),
    )
    parser.add_argument(
        "--confirm-live-inference",
        action="store_true",
        help=(
            "Required acknowledgement before two on-demand OCI Generative AI inference calls "
            "are made"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run one participant's direct SDK exercise and write safe evidence."""

    args = parse_args()
    if args.preflight and args.memory_exercise:
        raise RuntimeError("Choose either --preflight or --memory-exercise, not both.")
    if args.preflight:
        run_preflight(team_code=args.team_code, participant_code=args.participant_code)
        return
    if args.memory_exercise:
        if args.confirm_live_inference:
            raise RuntimeError("The memory exercise must not acknowledge or make live inference.")
        if args.output_path is None:
            raise RuntimeError("The memory exercise requires --output-path.")
        bundle = load_bundle(args.bundle)
        print_step(
            1,
            "PERSIST",
            "writing one selected synthetic procedural decision to Autonomous Database",
        )
        memory, pool = create_runtime_memory()
        try:
            result = run_memory_exercise(
                memory,
                bundle,
                team_code=args.team_code,
                participant_code=args.participant_code,
                procedure_id=args.memory_exercise,
            )
        finally:
            pool.close()
        print_step(2, "RETRIEVE", "recovering the selected decision with keyword search")
        print_step(3, "ISOLATE", "confirming the control scope is not visible to this participant")
        print("LAB01_ISOLATION_RESULT", result.evidence["isolation_passed"])
        print("LAB01_STEP 4/4 NO_INFERENCE: no OCI Generative AI request was made")
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(json.dumps(result.evidence, indent=2) + "\n", encoding="utf-8")
        execution = result.evidence["sdk_execution"]
        print("LAB01_MEMORY_EXERCISE_READY")
        print("SELECTED_PROCEDURE", result.evidence["selected_procedure_id"])
        print("RETRIEVAL_QUERY", result.evidence["algorithm"]["query"])
        print("RETRIEVED_PROCEDURES", ",".join(result.evidence["retrieved_procedure_ids"]))
        print("PERSISTENCE_CONFIRMED", execution["persistence_confirmed"])
        print("ISOLATION_PASS", result.evidence["isolation_passed"])
        print("NO_OCI_INFERENCE True")
        print("EVIDENCE_PATH", args.output_path)
        return
    if not args.confirm_live_inference:
        raise RuntimeError(
            "Live token evidence requires --confirm-live-inference. This command makes two "
            "on-demand OCI Generative AI calls using synthetic workshop data."
        )
    if args.output_path is None:
        raise RuntimeError("Live token evidence requires --output-path.")
    bundle = load_bundle(args.bundle)
    print_step(1, "PERSIST", "writing synthetic procedural decisions to Autonomous Database")
    memory, pool = create_runtime_memory()
    try:
        result = run_sdk_exercise(
            memory,
            bundle,
            team_code=args.team_code,
            participant_code=args.participant_code,
            publish_to_team_scope=args.publish_to_team_scope,
        )
    finally:
        pool.close()

    print_step(2, "RETRIEVE", "recovering only the decision relevant to the query")
    retrieved_ids = set(result.evidence["retrieved_procedure_ids"])
    retrieved_decisions = [
        (procedure.identifier, procedure.content)
        for procedure in bundle.procedures
        if procedure.identifier in retrieved_ids
    ]
    print_step(3, "ISOLATE", "confirming the control scope is not visible to this participant")
    print("LAB01_ISOLATION_RESULT", result.evidence["isolation_passed"])
    print_step(4, "COMPARE", "making exactly two OCI Generative AI calls with synthetic data")
    inference = run_token_comparison(
        create_inference_client(),
        inference_settings(),
        question=bundle.primary_query,
        baseline_decisions=[
            (procedure.identifier, procedure.content) for procedure in bundle.procedures
        ],
        retrieved_decisions=retrieved_decisions,
        required_terms=bundle.required_response_terms,
    )
    result.evidence["evidence_type"] = "oci_sdk_inference_validation"
    result.evidence["inference"] = inference

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(result.evidence, indent=2) + "\n", encoding="utf-8")
    execution = result.evidence["sdk_execution"]
    print("LAB01_OCI_SDK_READY")
    print("SCHEMA_POLICY", execution["schema_policy"])
    print("SEARCH_STRATEGY", execution["search_strategy"])
    print("RETRIEVAL_QUERY", result.evidence["algorithm"]["query"])
    print("RETRIEVED_PROCEDURES", ",".join(result.evidence["retrieved_procedure_ids"]) or "none")
    print("PERSISTED_PROCEDURES", ",".join(result.evidence["persisted_procedure_ids"]) or "none")
    print("INDIVIDUAL_CREATED", execution["individual_created"])
    print("INDIVIDUAL_EXISTING", execution["individual_existing"])
    print("PERSISTENCE_CONFIRMED", execution["persistence_confirmed"])
    print("ISOLATION_PASS", result.evidence["isolation_passed"])
    print("BASELINE_PROMPT_TOKENS", inference["baseline"]["prompt_tokens"])
    print("MEMORY_PROMPT_TOKENS", inference["memory_optimized"]["prompt_tokens"])
    print("INPUT_TOKEN_REDUCTION", inference["input_token_reduction"])
    print("TOKEN_QUALITY_PASS", inference["both_quality_checks_passed"])
    print("EVIDENCE_PATH", args.output_path)


if __name__ == "__main__":
    main()
