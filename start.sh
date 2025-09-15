#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# Use Cloud Run / Docker-provided PORT
PORT="${PORT:-8080}"

# Optional: sync model files from Supabase
# python supabase_utils.py || true

# Start FastAPI with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port $PORT
