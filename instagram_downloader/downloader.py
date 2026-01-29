"""
Download-Manager für Instagram-Medien
"""

import json
import subprocess
import time
import csv
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from tqdm import tqdm
import logging


class MediaItem:
    """Repräsentiert ein einzelnes Instagram-Medium"""
    
    def __init__(self, source: str, title: str, timestamp: int, url: str):
        self.source = source
        self.title = title
        self.timestamp = timestamp
        self.url = url
        self.filename: Optional[str] = None
        self.media_type: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für CSV-Export"""
        return {
            'source': self.source,
            'title': self.title,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            'url': self.url,
            'filename': self.filename or '',
            'media_type': self.media_type or ''
        }


class DownloadStats:
    """Tracking von Download-Statistiken"""
    
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
    
    def increment_success(self):
        self.success += 1
    
    def increment_failed(self):
        self.failed += 1
    
    def increment_skipped(self):
        self.skipped += 1
    
    def set_total(self, total: int):
        self.total = total
    
    def __str__(self) -> str:
        return (f"Total: {self.total} | "
                f"Erfolgreich: {self.success} | "
                f"Fehlgeschlagen: {self.failed} | "
                f"Übersprungen: {self.skipped}")


class InstagramDownloader:
    """Hauptklasse für Instagram-Downloads"""
    
    def __init__(self, config, logger: logging.Logger):
        """
        Initialisiert den Downloader
        
        Args:
            config: Config-Objekt
            logger: Logger-Instanz
        """
        self.config = config
        self.logger = logger
        self.stats = DownloadStats()
    
    def check_ytdlp(self) -> bool:
        """Prüft ob yt-dlp verfügbar ist"""
        import shutil
        return shutil.which("yt-dlp") is not None
    
    def sanitize_filename(self, name: str) -> str:
        """Erstellt einen gültigen Dateinamen"""
        return re.sub(r'[\\/*?:"<>|]', "_", name)
    
    def load_downloaded_state(self, state_file: Path) -> set:
        """Lädt bereits heruntergeladene URLs"""
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def save_downloaded_state(self, state_file: Path, url: str):
        """Speichert heruntergeladene URL"""
        with open(state_file, "a", encoding="utf-8") as f:
            f.write(f"{url}\n")
    
    def download_with_ytdlp(self, url: str, output_template: str, 
                           max_retries: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Lädt Medium mit yt-dlp herunter (mit Retry-Logik)
        BEWÄHRTE IMPLEMENTATION von instagram_downloader_ytdlp.py
        
        Args:
            url: Instagram-URL
            output_template: Ausgabe-Template für yt-dlp
            max_retries: Maximale Anzahl von Wiederholungsversuchen
            
        Returns:
            (success, filename) Tuple
        """
        if max_retries is None:
            max_retries = self.config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # yt-dlp Optionen (bewährte Konfiguration)
                cmd = [
                    "yt-dlp",
                    "--quiet",          # Weniger Ausgabe
                    "--no-warnings",
                    "--no-progress",
                    "-o", output_template,
                    "--no-playlist",    # Nur einzelnes Video
                    "--format", "best", # Beste Qualität
                    url
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=self.config.timeout
                )
                
                if result.returncode == 0:
                    # Finde die heruntergeladene Datei
                    # yt-dlp erstellt Dateien mit verschiedenen Endungen
                    base_path = Path(output_template)
                    parent_dir = base_path.parent
                    name_pattern = base_path.stem
                    
                    # Suche nach möglichen Dateien (in dieser Reihenfolge)
                    for ext in ['.mp4', '.jpg', '.jpeg', '.png', '.webm', '.mkv']:
                        potential_file = parent_dir / f"{name_pattern}{ext}"
                        if potential_file.exists():
                            return True, potential_file.name
                    
                    return False, None
                else:
                    if attempt < max_retries:
                        self.logger.warning(f"Versuch {attempt + 1}/{max_retries + 1} fehlgeschlagen, warte {self.config.retry_delay}s...")
                        time.sleep(self.config.retry_delay)
                    else:
                        return False, None
            
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout bei Versuch {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None
            
            except Exception as e:
                self.logger.error(f"Fehler beim Download: {e}")
                if attempt < max_retries:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None
        
        return False, None
    
    def parse_json_data(self, json_path: Path, category: str) -> List[MediaItem]:
        """
        Parst JSON-Datei und extrahiert MediaItems
        
        Args:
            json_path: Pfad zur JSON-Datei
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            Liste von MediaItem-Objekten
        """
        items = []
        
        if not json_path.exists():
            self.logger.warning(f"JSON-Datei nicht gefunden: {json_path}")
            return items
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if category == 'saved':
                items = self._parse_saved_posts(data)
            elif category == 'liked':
                items = self._parse_liked_posts(data)
            elif category == 'own':
                items = self._parse_own_posts(data)
            
            self.logger.info(f"Gefundene {category} Items: {len(items)}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von {json_path}: {e}")
        
        return items
    
    def _parse_saved_posts(self, data: Dict) -> List[MediaItem]:
        """
        Parst saved_posts.json
        BEWÄHRTE IMPLEMENTATION von instagram_downloader_ytdlp.py
        """
        items = []
        try:
            for item in data.get("saved_saved_media", []):
                title = item.get("title", "untitled")
                saved_data = item["string_map_data"]["Saved on"]
                timestamp = saved_data["timestamp"]
                url = saved_data["href"]
                
                items.append(MediaItem("saved", title, timestamp, url))
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von saved_posts: {e}")
        
        return items
    
    def _parse_liked_posts(self, data: Dict) -> List[MediaItem]:
        """
        Parst liked_posts.json
        BEWÄHRTE IMPLEMENTATION von instagram_downloader_ytdlp.py
        """
        items = []
        try:
            for item in data.get("likes_media_likes", []):
                title = item.get("title", "untitled")
                if item.get("string_list_data") and len(item["string_list_data"]) > 0:
                    liked_data = item["string_list_data"][0]
                    timestamp = liked_data["timestamp"]
                    url = liked_data["href"]
                    
                    items.append(MediaItem("liked", title, timestamp, url))
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von liked_posts: {e}")
        
        return items
    
    def _parse_own_posts(self, data: Dict) -> List[MediaItem]:
        """Parst eigene Posts (posts.json)"""
        items = []
        # TODO: Struktur anpassen basierend auf Instagram Export-Format
        for item in data.get("posts", []):
            title = item.get("title", "untitled")
            timestamp = item.get("creation_timestamp", 0)
            url = item.get("uri", "")
            
            if url:
                items.append(MediaItem("own", title, timestamp, url))
        
        return items
    
    def export_to_csv(self, items: List[MediaItem], csv_file: Path):
        """
        Exportiert Metadaten zu CSV
        
        Args:
            items: Liste von MediaItems
            csv_file: Pfad zur CSV-Datei
        """
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = ['source', 'title', 'timestamp', 'datetime', 'url', 'filename', 'media_type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in items:
                    writer.writerow(item.to_dict())
            
            self.logger.info(f"CSV-Export gespeichert: {csv_file}")
        
        except Exception as e:
            self.logger.error(f"Fehler beim CSV-Export: {e}")
    
    def download_category(self, category: str) -> bool:
        """
        Lädt alle Medien einer Kategorie herunter
        
        Args:
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            True wenn erfolgreich
        """
        self.logger.info(f"Starte Download für Kategorie: {category}")
        
        # Pfade abrufen
        json_path = self.config.get_data_path(category)
        download_dir = self.config.get_download_path(category)
        state_file = self.config.get_state_file(category)
        
        # JSON parsen
        items = self.parse_json_data(json_path, category)
        
        if not items:
            self.logger.warning(f"Keine Items für {category} gefunden")
            return False
        
        # Items nach Timestamp sortieren
        items.sort(key=lambda x: x.timestamp, reverse=True)
        
        # State laden
        downloaded_urls = self.load_downloaded_state(state_file)
        self.logger.info(f"Bereits heruntergeladen: {len(downloaded_urls)}")
        
        # Filtern
        items_to_download = [item for item in items if item.url not in downloaded_urls]
        self.logger.info(f"Zu downloadende Items: {len(items_to_download)}")
        
        if not items_to_download:
            self.logger.info("Alle Items bereits heruntergeladen!")
            return True
        
        # Download
        self.stats.set_total(len(items_to_download))
        
        for item in tqdm(items_to_download, desc=f"⬇️ {category.capitalize()}", unit="file"):
            try:
                # Dateinamen erstellen
                filename_base = f"{item.timestamp}_{self.sanitize_filename(item.title)}"
                output_template = str(download_dir / filename_base) + ".%(ext)s"
                
                # Download
                success, filename = self.download_with_ytdlp(item.url, output_template)
                
                if success:
                    item.filename = filename
                    item.media_type = "video" if filename.endswith(('.mp4', '.webm', '.mkv')) else "image"
                    self.save_downloaded_state(state_file, item.url)
                    self.stats.increment_success()
                else:
                    tqdm.write(f"❌ Fehlgeschlagen: {item.title[:50]}")
                    self.stats.increment_failed()
                
                # Delay
                time.sleep(self.config.request_delay)
            
            except KeyboardInterrupt:
                self.logger.warning("Download von Benutzer abgebrochen")
                raise
            
            except Exception as e:
                self.logger.error(f"Fehler bei '{item.title[:50]}': {e}")
                self.stats.increment_failed()
        
        # CSV-Export
        if self.config.csv_export:
            csv_file = self.config.get_csv_file(category)
            successful_items = [item for item in items if item.filename]
            self.export_to_csv(successful_items, csv_file)
        
        return True
