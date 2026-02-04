"""
Download-Manager für Instagram-Medien
"""

import csv
import json
import logging
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm

from .config import Config


class MediaItem:
    """Repräsentiert ein einzelnes Instagram-Medium mit Metadaten.

    Attributes:
        source (str): Die Quelle des Mediums (z.B. 'saved', 'liked', 'own').
        title (str): Der Titel oder eine Beschreibung des Mediums.
        timestamp (int): Der Unix-Timestamp der Veröffentlichung oder Speicherung.
        url (str): Die URL des Instagram-Beitrags.
        filename (Optional[str]): Der lokale Dateiname nach dem Download. Defaults to None.
        media_type (Optional[str]): Der Medientyp (z.B. 'video', 'image'). Defaults to None.
    """

    def __init__(self, source: str, title: str, timestamp: int, url: str) -> None:
        """
        Initialisiert ein MediaItem-Objekt.

        Args:
            source: Die Quelle des Mediums.
            title: Der Titel des Mediums.
            timestamp: Der Unix-Timestamp.
            url: Die URL des Instagram-Beitrags.
        """
        self.source = source
        self.title = title
        self.timestamp = timestamp
        self.url = url
        self.filename: Optional[str] = None
        self.media_type: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """
        Konvertiert das MediaItem-Objekt in ein Dictionary für den CSV-Export.

        Returns:
            Dict[str, str]: Ein Dictionary, das die Mediendaten enthält.
        """
        return {
            "source": self.source,
            "title": self.title,
            "timestamp": str(self.timestamp),
            "datetime": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "url": self.url,
            "filename": self.filename or "",
            "media_type": self.media_type or "",
        }


class DownloadStats:
    """Tracking von Download-Statistiken für den Instagram Downloader.

    Attributes:
        success (int): Anzahl der erfolgreich heruntergeladenen Medien.
        failed (int): Anzahl der fehlgeschlagenen Downloads.
        skipped (int): Anzahl der übersprungenen Downloads (bereits vorhanden).
        total (int): Gesamtzahl der versuchten Downloads.
    """

    def __init__(self) -> None:
        """Initialisiert ein DownloadStats-Objekt mit allen Zählern auf Null."""
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0

    def increment_success(self) -> None:
        """Erhöht den Zähler für erfolgreiche Downloads um eins."""
        self.success += 1

    def increment_failed(self) -> None:
        """Erhöht den Zähler für fehlgeschlagene Downloads um eins."""
        self.failed += 1

    def increment_skipped(self) -> None:
        """Erhöht den Zähler für übersprungene Downloads um eins."""
        self.skipped += 1

    def set_total(self, total: int) -> None:
        """Setzt die Gesamtzahl der zu verarbeitenden Items."

        Args:
            total (int): Die Gesamtzahl der Items.
        """
        self.total = total

    def __str__(self) -> str:
        """Gibt eine lesbare Zusammenfassung der Statistiken zurück."""
        return (
            f"Total: {self.total} | "
            f"Erfolgreich: {self.success} | "
            f"Fehlgeschlagen: {self.failed} | "
            f"Übersprungen: {self.skipped}"
        )


