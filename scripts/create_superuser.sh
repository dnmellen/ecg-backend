#!/bin/bash
docker compose exec api python scripts/create_superuser.py "$1"

