"""Load a participant-local, cross-platform environment file without shell execution."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

FORBIDDEN_KEY_FRAGMENTS = ("PASSWORD", "SECRET", "TOKEN", "PRIVATE_KEY")
PATH_VARIABLES = (
    "ADB_WALLET_DIR",
    "LAB02_CALIBRATION_FILE",
    "LAB02_DEVELOPMENT_MEASUREMENTS_FILE",
    "LAB02_REPORT_ROOT",
)


def add_session_file_argument(parser) -> None:
    parser.add_argument(
        "--session-file",
        type=Path,
        help="Private participant .env file outside the repository; passwords are never stored in it.",
    )


def load_participant_session(session_file: Path | None) -> Path | None:
    """Load a private dotenv file or retain the legacy local `.env` behavior."""
    if session_file is None:
        load_dotenv()
        return None
    path = session_file.expanduser().resolve()
    if not path.is_file():
        raise ValueError("Private participant session file is unavailable")
    values = dotenv_values(path)
    forbidden = [
        key
        for key, value in values.items()
        if value is not None and any(fragment in key.upper() for fragment in FORBIDDEN_KEY_FRAGMENTS)
    ]
    if forbidden:
        raise ValueError("Private participant session files must not contain passwords or secrets")
    load_dotenv(path, override=True)
    for key in PATH_VARIABLES:
        raw_value = values.get(key)
        if raw_value and not Path(raw_value).expanduser().is_absolute():
            os.environ[key] = str((path.parent / raw_value).resolve())
    return path
