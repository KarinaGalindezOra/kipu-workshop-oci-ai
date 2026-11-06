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


def resolve_compartment_id(config_file: Path | None, profile_name: str) -> str:
    config_kwargs = {"profile_name": profile_name}
    if config_file is not None:
        config_kwargs["file_location"] = str(config_file)
    config = oci.config.from_file(**config_kwargs)
    command = [
        "oci",
        "iam",
        "compartment",
        "list",
        "--compartment-id",
        config["tenancy"],
        "--profile",
        profile_name,
        "--auth",
        "security_token",
        "--all",
        "--output",
        "json",
    ]
    if config_file is not None:
        command[6:6] = ["--config-file", str(config_file)]
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
    *,
    participant: str,
    config_file: Path,
    profile_name: str,
    compartment_id: str,
    portable: bool = False,
) -> str:
    schema = participant_schema(participant)
    if portable:
        config_assignment = "$env:OCI_CONFIG_FILE = Join-Path $HOME '.oci\\config'"
        wallet_assignment = "$env:ADB_WALLET_DIR = Join-Path $HOME '.khipu\\lab02\\wallet'"
        calibration_assignment = (
            "$env:LAB02_CALIBRATION_FILE = Join-Path $HOME '.khipu\\lab02\\calibration.json'"
        )
        development_measurements_assignment = (
            "$env:LAB02_DEVELOPMENT_MEASUREMENTS_FILE = "
            "Join-Path $HOME '.khipu\\lab02\\development-measurements.json'"
        )
        report_assignment = "$env:LAB02_REPORT_ROOT = Join-Path $HOME '.khipu\\lab02\\artifacts'"
    else:
        config_assignment = f"$env:OCI_CONFIG_FILE = '{config_file}'"
        wallet_assignment = "$env:ADB_WALLET_DIR = 'C:\\KhipuPrivate\\Wallet_KWS2RAG'"
        calibration_assignment = (
            "$env:LAB02_CALIBRATION_FILE = 'C:\\KhipuPrivate\\lab02-calibration-02-es.json'"
        )
        development_measurements_assignment = (
            "$env:LAB02_DEVELOPMENT_MEASUREMENTS_FILE = "
            "'C:\\KhipuPrivate\\lab02-development-measurements.json'"
        )
        report_assignment = "$env:LAB02_REPORT_ROOT = 'C:\\KhipuPrivate\\artifacts\\lab02'"
    return f"""# Private Workshop 2 participant session for {participant}.
# Do not commit or distribute this file. Passwords are prompted at runtime.
$env:LAB02_PARTICIPANT_ID = '{participant}'
$env:ADB_USERNAME = '{schema}'
$env:OCI_REGION = 'us-chicago-1'
{config_assignment}
$env:OCI_CONFIG_PROFILE = '{profile_name}'
$env:OCI_COMPARTMENT_ID = '{compartment_id}'
$env:OCI_EMBEDDING_MODEL_ID = 'cohere.embed-v4.0'
$env:OCI_CHAT_MODEL_ID = 'xai.grok-4.7'
$env:ADB_CONNECT_STRING = 'kws2rag_tp'
{wallet_assignment}
$env:LAB02_VECTOR_DIMENSION = '1536'
$env:LAB02_CONTRACT_TABLE = 'LAB02_CONTRACT_CHUNKS'
{calibration_assignment}
{development_measurements_assignment}
{report_assignment}
$env:LAB02_TOP_K = '3'
$env:LAB02_SET_OUTPUT_DIMENSIONS = 'false'
"""


def render_dotenv_session(
    *,
    participant: str,
    profile_name: str,
    compartment_id: str,
    wallet_dir: str | Path,
    connect_alias: str,
    calibration_file: str | Path,
    development_measurements_file: str | Path,
    report_root: str | Path,
) -> str:
    """Render a cross-platform participant-local session with no passwords or tokens."""
    schema = participant_schema(participant)
    return f"""# Private Workshop 2 participant session. Keep this file outside the repository.
# This dotenv file is read by Python; do not source it and do not add passwords, tokens or keys.
LAB02_PARTICIPANT_ID={participant}
ADB_USERNAME={schema}
OCI_REGION=us-chicago-1
OCI_CONFIG_PROFILE={profile_name}
OCI_COMPARTMENT_ID={compartment_id}
OCI_EMBEDDING_MODEL_ID=cohere.embed-v4.0
OCI_CHAT_MODEL_ID=xai.grok-4.7
ADB_CONNECT_STRING={connect_alias}
ADB_WALLET_DIR={wallet_dir}
LAB02_VECTOR_DIMENSION=1536
LAB02_CONTRACT_TABLE=LAB02_CONTRACT_CHUNKS
LAB02_CALIBRATION_FILE={calibration_file}
LAB02_DEVELOPMENT_MEASUREMENTS_FILE={development_measurements_file}
LAB02_REPORT_ROOT={report_root}
LAB02_TOP_K=3
LAB02_SET_OUTPUT_DIMENSIONS=false
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant-id", required=True, type=participant_id)
    parser.add_argument("--config-file", type=Path)
    parser.add_argument("--profile-name", required=True)
    parser.add_argument(
        "--bootstrap-profile",
        help="Approved profile used only to resolve workshop metadata when preparing another participant's file",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--format", choices=("powershell", "dotenv"), default="dotenv")
    parser.add_argument("--wallet-dir", type=Path)
    parser.add_argument("--connect-alias")
    parser.add_argument("--calibration-file", type=Path)
    parser.add_argument("--development-measurements-file", type=Path)
    parser.add_argument("--report-root", type=Path)
    parser.add_argument(
        "--portable",
        action="store_true",
        help="Use the participant-local ${HOME}/.khipu/lab02 convention for dotenv paths",
    )
    parser.add_argument("--allow-repair-incomplete-file", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        current = args.output.read_text(encoding="utf-8")
        incomplete = "OCI_COMPARTMENT_ID = ''" in current or "OCI_COMPARTMENT_ID=" in current
        if not args.allow_repair_incomplete_file or not incomplete:
            raise SystemExit("Session file exists; refusing to overwrite it")
    if args.format == "dotenv" and not args.portable:
        required = {
            "--wallet-dir": args.wallet_dir,
            "--connect-alias": args.connect_alias,
            "--calibration-file": args.calibration_file,
            "--development-measurements-file": args.development_measurements_file,
            "--report-root": args.report_root,
        }
        missing = [option for option, value in required.items() if value is None]
        if missing:
            parser.error(f"dotenv format requires {', '.join(missing)}")
    compartment_id = resolve_compartment_id(
        args.config_file, args.bootstrap_profile or args.profile_name
    )

    rendered = (
        render_session(
            participant=args.participant_id,
            config_file=args.config_file or Path("~/.oci/config"),
            profile_name=args.profile_name,
            compartment_id=compartment_id,
            portable=args.portable,
        )
        if args.format == "powershell"
        else render_dotenv_session(
            participant=args.participant_id,
            profile_name=args.profile_name,
            compartment_id=compartment_id,
            wallet_dir=(
                "${HOME}/.khipu/lab02/wallet" if args.portable else args.wallet_dir
            ),
            connect_alias="kws2rag_tp" if args.portable else args.connect_alias,
            calibration_file=(
                "${HOME}/.khipu/lab02/calibration.json"
                if args.portable
                else args.calibration_file
            ),
            development_measurements_file=(
                "${HOME}/.khipu/lab02/development-measurements.json"
                if args.portable
                else args.development_measurements_file
            ),
            report_root=("${HOME}/.khipu/lab02/artifacts" if args.portable else args.report_root),
        )
    )
    args.output.write_text(rendered, encoding="utf-8")
    print("PRIVATE_SESSION_CREATED")


if __name__ == "__main__":
    main()
