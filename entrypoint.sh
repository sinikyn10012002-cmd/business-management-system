#!/bin/sh

mkdir -p /project/data

echo "Applying migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000