class InstagramDownloader:
    """Hauptklasse für den Instagram Media Downloader.

    Verwaltet das Parsen von Instagram-Daten, den Download von Medien
    über yt-dlp, den Export von Metadaten und die Statusverfolgung.
    """

    MEDIA_CATEGORY_SAVED: str = "saved"
    MEDIA_CATEGORY_LIKED: str = "liked"
    MEDIA_CATEGORY_OWN: str = "own"

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialisiert den Downloader.

        Args:
            config: Eine Instanz der Konfigurationsklasse (`Config`).
            logger: Eine Instanz des Loggers (`logging.Logger`).
        """
        self.config = config
        self.logger = logger
        self.stats = DownloadStats()

    def check_ytdlp(self) -> bool:
        """
        Prüft, ob yt-dlp auf dem System verfügbar ist.

        Returns:
            bool: True, wenn yt-dlp gefunden wird, sonst False.
        """
        return shutil.which("yt-dlp") is not None

    def sanitize_filename(self, name: str) -> str:
        """
        Erzeugt einen gültigen und sicheren Dateinamen aus einem gegebenen String.

        Ungültige Zeichen für Dateinamen werden durch Unterstriche ersetzt.

        Args:
            name: Der ursprüngliche Dateiname oder Titel.

        Returns:
            str: Ein bereinigter Dateiname.
        """
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    def load_downloaded_state(self, state_file: Path) -> set[str]:
        """
        Lädt eine Liste von bereits heruntergeladenen URLs aus einer Datei.

        Args:
            state_file: Der Pfad zur State-Datei, die die URLs enthält.

        Returns:
            set[str]: Ein Set von URLs, die bereits heruntergeladen wurden.
        """
        if state_file.exists():
            with open(state_file, encoding="utf-8") as f:
                return {line.strip() for line in f if line.strip()}
        return set()

    def save_downloaded_state(self, state_file: Path, url: str) -> None:
        """
        Speichert eine heruntergeladene URL in der State-Datei.

        Args:
            state_file: Der Pfad zur State-Datei.
            url: Die URL, die als heruntergeladen markiert werden soll.
        """
        with open(state_file, "a", encoding="utf-8") as f:
            f.write(f"{url}\n")

    def download_with_ytdlp(
        self, url: str, output_template: str, max_retries: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Lädt ein Medium von Instagram mit yt-dlp herunter, inklusive Retry-Logik.

        Verwendet eine bewährte yt-dlp-Konfiguration für Instagram-Downloads.

        Args:
            url: Die Instagram-URL des Mediums.
            output_template: Das yt-dlp Ausgabe-Template für den Dateinamen.
            max_retries: Die maximale Anzahl von Wiederholungsversuchen. Wenn None,
                         wird der Wert aus der Konfiguration verwendet.

        Returns:
            Tuple[bool, Optional[str]]: Ein Tupel, das angibt, ob der Download erfolgreich war
                                         (True/False) und den Namen der heruntergeladenen Datei
                                         (oder None bei Fehler).
        """
        if max_retries is None:
            max_retries = self.config.max_retries

        for attempt in range(max_retries + 1):
            try:
                # yt-dlp Optionen (bewährte Konfiguration)
                cmd = [
                    "yt-dlp",
                    "--quiet",  # Weniger Ausgabe
                    "--no-warnings",
                    "--no-progress",
                    "-o",
                    output_template,
                    "--no-playlist",  # Nur einzelnes Video
                    "--format",
                    "best",  # Beste Qualität
                    url,
                ]

                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    check=True,  # Raise an exception if non-zero exit code
                )

                # Finde die heruntergeladene Datei
                # yt-dlp erstellt Dateien mit verschiedenen Endungen
                base_path = Path(output_template)
                parent_dir = base_path.parent
                name_pattern = base_path.stem

                # Suche nach möglichen Dateien (in dieser Reihenfolge)
                for ext in [".mp4", ".jpg", ".jpeg", ".png", ".webm", ".mkv"]:
                    potential_file = parent_dir / f"{name_pattern}{ext}"
                    if potential_file.exists():
                        return True, potential_file.name

                return False, None  # Fallback if file not found after successful download

            except subprocess.CalledProcessError as e:
                self.logger.error(
                    f"yt-dlp Fehler (Versuch {attempt + 1}/{max_retries + 1}): {e.stderr.strip()}"
                )
                if attempt < max_retries:
                    self.logger.warning(f"Warte {self.config.retry_delay}s vor erneutem Versuch...")
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
                self.logger.error(
                    f"Unerwarteter Fehler beim Download (Versuch {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None

        return False, None

    def parse_json_data(self, json_path: Path, category: str) -> List[MediaItem]:
        """
        Parst eine JSON-Datei und extrahiert Instagram-Mediendaten als MediaItem-Objekte.

        Args:
            json_path: Der Pfad zur JSON-Datei mit den Instagram-Exportdaten.
            category: Die Kategorie der Medien (z.B. 'saved', 'liked', 'own').

        Returns:
            List[MediaItem]: Eine Liste von `MediaItem`-Objekten, die die extrahierten Daten darstellen.
                             Gibt eine leere Liste zurück, wenn die Datei nicht existiert oder ein Fehler auftritt.
        """
        items: List[MediaItem] = []

        if not json_path.exists():
            self.logger.warning(f"JSON-Datei nicht gefunden: {json_path}")
            return items

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            if category == self.MEDIA_CATEGORY_SAVED:
                items = self._parse_saved_posts(data)
            elif category == self.MEDIA_CATEGORY_LIKED:
                items = self._parse_liked_posts(data)
            elif category == self.MEDIA_CATEGORY_OWN:
                items = self._parse_own_posts(data)
            else:
                self.logger.error(f"Unbekannte Medien-Kategorie: {category}")

            self.logger.info(f"Gefundene {category} Items: {len(items)}")

        except json.JSONDecodeError:
            self.logger.error(f"Ungültiges JSON-Format in Datei: {json_path}")
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von {json_path}: {e}")

        return items

    def _parse_saved_posts(self, data: Dict) -> List[MediaItem]:
        """
        Parst die JSON-Daten für 'saved_posts.json'.

        Extrahiert die relevanten Informationen für gespeicherte Posts.

        Args:
            data: Das geparste JSON-Objekt aus 'saved_posts.json'.

        Returns:
            List[MediaItem]: Eine Liste von `MediaItem`-Objekten für gespeicherte Posts.
        """
        items: List[MediaItem] = []
        try:
            for item in data.get("saved_saved_media", []):
                title = item.get("title", "untitled")
                saved_data = item["string_map_data"]["Saved on"]
                timestamp = saved_data["timestamp"]
                url = saved_data["href"]

                items.append(MediaItem(self.MEDIA_CATEGORY_SAVED, title, timestamp, url))
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von saved_posts: {e}")

        return items

    def _parse_liked_posts(self, data: Dict) -> List[MediaItem]:
        """
        Parst die JSON-Daten für 'liked_posts.json'.

        Extrahiert die relevanten Informationen für gelikte Posts.

        Args:
            data: Das geparste JSON-Objekt aus 'liked_posts.json'.

        Returns:
            List[MediaItem]: Eine Liste von `MediaItem`-Objekten für gelikte Posts.
        """
        items: List[MediaItem] = []
        try:
            for item in data.get("likes_media_likes", []):
                title = item.get("title", "untitled")
                if item.get("string_list_data") and len(item["string_list_data"]) > 0:
                    liked_data = item["string_list_data"][0]
                    timestamp = liked_data["timestamp"]
                    url = liked_data["href"]

                    items.append(MediaItem(self.MEDIA_CATEGORY_LIKED, title, timestamp, url))
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen von liked_posts: {e}")

        return items

    def _parse_own_posts(self, data: Dict) -> List[MediaItem]:
        """
        Parst die JSON-Daten für eigene Posts (z.B. 'posts.json').

        Extrahiert die relevanten Informationen für eigene Posts.

        Args:
            data: Das geparste JSON-Objekt aus 'posts.json'.

        Returns:
            List[MediaItem]: Eine Liste von `MediaItem`-Objekten für eigene Posts.
        """
        items: List[MediaItem] = []
        # TODO: Struktur anpassen basierend auf Instagram Export-Format
        for item in data.get("posts", []):
            title = item.get("title", "untitled")
            timestamp = item.get("creation_timestamp", 0)
            url = item.get("uri", "")

            if url:
                items.append(MediaItem(self.MEDIA_CATEGORY_OWN, title, timestamp, url))

        return items

    def export_to_csv(self, items: List[MediaItem], csv_file: Path) -> None:
        """
        Exportiert Metadaten einer Liste von MediaItems in eine CSV-Datei.

        Args:
            items: Eine Liste von `MediaItem`-Objekten, deren Metadaten exportiert werden sollen.
            csv_file: Der Pfad zur Ausgabedatei für den CSV-Export.
        """
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "source",
                    "title",
                    "timestamp",
                    "datetime",
                    "url",
                    "filename",
                    "media_type",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for item in items:
                    writer.writerow(item.to_dict())

            self.logger.info(f"CSV-Export gespeichert: {csv_file}")

        except Exception as e:
            self.logger.error(f"Fehler beim CSV-Export: {e}")

    def download_category(self, category: str) -> bool:
        """
        Lädt alle Medien einer bestimmten Kategorie herunter.

        Diese Methode parst die JSON-Daten für die angegebene Kategorie,
        filtert bereits heruntergeladene Medien heraus und initiiert den Download
        der verbleibenden Medien.

        Args:
            category: Die Medienkategorie (z.B. 'saved', 'liked', 'own').

        Returns:
            bool: True, wenn der Download-Prozess für die Kategorie erfolgreich abgeschlossen wurde
                  oder keine neuen Items zum Download vorhanden waren, sonst False.
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

        # Items nach Timestamp sortieren (neueste zuerst)
        items.sort(key=lambda x: x.timestamp, reverse=True)

        # State laden
        downloaded_urls = self.load_downloaded_state(state_file)
        self.logger.info(f"Bereits heruntergeladen: {len(downloaded_urls)}")

        # Filtern der Items, die noch heruntergeladen werden müssen
        items_to_download = [item for item in items if item.url not in downloaded_urls]
        self.logger.info(f"Verbleibende Items zum Download: {len(items_to_download)}")

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
                    item.media_type = (
                        "video"
                        if filename and filename.endswith((".mp4", ".webm", ".mkv"))
                        else "image"
                    )
                    self.save_downloaded_state(state_file, item.url)
                    self.stats.increment_success()
                else:
                    tqdm.write(f"❌ Fehlgeschlagen: {item.title[:50]}")
                    self.stats.increment_failed()

                # Delay
                time.sleep(self.config.request_delay)

            except KeyboardInterrupt:
                self.logger.warning("Download von Benutzer abgebrochen")
                raise  # Re-raise, damit CLI den Abbruch handhaben kann

            except Exception as e:
                self.logger.error(f"Fehler bei '{item.title[:50]}': {e}", exc_info=True)
                self.stats.increment_failed()

        # CSV-Export
        if self.config.csv_export:
            csv_file = self.config.get_csv_file(category)
            successful_items = [item for item in items if item.filename]
            self.export_to_csv(successful_items, csv_file)

        return True
