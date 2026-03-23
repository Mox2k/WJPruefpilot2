"""VDE-Pruefung Detail-Seite mit 3-Seiten-Wizard."""

import os
import glob
from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit, QScrollArea,
    QStackedWidget, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QThread, QTimer
import qtawesome as qta

from settings import Settings
from pdf_vde_generator import PDFGeneratorVDE


class PdfWorkerVDE(QThread):
    """Generiert VDE-PDFs in einem Hintergrund-Thread."""

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


# 13 Sichtpruefungs-Punkte (Keys muessen exakt mit pdf_vde_generator uebereinstimmen)
SICHTPRUEFUNG_PUNKTE = [
    "Typenschild/Warnhinweis/Kennzeichnungen",
    "Gehäuse/Schutzabdeckungen",
    "Anschlussleitung/stecker,Anschlussklemmen und -adern",
    "Biegeschutz/Zugentlastung",
    "Leitungshalterungen, Sicherungshalter, usw.",
    "Kühlluftöffnungen/Luftfilter",
    "Schalter, Steuer, Einstell- und Sicherheitsvorrichtungen",
    "Bemessung der zugänglichen Gerätesicherung",
    "Beuteile und Baugruppen",
    "Anzeichen von Überlastung/unsachgemäßem Gebrauch",
    "Sicherheitsbeeinträchtigende Verschmutzung/Korrission/Alterung",
    "Mechanische Gefährdung",
    "Unzulässige Eingriffe und Änderungen",
]

# Relevante Messwerte je Schutzklasse
MESSWERTE_PRO_SK = {
    1: ["rpe", "riso", "ipe"],
    2: ["riso", "ib"],
    3: ["riso"],
}

MESSWERT_LABELS = {
    "rpe": ("Schutzleiterwiderstand RPE", "Ω"),
    "riso": ("Isolationswiderstand RISO", "MΩ"),
    "ipe": ("Schutzleiterstrom IPE", "mA"),
    "ib": ("Differenzstrom IB", "mA"),
}


