#!/bin/bash
set -euo pipefail

# Ensure we're logged into GitHub Container Registry
if ! docker info | grep -q "ghcr.io"; then
  echo "Error: Not logged into ghcr.io. Please run 'docker login ghcr.io' first."
  exit 1
fi

echo "Building Docker image..."
docker build --tag ghcr.io/0235-jp/karkuri-agent-dev:latest \
             --no-cache \
             --file Dockerfile .
echo "Pushing Docker image..."
docker push ghcr.io/0235-jp/karkuri-agent-dev:latest
