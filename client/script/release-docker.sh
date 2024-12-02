#!/bin/bash
set -euo pipefail

echo "Building Docker image..."
docker build --tag ghcr.io/0235-jp/karkuri-agent-app-dev:latest \
             --no-cache \
             --file Dockerfile .
echo "Pushing Docker image..."
docker push ghcr.io/0235-jp/karkuri-agent-app-dev:latest
