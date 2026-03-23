"""Wiederverwendbare modale Dialog-Komponente im App-Stil.

Ersetzt QMessageBox durch eigenes Overlay mit Theme-Support,
abgerundeten Ecken und App-eigenen Buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor
import qtawesome as qta


class OverlayDialog(QWidget):
    """Modaler Dialog als Overlay im App-Stil.

    Typen:
        - "bestaetigung": Ja/Nein-Dialog (z.B. PDF ueberschreiben?)
        - "fehler": Fehlermeldung mit OK-Button
        - "warnung": Warnung mit OK-Button
        - "info": Info mit OK-Button

    Verwendung:
        dialog = OverlayDialog(parent_widget)
        dialog.zeige(
            typ="bestaetigung",
            titel="PDF ueberschreiben?",
            nachricht="Es existiert bereits ein Protokoll. Ueberschreiben?",
            bei_bestaetigung=lambda: ...,
        )
    """

    # Ergebnis-Signals
    bestaetigt = Signal()
    abgelehnt = Signal()

    # Icon-Mapping pro Typ
    TYP_CONFIG = {
        "bestaetigung": {"icon": "ri.question-line", "farb_key": "warnung"},
        "fehler": {"icon": "ri.error-warning-line", "farb_key": "fehler"},
        "warnung": {"icon": "ri.alert-line", "farb_key": "warnung"},
        "info": {"icon": "ri.information-line", "farb_key": "info"},
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        self._farben = {}
        self._bei_bestaetigung = None
        self._bei_ablehnung = None
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut das Overlay mit zentriertem Dialog-Kasten auf."""
        # Gesamtes Overlay (Dimm-Hintergrund)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

        # Aeusseres Layout zum Zentrieren
        aussen = QVBoxLayout(self)
        aussen.setAlignment(Qt.AlignCenter)
        aussen.setContentsMargins(0, 0, 0, 0)

        # Dialog-Box
        self._dialog_box = QWidget()
        self._dialog_box.setFixedWidth(360)
        self._dialog_box.setMaximumHeight(240)

        box_layout = QVBoxLayout(self._dialog_box)
        box_layout.setContentsMargins(24, 20, 24, 20)
        box_layout.setSpacing(12)

        # Icon + Titel (horizontal)
        header = QHBoxLayout()
        header.setSpacing(12)

        self._icon_label = QLabel()
        self._icon_label.setFixedSize(28, 28)
        self._icon_label.setAlignment(Qt.AlignCenter)
        header.addWidget(self._icon_label)

        self._titel_label = QLabel()
        self._titel_label.setWordWrap(True)
        header.addWidget(self._titel_label, 1)
        box_layout.addLayout(header)

        # Nachricht
        self._nachricht_label = QLabel()
        self._nachricht_label.setWordWrap(True)
        self._nachricht_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        box_layout.addWidget(self._nachricht_label)

        box_layout.addStretch()

        # Buttons
        self._button_zeile = QHBoxLayout()
        self._button_zeile.setSpacing(12)
        self._button_zeile.addStretch()

        self._btn_abbrechen = QPushButton("Abbrechen")
        self._btn_abbrechen.setObjectName("secondaryButton")
        self._btn_abbrechen.setCursor(Qt.PointingHandCursor)
        self._btn_abbrechen.setFixedHeight(34)
        self._btn_abbrechen.setMinimumWidth(90)
        self._btn_abbrechen.clicked.connect(self._ablehnen)
        self._button_zeile.addWidget(self._btn_abbrechen)

        self._btn_ok = QPushButton("OK")
        self._btn_ok.setObjectName("primaryButton")
        self._btn_ok.setCursor(Qt.PointingHandCursor)
        self._btn_ok.setFixedHeight(34)
        self._btn_ok.setMinimumWidth(90)
        self._btn_ok.clicked.connect(self._bestaetigen)
        self._button_zeile.addWidget(self._btn_ok)

        box_layout.addLayout(self._button_zeile)
        aussen.addWidget(self._dialog_box)

    # --- Oeffentliche API ---

    def zeige(self, typ="info", titel="", nachricht="",
              bei_bestaetigung=None, bei_ablehnung=None,
              ok_text=None, abbrechen_text=None):
        """Zeigt den Dialog mit Animation an.

        Args:
            typ: "bestaetigung", "fehler", "warnung", "info"
            titel: Dialog-Titel
            nachricht: Dialog-Text
            bei_bestaetigung: Callback bei OK/Ja
            bei_ablehnung: Callback bei Abbrechen/Nein
            ok_text: Optionaler Text fuer OK-Button
            abbrechen_text: Optionaler Text fuer Abbrechen-Button
        """
        self._bei_bestaetigung = bei_bestaetigung
        self._bei_ablehnung = bei_ablehnung

        # Inhalt setzen
        config = self.TYP_CONFIG.get(typ, self.TYP_CONFIG["info"])
        icon_farbe = self._farben.get(config["farb_key"], "#42a5f5")

        # Icon als Pixmap
        icon = qta.icon(config["icon"], color=icon_farbe)
        self._icon_label.setPixmap(icon.pixmap(24, 24))

        self._titel_label.setText(titel)
        self._nachricht_label.setText(nachricht)

        # Buttons konfigurieren
        ist_bestaetigung = (typ == "bestaetigung")
        self._btn_abbrechen.setVisible(ist_bestaetigung)

        if ok_text:
            self._btn_ok.setText(ok_text)
        else:
            self._btn_ok.setText("Ja" if ist_bestaetigung else "OK")

        if abbrechen_text:
            self._btn_abbrechen.setText(abbrechen_text)

        # Groesse und Position
        if self.parent():
            self.setGeometry(self.parent().rect())

        self._wende_styles_an()
        self.show()
        self.raise_()
        self._animiere_einblenden()

    def schliesse(self):
        """Schliesst den Dialog."""
        self.hide()

    def setze_farben(self, farben: dict):
        """Aktualisiert die Farbpalette."""
        self._farben = farben
        self._wende_styles_an()

    # --- Interne Methoden ---

    def _wende_styles_an(self):
        """Wendet die aktuellen Farben auf den Dialog an."""
        if not self._farben:
            return

        f = self._farben
        self._dialog_box.setStyleSheet(f"""
            QWidget {{
                background-color: {f.get("basis_hell", "#363d52")};
                border-radius: 14px;
            }}
        """)
        self._titel_label.setStyleSheet(f"""
            font-family: "Plus Jakarta Sans";
            font-size: 14px;
            font-weight: 600;
            color: {f.get("text_primaer", "#e0e0e0")};
            background: transparent;
        """)
        self._nachricht_label.setStyleSheet(f"""
            font-size: 12px;
            color: {f.get("text_sekundaer", "#8a8fa0")};
            background: transparent;
            padding-left: 40px;
        """)
        self._icon_label.setStyleSheet("background: transparent;")

        # Buttons explizit stylen (Dialog-Box-Stylesheet ueberschreibt sonst alles)
        self._btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {f.get("akzent", "#ed1b24")};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {f.get("akzent_hover", "#d41920")};
            }}
            QPushButton:pressed {{
                background-color: {f.get("akzent_pressed", "#b8151c")};
            }}
        """)
        self._btn_abbrechen.setStyleSheet(f"""
            QPushButton {{
                background-color: {f.get("basis", "#2c3245")};
                color: {f.get("text_primaer", "#e0e0e0")};
                border: 1px solid {f.get("border", "#3a4158")};
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {f.get("hover_bg", "#3a4158")};
            }}
        """)

    def _animiere_einblenden(self):
        """Fade-Animation beim Einblenden."""
        opacity = QGraphicsOpacityEffect(self)
        opacity.setOpacity(0.0)
        self.setGraphicsEffect(opacity)

        self._fade_anim = QPropertyAnimation(opacity, b"opacity")
        self._fade_anim.setDuration(150)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_anim.finished.connect(lambda: self.setGraphicsEffect(None))
        self._fade_anim.start()

    def _bestaetigen(self):
        """OK/Ja geklickt."""
        self.schliesse()
        self.bestaetigt.emit()
        if self._bei_bestaetigung:
            self._bei_bestaetigung()

    def _ablehnen(self):
        """Abbrechen/Nein geklickt."""
        self.schliesse()
        self.abgelehnt.emit()
        if self._bei_ablehnung:
            self._bei_ablehnung()

    # --- Events ---

    def paintEvent(self, event):
        """Zeichnet halbtransparenten Dimm-Hintergrund."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        painter.end()

    def mousePressEvent(self, event):
        """Klick ausserhalb der Dialog-Box schliesst den Dialog."""
        dialog_rect = self._dialog_box.geometry()
        if not dialog_rect.contains(event.pos()):
            if self._btn_abbrechen.isVisible():
                # Bestaetigungs-Dialog: Klick ausserhalb = Abbrechen
                self._ablehnen()
            else:
                # Info/Fehler/Warnung: Klick ausserhalb = OK
                self._bestaetigen()
        event.accept()

    def keyPressEvent(self, event):
        """Escape schliesst den Dialog."""
        if event.key() == Qt.Key_Escape:
            if self._btn_abbrechen.isVisible():
                self._ablehnen()
            else:
                self._bestaetigen()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._bestaetigen()
