#!/usr/bin/env bash
set -euo pipefail

OWNER="${1:?owner required}"
REPO="${2:?repo required}"
BRANCH="${3:-}"
BASE_URL="${ARCHAEOLOGIST_API_URL:-http://localhost:8000}"

curl -fsS "$BASE_URL/health" >/dev/null || {
  echo "Analyzer not running at $BASE_URL. Start it with: docker-compose up -d backend" >&2
  exit 1
}

curl -fsS -X POST "$BASE_URL/api/openclaw/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"owner\":\"$OWNER\",\"repo\":\"$REPO\",\"branch\":\"$BRANCH\"}"
