"""
Konfigurationsmanagement für Instagram Media Downloader
"""

import configparser
import os
from pathlib import Path
from typing import Optional, Union, cast

from dotenv import load_dotenv


class Config:
    """Zentrale Konfigurationsklasse.

    Verwaltet das Laden und den Zugriff auf Anwendungseinstellungen
    aus Umgebungsvariablen, INI-Dateien und stellt Standardwerte bereit.
    """

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """
        Initialisiert die Konfiguration.

        Lädt Umgebungsvariablen aus der .env-Datei und initialisiert die
        Konfiguration mit Standardwerten, die durch Umgebungsvariablen
        und optional durch eine INI-Datei überschrieben werden können.

        Args:
            config_file: Optionaler Pfad zu einer zusätzlichen INI-Konfigurationsdatei.
        """
        load_dotenv()  # Lädt .env-Datei bei Initialisierung
        self.base_dir = Path(__file__).parent.parent.resolve()

        # Standard-Konfiguration
        self._defaults: dict[str, Union[str, int, float, bool]] = {
            "username": os.getenv("INSTAGRAM_USERNAME", "skymuss"),
            "data_dir": os.getenv("DATA_DIR", str(self.base_dir / "data")),
            "download_dir": os.getenv("DOWNLOAD_DIR", str(self.base_dir / "downloads")),
            "state_dir": os.getenv("STATE_DIR", str(self.base_dir / "state")),
            "request_delay": float(os.getenv("REQUEST_DELAY", "1.0")),
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("RETRY_DELAY", "5.0")),
            "timeout": int(os.getenv("TIMEOUT", "60")),
            "parallel_downloads": int(os.getenv("PARALLEL_DOWNLOADS", "1")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "csv_export": os.getenv("CSV_EXPORT", "true").lower() == "true",
        }

        # Config-Datei laden wenn vorhanden
        if config_file and config_file.exists():
            self._load_config_file(config_file)

    def _load_config_file(self, config_file: Path) -> None:
        """
        Lädt Konfigurationseinstellungen aus einer INI-Datei.

        Die Werte in der INI-Datei überschreiben die Standardwerte
        und Umgebungsvariablen.

        Args:
            config_file: Der Pfad zur INI-Konfigurationsdatei.
        """
        parser = configparser.ConfigParser()
        parser.read(config_file)

        if "DEFAULT" in parser:
            for key, value in parser["DEFAULT"].items():
                if key in self._defaults:
                    # Typ-Konvertierung basierend auf Standard-Wert
                    default_type = type(self._defaults[key])
                    if default_type is bool:
                        self._defaults[key] = value.lower() == "true"
                    elif default_type is int:
                        self._defaults[key] = int(value)
                    elif default_type is float:
                        self._defaults[key] = float(value)
                    else:
                        self._defaults[key] = value

    @property
    def username(self) -> str:
        """Der Instagram-Benutzername."""
        return cast(str, self._defaults["username"])

    @property
    def data_dir(self) -> Path:
        """Das Verzeichnis mit den Instagram-Exportdaten."""
        return Path(cast(str, self._defaults["data_dir"]))

    @property
    def download_dir(self) -> Path:
        """Das Zielverzeichnis für heruntergeladene Medien."""
        return Path(cast(str, self._defaults["download_dir"]))

    @property
    def state_dir(self) -> Path:
        """Das Verzeichnis für den Download-Status (Resume-Funktion)."""
        return Path(cast(str, self._defaults["state_dir"]))

    @property
    def request_delay(self) -> float:
        """Die Verzögerung zwischen HTTP-Anfragen in Sekunden."""
        return cast(float, self._defaults["request_delay"])

    @property
    def max_retries(self) -> int:
        """Die maximale Anzahl von Wiederholungsversuchen bei Fehlern."""
        return cast(int, self._defaults["max_retries"])

    @property
    def retry_delay(self) -> float:
        """Die Verzögerung zwischen Wiederholungsversuchen in Sekunden."""
        return cast(float, self._defaults["retry_delay"])

    @property
    def timeout(self) -> int:
        """Das Timeout für einzelne Download-Operationen in Sekunden."""
        return cast(int, self._defaults["timeout"])

    @property
    def parallel_downloads(self) -> int:
        """Die maximale Anzahl paralleler Downloads (aktuell 1)."""
        return cast(int, self._defaults["parallel_downloads"])

    @property
    def log_level(self) -> str:
        """Der konfigurierte Log-Level (z.B. 'INFO', 'DEBUG')."""
        return cast(str, self._defaults["log_level"])

    @property
    def csv_export(self) -> bool:
        """Gibt an, ob der CSV-Metadaten-Export aktiviert ist."""
        return cast(bool, self._defaults["csv_export"])

    def get_data_path(self, category: str) -> Path:
        """
        Gibt den vollständigen Pfad zur JSON-Datei für eine bestimmte Kategorie zurück.

        Args:
            category: Die Medienkategorie ('saved', 'liked' oder 'own').

        Returns:
            Path: Der vollständige Pfad zur JSON-Datendatei.

        Raises:
            ValueError: Wenn eine unbekannte Kategorie angegeben wird.
        """
        user_data_dir = self.data_dir / self.username

        if category == "saved":
            return user_data_dir / "saved" / "saved_posts.json"
        elif category == "liked":
            return user_data_dir / "likes" / "liked_posts.json"
        elif category == "own":
            return user_data_dir / "posts" / "posts.json"
        else:
            raise ValueError(f"Unbekannte Kategorie: {category}")

    def get_download_path(self, category: str) -> Path:
        """
        Gibt den vollständigen Download-Ordnerpfad für eine Kategorie zurück.

        Erstellt das Verzeichnis, falls es noch nicht existiert.

        Args:
            category: Die Medienkategorie ('saved', 'liked' oder 'own').

        Returns:
            Path: Der vollständige Pfad zum Download-Ordner.
        """
        download_path = self.download_dir / category
        download_path.mkdir(parents=True, exist_ok=True)
        return download_path

    def get_state_file(self, category: str) -> Path:
        """
        Gibt den Pfad zur State-Datei für eine Kategorie zurück.

        Die State-Datei speichert Informationen über bereits heruntergeladene Medien
        für die Resume-Funktionalität.
        Erstellt das State-Verzeichnis, falls es noch nicht existiert.

        Args:
            category: Die Medienkategorie ('saved', 'liked' oder 'own').

        Returns:
            Path: Der vollständige Pfad zur State-Datei.
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)
        return self.state_dir / f"{category}_downloaded.txt"

    def get_csv_file(self, category: str) -> Path:
        """
        Gibt den Pfad zu der CSV-Datei für eine Kategorie zurück.

        Args:
            category: Die Medienkategorie ('saved', 'liked' oder 'own').

        Returns:
            Path: Der vollständige Pfad zur CSV-Datei.
        """
        return self.base_dir / f"instagram_{category}_metadata.csv"
