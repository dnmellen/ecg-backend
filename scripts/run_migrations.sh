#!/bin/bash
docker compose exec api alembic upgrade head
