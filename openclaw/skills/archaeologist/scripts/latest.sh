#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${ARCHAEOLOGIST_API_URL:-http://localhost:8000}"
curl -fsS "$BASE_URL/api/openclaw/repositories/latest"
