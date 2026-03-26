"""Hauptfenster der Anwendung mit Custom Title Bar, Sidebar, Content und Overlay-Mechanik."""

import sys
import ctypes
import ctypes.wintypes
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QStackedWidget, QApplication, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QPoint, Signal
)
from PySide6.QtGui import QPainter, QBrush, QColor, QPainterPath, QRegion

from ui.title_bar import TitleBar
from ui.sidebar import Sidebar
from ui.auftraege_seite import AuftraegeSeite
from ui.detail_temp_seite import DetailTempSeite
from ui.detail_vde_seite import DetailVDESeite
from ui.info_seite import InfoSeite
from ui.overlay_dialog import OverlayDialog
from ui.settings_overlay import SettingsOverlay
from ui.styles import FARBEN_DARK, FARBEN_LIGHT, generiere_stylesheet
from settings import Settings
from updater import UpdatePruefThread, DownloadThread, starte_update


# Windows Konstanten
GWL_STYLE = -16
WS_THICKFRAME = 0x00040000
WS_CAPTION = 0x00C00000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084

HTCLIENT = 1
HTCAPTION = 2
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.wintypes.HWND),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.wintypes.WPARAM),
        ("lParam", ctypes.wintypes.LPARAM),
        ("time", ctypes.wintypes.DWORD),
        ("pt", ctypes.wintypes.POINT),
    ]


