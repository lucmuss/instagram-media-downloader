#!/usr/bin/env python3
"""
Instagram Media Downloader (yt-dlp Version)
============================================
Lädt alle gespeicherten Posts und Likes von Instagram herunter.
- Verwendet yt-dlp für zuverlässige Instagram-Downloads
- Speichert alle Dateien in einem flachen Ordner
- Zeigt Fortschrittsbalken während des Downloads
- Resume-Funktion: überspringt bereits heruntergeladene Dateien
- Exportiert Metadaten in CSV
"""

import json
import subprocess
from pathlib import Path
from tqdm import tqdm
import time
import csv
from datetime import datetime
import sys
import shutil

# ===== KONFIGURATION =====

# Was soll heruntergeladen werden?
DOWNLOAD_SAVED = False   # Gespeicherte Posts herunterladen
DOWNLOAD_LIKED = True   # Gelikte Posts herunterladen

# Pfade
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data" / "skymuss"
SAVED_POSTS_JSON = DATA_DIR / "saved" / "saved_posts.json"
LIKED_POSTS_JSON = DATA_DIR / "likes" / "liked_posts.json"
DOWNLOAD_DIR = BASE_DIR / "downloads" / "likes"
STATE_DIR = BASE_DIR / "state"
CSV_FILE = BASE_DIR / "instagram_metadata.csv"

# Verzeichnisse erstellen
DOWNLOAD_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

# State-Tracking-Datei
DOWNLOADED_STATE_FILE = STATE_DIR / "downloaded.txt"

# Delay zwischen Downloads
REQUEST_DELAY = 1.0  # Sekunden


# ===== HILFSFUNKTIONEN =====

def check_ytdlp():
    """Prüft ob yt-dlp installiert ist"""
    return shutil.which("yt-dlp") is not None


