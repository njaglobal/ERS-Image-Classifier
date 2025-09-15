#!/bin/bash
# Activate virtual environment (optional; Railway handles this automatically)
# Start FastAPI using uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT