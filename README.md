# 📥 Instagram Media Downloader v2.0

Ein **professionelles** Python CLI-Tool zum Herunterladen von Instagram-Medien aus deinem Datenexport.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

✅ **Separate Kategorien** - Download von Saved Posts (Bookmarks), Liked Posts und eigenen Posts  
✅ **Professionelles CLI** - Intuitive Kommandozeilen-Schnittstelle mit vielen Optionen  
✅ **Organisierte Struktur** - Automatische Sortierung in separate Ordner (saved/, liked/, own/)  
✅ **Konfigurierbar** - Via CLI-Argumente, Umgebungsvariablen oder Config-Datei  
✅ **Robustes Logging** - Farbige Console-Ausgabe + detaillierte Log-Dateien  
✅ **Retry-Mechanismus** - Automatische Wiederholungsversuche bei Fehlern  
✅ **Resume-Funktion** - Fortsetzen nach Unterbrechung ohne erneuten Download  
✅ **CSV-Export** - Detaillierte Metadaten für alle Downloads  
✅ **Progress-Tracking** - Fortschrittsbalken mit tqdm  
✅ **Production-Ready** - Fehlerbehandlung, Validierung, saubere Architektur  

## 📋 Voraussetzungen

### System-Requirements

- **Python** 3.8 oder höher
- **yt-dlp** - Für Instagram-Downloads (System-Package oder pip)
- **tqdm** - Python-Package (wird automatisch installiert)

### 🚀 Schnell-Installation

```bash
# 1. Repository klonen
git clone https://github.com/lucmuss/instagram-media-downloader.git
cd instagram-media-downloader

# 2. Virtual Environment erstellen (empfohlen)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# 3. Dependencies installieren
pip install tqdm

# 4. yt-dlp installieren
sudo apt install yt-dlp  # Ubuntu/Debian
# oder: pip install yt-dlp

# 5. Fertig! Tool verwenden
python3 -m instagram_downloader --help
```

### Alternative: Mit pip-Installation

```bash
# Im Virtual Environment
pip install -e .
instagram-downloader --help
```

**💡 Tipp:** Siehe `QUICKSTART.md` für detaillierte Installationsanweisungen!

## 🚀 Schnellstart

### 1. Instagram-Datenexport vorbereiten

Lade deinen Instagram-Datenexport herunter und stelle sicher, dass er diese Struktur hat:

```
instagram-media-downloader/
├── data/
│   └── skymuss/              # Dein Username
│       ├── saved/
│       │   └── saved_posts.json     # Gespeicherte Posts (Bookmarks)
│       └── likes/
│           └── liked_posts.json     # Gelikte Posts
```

**Instagram-Daten herunterladen:**
1. Instagram → Einstellungen → Konto-Center → Deine Informationen und Berechtigungen
2. "Informationen herunterladen" → JSON-Format auswählen
3. Warte auf E-Mail mit Download-Link
4. Entpacke Daten in `data/` Ordner

### 2. Tool verwenden

```bash
# Gelikte Posts herunterladen
python3 -m instagram_downloader liked

# Gespeicherte Posts (Bookmarks)
python3 -m instagram_downloader saved

# Alles herunterladen
python3 -m instagram_downloader all
```

## 📖 Verwendung

### Grundlegende Syntax

```bash
# Nach Installation mit pip
instagram-downloader <command> [optionen]

# Ohne Installation (direkt als Modul)
python3 -m instagram_downloader <command> [optionen]
```

### Verfügbare Commands

| Command | Beschreibung |
|---------|-------------|
| `saved` | Lädt gespeicherte Posts (Bookmarks) herunter |
| `liked` | Lädt gelikte Posts herunter |
| `own` | Lädt eigene Posts herunter |
| `all` | Lädt alle drei Kategorien herunter |

### CLI-Optionen

#### Konfiguration

```bash
-u, --username USERNAME        Instagram-Username
-d, --data-dir PATH           Verzeichnis mit Instagram-Export
-o, --output-dir PATH         Ziel-Verzeichnis für Downloads
-c, --config PATH             Pfad zu Konfigurationsdatei (.ini)
```

#### Download-Optionen

