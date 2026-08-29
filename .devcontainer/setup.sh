#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
cp -n .env.example .env 2>/dev/null || true
docker compose up --build --detach

echo "NewsPulse setup completed. Run: bash .devcontainer/show-url.sh"

