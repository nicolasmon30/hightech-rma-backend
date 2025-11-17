#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
