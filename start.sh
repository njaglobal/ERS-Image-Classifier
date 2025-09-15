#!/usr/bin/env bash
# start.sh

# Exit on error
set -o errexit
set -o pipefail
set -o nounset

# Sync model files from Supabase (optional, won’t crash if fails)
# python supabase_utils.py || true

# Start FastAPI app with uvicorn (production mode, no reload)
exec uvicorn main:app --host 0.0.0.0 --port 10000