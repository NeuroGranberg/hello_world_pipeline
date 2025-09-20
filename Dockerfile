# Minimal image for the hello-world pipeline.
# Replace the base image if you need GPUs or system packages.
FROM prefecthq/prefect:3-python3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy flow code last to maximise layer cache hits.
COPY flows/ ./flows/

# The Prefect worker sets the entrypoint; no CMD is required here.
