#!/usr/bin/env bash
set -euo pipefail

trap 'printf "%s\n" "bootstrap: interrupted" >&2; exit 130' INT

printf '%s\n' 'bootstrap: checking REPLACE_PREREQUISITE_COMMAND'
if ! command -v REPLACE_PREREQUISITE_COMMAND >/dev/null 2>&1; then
  printf '%s\n' 'bootstrap: REPLACE_PREREQUISITE_COMMAND is unavailable. Follow the host setup instructions.' >&2
  exit 1
fi

printf '%s\n' 'bootstrap: prerequisites ready; starting host pipeline'
exec REPLACE_PIPELINE_COMMAND "$@"
