# Multi-stage build for maximum optimization
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install Python packages from wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY flows/ ./flows/

# Switch to non-root user
USER appuser

# The Prefect worker will set the entrypoint
