# ==========================
# Stage 1: Build stage
# ==========================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Upgrade pip and install packages without cache
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ==========================
# Stage 2: Final image
# ==========================
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

# Remove unnecessary Python cache files to save space
RUN find . -type d -name "__pycache__" -exec rm -rf {} + \
    && chmod +x start.sh

# Expose FastAPI port
EXPOSE 8000

# Start the app
CMD ["./start.sh"]

  