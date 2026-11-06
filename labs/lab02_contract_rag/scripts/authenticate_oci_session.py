"""Create or renew the OCI CLI session required by one Workshop 2 participant."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from lab02_contract_rag.private_session import add_session_file_argument, load_participant_session


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set by the private participant session")
    return value


def config_location() -> Path:
    value = os.getenv("OCI_CONFIG_FILE")
    return Path(value).expanduser() if value else Path.home() / ".oci" / "config"


def authenticate_command(*, config_file: Path, profile_name: str, region: str, minutes: int) -> list[str]:
    return [
        "oci",
        "session",
        "authenticate",
        "--config-location",
        str(config_file),
        "--profile-name",
        profile_name,
        "--region",
        region,
        "--session-expiration-in-minutes",
        str(minutes),
    ]


def validate_command(*, config_file: Path, profile_name: str) -> list[str]:
    return [
        "oci",
        "--config-file",
        str(config_file),
        "--profile",
        profile_name,
        "--auth",
        "security_token",
        "session",
        "validate",
        "--output",
        "json",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_session_file_argument(parser)
    parser.add_argument("--session-expiration-minutes", type=int, default=60)
    args = parser.parse_args()
    if not 5 <= args.session_expiration_minutes <= 60:
        parser.error("--session-expiration-minutes must be between 5 and 60")
    load_participant_session(args.session_file)
    if shutil.which("oci") is None:
        raise SystemExit("OCI CLI is unavailable; activate .venv and reinstall the Lab 2 dependencies")

    config_file = config_location()
    profile_name = required_environment("OCI_CONFIG_PROFILE")
    region = required_environment("OCI_REGION")
    subprocess.run(
        authenticate_command(
            config_file=config_file,
            profile_name=profile_name,
            region=region,
            minutes=args.session_expiration_minutes,
        ),
        check=True,
    )
    subprocess.run(validate_command(config_file=config_file, profile_name=profile_name), check=True)
    print("OCI_SESSION_AUTHENTICATED")
    print("OCI_SESSION_VALID")


if __name__ == "__main__":
    main()
