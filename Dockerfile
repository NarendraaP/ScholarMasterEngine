FROM python:3.9-slim

# Paper 11: Production Docker Container
# ======================================
# Multi-stage build for minimal image size

LABEL maintainer="ScholarMaster Research Group"
LABEL paper="Paper 11 - Deployment & Validation"
LABEL version="2.1"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    SCHOLAR_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create application user (non-root for security)
RUN useradd -m -u 1000 scholar && \
    mkdir -p /opt/scholarmaster && \
    chown -R scholar:scholar /opt/scholarmaster

WORKDIR /opt/scholarmaster

# Copy requirements first (layer caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=scholar:scholar . .

# Create necessary directories
RUN mkdir -p data logs checkpoints && \
    chown -R scholar:scholar data logs checkpoints

# Switch to non-root user
USER scholar

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Expose ports
EXPOSE 5000 8080

# Entry point
CMD ["python3", "main.py"]