```bash
--delay SECONDS               Verzögerung zwischen Downloads (Standard: 1.0)
--max-retries N               Max. Wiederholungsversuche (Standard: 3)
--timeout SECONDS             Timeout für Downloads (Standard: 60)
--no-csv                      CSV-Export deaktivieren
```

#### Logging

```bash
--log-level LEVEL             Log-Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
--log-file PATH               Pfad zur Log-Datei
--no-log-file                 Keine Log-Datei erstellen
```

### Beispiele

#### Mit eigenem Username

```bash
python3 -m instagram_downloader liked --username mein_username
```

#### Mit angepasster Verzögerung (bei Rate-Limits)

```bash
python3 -m instagram_downloader saved --delay 2.5
```

#### Mit Debug-Logging

```bash
python3 -m instagram_downloader all --log-level DEBUG
```

#### Mit Konfigurationsdatei

```bash
# 1. Beispiel-Konfiguration kopieren
cp config.example.ini config.ini

# 2. In config.ini Username und Pfade anpassen

# 3. Verwenden
python3 -m instagram_downloader saved --config config.ini
```

#### Custom Ausgabe-Verzeichnis

```bash
python3 -m instagram_downloader liked --output-dir /mnt/externe-festplatte/instagram
```

#### Nur neue Downloads (Resume)

```bash
# Wird automatisch fortgesetzt - bereits heruntergeladene Dateien werden übersprungen
python3 -m instagram_downloader liked
```

## ⚙️ Konfiguration

### Via Umgebungsvariablen

```bash
export INSTAGRAM_USERNAME="mein_username"
export DATA_DIR="/pfad/zum/instagram-export/data"
export DOWNLOAD_DIR="/pfad/zum/output"
export REQUEST_DELAY="1.5"
export MAX_RETRIES="5"
export LOG_LEVEL="DEBUG"

python3 -m instagram_downloader liked
```

### Via Config-Datei

Erstelle `config.ini`:

```ini
[DEFAULT]
username = mein_username
data_dir = /pfad/zum/data
download_dir = /pfad/zum/output
request_delay = 1.5
max_retries = 3
log_level = INFO
csv_export = true
```

Verwenden:

```bash
python3 -m instagram_downloader saved --config config.ini
```

## 📁 Verzeichnisstruktur

Nach der Installation und ersten Nutzung:

```
instagram-media-downloader/
├── instagram_downloader/       # Python-Package
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                 # CLI-Interface
│   ├── config.py              # Konfiguration
│   ├── downloader.py          # Download-Logik
│   └── logger.py              # Logging
├── data/                      # Instagram-Export-Daten
│   └── skymuss/
│       ├── saved/
│       ├── likes/
│       └── posts/
├── downloads/                 # Heruntergeladene Medien
│   ├── saved/                # Gespeicherte Posts
│   ├── liked/                # Gelikte Posts
│   └── own/                  # Eigene Posts
├── state/                    # Resume-State-Dateien
│   ├── saved_downloaded.txt
│   ├── liked_downloaded.txt
│   └── own_downloaded.txt
├── logs/                     # Log-Dateien
│   └── instagram_downloader_*.log
├── config.example.ini        # Beispiel-Konfiguration
├── setup.py                  # Installation
├── requirements.txt          # Dependencies
└── README.md                 # Diese Datei
```

## 📊 CSV-Metadaten

Für jede Kategorie wird eine CSV-Datei erstellt:

- `instagram_saved_metadata.csv`
- `instagram_liked_metadata.csv`
- `instagram_own_metadata.csv`

**Format:**

| Spalte | Beschreibung |
|--------|-------------|
| source | Kategorie (saved, liked, own) |
| title | Instagram-Username des Erstellers |
| timestamp | Unix-Timestamp |
| datetime | Lesbare Datumszeit |
| url | Original Instagram-URL |
| filename | Lokaler Dateiname |
| media_type | video oder image |

## 🔧 Fehlerbehebung

### yt-dlp nicht gefunden

**Problem:** `yt-dlp ist nicht installiert!`

**Lösung:**
```bash
# System-weite Installation (empfohlen)
sudo apt update
sudo apt install yt-dlp

# Oder im Virtual Environment
pip install yt-dlp

# Verifizieren
yt-dlp --version
```

### Rate-Limits von Instagram

