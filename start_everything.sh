#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
ENTRYPOINT="$PROJECT_ROOT/scripts/entrypoints/start_all.sh"

if [ ! -x "$ENTRYPOINT" ]; then
  echo "❌ Could not find executable start_all script at $ENTRYPOINT"
  echo "Ensure scripts/entrypoints/start_all.sh exists and is executable."
  exit 1
fi

exec "$ENTRYPOINT"
