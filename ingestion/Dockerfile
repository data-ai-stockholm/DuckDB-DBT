FROM python:3.11-slim

LABEL maintainer="data-ai-stockholm"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build tools (some Python packages may need them)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Ensure ingestion_data dir exists and is writeable
RUN mkdir -p /app/ingestion_data \
    && chown -R 1000:1000 /app/ingestion_data || true

# NOTE: do NOT add an ENTRYPOINT or CMD here — leave runtime control to docker-compose or the user

WORKDIR /app
