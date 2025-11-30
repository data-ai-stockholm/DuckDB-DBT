FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install OS deps and python/pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip build-essential git ca-certificates curl \
      libssl-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY ../requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt