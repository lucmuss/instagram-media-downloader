#!/bin/bash
set -e

echo "Starting Instagram Media Downloader..."

# Run tests if requested (recommended for production)
if [ "$RUN_TESTS" = "true" ]; then
    echo "Running tests..."
    python -m pytest tests/ -v --tb=short
    echo "Tests passed."
fi

# Application is ready
echo "Instagram Media Downloader is ready."
echo "Run: python -m instagram_downloader --help"

# Keep container running if no command provided
if [ $# -eq 0 ]; then
    echo "Container ready. Use docker exec to run commands."
    tail -f /dev/null
else
    exec "$@"
fi