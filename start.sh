#!/bin/sh

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-config /app/uvicorn_log_config.yaml