class DimmOverlay(QWidget):
    """Halbtransparentes Overlay zum Abdunkeln bei geoeffneter Detail-Ansicht."""

    geschlossen = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        """Zeichnet halbtransparenten dunklen Hintergrund."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        painter.end()

    def mousePressEvent(self, event):
        """Klick auf den abgedunkelten Bereich (nicht auf Kind-Widget) schliesst Detail."""
        self.geschlossen.emit()
        event.accept()


class MainWindow(QMainWindow):
    """Frameless Hauptfenster mit Custom Title Bar, Sidebar und Overlay-Detail-Seiten."""

    SIDEBAR_BREITE_EINGEKLAPPT = 52
    SIDEBAR_BREITE_AUSGEKLAPPT = 200
    START_BREITE = 1000
    START_HOEHE = 700
    MIN_BREITE = 800
    MIN_HOEHE = 500

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(self.MIN_BREITE, self.MIN_HOEHE)

        # Zustand
        self._ist_maximiert = False
        self._normale_geometrie = None
        self._aktuelle_farben = FARBEN_DARK
        self._resize_rand = 6
        self._aktive_detail = None

        # Settings laden
        self._app_settings = Settings("settings.ini")
        self._ist_dark = self._app_settings.get_theme() == "dark"
        self._aktuelle_farben = FARBEN_DARK if self._ist_dark else FARBEN_LIGHT

        # Fensterposition/-groesse wiederherstellen
        self._stelle_fenster_wieder_her()

        self._erstelle_ui()
        self._wende_theme_an()

        # Sidebar-Zustand wiederherstellen
        sidebar_offen = self._app_settings.get_sidebar_ausgeklappt()
        if sidebar_offen:
            self._sidebar.setFixedWidth(self.SIDEBAR_BREITE_AUSGEKLAPPT)
            self._sidebar.aktualisiere_labels(True)
        self._title_bar.aktualisiere_sidebar_icon(sidebar_offen)

        # Aktive Seite wiederherstellen
        gespeicherte_seite = self._app_settings.get_aktive_seite()
        if gespeicherte_seite != "auftraege":
            self._seite_wechseln(gespeicherte_seite)
            self._sidebar.setze_aktive_seite(gespeicherte_seite)

        # Maximiert wiederherstellen (nach UI-Aufbau)
        if self._app_settings.get_fenster_maximiert():
            self._normale_geometrie = self.geometry()
            bildschirm = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(bildschirm)
            self._ist_maximiert = True
            self._title_bar.aktualisiere_maximieren_icon(True)

        # Windows-Fensterstile setzen fuer Resize und Snap
        self._setze_win32_styles()

        # Auto-Update Check im Hintergrund
        self._download_thread = None
        self._starte_update_pruefung()

    def _setze_win32_styles(self):
        """Setzt Win32-Fensterstile fuer native Resize-Raender und Snap."""
        hwnd = int(self.winId())
        stil = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        stil |= WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, stil)
        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            0x0001 | 0x0002 | 0x0004 | 0x0020  # NOMOVE | NOSIZE | NOZORDER | FRAMECHANGED
        )

    def resizeEvent(self, event):
        """Aktualisiert Overlay-Position bei Groessenaenderung."""
        super().resizeEvent(event)
        if self._dimm_overlay.isVisible():
            self._dimm_overlay.setGeometry(self._aussen_widget.rect())
            self._positioniere_detail()

    def paintEvent(self, event):
        """Zeichnet das Fenster mit Anti-Aliased abgerundeten Ecken."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        bg_farbe = self._aktuelle_farben.get("basis", "#2c3245")
        painter.setBrush(QBrush(QColor(bg_farbe)))
        painter.setPen(Qt.NoPen)
        radius = 8 if not self._ist_maximiert else 0
        painter.drawRoundedRect(self.rect(), radius, radius)

    def _stelle_fenster_wieder_her(self):
        """Stellt Fensterposition und -groesse aus Settings wieder her, oder zentriert."""
        geo = self._app_settings.get_fenster_geometrie()
        if geo:
            x, y, b, h = geo
            # Sicherstellen, dass das Fenster auf dem sichtbaren Bildschirm liegt
            bildschirm = QApplication.primaryScreen().availableGeometry()
            if (x + b > 0 and y + h > 0 and
                    x < bildschirm.width() and y < bildschirm.height()):
                self.setGeometry(x, y,
                                 max(b, self.MIN_BREITE),
                                 max(h, self.MIN_HOEHE))
                return
        # Fallback: Zentrieren
        bildschirm = QApplication.primaryScreen().geometry()
        x = (bildschirm.width() - self.START_BREITE) // 2
        y = (bildschirm.height() - self.START_HOEHE) // 2
        self.setGeometry(x, y, self.START_BREITE, self.START_HOEHE)

    def closeEvent(self, event):
        """Speichert den Fensterzustand beim Schliessen."""
        # Fenstergeometrie (nicht-maximierte Groesse)
        if self._ist_maximiert:
            if self._normale_geometrie:
                geo = self._normale_geometrie
                self._app_settings.set_fenster_geometrie(
                    geo.x(), geo.y(), geo.width(), geo.height()
                )
        else:
            geo = self.geometry()
            self._app_settings.set_fenster_geometrie(
                geo.x(), geo.y(), geo.width(), geo.height()
            )

        self._app_settings.set_fenster_maximiert(self._ist_maximiert)

        # Sidebar-Zustand
        sidebar_offen = self._sidebar.width() > self.SIDEBAR_BREITE_EINGEKLAPPT
        self._app_settings.set_sidebar_ausgeklappt(sidebar_offen)

        super().closeEvent(event)

    def _erstelle_ui(self):
        """Baut das gesamte UI auf: Title Bar, Sidebar, Content, Overlay."""
        self._aussen_widget = QWidget()
        self._aussen_widget.setObjectName("aussenWidget")
        self.setCentralWidget(self._aussen_widget)

        aussen_layout = QVBoxLayout(self._aussen_widget)
        aussen_layout.setContentsMargins(0, 0, 0, 0)
        aussen_layout.setSpacing(0)

        # Title Bar
        self._title_bar = TitleBar(self)
        self._title_bar.minimieren_geklickt.connect(self.showMinimized)
        self._title_bar.maximieren_geklickt.connect(self._toggle_maximieren)
        self._title_bar.schliessen_geklickt.connect(self.close)
        self._title_bar.toggle_geklickt.connect(self._sidebar_toggle)
        self._title_bar.theme_geklickt.connect(self._theme_wechseln)
        aussen_layout.addWidget(self._title_bar)

        # Hauptbereich: Sidebar + Content
        hauptbereich = QWidget()
        hauptbereich.setObjectName("hauptbereich")
        hauptbereich.setAttribute(Qt.WA_StyledBackground, True)
        haupt_layout = QHBoxLayout(hauptbereich)
        haupt_layout.setContentsMargins(0, 0, 0, 0)
        haupt_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(self)
        self._sidebar.setFixedWidth(self.SIDEBAR_BREITE_EINGEKLAPPT)
        self._sidebar.navigation_geklickt.connect(self._seite_wechseln)
        self._sidebar.settings_geklickt.connect(self._oeffne_settings)
        haupt_layout.addWidget(self._sidebar)

        # Content-Container mit Margin
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_container.setAttribute(Qt.WA_StyledBackground, True)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 10, 10)
        content_layout.setSpacing(0)

        # Content-Bereich mit Schatten
        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("contentStack")

        schatten = QGraphicsDropShadowEffect()
        schatten.setBlurRadius(20)
        schatten.setOffset(0, 2)
        schatten.setColor(QColor(0, 0, 0, 80))
        self._content_stack.setGraphicsEffect(schatten)

        content_layout.addWidget(self._content_stack)
        haupt_layout.addWidget(content_container)

        self._erstelle_seiten()
        aussen_layout.addWidget(hauptbereich)

        # --- Dimm-Overlay (ueberlappt gesamtes Fenster) ---
        self._dimm_overlay = DimmOverlay(self._aussen_widget)
        self._dimm_overlay.hide()
        self._dimm_overlay.geschlossen.connect(self._schliesse_detail)

        # --- Detail-Seiten (werden als Kinder des Overlays positioniert) ---
        self._detail_temp = DetailTempSeite()
        self._detail_temp.pdf_erstellt.connect(self._temp_pdf_erstellt)

        self._detail_vde = DetailVDESeite()
        self._detail_vde.pdf_erstellt.connect(self._vde_pdf_erstellt)

        # --- Settings-Overlay ---
        self._settings_overlay = SettingsOverlay()
        self._settings_overlay.settings_geaendert.connect(self._settings_geaendert)

        # --- Dialog-Komponente (ueberlappt gesamtes Fenster) ---
        self._dialog = OverlayDialog(self._aussen_widget)
        self._dialog.hide()

        # Detail-Seiten Zugriff auf Dialog geben
        self._detail_temp.setze_dialog(self._dialog)
        self._detail_vde.setze_dialog(self._dialog)

        # Auftragswechsel loescht den Eingaben-Cache
        self._auftraege_seite.auftrag_gewechselt.connect(
            self._detail_temp.loesche_eingaben_cache
        )
        self._auftraege_seite.auftrag_gewechselt.connect(
            self._detail_vde.loesche_eingaben_cache
        )

    def _erstelle_seiten(self):
        """Erstellt die Seiten fuer den Content-Bereich."""
        # Auftraege-Seite (Index 0)
        self._auftraege_seite = AuftraegeSeite()
        self._auftraege_seite.temp_geklickt.connect(self._oeffne_temp_detail)
        self._auftraege_seite.vde_geklickt.connect(self._oeffne_vde_detail)
        self._content_stack.addWidget(self._auftraege_seite)

        # Info-Seite (Index 1)
        self._info_seite = InfoSeite()
        self._content_stack.addWidget(self._info_seite)

        # Auftraege laden
        self._auftraege_seite.lade_auftraege()

    # --- Seitennavigation ---

    def _seite_wechseln(self, seiten_name: str):
        """Wechselt die angezeigte Seite im Content-Bereich mit Fade+Slide-Animation."""
        self._app_settings.set_aktive_seite(seiten_name)

        seiten_map = {"auftraege": 0, "info": 1}
        neuer_index = seiten_map.get(seiten_name, 0)
        alter_index = self._content_stack.currentIndex()

        if neuer_index == alter_index:
            return

        ziel_widget = self._content_stack.widget(neuer_index)
        if not ziel_widget:
            return

        # Opacity-Effekt fuer Fade-In
        opacity_effekt = QGraphicsOpacityEffect(ziel_widget)
        opacity_effekt.setOpacity(0.0)
        ziel_widget.setGraphicsEffect(opacity_effekt)

        self._content_stack.setCurrentIndex(neuer_index)

        # Slide-Startposition
        richtung = 1 if neuer_index > alter_index else -1
        start_pos = ziel_widget.pos()
        ziel_widget.move(start_pos.x() + (16 * richtung), start_pos.y())

        # Fade-Animation
        self._fade_anim = QPropertyAnimation(opacity_effekt, b"opacity")
        self._fade_anim.setDuration(200)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Slide-Animation
        self._slide_anim = QPropertyAnimation(ziel_widget, b"pos")
        self._slide_anim.setDuration(200)
        self._slide_anim.setStartValue(QPoint(start_pos.x() + (16 * richtung), start_pos.y()))
        self._slide_anim.setEndValue(start_pos)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._seitenwechsel_gruppe = QParallelAnimationGroup()
        self._seitenwechsel_gruppe.addAnimation(self._fade_anim)
        self._seitenwechsel_gruppe.addAnimation(self._slide_anim)
        self._seitenwechsel_gruppe.finished.connect(
            lambda: ziel_widget.setGraphicsEffect(None)
        )
        self._seitenwechsel_gruppe.start()

    # --- Detail-Seiten (Overlay) ---

    def _oeffne_temp_detail(self, waage_daten):
        """Oeffnet die Temperaturjustage-Detailseite fuer eine Waage."""
        self._detail_temp.setze_waage(waage_daten, self._aktuelle_farben)
        self._zeige_detail(self._detail_temp)

    def _oeffne_vde_detail(self, waage_daten):
        """Oeffnet die VDE-Pruefung-Detailseite fuer eine Waage."""
        kundennummer = self._auftraege_seite.get_aktuelle_kundennummer()
        self._detail_vde.setze_waage(waage_daten, self._aktuelle_farben, kundennummer)
        self._zeige_detail(self._detail_vde)

    def _oeffne_settings(self):
        """Oeffnet das Settings-Overlay."""
        self._settings_overlay.lade_werte()
        self._settings_overlay.aktualisiere_theme(self._aktuelle_farben, self._ist_dark)
        self._zeige_detail(self._settings_overlay)

    def _zeige_detail(self, detail_widget):
        """Zeigt eine Detail-Seite mit Dimm-Overlay und Animation."""
        self._aktive_detail = detail_widget

        # Detail-Widget als Kind des Overlays einhaengen
        detail_widget.setParent(self._dimm_overlay)

        # Overlay positionieren und anzeigen
        self._dimm_overlay.setGeometry(self._aussen_widget.rect())
        self._positioniere_detail()

        # Opacity-Effekt fuer Fade-In des gesamten Overlays
        overlay_opacity = QGraphicsOpacityEffect(self._dimm_overlay)
        overlay_opacity.setOpacity(0.0)
        self._dimm_overlay.setGraphicsEffect(overlay_opacity)
        self._dimm_overlay.show()
        self._dimm_overlay.raise_()
        detail_widget.show()

        # Fade-Animation
        self._overlay_fade = QPropertyAnimation(overlay_opacity, b"opacity")
        self._overlay_fade.setDuration(150)
        self._overlay_fade.setStartValue(0.0)
        self._overlay_fade.setEndValue(1.0)
        self._overlay_fade.setEasingCurve(QEasingCurve.OutCubic)

        # Slide-Animation fuer Detail-Seite (16px nach oben)
        ziel_pos = detail_widget.pos()
        detail_widget.move(ziel_pos.x(), ziel_pos.y() + 16)

        self._detail_slide = QPropertyAnimation(detail_widget, b"pos")
        self._detail_slide.setDuration(150)
        self._detail_slide.setStartValue(QPoint(ziel_pos.x(), ziel_pos.y() + 16))
        self._detail_slide.setEndValue(ziel_pos)
        self._detail_slide.setEasingCurve(QEasingCurve.OutCubic)

        # Beide parallel starten
        self._detail_anim_gruppe = QParallelAnimationGroup()
        self._detail_anim_gruppe.addAnimation(self._overlay_fade)
        self._detail_anim_gruppe.addAnimation(self._detail_slide)
        self._detail_anim_gruppe.finished.connect(
            lambda: self._dimm_overlay.setGraphicsEffect(None)
        )
        self._detail_anim_gruppe.start()

    def _positioniere_detail(self):
        """Positioniert die aktive Detail-Seite im Content-Bereich oder zentriert (Settings)."""
        if not self._aktive_detail:
            return

        if self._aktive_detail is self._settings_overlay:
            self._positioniere_settings()
        else:
            # Detail-Seite fuellt den Content-Bereich
            pos = self._content_stack.mapTo(self._aussen_widget, QPoint(0, 0))
            self._aktive_detail.setGeometry(
                pos.x(), pos.y(),
                self._content_stack.width(), self._content_stack.height()
            )

    def _positioniere_settings(self):
        """Positioniert das Settings-Overlay zentriert im Fenster (kleiner als Content)."""
        fenster_rect = self._aussen_widget.rect()

        # ~85% der Fenstergroesse, max 750x550
        breite = min(int(fenster_rect.width() * 0.75), 750)
        hoehe = min(int(fenster_rect.height() * 0.80), 550)

        x = (fenster_rect.width() - breite) // 2
        y = (fenster_rect.height() - hoehe) // 2

        self._settings_overlay.setGeometry(x, y, breite, hoehe)

    def _schliesse_detail(self):
        """Schliesst die aktive Detail-Seite und blendet das Overlay aus."""
        if self._aktive_detail:
            # Eingaben speichern bevor die Detail-Seite geschlossen wird
            if hasattr(self._aktive_detail, '_speichere_eingaben'):
                self._aktive_detail._speichere_eingaben()

            # Bei Settings: Settings aller Komponenten neu laden
            if self._aktive_detail is self._settings_overlay:
                self._detail_temp._settings.reload()
                self._detail_temp._lade_messgeraete()
                self._detail_vde._settings.reload()
                self._detail_vde._lade_messgeraete()
                self._auftraege_seite._settings.reload()

            self._aktive_detail.hide()
        self._dimm_overlay.hide()
        self._aktive_detail = None

    def _temp_pdf_erstellt(self, kalibrier_nr):
        """Aktualisiert die Tabelle nach erfolgreicher Temp-PDF-Erstellung."""
        self._pdf_erstellt(kalibrier_nr, "temp")

    def _vde_pdf_erstellt(self, kalibrier_nr):
        """Aktualisiert die Tabelle nach erfolgreicher VDE-PDF-Erstellung."""
        self._pdf_erstellt(kalibrier_nr, "vde")

    def _pdf_erstellt(self, kalibrier_nr, art):
        """Extrahiert die WJ-Nummer aus der Kalibrierscheinnummer und aktualisiert die Tabelle."""
        teile = kalibrier_nr.split("_")
        if len(teile) >= 4:
            wj_nummer = "_".join(teile[3:])  # Falls WJ-Nummer selbst _ enthaelt
            self._auftraege_seite.aktualisiere_status(wj_nummer, art)

    # --- Settings ---

    def _settings_geaendert(self):
        """Wird aufgerufen wenn sich Einstellungen geaendert haben."""
        # Aktuell keine sofortige Aktion noetig -- wird beim Schliessen behandelt
        pass

    # --- Sidebar ---

    def _sidebar_toggle(self):
        """Klappt die Sidebar auf oder zu mit Animation."""
        aktuelle_breite = self._sidebar.width()
        wird_ausgeklappt = aktuelle_breite == self.SIDEBAR_BREITE_EINGEKLAPPT
        ziel_breite = (self.SIDEBAR_BREITE_AUSGEKLAPPT if wird_ausgeklappt
                       else self.SIDEBAR_BREITE_EINGEKLAPPT)

        self._title_bar.aktualisiere_sidebar_icon(wird_ausgeklappt)

        if not wird_ausgeklappt:
            self._sidebar.aktualisiere_labels(False)

        self._sidebar_animation = QPropertyAnimation(self._sidebar, b"minimumWidth")
        self._sidebar_animation.setDuration(200)
        self._sidebar_animation.setStartValue(aktuelle_breite)
        self._sidebar_animation.setEndValue(ziel_breite)
        self._sidebar_animation.setEasingCurve(QEasingCurve.InOutCubic)

        self._sidebar_max_animation = QPropertyAnimation(self._sidebar, b"maximumWidth")
        self._sidebar_max_animation.setDuration(200)
        self._sidebar_max_animation.setStartValue(aktuelle_breite)
        self._sidebar_max_animation.setEndValue(ziel_breite)
        self._sidebar_max_animation.setEasingCurve(QEasingCurve.InOutCubic)

        self._sidebar_anim_gruppe = QParallelAnimationGroup()
        self._sidebar_anim_gruppe.addAnimation(self._sidebar_animation)
        self._sidebar_anim_gruppe.addAnimation(self._sidebar_max_animation)

        if wird_ausgeklappt:
            self._sidebar_anim_gruppe.finished.connect(
                lambda: self._sidebar.aktualisiere_labels(True)
            )

        self._sidebar_anim_gruppe.start()

    # --- Theme ---

    def _theme_wechseln(self):
        """Wechselt zwischen Dark und Light Theme."""
        self._ist_dark = not self._ist_dark
        self._aktuelle_farben = FARBEN_DARK if self._ist_dark else FARBEN_LIGHT
        self._app_settings.set_theme("dark" if self._ist_dark else "light")
        self._wende_theme_an()

    def _wende_theme_an(self):
        """Wendet das aktuelle Theme auf alle Komponenten an."""
        stylesheet = generiere_stylesheet(self._aktuelle_farben)
        self.setStyleSheet(stylesheet)
        # Tooltip-Styling global auf Application-Ebene, damit es auch bei
        # reparented Widgets (Detail-Seiten im Overlay) greift
        QApplication.instance().setStyleSheet(f"""
            QToolTip {{
                background-color: {self._aktuelle_farben["basis"]};
                color: {self._aktuelle_farben["text_primaer"]};
                border: 1px solid {self._aktuelle_farben["border"]};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """)
        self._title_bar.aktualisiere_theme_icons(
            self._ist_dark, self._aktuelle_farben["icon_farbe"]
        )
        self._sidebar.aktualisiere_theme(self._ist_dark, self._aktuelle_farben)
        self._auftraege_seite.aktualisiere_theme(self._aktuelle_farben)
        self._info_seite.aktualisiere_theme(self._aktuelle_farben)
        self._detail_temp.aktualisiere_theme(self._aktuelle_farben)
        self._detail_vde.aktualisiere_theme(self._aktuelle_farben)
        self._settings_overlay.aktualisiere_theme(self._aktuelle_farben, self._ist_dark)
        self._dialog.setze_farben(self._aktuelle_farben)

    # --- Auto-Update ---

    def _starte_update_pruefung(self):
        """Startet den Update-Check im Hintergrund (wenn in Settings aktiviert)."""
        if not self._app_settings.get_auto_update():
            return

        self._update_thread = UpdatePruefThread()
        self._update_thread.neue_version_gefunden.connect(self._zeige_update_dialog)
        # Fehlschlag wird still ignoriert (kein Dialog)
        self._update_thread.start()

    def _zeige_update_dialog(self, neue_version, download_url, release_name, dateigroesse):
        """Zeigt den 'Neue Version verfuegbar'-Dialog."""
        from version import __version__

        self._update_url = download_url
        self._update_dateigroesse = dateigroesse
        self._update_version = neue_version

        self._dialog.zeige(
            typ="info",
            titel=f"Neue Version verfügbar",
            nachricht=f"Version {neue_version} ist verfügbar.\n(Aktuell: {__version__})",
            ok_text="Jetzt updaten",
            abbrechen_text="Später",
            bei_bestaetigung=self._starte_download,
            bei_ablehnung=None,
        )

    def _starte_download(self):
        """Startet den Download der neuen Version mit Fortschrittsanzeige."""
        self._dialog.zeige_fortschritt(
            titel="Update wird heruntergeladen…",
            nachricht=f"Version {self._update_version}",
            bei_abbruch=self._download_abbrechen,
        )

        self._download_thread = DownloadThread(
            self._update_url, self._update_dateigroesse
        )
        self._download_thread.fortschritt.connect(self._dialog.setze_fortschritt)
        self._download_thread.abgeschlossen.connect(self._download_fertig)
        self._download_thread.fehler.connect(self._download_fehler)
        self._download_thread.start()

    def _download_abbrechen(self):
        """Bricht den laufenden Download ab."""
        if self._download_thread and self._download_thread.isRunning():
            self._download_thread.abbrechen()

    def _download_fertig(self, pfad):
        """Download abgeschlossen — Self-Replace starten und App beenden."""
        self._dialog.schliesse()

        if starte_update(pfad):
            # Hinweis zeigen, dann App beenden
            self._dialog.zeige(
                typ="info",
                titel="Update installiert",
                nachricht=f"Version {self._update_version} wurde installiert.\n"
                          "Die App wird jetzt beendet — bitte neu starten.",
                bei_bestaetigung=lambda: QApplication.instance().quit(),
            )
        else:
            # Self-Replace fehlgeschlagen (z.B. nicht im frozen-Modus)
            self._dialog.zeige(
                typ="info",
                titel="Update heruntergeladen",
                nachricht=f"Die neue Version wurde gespeichert:\n{pfad}\n\n"
                          "Automatische Installation ist nur in der\n"
                          "gepackten .exe verfügbar.",
            )

    def _download_fehler(self, fehlermeldung):
        """Zeigt eine Fehlermeldung wenn der Download fehlschlaegt."""
        self._dialog.zeige(
            typ="fehler",
            titel="Update fehlgeschlagen",
            nachricht=fehlermeldung,
        )

    # --- Fenster ---

    def _toggle_maximieren(self):
        """Maximiert oder stellt das Fenster wieder her."""
        if self._ist_maximiert:
            if self._normale_geometrie:
                self.setGeometry(self._normale_geometrie)
            self._ist_maximiert = False
        else:
            self._normale_geometrie = self.geometry()
            bildschirm = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(bildschirm)
            self._ist_maximiert = True
        self._title_bar.aktualisiere_maximieren_icon(self._ist_maximiert)

    # --- Windows Native Events ---

    def nativeEvent(self, event_type, message):
        """Behandelt WM_NCCALCSIZE und WM_NCHITTEST fuer Frameless + Snap + Resize."""
        if event_type != b"windows_generic_MSG":
            return super().nativeEvent(event_type, message)

        try:
            msg = MSG.from_address(int(message))

            if msg.message == WM_NCCALCSIZE:
                if msg.wParam:
                    return True, 0
                return super().nativeEvent(event_type, message)

            if msg.message == WM_NCHITTEST:
                x_screen = ctypes.c_short(msg.lParam & 0xFFFF).value
                y_screen = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value

                geo = self.frameGeometry()
                x = x_screen - geo.left()
                y = y_screen - geo.top()
                w = geo.width()
                h = geo.height()
                r = self._resize_rand

                # Bei offenem Overlay: Klick auf Title Bar schliesst Overlay
                if self._dimm_overlay.isVisible():
                    title_bar_hoehe = self._title_bar.height()
                    if y < title_bar_hoehe:
                        # Klick in Title Bar Bereich -> als Client behandeln
                        # damit mousePressEvent des DimmOverlay greift
                        return True, HTCLIENT

                # Ecken
                if x < r and y < r:
                    return True, HTTOPLEFT
                if x > w - r and y < r:
                    return True, HTTOPRIGHT
                if x < r and y > h - r:
                    return True, HTBOTTOMLEFT
                if x > w - r and y > h - r:
                    return True, HTBOTTOMRIGHT

                # Raender
                if x < r:
                    return True, HTLEFT
                if x > w - r:
                    return True, HTRIGHT
                if y < r:
                    return True, HTTOP
                if y > h - r:
                    return True, HTBOTTOM

                # Title Bar -> HTCAPTION
                title_bar_hoehe = self._title_bar.height()
                if y < title_bar_hoehe:
                    if x < 40 or x > w - 180:
                        return True, HTCLIENT
                    return True, HTCAPTION

        except Exception:
            pass

        return super().nativeEvent(event_type, message)
