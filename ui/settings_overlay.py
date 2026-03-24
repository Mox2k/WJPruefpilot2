"""Settings-Overlay mit vertikaler Reiter-Navigation (wie Wispr Flow)."""

import os
import shutil

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QScrollArea, QFileDialog,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QRectF
from PySide6.QtGui import QPainter, QColor, QPixmap
import qtawesome as qta

from settings import Settings


class SettingsTabButton(QPushButton):
    """Ein Tab-Button fuer die Settings-Navigation mit Icon, Label und Active-Indicator."""

    def __init__(self, icon_name, text, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsTabButton")
        self._icon_name = icon_name
        self._text = text
        self._icon_farbe = "#8a8fa0"
        self._icon_farbe_aktiv = "#ffffff"
        self._indicator_farbe = "#ed1b24"
        self._ist_aktiv = False

        self.setIcon(qta.icon(icon_name, color=self._icon_farbe))
        self.setIconSize(QSize(18, 18))
        self.setText(f"  {text}")
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._ist_aktiv:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self._indicator_farbe))
            balken_hoehe = 18
            y = (self.height() - balken_hoehe) / 2
            painter.drawRoundedRect(QRectF(0, y, 3, balken_hoehe), 1.5, 1.5)
            painter.end()

    def setze_aktiv(self, aktiv):
        self._ist_aktiv = aktiv
        farbe = self._icon_farbe_aktiv if aktiv else self._icon_farbe
        self.setIcon(qta.icon(self._icon_name, color=farbe))
        self.setProperty("aktiv", aktiv)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def aktualisiere_farben(self, icon_farbe, icon_farbe_aktiv, indicator_farbe):
        self._icon_farbe = icon_farbe
        self._icon_farbe_aktiv = icon_farbe_aktiv
        self._indicator_farbe = indicator_farbe
        farbe = self._icon_farbe_aktiv if self._ist_aktiv else self._icon_farbe
        self.setIcon(qta.icon(self._icon_name, color=farbe))
        self.update()


