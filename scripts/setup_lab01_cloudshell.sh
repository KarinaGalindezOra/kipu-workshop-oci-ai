#!/usr/bin/env bash
# Source this file from the repository root. It validates a privately delivered Lab 1 session.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Run: source scripts/setup_lab01_cloudshell.sh" >&2
  exit 1
fi

setup_failure() {
  echo "$1" >&2
  return 1
}

project_root="${PROJECT_ROOT:-$HOME/khipu-workshop}"
venv_dir="${LAB01_VENV_DIR:-$project_root/.venv}"
wallet_dir="${LAB01_WALLET_DIR:-}"

if [[ ! -d "$project_root" ]]; then
  setup_failure "LAB01_SESSION_NOT_READY: repository directory is unavailable."
  return 1
fi

if [[ ! -f "$venv_dir/bin/activate" ]]; then
  setup_failure "LAB01_SESSION_NOT_READY: Python virtual environment is unavailable."
  return 1
fi

# shellcheck disable=SC1090
source "$venv_dir/bin/activate"

if [[ -z "$wallet_dir" ]]; then
  setup_failure "LAB01_SESSION_NOT_READY: LAB01_WALLET_DIR is not set. Use the privately delivered wallet directory."
  return 1
fi

wallet_tnsnames="$wallet_dir/tnsnames.ora"

if [[ ! -f "$wallet_tnsnames" ]]; then
  setup_failure "LAB01_SESSION_NOT_READY: the wallet does not contain tnsnames.ora."
  return 1
fi

for required_name in LAB01_DB_USER LAB01_MEMORY_SCHEMA_OWNER LAB01_MEMORY_STORE_ID; do
  if [[ -z "${!required_name:-}" ]]; then
    setup_failure "LAB01_SESSION_NOT_READY: $required_name is not set."
    return 1
  fi
done

# Agent Memory SDK expects its logical store name, not the RAW database UID.
# Keep this validation aligned with the SDK identifier contract so a session
# fails before any database connection when the wrong value was supplied.
if [[ ! "$LAB01_MEMORY_STORE_ID" =~ ^[A-Za-z][A-Za-z0-9_]{0,15}$ ]]; then
  setup_failure "LAB01_SESSION_NOT_READY: LAB01_MEMORY_STORE_ID must be the logical ADB MEMORY_STORE_NAME (1-16 letters, numbers, or underscores; starts with a letter)."
  return 1
fi

export LAB01_WALLET_DIR="$wallet_dir"

if [[ -z "${LAB01_DB_DSN:-}" ]]; then
  LAB01_DB_DSN="$(awk -F= 'tolower($1) ~ /_low[[:space:]]*$/ { gsub(/[[:space:]]/, "", $1); print $1; exit }' "$wallet_tnsnames")"
  if [[ -z "$LAB01_DB_DSN" ]]; then
    setup_failure "LAB01_SESSION_NOT_READY: a lower database service alias could not be selected from the wallet."
    return 1
  fi
  export LAB01_DB_DSN
fi

printf '%s\n' "LAB01_SESSION_READY"
printf '%s\n' "LAB01_VENV_ACTIVE true"
printf '%s\n' "LAB01_WALLET_READY true"
printf '%s\n' "LAB01_DSN_SELECTED true"
printf '%s\n' "LAB01_MEMORY_STORE_READY true"