**Problem:** Viele Downloads schlagen fehl

**Lösung:** Erhöhe die Verzögerung:
```bash
python3 -m instagram_downloader saved --delay 2.5
# oder sogar
python3 -m instagram_downloader saved --delay 5.0
```

### JSON-Datei nicht gefunden

**Problem:** `JSON-Datei nicht gefunden`

**Lösung:** Überprüfe die Pfade und Username:
```bash
python3 -m instagram_downloader liked --data-dir /korrekter/pfad/zum/data --username dein_username

# Oder setze Umgebungsvariablen
export INSTAGRAM_USERNAME="dein_username"
export DATA_DIR="/korrekter/pfad/zum/data"
python3 -m instagram_downloader liked
```

### Downloads schlagen fehl

**Mögliche Ursachen:**
- Posts wurden gelöscht
- Account ist privat
- Netzwerkprobleme
- Instagram-Änderungen

**Lösung:** Logs prüfen in `logs/` Verzeichnis

### Resume nach Unterbrechung

Einfach den gleichen Befehl erneut ausführen:
```bash
python3 -m instagram_downloader liked
# Überspringt automatisch bereits heruntergeladene Dateien
# basierend auf state/liked_downloaded.txt
```

## 🐛 Development

### Entwicklungsumgebung einrichten

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate  # Windows

# Development-Installation
pip install -e ".[dev]"
```

### Tests ausführen

```bash
pytest tests/
```

### Code-Formatierung

```bash
black instagram_downloader/
```

### Linting

```bash
flake8 instagram_downloader/
```

## 📝 Direkte Ausführung (empfohlen)

Das Tool kann direkt als Python-Modul ausgeführt werden, ohne Installation:

```bash
# Tool-Hilfe anzeigen
python3 -m instagram_downloader --help

# Verschiedene Kommandos
python3 -m instagram_downloader saved
python3 -m instagram_downloader liked
python3 -m instagram_downloader own
python3 -m instagram_downloader all
```

Dies ist die **empfohlene Methode**, da sie keine Installation erfordert.

## 🛡️ Hinweise

⚠️ **Instagram Terms of Service** - Nutze dieses Tool nur für deine eigenen Daten  
⚠️ **Rate Limits** - Respektiere Instagram's Server-Limits  
⚠️ **Datenschutz** - Heruntergeladene Medien sind deine persönlichen Backups  
⚠️ **Keine Garantie** - Instagram kann HTML-Struktur jederzeit ändern  

## 📄 Lizenz

MIT License - Für persönlichen Gebrauch. Siehe [LICENSE](LICENSE) für Details.

## 🤝 Contributing

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📧 Support

Bei Problemen bitte ein GitHub Issue erstellen mit:
- **Fehlermeldung** (vollständiger Stacktrace)
- **Python-Version:** `python3 --version`
- **yt-dlp Version:** `yt-dlp --version`
- **Verwendeter Befehl** (z.B. `python3 -m instagram_downloader liked`)
- **Log-Ausgabe** (aus `logs/` Verzeichnis)
- **Betriebssystem** (Ubuntu, macOS, etc.)

Siehe auch `QUICKSTART.md` und `INSTALLATION.md` für häufige Probleme.

## 🎯 Roadmap

- [ ] Parallele Downloads (ThreadPoolExecutor)
- [ ] GUI-Version (optional)
- [ ] Docker-Image
- [ ] Carousel-Posts (mehrere Medien pro Post)
- [ ] Stories-Support
- [ ] Filter nach Datum/Kategorie
- [ ] Automatische Deduplizierung

## ⭐ Changelog

### Version 2.0.0 (2026-01-29)

- ✨ Komplette Überarbeitung zu professionellem CLI-Tool
- ✨ Separate Ordner für saved/liked/own
- ✨ Konfigurationssystem (CLI/ENV/Config-File)
- ✨ Professionelles Logging mit Farben
- ✨ Retry-Mechanismus mit exponential backoff
- ✨ Setup.py für pip-Installation
- ✨ Umfassende Dokumentation
- ✨ Production-ready Code-Qualität

### Version 1.0.0

- Initiale Version mit grundlegenden Features

---

**Entwickelt mit ❤️ für Instagram-Sammler**
