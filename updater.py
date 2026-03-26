"""Auto-Updater: Prueft GitHub auf neue Versionen, laedt Updates herunter und ersetzt die .exe.

Ablauf:
    1. UpdatePruefThread prueft GitHub API im Hintergrund
    2. Bei neuer Version: Signal an MainWindow
    3. DownloadThread laedt .exe herunter (mit Fortschritt + Abbruch)
    4. Batch-Helper ersetzt die laufende .exe und startet neu
"""

import os
import sys
import tempfile
import subprocess
import urllib.request
import urllib.error
import json
import logging

from PySide6.QtCore import QThread, Signal

from version import __version__

logger = logging.getLogger(__name__)

# GitHub Repository
GITHUB_OWNER = "Mox2k"
GITHUB_REPO = "WJPruefpilot2"
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# Temporaere Dateien
DOWNLOAD_DATEINAME = "WJPruefpilot_update.exe"


def _parse_version(version_str: str) -> tuple:
    """Parst einen Versionsstring wie '2.1.0' oder 'v2.1.0' zu einem Tuple (2, 1, 0).

    Gibt (0, 0, 0) zurueck wenn der String nicht parsbar ist.
    """
    version_str = version_str.strip().lstrip("v")
    try:
        teile = version_str.split(".")
        return tuple(int(t) for t in teile)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def ist_neuer(remote_version: str, lokale_version: str) -> bool:
    """Prueft ob die Remote-Version neuer ist als die lokale."""
    return _parse_version(remote_version) > _parse_version(lokale_version)


class UpdatePruefThread(QThread):
    """Prueft im Hintergrund ob eine neue Version auf GitHub verfuegbar ist.

    Signals:
        neue_version_gefunden(str, str, str, int):
            (neue_version, download_url, release_name, dateigroesse)
        pruefung_fehlgeschlagen(str): Fehlermeldung (nur fuer Logging)
    """

    neue_version_gefunden = Signal(str, str, str, int)
    pruefung_fehlgeschlagen = Signal(str)

    def run(self):
        """Fuehrt den API-Call durch und vergleicht Versionen."""
        try:
            anfrage = urllib.request.Request(
                API_URL,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": f"WJPruefpilot/{__version__}",
                },
            )
            with urllib.request.urlopen(anfrage, timeout=10) as antwort:
                daten = json.loads(antwort.read().decode("utf-8"))

            tag = daten.get("tag_name", "")
            release_name = daten.get("name", tag)

            if not ist_neuer(tag, __version__):
                logger.info("Kein Update verfuegbar (aktuell: %s, remote: %s)", __version__, tag)
                return

            # .exe-Asset suchen
            assets = daten.get("assets", [])
            exe_asset = None
            for asset in assets:
                if asset.get("name", "").lower().endswith(".exe"):
                    exe_asset = asset
                    break

            if not exe_asset:
                self.pruefung_fehlgeschlagen.emit("Kein .exe-Asset im Release gefunden")
                return

            download_url = exe_asset.get("browser_download_url", "")
            dateigroesse = exe_asset.get("size", 0)

            if not download_url:
                self.pruefung_fehlgeschlagen.emit("Keine Download-URL im Release-Asset")
                return

            neue_version = tag.lstrip("v")
            logger.info("Neue Version gefunden: %s (aktuell: %s)", neue_version, __version__)
            self.neue_version_gefunden.emit(neue_version, download_url, release_name, dateigroesse)

        except urllib.error.URLError as e:
            # Offline oder Netzwerkfehler — still ignorieren
            logger.debug("Update-Pruefung fehlgeschlagen (Netzwerk): %s", e)
            self.pruefung_fehlgeschlagen.emit(str(e))
        except Exception as e:
            logger.debug("Update-Pruefung fehlgeschlagen: %s", e)
            self.pruefung_fehlgeschlagen.emit(str(e))


