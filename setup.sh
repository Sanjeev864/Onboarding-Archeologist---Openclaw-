#!/usr/bin/env bash
set -euo pipefail

echo "Checking prerequisites..."
command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add your GITHUB_TOKEN before analyzing private repositories."
fi

mkdir -p data
echo "Setup complete. Run: docker-compose up -d --build"
