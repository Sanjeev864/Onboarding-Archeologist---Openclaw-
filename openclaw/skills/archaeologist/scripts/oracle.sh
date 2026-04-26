#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_ID="${1:?repository id required}"
QUESTION="${2:?question required}"
BASE_URL="${ARCHAEOLOGIST_API_URL:-http://localhost:8000}"

curl -fsS -X POST "$BASE_URL/api/openclaw/ask" \
  -H "Content-Type: application/json" \
  -d "{\"repository_id\":$REPOSITORY_ID,\"question\":\"$QUESTION\"}"
