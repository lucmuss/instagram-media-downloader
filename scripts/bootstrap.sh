#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log() {
    printf "[bootstrap] %s\n" "$*"
}

to_lower() {
    printf "%s" "${1:-}" | tr "[:upper:]" "[:lower:]"
}

load_env() {
    if [ -f ".env" ]; then
        log "Lade .env"
        set -a
        # shellcheck disable=SC1091
        source ".env"
        set +a
    else
        log "Keine .env gefunden. Nutze vorhandene System-Umgebung."
    fi
}

prepare_dirs() {
    local download_dir="${DOWNLOAD_DIR:-$ROOT_DIR/downloads}"
    local state_dir="${STATE_DIR:-$ROOT_DIR/state}"
    local logs_dir="${LOG_DIR:-$ROOT_DIR/logs}"

    mkdir -p "$download_dir" "$state_dir" "$logs_dir"
    log "Verzeichnisse vorbereitet:"
    log "  DOWNLOAD_DIR=$download_dir"
    log "  STATE_DIR=$state_dir"
    log "  LOG_DIR=$logs_dir"
}

run_tests() {
    if [ "$(to_lower "${RUN_TESTS:-false}")" != "true" ]; then
        log "Tests deaktiviert (RUN_TESTS!=true)."
        return 0
    fi

    if [ ! -d "tests" ]; then
        log "tests/ nicht gefunden. Tests werden uebersprungen."
        return 0
    fi

    log "Starte Tests..."
    uv run pytest tests/ -v --tb=short
    log "Tests erfolgreich."
}

show_info() {
    if command -v yt-dlp >/dev/null 2>&1; then
        log "yt-dlp verfuegbar."
    else
        log "yt-dlp nicht gefunden. Installiere z. B. mit 'uv tool install yt-dlp'."
    fi

    log "Beispiel:"
    log "  uv run python -m instagram_downloader --help"
}

run_all() {
    load_env
    prepare_dirs
    run_tests
    show_info
}

usage() {
    cat <<'EOF'
Usage:
  ./scripts/bootstrap.sh [command]

Commands:
  all           Voller Bootstrap (default)
  load_env      .env explizit laden (falls vorhanden)
  prepare_dirs  Download/State/Log Verzeichnisse anlegen
  run_tests     Tests nur bei RUN_TESTS=true ausfuehren
  show_info     Kurzinfo zu Runtime/Abhaengigkeiten
EOF
}

case "${1:-all}" in
    all)
        run_all
        ;;
    load_env)
        load_env
        ;;
    prepare_dirs)
        load_env
        prepare_dirs
        ;;
    run_tests)
        load_env
        run_tests
        ;;
    show_info)
        load_env
        show_info
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        log "Unbekannter Befehl: $1"
        usage
        exit 1
        ;;
esac