class SettingsOverlay(QWidget):
    """Settings-Overlay mit vertikaler Tab-Navigation und Auto-Save."""

    settings_geaendert = Signal()    # Allgemeines Signal bei Aenderungen

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("settingsOverlay")
        self._settings = Settings("settings.ini")
        self._aktuelle_farben = {}
        self._ist_dark = True
        self._tab_buttons = []
        self._erstelle_ui()

    def _erstelle_ui(self):
        haupt = QHBoxLayout(self)
        haupt.setContentsMargins(0, 0, 0, 0)
        haupt.setSpacing(0)

        # --- Linke Tab-Leiste ---
        self._tab_panel = QWidget()
        self._tab_panel.setObjectName("settingsTabPanel")
        self._tab_panel.setFixedWidth(180)
        tab_layout = QVBoxLayout(self._tab_panel)
        tab_layout.setContentsMargins(8, 16, 8, 16)
        tab_layout.setSpacing(4)

        # Titel
        titel = QLabel("Einstellungen")
        titel.setObjectName("settingsSectionTitel")
        titel.setContentsMargins(10, 0, 0, 12)
        tab_layout.addWidget(titel)

        tabs = [
            ("ri.settings-line", "Allgemein"),
            ("ri.database-2-line", "SimplyCal"),
            ("ri.building-2-line", "Firma"),
            ("ri.user-settings-line", "Prüfer"),
            ("ri.thermometer-line", "Messgeräte"),
            ("ri.function-line", "System"),
        ]

        for i, (icon, text) in enumerate(tabs):
            btn = SettingsTabButton(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self._tab_geklickt(idx))
            tab_layout.addWidget(btn)
            self._tab_buttons.append(btn)

        tab_layout.addStretch()
        haupt.addWidget(self._tab_panel)

        # --- Rechter Content-Bereich ---
        content_widget = QWidget()
        content_widget.setObjectName("settingsContent")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("settingsContent")

        self._erstelle_allgemein_panel()
        self._erstelle_simplycal_panel()
        self._erstelle_firma_panel()
        self._erstelle_pruefer_panel()
        self._erstelle_messgeraete_panel()
        self._erstelle_system_panel()

        content_layout.addWidget(self._content_stack)
        haupt.addWidget(content_widget)

        # Erster Tab aktiv
        self._tab_geklickt(0)

    def _tab_geklickt(self, index):
        for btn in self._tab_buttons:
            btn.setze_aktiv(False)
        self._tab_buttons[index].setze_aktiv(True)
        self._content_stack.setCurrentIndex(index)

    # --- Hilfsmethoden fuer Panels ---

    def _erstelle_scroll_panel(self):
        """Erstellt ein scrollbares Panel fuer einen Tab."""
        scroll = QScrollArea()
        scroll.setObjectName("detailScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        inhalt = QWidget()
        inhalt.setObjectName("settingsContent")
        layout = QVBoxLayout(inhalt)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        scroll.setWidget(inhalt)
        self._content_stack.addWidget(scroll)
        return layout

    def _section_titel(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("settingsSectionTitel")
        return lbl

    def _settings_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("settingsLabel")
        return lbl

    def _settings_input(self, wert="", breite=None):
        inp = QLineEdit(wert)
        inp.setObjectName("settingsInput")
        inp.setFixedHeight(36)
        if breite:
            inp.setFixedWidth(breite)
        else:
            inp.setMaximumWidth(300)
        return inp

    def _trennlinie(self):
        linie = QFrame()
        linie.setObjectName("settingsTrennlinie")
        linie.setFrameShape(QFrame.HLine)
        return linie

    def _pfad_zeile(self, aktueller_pfad="", dialog_titel="Ordner wählen"):
        """Erstellt Textfeld + Durchsuchen-Button fuer Ordnerpfade."""
        zeile = QHBoxLayout()
        zeile.setSpacing(8)

        eingabe = self._settings_input(aktueller_pfad)
        zeile.addWidget(eingabe)

        btn = QPushButton("Durchsuchen")
        btn.setObjectName("settingsBrowseButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.clicked.connect(
            lambda: self._ordner_waehlen(eingabe, dialog_titel)
        )
        zeile.addWidget(btn)

        return zeile, eingabe

    def _ordner_waehlen(self, eingabe_feld, titel):
        pfad = QFileDialog.getExistingDirectory(self, titel, eingabe_feld.text())
        if pfad:
            eingabe_feld.setText(pfad)

    def _bild_upload_zeile(self, aktueller_dateiname="", vorschau_groesse=(60, 40)):
        """Erstellt Thumbnail-Vorschau + Datei-waehlen-Button."""
        container = QWidget()
        container.setObjectName("detailScrollInhalt")
        zeile = QHBoxLayout(container)
        zeile.setContentsMargins(0, 0, 0, 0)
        zeile.setSpacing(12)

        vorschau = QLabel()
        vorschau.setObjectName("settingsImagePreview")
        vorschau.setFixedSize(vorschau_groesse[0], vorschau_groesse[1])
        vorschau.setAlignment(Qt.AlignCenter)
        vorschau.setScaledContents(False)

        # Vorschau laden
        self._aktualisiere_bild_vorschau(vorschau, aktueller_dateiname, vorschau_groesse)

        zeile.addWidget(vorschau)

        dateiname_label = QLabel(aktueller_dateiname if aktueller_dateiname else "Kein Bild")
        dateiname_label.setObjectName("settingsLabel")
        dateiname_label.setWordWrap(True)
        zeile.addWidget(dateiname_label, 1)

        btn = QPushButton("Wählen")
        btn.setObjectName("settingsBrowseButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.setFixedWidth(70)
        zeile.addWidget(btn)

        return container, vorschau, dateiname_label, btn

    def _aktualisiere_bild_vorschau(self, label, dateiname, groesse=(60, 40)):
        """Laedt ein Bild als Thumbnail in ein QLabel."""
        if not dateiname:
            label.clear()
            return

        # In data/ oder Arbeitsverzeichnis suchen
        data_pfad = os.path.join(self._settings.get_data_verzeichnis(), dateiname)
        alt_pfad = os.path.join(os.getcwd(), dateiname)

        pfad = data_pfad if os.path.exists(data_pfad) else alt_pfad

        if os.path.exists(pfad):
            pixmap = QPixmap(pfad)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(
                    groesse[0] - 8, groesse[1] - 8,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
                return
        label.clear()

    def _bild_waehlen(self, vorschau, dateiname_label, speicher_callback):
        """Oeffnet Datei-Dialog, kopiert Bild nach data/ und aktualisiert Vorschau."""
        pfad, _ = QFileDialog.getOpenFileName(
            self, "Bild wählen", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not pfad:
            return

        # Nach data/ kopieren
        data_dir = self._settings.get_data_verzeichnis()
        dateiname = os.path.basename(pfad)
        ziel = os.path.join(data_dir, dateiname)
        if os.path.abspath(pfad) != os.path.abspath(ziel):
            shutil.copy2(pfad, ziel)

        # Vorschau + Label aktualisieren
        dateiname_label.setText(dateiname)
        self._aktualisiere_bild_vorschau(vorschau, dateiname)

        # In Settings speichern
        speicher_callback(dateiname)
        self.settings_geaendert.emit()

    # --- Panel: Allgemein ---

    def _erstelle_allgemein_panel(self):
        layout = self._erstelle_scroll_panel()

        layout.addWidget(self._section_titel("Allgemein"))

        # Protokoll-Speicherpfad
        layout.addWidget(self._settings_label("Protokoll-Speicherpfad"))
        pfad_zeile, self._protokoll_input = self._pfad_zeile(
            self._settings.get_protokoll_path(), "Protokoll-Ordner wählen"
        )
        self._protokoll_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_protokoll_path, t)
        )
        layout.addLayout(pfad_zeile)

        layout.addStretch()

    # --- Panel: SimplyCal ---

    def _erstelle_simplycal_panel(self):
        layout = self._erstelle_scroll_panel()

        layout.addWidget(self._section_titel("SimplyCal"))

        # DB-Verzeichnis
        layout.addWidget(self._settings_label("Datenbank-Verzeichnis"))
        pfad_zeile, self._db_pfad_input = self._pfad_zeile(
            self._settings.get_db_verzeichnis(), "SimplyCal-Ordner wählen"
        )
        self._db_pfad_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_db_verzeichnis, t)
        )
        layout.addLayout(pfad_zeile)

        layout.addStretch()

    # --- Panel: Firma ---

    def _erstelle_firma_panel(self):
        layout = self._erstelle_scroll_panel()

        layout.addWidget(self._section_titel("Firmendaten"))

        firmen_daten = self._settings.get_company_data()

        # Zeile 1: Firmenname + Straße nebeneinander
        zeile1 = QHBoxLayout()
        zeile1.setSpacing(12)

        firma_box = QVBoxLayout()
        firma_box.setSpacing(6)
        firma_box.addWidget(self._settings_label("Firmenname"))
        self._firma_input = self._settings_input(firmen_daten['firma'])
        self._firma_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'firma', v), t
            )
        )
        firma_box.addWidget(self._firma_input)
        zeile1.addLayout(firma_box, 1)

        strasse_box = QVBoxLayout()
        strasse_box.setSpacing(6)
        strasse_box.addWidget(self._settings_label("Straße"))
        self._strasse_input = self._settings_input(firmen_daten['strasse'])
        self._strasse_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'strasse', v), t
            )
        )
        strasse_box.addWidget(self._strasse_input)
        zeile1.addLayout(strasse_box, 1)

        layout.addLayout(zeile1)

        # Zeile 2: PLZ + Ort + Land
        zeile2 = QHBoxLayout()
        zeile2.setSpacing(12)

        plz_box = QVBoxLayout()
        plz_box.setSpacing(6)
        plz_box.addWidget(self._settings_label("PLZ"))
        self._plz_input = self._settings_input(firmen_daten['plz'], breite=80)
        self._plz_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'plz', v), t
            )
        )
        plz_box.addWidget(self._plz_input)
        zeile2.addLayout(plz_box)

        ort_box = QVBoxLayout()
        ort_box.setSpacing(6)
        ort_box.addWidget(self._settings_label("Ort"))
        self._ort_input = self._settings_input(firmen_daten['ort'])
        self._ort_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'ort', v), t
            )
        )
        ort_box.addWidget(self._ort_input)
        zeile2.addLayout(ort_box, 1)

        land_box = QVBoxLayout()
        land_box.setSpacing(6)
        land_box.addWidget(self._settings_label("Land"))
        self._land_input = self._settings_input(
            self._settings.get_setting('FIRMA', 'land', 'Germany')
        )
        self._land_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'land', v), t
            )
        )
        land_box.addWidget(self._land_input)
        zeile2.addLayout(land_box, 1)

        layout.addLayout(zeile2)

        # Zeile 3: Telefon + Webseite nebeneinander
        zeile3 = QHBoxLayout()
        zeile3.setSpacing(12)

        tel_box = QVBoxLayout()
        tel_box.setSpacing(6)
        tel_box.addWidget(self._settings_label("Telefon"))
        self._telefon_input = self._settings_input(
            self._settings.get_setting('FIRMA', 'telefon', '')
        )
        self._telefon_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'telefon', v), t
            )
        )
        tel_box.addWidget(self._telefon_input)
        zeile3.addLayout(tel_box, 1)

        web_box = QVBoxLayout()
        web_box.setSpacing(6)
        web_box.addWidget(self._settings_label("Webseite"))
        self._webseite_input = self._settings_input(
            self._settings.get_setting('FIRMA', 'webseite', '')
        )
        self._webseite_input.textChanged.connect(
            lambda t: self._auto_speichern(
                lambda v: self._settings.set_setting('FIRMA', 'webseite', v), t
            )
        )
        web_box.addWidget(self._webseite_input)
        zeile3.addLayout(web_box, 1)

        layout.addLayout(zeile3)

        layout.addWidget(self._trennlinie())

        # Logo + Stempel nebeneinander
        bilder_zeile = QHBoxLayout()
        bilder_zeile.setSpacing(16)

        # Logo
        logo_box = QVBoxLayout()
        logo_box.setSpacing(6)
        logo_box.addWidget(self._settings_label("Firmenlogo"))
        logo_datei = self._settings.get_setting('FIRMA', 'logo', '')
        logo_container, self._logo_vorschau, self._logo_label, logo_btn = \
            self._bild_upload_zeile(logo_datei, vorschau_groesse=(48, 32))
        logo_btn.clicked.connect(
            lambda: self._bild_waehlen(
                self._logo_vorschau, self._logo_label,
                lambda f: self._settings.set_setting('FIRMA', 'logo', f)
            )
        )
        logo_box.addWidget(logo_container)
        bilder_zeile.addLayout(logo_box, 1)

        # Stempel
        stempel_box = QVBoxLayout()
        stempel_box.setSpacing(6)
        stempel_box.addWidget(self._settings_label("Firmenstempel"))
        stempel_datei = self._settings.get_setting('FIRMA', 'stempel', '')
        stempel_container, self._stempel_vorschau, self._stempel_label, stempel_btn = \
            self._bild_upload_zeile(stempel_datei, vorschau_groesse=(48, 32))
        stempel_btn.clicked.connect(
            lambda: self._bild_waehlen(
                self._stempel_vorschau, self._stempel_label,
                lambda f: self._settings.set_setting('FIRMA', 'stempel', f)
            )
        )
        stempel_box.addWidget(stempel_container)
        bilder_zeile.addLayout(stempel_box, 1)

        layout.addLayout(bilder_zeile)

        layout.addStretch()

    # --- Panel: Pruefer ---

    def _erstelle_pruefer_panel(self):
        layout = self._erstelle_scroll_panel()

        layout.addWidget(self._section_titel("Prüfer"))

        # Kürzel + Name in einer Zeile
        name_zeile = QHBoxLayout()
        name_zeile.setSpacing(12)

        kuerzel_box = QVBoxLayout()
        kuerzel_box.setSpacing(6)
        kuerzel_box.setContentsMargins(0, 0, 0, 0)
        kuerzel_box.addWidget(self._settings_label("Kürzel"))
        gespeichertes_kuerzel = self._settings.get_setting('PRUEFER', 'kuerzel', '')
        self._pruefer_kuerzel_input = self._settings_input(gespeichertes_kuerzel, breite=80)
        self._pruefer_kuerzel_input.setMaxLength(5)
        self._pruefer_kuerzel_input.setPlaceholderText(
            self._settings.get_pruefer_kuerzel() or "Auto"
        )
        self._pruefer_kuerzel_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_pruefer_kuerzel, t)
        )
        kuerzel_box.addWidget(self._pruefer_kuerzel_input, alignment=Qt.AlignLeft)
        name_zeile.addLayout(kuerzel_box)

        name_box = QVBoxLayout()
        name_box.setSpacing(6)
        name_box.addWidget(self._settings_label("Name"))
        self._pruefer_name_input = self._settings_input(self._settings.get_pruefer_name())
        self._pruefer_name_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_pruefer_name, t)
        )
        name_box.addWidget(self._pruefer_name_input)
        name_zeile.addLayout(name_box, 1)

        layout.addLayout(name_zeile)

        layout.addWidget(self._trennlinie())

        # Unterschrift
        layout.addWidget(self._settings_label("Unterschrift"))
        unterschrift_datei = self._settings.get_setting('PRUEFER', 'unterschrift', '')
        us_container, self._us_vorschau, self._us_label, us_btn = \
            self._bild_upload_zeile(unterschrift_datei, vorschau_groesse=(48, 32))
        us_btn.clicked.connect(
            lambda: self._bild_waehlen(
                self._us_vorschau, self._us_label,
                lambda f: self._settings.set_setting('PRUEFER', 'unterschrift', f)
            )
        )
        layout.addWidget(us_container)

        layout.addStretch()

    # --- Panel: Messgeraete ---

    def _erstelle_messgeraete_panel(self):
        layout = self._erstelle_scroll_panel()

        # Temperatur-Messgeraete
        layout.addWidget(self._section_titel("Temperaturmessgeräte"))

        self._temp_geraete_layout = QVBoxLayout()
        self._temp_geraete_layout.setSpacing(8)
        self._temp_geraete_widgets = []

        for geraet in self._settings.get_messgeraete_strukturiert("temp"):
            self._geraet_zeile_hinzufuegen(
                self._temp_geraete_layout, self._temp_geraete_widgets,
                "temp", geraet['name'], geraet['seriennummer']
            )

        layout.addLayout(self._temp_geraete_layout)

        btn_temp_add = QPushButton("  Messgerät hinzufügen")
        btn_temp_add.setObjectName("settingsAddButton")
        btn_temp_add.setIcon(qta.icon("ri.add-line", color="#8a8fa0"))
        btn_temp_add.setCursor(Qt.PointingHandCursor)
        btn_temp_add.setFixedHeight(36)
        btn_temp_add.clicked.connect(
            lambda: self._geraet_zeile_hinzufuegen(
                self._temp_geraete_layout, self._temp_geraete_widgets, "temp"
            )
        )
        layout.addWidget(btn_temp_add)

        layout.addWidget(self._trennlinie())

        # VDE-Messgeraete
        layout.addWidget(self._section_titel("VDE-Messgeräte"))

        self._vde_geraete_layout = QVBoxLayout()
        self._vde_geraete_layout.setSpacing(8)
        self._vde_geraete_widgets = []

        for geraet in self._settings.get_messgeraete_strukturiert("vde"):
            self._geraet_zeile_hinzufuegen(
                self._vde_geraete_layout, self._vde_geraete_widgets,
                "vde", geraet['name'], geraet['seriennummer']
            )

        layout.addLayout(self._vde_geraete_layout)

        btn_vde_add = QPushButton("  Messgerät hinzufügen")
        btn_vde_add.setObjectName("settingsAddButton")
        btn_vde_add.setIcon(qta.icon("ri.add-line", color="#8a8fa0"))
        btn_vde_add.setCursor(Qt.PointingHandCursor)
        btn_vde_add.setFixedHeight(36)
        btn_vde_add.clicked.connect(
            lambda: self._geraet_zeile_hinzufuegen(
                self._vde_geraete_layout, self._vde_geraete_widgets, "vde"
            )
        )
        layout.addWidget(btn_vde_add)

        layout.addStretch()

    def _geraet_zeile_hinzufuegen(self, parent_layout, widget_liste, typ,
                                    name="", seriennummer=""):
        """Fuegt eine Messgeraete-Zeile hinzu (Name + S/N + Entfernen-Button)."""
        if len(widget_liste) >= 10:
            return

        container = QWidget()
        container.setObjectName("detailScrollInhalt")
        zeile = QHBoxLayout(container)
        zeile.setContentsMargins(0, 0, 0, 0)
        zeile.setSpacing(8)

        name_input = self._settings_input(name)
        name_input.setPlaceholderText("Gerätename")
        name_input.textChanged.connect(lambda: self._speichere_messgeraete(typ))
        zeile.addWidget(name_input, 2)

        sn_input = self._settings_input(seriennummer)
        sn_input.setPlaceholderText("Seriennummer")
        sn_input.textChanged.connect(lambda: self._speichere_messgeraete(typ))
        zeile.addWidget(sn_input, 1)

        btn_entfernen = QPushButton()
        btn_entfernen.setObjectName("settingsRemoveButton")
        btn_entfernen.setIcon(qta.icon("ri.close-line", color="#8a8fa0"))
        btn_entfernen.setFixedSize(32, 32)
        btn_entfernen.setCursor(Qt.PointingHandCursor)
        btn_entfernen.setToolTip("Entfernen")
        btn_entfernen.clicked.connect(
            lambda: self._geraet_entfernen(
                parent_layout, widget_liste, container, typ
            )
        )
        zeile.addWidget(btn_entfernen)

        widget_info = {"container": container, "name": name_input, "sn": sn_input}
        widget_liste.append(widget_info)
        parent_layout.addWidget(container)

    def _geraet_entfernen(self, parent_layout, widget_liste, container, typ):
        """Entfernt eine Messgeraete-Zeile."""
        for i, info in enumerate(widget_liste):
            if info["container"] is container:
                widget_liste.pop(i)
                break
        parent_layout.removeWidget(container)
        container.deleteLater()
        self._speichere_messgeraete(typ)

    def _speichere_messgeraete(self, typ):
        """Speichert alle Messgeraete eines Typs (debounced)."""
        widget_liste = self._temp_geraete_widgets if typ == "temp" else self._vde_geraete_widgets
        geraete = []
        for info in widget_liste:
            name = info["name"].text().strip()
            sn = info["sn"].text().strip()
            if name or sn:
                geraete.append({"name": name, "seriennummer": sn})
        self._settings.set_messgeraete_strukturiert(typ, geraete)
        self.settings_geaendert.emit()

    # --- Panel: System ---

    def _erstelle_system_panel(self):
        layout = self._erstelle_scroll_panel()

        # --- Temperatur-Standardwerte ---
        layout.addWidget(self._section_titel("Temperatur-Standardwerte"))

        temp_zeile = QHBoxLayout()
        temp_zeile.setSpacing(12)

        t1_box = QVBoxLayout()
        t1_box.setSpacing(6)
        t1_box.addWidget(self._settings_label("Soll-Temp. PP1 (°C)"))
        self._soll_temp1_input = self._settings_input(
            self._settings.get_standard_soll_temp1(), breite=100
        )
        self._soll_temp1_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_soll_temp1, t)
        )
        t1_box.addWidget(self._soll_temp1_input)
        temp_zeile.addLayout(t1_box)

        t2_box = QVBoxLayout()
        t2_box.setSpacing(6)
        t2_box.addWidget(self._settings_label("Soll-Temp. PP2 (°C)"))
        self._soll_temp2_input = self._settings_input(
            self._settings.get_standard_soll_temp2(), breite=100
        )
        self._soll_temp2_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_soll_temp2, t)
        )
        t2_box.addWidget(self._soll_temp2_input)
        temp_zeile.addLayout(t2_box)

        umg_box = QVBoxLayout()
        umg_box.setSpacing(6)
        umg_box.addWidget(self._settings_label("Umgebungstemp. (°C)"))
        self._umgebung_temp_input = self._settings_input(
            self._settings.get_standard_umgebung_temp(), breite=100
        )
        self._umgebung_temp_input.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_umgebung_temp, t)
        )
        umg_box.addWidget(self._umgebung_temp_input)
        temp_zeile.addLayout(umg_box)

        temp_zeile.addStretch()
        layout.addLayout(temp_zeile)

        layout.addWidget(self._trennlinie())

        # --- VDE-Standardwerte ---
        layout.addWidget(self._section_titel("VDE-Standardwerte"))

        vde_zeile = QHBoxLayout()
        vde_zeile.setSpacing(12)

        ns_box = QVBoxLayout()
        ns_box.setSpacing(6)
        ns_box.addWidget(self._settings_label("Nennspannung (V)"))
        self._std_nennspannung = self._settings_input(
            self._settings.get_standard_nennspannung(), breite=80
        )
        self._std_nennspannung.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_nennspannung, t)
        )
        ns_box.addWidget(self._std_nennspannung)
        vde_zeile.addLayout(ns_box)

        freq_box = QVBoxLayout()
        freq_box.setSpacing(6)
        freq_box.addWidget(self._settings_label("Frequenz (Hz)"))
        self._std_frequenz = self._settings_input(
            self._settings.get_standard_frequenz(), breite=80
        )
        self._std_frequenz.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_frequenz, t)
        )
        freq_box.addWidget(self._std_frequenz)
        vde_zeile.addLayout(freq_box)

        cos_box = QVBoxLayout()
        cos_box.setSpacing(6)
        cos_box.addWidget(self._settings_label("cos φ"))
        self._std_cosphi = self._settings_input(
            self._settings.get_standard_cosphi(), breite=80
        )
        self._std_cosphi.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_cosphi, t)
        )
        cos_box.addWidget(self._std_cosphi)
        vde_zeile.addLayout(cos_box)

        vde_zeile.addStretch()
        layout.addLayout(vde_zeile)

        # VDE Messwerte-Standardwerte
        layout.addWidget(self._settings_label("Messwerte-Vorgaben"))

        mw_zeile = QHBoxLayout()
        mw_zeile.setSpacing(12)

        rpe_box = QVBoxLayout()
        rpe_box.setSpacing(6)
        rpe_box.addWidget(self._settings_label("RPE (Ω)"))
        self._std_rpe = self._settings_input(
            self._settings.get_standard_rpe(), breite=80
        )
        self._std_rpe.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_rpe, t)
        )
        rpe_box.addWidget(self._std_rpe)
        mw_zeile.addLayout(rpe_box)

        riso_box = QVBoxLayout()
        riso_box.setSpacing(6)
        riso_box.addWidget(self._settings_label("RISO (MΩ)"))
        self._std_riso = self._settings_input(
            self._settings.get_standard_riso(), breite=80
        )
        self._std_riso.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_riso, t)
        )
        riso_box.addWidget(self._std_riso)
        mw_zeile.addLayout(riso_box)

        ipe_box = QVBoxLayout()
        ipe_box.setSpacing(6)
        ipe_box.addWidget(self._settings_label("IPE (mA)"))
        self._std_ipe = self._settings_input(
            self._settings.get_standard_ipe(), breite=80
        )
        self._std_ipe.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_ipe, t)
        )
        ipe_box.addWidget(self._std_ipe)
        mw_zeile.addLayout(ipe_box)

        ib_box = QVBoxLayout()
        ib_box.setSpacing(6)
        ib_box.addWidget(self._settings_label("IB (mA)"))
        self._std_ib = self._settings_input(
            self._settings.get_standard_ib(), breite=80
        )
        self._std_ib.textChanged.connect(
            lambda t: self._auto_speichern(self._settings.set_standard_ib, t)
        )
        ib_box.addWidget(self._std_ib)
        mw_zeile.addLayout(ib_box)

        mw_zeile.addStretch()
        layout.addLayout(mw_zeile)

        layout.addWidget(self._trennlinie())

        # --- Infoboxen (2x2 Grid) ---
        layout.addWidget(self._section_titel("Infoboxen"))

        self._infobox_toggles = {}
        infobox_items = [
            ("temp_info", "Temp — Hinweise"),
            ("vde_grundeinstellungen", "VDE — Grundeinstellungen"),
            ("vde_sichtpruefung", "VDE — Sichtprüfung"),
            ("vde_messwerte", "VDE — Messwerte"),
        ]

        from PySide6.QtWidgets import QGridLayout
        ib_grid = QGridLayout()
        ib_grid.setSpacing(6)
        for i, (key, label) in enumerate(infobox_items):
            toggle_btn = QPushButton(f"  {label}")
            toggle_btn.setCursor(Qt.PointingHandCursor)
            toggle_btn.setFixedHeight(32)
            toggle_btn.setProperty("bestanden", self._settings.get_infobox_anzeigen(key))
            toggle_btn.clicked.connect(
                lambda _, k=key, b=toggle_btn: self._toggle_infobox(k, b)
            )
            self._infobox_toggles[key] = toggle_btn
            ib_grid.addWidget(toggle_btn, i // 2, i % 2)

        layout.addLayout(ib_grid)

        layout.addStretch()

    # --- Auto-Save ---

    def _auto_speichern(self, setter, wert):
        """Speichert sofort bei jeder Aenderung."""
        setter(wert)
        self.settings_geaendert.emit()

    def _toggle_infobox(self, key, btn):
        """Schaltet eine Infobox-Einstellung um."""
        aktuell = btn.property("bestanden")
        btn.setProperty("bestanden", not aktuell)
        self._settings.set_infobox_anzeigen(key, not aktuell)
        self._aktualisiere_infobox_toggle_styles()
        self.settings_geaendert.emit()

    def _aktualisiere_infobox_toggle_styles(self):
        """Aktualisiert die Icons und Textfarbe aller Infobox-Toggles."""
        text_farbe = self._aktuelle_farben.get("text_primaer", "#e0e0e0")
        for key, btn in self._infobox_toggles.items():
            bestanden = btn.property("bestanden")
            if bestanden:
                farbe = self._aktuelle_farben.get("erfolg", "#4caf50")
                btn.setIcon(qta.icon("ri.checkbox-circle-line", color=farbe))
            else:
                farbe = self._aktuelle_farben.get("fehler", "#f44336")
                btn.setIcon(qta.icon("ri.close-circle-line", color=farbe))
            btn.setIconSize(QSize(22, 22))
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: none; "
                f"text-align: left; font-size: 13px; padding-left: 2px; "
                f"color: {text_farbe}; }}"
            )

    # --- Oeffentliche Methoden ---

    def lade_werte(self):
        """Laedt alle aktuellen Werte aus den Settings in die Felder."""
        self._protokoll_input.setText(self._settings.get_protokoll_path())
        self._db_pfad_input.setText(self._settings.get_db_verzeichnis())

        firmen_daten = self._settings.get_company_data()
        self._firma_input.setText(firmen_daten['firma'])
        self._strasse_input.setText(firmen_daten['strasse'])
        self._plz_input.setText(firmen_daten['plz'])
        self._ort_input.setText(firmen_daten['ort'])

        self._pruefer_name_input.setText(self._settings.get_pruefer_name())
        self._pruefer_kuerzel_input.setText(
            self._settings.get_setting('PRUEFER', 'kuerzel', '')
        )

        self._soll_temp1_input.setText(self._settings.get_standard_soll_temp1())
        self._soll_temp2_input.setText(self._settings.get_standard_soll_temp2())
        self._umgebung_temp_input.setText(self._settings.get_standard_umgebung_temp())
        self._std_nennspannung.setText(self._settings.get_standard_nennspannung())
        self._std_frequenz.setText(self._settings.get_standard_frequenz())
        self._std_cosphi.setText(self._settings.get_standard_cosphi())
        self._std_rpe.setText(self._settings.get_standard_rpe())
        self._std_riso.setText(self._settings.get_standard_riso())
        self._std_ipe.setText(self._settings.get_standard_ipe())
        self._std_ib.setText(self._settings.get_standard_ib())
        for key, btn in self._infobox_toggles.items():
            btn.setProperty("bestanden", self._settings.get_infobox_anzeigen(key))
        self._aktualisiere_infobox_toggle_styles()

        # Immer beim ersten Tab starten
        self._tab_geklickt(0)

    def aktualisiere_theme(self, farben, ist_dark=None):
        """Aktualisiert die Farben bei Theme-Wechsel."""
        self._aktuelle_farben = farben
        if ist_dark is not None:
            self._ist_dark = ist_dark

        # Tab-Button-Farben aktualisieren
        for btn in self._tab_buttons:
            btn.aktualisiere_farben(
                farben["icon_farbe"], farben["text_aktiv"], farben.get("indicator", "#ed1b24")
            )

        # Infobox-Toggle-Farben aktualisieren
        self._aktualisiere_infobox_toggle_styles()

    def mousePressEvent(self, event):
        """Akzeptiert Mouse-Events um Propagation zum Overlay zu verhindern."""
        event.accept()
