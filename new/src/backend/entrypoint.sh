#!/bin/bash

# This script runs migrations before running the gunicorn server.
# It is used in the Dockerfile.

cd /acc2/app

# run database migrations
alembic upgrade head

# use gunicorn with 4 workers
# uvicorn.workers.UvicornWorker is used for async processing
# setting timeout to 1 hour for long lasting computations
# running on port 8000
exec gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 6000 --bind 0.0.0.0:8000 main:web_app
