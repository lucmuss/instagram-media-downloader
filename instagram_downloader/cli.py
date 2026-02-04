"""
CLI-Interface für Instagram Media Downloader
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .config import Config
from .downloader import InstagramDownloader
from .logger import get_log_file_path, setup_logger


def create_parser() -> argparse.ArgumentParser:
    """
    Erstellt und konfiguriert den ArgumentParser für die CLI.

    Returns:
        argparse.ArgumentParser: Der konfigurierte ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="instagram-downloader",
        description="📥 Instagram Media Downloader - Lädt deine Instagram-Medien herunter",
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

Konfiguration über Umgebungsvariablen (siehe .env.example):
  INSTAGRAM_USERNAME  - Dein Instagram-Username (Standard: skymuss)
  DATA_DIR           - Verzeichnis mit Instagram-Export
  DOWNLOAD_DIR       - Ziel-Verzeichnis für Downloads
  REQUEST_DELAY      - Verzögerung zwischen Requests (Sekunden)
  MAX_RETRIES        - Max. Wiederholungsversuche bei Fehlern
  LOG_LEVEL          - Log-Level (DEBUG, INFO, WARNING, ERROR)
        """,
    )

    parser.add_argument(
        "command",
        choices=["saved", "liked", "own", "all"],
        help="Welche Medien herunterladen (saved=Bookmarks, liked=Likes, own=Eigene Posts, all=Alles)",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Konfigurationsoptionen
    config_group = parser.add_argument_group("Konfiguration")

    config_group.add_argument(
        "-u", "--username", type=str, help="Instagram-Username (überschreibt INSTAGRAM_USERNAME)"
    )

    config_group.add_argument(
        "-d", "--data-dir", type=Path, help="Verzeichnis mit Instagram-Export-Daten"
    )

    config_group.add_argument(
        "-o", "--output-dir", type=Path, help="Ziel-Verzeichnis für Downloads"
    )

    config_group.add_argument(
        "-c", "--config", type=Path, help="Pfad zu Konfigurationsdatei (.ini)"
    )

    # Download-Optionen
    download_group = parser.add_argument_group("Download-Optionen")

    download_group.add_argument(
        "--delay", type=float, help="Verzögerung zwischen Downloads in Sekunden (Standard: 1.0)"
    )

    download_group.add_argument(
        "--max-retries", type=int, help="Maximale Wiederholungsversuche bei Fehlern (Standard: 3)"
    )

    download_group.add_argument(
        "--timeout", type=int, help="Timeout für einzelne Downloads in Sekunden (Standard: 60)"
    )

    download_group.add_argument(
        "--no-csv", action="store_true", help="CSV-Metadaten-Export deaktivieren"
    )

    # Logging-Optionen
    log_group = parser.add_argument_group("Logging")

    log_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log-Level (Standard: INFO)",
    )

    log_group.add_argument(
        "--log-file", type=Path, help="Pfad zur Log-Datei (Standard: automatisch generiert)"
    )

    log_group.add_argument(
        "--no-log-file", action="store_true", help="Keine Log-Datei erstellen (nur Console)"
    )

    return parser


def apply_cli_args_to_config(config: Config, args: argparse.Namespace) -> None:
    """
    Wendet die über die Befehlszeile empfangenen Argumente auf das Konfigurations-Objekt an.

    CLI-Argumente überschreiben dabei Werte aus Umgebungsvariablen oder der Konfigurationsdatei.

    Args:
        config: Die Instanz des `Config`-Objekts, das aktualisiert werden soll.
        args: Der geparste `argparse.Namespace`-Objekt, das die CLI-Argumente enthält.
    """
    if args.username:
        config._defaults["username"] = args.username

    if args.data_dir:
        config._defaults["data_dir"] = str(args.data_dir)

    if args.output_dir:
        config._defaults["download_dir"] = str(args.output_dir)

    if args.delay:
        config._defaults["request_delay"] = args.delay

    if args.max_retries:
        config._defaults["max_retries"] = args.max_retries

    if args.timeout:
        config._defaults["timeout"] = args.timeout

    if args.no_csv:
        config._defaults["csv_export"] = False

    if args.log_level:
        config._defaults["log_level"] = args.log_level


def print_banner() -> None:
    """
    Zeigt ein ansprechendes Banner mit Programm- und Versionsinformationen an.
    """
    print("=" * 70)
    print("🎯 INSTAGRAM MEDIA DOWNLOADER")
    print(f"   Version {__version__}")
    print("=" * 70)
    print()


def print_summary(downloader: InstagramDownloader, download_dir: Path) -> None:
    """
    Zeigt eine Zusammenfassung der Download-Ergebnisse an.

    Args:
        downloader: Die `InstagramDownloader`-Instanz, die die Download-Statistiken enthält.
        download_dir: Der Pfad zum Hauptdownload-Verzeichnis.
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


