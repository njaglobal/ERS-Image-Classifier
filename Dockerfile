# # Use official Python slim image
# FROM python:3.12-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy only requirements first for faster caching
# COPY requirements.txt .

# # Install lightweight API dependencies
# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the app
# COPY . .

# # Make start.sh executable
# RUN chmod +x start.sh

# # Expose port (for FastAPI/uvicorn)
# EXPOSE 8000

# # Start the app
# CMD ["./start.sh"]

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement files first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt 

COPY . .

RUN chmod +x start.sh

EXPOSE 8000
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV INSTALL_ML=1

CMD ["./start.sh"]