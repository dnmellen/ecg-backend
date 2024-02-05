#!/bin/bash
docker-compose --log-level ERROR exec api python scripts/create_superuser.py "$1"

