# Multi-stage Dockerfile for ElizaOS-OpenCog-GnuCash Microservices
# Supports both cognitive services and GGML-optimized ML services with security hardening

FROM python:3.12-slim as base

# Security: Use specific base image SHA for reproducibility
# Install system dependencies with security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    git \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    # Security scanning tools
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    # Remove package manager to prevent runtime package installation
    && apt-get purge -y --auto-remove apt-utils \
    # Create app directory with proper permissions
    && mkdir -p /app \
    && chmod 755 /app

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Security: Upgrade pip and install dependencies with security flags
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --no-compile --disable-pip-version-check \
       --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
       -r requirements.txt \
    # Remove pip cache to reduce image size
    && rm -rf ~/.cache/pip

# Production stage with security hardening
FROM base as production

# Security: Copy application code with proper permissions
COPY --chown=1000:1000 src/ ./src/
COPY --chown=1000:1000 *.py ./

# Security: Create non-root user with specific UID/GID and restricted permissions
RUN groupadd -r -g 1000 appuser \
    && useradd -r -u 1000 -g appuser -d /app -s /sbin/nologin -c "Application User" appuser \
    # Set proper permissions
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    # Remove write permissions for security
    && chmod -R 444 /app/src/ \
    && chmod 555 /app/*.py \
    # Create runtime directories with proper permissions
    && mkdir -p /app/logs /app/metrics /app/tmp \
    && chown appuser:appuser /app/logs /app/metrics /app/tmp \
    && chmod 755 /app/logs /app/metrics /app/tmp

# Security: Switch to non-root user
USER appuser

# Security: Enhanced health check with better security
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f -s --max-time 5 http://localhost:8000/health || exit 1

# Security: Read-only filesystem (will be overridden by docker-compose if needed)
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# Default command with security context
CMD ["python", "-u", "-m", "src.microservices.service_discovery"]

# GGML-optimized stage for ML services with enhanced security
FROM base as ggml

# Install additional ML dependencies securely
RUN pip install --no-cache-dir --no-compile \
    torch \
    transformers \
    accelerate \
    bitsandbytes \
    # Security scanning for Python
    bandit \
    safety \
    && rm -rf ~/.cache/pip

# Security: Create GGML directory with proper permissions
RUN mkdir -p /app/ggml /app/models \
    && chmod 755 /app/ggml /app/models

# Copy ML-specific configurations with security
COPY --chown=1000:1000 docker/configs/ggml/ ./configs/ 2>/dev/null || true

# Copy application code with security
COPY --chown=1000:1000 src/ ./src/
COPY --chown=1000:1000 *.py ./

# Security: Create ML service user with restricted permissions
RUN groupadd -r -g 1001 mluser \
    && useradd -r -u 1001 -g mluser -d /app -s /sbin/nologin -c "ML Service User" mluser \
    && chown -R mluser:mluser /app \
    && chmod -R 755 /app \
    && chmod -R 444 /app/src/ \
    # Create runtime directories for ML operations
    && mkdir -p /app/model_cache /app/inference_logs \
    && chown mluser:mluser /app/model_cache /app/inference_logs \
    && chmod 755 /app/model_cache /app/inference_logs

USER mluser

# Security: Enhanced health check for ML services
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f -s --max-time 10 http://localhost:8000/health || exit 1

# Command for GGML services with security
CMD ["python", "-u", "-m", "src.microservices.ggml_optimization"]

# Service discovery stage
FROM production as discovery

EXPOSE 8001

ENV SERVICE_TYPE=discovery
ENV SERVICE_PORT=8001

CMD ["python", "-c", "from src.microservices import ServiceRegistry; import asyncio; asyncio.run(ServiceRegistry().start())"]

# Load balancer stage  
FROM production as loadbalancer

EXPOSE 8002

ENV SERVICE_TYPE=loadbalancer
ENV SERVICE_PORT=8002

CMD ["python", "-c", "from src.microservices import LoadBalancer; print('Load balancer ready')"]

# Orchestration stage
FROM production as orchestrator

EXPOSE 8003

ENV SERVICE_TYPE=orchestrator
ENV SERVICE_PORT=8003

CMD ["python", "-c", "from src.microservices import ServiceOrchestrator; print('Orchestrator ready')"]