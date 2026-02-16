#!/usr/bin/env bash
set -euo pipefail

echo "Starting Instagram Media Downloader..."
/app/scripts/bootstrap.sh all

if [ "$#" -eq 0 ]; then
    echo "Container bereit. Beispiel:"
    echo "  docker exec -it <container> uv run python -m instagram_downloader --help"
    tail -f /dev/null
fi

exec "$@"
