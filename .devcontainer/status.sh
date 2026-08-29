#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
echo "NewsPulse services:"
docker compose ps --format 'table {{.Name}}\t{{.Status}}' || true
echo
echo "When the frontend is healthy, run: bash .devcontainer/show-url.sh"

