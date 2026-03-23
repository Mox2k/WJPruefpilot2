"""Collapsible Sidebar mit WJ-Logo und Icon-Navigation."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtSvgWidgets import QSvgWidget
import qtawesome as qta


class SidebarButton(QPushButton):
    """Ein einzelner Sidebar-Button mit Icon, optionalem Label und Active-Indicator."""

    def __init__(self, icon_name: str, text: str, seiten_name: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarButton")
        self._icon_name = icon_name
        self._text = text
        self._seiten_name = seiten_name
        self._icon_farbe = "#8a8fa0"
        self._icon_farbe_aktiv = "#ffffff"
        self._indicator_farbe = "#ed1b24"
        self._ist_aktiv = False

        self.setIcon(qta.icon(icon_name, color=self._icon_farbe))
        self.setIconSize(QSize(22, 22))
        self.setText("")
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(text)

    def paintEvent(self, event):
        """Zeichnet den Button mit optionalem Active-Indicator."""
        super().paintEvent(event)
        if self._ist_aktiv:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self._indicator_farbe))
            # Vertikaler Balken links (3px breit, 20px hoch, zentriert)
            balken_hoehe = 20
            y = (self.height() - balken_hoehe) / 2
            painter.drawRoundedRect(QRectF(0, y, 3, balken_hoehe), 1.5, 1.5)
            painter.end()

    def setze_aktiv(self, aktiv: bool):
        """Setzt den aktiven Zustand des Buttons."""
        self._ist_aktiv = aktiv
        farbe = self._icon_farbe_aktiv if aktiv else self._icon_farbe
        self.setIcon(qta.icon(self._icon_name, color=farbe))
        self.setProperty("aktiv", aktiv)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def zeige_label(self, sichtbar: bool):
        """Zeigt oder versteckt das Text-Label."""
        self.setText(f"  {self._text}" if sichtbar else "")

    def aktualisiere_farben(self, icon_farbe: str, icon_farbe_aktiv: str,
                            indicator_farbe: str = ""):
        """Aktualisiert die Icon-Farben bei Theme-Wechsel."""
        self._icon_farbe = icon_farbe
        self._icon_farbe_aktiv = icon_farbe_aktiv
        if indicator_farbe:
            self._indicator_farbe = indicator_farbe
        farbe = self._icon_farbe_aktiv if self._ist_aktiv else self._icon_farbe
        self.setIcon(qta.icon(self._icon_name, color=farbe))
        self.update()


class Sidebar(QWidget):
    """Collapsible Sidebar mit WJ-Logo, Navigation und Settings/Info."""

    navigation_geklickt = Signal(str)
    settings_geklickt = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._buttons = []
        self._aktiver_button = None
        self._ist_ausgeklappt = False
        self._ist_dark = True
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut die Sidebar auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)

        # Logo-Bereich: Icon + optionaler Text "Pruefpilot"
        self._logo_container = QWidget()
        self._logo_container.setFixedHeight(44)
        self._logo_container.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(self._logo_container)
        logo_layout.setContentsMargins(8, 4, 8, 4)
        logo_layout.setSpacing(8)

        # WJ-Logomark (klein, immer sichtbar)
        basis_pfad = os.path.dirname(os.path.dirname(__file__))
        self._logo_dark_pfad = os.path.join(basis_pfad, "assets", "icons", "Asset 10.svg")
        self._logo_light_pfad = os.path.join(basis_pfad, "assets", "icons", "Asset 9.svg")

        self._logo_widget = QSvgWidget(self._logo_dark_pfad)
        self._logo_widget.setFixedSize(32, 18)
        logo_layout.addWidget(self._logo_widget, alignment=Qt.AlignVCenter)

        # Text "Pruefpilot" (nur sichtbar wenn ausgeklappt)
        self._logo_text = QLabel("Pruefpilot")
        self._logo_text.setObjectName("logoText")
        self._logo_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        self._logo_text.setVisible(False)
        logo_layout.addWidget(self._logo_text, alignment=Qt.AlignVCenter)

        logo_layout.addStretch()
        layout.addWidget(self._logo_container)
        layout.addSpacing(12)

        # Navigations-Buttons (oben)
        self._btn_auftraege = SidebarButton(
            "ri.survey-line", "SimplyCal", "auftraege"
        )
        self._btn_auftraege.clicked.connect(
            lambda: self._navigation_klick(self._btn_auftraege)
        )
        layout.addWidget(self._btn_auftraege)
        self._buttons.append(self._btn_auftraege)

        # Spacer
        layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Settings-Button (unten)
        self._btn_settings = SidebarButton(
            "ri.settings-line", "Einstellungen", "settings"
        )
        self._btn_settings.clicked.connect(
            lambda: self.settings_geklickt.emit()
        )
        layout.addWidget(self._btn_settings)
        self._buttons.append(self._btn_settings)

        # Info-Button (unten)
        self._btn_info = SidebarButton(
            "ri.information-line", "Info", "info"
        )
        self._btn_info.clicked.connect(
            lambda: self._navigation_klick(self._btn_info)
        )
        layout.addWidget(self._btn_info)
        self._buttons.append(self._btn_info)

        # Auftraege als Standard aktiv
        self._navigation_klick(self._btn_auftraege)

    def _navigation_klick(self, button: SidebarButton):
        """Behandelt Klick auf einen Navigations-Button."""
        if self._aktiver_button:
            self._aktiver_button.setze_aktiv(False)
        button.setze_aktiv(True)
        self._aktiver_button = button
        self.navigation_geklickt.emit(button._seiten_name)

    def setze_aktive_seite(self, seiten_name: str):
        """Setzt den aktiven Button programmatisch (ohne Signal zu emittieren)."""
        for btn in self._buttons:
            if btn._seiten_name == seiten_name:
                if self._aktiver_button:
                    self._aktiver_button.setze_aktiv(False)
                btn.setze_aktiv(True)
                self._aktiver_button = btn
                break

    def aktualisiere_labels(self, ausgeklappt: bool):
        """Zeigt oder versteckt alle Button-Labels und Logo-Text."""
        self._ist_ausgeklappt = ausgeklappt
        self._logo_text.setVisible(ausgeklappt)
        for btn in self._buttons:
            btn.zeige_label(ausgeklappt)

    def aktualisiere_theme(self, ist_dark: bool, farben: dict):
        """Aktualisiert Farben bei Theme-Wechsel."""
        self._ist_dark = ist_dark
        icon_farbe = farben["icon_farbe"]
        text_aktiv = farben["text_aktiv"]
        text_primaer = farben["text_primaer"]

        # Button-Farben
        indicator = farben.get("indicator", "#ed1b24")
        for btn in self._buttons:
            btn.aktualisiere_farben(icon_farbe, text_aktiv, indicator)

        # Logo SVG wechseln (dark/light Variante)
        logo_pfad = self._logo_dark_pfad if ist_dark else self._logo_light_pfad
        if os.path.exists(logo_pfad):
            self._logo_widget.load(logo_pfad)

        # Logo-Text Farbe
        self._logo_text.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {text_primaer};"
        )
