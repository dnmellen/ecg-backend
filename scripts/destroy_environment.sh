#!/bin/bash

docker-compose down
docker-compose rm api
docker-compose rm db
docker volume rm ecg-backend_postgres_data