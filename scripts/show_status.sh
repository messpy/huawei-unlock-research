#!/usr/bin/env sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
STATE_FILE="$PROJECT_DIR/state/probe-state.json"
if [ ! -f "$STATE_FILE" ]; then
  echo "No state file yet. No probe has been started."
  exit 0
fi
python3 -m json.tool "$STATE_FILE"