class DownloadThread(QThread):
    """Laedt eine Datei herunter und meldet den Fortschritt.

    Signals:
        fortschritt(int): Prozent (0-100)
        abgeschlossen(str): Pfad zur heruntergeladenen Datei
        fehler(str): Fehlermeldung
    """

    fortschritt = Signal(int)
    abgeschlossen = Signal(str)
    fehler = Signal(str)

    def __init__(self, url: str, erwartete_groesse: int, parent=None):
        super().__init__(parent)
        self._url = url
        self._erwartete_groesse = erwartete_groesse
        self._abgebrochen = False

    def abbrechen(self):
        """Bricht den Download ab."""
        self._abgebrochen = True

    def run(self):
        """Fuehrt den Download durch."""
        ziel_pfad = os.path.join(tempfile.gettempdir(), DOWNLOAD_DATEINAME)

        try:
            anfrage = urllib.request.Request(
                self._url,
                headers={"User-Agent": f"WJPruefpilot/{__version__}"},
            )
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                gesamt = int(antwort.headers.get("Content-Length", 0))
                if gesamt == 0:
                    gesamt = self._erwartete_groesse

                heruntergeladen = 0
                block_groesse = 65536  # 64 KB

                with open(ziel_pfad, "wb") as datei:
                    while True:
                        if self._abgebrochen:
                            datei.close()
                            self._aufraeumen(ziel_pfad)
                            return

                        block = antwort.read(block_groesse)
                        if not block:
                            break

                        datei.write(block)
                        heruntergeladen += len(block)

                        if gesamt > 0:
                            prozent = int((heruntergeladen / gesamt) * 100)
                            self.fortschritt.emit(min(prozent, 100))

            # Dateigroessen-Check
            tatsaechliche_groesse = os.path.getsize(ziel_pfad)
            if self._erwartete_groesse > 0 and tatsaechliche_groesse != self._erwartete_groesse:
                self._aufraeumen(ziel_pfad)
                self.fehler.emit(
                    f"Dateigroesse stimmt nicht ueberein "
                    f"(erwartet: {self._erwartete_groesse}, erhalten: {tatsaechliche_groesse})"
                )
                return

            if self._abgebrochen:
                self._aufraeumen(ziel_pfad)
                return

            logger.info("Download abgeschlossen: %s (%d Bytes)", ziel_pfad, tatsaechliche_groesse)
            self.abgeschlossen.emit(ziel_pfad)

        except Exception as e:
            self._aufraeumen(ziel_pfad)
            logger.error("Download fehlgeschlagen: %s", e)
            self.fehler.emit(f"Download fehlgeschlagen: {e}")

    @staticmethod
    def _aufraeumen(pfad: str):
        """Loescht eine unvollstaendige Download-Datei."""
        try:
            if os.path.exists(pfad):
                os.remove(pfad)
        except OSError:
            pass


def starte_update(download_pfad: str) -> bool:
    """Schreibt das Batch-Script und startet den Self-Replace-Vorgang.

    Args:
        download_pfad: Pfad zur heruntergeladenen neuen .exe

    Returns:
        True wenn das Batch-Script erfolgreich gestartet wurde
    """
    if not getattr(sys, 'frozen', False):
        logger.warning("Self-Replace nur im gepackten Modus moeglich")
        return False

    aktuelle_exe = sys.executable
    batch_pfad = os.path.join(tempfile.gettempdir(), "wjpruefpilot_update.bat")

    batch_inhalt = f"""@echo off
setlocal
set "UPDATE={download_pfad}"
set "TARGET={aktuelle_exe}"
set "BACKUP=%TARGET%.bak"

:: Warten bis alter Prozess beendet und _MEI bereinigt ist
ping -n 5 127.0.0.1 >nul

:: Sicherungskopie erstellen
copy /y "%TARGET%" "%BACKUP%" >nul 2>&1

:: Ersetzen mit Retry (3 Versuche, falls .exe noch gesperrt)
set VERSUCH=0
:retry
set /a VERSUCH+=1
move /y "%UPDATE%" "%TARGET%" >nul 2>&1
if %errorlevel% neq 0 (
    if %VERSUCH% lss 3 (
        ping -n 3 127.0.0.1 >nul
        goto retry
    )
    echo Update fehlgeschlagen nach 3 Versuchen.
    :: Backup wiederherstellen
    move /y "%BACKUP%" "%TARGET%" >nul 2>&1
    pause
    goto end
)

:: Backup loeschen (nicht mehr noetig)
del "%BACKUP%" >nul 2>&1

:: Warten bis Dateisystem bereit ist
ping -n 4 127.0.0.1 >nul

:: Neue Version starten
start "" "%TARGET%"

:end
:: Batch loescht sich selbst
del "%~f0"
"""

    try:
        with open(batch_pfad, "w", encoding="ascii", errors="replace") as f:
            f.write(batch_inhalt)

        # Batch-Script detached starten (kein Fenster)
        subprocess.Popen(
            [batch_pfad],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True,
        )

        logger.info("Update-Batch gestartet: %s", batch_pfad)
        return True

    except Exception as e:
        logger.error("Konnte Update-Batch nicht starten: %s", e)
        return False
