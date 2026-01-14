#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" || true
  fi
}
trap cleanup EXIT

# Backend
(
  cd "$BACKEND_DIR"
  if [[ ! -d "$BACKEND_VENV" ]]; then
    uv venv "$BACKEND_VENV"
  fi
  if [[ ! -f "$BACKEND_VENV/.deps_installed" ]]; then
    uv pip install --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      -r requirements.txt
    touch "$BACKEND_VENV/.deps_installed"
  fi
  uv run --venv "$BACKEND_VENV" uvicorn main:app --reload --port 8000
) &
BACKEND_PID=$!

# Frontend
(
  cd "$FRONTEND_DIR"
  if [[ ! -d "node_modules" ]]; then
    npm install
  fi
  npm run dev
) &
FRONTEND_PID=$!

wait
