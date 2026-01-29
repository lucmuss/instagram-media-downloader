"""
CLI-Interface für Instagram Media Downloader
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .config import Config
from .logger import setup_logger, get_log_file_path
from .downloader import InstagramDownloader


def create_parser() -> argparse.ArgumentParser:
    """Erstellt den ArgumentParser für die CLI"""
    
    parser = argparse.ArgumentParser(
        prog='instagram-downloader',
        description='📥 Instagram Media Downloader - Lädt deine Instagram-Medien herunter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Alle gespeicherten Posts herunterladen
  instagram-downloader saved
  
  # Alle gelikten Posts herunterladen
  instagram-downloader liked
  
  # Eigene Posts herunterladen
  instagram-downloader own
  
  # Alles herunterladen
  instagram-downloader all
  
  # Mit custom Konfiguration
  instagram-downloader saved --username mein_username --delay 2.0
  
  # Mit Debug-Logging
  instagram-downloader liked --log-level DEBUG

Konfiguration über Umgebungsvariablen:
  INSTAGRAM_USERNAME  - Dein Instagram-Username (Standard: skymuss)
  DATA_DIR           - Verzeichnis mit Instagram-Export
  DOWNLOAD_DIR       - Ziel-Verzeichnis für Downloads
  REQUEST_DELAY      - Verzögerung zwischen Requests (Sekunden)
  MAX_RETRIES        - Max. Wiederholungsversuche bei Fehlern
  LOG_LEVEL          - Log-Level (DEBUG, INFO, WARNING, ERROR)
        """
    )
    
    parser.add_argument(
        'command',
        choices=['saved', 'liked', 'own', 'all'],
        help='Welche Medien herunterladen (saved=Bookmarks, liked=Likes, own=Eigene Posts, all=Alles)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # Konfigurationsoptionen
    config_group = parser.add_argument_group('Konfiguration')
    
    config_group.add_argument(
        '-u', '--username',
        type=str,
        help='Instagram-Username (überschreibt INSTAGRAM_USERNAME)'
    )
    
    config_group.add_argument(
        '-d', '--data-dir',
        type=Path,
        help='Verzeichnis mit Instagram-Export-Daten'
    )
    
    config_group.add_argument(
        '-o', '--output-dir',
        type=Path,
        help='Ziel-Verzeichnis für Downloads'
    )
    
    config_group.add_argument(
        '-c', '--config',
        type=Path,
        help='Pfad zu Konfigurationsdatei (.ini)'
    )
    
    # Download-Optionen
    download_group = parser.add_argument_group('Download-Optionen')
    
    download_group.add_argument(
        '--delay',
        type=float,
        help='Verzögerung zwischen Downloads in Sekunden (Standard: 1.0)'
    )
    
    download_group.add_argument(
        '--max-retries',
        type=int,
        help='Maximale Wiederholungsversuche bei Fehlern (Standard: 3)'
    )
    
    download_group.add_argument(
        '--timeout',
        type=int,
        help='Timeout für einzelne Downloads in Sekunden (Standard: 60)'
    )
    
    download_group.add_argument(
        '--no-csv',
        action='store_true',
        help='CSV-Metadaten-Export deaktivieren'
    )
    
    # Logging-Optionen
    log_group = parser.add_argument_group('Logging')
    
    log_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log-Level (Standard: INFO)'
    )
    
    log_group.add_argument(
        '--log-file',
        type=Path,
        help='Pfad zur Log-Datei (Standard: automatisch generiert)'
    )
    
    log_group.add_argument(
        '--no-log-file',
        action='store_true',
        help='Keine Log-Datei erstellen (nur Console)'
    )
    
    return parser


def apply_cli_args_to_config(config: Config, args: argparse.Namespace):
    """
    Wendet CLI-Argumente auf Config-Objekt an
    
    Args:
        config: Config-Objekt
        args: ParsedArguments von argparse
    """
    if args.username:
        config._defaults['username'] = args.username
    
    if args.data_dir:
        config._defaults['data_dir'] = str(args.data_dir)
    
    if args.output_dir:
        config._defaults['download_dir'] = str(args.output_dir)
    
    if args.delay:
        config._defaults['request_delay'] = args.delay
    
    if args.max_retries:
        config._defaults['max_retries'] = args.max_retries
    
    if args.timeout:
        config._defaults['timeout'] = args.timeout
    
    if args.no_csv:
        config._defaults['csv_export'] = False
    
    if args.log_level:
        config._defaults['log_level'] = args.log_level


