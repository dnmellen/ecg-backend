#!/bin/bash
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path/to/test/files> [additional pytest arguments]"
    exit 1
fi

test_path="$1"
shift

TEST=1 docker-compose --log-level ERROR run --rm -e TEST api pytest --cov=app "$test_path" "$@"