def sanitize_filename(name):
    """Erstellt einen gültigen Dateinamen"""
    import re
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def load_downloaded_state():
    """Lädt bereits heruntergeladene URLs aus State-Datei"""
    if DOWNLOADED_STATE_FILE.exists():
        with open(DOWNLOADED_STATE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_downloaded_state(url):
    """Speichert heruntergeladene URL in State-Datei"""
    with open(DOWNLOADED_STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")


def download_with_ytdlp(url, output_template):
    """
    Lädt Medien mit yt-dlp herunter
    Returns: (success, filename) oder (False, None)
    """
    try:
        # yt-dlp Optionen
        cmd = [
            "yt-dlp",
            "--quiet",  # Weniger Ausgabe
            "--no-warnings",
            "--no-progress",
            "-o", output_template,
            "--no-playlist",  # Nur einzelnes Video
            "--format", "best",  # Beste Qualität
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Finde die heruntergeladene Datei
            # yt-dlp erstellt Dateien mit verschiedenen Endungen
            base_path = Path(output_template)
            parent_dir = base_path.parent
            name_pattern = base_path.stem
            
            # Suche nach möglichen Dateien
            for ext in ['.mp4', '.jpg', '.jpeg', '.png', '.webm', '.mkv']:
                potential_file = parent_dir / f"{name_pattern}{ext}"
                if potential_file.exists():
                    return True, potential_file.name
            
            return False, None
        else:
            return False, None
    
    except subprocess.TimeoutExpired:
        return False, None
    except Exception as e:
        return False, None


def parse_saved_posts(json_path):
    """Lädt und parst saved_posts.json"""
    items = []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for item in data.get("saved_saved_media", []):
            title = item.get("title", "untitled")
            saved_data = item["string_map_data"]["Saved on"]
            timestamp = saved_data["timestamp"]
            url = saved_data["href"]
            
            items.append({
                "source": "saved",
                "title": title,
                "timestamp": timestamp,
                "url": url
            })
    except Exception as e:
        print(f"❌ Fehler beim Laden von saved_posts.json: {e}")
    
    return items


def parse_liked_posts(json_path):
    """Lädt und parst liked_posts.json"""
    items = []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for item in data.get("likes_media_likes", []):
            title = item.get("title", "untitled")
            if item.get("string_list_data") and len(item["string_list_data"]) > 0:
                liked_data = item["string_list_data"][0]
                timestamp = liked_data["timestamp"]
                url = liked_data["href"]
                
                items.append({
                    "source": "liked",
                    "title": title,
                    "timestamp": timestamp,
                    "url": url
                })
    except Exception as e:
        print(f"❌ Fehler beim Laden von liked_posts.json: {e}")
    
    return items


def write_csv_metadata(metadata_list):
    """Schreibt Metadaten in CSV-Datei"""
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "source", "title", "timestamp", "datetime", "url", 
                "filename", "media_type"
            ])
            writer.writeheader()
            writer.writerows(metadata_list)
        print(f"📊 Metadaten gespeichert: {CSV_FILE}")
    except Exception as e:
        print(f"⚠️ Fehler beim CSV-Export: {e}")


# ===== HAUPTFUNKTION =====

def main():
    print("=" * 70)
    print("🎯 INSTAGRAM MEDIA DOWNLOADER (yt-dlp)")
    print("=" * 70)
    
    # yt-dlp Check
    if not check_ytdlp():
        print("\n❌ FEHLER: yt-dlp ist nicht installiert!")
        print("\n📦 Installation:")
        print("   sudo apt install yt-dlp")
        print("   # oder")
        print("   pip install yt-dlp")
        print("\n💡 Danach Skript erneut ausführen.")
        sys.exit(1)
    
    print("✅ yt-dlp gefunden\n")
    
    # Konfiguration anzeigen
    print("⚙️ Konfiguration:")
    print(f"   • Gespeicherte Posts: {'✅ JA' if DOWNLOAD_SAVED else '❌ NEIN'}")
    print(f"   • Gelikte Posts:      {'✅ JA' if DOWNLOAD_LIKED else '❌ NEIN'}")
    print()
    
    # JSON-Dateien laden (basierend auf Konfiguration)
    print("📂 Lade JSON-Daten...")
    saved_items = []
    liked_items = []
    
    if DOWNLOAD_SAVED and SAVED_POSTS_JSON.exists():
        saved_items = parse_saved_posts(SAVED_POSTS_JSON)
        print(f"📦 Gespeicherte Posts: {len(saved_items)}")
    elif DOWNLOAD_SAVED:
        print(f"⚠️ Gespeicherte Posts: Datei nicht gefunden")
    
    if DOWNLOAD_LIKED and LIKED_POSTS_JSON.exists():
        liked_items = parse_liked_posts(LIKED_POSTS_JSON)
        print(f"❤️ Gelikte Posts: {len(liked_items)}")
    elif DOWNLOAD_LIKED:
        print(f"⚠️ Gelikte Posts: Datei nicht gefunden")
    
    # Alle Items kombinieren und nach Timestamp sortieren
    all_items = saved_items + liked_items
    
    if not all_items:
        print("\n❌ Keine Daten zum Herunterladen gefunden!")
        print("💡 Prüfe die Konfiguration (DOWNLOAD_SAVED / DOWNLOAD_LIKED)")
        return
    
    all_items.sort(key=lambda x: x["timestamp"], reverse=True)
    print(f"📊 Gesamt Einträge: {len(all_items)}")
    
    # Bereits heruntergeladene URLs laden
    downloaded_urls = load_downloaded_state()
    print(f"✅ Bereits heruntergeladen: {len(downloaded_urls)}")
    
    # Filtern: nur noch nicht heruntergeladene Items
    items_to_download = [item for item in all_items if item["url"] not in downloaded_urls]
    print(f"⏬ Zu laden: {len(items_to_download)}")
    
    if not items_to_download:
        print("\n✅ Alle Medien bereits heruntergeladen!")
        return
    
    # Metadaten für CSV sammeln
    metadata_list = []
    
    # Download-Schleife
    stats = {"success": 0, "skipped": 0, "failed": 0}
    
    print(f"\n🚀 Starte Download ({len(items_to_download)} Dateien)...\n")
    print("⚠️ HINWEIS: Instagram könnte Login erfordern für private Inhalte")
    print("⚠️ Einige Downloads können fehlschlagen (gelöschte Posts, private Accounts)\n")
    
    for item in tqdm(items_to_download, desc="⬇️ Download", unit="file"):
        try:
            title = item["title"]
            timestamp = item["timestamp"]
            url = item["url"]
            source = item["source"]
            
            # Dateinamen vorbereiten (ohne Endung, yt-dlp fügt sie hinzu)
            filename_base = f"{timestamp}_{sanitize_filename(title)}"
            output_template = str(DOWNLOAD_DIR / filename_base) + ".%(ext)s"
            
            # Mit yt-dlp herunterladen
            success, filename = download_with_ytdlp(url, output_template)
            
            if success:
                # Erfolg! State speichern
                save_downloaded_state(url)
                stats["success"] += 1
                
                # Medientyp ermitteln
                media_type = "video" if filename.endswith(('.mp4', '.webm', '.mkv')) else "image"
                
                # Metadaten für CSV speichern
                metadata_list.append({
                    "source": source,
                    "title": title,
                    "timestamp": timestamp,
                    "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "url": url,
                    "filename": filename,
                    "media_type": media_type
                })
            else:
                tqdm.write(f"❌ Download fehlgeschlagen: {title[:50]}")
                stats["failed"] += 1
            
            # Kleine Pause
            time.sleep(REQUEST_DELAY)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Download von Benutzer abgebrochen!")
            print("💡 Resume möglich: einfach Skript neu starten")
            sys.exit(0)
        
        except Exception as e:
            tqdm.write(f"❌ Fehler bei '{title[:50]}': {e}")
            stats["failed"] += 1
    
    # CSV-Export
    if metadata_list:
        write_csv_metadata(metadata_list)
    
    # Abschlussstatistik
    print("\n" + "=" * 70)
    print("📊 DOWNLOAD ABGESCHLOSSEN")
    print("=" * 70)
    print(f"✅ Erfolgreich:   {stats['success']}")
    print(f"⏭️ Übersprungen:  {stats['skipped']}")
    print(f"❌ Fehlgeschlagen: {stats['failed']}")
    print(f"📁 Speicherort:   {DOWNLOAD_DIR}")
    print(f"📊 CSV-Metadaten: {CSV_FILE}")
    print("=" * 70)
    
    if stats["failed"] > 0:
        print("\n💡 TIPPS bei Fehlschlägen:")
        print("   • Gelöschte Posts können nicht heruntergeladen werden")
        print("   • Private Accounts benötigen evtl. Login-Cookies")
        print("   • Instagram-Rate-Limits: Später erneut versuchen")


if __name__ == "__main__":
    main()