def print_banner():
    """Zeigt Banner mit Programminfo"""
    print("=" * 70)
    print("🎯 INSTAGRAM MEDIA DOWNLOADER")
    print(f"   Version {__version__}")
    print("=" * 70)
    print()


def print_summary(downloader: InstagramDownloader, download_dir: Path):
    """
    Zeigt Download-Zusammenfassung
    
    Args:
        downloader: Downloader-Instanz mit Statistiken
        download_dir: Download-Verzeichnis
    """
    print("\n" + "=" * 70)
    print("📊 DOWNLOAD ABGESCHLOSSEN")
    print("=" * 70)
    print(f"✅ Erfolgreich:    {downloader.stats.success}")
    print(f"❌ Fehlgeschlagen: {downloader.stats.failed}")
    print(f"⏭️  Übersprungen:  {downloader.stats.skipped}")
    print(f"📁 Speicherort:    {download_dir}")
    print("=" * 70)
    
    if downloader.stats.failed > 0:
        print("\n💡 HINWEISE:")
        print("   • Gelöschte Posts können nicht heruntergeladen werden")
        print("   • Private Accounts benötigen evtl. Login-Cookies")
        print("   • Bei Rate-Limits: Später erneut versuchen")


def main(argv: Optional[list] = None):
    """
    Haupteinstiegspunkt für CLI
    
    Args:
        argv: Optional - Command-line Argumente (für Tests)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    try:
        # Banner anzeigen
        print_banner()
        
        # Config laden
        config_file = args.config if args.config else None
        config = Config(config_file)
        
        # CLI-Args anwenden
        apply_cli_args_to_config(config, args)
        
        # Logger setup
        log_file = None
        if not args.no_log_file:
            if args.log_file:
                log_file = args.log_file
            else:
                log_file = get_log_file_path(config.base_dir, args.command)
        
        logger = setup_logger(
            level=config.log_level,
            log_file=log_file,
            console=True
        )
        
        logger.info(f"Instagram Media Downloader v{__version__} gestartet")
        logger.info(f"Kommando: {args.command}")
        logger.info(f"Username: {config.username}")
        
        # Downloader erstellen
        downloader = InstagramDownloader(config, logger)
        
        # yt-dlp Check
        if not downloader.check_ytdlp():
            logger.error("yt-dlp ist nicht installiert!")
            print("\n❌ FEHLER: yt-dlp ist nicht installiert!")
            print("\n📦 Installation:")
            print("   sudo apt install yt-dlp")
            print("   # oder")
            print("   pip install yt-dlp")
            sys.exit(1)
        
        logger.info("yt-dlp gefunden ✓")
        
        # Kategorien bestimmen
        categories = []
        if args.command == 'all':
            categories = ['saved', 'liked', 'own']
        else:
            categories = [args.command]
        
        # Downloads durchführen
        for category in categories:
            try:
                logger.info(f"\n{'=' * 50}")
                logger.info(f"Kategorie: {category.upper()}")
                logger.info(f"{'=' * 50}")
                
                # Download
                downloader.download_category(category)
                
                # Zusammenfassung für diese Kategorie
                download_dir = config.get_download_path(category)
                print_summary(downloader, download_dir)
                
                # Stats zurücksetzen für nächste Kategorie
                if len(categories) > 1:
                    downloader.stats = type(downloader.stats)()
                
            except KeyboardInterrupt:
                logger.warning("\n⚠️ Download abgebrochen!")
                print("\n💡 Resume: Einfach Befehl erneut ausführen")
                sys.exit(0)
            
            except Exception as e:
                logger.error(f"Fehler bei Kategorie {category}: {e}", exc_info=True)
                print(f"\n❌ Fehler: {e}")
                continue
        
        logger.info("Alle Downloads abgeschlossen")
        print("\n✨ Fertig!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
