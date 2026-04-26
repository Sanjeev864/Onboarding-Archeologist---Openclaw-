#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT_DIR/openclaw/skills/archaeologist"
DESTINATION="$OPENCLAW_HOME/skills/archaeologist"

if [ ! -d "$SOURCE" ]; then
  echo "Skill source not found: $SOURCE" >&2
  exit 1
fi

mkdir -p "$(dirname "$DESTINATION")"
rm -rf "$DESTINATION"
cp -R "$SOURCE" "$DESTINATION"

echo "Installed Code Archaeologist skill to: $DESTINATION"
echo "Next:"
echo "1. Ensure backend is running: docker-compose up -d backend"
echo "2. Enable the skill in $OPENCLAW_HOME/openclaw.json if needed"
echo "3. Restart OpenClaw gateway: openclaw gateway"
