# 🚀 Installations-Anleitung

## Installation mit pip (empfohlen)

### Option 1: Virtual Environment (beste Praxis)

```bash
# 1. Virtual Environment erstellen
cd /home/skymuss/projects/instagram-media-downloader
python3 -m venv venv

# 2. Virtual Environment aktivieren
source venv/bin/activate

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Package installieren (Development Mode)
pip install -e .

# 5. Tool verwenden
instagram-downloader --help
```

### Option 2: System-weite Installation mit pipx (empfohlen für Tools)

```bash
# 1. pipx installieren (falls nicht vorhanden)
sudo apt update
sudo apt install pipx
pipx ensurepath

# 2. Tool installieren
pipx install -e /home/skymuss/projects/instagram-media-downloader

# 3. Tool verwenden
instagram-downloader --help
```

### Option 3: Direkte Ausführung ohne Installation

```bash
# 1. Dependencies installieren
cd /home/skymuss/projects/instagram-media-downloader
pip install --user tqdm

# 2. Tool als Modul ausführen
python3 -m instagram_downloader --help

# 3. Beispiel-Nutzung
python3 -m instagram_downloader liked
```

## yt-dlp installieren

```bash
# System-Paket (empfohlen)
sudo apt update
sudo apt install yt-dlp

# Oder via pip (in venv)
pip install yt-dlp

# Oder via pipx
pipx install yt-dlp
```

## Schnelltest

Nach der Installation:

```bash
# Hilfe anzeigen
instagram-downloader --help
# oder
python3 -m instagram_downloader --help

# Version prüfen
instagram-downloader --version
# oder
python3 -m instagram_downloader --version
```

## Troubleshooting

### "externally-managed-environment" Fehler

Wenn du den Fehler siehst:
```
error: externally-managed-environment
```

**Lösung 1 (empfohlen):** Nutze Virtual Environment (siehe Option 1)

**Lösung 2:** Nutze pipx (siehe Option 2)

**Lösung 3:** Nutze `--user` Flag:
```bash
pip install --user -e .
```

### "No module named 'tqdm'" Fehler

```bash
# In venv
pip install tqdm

# Ohne venv
pip install --user tqdm
```

### Berechtigungsprobleme

```bash
# Verwende --user für user-level Installation
pip install --user tqdm

# Oder nutze Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install tqdm
```
