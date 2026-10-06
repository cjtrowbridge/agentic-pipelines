#!/usr/bin/env bash
set -euo pipefail

trap 'printf "%s\n" "bootstrap: interrupted" >&2; exit 130' INT

printf '%s\n' 'bootstrap: locating REPLACE_PYTHON_COMMAND'
if ! command -v REPLACE_PYTHON_COMMAND >/dev/null 2>&1; then
  printf '%s\n' 'bootstrap: REPLACE_PYTHON_COMMAND is unavailable. Follow the host setup instructions.' >&2
  exit 1
fi

REPLACE_PYTHON_COMMAND -B "$(dirname "$0")/../scripts/bootstrap.py"

printf '%s\n' 'bootstrap: prerequisites ready; starting host pipeline'
exec REPLACE_PIPELINE_COMMAND "$@"
