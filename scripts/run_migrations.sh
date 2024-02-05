#!/bin/bash
docker-compose --log-level ERROR exec api alembic upgrade head
