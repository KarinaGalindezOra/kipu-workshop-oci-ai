"""Workshop command entry point."""

import sys

from lab02_contract_rag.live_validation import main

if "--ingest-only" not in sys.argv:
    sys.argv.append("--ingest-only")

if __name__ == "__main__":
    main()
