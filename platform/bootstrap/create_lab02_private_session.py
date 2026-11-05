"""Create one password-free private Lab 2 session file from authenticated OCI metadata."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import oci
from lab02_contract_rag.participant import participant_id, participant_schema


def classify_cli_error(stderr: str) -> str:
    if "ConfigFileNotFound" in stderr:
        return "config_file_not_found"
    if "NotAuthenticated" in stderr or "not authenticated" in stderr.lower():
        return "not_authenticated"
    if "ProfileNotFound" in stderr:
        return "profile_not_found"
    return "unclassified"


def resolve_compartment_id(config_file: Path, profile_name: str) -> str:
    config = oci.config.from_file(file_location=str(config_file), profile_name=profile_name)
    command = [
        "oci",
        "iam",
        "compartment",
        "list",
        "--compartment-id",
        config["tenancy"],
        "--config-file",
        str(config_file),
        "--profile",
        profile_name,
        "--auth",
        "security_token",
        "--all",
        "--output",
        "json",
    ]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        compartments = json.loads(completed.stdout)["data"]
    except subprocess.CalledProcessError as error:
        classification = classify_cli_error(error.stderr)
        raise SystemExit(
            f"OCI compartment lookup CLI exit code {error.returncode} ({classification})"
        ) from None
    except json.JSONDecodeError:
        raise SystemExit("OCI compartment lookup returned invalid JSON") from None
    except KeyError:
        raise SystemExit("OCI compartment lookup returned no data") from None
    matches = [
        item
        for item in compartments
        if item["name"] == "cmp-khipu-workshop2-trial" and item["lifecycle-state"] == "ACTIVE"
    ]
    if len(matches) != 1:
        raise SystemExit("Workshop compartment is not uniquely available")
    return str(matches[0]["id"])


def render_session(
    *, participant: str, config_file: Path, profile_name: str, compartment_id: str
) -> str:
    schema = participant_schema(participant)
    return f"""# Private facilitator rehearsal session for Workshop 2 participant {participant}.
# Do not commit or distribute this file. Passwords are prompted at runtime.
$env:LAB02_PARTICIPANT_ID = '{participant}'
$env:ADB_USERNAME = '{schema}'
$env:OCI_REGION = 'us-chicago-1'
$env:OCI_CONFIG_FILE = '{config_file}'
$env:OCI_CONFIG_PROFILE = '{profile_name}'
$env:OCI_COMPARTMENT_ID = '{compartment_id}'
$env:OCI_EMBEDDING_MODEL_ID = 'cohere.embed-v4.0'
$env:OCI_CHAT_MODEL_ID = 'xai.grok-4.7'
$env:ADB_CONNECT_STRING = 'kws2rag_tp'
$env:ADB_WALLET_DIR = 'C:\\KhipuPrivate\\Wallet_KWS2RAG'
$env:LAB02_VECTOR_DIMENSION = '1536'
$env:LAB02_CONTRACT_TABLE = 'LAB02_CONTRACT_CHUNKS'
$env:LAB02_CALIBRATION_FILE = 'C:\\KhipuPrivate\\lab02-calibration-02-es.json'
$env:LAB02_REPORT_ROOT = 'C:\\KhipuPrivate\\artifacts\\lab02'
$env:LAB02_TOP_K = '3'
$env:LAB02_SET_OUTPUT_DIMENSIONS = 'false'
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant-id", required=True, type=participant_id)
    parser.add_argument("--config-file", type=Path, required=True)
    parser.add_argument("--profile-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-repair-incomplete-file", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        current = args.output.read_text(encoding="utf-8")
        if not args.allow_repair_incomplete_file or "OCI_COMPARTMENT_ID = ''" not in current:
            raise SystemExit("Session file exists; refusing to overwrite it")
    compartment_id = resolve_compartment_id(args.config_file, args.profile_name)

    args.output.write_text(
        render_session(
            participant=args.participant_id,
            config_file=args.config_file,
            profile_name=args.profile_name,
            compartment_id=compartment_id,
        ),
        encoding="utf-8",
    )
    print("PRIVATE_SESSION_CREATED")


if __name__ == "__main__":
    main()
