#!/bin/bash

# This script runs migrations before running the gunicorn server.
# It is used in the Dockerfile.

cd /acc2/app

alembic upgrade head

exec gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 600 --bind 0.0.0.0:8000 main:web_app