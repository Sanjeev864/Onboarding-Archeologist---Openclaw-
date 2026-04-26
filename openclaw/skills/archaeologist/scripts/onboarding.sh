#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_ID="${1:?repository id required}"
LEVEL="${2:-junior}"
BASE_URL="${ARCHAEOLOGIST_API_URL:-http://localhost:8000}"
curl -fsS "$BASE_URL/api/openclaw/repositories/$REPOSITORY_ID/onboarding/$LEVEL"
