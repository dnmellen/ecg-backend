#!/bin/bash

echo "Starting database..."
docker-compose --log-level ERROR up -d db

echo "Waiting for database..."
scripts/wait_for_db.sh

echo "Starting API..."
docker-compose --log-level ERROR up -d api

echo "Running migrations..."
scripts/run_migrations.sh

echo "Creating superuser..."
scripts/create_superuser.sh admin

echo
echo
echo "-----------------------------"
echo "Your admin user has been created with the username 'admin'."
echo "Go to API docs at http://localhost:8000/api/docs"
