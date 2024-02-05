#!/bin/bash

docker-compose --log-level ERROR exec api bash -c "while !</dev/tcp/db/5432; do sleep 1; done;"
