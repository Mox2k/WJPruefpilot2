"""Gemeinsame Basisklasse fuer Detail-Seiten (Temp + VDE).

Enthaelt duplizierten Code, der in beiden Detail-Seiten identisch war:
Validierung, Spinner, Fehleranzeige, PDF-Feedback, Hilfsmethoden.
"""

import os
import glob

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSize, QThread, QTimer
import qtawesome as qta

from settings import Settings


class PdfWorker(QThread):
    """Generiert PDFs in einem Hintergrund-Thread."""

    fertig = Signal(bool, str)  # (erfolg, datei_pfad_oder_fehler)

    def __init__(self, generator, datei_pfad):
        super().__init__()
        self._generator = generator
        self._datei_pfad = datei_pfad

    def run(self):
        try:
            erfolg = self._generator.generate_pdf(self._datei_pfad)
            if erfolg:
                self.fertig.emit(True, self._datei_pfad)
            else:
                self.fertig.emit(False, "PDF-Generierung fehlgeschlagen")
        except Exception as e:
            self.fertig.emit(False, str(e))


class DetailBasis(QWidget):
    """Basisklasse mit gemeinsamen Methoden fuer Detail-Seiten."""

    pdf_erstellt = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = Settings("settings.ini")
        self._waage_daten = None
        self._aktuelle_farben = {}
        self._dialog = None
        self._spinner_timer = None
        self._spinner_winkel = 0
        self._kalibrier_nr = ""
        self._eingaben_cache = {}
        self._validierte_felder = {}

    # --- Validierung ---

    def _validiere_dezimal(self, text):
        """Validiert eine Dezimalzahl (Komma und Punkt erlaubt).
        Gibt Fehlermeldung oder None zurueck."""
        text = text.strip().replace(",", ".")
        if not text:
            return "Pflichtfeld"
        try:
            float(text)
            return None
        except ValueError:
            return "Ungültige Zahl"

    def _validiere_datum(self, text):
        """Validiert ein Datum im Format TT.MM.JJJJ.
        Gibt Fehlermeldung oder None zurueck."""
        text = text.strip()
        if not text:
            return "Pflichtfeld"
        teile = text.split(".")
        if len(teile) != 3:
            return "Format: TT.MM.JJJJ"
        try:
            tag, monat, jahr = int(teile[0]), int(teile[1]), int(teile[2])
            if not (1 <= tag <= 31 and 1 <= monat <= 12 and 2000 <= jahr <= 2099):
                return "Ungültiges Datum"
            return None
        except ValueError:
            return "Format: TT.MM.JJJJ"

    def _live_validierung(self, feld_name):
        """Fuehrt Live-Validierung fuer ein Feld durch und aktualisiert UI."""
        feld = self._validierte_felder.get(feld_name)
        if not feld or not feld["validator"]:
            return

        text = feld["input"].text()
        fehler_text = feld["validator"](text)

        if fehler_text:
            feld["input"].setObjectName("formInputFehler")
            feld["fehler"].setText(fehler_text)
            feld["fehler"].setVisible(True)
        else:
            feld["input"].setObjectName("formInput")
            feld["fehler"].setText("")
            feld["fehler"].setVisible(False)

        # Stylesheet neu anwenden (ObjectName hat sich geaendert)
        feld["input"].style().unpolish(feld["input"])
        feld["input"].style().polish(feld["input"])

    def _validiere_alle(self):
        """Validiert alle Felder und gibt True zurueck wenn alles OK ist."""
        alle_ok = True
        for name, feld in self._validierte_felder.items():
            if feld["validator"]:
                text = feld["input"].text()
                fehler_text = feld["validator"](text)
                if fehler_text:
                    feld["input"].setObjectName("formInputFehler")
                    feld["fehler"].setText(fehler_text)
                    feld["fehler"].setVisible(True)
                    feld["input"].style().unpolish(feld["input"])
                    feld["input"].style().polish(feld["input"])
                    alle_ok = False
        return alle_ok

    def _setze_felder_zurueck(self):
        """Setzt alle Validierungszustaende zurueck."""
        for feld in self._validierte_felder.values():
            feld["input"].setObjectName("formInput")
            feld["fehler"].setVisible(False)
            feld["input"].style().unpolish(feld["input"])
            feld["input"].style().polish(feld["input"])

    # --- Hilfsmethoden ---

    def _form_label(self, text, tooltip=None):
        """Erstellt ein Formularlabel, optional mit Info-Icon und Tooltip."""
        if not tooltip:
            lbl = QLabel(text)
            lbl.setObjectName("formLabel")
            return lbl

        # Container mit Label + Info-Icon
        container = QWidget()
        container.setObjectName("detailScrollInhalt")
        zeile = QHBoxLayout(container)
        zeile.setContentsMargins(0, 0, 0, 0)
        zeile.setSpacing(6)

        lbl = QLabel(text)
        lbl.setObjectName("formLabel")
        zeile.addWidget(lbl)

        info_btn = QLabel()
        info_btn.setObjectName("detailScrollInhalt")
        info_btn.setFixedSize(16, 16)
        info_farbe = self._aktuelle_farben.get("info", "#42a5f5")
        info_btn.setPixmap(
            qta.icon("ri.information-line", color=info_farbe).pixmap(14, 14)
        )
        info_btn.setToolTip(tooltip)
        info_btn.setCursor(Qt.WhatsThisCursor)
        zeile.addWidget(info_btn)

        zeile.addStretch()
        return container

    def _parse_dezimal(self, text):
        """Konvertiert Text mit Komma oder Punkt zu float."""
        text = text.strip().replace(",", ".")
        if not text:
            raise ValueError("leer")
        return float(text)

    def _zeige_fehler(self, text):
        """Zeigt eine Fehlermeldung in der Aktionszeile."""
        self._fehler_label.setText(text)
        self._fehler_label.setVisible(True)

    def _verstecke_fehler(self):
        """Versteckt die Fehlermeldung."""
        self._fehler_label.setVisible(False)

    def _wj_nummer(self):
        """Gibt die aktuelle WJ-Nummer zurueck."""
        if self._waage_daten:
            return str(self._waage_daten[0]) if self._waage_daten[0] else ""
        return ""

    def _finde_existierendes_pdf(self, wj_nummer, prefix="TK"):
        """Sucht im Protokoll-Ordner nach einem vorhandenen PDF fuer diese Waage.

        Args:
            wj_nummer: Die WJ-Nummer der Waage.
            prefix: "TK" fuer Temp, "VDE" fuer VDE.
        """
        if not wj_nummer:
            return None
        protokoll_pfad = self._settings.get_protokoll_path()
        if not protokoll_pfad or not os.path.isdir(protokoll_pfad):
            return None
        treffer = glob.glob(os.path.join(protokoll_pfad, f"{prefix}_*_{wj_nummer}.pdf"))
        if treffer:
            # Neuestes nehmen (nach Aenderungsdatum)
            return max(treffer, key=os.path.getmtime)
        return None

    # --- Spinner ---

    def _starte_spinner(self):
        """Zeigt einen Spinner neben dem PDF-Button waehrend der Generierung."""
        self._pdf_btn.setEnabled(False)
        self._spinner_winkel = 0

        # Spinner im Feedback-Bereich anzeigen
        akzent = self._aktuelle_farben.get("akzent", "#ed1b24")
        self._pdf_feedback.setIcon(qta.icon("ri.loader-5-line", color=akzent))
        self._pdf_feedback.setIconSize(QSize(24, 24))
        self._pdf_feedback.setVisible(True)
        self._pdf_feedback.setToolTip("")

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(50)
        self._spinner_timer.timeout.connect(self._spinner_tick)
        self._spinner_timer.start()

    def _spinner_tick(self):
        """Aktualisiert den Spinner-Winkel und das Icon."""
        self._spinner_winkel = (self._spinner_winkel + 30) % 360
        akzent = self._aktuelle_farben.get("akzent", "#ed1b24")
        self._pdf_feedback.setIcon(qta.icon("ri.loader-5-line", color=akzent,
                                             rotated=self._spinner_winkel))

    def _stoppe_spinner(self):
        """Stellt den PDF-Button wieder her."""
        if self._spinner_timer:
            self._spinner_timer.stop()
            self._spinner_timer = None
        self._pdf_btn.setEnabled(True)
        self._pdf_feedback.setVisible(False)
        self._pdf_feedback.setToolTip("PDF öffnen")

    # --- PDF-Feedback ---

    def _zeige_pdf_feedback(self, pfad):
        """Zeigt gruenes Feedback-Icon (klickbar zum Oeffnen)."""
        erfolg_farbe = self._aktuelle_farben.get("erfolg", "#4caf50")
        self._pdf_feedback.setIcon(
            qta.icon("ri.file-text-line", color=erfolg_farbe)
        )
        self._pdf_feedback.setIconSize(QSize(24, 24))
        self._pdf_feedback.setVisible(True)

        # Klick oeffnet PDF
        try:
            self._pdf_feedback.clicked.disconnect()
        except RuntimeError:
            pass
        self._pdf_feedback.clicked.connect(lambda: os.startfile(pfad))

    def _pdf_fertig(self, erfolg, ergebnis):
        """Callback wenn der PDF-Worker fertig ist."""
        self._stoppe_spinner()

        if erfolg:
            self._zeige_pdf_feedback(ergebnis)
            self.pdf_erstellt.emit(self._kalibrier_nr)
        else:
            self._zeige_fehler(f"Fehler: {ergebnis}")

    # --- Oeffentliche Methoden ---

    def setze_dialog(self, dialog):
        """Setzt die Referenz zur Dialog-Komponente."""
        self._dialog = dialog

    def loesche_eingaben_cache(self):
        """Loescht alle gespeicherten Eingaben (z.B. bei Auftragswechsel)."""
        self._eingaben_cache.clear()
