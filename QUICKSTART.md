# ⚡ Quick Start Guide

## Installation im Virtual Environment (bereits aktiviert)

Da Sie bereits ein `venv` aktiviert haben, führen Sie diese Befehle aus:

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. Package im Development-Modus installieren
pip install -e .

# 3. Verifizieren
instagram-downloader --help
```

## Alternative: Direkte Verwendung ohne Installation

Falls die Installation Probleme macht, können Sie das Tool direkt ausführen:

```bash
# Dependencies installieren
pip install tqdm

# Tool direkt als Modul ausführen
python3 -m instagram_downloader --help
python3 -m instagram_downloader liked
python3 -m instagram_downloader saved
```

## Schnelltest

```bash
# Hilfe anzeigen
python3 -m instagram_downloader --help

# Version anzeigen
python3 -m instagram_downloader --version

# Gelikte Posts herunterladen (Beispiel)
python3 -m instagram_downloader liked

# Mit Optionen
python3 -m instagram_downloader liked --delay 2.0 --log-level INFO

# Alle Kategorien
python3 -m instagram_downloader all
```

## Wichtig vor dem ersten Download

1. **Instagram-Export vorbereiten:**
   ```bash
   # Stelle sicher, dass diese Struktur existiert:
   data/skymuss/saved/saved_posts.json
   data/skymuss/likes/liked_posts.json
   ```

2. **yt-dlp installieren:**
   ```bash
   sudo apt install yt-dlp
   ```

## Beispiel-Workflow

```bash
# 1. Virtual Environment aktivieren (bereits gemacht)
source venv/bin/activate

# 2. Dependencies installieren
pip install tqdm

# 3. Gelikte Posts herunterladen
python3 -m instagram_downloader liked

# Ausgabe erscheint in:
# - downloads/liked/        (Medien-Dateien)
# - instagram_liked_metadata.csv  (Metadaten)
# - logs/                   (Log-Dateien)
```

## Häufige Befehle

```bash
# Nur Bookmarks (Saved)
python3 -m instagram_downloader saved

# Nur Likes
python3 -m instagram_downloader liked

# Nur eigene Posts
python3 -m instagram_downloader own

# Alles
python3 -m instagram_downloader all

# Mit Debug-Logging
python3 -m instagram_downloader liked --log-level DEBUG

# Bei Rate-Limits: längere Verzögerung
python3 -m instagram_downloader saved --delay 3.0
```
