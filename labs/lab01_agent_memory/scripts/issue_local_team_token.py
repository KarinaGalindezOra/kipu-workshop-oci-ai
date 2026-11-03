"""Issue a short-lived local-rehearsal token for one Lab 1 workshop team."""

from __future__ import annotations

import argparse
import os

from lab01_agent_memory.gateway_auth import issue_local_team_token


def main() -> None:
    """Print a token without printing its signing secret."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--ttl-seconds", type=int, default=3600)
    args = parser.parse_args()
    secret = os.environ.get("LAB01_WORKSHOP_TOKEN_SECRET")
    if not secret:
        raise RuntimeError("LAB01_WORKSHOP_TOKEN_SECRET must be set before issuing a token")
    print(issue_local_team_token(args.team_id, secret, args.ttl_seconds))


if __name__ == "__main__":
    main()
