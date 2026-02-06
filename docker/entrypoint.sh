#!/bin/bash
set -e

echo "Starting Instagram Media Downloader..."

if [ "$RUN_TESTS" = "true" ]; then
    if [ -d "tests" ]; then
        echo "Running tests..."
        uv run pytest tests/ -v --tb=short
        echo "Tests passed."
    else
        echo "Tests directory not found. Skipping tests."
    fi
fi

echo "Instagram Media Downloader is ready."
echo "Run: uv run python -m instagram_downloader --help"

if [ $# -eq 0 ]; then
    echo "Container ready. Use docker exec to run commands."
    tail -f /dev/null
else
    exec "$@"
fi
