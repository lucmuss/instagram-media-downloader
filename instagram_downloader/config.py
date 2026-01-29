"""
Konfigurationsmanagement für Instagram Media Downloader
"""

import os
from pathlib import Path
from typing import Optional
import configparser


class Config:
    """Zentrale Konfigurationsklasse"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialisiert die Konfiguration
        
        Args:
            config_file: Optionaler Pfad zur Konfigurationsdatei
        """
        self.base_dir = Path(__file__).parent.parent.resolve()
        
        # Standard-Konfiguration
        self._defaults = {
            'username': os.getenv('INSTAGRAM_USERNAME', 'skymuss'),
            'data_dir': os.getenv('DATA_DIR', str(self.base_dir / 'data')),
            'download_dir': os.getenv('DOWNLOAD_DIR', str(self.base_dir / 'downloads')),
            'state_dir': os.getenv('STATE_DIR', str(self.base_dir / 'state')),
            'request_delay': float(os.getenv('REQUEST_DELAY', '1.0')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'retry_delay': float(os.getenv('RETRY_DELAY', '5.0')),
            'timeout': int(os.getenv('TIMEOUT', '60')),
            'parallel_downloads': int(os.getenv('PARALLEL_DOWNLOADS', '1')),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'csv_export': os.getenv('CSV_EXPORT', 'true').lower() == 'true',
        }
        
        # Config-Datei laden wenn vorhanden
        if config_file and config_file.exists():
            self._load_config_file(config_file)
    
    def _load_config_file(self, config_file: Path):
        """Lädt Konfiguration aus INI-Datei"""
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        if 'DEFAULT' in parser:
            for key, value in parser['DEFAULT'].items():
                if key in self._defaults:
                    # Typ-Konvertierung basierend auf Standard-Wert
                    default_type = type(self._defaults[key])
                    if default_type == bool:
                        self._defaults[key] = value.lower() == 'true'
                    elif default_type == int:
                        self._defaults[key] = int(value)
                    elif default_type == float:
                        self._defaults[key] = float(value)
                    else:
                        self._defaults[key] = value
    
    @property
    def username(self) -> str:
        return self._defaults['username']
    
    @property
    def data_dir(self) -> Path:
        return Path(self._defaults['data_dir'])
    
    @property
    def download_dir(self) -> Path:
        return Path(self._defaults['download_dir'])
    
    @property
    def state_dir(self) -> Path:
        return Path(self._defaults['state_dir'])
    
    @property
    def request_delay(self) -> float:
        return self._defaults['request_delay']
    
    @property
    def max_retries(self) -> int:
        return self._defaults['max_retries']
    
    @property
    def retry_delay(self) -> float:
        return self._defaults['retry_delay']
    
    @property
    def timeout(self) -> int:
        return self._defaults['timeout']
    
    @property
    def parallel_downloads(self) -> int:
        return self._defaults['parallel_downloads']
    
    @property
    def log_level(self) -> str:
        return self._defaults['log_level']
    
    @property
    def csv_export(self) -> bool:
        return self._defaults['csv_export']
    
    def get_data_path(self, category: str) -> Path:
        """
        Gibt den Pfad für eine bestimmte Kategorie zurück
        
        Args:
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            Path zur JSON-Datei
        """
        user_data_dir = self.data_dir / self.username
        
        if category == 'saved':
            return user_data_dir / 'saved' / 'saved_posts.json'
        elif category == 'liked':
            return user_data_dir / 'likes' / 'liked_posts.json'
        elif category == 'own':
            return user_data_dir / 'posts' / 'posts.json'
        else:
            raise ValueError(f"Unbekannte Kategorie: {category}")
    
    def get_download_path(self, category: str) -> Path:
        """
        Gibt den Download-Ordner für eine Kategorie zurück
        
        Args:
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            Path zum Download-Ordner
        """
        download_path = self.download_dir / category
        download_path.mkdir(parents=True, exist_ok=True)
        return download_path
    
    def get_state_file(self, category: str) -> Path:
        """
        Gibt die State-Datei für eine Kategorie zurück
        
        Args:
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            Path zur State-Datei
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)
        return self.state_dir / f"{category}_downloaded.txt"
    
    def get_csv_file(self, category: str) -> Path:
        """
        Gibt den CSV-Pfad für eine Kategorie zurück
        
        Args:
            category: 'saved', 'liked' oder 'own'
            
        Returns:
            Path zur CSV-Datei
        """
        return self.base_dir / f"instagram_{category}_metadata.csv"
