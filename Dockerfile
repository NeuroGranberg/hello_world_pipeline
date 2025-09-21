# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (keep Python 3.11 from base image)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install Python packages from wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY flows/ ./flows/

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Verify Python is accessible
RUN python3 --version && which python3

# The Prefect worker will set the entrypoint
