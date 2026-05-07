#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
ARCHAEOLOGIST_API_URL="${ARCHAEOLOGIST_API_URL:-http://localhost:8000}"
SKIP_BACKEND_CHECK="${SKIP_BACKEND_CHECK:-false}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT_DIR/openclaw/skills/archaeologist"
CONFIG_SOURCE="$ROOT_DIR/openclaw/openclaw.config.yaml"
DESTINATION="$OPENCLAW_HOME/skills/archaeologist"
CONFIG_DESTINATION="$OPENCLAW_HOME/openclaw.config.yaml"
JSON_CONFIG_DESTINATION="$OPENCLAW_HOME/openclaw.json"
ENV_FILE="$OPENCLAW_HOME/archaeologist.env"

fail() {
  echo "OpenClaw skill install failed: $*" >&2
  exit 1
}

if [ ! -d "$SOURCE" ]; then
  fail "Skill source not found: $SOURCE"
fi

if [ ! -f "$CONFIG_SOURCE" ]; then
  fail "Gateway config not found: $CONFIG_SOURCE"
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  fail "TELEGRAM_BOT_TOKEN is not set. Set it before installing so OpenClaw can start the Telegram channel."
fi

if [ "$SKIP_BACKEND_CHECK" != "true" ]; then
  HEALTH_URL="${ARCHAEOLOGIST_API_URL%/}/health"
  if command -v curl >/dev/null 2>&1; then
    curl -fsS --max-time 10 "$HEALTH_URL" >/dev/null || fail "Backend is not reachable at $ARCHAEOLOGIST_API_URL. Start FastAPI first, or set SKIP_BACKEND_CHECK=true."
  else
    fail "curl is required for backend verification. Install curl or set SKIP_BACKEND_CHECK=true."
  fi
  echo "Backend reachable at $HEALTH_URL"
fi

mkdir -p "$(dirname "$DESTINATION")" "$OPENCLAW_HOME"
rm -rf "$DESTINATION"
cp -R "$SOURCE" "$DESTINATION"
cp "$CONFIG_SOURCE" "$CONFIG_DESTINATION"

cat > "$JSON_CONFIG_DESTINATION" <<JSON
{
  "skills": {
    "entries": {
      "archaeologist": {
        "enabled": true,
        "path": "~/.openclaw/skills/archaeologist",
        "env": {
          "ARCHAEOLOGIST_API_URL": "$ARCHAEOLOGIST_API_URL"
        }
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "mode": "polling",
      "botTokenEnv": "TELEGRAM_BOT_TOKEN",
      "skills": ["archaeologist"],
      "allowedCommands": ["analyze-autonomous", "agent-trace", "onboarding", "agent-feedback", "agent-status", "ask"],
      "rateLimits": {
        "default": { "requests": 20, "windowSeconds": 60 },
        "analyze-autonomous": { "requests": 3, "windowSeconds": 600 },
        "onboarding": { "requests": 10, "windowSeconds": 300 },
        "agent-feedback": { "requests": 30, "windowSeconds": 300 }
      }
    }
  }
}
JSON

cat > "$ENV_FILE" <<ENV
export ARCHAEOLOGIST_API_URL="$ARCHAEOLOGIST_API_URL"
: "\${TELEGRAM_BOT_TOKEN:?Set TELEGRAM_BOT_TOKEN before starting OpenClaw Gateway.}"
ENV

echo "Installed Onboarding Archaeologist skill to: $DESTINATION"
echo "Registered skill config at: $JSON_CONFIG_DESTINATION"
echo "Copied gateway YAML to: $CONFIG_DESTINATION"
echo "Environment helper written to: $ENV_FILE"
echo ""
echo "Next:"
echo "1. Restart OpenClaw Gateway: openclaw gateway"
echo "2. In a new shell, run: source \"$ENV_FILE\""
