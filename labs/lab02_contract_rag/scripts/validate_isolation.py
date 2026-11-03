"""Read-only cross-participant probe; does not create, alter or delete data."""

import argparse

from dotenv import load_dotenv
from lab02_contract_rag.live_validation import create_database_connection, settings_from_environment
from lab02_contract_rag.participant import assert_peer_access_denied, participant_id

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--peer-participant-id", required=True, type=participant_id)
parser.add_argument("--confirm-peer-table-ready", action="store_true")
args = parser.parse_args()
if not args.confirm_peer_table_ready:
    parser.error("An administrator must confirm the peer user and table exist before this probe")
load_dotenv()
try:
    settings = settings_from_environment(require_calibration=False)
    if args.peer_participant_id == settings.participant_id:
        raise ValueError("Select a different participant")
    with create_database_connection(settings) as connection:
        assert_peer_access_denied(connection, args.peer_participant_id, settings.table_name)
    print("PEER_READ_DENIED True; prerequisite: administrator verified peer table existence")
except Exception:
    raise SystemExit("Isolation validation failed; administrator review required") from None