def main(argv: Optional[List[str]] = None) -> None:
    """
    Der Haupteinstiegspunkt für die Befehlszeilenschnittstelle (CLI).

    Diese Funktion parst Kommandozeilen-Argumente, initialisiert die Konfiguration
    und den Logger, führt die Downloads durch und gibt eine Zusammenfassung aus.

    Args:
        argv: Optional. Eine Liste von String-Argumenten (ähnlich sys.argv).
              Wird hauptsächlich für Testzwecke verwendet. Wenn None, werden die
              Argumente von `sys.argv` verwendet.
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
            log_file = args.log_file or get_log_file_path(config.base_dir, args.command)

        logger = setup_logger(level=config.log_level, log_file=log_file, console=True)

        logger.info(f"Instagram Media Downloader v{__version__} gestartet")
        logger.info(f"Kommando: {args.command}")
        logger.info(f"Username: {config.username}")

        # Downloader erstellen
        downloader = InstagramDownloader(config, logger)

        # yt-dlp Check
        if not downloader.check_ytdlp():
            logger.critical("yt-dlp ist nicht installiert oder nicht im PATH gefunden!")
            print("\n❌ FEHLER: yt-dlp ist nicht installiert oder nicht im PATH gefunden!")
            print("\n📦 Installation:")
            print("   sudo apt install yt-dlp")
            print("   # oder falls Python-Paket:")
            print("   pip install yt-dlp")
            sys.exit(1)

        logger.info("yt-dlp gefunden ✓")

        # Kategorien bestimmen
        categories = []
        if args.command == "all":
            categories = [
                downloader.MEDIA_CATEGORY_SAVED,
                downloader.MEDIA_CATEGORY_LIKED,
                downloader.MEDIA_CATEGORY_OWN,
            ]
        else:
            categories = [args.command]

        # Downloads durchführen
        for category in categories:
            try:
                logger.info("\n{'=' * 50}")
                logger.info(f"Kategorie: {category.upper()}")
                logger.info("{'=' * 50}")

                # Download
                downloader.download_category(category)

                # Zusammenfassung für diese Kategorie
                # download_dir wird in download_category erstellt/genutzt
                # Hier wird nur der Pfad für die Anzeige benötigt
                display_download_dir = config.get_download_path(category)
                print_summary(downloader, display_download_dir)

                # Stats zurücksetzen für nächste Kategorie
                if len(categories) > 1:
                    downloader.stats = type(
                        downloader.stats
                    )()  # Reset statistics for next category

            except KeyboardInterrupt:
                logger.warning(
                    "\n⚠️ Download von Kategorie '{category}' durch Benutzer abgebrochen!"
                )
                print(
                    "\n💡 HINWEIS: Download kann jederzeit fortgesetzt werden, indem der Befehl erneut ausgeführt wird."
                )
                sys.exit(0)  # Exit gracefully on user interruption

            except Exception as e:
                logger.error(f"Fehler bei Kategorie {category}: {e}", exc_info=True)
                print(f"\n❌ FEHLER in Kategorie '{category}': {e}")
                continue  # Continue with next category if one fails

        logger.info("Alle Downloads erfolgreich abgeschlossen.")
        print("\n✨ Fertig! Alle Downloads wurden verarbeitet.")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Programm durch Benutzer abgebrochen.")
        print("\n\n⚠️ Programm abgebrochen.")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"\n❌ FATALER FEHLER: {e}", exc_info=True)
        print(f"\n❌ FATALER FEHLER: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
