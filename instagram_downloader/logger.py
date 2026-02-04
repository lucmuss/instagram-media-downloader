"""
Logging-Konfiguration für Instagram Media Downloader
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatiert Log-Meldungen mit Farben für die Konsole.

    Fügt Farbcodes basierend auf dem Log-Level hinzu, um die Lesbarkeit
    von Konsolen-Ausgaben zu verbessern.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Grün
        "WARNING": "\033[33m",  # Gelb
        "ERROR": "\033[31m",  # Rot
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formatiert einen Log-Record mit Farben.

        Args:
            record: Der zu formatierende Log-Record.

        Returns:
            str: Die farbig formatierte Log-Meldung.
        """
        if record.levelname in self.COLORS:
            color_code = self.COLORS[record.levelname]
            reset_code = self.COLORS["RESET"]
            record.levelname = f"{color_code}{record.levelname}{reset_code}"
        return super().format(record)


def setup_logger(
    name: str = "instagram_downloader",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
) -> logging.Logger:
    """
    Richtet einen Logger mit optionalem Datei- und Konsolen-Handler ein.

    Args:
        name: Der Name des Loggers. Defaults to "instagram_downloader".
        level: Das minimale Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to "INFO".
        log_file: Optionaler Pfad zu einer Log-Datei, in die geschrieben werden soll.
                  Wenn None, wird keine Datei geloggt.
        console: Steuert, ob Logs auf der Konsole ausgegeben werden sollen.
                 Defaults to True.

    Returns:
        logging.Logger: Der konfigurierte Logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Entferne existierende Handler, um Doppelungen bei erneuter Konfiguration zu vermeiden
    logger.handlers.clear()

    # Format für Log-Nachrichten gemäß CLINE-Regeln
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Console Handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = ColoredFormatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        # Die Log-Datei bekommt immer alle DEBUG Logs
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_log_file_path(base_dir: Path, category: Optional[str] = None) -> Path:
    """
    Generiert einen einzigartigen Dateipfad für eine Log-Datei mit Zeitstempel.

    Das Verzeichnis `logs` wird im `base_dir` erstellt, falls es nicht existiert.

    Args:
        base_dir: Das Basisverzeichnis, in dem der `logs`-Ordner erstellt wird.
        category: Optional. Eine Kategorie zur Benennung der Log-Datei (z.B. 'saved',
                  'liked', 'own'). Wird dem Dateinamen vorangestellt.

    Returns:
        Path: Der vollständige Pfad zur generierten Log-Datei.
    """
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if category:
        log_filename = f"instagram_downloader_{category}_{timestamp}.log"
    else:
        log_filename = f"instagram_downloader_{timestamp}.log"

    return logs_dir / log_filename
