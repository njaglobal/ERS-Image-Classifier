#!/bin/bash

echo "🔹 Starting FastAPI server..."

# Conditionally install ML frameworks
if [ "$INSTALL_ML" = "1" ]; then
    echo "⚡ Installing TensorFlow, PyTorch, Transformers..."
    pip install --no-cache-dir -r ml-requirements.txt
fi

# Run FastAPI
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}