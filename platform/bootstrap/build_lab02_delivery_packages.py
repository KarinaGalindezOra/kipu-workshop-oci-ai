"""Build private Workshop 2 participant packages without printing credentials."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import oci


def resolve_compartment_id(*, profile_name: str, compartment_name: str) -> str:
    config = oci.config.from_file(profile_name=profile_name)
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
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Unable to resolve the workshop compartment (OCI CLI exit code {error.returncode})"
        ) from None
    records = json.loads(completed.stdout)["data"]
    matches = [
        record
        for record in records
        if record["name"] == compartment_name and record["lifecycle-state"] == "ACTIVE"
    ]
    if len(matches) != 1:
        raise RuntimeError("Workshop compartment is not uniquely available")
    return str(matches[0]["id"])


def render_session(*, participant_id: str, database_user: str, compartment_id: str) -> str:
    return f"""# Private Workshop 2 session. Keep this package outside the repository.
# Do not source this file. It contains no password, token, or private key.
LAB02_PARTICIPANT_ID={participant_id}
ADB_USERNAME={database_user}
OCI_REGION=us-chicago-1
OCI_CONFIG_PROFILE=KHIPU_WS2_PARTICIPANT
OCI_COMPARTMENT_ID={compartment_id}
OCI_EMBEDDING_MODEL_ID=cohere.embed-v4.0
OCI_CHAT_MODEL_ID=xai.grok-4.7
ADB_CONNECT_STRING=kws2rag_tp
ADB_WALLET_DIR=wallet
LAB02_VECTOR_DIMENSION=1536
LAB02_CONTRACT_TABLE=LAB02_CONTRACT_CHUNKS
LAB02_CALIBRATION_FILE=calibration.json
LAB02_DEVELOPMENT_MEASUREMENTS_FILE=development-measurements.json
LAB02_REPORT_ROOT=artifacts
LAB02_TOP_K=3
LAB02_SET_OUTPUT_DIMENSIONS=false
"""


def write_start_here(package_dir: Path) -> None:
    package_dir.joinpath("START_HERE.md").write_text(
        """# Workshop 2: paquete privado individual

1. Descomprime esta carpeta **fuera** del repositorio y no la subas a Git.
2. Conserva juntos `lab02-participant.env`, `wallet/`, `calibration.json` y
   `development-measurements.json`.
3. Sigue desde el Paso 3 de la guía pública:
   https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai/blob/main/labs/lab02_contract_rag/docs/participant_step_by_step.md
4. Recibirás por un canal privado separado tu contraseña de ADB y la contraseña
   del wallet. Escríbelas solo cuando la aplicación las solicite.

No envíes este paquete a otras personas ni copies su contenido a un ticket,
chat público o repositorio.
""",
        encoding="utf-8",
    )


def copy_wallet(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("*.lck"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--wallet-dir", required=True, type=Path)
    parser.add_argument("--calibration-file", required=True, type=Path)
    parser.add_argument("--development-measurements-file", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--bootstrap-profile", default="KHIPU_WS2_ADMIN")
    parser.add_argument("--compartment-name", default="cmp-khipu-workshop2-trial")
    args = parser.parse_args()

    required_paths = (
        args.handoff,
        args.wallet_dir,
        args.calibration_file,
        args.development_measurements_file,
    )
    if not all(path.exists() for path in required_paths):
        raise SystemExit("Required private delivery input is unavailable")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise SystemExit("Output directory must be new or empty")

    compartment_id = resolve_compartment_id(
        profile_name=args.bootstrap_profile,
        compartment_name=args.compartment_name,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with args.handoff.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required_columns = {"participant_id", "email", "database_user", "database_password", "wallet_password"}
    if not rows or not required_columns.issubset(rows[0]):
        raise SystemExit("Private handoff does not have the expected columns")

    with tempfile.TemporaryDirectory(prefix="lab02-delivery-") as temp_dir:
        staging_root = Path(temp_dir)
        packages_dir = args.output_dir / "participant-packages"
        packages_dir.mkdir()
        for row in rows:
            participant_id = row["participant_id"].strip().lower()
            package_dir = staging_root / participant_id
            package_dir.mkdir()
            package_dir.joinpath("lab02-participant.env").write_text(
                render_session(
                    participant_id=participant_id,
                    database_user=row["database_user"].strip(),
                    compartment_id=compartment_id,
                ),
                encoding="utf-8",
            )
            copy_wallet(args.wallet_dir, package_dir / "wallet")
            shutil.copy2(args.calibration_file, package_dir / "calibration.json")
            shutil.copy2(
                args.development_measurements_file,
                package_dir / "development-measurements.json",
            )
            write_start_here(package_dir)
            archive = shutil.make_archive(
                str(packages_dir / f"Workshop2-{participant_id}-private-package"),
                "zip",
                root_dir=package_dir,
            )
            if not Path(archive).is_file():
                raise RuntimeError("A private package could not be created")
        # This handoff is for Sofía only and is transferred through the approved private channel.
        sofia_handoff = staging_root / "Workshop2-Sofia-private-handoff"
        sofia_handoff.mkdir()
        shutil.copy2(args.handoff, sofia_handoff / "sofia-private-distribution.csv")
        for package in packages_dir.glob("*.zip"):
            shutil.copy2(package, sofia_handoff / package.name)
        private_handoff = shutil.make_archive(
            str(args.output_dir / "Workshop2-Sofia-private-handoff"),
            "zip",
            root_dir=staging_root,
            base_dir=sofia_handoff.name,
        )
    if not Path(private_handoff).is_file():
        raise RuntimeError("Sofía private handoff could not be created")
    participant_ids = ",".join(row["participant_id"].strip().lower() for row in rows)
    print(f"PRIVATE_PACKAGES_CREATED count={len(rows)} participants={participant_ids}")
    print("SOFIA_PRIVATE_HANDOFF_CREATED")


if __name__ == "__main__":
    main()
