#!/usr/bin/env bash
# start.sh

# Exit on error
set -o errexit
set -o pipefail
set -o nounset

# Default PORT to 10000 if not provided by Render
PORT="${PORT:-10000}"

# Optional: Sync model files from Supabase (won’t crash if fails)
# python supabase_utils.py || true

# Start FastAPI app with uvicorn (production mode)
exec uvicorn main:app --host 0.0.0.0 --port $PORT