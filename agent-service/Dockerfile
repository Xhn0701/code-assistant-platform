# ============================================
# Agent Service - Python FastAPI
# ============================================

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (for tree-sitter, gitpython, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for dependency caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for vector store
RUN mkdir -p /data/vectorstore

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/ping')" || exit 1

# Run application with Celery worker
CMD ["bash", "start.sh"]
