"""
Logging-Konfiguration für Instagram Media Downloader
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatiert Log-Meldungen mit Farben für die Konsole"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Grün
        'WARNING': '\033[33m',    # Gelb
        'ERROR': '\033[31m',      # Rot
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Formatiert einen Log-Record mit Farben"""
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = "instagram_downloader", 
                 level: str = "INFO",
                 log_file: Optional[Path] = None,
                 console: bool = True) -> logging.Logger:
    """
    Richtet einen Logger mit Datei- und/oder Konsolen-Handler ein
    
    Args:
        name: Name des Loggers
        level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional - Pfad zur Log-Datei
        console: Ob Console-Logging aktiviert werden soll
        
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Entferne existierende Handler
    logger.handlers.clear()
    
    # Format für Log-Nachrichten
    log_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
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
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Datei bekommt immer alle Logs
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_log_file_path(base_dir: Path, category: Optional[str] = None) -> Path:
    """
    Erstellt einen Pfad für eine Log-Datei mit Zeitstempel
    
    Args:
        base_dir: Basis-Verzeichnis für Logs
        category: Optional - Kategorie (saved, liked, own)
        
    Returns:
        Path zur Log-Datei
    """
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if category:
        log_filename = f"instagram_downloader_{category}_{timestamp}.log"
    else:
        log_filename = f"instagram_downloader_{timestamp}.log"
    
    return logs_dir / log_filename