class DetailVDESeite(QWidget):
    """Detail-Seite fuer VDE-Pruefung als 3-Seiten-Wizard."""

    pdf_erstellt = Signal(str)  # Kalibrierscheinnummer der erstellten PDF

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("detailSeite")
        self._settings = Settings("settings.ini")
        self._waage_daten = None
        self._kundennummer = None
        self._aktuelle_farben = {}
        self._worker = None
        self._spinner_winkel = 0
        self._spinner_timer = None
        self._dialog = None
        self._validierte_felder = {}  # name -> {"input": QLineEdit, "fehler": QLabel, "validator": fn}
        self._eingaben_cache = {}  # WJ-Nummer -> Dict
        self._checkboxes = {}  # Key -> QCheckBox (Sichtpruefung)
        self._messwert_widgets = {}  # key -> {"container": QWidget, ...}
        self._aktuelle_seite = 0
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut den 3-Seiten-Wizard auf."""
        haupt_layout = QVBoxLayout(self)
        haupt_layout.setContentsMargins(0, 0, 0, 0)
        haupt_layout.setSpacing(0)

        # Scrollbereich
        scroll = QScrollArea()
        scroll.setObjectName("detailScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_inhalt = QWidget()
        scroll_inhalt.setObjectName("detailScrollInhalt")
        self._content = QVBoxLayout(scroll_inhalt)
        self._content.setContentsMargins(32, 20, 32, 16)
        self._content.setSpacing(12)

        self._erstelle_header()
        self._erstelle_stepper()
        self._erstelle_seiten()
        self._content.addStretch()

        scroll.setWidget(scroll_inhalt)
        haupt_layout.addWidget(scroll)

        # Aktionszeile (fixiert unten)
        self._erstelle_aktionszeile(haupt_layout)

        # Erste Seite anzeigen
        self._zeige_seite(0)

    # --- Header ---

    def _erstelle_header(self):
        """Header: Gross 'VDE-Prüfung', darunter kleiner Waagen-Info."""
        self._titel = QLabel("VDE-Prüfung")
        self._titel.setObjectName("detailSeitenTitel")
        self._content.addWidget(self._titel)

        self._waagen_info = QLabel("—")
        self._waagen_info.setObjectName("detailWaagenInfo")
        self._content.addWidget(self._waagen_info)

    # --- Stepper ---

    def _erstelle_stepper(self):
        """Erstellt eine dezente Stepper-Navigation mit 3 klickbaren Schritten."""
        self._stepper_widget = QWidget()
        self._stepper_widget.setObjectName("detailScrollInhalt")
        stepper_layout = QHBoxLayout(self._stepper_widget)
        stepper_layout.setContentsMargins(0, 0, 0, 0)
        stepper_layout.setSpacing(0)

        self._stepper_labels = []
        self._stepper_punkte = []
        self._stepper_linien = []

        schritte = ["Grundeinstellungen", "Sichtprüfung", "Messwerte"]

        for i, text in enumerate(schritte):
            if i > 0:
                linie = QWidget()
                linie.setFixedHeight(1)
                linie.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                stepper_layout.addWidget(linie, alignment=Qt.AlignVCenter)
                self._stepper_linien.append(linie)

            schritt_widget = QWidget()
            schritt_widget.setObjectName("detailScrollInhalt")
            schritt_widget.setCursor(Qt.PointingHandCursor)
            schritt_layout = QHBoxLayout(schritt_widget)
            schritt_layout.setContentsMargins(6, 4, 6, 4)
            schritt_layout.setSpacing(6)
            schritt_layout.setAlignment(Qt.AlignCenter)

            punkt = QLabel(str(i + 1))
            punkt.setFixedSize(24, 24)
            punkt.setAlignment(Qt.AlignCenter)
            schritt_layout.addWidget(punkt)
            self._stepper_punkte.append(punkt)

            label = QLabel(text)
            label.setObjectName("formLabel")
            schritt_layout.addWidget(label)
            self._stepper_labels.append(label)

            schritt_widget.mousePressEvent = lambda e, idx=i: self._zeige_seite(idx)
            stepper_layout.addWidget(schritt_widget)

        self._content.addWidget(self._stepper_widget)

    def _aktualisiere_stepper(self):
        """Aktualisiert Stepper-Farben basierend auf aktuellem Schritt und Theme."""
        akzent = self._aktuelle_farben.get("akzent", "#ed1b24")
        text_p = self._aktuelle_farben.get("text_primaer", "#e0e0e0")
        text_s = self._aktuelle_farben.get("text_sekundaer", "#8a8fa0")
        basis = self._aktuelle_farben.get("basis", "#2c3245")
        border = self._aktuelle_farben.get("border", "#3a4158")

        for i, punkt in enumerate(self._stepper_punkte):
            if i == self._aktuelle_seite:
                punkt.setStyleSheet(f"""
                    background-color: {akzent};
                    color: #ffffff;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                """)
                self._stepper_labels[i].setStyleSheet(f"color: {text_p}; font-size: 11px; font-weight: 600;")
            elif i < self._aktuelle_seite:
                punkt.setStyleSheet(f"""
                    background-color: {akzent};
                    color: #ffffff;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                """)
                self._stepper_labels[i].setStyleSheet(f"color: {text_p}; font-size: 11px;")
            else:
                punkt.setStyleSheet(f"""
                    background-color: {basis};
                    color: {text_s};
                    border: 1px solid {border};
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                """)
                self._stepper_labels[i].setStyleSheet(f"color: {text_s}; font-size: 11px;")

        for i, linie in enumerate(self._stepper_linien):
            if i < self._aktuelle_seite:
                linie.setStyleSheet(f"background-color: {akzent};")
            else:
                linie.setStyleSheet(f"background-color: {border};")

    # --- Wizard-Seiten ---

    def _erstelle_seiten(self):
        """Erstellt die drei Wizard-Seiten als QStackedWidget."""
        self._seiten_stack = QStackedWidget()
        self._seiten_stack.setObjectName("detailScrollInhalt")

        self._erstelle_seite1()
        self._erstelle_seite2()
        self._erstelle_seite3()

        self._content.addWidget(self._seiten_stack)

    def _zeige_seite(self, index):
        """Wechselt zur angegebenen Wizard-Seite."""
        self._aktuelle_seite = index
        self._seiten_stack.setCurrentIndex(index)
        self._aktualisiere_stepper()
        self._aktualisiere_navigation()

    # --- Seite 1: Grundeinstellungen ---

    def _erstelle_trennlinie(self):
        """Erstellt eine gestrichelte Trennlinie zwischen Formular-Gruppen."""
        linie = QFrame()
        linie.setObjectName("gruppenTrennlinie")
        linie.setFrameShape(QFrame.HLine)
        return linie

    def _erstelle_seite1(self):
        """VDE-Typ, Schutzklasse, elektrische Daten, Messgeraet, Datum."""
        seite = QWidget()
        seite.setObjectName("detailScrollInhalt")
        layout = QVBoxLayout(seite)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Infobox
        self._infobox1 = self._erstelle_infobox(
            "Wählen Sie die VDE-Prüfungsart und geben Sie die elektrischen "
            "Grunddaten des Prüflings ein. Die Schutzklasse bestimmt, welche "
            "Messwerte auf Seite 3 relevant sind."
        )
        layout.addWidget(self._infobox1["widget"])

        # --- Messgerät + Prüfdatum ---
        mg_datum_zeile = QHBoxLayout()
        mg_datum_zeile.setSpacing(16)

        mg_box = QVBoxLayout()
        mg_box.setSpacing(4)
        mg_box.addWidget(self._form_label(
            "VDE-Messgerät",
            tooltip="VDE-Messgerät aus den Einstellungen"
        ))
        self._messgeraet_dropdown = QComboBox()
        self._messgeraet_dropdown.setObjectName("formDropdown")
        self._messgeraet_dropdown.setMinimumWidth(280)
        self._messgeraet_dropdown.setFixedHeight(36)
        self._lade_messgeraete()
        mg_box.addWidget(self._messgeraet_dropdown)

        self._messgeraet_fehler = QLabel("")
        self._messgeraet_fehler.setObjectName("formFehler")
        self._messgeraet_fehler.setVisible(False)
        mg_box.addWidget(self._messgeraet_fehler)
        mg_datum_zeile.addLayout(mg_box)

        datum_box = QVBoxLayout()
        datum_box.setSpacing(4)
        datum_box.addWidget(self._form_label("Prüfdatum"))
        self._datum_input = self._erstelle_validiertes_feld(
            "datum", breite=130, standard=date.today().strftime("%d.%m.%Y"),
            validator=self._validiere_datum
        )
        datum_box.addWidget(self._datum_input["input"])
        datum_box.addWidget(self._datum_input["fehler"])
        mg_datum_zeile.addLayout(datum_box)

        mg_datum_zeile.addStretch()
        layout.addLayout(mg_datum_zeile)

        layout.addWidget(self._erstelle_trennlinie())

        # --- Gruppe 1: VDE-Typ + Schutzklasse ---
        obere_zeile = QHBoxLayout()
        obere_zeile.setSpacing(32)

        # VDE-Typ
        vde_box = QVBoxLayout()
        vde_box.setSpacing(4)
        vde_titel = QLabel("VDE-Prüfungsart")
        vde_titel.setObjectName("formGruppenTitel")
        vde_box.addWidget(vde_titel)

        vde701_zeile = QHBoxLayout()
        vde701_zeile.setSpacing(10)
        self._rb_701 = QPushButton("  VDE 701")
        self._rb_701.setCursor(Qt.PointingHandCursor)
        self._rb_701.setFixedHeight(36)
        self._rb_701.setProperty("vde_aktiv", True)
        self._rb_701.clicked.connect(lambda: self._waehle_vde_typ(0))
        vde701_zeile.addWidget(self._rb_701)

        self._pruefungsart_dropdown = QComboBox()
        self._pruefungsart_dropdown.setObjectName("formDropdown")
        self._pruefungsart_dropdown.setFixedHeight(36)
        self._pruefungsart_dropdown.setMinimumWidth(180)
        self._pruefungsart_dropdown.addItems(["Neugerät", "Erweiterung", "Instandsetzung"])
        vde701_zeile.addWidget(self._pruefungsart_dropdown)
        vde_box.addLayout(vde701_zeile)

        self._rb_702 = QPushButton("  VDE 702 — Wiederholungsprüfung")
        self._rb_702.setCursor(Qt.PointingHandCursor)
        self._rb_702.setFixedHeight(36)
        self._rb_702.setProperty("vde_aktiv", False)
        self._rb_702.clicked.connect(lambda: self._waehle_vde_typ(1))
        vde_box.addWidget(self._rb_702)

        self._vde_typ_aktiv = 0  # 0 = 701, 1 = 702
        obere_zeile.addLayout(vde_box)

        # Schutzklasse (rechts daneben)
        sk_box = QVBoxLayout()
        sk_box.setSpacing(4)
        sk_box.addWidget(self._form_label(
            "Schutzklasse",
            tooltip="Schutzklasse I: Schutzleiter, II: Schutzisolierung, III: Schutzkleinspannung"
        ))
        self._sk_dropdown = QComboBox()
        self._sk_dropdown.setObjectName("formDropdown")
        self._sk_dropdown.setFixedHeight(36)
        self._sk_dropdown.setFixedWidth(80)
        self._sk_dropdown.addItems(["I", "II", "III"])
        self._sk_dropdown.currentIndexChanged.connect(self._schutzklasse_geaendert)
        sk_box.addWidget(self._sk_dropdown)
        sk_box.addStretch()
        obere_zeile.addLayout(sk_box)

        obere_zeile.addStretch()
        layout.addLayout(obere_zeile)

        layout.addWidget(self._erstelle_trennlinie())

        # --- Gruppe 2: Elektrische Daten ---
        elek_titel = QLabel("Elektrische Daten")
        elek_titel.setObjectName("formGruppenTitel")
        layout.addWidget(elek_titel)

        elek_zeile = QHBoxLayout()
        elek_zeile.setSpacing(16)

        elek_zeile.addLayout(self._feld_mit_einheit("Nennspannung", "nennspannung", "230", "V"))
        elek_zeile.addLayout(self._feld_mit_einheit("Nennstrom", "nennstrom", "", "A"))
        elek_zeile.addLayout(self._feld_mit_einheit("Nennleistung", "nennleistung", "", "W"))
        elek_zeile.addLayout(self._feld_mit_einheit("Frequenz", "frequenz", "50", "Hz"))
        elek_zeile.addLayout(self._feld_mit_einheit("cos φ", "cosphi", "1", ""))
        elek_zeile.addStretch()
        layout.addLayout(elek_zeile)

        layout.addStretch()
        self._seiten_stack.addWidget(seite)

    def _waehle_vde_typ(self, typ):
        """Wechselt zwischen VDE 701 und 702."""
        self._vde_typ_aktiv = typ
        self._rb_701.setProperty("vde_aktiv", typ == 0)
        self._rb_702.setProperty("vde_aktiv", typ == 1)
        self._pruefungsart_dropdown.setEnabled(typ == 0)
        self._aktualisiere_vde_typ_styles()

    def _aktualisiere_vde_typ_styles(self):
        """Aktualisiert VDE-Typ-Button-Styles."""
        akzent = self._aktuelle_farben.get("akzent", "#ed1b24")
        basis = self._aktuelle_farben.get("basis", "#2c3245")
        border = self._aktuelle_farben.get("border", "#3a4158")
        text_p = self._aktuelle_farben.get("text_primaer", "#e0e0e0")
        text_s = self._aktuelle_farben.get("text_sekundaer", "#8a8fa0")

        for btn, aktiv in [(self._rb_701, self._vde_typ_aktiv == 0),
                           (self._rb_702, self._vde_typ_aktiv == 1)]:
            if aktiv:
                icon = qta.icon("ri.radio-button-fill", color=akzent)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {text_p}; font-size: 13px; font-weight: 500;
                        text-align: left; padding-left: 4px;
                    }}
                """)
            else:
                icon = qta.icon("ri.radio-button-line", color=text_s)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {text_s}; font-size: 13px; font-weight: 500;
                        text-align: left; padding-left: 4px;
                    }}
                """)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))

    def _schutzklasse_geaendert(self, index):
        """Aktualisiert sichtbare Messwertfelder basierend auf Schutzklasse."""
        sk = index + 1  # 1, 2 oder 3
        relevante = MESSWERTE_PRO_SK.get(sk, [])
        for key, widgets in self._messwert_widgets.items():
            sichtbar = key in relevante
            widgets["container"].setVisible(sichtbar)

    # --- Seite 2: Sichtpruefung ---

    def _erstelle_seite2(self):
        """13 Pruefpunkte als Icon-Buttons in zwei Spalten."""
        seite = QWidget()
        seite.setObjectName("detailScrollInhalt")
        layout = QVBoxLayout(seite)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Infobox
        self._infobox2 = self._erstelle_infobox(
            "Bewerten Sie jeden Prüfpunkt der Sichtprüfung. "
            "Grün = bestanden (i.O.), rot = nicht bestanden (n.i.O.). "
            "Alle Punkte sind standardmäßig auf bestanden gesetzt."
        )
        layout.addWidget(self._infobox2["widget"])

        gruppe_titel = QLabel("Sichtprüfung")
        gruppe_titel.setObjectName("formGruppenTitel")
        layout.addWidget(gruppe_titel)

        # Zwei-Spalten-Grid
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for i, punkt in enumerate(SICHTPRUEFUNG_PUNKTE):
            spalte = i % 2
            zeile_nr = i // 2

            btn = QPushButton(f"  {punkt}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setProperty("bestanden", True)
            btn.clicked.connect(lambda _, b=btn: self._toggle_sichtpruefung(b))
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; "
                "text-align: left; font-size: 12px; padding-left: 2px; }"
            )
            self._checkboxes[punkt] = btn
            grid.addWidget(btn, zeile_nr, spalte)

        layout.addLayout(grid)
        layout.addStretch()
        self._seiten_stack.addWidget(seite)

    def _toggle_sichtpruefung(self, btn):
        """Schaltet einen Sichtpruefungs-Punkt um."""
        aktuell = btn.property("bestanden")
        btn.setProperty("bestanden", not aktuell)
        self._aktualisiere_sichtpruefung_icon(btn)

    def _aktualisiere_sichtpruefung_icon(self, btn):
        """Setzt Icon fuer einen Sichtpruefungs- oder Funktionspruefungs-Button."""
        bestanden = btn.property("bestanden")
        if bestanden:
            farbe = self._aktuelle_farben.get("erfolg", "#4caf50")
            btn.setIcon(qta.icon("ri.checkbox-circle-line", color=farbe))
        else:
            farbe = self._aktuelle_farben.get("fehler", "#f44336")
            btn.setIcon(qta.icon("ri.close-circle-line", color=farbe))
        btn.setIconSize(QSize(22, 22))
        text_farbe = self._aktuelle_farben.get("text_primaer", "#e0e0e0")
        btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"text-align: left; font-size: 13px; padding-left: 2px; color: {text_farbe}; }}"
        )

    def _aktualisiere_alle_sichtpruefung_icons(self):
        """Aktualisiert alle Sichtpruefungs-Icons (z.B. bei Theme-Wechsel)."""
        for btn in self._checkboxes.values():
            self._aktualisiere_sichtpruefung_icon(btn)

    def _aktualisiere_toggle_style(self, btn):
        """Setzt Icon fuer den Funktionspruefungs-Button (gleicher Stil wie Sichtpruefung)."""
        self._aktualisiere_sichtpruefung_icon(btn)

    # --- Seite 3: Messwerte & Ergebnis ---

    def _erstelle_seite3(self):
        """Messwerte (dynamisch nach Schutzklasse), Funktionspruefung, Bemerkungen."""
        seite = QWidget()
        seite.setObjectName("detailScrollInhalt")
        layout = QVBoxLayout(seite)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Infobox
        self._infobox3 = self._erstelle_infobox(
            "Geben Sie die Messwerte Ihres VDE-Prüfgeräts ein. "
            "Je nach Schutzklasse sind unterschiedliche Messungen relevant. "
            "Das Prüfergebnis wird automatisch anhand der Grenzwerte ermittelt."
        )
        layout.addWidget(self._infobox3["widget"])

        # Zweispaltiges Layout: Messwerte links, Bemerkungen+Funktion rechts
        zwei_spalten = QHBoxLayout()
        zwei_spalten.setSpacing(24)

        # --- Linke Spalte: Messwerte ---
        links = QVBoxLayout()
        links.setSpacing(10)

        mess_titel = QLabel("Messwerte")
        mess_titel.setObjectName("formGruppenTitel")
        links.addWidget(mess_titel)

        for key, (label, einheit) in MESSWERT_LABELS.items():
            container = QWidget()
            container.setObjectName("detailScrollInhalt")
            c_layout = QVBoxLayout(container)
            c_layout.setContentsMargins(0, 0, 0, 0)
            c_layout.setSpacing(4)

            c_layout.addWidget(self._form_label(label))
            feld = self._erstelle_validiertes_feld(
                f"mw_{key}", breite=140, standard="",
                validator=self._validiere_dezimal_optional,
                einheit=einheit if einheit else None
            )
            mess_zeile = QHBoxLayout()
            mess_zeile.setSpacing(8)
            mess_zeile.addWidget(feld["input"])

            # Bemerkung direkt neben Messwert
            bem_input = QLineEdit()
            bem_input.setObjectName("formInput")
            bem_input.setFixedHeight(36)
            bem_input.setMinimumWidth(160)
            bem_input.setPlaceholderText("Bemerkung...")
            mess_zeile.addWidget(bem_input)

            mess_zeile.addStretch()
            c_layout.addLayout(mess_zeile)
            c_layout.addWidget(feld["fehler"])

            self._messwert_widgets[key] = {
                "container": container,
                "feld": feld,
                "bemerkung": bem_input,
            }
            links.addWidget(container)

        links.addStretch()
        zwei_spalten.addLayout(links, 1)

        # --- Rechte Spalte: Funktionsprüfung + Bemerkungen ---
        rechts = QVBoxLayout()
        rechts.setSpacing(10)

        funk_titel = QLabel("Funktionsprüfung")
        funk_titel.setObjectName("formGruppenTitel")
        rechts.addWidget(funk_titel)

        self._funktion_toggle = QPushButton("  Funktion des Gerätes i.O.")
        self._funktion_toggle.setCursor(Qt.PointingHandCursor)
        self._funktion_toggle.setFixedHeight(34)
        self._funktion_toggle.setProperty("bestanden", True)
        self._funktion_toggle.clicked.connect(self._toggle_funktion)
        rechts.addWidget(self._funktion_toggle)

        rechts.addWidget(self._erstelle_trennlinie())

        bem_label = self._form_label("Bemerkungen (optional)")
        rechts.addWidget(bem_label)

        self._bemerkungen = QTextEdit()
        self._bemerkungen.setObjectName("formTextArea")
        self._bemerkungen.setMaximumHeight(120)
        self._bemerkungen.setPlaceholderText("Optionale Bemerkungen zum Protokoll...")
        rechts.addWidget(self._bemerkungen)

        rechts.addStretch()
        zwei_spalten.addLayout(rechts, 1)

        layout.addLayout(zwei_spalten)
        layout.addStretch()
        self._seiten_stack.addWidget(seite)

    def _toggle_funktion(self):
        """Schaltet den Funktionspruefungs-Toggle um."""
        aktuell = self._funktion_toggle.property("bestanden")
        self._funktion_toggle.setProperty("bestanden", not aktuell)
        self._aktualisiere_toggle_style(self._funktion_toggle)

    # --- Aktionszeile (Navigation + PDF-Button) ---

    def _erstelle_aktionszeile(self, eltern_layout):
        """Zurueck/Weiter-Buttons und PDF-Button am unteren Rand."""
        aktions_widget = QWidget()
        aktions_widget.setObjectName("detailAktionszeile")
        aktions_widget.setAttribute(Qt.WA_StyledBackground, True)
        zeile = QHBoxLayout(aktions_widget)
        zeile.setContentsMargins(32, 10, 32, 16)
        zeile.setSpacing(12)

        # Fehlermeldung (links)
        self._fehler_label = QLabel("")
        self._fehler_label.setObjectName("formFehler")
        self._fehler_label.setVisible(False)
        zeile.addWidget(self._fehler_label)

        zeile.addStretch()

        # PDF-Feedback-Icon
        self._pdf_feedback = QPushButton()
        self._pdf_feedback.setObjectName("pdfFeedbackBtn")
        self._pdf_feedback.setVisible(False)
        self._pdf_feedback.setCursor(Qt.PointingHandCursor)
        self._pdf_feedback.setToolTip("PDF öffnen")
        self._pdf_feedback.setFixedSize(40, 40)
        self._pdf_feedback.setStyleSheet(
            "QPushButton#pdfFeedbackBtn { background: transparent; border: none; }"
        )
        zeile.addWidget(self._pdf_feedback)

        # Zurueck-Button
        self._btn_zurueck = QPushButton("  Zurück")
        self._btn_zurueck.setObjectName("secondaryButton")
        self._btn_zurueck.setIcon(qta.icon("ri.arrow-left-s-line", color="#8a8fa0"))
        self._btn_zurueck.setIconSize(QSize(18, 18))
        self._btn_zurueck.setCursor(Qt.PointingHandCursor)
        self._btn_zurueck.setFixedHeight(42)
        self._btn_zurueck.setMinimumWidth(120)
        self._btn_zurueck.clicked.connect(lambda: self._zeige_seite(self._aktuelle_seite - 1))
        zeile.addWidget(self._btn_zurueck)

        # Weiter-Button
        self._btn_weiter = QPushButton("  Weiter")
        self._btn_weiter.setObjectName("primaryButton")
        self._btn_weiter.setIcon(qta.icon("ri.arrow-right-s-line", color="#ffffff"))
        self._btn_weiter.setIconSize(QSize(18, 18))
        self._btn_weiter.setCursor(Qt.PointingHandCursor)
        self._btn_weiter.setFixedHeight(42)
        self._btn_weiter.setMinimumWidth(120)
        self._btn_weiter.setLayoutDirection(Qt.RightToLeft)
        self._btn_weiter.clicked.connect(lambda: self._zeige_seite(self._aktuelle_seite + 1))
        zeile.addWidget(self._btn_weiter)

        # PDF-Button (nur auf Seite 3 sichtbar)
        self._pdf_btn = QPushButton("  PDF erstellen")
        self._pdf_btn.setObjectName("primaryButton")
        self._pdf_btn.setIcon(qta.icon("ri.printer-line", color="#ffffff"))
        self._pdf_btn.setIconSize(QSize(18, 18))
        self._pdf_btn.setCursor(Qt.PointingHandCursor)
        self._pdf_btn.setFixedHeight(42)
        self._pdf_btn.setMinimumWidth(160)
        self._pdf_btn.clicked.connect(self._erstelle_pdf)
        zeile.addWidget(self._pdf_btn)

        eltern_layout.addWidget(aktions_widget)

    def _aktualisiere_navigation(self):
        """Zeigt/versteckt Zurueck/Weiter/PDF-Buttons je nach aktiver Seite."""
        self._btn_zurueck.setVisible(self._aktuelle_seite > 0)
        self._btn_weiter.setVisible(self._aktuelle_seite < 2)
        self._pdf_btn.setVisible(self._aktuelle_seite == 2)

    # --- Validierung ---

    def _erstelle_validiertes_feld(self, name, breite=140, standard="",
                                    validator=None, einheit=None):
        """Erstellt ein QLineEdit mit Fehlerlabel, Live-Validierung und optionaler Einheit."""
        eingabe = QLineEdit(standard)
        eingabe.setObjectName("formInput")
        eingabe.setFixedWidth(breite)
        eingabe.setFixedHeight(36)

        # Einheit als Suffix-Label im Input
        if einheit:
            suffix = QLabel(einheit, eingabe)
            suffix.setObjectName("formEinheitInline")
            suffix.setStyleSheet(
                f"color: {self._aktuelle_farben.get('text_sekundaer', '#8a8fa0')}; "
                f"font-size: 12px; background: transparent; padding-right: 8px;"
            )
            suffix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Rechts im Input positionieren
            def _positioniere_suffix(event=None, e=eingabe, s=suffix):
                s.setGeometry(0, 0, e.width(), e.height())
            eingabe.resizeEvent = _positioniere_suffix
            _positioniere_suffix()
            # Padding rechts fuer den Suffix-Text
            eingabe.setStyleSheet(
                eingabe.styleSheet() + f"padding-right: {len(einheit) * 8 + 12}px;"
            )

        fehler = QLabel("")
        fehler.setObjectName("formFehler")
        fehler.setVisible(False)
        fehler.setFixedHeight(16)

        feld_info = {"input": eingabe, "fehler": fehler, "validator": validator}
        self._validierte_felder[name] = feld_info

        if validator:
            eingabe.textChanged.connect(lambda text, n=name: self._live_validierung(n))

        return feld_info

    def _live_validierung(self, feld_name):
        """Live-Validierung fuer ein Feld."""
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

        feld["input"].style().unpolish(feld["input"])
        feld["input"].style().polish(feld["input"])

    def _validiere_alle_sichtbar(self):
        """Validiert alle sichtbaren Pflichtfelder. Gibt True zurueck wenn OK."""
        alle_ok = True
        for name, feld in self._validierte_felder.items():
            if not feld["validator"]:
                continue
            # Messwert-Felder nur validieren wenn sichtbar
            if name.startswith("mw_"):
                key = name[3:]
                if key in self._messwert_widgets:
                    if not self._messwert_widgets[key]["container"].isVisible():
                        continue
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

    def _validiere_dezimal(self, text):
        """Validiert eine Dezimalzahl (Pflichtfeld)."""
        text = text.strip().replace(",", ".")
        if not text:
            return "Pflichtfeld"
        try:
            float(text)
            return None
        except ValueError:
            return "Ungültige Zahl"

    def _validiere_dezimal_optional(self, text):
        """Validiert eine Dezimalzahl (kein Pflichtfeld, aber wenn gefuellt muss es gueltig sein)."""
        text = text.strip().replace(",", ".")
        if not text:
            return None  # Leeres Feld ist OK
        try:
            float(text)
            return None
        except ValueError:
            return "Ungültige Zahl"

    def _validiere_datum(self, text):
        """Validiert ein Datum im Format TT.MM.JJJJ."""
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

    # --- Eingaben-Persistenz (Session) ---

    def _speichere_eingaben(self):
        """Speichert die aktuellen Eingaben fuer die aktive Waage im Cache."""
        wj = self._wj_nummer()
        if not wj:
            return

        # Sichtpruefung
        sichtpruefung = {}
        for key, btn in self._checkboxes.items():
            sichtpruefung[key] = btn.property("bestanden")

        # Messwerte + Bemerkungen
        messwerte = {}
        for key, widgets in self._messwert_widgets.items():
            messwerte[key] = {
                "wert": widgets["feld"]["input"].text(),
                "bemerkung": widgets["bemerkung"].text(),
            }

        self._eingaben_cache[wj] = {
            "vde_typ": self._vde_typ_aktiv,
            "pruefungsart": self._pruefungsart_dropdown.currentIndex(),
            "schutzklasse": self._sk_dropdown.currentIndex(),
            "nennspannung": self._validierte_felder["nennspannung"]["input"].text(),
            "nennstrom": self._validierte_felder["nennstrom"]["input"].text(),
            "nennleistung": self._validierte_felder["nennleistung"]["input"].text(),
            "frequenz": self._validierte_felder["frequenz"]["input"].text(),
            "cosphi": self._validierte_felder["cosphi"]["input"].text(),
            "messgeraet_index": self._messgeraet_dropdown.currentIndex(),
            "datum": self._validierte_felder["datum"]["input"].text(),
            "sichtpruefung": sichtpruefung,
            "messwerte": messwerte,
            "funktion_io": self._funktion_toggle.property("bestanden"),
            "bemerkungen": self._bemerkungen.toPlainText(),
            "aktuelle_seite": self._aktuelle_seite,
        }

    def _lade_eingaben(self, wj_nummer):
        """Laedt gespeicherte Eingaben fuer eine Waage. Gibt True zurueck bei Treffer."""
        daten = self._eingaben_cache.get(wj_nummer)
        if not daten:
            return False

        # VDE-Typ
        self._waehle_vde_typ(daten["vde_typ"])
        self._pruefungsart_dropdown.setCurrentIndex(daten["pruefungsart"])

        # Schutzklasse
        self._sk_dropdown.setCurrentIndex(daten["schutzklasse"])

        # Elektrische Daten
        self._validierte_felder["nennspannung"]["input"].setText(daten["nennspannung"])
        self._validierte_felder["nennstrom"]["input"].setText(daten["nennstrom"])
        self._validierte_felder["nennleistung"]["input"].setText(daten["nennleistung"])
        self._validierte_felder["frequenz"]["input"].setText(daten["frequenz"])
        self._validierte_felder["cosphi"]["input"].setText(daten["cosphi"])

        # Messgeraet + Datum
        if daten["messgeraet_index"] < self._messgeraet_dropdown.count():
            self._messgeraet_dropdown.setCurrentIndex(daten["messgeraet_index"])
        self._validierte_felder["datum"]["input"].setText(daten["datum"])

        # Sichtpruefung
        for key, bestanden in daten.get("sichtpruefung", {}).items():
            if key in self._checkboxes:
                self._checkboxes[key].setProperty("bestanden", bestanden)

        # Messwerte
        for key, mw_daten in daten.get("messwerte", {}).items():
            if key in self._messwert_widgets:
                self._messwert_widgets[key]["feld"]["input"].setText(mw_daten["wert"])
                self._messwert_widgets[key]["bemerkung"].setText(mw_daten["bemerkung"])

        # Funktionspruefung
        self._funktion_toggle.setProperty("bestanden", daten.get("funktion_io", True))

        # Bemerkungen
        self._bemerkungen.setPlainText(daten.get("bemerkungen", ""))

        # Wizard-Seite wiederherstellen
        self._zeige_seite(daten.get("aktuelle_seite", 0))

        return True

    def loesche_eingaben_cache(self):
        """Loescht alle gespeicherten Eingaben (z.B. bei Auftragswechsel)."""
        self._eingaben_cache.clear()

    # --- Hilfsmethoden ---

    def _form_label(self, text, tooltip=None):
        """Erstellt ein Formularlabel, optional mit Info-Icon und Tooltip."""
        if not tooltip:
            lbl = QLabel(text)
            lbl.setObjectName("formLabel")
            return lbl

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

    def _feld_mit_einheit(self, label_text, name, standard, einheit):
        """Erstellt ein Eingabefeld mit Label und Einheit im Input als VBox."""
        box = QVBoxLayout()
        box.setSpacing(4)
        box.addWidget(self._form_label(label_text))

        feld = self._erstelle_validiertes_feld(
            name, breite=120, standard=standard,
            validator=self._validiere_dezimal_optional,
            einheit=einheit if einheit else None
        )
        box.addWidget(feld["input"])
        box.addWidget(feld["fehler"])
        return box

    def _erstelle_infobox(self, text):
        """Erstellt eine Infobox mit X-Button zum Ausblenden."""
        widget = QWidget()
        widget.setObjectName("infoBox")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label, alignment=Qt.AlignTop)

        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setObjectName("infoBoxText")
        layout.addWidget(text_label, 1)

        close_btn = QPushButton()
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 4px; }"
            "QPushButton:hover { background: rgba(128,128,128,40); }"
        )
        close_btn.clicked.connect(lambda: widget.setVisible(False))
        layout.addWidget(close_btn, alignment=Qt.AlignTop)

        return {
            "widget": widget,
            "icon": icon_label,
            "text": text_label,
            "close": close_btn,
        }

    def _aktualisiere_infobox(self, infobox):
        """Aktualisiert Icons und Styling einer Infobox."""
        info_farbe = self._aktuelle_farben.get("info", "#42a5f5")
        icon_farbe = self._aktuelle_farben.get("text_sekundaer", "#8a8fa0")
        bg_farbe = self._aktuelle_farben.get("basis", "#2c3245")

        infobox["icon"].setPixmap(
            qta.icon("ri.information-line", color=info_farbe).pixmap(18, 18)
        )
        infobox["close"].setIcon(qta.icon("ri.close-line", color=icon_farbe))
        infobox["widget"].setStyleSheet(f"""
            QWidget#infoBox {{
                background-color: {bg_farbe};
                border-radius: 8px;
                border-left: 3px solid {info_farbe};
            }}
        """)
        infobox["text"].setStyleSheet(f"""
            font-size: 12px;
            color: {self._aktuelle_farben.get("text_sekundaer", "#8a8fa0")};
            background: transparent;
        """)

    def _lade_messgeraete(self):
        """Laedt VDE-Messgeraete aus den Settings."""
        self._messgeraet_dropdown.clear()
        messgeraete = self._settings.get_messgeraete()
        gefunden = False
        for i in range(1, 11):
            geraet = messgeraete.get(f"VDE-Messgeraet_{i}", "")
            if geraet:
                self._messgeraet_dropdown.addItem(geraet)
                gefunden = True

        if not gefunden:
            self._messgeraet_dropdown.addItem("— Kein Messgerät —")
            self._messgeraet_fehler.setText("Kein VDE-Messgerät in den Einstellungen gefunden")
            self._messgeraet_fehler.setVisible(True)

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

    def _finde_existierendes_pdf(self, wj_nummer):
        """Sucht im Protokoll-Ordner nach einem vorhandenen VDE-PDF."""
        if not wj_nummer:
            return None
        protokoll_pfad = self._settings.get_protokoll_path()
        if not protokoll_pfad or not os.path.isdir(protokoll_pfad):
            return None
        treffer = glob.glob(os.path.join(protokoll_pfad, f"VDE_*_{wj_nummer}.pdf"))
        if treffer:
            return max(treffer, key=os.path.getmtime)
        return None

    # --- Spinner ---

    def _starte_spinner(self):
        """Zeigt einen Spinner auf dem PDF-Button."""
        self._pdf_btn.setEnabled(False)
        self._pdf_btn.setText("")
        self._spinner_winkel = 0

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(50)
        self._spinner_timer.timeout.connect(self._spinner_tick)
        self._spinner_timer.start()

    def _spinner_tick(self):
        """Aktualisiert den Spinner."""
        self._spinner_winkel = (self._spinner_winkel + 30) % 360
        # Rotierendes Loader-Icon
        self._pdf_btn.setIcon(qta.icon("ri.loader-4-line", color="#ffffff",
                                        rotated=self._spinner_winkel))

    def _stoppe_spinner(self):
        """Stellt den PDF-Button wieder her."""
        if self._spinner_timer:
            self._spinner_timer.stop()
            self._spinner_timer = None
        self._pdf_btn.setEnabled(True)
        self._pdf_btn.setText("  PDF erstellen")
        self._pdf_btn.setIcon(qta.icon("ri.printer-line", color="#ffffff"))

    # --- Oeffentliche Methoden ---

    def setze_dialog(self, dialog):
        """Setzt die Referenz zur Dialog-Komponente."""
        self._dialog = dialog

    def setze_waage(self, waage_daten, farben, kundennummer=None):
        """Setzt Waagendaten und aktualisiert die Anzeige."""
        self._speichere_eingaben()

        self._waage_daten = waage_daten
        self._kundennummer = kundennummer
        self._aktuelle_farben = farben

        wj_nummer = str(waage_daten[0]) if waage_daten[0] else "—"
        modell = str(waage_daten[4]) if waage_daten[4] else ""
        hersteller = str(waage_daten[3]) if waage_daten[3] else ""

        # Header: Titel + Waagen-Info
        self._titel.setText("VDE-Prüfung")
        teile = [t for t in (wj_nummer, hersteller, modell) if t]
        self._waagen_info.setText(" · ".join(teile))

        # Tooltip mit erweiterten Waagen-Infos
        sn = str(waage_daten[1]) if waage_daten[1] else ""
        standort = str(waage_daten[5]) if waage_daten[5] else ""
        raum = str(waage_daten[6]) if waage_daten[6] else ""
        inventar = str(waage_daten[2]) if waage_daten[2] else ""
        tooltip_zeilen = []
        if sn:
            tooltip_zeilen.append(f"S/N: {sn}")
        if inventar:
            tooltip_zeilen.append(f"Inventar-Nr: {inventar}")
        if hersteller:
            tooltip_zeilen.append(f"Hersteller: {hersteller}")
        if standort:
            tooltip_zeilen.append(f"Standort: {standort}")
        if raum:
            tooltip_zeilen.append(f"Raum: {raum}")
        self._waagen_info.setToolTip("\n".join(tooltip_zeilen) if tooltip_zeilen else "")

        # Felder zuruecksetzen
        self._verstecke_fehler()
        self._setze_felder_zurueck()

        if not self._lade_eingaben(wj_nummer):
            # Standardwerte setzen
            self._waehle_vde_typ(0)
            self._pruefungsart_dropdown.setCurrentIndex(0)
            self._sk_dropdown.setCurrentIndex(0)
            self._validierte_felder["nennspannung"]["input"].setText(
                self._settings.get_standard_nennspannung())
            self._validierte_felder["nennstrom"]["input"].setText("")
            self._validierte_felder["nennleistung"]["input"].setText("")
            self._validierte_felder["frequenz"]["input"].setText(
                self._settings.get_standard_frequenz())
            self._validierte_felder["cosphi"]["input"].setText(
                self._settings.get_standard_cosphi())
            self._validierte_felder["datum"]["input"].setText(
                date.today().strftime("%d.%m.%Y")
            )
            # Alle Sichtpruefung auf bestanden
            for btn in self._checkboxes.values():
                btn.setProperty("bestanden", True)
            # Messwerte mit Standardwerten aus Settings
            std_werte = {
                "rpe": self._settings.get_standard_rpe(),
                "riso": self._settings.get_standard_riso(),
                "ipe": self._settings.get_standard_ipe(),
                "ib": self._settings.get_standard_ib(),
            }
            for key, widgets in self._messwert_widgets.items():
                widgets["feld"]["input"].setText(std_werte.get(key, ""))
                widgets["bemerkung"].setText("")
            # Funktionspruefung bestanden
            self._funktion_toggle.setProperty("bestanden", True)
            self._bemerkungen.clear()
            self._zeige_seite(0)

        # Schutzklasse-abhaengige Felder aktualisieren
        self._schutzklasse_geaendert(self._sk_dropdown.currentIndex())

        # PDF-Status pruefen
        pdf_pfad = self._finde_existierendes_pdf(wj_nummer)
        if pdf_pfad:
            self._zeige_pdf_feedback(pdf_pfad)
        else:
            self._pdf_feedback.setVisible(False)

        # Messgeraete neu laden und UI aktualisieren
        self._lade_messgeraete()
        self._aktualisiere_alle_infoboxen()
        self._aktualisiere_toggle_style(self._funktion_toggle)
        self._aktualisiere_stepper()
        self._aktualisiere_vde_typ_styles()
        self._aktualisiere_alle_sichtpruefung_icons()

    def _setze_felder_zurueck(self):
        """Setzt alle Validierungszustaende zurueck."""
        for feld in self._validierte_felder.values():
            feld["input"].setObjectName("formInput")
            feld["fehler"].setVisible(False)
            feld["input"].style().unpolish(feld["input"])
            feld["input"].style().polish(feld["input"])

    def _aktualisiere_alle_infoboxen(self):
        """Aktualisiert alle Infobox-Icons, Styles und Sichtbarkeit."""
        infobox_keys = [
            (self._infobox1, "vde_grundeinstellungen"),
            (self._infobox2, "vde_sichtpruefung"),
            (self._infobox3, "vde_messwerte"),
        ]
        for ib, key in infobox_keys:
            self._aktualisiere_infobox(ib)
            ib["widget"].setVisible(self._settings.get_infobox_anzeigen(key))

    def aktualisiere_theme(self, farben):
        """Aktualisiert Farben bei Theme-Wechsel."""
        self._aktuelle_farben = farben
        self._aktualisiere_alle_infoboxen()
        self._aktualisiere_toggle_style(self._funktion_toggle)
        self._aktualisiere_stepper()
        self._aktualisiere_vde_typ_styles()
        self._aktualisiere_alle_sichtpruefung_icons()

        # Zurueck-Button Icon aktualisieren
        icon_farbe = farben.get("text_sekundaer", "#8a8fa0")
        self._btn_zurueck.setIcon(qta.icon("ri.arrow-left-s-line", color=icon_farbe))

        # Feedback-Icon aktualisieren falls sichtbar
        if self._pdf_feedback.isVisible():
            pdf_pfad = self._finde_existierendes_pdf(self._wj_nummer())
            if pdf_pfad:
                self._zeige_pdf_feedback(pdf_pfad)

    # --- PDF-Generierung ---

    def _erstelle_pdf(self):
        """Generiert das VDE-PDF mit den eingegebenen Daten."""
        self._verstecke_fehler()

        # Validierung
        if not self._validiere_alle_sichtbar():
            self._zeige_fehler("Bitte ungültige Felder korrigieren")
            return

        # Messwerte sammeln
        sk = self._sk_dropdown.currentIndex() + 1
        relevante = MESSWERTE_PRO_SK.get(sk, [])

        messwerte = {}
        bemerkungen_mw = {}
        for key in ["rpe", "riso", "ipe", "ib"]:
            if key in relevante:
                text = self._messwert_widgets[key]["feld"]["input"].text().strip().replace(",", ".")
                messwerte[key] = text if text else "-"
                bemerkungen_mw[key] = self._messwert_widgets[key]["bemerkung"].text().strip()
            else:
                messwerte[key] = "-"
                bemerkungen_mw[key] = ""

        # Pruefungsart
        vde_pruefung = {
            "vde_701": self._vde_typ_aktiv == 0,
            "pruefungsart": self._pruefungsart_dropdown.currentIndex(),
            "vde_702": self._vde_typ_aktiv == 1,
        }

        # Sichtpruefung
        visuelle_daten = {}
        for key, btn in self._checkboxes.items():
            visuelle_daten[key] = 1 if btn.property("bestanden") else 0

        # Elektrische Pruefung
        elektrische_daten = {
            "funktion_check_var": 1 if self._funktion_toggle.property("bestanden") else 0,
        }

        pruefdatum = self._validierte_felder["datum"]["input"].text().strip()
        bemerkungen = self._bemerkungen.toPlainText().strip()
        messgeraet = self._messgeraet_dropdown.currentText()

        # Pruefen ob PDF bereits existiert
        wj_nummer = self._wj_nummer()
        existierendes_pdf = self._finde_existierendes_pdf(wj_nummer)

        if existierendes_pdf and self._dialog:
            self._dialog.zeige(
                typ="bestaetigung",
                titel="Protokoll überschreiben?",
                nachricht="Für diese Waage existiert bereits ein "
                          "VDE-Protokoll. Soll es überschrieben werden?",
                bei_bestaetigung=lambda: self._fuehre_pdf_generierung_aus(
                    sk, messwerte, bemerkungen_mw, vde_pruefung,
                    visuelle_daten, elektrische_daten,
                    pruefdatum, bemerkungen, messgeraet
                ),
                ok_text="Überschreiben",
                abbrechen_text="Abbrechen",
            )
        else:
            self._fuehre_pdf_generierung_aus(
                sk, messwerte, bemerkungen_mw, vde_pruefung,
                visuelle_daten, elektrische_daten,
                pruefdatum, bemerkungen, messgeraet
            )

    def _fuehre_pdf_generierung_aus(self, sk, messwerte, bemerkungen_mw,
                                     vde_pruefung, visuelle_daten,
                                     elektrische_daten, pruefdatum,
                                     bemerkungen, messgeraet):
        """Fuehrt die eigentliche PDF-Generierung durch."""
        try:
            generator = PDFGeneratorVDE()
            generator.add_company_and_inspector_data()

            # Waagendaten bereinigen: None -> ''
            waage_sauber = tuple(
                str(v) if v is not None else '' for v in self._waage_daten
            )
            generator.add_waagen_data(waage_sauber)

            # Kundennummer
            if self._kundennummer:
                generator.add_kundennummer(self._kundennummer)

            # Elektrische Daten
            nennspannung = self._validierte_felder["nennspannung"]["input"].text().strip().replace(",", ".")
            nennstrom = self._validierte_felder["nennstrom"]["input"].text().strip().replace(",", ".")
            nennleistung = self._validierte_felder["nennleistung"]["input"].text().strip().replace(",", ".")
            frequenz = self._validierte_felder["frequenz"]["input"].text().strip().replace(",", ".")
            cosphi = self._validierte_felder["cosphi"]["input"].text().strip().replace(",", ".")

            generator.add_vde_pruefung(
                schutzklasse=str(sk),
                rpe=messwerte["rpe"],
                riso=messwerte["riso"],
                ipe=messwerte["ipe"],
                ib=messwerte["ib"],
                vde_messgeraet=messgeraet,
                nennspannung=nennspannung,
                nennstrom=nennstrom,
                nennleistung=nennleistung,
                frequenz=frequenz,
                cosphi=cosphi,
                visuelle_pruefung_daten=visuelle_daten,
                rpe_bemerkungen=bemerkungen_mw.get("rpe", ""),
                riso_bemerkungen=bemerkungen_mw.get("riso", ""),
                ipe_bemerkungen=bemerkungen_mw.get("ipe", ""),
                ib_bemerkungen=bemerkungen_mw.get("ib", ""),
                elektrische_pruefung_daten=elektrische_daten,
                vde_pruefung=vde_pruefung,
            )
            generator.add_pruefdatum_bemerkungen(pruefdatum, bemerkungen)

            # Dateiname und Pfad
            self._kalibrier_nr = generator.get_calibration_number()
            protokoll_pfad = self._settings.get_protokoll_path()
            os.makedirs(protokoll_pfad, exist_ok=True)
            datei_pfad = os.path.join(protokoll_pfad, f"{self._kalibrier_nr}.pdf")

            # Spinner starten, PDF im Hintergrund generieren
            self._starte_spinner()

            self._worker = PdfWorkerVDE(generator, datei_pfad)
            self._worker.fertig.connect(self._pdf_fertig)
            self._worker.start()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._zeige_fehler(f"Fehler: {e}")

    def _pdf_fertig(self, erfolg, ergebnis):
        """Callback wenn der PDF-Worker fertig ist."""
        self._stoppe_spinner()

        if erfolg:
            self._zeige_pdf_feedback(ergebnis)
            self.pdf_erstellt.emit(self._kalibrier_nr)
        else:
            self._zeige_fehler(f"Fehler: {ergebnis}")

    def _zeige_pdf_feedback(self, pfad):
        """Zeigt gruenes Feedback-Icon (klickbar zum Oeffnen)."""
        erfolg_farbe = self._aktuelle_farben.get("erfolg", "#4caf50")
        self._pdf_feedback.setIcon(
            qta.icon("ri.file-check-line", color=erfolg_farbe)
        )
        self._pdf_feedback.setIconSize(QSize(24, 24))
        self._pdf_feedback.setVisible(True)

        try:
            self._pdf_feedback.clicked.disconnect()
        except RuntimeError:
            pass
        self._pdf_feedback.clicked.connect(lambda: os.startfile(pfad))

    def keyPressEvent(self, event):
        """Pfeiltasten-Navigation zwischen Wizard-Seiten."""
        if event.key() == Qt.Key_Right and self._aktuelle_seite < 2:
            self._zeige_seite(self._aktuelle_seite + 1)
            event.accept()
        elif event.key() == Qt.Key_Left and self._aktuelle_seite > 0:
            self._zeige_seite(self._aktuelle_seite - 1)
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Akzeptiert Mouse-Events um Propagation zum Overlay zu verhindern."""
        event.accept()
