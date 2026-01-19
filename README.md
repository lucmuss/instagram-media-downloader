# 📥 Instagram Media Downloader

Ein robustes Python-Skript zum Herunterladen aller **gespeicherten Posts** und **Likes** aus deinem Instagram-Datenexport.

## ✨ Funktionen

✅ **Automatische Medien-Extraktion** - Lädt echte MP4/JPG-Dateien (keine HTML-Seiten)  
✅ **Flacher Ordner** - Alle Medien in einem Verzeichnis (`downloads/`)  
✅ **Fortschrittsbalken** - Zeigt Download-Fortschritt mit `tqdm`  
✅ **Resume-Funktion** - Startet bei Unterbrechung automatisch fort  
✅ **CSV-Export** - Metadaten (Titel, Datum, URLs) in übersichtlicher Tabelle  
✅ **Duplikat-Schutz** - Bereits vorhandene Dateien werden übersprungen  
✅ **Robuste Fehlerbehandlung** - Fehlgeschlagene Downloads blockieren nicht den Prozess  

## 📋 Voraussetzungen

### Python-Pakete installieren

```bash
pip install requests beautifulsoup4 tqdm
```

**Benötigte Pakete:**
- `requests` - HTTP-Requests
- `beautifulsoup4` - HTML-Parsing
- `tqdm` - Fortschrittsbalken

## 🚀 Verwendung

### 1. Instagram-Datenexport vorbereiten

Stelle sicher, dass deine Instagram-JSON-Dateien hier liegen:
```
data/skymuss/saved/saved_posts.json
data/skymuss/likes/liked_posts.json
```

### 2. Skript ausführen

```bash
python instagram_downloader.py
```

### 3. Download-Prozess

Das Skript:
1. Lädt beide JSON-Dateien
2. Kombiniert alle Posts (Saved + Liked)
3. Prüft, welche bereits heruntergeladen wurden
4. Lädt fehlende Medien mit Fortschrittsbalken
5. Speichert Metadaten in CSV

### 4. Bei Unterbrechung fortsetzen

Einfach Skript erneut starten! Die Resume-Funktion überspringt automatisch alle bereits heruntergeladenen Dateien.

```bash
python instagram_downloader.py  # Fährt automatisch fort!
```

## 📁 Verzeichnisstruktur

```
instagram-export/
├── instagram_downloader.py          # Hauptskript
├── README.md                         # Diese Datei
├── requirements.txt                  # Python-Dependencies
├── data/
│   └── skymuss/
│       ├── saved/
│       │   └── saved_posts.json     # Gespeicherte Posts
│       └── likes/
│           └── liked_posts.json     # Gelikte Posts
├── downloads/                        # 📥 Heruntergeladene Medien
│   ├── 1766401968_tha_truth_7.31.mp4
│   ├── 1766401009_focus_szn_.mp4
│   └── ...
├── state/
│   └── downloaded.txt               # Tracking (für Resume)
└── instagram_metadata.csv           # 📊 Metadaten-Export
```

## 📊 CSV-Metadaten

Die generierte `instagram_metadata.csv` enthält:

| Spalte      | Beschreibung                        |
|-------------|-------------------------------------|
| `source`    | "saved" oder "liked"               |
| `title`     | Instagram-Username des Erstellers  |
| `timestamp` | Unix-Timestamp                     |
| `datetime`  | Lesbare Datumszeit                 |
| `url`       | Original Instagram-URL             |
| `filename`  | Lokaler Dateiname                  |
| `media_type`| "video" oder "image"               |

## 🎯 Dateinamen-Format

Alle Dateien folgen diesem Schema:
```
{timestamp}_{username}.{ext}

Beispiele:
- 1766401968_tha_truth_7.31.mp4
- 1765495433_thebrainmaze.jpg
```

## ⚙️ Konfiguration

Du kannst im Skript folgendes anpassen:

```python
# Delay zwischen Requests (Zeile 42)
REQUEST_DELAY = 0.8  # Sekunden (erhöhen bei Rate-Limits)

# Download-Verzeichnis (Zeile 29)
DOWNLOAD_DIR = BASE_DIR / "downloads"
```

## 🔧 Fehlerbehebung

### Instagram blockiert Zugriffe

**Problem:** Zu viele Requests zu schnell  
**Lösung:** `REQUEST_DELAY` auf 1.5-2 Sekunden erhöhen

### "Keine Medien-URL gefunden"

**Ursachen:**
- Post wurde gelöscht
- Privater Account
- Instagram hat HTML-Struktur geändert

**Lösung:** Diese Posts werden übersprungen (siehe Log)

### Bestimmte Dateien re-downloaden

1. Datei aus `downloads/` löschen
2. URL aus `state/downloaded.txt` entfernen
3. Skript neu starten

## 📈 Statistiken

Nach Abschluss siehst du:
```
📊 DOWNLOAD ABGESCHLOSSEN
======================================================================
✅ Erfolgreich:   150
⏭️ Übersprungen:  20
❌ Fehlgeschlagen: 5
📁 Speicherort:   /home/skymuss/projects/instagram-export/downloads
📊 CSV-Metadaten: /home/skymuss/projects/instagram-export/instagram_metadata.csv
======================================================================
```

## ⚡ Performance-Tipps

1. **Paralleler Download** (aktuell nicht implementiert) - Könnte beschleunigen
2. **Caching** - `state/downloaded.txt` nie löschen!
3. **Netzwerk** - Stabile Internetverbindung verwenden

## 🛡️ Wichtige Hinweise

⚠️ **Instagram Terms of Service** - Stelle sicher, dass du nur deine eigenen Daten herunterlädst  
⚠️ **Rate Limits** - Bei zu vielen Requests kann Instagram temporär blockieren  
⚠️ **Datenschutz** - Die heruntergeladenen Daten sind deine persönlichen Exporte  

## 📝 To-Do / Erweiterungen

- [ ] Paralleles Herunterladen (mit ThreadPoolExecutor)
- [ ] Carousel-Posts (mehrere Bilder pro Post)
- [ ] Bessere Fehlerbehandlung für gelöschte Posts
- [ ] Automatisches Retry bei Netzwerkfehlern
- [ ] GUI-Version (optional)

## 🐛 Bugs melden

Bei Problemen bitte Issue erstellen mit:
- Fehlermeldung
- Python-Version (`python --version`)
- Beispiel-URL (ohne persönliche Daten)

## 📄 Lizenz

Für persönlichen Gebrauch. Kein Support für kommerziellen Einsatz.

---

**Entwickelt mit ❤️ für deine Instagram-Sammlung**
