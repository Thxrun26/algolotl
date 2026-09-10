#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "🦎 Algolotl — starting…"
python3 scripts/generate.py
cd backend
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -q -r requirements.txt
export ALGO_SECRET_KEY="${ALGO_SECRET_KEY:-$(python3 -c 'import secrets;print(secrets.token_hex(32))')}"
echo "→ http://localhost:8000   (docs: /docs)"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
