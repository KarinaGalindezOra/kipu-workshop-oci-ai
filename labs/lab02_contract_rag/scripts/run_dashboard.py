"""Launch a loopback-only dashboard for the participant assigned in the private session."""

import argparse
import os
import subprocess
import sys

from lab02_contract_rag.corpus import LAB_ROOT
from lab02_contract_rag.participant import participant_id
from lab02_contract_rag.private_session import add_session_file_argument, load_participant_session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8502)
    add_session_file_argument(parser)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Use a nonprivileged local port")
    load_participant_session(args.session_file)
    try:
        participant_id(os.environ["LAB02_PARTICIPANT_ID"])
    except (KeyError, ValueError):
        raise SystemExit("Load your private participant session first") from None
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(LAB_ROOT / "ui/app.py"),
                "--server.address",
                "127.0.0.1",
                "--server.port",
                str(args.port),
                "--server.headless",
                "true",
                "--browser.gatherUsageStats",
                "false",
            ]
        )
    )


if __name__ == "__main__":
    main()
