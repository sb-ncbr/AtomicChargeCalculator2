#!/bin/bash
# This script is used to set up the development environment for the application.

DB_CONTAINER_NAME=dev-postgres-$$

cleanup() {
    echo "Cleaning up docker container ($DB_CONTAINER_NAME)..."
    if [ "$(docker ps -q -f name=$DB_CONTAINER_NAME)" ]; then
        docker stop $DB_CONTAINER_NAME
        echo "Container stopped and removed."
    elif [ "$(docker ps -aq -f name=$DB_CONTAINER_NAME)" ]; then
        echo "Container $DB_CONTAINER_NAME exists but is not running. Attempting removal..."
        docker rm $DB_CONTAINER_NAME
        echo "Container removed."
    else
        echo "Container $DB_CONTAINER_NAME not found or already removed."
    fi
}

trap cleanup EXIT INT TERM

echo "Navigating to the application directory..."
cd ./app || {
    echo "Failed to navigate to ./app"
    exit 1
}

echo "Installing dependencies..."
poetry install || {
    echo "Failed to install dependencies"
    exit 1
}

echo "Starting PostgreSQL database ($DB_CONTAINER_NAME)..."
docker run -d --rm --name=$DB_CONTAINER_NAME -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17-alpine || {
    echo "Failed to start PostgreSQL container"
    exit 1
}

echo "Waiting for PostgreSQL database ($DB_CONTAINER_NAME) to be ready..."

if ! docker ps -q -f name=$DB_CONTAINER_NAME; then
    echo "ERROR: PostgreSQL container ($DB_CONTAINER_NAME) failed to start."
    echo "--- Docker Logs ---"
    docker logs $DB_CONTAINER_NAME
    echo "--- End Docker Logs ---"
    exit 1
fi

echo "PostgreSQL container is ready."

echo "Running migrations..."
poetry run alembic upgrade head

echo "Setting up the environment..."
export CHARGEFW2_INSTALL_DIR=/opt/chargefw2

echo "Starting the web server..."
poetry run gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:web_app
