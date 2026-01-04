#!/bin/bash
set -e

echo "Waiting for database connection..."
# A simple wait loop could be added here if needed, or rely on restart_policy.
# But Alembic usually fails fast if DB is down.

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000