"""Temperaturjustage Detail-Seite mit Formular, Live-Validierung und PDF-Generierung."""

import os
from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from settings import Settings
from pdf_temp_generator import PDFGeneratorTemp
from ui.detail_basis import DetailBasis, PdfWorker


class DetailTempSeite(DetailBasis):
    """Detail-Seite fuer Temperaturjustage mit Formular und PDF-Generierung."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("detailSeite")
        self._worker = None
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut die Detail-Seite auf."""
        haupt_layout = QVBoxLayout(self)
        haupt_layout.setContentsMargins(0, 0, 0, 0)
        haupt_layout.setSpacing(0)

        # Fixierter Bereich oben (Header + Infobox)
        fix_oben = QWidget()
        fix_oben.setObjectName("detailScrollInhalt")
        fix_layout = QVBoxLayout(fix_oben)
        fix_layout.setContentsMargins(32, 20, 32, 0)
        fix_layout.setSpacing(12)
        self._content = fix_layout

        self._erstelle_header()
        self._erstelle_infobox()

        haupt_layout.addWidget(fix_oben)

        # Scrollbereich (nur Formular)
        scroll = QScrollArea()
        scroll.setObjectName("detailScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_inhalt = QWidget()
        scroll_inhalt.setObjectName("detailScrollInhalt")
        self._content = QVBoxLayout(scroll_inhalt)
        self._content.setContentsMargins(32, 8, 32, 16)
        self._content.setSpacing(12)

        self._erstelle_formular()
        self._content.addStretch()

        scroll.setWidget(scroll_inhalt)
        haupt_layout.addWidget(scroll)

        # Aktionszeile (fixiert unten)
        self._erstelle_aktionszeile(haupt_layout)

    # --- Header ---

    def _erstelle_header(self):
        """Header: Gross 'Temperaturkalibrierung', darunter kleiner Waagen-Info."""
        self._titel = QLabel("Temperaturkalibrierung")
        self._titel.setObjectName("detailSeitenTitel")
        self._content.addWidget(self._titel)

        self._waagen_info = QLabel("—")
        self._waagen_info.setObjectName("detailWaagenInfo")
        self._content.addWidget(self._waagen_info)

    # --- Infobox ---

    def _erstelle_infobox(self):
        """Erstellt eine Infobox mit X-Button zum dauerhaften Ausblenden (pro Session)."""
        self._infobox_ausgeblendet = False

        self._infobox = QWidget()
        self._infobox.setObjectName("infoBox")
        infobox_layout = QHBoxLayout(self._infobox)
        infobox_layout.setContentsMargins(12, 12, 12, 12)
        infobox_layout.setSpacing(10)

        # Info-Icon links
        self._infobox_icon = QLabel()
        self._infobox_icon.setFixedSize(20, 20)
        self._infobox_icon.setAlignment(Qt.AlignCenter)
        infobox_layout.addWidget(self._infobox_icon, alignment=Qt.AlignTop)

        # Text
        self._infobox_text = QLabel(
            "Geben Sie die Ist-Temperaturen vom Display des Feuchtebestimmers ein. "
            "Die Soll-Werte sind vorausgefüllt. Komma und Punkt werden als "
            "Dezimaltrenner akzeptiert."
        )
        self._infobox_text.setWordWrap(True)
        self._infobox_text.setObjectName("infoBoxText")
        infobox_layout.addWidget(self._infobox_text, 1)

        # X-Button zum Ausblenden
        self._infobox_close = QPushButton()
        self._infobox_close.setObjectName("infoBoxClose")
        self._infobox_close.setFixedSize(22, 22)
        self._infobox_close.setCursor(Qt.PointingHandCursor)
        self._infobox_close.clicked.connect(self._schliesse_infobox)
        infobox_layout.addWidget(self._infobox_close, alignment=Qt.AlignTop)

        self._content.addWidget(self._infobox)

    def _schliesse_infobox(self):
        """Blendet die Infobox fuer die Session aus."""
        self._infobox_ausgeblendet = True
        self._infobox.setVisible(False)

    def _aktualisiere_infobox_icons(self):
        """Aktualisiert Icons, Styling und Sichtbarkeit der Infobox."""
        # Sichtbarkeit aus Settings
        anzeigen = self._settings.get_infobox_anzeigen("temp_info")
        if not self._infobox_ausgeblendet:
            self._infobox.setVisible(anzeigen)

        info_farbe = self._aktuelle_farben.get("info", "#42a5f5")
        icon_farbe = self._aktuelle_farben.get("text_sekundaer", "#8a8fa0")

        icon = qta.icon("ri.information-line", color=info_farbe)
        self._infobox_icon.setPixmap(icon.pixmap(18, 18))

        self._infobox_close.setIcon(qta.icon("ri.close-line", color=icon_farbe))

        # Styles werden global ueber styles.py angewendet (ObjectNames infoBox/infoBoxText)

    # --- Formular ---

    def _erstelle_formular(self):
        """Erstellt das gesamte Formular mit sauberer Ausrichtung."""

        # --- Zeile 1: Messgeraet + Pruefdatum + Umgebungstemperatur ---
        zeile1 = QHBoxLayout()
        zeile1.setSpacing(16)

        mg_box = QVBoxLayout()
        mg_box.setSpacing(4)
        mg_box.addWidget(self._form_label(
            "Messgerät",
            tooltip="Temperaturmessgerät aus den Einstellungen"
        ))

        self._messgeraet_dropdown = QComboBox()
        self._messgeraet_dropdown.setObjectName("formDropdown")
        self._messgeraet_dropdown.setMinimumWidth(300)
        self._messgeraet_dropdown.setFixedHeight(36)
        mg_box.addWidget(self._messgeraet_dropdown)

        self._messgeraet_fehler = QLabel("")
        self._messgeraet_fehler.setObjectName("formFehler")
        self._messgeraet_fehler.setVisible(False)
        mg_box.addWidget(self._messgeraet_fehler)

        self._lade_messgeraete()

        zeile1.addLayout(mg_box)

        datum_box = QVBoxLayout()
        datum_box.setSpacing(4)
        datum_box.addWidget(self._form_label("Prüfdatum"))

        self._datum_input = self._erstelle_validiertes_feld(
            "datum", standard=date.today().strftime("%d.%m.%Y"),
            validator=self._validiere_datum
        )
        self._datum_input["input"].setMaximumWidth(130)
        datum_box.addWidget(self._datum_input["input"])
        datum_box.addWidget(self._datum_input["fehler"])

        zeile1.addLayout(datum_box)

        zeile1.addStretch()

        # Umgebungstemperatur (float rechts)
        umgebung_box = QVBoxLayout()
        umgebung_box.setSpacing(4)
        umgebung_box.addWidget(self._form_label(
            "Umgebungstemperatur",
            tooltip="Raumtemperatur am Prüfort zum Zeitpunkt der Kalibrierung"
        ))

        umgebung_feld = self._erstelle_validiertes_feld(
            "umgebung", standard="22,0",
            validator=self._validiere_dezimal, einheit="°C"
        )
        self._umgebung = umgebung_feld["input"]
        umgebung_box.addWidget(self._umgebung)
        umgebung_box.addWidget(umgebung_feld["fehler"])
        zeile1.addLayout(umgebung_box)

        self._content.addLayout(zeile1)

        # Trennlinie
        trenn1 = QFrame()
        trenn1.setObjectName("gruppenTrennlinie")
        trenn1.setFrameShape(QFrame.HLine)
        self._content.addWidget(trenn1)

        # --- Zweispaltiges Layout: Pruefpunkte links, Bemerkungen rechts ---
        zwei_spalten = QHBoxLayout()
        zwei_spalten.setSpacing(24)

        # Linke Spalte: Pruefpunkte
        links = QVBoxLayout()
        links.setSpacing(8)

        self._pp_container = QWidget()
        self._pp_container.setObjectName("detailScrollInhalt")
        self._pp_layout = QHBoxLayout(self._pp_container)
        self._pp_layout.setContentsMargins(0, 0, 0, 0)
        self._pp_layout.setSpacing(24)

        self._pp1_widget = QWidget()
        self._pp1_widget.setObjectName("detailScrollInhalt")
        pp1_box = self._erstelle_pruefpunkt("Prüfpunkt 1  —  100 °C", "100,0", "pp1")
        self._pp1_widget.setLayout(pp1_box["layout"])
        self._soll1 = pp1_box["soll"]
        self._ist1 = pp1_box["ist"]
        self._pp_layout.addWidget(self._pp1_widget)

        self._pp2_widget = QWidget()
        self._pp2_widget.setObjectName("detailScrollInhalt")
        pp2_box = self._erstelle_pruefpunkt("Prüfpunkt 2  —  160 °C", "160,0", "pp2")
        self._pp2_widget.setLayout(pp2_box["layout"])
        self._soll2 = pp2_box["soll"]
        self._ist2 = pp2_box["ist"]
        self._pp_layout.addWidget(self._pp2_widget)

        self._pp_layout.addStretch()
        self._pp_ist_zweispaltig = True
        links.addWidget(self._pp_container)

        links.addStretch()
        zwei_spalten.addLayout(links, 2)

        # Rechte Spalte: Bemerkungen
        rechts = QVBoxLayout()
        rechts.setSpacing(8)

        rechts.addWidget(self._form_label("Bemerkungen (optional)"))

        self._bemerkungen = QTextEdit()
        self._bemerkungen.setObjectName("formTextArea")
        self._bemerkungen.setMaximumHeight(140)
        self._bemerkungen.setLineWrapMode(QTextEdit.WidgetWidth)
        self._bemerkungen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._bemerkungen.setPlaceholderText("Optionale Bemerkungen zum Protokoll...")
        rechts.addWidget(self._bemerkungen)

        rechts.addStretch()
        zwei_spalten.addLayout(rechts, 1)

        self._content.addLayout(zwei_spalten)

    def _erstelle_validiertes_feld(self, name, standard="",
                                    validator=None, einheit=None):
        """Erstellt ein QLineEdit mit Fehlerlabel, Live-Validierung und optionaler Einheit."""
        eingabe = QLineEdit(standard)
        eingabe.setObjectName("formInput")
        eingabe.setFixedHeight(36)

        # Einheit als Suffix-Label im Input (Styles via formEinheitInline + hat_einheit Property)
        if einheit:
            suffix = QLabel(einheit, eingabe)
            suffix.setObjectName("formEinheitInline")
            suffix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            def _positioniere_suffix(event=None, e=eingabe, s=suffix):
                s.setGeometry(0, 0, e.width(), e.height())
            eingabe.resizeEvent = _positioniere_suffix
            _positioniere_suffix()
            eingabe.setProperty("hat_einheit", "true")

        fehler = QLabel("")
        fehler.setObjectName("formFehler")
        fehler.setVisible(False)
        fehler.setFixedHeight(16)

        feld_info = {"input": eingabe, "fehler": fehler, "validator": validator}
        self._validierte_felder[name] = feld_info

        if validator:
            eingabe.textChanged.connect(lambda text, n=name: self._live_validierung(n))

        return feld_info

    def _erstelle_pruefpunkt(self, titel, soll_default, prefix):
        """Erstellt eine Pruefpunkt-Gruppe mit Soll- und Ist-Feld untereinander."""
        box = QVBoxLayout()
        box.setSpacing(8)

        titel_label = QLabel(titel)
        titel_label.setObjectName("formGruppenTitel")
        box.addWidget(titel_label)

        # Soll-Feld
        soll_box = QVBoxLayout()
        soll_box.setSpacing(4)
        soll_box.addWidget(self._form_label("Soll-Temperatur"))
        soll_feld = self._erstelle_validiertes_feld(
            f"{prefix}_soll", standard=soll_default,
            validator=self._validiere_dezimal, einheit="°C"
        )
        soll_box.addWidget(soll_feld["input"])
        soll_box.addWidget(soll_feld["fehler"])
        box.addLayout(soll_box)

        # Ist-Feld
        ist_box = QVBoxLayout()
        ist_box.setSpacing(4)
        ist_box.addWidget(self._form_label("Ist-Temperatur"))
        ist_feld = self._erstelle_validiertes_feld(
            f"{prefix}_ist", standard=soll_default,
            validator=self._validiere_dezimal, einheit="°C"
        )
        ist_box.addWidget(ist_feld["input"])
        ist_box.addWidget(ist_feld["fehler"])
        box.addLayout(ist_box)

        return {"layout": box, "soll": soll_feld["input"], "ist": ist_feld["input"]}

    # --- Eingaben-Persistenz (Session) ---

    def _speichere_eingaben(self):
        """Speichert die aktuellen Eingaben fuer die aktive Waage im Cache."""
        wj = self._wj_nummer()
        if not wj:
            return
        self._eingaben_cache[wj] = {
            "soll1": self._soll1.text(),
            "ist1": self._ist1.text(),
            "soll2": self._soll2.text(),
            "ist2": self._ist2.text(),
            "umgebung": self._umgebung.text(),
            "datum": self._validierte_felder["datum"]["input"].text(),
            "bemerkungen": self._bemerkungen.toPlainText(),
            "messgeraet_index": self._messgeraet_dropdown.currentIndex(),
        }

    def _lade_eingaben(self, wj_nummer):
        """Laedt gespeicherte Eingaben fuer eine Waage aus dem Cache.
        Gibt True zurueck wenn Daten gefunden wurden."""
        daten = self._eingaben_cache.get(wj_nummer)
        if not daten:
            return False

        self._validierte_felder["pp1_soll"]["input"].setText(daten["soll1"])
        self._validierte_felder["pp1_ist"]["input"].setText(daten["ist1"])
        self._validierte_felder["pp2_soll"]["input"].setText(daten["soll2"])
        self._validierte_felder["pp2_ist"]["input"].setText(daten["ist2"])
        self._validierte_felder["umgebung"]["input"].setText(daten["umgebung"])
        self._validierte_felder["datum"]["input"].setText(daten["datum"])
        self._bemerkungen.setPlainText(daten["bemerkungen"])
        if daten["messgeraet_index"] < self._messgeraet_dropdown.count():
            self._messgeraet_dropdown.setCurrentIndex(daten["messgeraet_index"])
        return True

    # --- Aktionszeile ---

    def _erstelle_aktionszeile(self, eltern_layout):
        """PDF-Button und Feedback-Icon am unteren Rand."""
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

        # PDF-Feedback-Icon (initial versteckt)
        self._pdf_feedback = QPushButton()
        self._pdf_feedback.setObjectName("pdfFeedbackBtn")
        self._pdf_feedback.setVisible(False)
        self._pdf_feedback.setCursor(Qt.PointingHandCursor)
        self._pdf_feedback.setToolTip("PDF öffnen")
        self._pdf_feedback.setFixedSize(40, 40)
        # Style via pdfFeedbackBtn ObjectName in styles.py
        zeile.addWidget(self._pdf_feedback)

        # PDF-erstellen-Button
        self._pdf_btn = QPushButton("  PDF erstellen")
        self._pdf_btn.setObjectName("primaryButton")
        self._pdf_btn.setIcon(qta.icon("ri.printer-line", color="#ffffff"))
        self._pdf_btn.setIconSize(QSize(22, 22))
        self._pdf_btn.setCursor(Qt.PointingHandCursor)
        self._pdf_btn.setFixedHeight(42)
        self._pdf_btn.setMinimumWidth(160)
        self._pdf_btn.clicked.connect(self._erstelle_pdf)
        zeile.addWidget(self._pdf_btn)

        eltern_layout.addWidget(aktions_widget)

    def _lade_messgeraete(self):
        """Laedt Temperatur-Messgeraete aus den Settings."""
        self._messgeraet_dropdown.clear()
        messgeraete = self._settings.get_messgeraete()
        gefunden = False
        for i in range(1, 11):
            geraet = messgeraete.get(f"Temperaturmessgeraet_{i}", "")
            if geraet:
                self._messgeraet_dropdown.addItem(geraet)
                gefunden = True

        if not gefunden:
            self._messgeraet_dropdown.addItem("— Kein Messgerät —")
            self._messgeraet_fehler.setText("Kein Messgerät in den Einstellungen gefunden")
            self._messgeraet_fehler.setVisible(True)

    # --- Oeffentliche Methoden ---

    def setze_waage(self, waage_daten, farben):
        """Setzt Waagendaten und aktualisiert die Anzeige."""
        # Vorherige Eingaben speichern bevor neue Waage geladen wird
        self._speichere_eingaben()

        self._waage_daten = waage_daten
        self._aktuelle_farben = farben

        wj_nummer = str(waage_daten[0]) if waage_daten[0] else "—"
        modell = str(waage_daten[4]) if waage_daten[4] else ""
        hersteller = str(waage_daten[3]) if waage_daten[3] else ""

        # Header: Titel + Waagen-Info
        self._titel.setText("Temperaturkalibrierung")
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

        # Felder: gespeicherte Eingaben laden oder Standardwerte setzen
        self._verstecke_fehler()
        self._setze_felder_zurueck()

        if not self._lade_eingaben(wj_nummer):
            # Keine gespeicherten Eingaben -> Standardwerte aus Settings
            soll1 = self._settings.get_standard_soll_temp1()
            soll2 = self._settings.get_standard_soll_temp2()
            umgebung = self._settings.get_standard_umgebung_temp()
            self._validierte_felder["pp1_soll"]["input"].setText(soll1)
            self._validierte_felder["pp2_soll"]["input"].setText(soll2)
            self._validierte_felder["pp1_ist"]["input"].setText(soll1)
            self._validierte_felder["pp2_ist"]["input"].setText(soll2)
            self._validierte_felder["umgebung"]["input"].setText(umgebung)
            self._bemerkungen.clear()
            self._validierte_felder["datum"]["input"].setText(
                date.today().strftime("%d.%m.%Y")
            )

        # PDF-Status aus Dateisystem pruefen
        pdf_pfad = self._finde_existierendes_pdf(wj_nummer)
        if pdf_pfad:
            self._zeige_pdf_feedback(pdf_pfad)
        else:
            self._pdf_feedback.setVisible(False)

        # Messgeraete neu laden und Infobox aktualisieren
        self._lade_messgeraete()
        self._aktualisiere_infobox_icons()

    def aktualisiere_theme(self, farben):
        """Aktualisiert Farben bei Theme-Wechsel."""
        self._aktuelle_farben = farben
        self._aktualisiere_infobox_icons()
        # Feedback-Icon Farbe aktualisieren falls sichtbar
        if self._pdf_feedback.isVisible():
            pdf_pfad = self._finde_existierendes_pdf(self._wj_nummer())
            if pdf_pfad:
                self._zeige_pdf_feedback(pdf_pfad)

    def resizeEvent(self, event):
        """Wechselt Pruefpunkt-Layout zwischen zwei- und einspaltig."""
        super().resizeEvent(event)
        SCHWELLE = 600  # Unter dieser Breite einspaltig
        breit_genug = self.width() >= SCHWELLE

        if breit_genug and not self._pp_ist_zweispaltig:
            # Zu zweispaltig wechseln (HBox)
            self._wechsle_pp_layout(QHBoxLayout)
            self._pp_ist_zweispaltig = True
        elif not breit_genug and self._pp_ist_zweispaltig:
            # Zu einspaltig wechseln (VBox)
            self._wechsle_pp_layout(QVBoxLayout)
            self._pp_ist_zweispaltig = False

    def _wechsle_pp_layout(self, layout_klasse):
        """Wechselt das Layout des Pruefpunkt-Containers."""
        # Widgets aus altem Layout entfernen
        self._pp_layout.removeWidget(self._pp1_widget)
        self._pp_layout.removeWidget(self._pp2_widget)

        # Altes Layout loeschen
        QWidget().setLayout(self._pp_container.layout())

        # Neues Layout erstellen
        self._pp_layout = layout_klasse(self._pp_container)
        self._pp_layout.setContentsMargins(0, 0, 0, 0)
        self._pp_layout.setSpacing(40 if layout_klasse == QHBoxLayout else 28)
        self._pp_layout.addWidget(self._pp1_widget)
        self._pp_layout.addWidget(self._pp2_widget)
        self._pp_layout.addStretch()

    def mousePressEvent(self, event):
        """Akzeptiert Mouse-Events um Propagation zum Overlay zu verhindern."""
        event.accept()

    # --- PDF-Generierung ---

    def _erstelle_pdf(self):
        """Generiert das Temperatur-PDF mit den eingegebenen Daten."""
        self._verstecke_fehler()

        # Live-Validierung aller Felder
        if not self._validiere_alle():
            self._zeige_fehler("Bitte ungültige Felder korrigieren")
            return

        # Werte auslesen
        try:
            soll1 = self._parse_dezimal(self._soll1.text())
            ist1 = self._parse_dezimal(self._ist1.text())
            soll2 = self._parse_dezimal(self._soll2.text())
            ist2 = self._parse_dezimal(self._ist2.text())
        except ValueError:
            self._zeige_fehler("Ungültige Temperaturwerte")
            return

        umgebung_text = self._umgebung.text().strip().replace(",", ".")
        pruefdatum = self._validierte_felder["datum"]["input"].text().strip()
        bemerkungen = self._bemerkungen.toPlainText().strip()
        messgeraet = self._messgeraet_dropdown.currentText()

        # Pruefen ob PDF bereits existiert -> Ueberschreib-Dialog
        wj_nummer = self._wj_nummer()
        existierendes_pdf = self._finde_existierendes_pdf(wj_nummer)

        if existierendes_pdf and self._dialog:
            self._dialog.zeige(
                typ="bestaetigung",
                titel="Protokoll überschreiben?",
                nachricht=f"Für diese Waage existiert bereits ein "
                          f"Temperaturprotokoll. Soll es überschrieben werden?",
                bei_bestaetigung=lambda: self._fuehre_pdf_generierung_aus(
                    soll1, ist1, soll2, ist2, umgebung_text,
                    pruefdatum, bemerkungen, messgeraet
                ),
                ok_text="Überschreiben",
                abbrechen_text="Abbrechen",
            )
        else:
            self._fuehre_pdf_generierung_aus(
                soll1, ist1, soll2, ist2, umgebung_text,
                pruefdatum, bemerkungen, messgeraet
            )

    def _fuehre_pdf_generierung_aus(self, soll1, ist1, soll2, ist2,
                                     umgebung_text, pruefdatum,
                                     bemerkungen, messgeraet):
        """Fuehrt die eigentliche PDF-Generierung durch."""
        try:
            generator = PDFGeneratorTemp()
            generator.add_company_and_inspector_data()

            # Waagendaten bereinigen: None -> '' (DB-Subqueries koennen NULL liefern)
            waage_sauber = tuple(
                str(v) if v is not None else '' for v in self._waage_daten
            )
            generator.add_waagen_data(waage_sauber)
            generator.add_tempjustage_data({
                'ist_temp1': str(ist1),
                'soll_temp1': str(soll1),
                'ist_temp2': str(ist2),
                'soll_temp2': str(soll2),
                'temp_messgeraet': messgeraet,
                'umgebung_temp': umgebung_text,
            })
            generator.add_pruefdatum_bemerkungen(pruefdatum, bemerkungen)

            # Dateiname und Pfad
            self._kalibrier_nr = generator.get_calibration_number()
            protokoll_pfad = self._settings.get_protokoll_path()
            os.makedirs(protokoll_pfad, exist_ok=True)
            datei_pfad = os.path.join(protokoll_pfad, f"{self._kalibrier_nr}.pdf")

            # Spinner starten, PDF im Hintergrund generieren
            self._starte_spinner()

            self._worker = PdfWorker(generator, datei_pfad)
            self._worker.fertig.connect(self._pdf_fertig)
            self._worker.start()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._zeige_fehler(f"Fehler: {e}")

