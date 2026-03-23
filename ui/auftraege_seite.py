"""Auftraege-Seite mit Auftrags-Dropdown und Waagentabelle mit Icon-Buttons."""

import os
import glob

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyle, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QEvent, QTimer
from PySide6.QtGui import QColor, QPen, QBrush
import qtawesome as qta

from settings import Settings
from external_db import ExternalDatabase


class ChevronComboBox(QComboBox):
    """ComboBox mit Chevron-Icon das sich beim Oeffnen/Schliessen dreht."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ist_offen = False
        self._icon_farbe = "#8a8fa0"

    def showPopup(self):
        super().showPopup()
        self._ist_offen = True
        self._aktualisiere_chevron()

    def hidePopup(self):
        super().hidePopup()
        self._ist_offen = False
        self._aktualisiere_chevron()

    def setze_icon_farbe(self, farbe: str):
        self._icon_farbe = farbe
        self._aktualisiere_chevron()

    def _aktualisiere_chevron(self):
        import tempfile
        icon_name = "ri.arrow-up-s-line" if self._ist_offen else "ri.arrow-down-s-line"
        icon = qta.icon(icon_name, color=self._icon_farbe)
        pixmap = icon.pixmap(12, 12)
        pfad = os.path.join(tempfile.gettempdir(), "wj_chevron.png")
        pixmap.save(pfad, "PNG")
        pfad_css = pfad.replace("\\", "/")
        self.setStyleSheet(f"""
            QComboBox#auftragDropdown::down-arrow {{
                image: url({pfad_css});
                width: 12px;
                height: 12px;
            }}
        """)


class ZeilenHoverDelegate(QStyledItemDelegate):
    """Delegate der die ganze Zeile bei Hover hervorhebt und Status-Icons zeichnet."""

    FADE_SCHRITTE = 6
    FADE_INTERVALL = 16  # ~60fps

    def __init__(self, tabelle, parent=None):
        super().__init__(parent)
        self._tabelle = tabelle
        self._hover_zeile = -1
        self._hover_farbe = QColor("#3a4158")
        self._selected_farbe = QColor("#343b50")
        self._erfolg_farbe = QColor("#4caf50")
        self._fehler_farbe = QColor("#f44336")
        self._icon_cache = {}

        # Alpha-Werte pro Zeile fuer sanftes Fade (0.0 - 1.0)
        self._zeilen_alpha = {}
        self._fade_timer = QTimer(parent)
        self._fade_timer.setInterval(self.FADE_INTERVALL)
        self._fade_timer.timeout.connect(self._fade_tick)

    def setze_hover_zeile(self, zeile):
        if zeile != self._hover_zeile:
            self._hover_zeile = zeile
            if not self._fade_timer.isActive():
                self._fade_timer.start()

    def _fade_tick(self):
        """Aktualisiert Alpha-Werte: Hover-Zeile blendet ein, andere aus."""
        aenderung = False
        schritt = 1.0 / self.FADE_SCHRITTE

        relevante_zeilen = set(self._zeilen_alpha.keys())
        if self._hover_zeile >= 0:
            relevante_zeilen.add(self._hover_zeile)

        for zeile in relevante_zeilen:
            aktuell = self._zeilen_alpha.get(zeile, 0.0)
            if zeile == self._hover_zeile:
                if aktuell < 1.0:
                    self._zeilen_alpha[zeile] = min(1.0, aktuell + schritt)
                    aenderung = True
                    self._invalidiere_zeile(zeile)
            else:
                if aktuell > 0.0:
                    neuer_wert = max(0.0, aktuell - schritt)
                    if neuer_wert == 0.0:
                        del self._zeilen_alpha[zeile]
                    else:
                        self._zeilen_alpha[zeile] = neuer_wert
                    aenderung = True
                    self._invalidiere_zeile(zeile)

        if not aenderung:
            self._fade_timer.stop()

    def _invalidiere_zeile(self, zeile):
        model = self._tabelle.model()
        if not model or zeile < 0 or zeile >= model.rowCount():
            return
        for spalte in range(model.columnCount()):
            index = model.index(zeile, spalte)
            self._tabelle.update(index)

    def aktualisiere_farben(self, hover_farbe, selected_farbe,
                            erfolg_farbe=None, fehler_farbe=None):
        """Aktualisiert die Farben bei Theme-Wechsel."""
        self._hover_farbe = QColor(hover_farbe)
        self._selected_farbe = QColor(selected_farbe)
        if erfolg_farbe:
            self._erfolg_farbe = QColor(erfolg_farbe)
        if fehler_farbe:
            self._fehler_farbe = QColor(fehler_farbe)
        self._icon_cache.clear()

    def _hole_status_icon(self, typ, erledigt):
        """Gibt ein gecachtes Status-Icon-Pixmap zurueck."""
        key = (typ, erledigt)
        if key not in self._icon_cache:
            if typ == "temp":
                name = "ri.thermometer-fill" if erledigt else "ri.thermometer-line"
            else:
                name = "ri.flashlight-fill" if erledigt else "ri.flashlight-line"
            farbe = self._erfolg_farbe if erledigt else self._fehler_farbe
            self._icon_cache[key] = qta.icon(name, color=farbe.name()).pixmap(20, 20)
        return self._icon_cache[key]

    def paint(self, painter, option, index):
        """Zeichnet Zeilen mit Hover, Selection und Status-Icons."""
        # Hover-Hintergrund mit Alpha-Blend
        alpha = self._zeilen_alpha.get(index.row(), 0.0)
        if alpha > 0.0:
            painter.save()
            farbe = QColor(self._hover_farbe)
            farbe.setAlphaF(alpha)
            painter.fillRect(option.rect, farbe)
            painter.restore()

        # Selection-Hintergrund
        if option.state & QStyle.State_Selected:
            painter.save()
            painter.fillRect(option.rect, self._selected_farbe)
            painter.restore()

        # Status-Spalten: Icon statt Text
        if index.column() in (5, 6):
            status = index.data(Qt.UserRole)
            erledigt = status == "erledigt"
            typ = "temp" if index.column() == 5 else "vde"
            pixmap = self._hole_status_icon(typ, erledigt)
            if pixmap:
                x = option.rect.x() + (option.rect.width() - pixmap.width()) // 2
                y = option.rect.y() + (option.rect.height() - pixmap.height()) // 2
                painter.drawPixmap(x, y, pixmap)
            return

        # Text zeichnen (fuer alle anderen Spalten)
        painter.save()
        text_rect = option.rect.adjusted(10, 0, -10, 0)
        alignment = int(index.data(Qt.TextAlignmentRole) or (Qt.AlignLeft | Qt.AlignVCenter))
        farbe = index.data(Qt.ForegroundRole)
        if farbe and isinstance(farbe, QBrush):
            painter.setPen(QPen(farbe.color()))
        elif farbe and isinstance(farbe, QColor):
            painter.setPen(QPen(farbe))
        else:
            painter.setPen(QPen(option.palette.text().color()))
        painter.drawText(text_rect, alignment, index.data(Qt.DisplayRole) or "")
        painter.restore()


class AuftraegeSeite(QWidget):
    """Seite mit Auftragsauswahl und Waagentabelle mit klickbaren Status-Icons."""

    temp_geklickt = Signal(tuple)   # Sendet Waagen-Datensatz fuer Temp-Detail
    vde_geklickt = Signal(tuple)    # Sendet Waagen-Datensatz fuer VDE-Detail
    auftrag_gewechselt = Signal()   # Wird bei Auftragswechsel emittiert

    # Spalten-Definition: (Anzeigename, Index im DB-Ergebnis, Breite)
    SPALTEN = [
        ("WJ-Nummer", 0, 120),
        ("Hersteller", 3, 150),
        ("Modell", 4, 150),
        ("S/N", 1, 120),
        ("Standort", 5, 120),
        ("Temp", None, 60),   # Status-Icon-Spalte
        ("VDE", None, 60),    # Status-Icon-Spalte
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contentSeite")
        self._settings = Settings("settings.ini")
        self._waagen_daten = []
        self._waagen_map = {}  # WJ-Nummer -> waage_daten (vermeidet QVariant-Roundtrip)
        self._aktuelle_farben = None
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut die Auftraege-Seite auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Titel
        self._titel = QLabel("SimplyCal")
        self._titel.setObjectName("seitenTitel")
        self._titel.setStyleSheet("padding: 0px;")
        layout.addWidget(self._titel)

        # Datenbank + Auftrags-Auswahl
        auswahl_layout = QHBoxLayout()
        auswahl_layout.setSpacing(12)

        # Datenbank-Dropdown
        db_label = QLabel("Datenbank:")
        db_label.setObjectName("auftragLabel")
        auswahl_layout.addWidget(db_label)

        self._db_dropdown = ChevronComboBox()
        self._db_dropdown.setObjectName("auftragDropdown")
        self._db_dropdown.setMinimumWidth(200)
        self._db_dropdown.setFixedHeight(36)
        self._db_dropdown.currentIndexChanged.connect(self._datenbank_gewaehlt)
        auswahl_layout.addWidget(self._db_dropdown)

        # Auftrags-Dropdown
        auswahl_label = QLabel("Auftrag:")
        auswahl_label.setObjectName("auftragLabel")
        auswahl_layout.addWidget(auswahl_label)

        self._auftrags_dropdown = ChevronComboBox()
        self._auftrags_dropdown.setObjectName("auftragDropdown")
        self._auftrags_dropdown.setMinimumWidth(350)
        self._auftrags_dropdown.setFixedHeight(36)
        self._auftrags_dropdown.currentIndexChanged.connect(self._auftrag_gewaehlt)
        auswahl_layout.addWidget(self._auftrags_dropdown)

        auswahl_layout.addStretch()
        layout.addLayout(auswahl_layout)

        # Suchfeld
        self._such_input = QLineEdit()
        self._such_input.setObjectName("formInput")
        self._such_input.setPlaceholderText("Suche")
        self._such_input.setFixedHeight(36)
        self._such_input.setClearButtonEnabled(True)
        such_icon = qta.icon("ri.search-line", color="#8a8fa0")
        self._such_input.addAction(such_icon, QLineEdit.LeadingPosition)
        self._such_input.textChanged.connect(self._filtere_tabelle)
        layout.addWidget(self._such_input)

        # Waagentabelle
        self._tabelle = QTableWidget()
        self._tabelle.setObjectName("waageTabelle")
        self._tabelle.setColumnCount(len(self.SPALTEN))
        self._tabelle.setHorizontalHeaderLabels([s[0] for s in self.SPALTEN])
        self._tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tabelle.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tabelle.verticalHeader().setVisible(False)
        self._tabelle.verticalHeader().setDefaultSectionSize(40)
        self._tabelle.setShowGrid(False)
        self._tabelle.setSortingEnabled(True)
        self._tabelle.setFocusPolicy(Qt.NoFocus)
        self._tabelle.setMouseTracking(True)
        self._tabelle.viewport().setMouseTracking(True)

        # Hover-Delegate mit Icon-Support
        self._delegate = ZeilenHoverDelegate(self._tabelle, self._tabelle)
        self._tabelle.setItemDelegate(self._delegate)

        # Viewport EventFilter fuer Maus-Tracking und Klick-Handling
        self._tabelle.viewport().installEventFilter(self)

        # Spaltenbreiten
        header = self._tabelle.horizontalHeader()
        for i, (_, _, breite) in enumerate(self.SPALTEN):
            if breite:
                self._tabelle.setColumnWidth(i, breite)
        # Modell-Spalte dehnt sich
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        layout.addWidget(self._tabelle)

    def eventFilter(self, obj, event):
        """Trackt Mausposition fuer Zeilen-Hover und behandelt Klicks auf Status-Icons."""
        if obj == self._tabelle.viewport():
            if event.type() == QEvent.MouseMove:
                pos = event.position().toPoint()
                zeile = self._tabelle.rowAt(pos.y())
                spalte = self._tabelle.columnAt(pos.x())
                self._delegate.setze_hover_zeile(zeile)
                # Cursor aendern fuer Status-Spalten
                if spalte in (5, 6) and zeile >= 0:
                    self._tabelle.viewport().setCursor(Qt.PointingHandCursor)
                else:
                    self._tabelle.viewport().setCursor(Qt.ArrowCursor)

            elif event.type() == QEvent.Leave:
                self._delegate.setze_hover_zeile(-1)
                self._tabelle.viewport().setCursor(Qt.ArrowCursor)

            elif event.type() == QEvent.MouseButtonRelease:
                pos = event.position().toPoint()
                index = self._tabelle.indexAt(pos)
                if index.isValid() and index.column() in (5, 6):
                    waage = self._hole_waage_fuer_zeile(index.row())
                    if waage:
                        if index.column() == 5:
                            self.temp_geklickt.emit(waage)
                        else:
                            self.vde_geklickt.emit(waage)

        return super().eventFilter(obj, event)

    def _hole_waage_fuer_zeile(self, zeile):
        """Gibt die Waagendaten fuer eine Tabellenzeile zurueck (sortier-sicher)."""
        item = self._tabelle.item(zeile, 0)
        if item:
            wj_nummer = item.text()
            return self._waagen_map.get(wj_nummer)
        return None

    def lade_auftraege(self):
        """Laedt Datenbanken und Auftraege."""
        self._lade_datenbanken()

    def _lade_datenbanken(self):
        """Laedt verfuegbare SQLite-Dateien in den Datenbank-Dropdown."""
        self._db_dropdown.blockSignals(True)
        aktuelle_db = self._settings.get_selected_database()
        self._db_dropdown.clear()

        db_verzeichnis = self._settings.get_db_verzeichnis()
        if not db_verzeichnis or not os.path.isdir(db_verzeichnis):
            self._db_dropdown.addItem("-- Kein Verzeichnis --", None)
            self._db_dropdown.blockSignals(False)
            self._auftrags_dropdown.clear()
            self._auftrags_dropdown.addItem("-- Auftrag wählen --", None)
            return

        try:
            datenbanken = self._settings.get_sqlite_databases(db_verzeichnis)
        except Exception:
            datenbanken = []

        if not datenbanken:
            self._db_dropdown.addItem("-- Keine Datenbank --", None)
            self._db_dropdown.blockSignals(False)
            self._auftrags_dropdown.clear()
            self._auftrags_dropdown.addItem("-- Auftrag wählen --", None)
            return

        aktiver_index = 0
        for i, db_name in enumerate(datenbanken):
            self._db_dropdown.addItem(db_name, db_name)
            if db_name == aktuelle_db:
                aktiver_index = i

        self._db_dropdown.setCurrentIndex(aktiver_index)
        self._db_dropdown.blockSignals(False)

        # Auftraege fuer die aktive DB laden
        self._lade_auftraege_fuer_db(datenbanken[aktiver_index])

    def _datenbank_gewaehlt(self, index):
        """Wird aufgerufen wenn eine andere Datenbank gewaehlt wird."""
        db_name = self._db_dropdown.currentData()
        if db_name:
            self._settings.set_selected_database(db_name)
            self._lade_auftraege_fuer_db(db_name)

    def _lade_auftraege_fuer_db(self, db_name):
        """Laedt Auftraege aus einer bestimmten Datenbank."""
        self._auftrags_dropdown.blockSignals(True)
        self._auftrags_dropdown.clear()
        self._auftrags_dropdown.addItem("-- Auftrag wählen --", None)

        if not db_name:
            self._auftrags_dropdown.blockSignals(False)
            return

        letzter_auftrag = self._settings.get_letzter_auftrag()
        aktiver_index = 0

        try:
            db = ExternalDatabase(db_name)
            auftraege = db.get_auftragsinformationen()

            for i, (auf_nummer, auf_kunde, firma) in enumerate(auftraege):
                anzeige = f"{auf_nummer}  —  {firma}"
                self._auftrags_dropdown.addItem(anzeige, (auf_nummer, auf_kunde))
                if auf_nummer == letzter_auftrag:
                    aktiver_index = i + 1  # +1 wegen "-- Auftrag wählen --"

        except Exception as e:
            print(f"Fehler beim Laden der Auftraege: {e}")

        self._auftrags_dropdown.blockSignals(False)

        # Letzten Auftrag wiederherstellen und Waagen laden
        if aktiver_index > 0:
            self._auftrags_dropdown.setCurrentIndex(aktiver_index)
            daten = self._auftrags_dropdown.currentData()
            if daten:
                auf_nummer, auf_kunde = daten
                self._lade_waagen(auf_kunde)

    def _auftrag_gewaehlt(self, index):
        """Wird aufgerufen wenn ein Auftrag im Dropdown gewaehlt wird."""
        self.auftrag_gewechselt.emit()
        self._such_input.clear()
        daten = self._auftrags_dropdown.currentData()
        if not daten:
            self._tabelle.setRowCount(0)
            self._waagen_daten = []
            self._settings.set_letzter_auftrag('')
            return

        auf_nummer, auf_kunde = daten
        self._settings.set_letzter_auftrag(auf_nummer)
        self._lade_waagen(auf_kunde)

    def _lade_waagen(self, kundennummer):
        """Laedt Waagen fuer eine Kundennummer und fuellt die Tabelle."""
        db_name = self._settings.get_selected_database()
        if not db_name:
            return

        try:
            db = ExternalDatabase(db_name)
            self._waagen_daten = db.get_waagen_by_kunde(kundennummer)
        except Exception as e:
            print(f"Fehler beim Laden der Waagen: {e}")
            self._waagen_daten = []

        self._fuelle_tabelle()

    def _fuelle_tabelle(self):
        """Fuellt die Tabelle mit den geladenen Waagendaten."""
        self._tabelle.setSortingEnabled(False)
        self._tabelle.setRowCount(len(self._waagen_daten))
        self._waagen_map.clear()

        protokoll_pfad = self._settings.get_protokoll_path()

        for zeile, waage in enumerate(self._waagen_daten):
            # WJ-Nummer fuer Lookup-Map
            wj_nummer = str(waage[0]) if waage[0] else ""
            self._waagen_map[wj_nummer] = waage

            # Daten-Spalten
            for spalte, (_, db_index, _) in enumerate(self.SPALTEN):
                if db_index is not None:
                    wert = str(waage[db_index]) if waage[db_index] else ""
                    item = QTableWidgetItem(wert)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self._tabelle.setItem(zeile, spalte, item)

            wj_nummer = str(waage[0]) if waage[0] else ""

            # Status Temp (Spalte 5) -- Icon wird vom Delegate gezeichnet
            temp_status = self._pruefe_pdf_status("TK", wj_nummer, protokoll_pfad)
            temp_item = QTableWidgetItem()
            temp_item.setTextAlignment(Qt.AlignCenter)
            if temp_status:
                temp_item.setData(Qt.UserRole, "erledigt")
            self._tabelle.setItem(zeile, 5, temp_item)

            # Status VDE (Spalte 6)
            vde_status = self._pruefe_pdf_status("VDE", wj_nummer, protokoll_pfad)
            vde_item = QTableWidgetItem()
            vde_item.setTextAlignment(Qt.AlignCenter)
            if vde_status:
                vde_item.setData(Qt.UserRole, "erledigt")
            self._tabelle.setItem(zeile, 6, vde_item)

        self._tabelle.setSortingEnabled(True)

        # Stagger-Fade-In Animation fuer Zeilen
        self._starte_zeilen_animation()

    def _starte_zeilen_animation(self):
        """Startet gestaffeltes Fade-In fuer alle Tabellenzeilen."""
        self._zeilen_animationen = []
        anzahl = self._tabelle.rowCount()
        if anzahl == 0:
            return

        for zeile in range(anzahl):
            self._tabelle.setRowHeight(zeile, 0)

        for zeile in range(anzahl):
            delay = zeile * 30

            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda z=zeile: self._animiere_zeile(z, 40)
            )
            timer.start(delay)
            self._zeilen_animationen.append(timer)

    def _animiere_zeile(self, zeile: int, ziel_hoehe: int):
        """Animiert eine einzelne Zeile von Hoehe 0 auf Zielhoehe."""
        if zeile >= self._tabelle.rowCount():
            return

        aktuelle_hoehe = 0
        schritte = 8
        schritt_hoehe = ziel_hoehe / schritte

        def naechster_schritt():
            nonlocal aktuelle_hoehe
            aktuelle_hoehe += schritt_hoehe
            if aktuelle_hoehe >= ziel_hoehe:
                self._tabelle.setRowHeight(zeile, ziel_hoehe)
                return
            self._tabelle.setRowHeight(zeile, int(aktuelle_hoehe))
            QTimer.singleShot(12, naechster_schritt)

        naechster_schritt()

    def _pruefe_pdf_status(self, prefix, wj_nummer, protokoll_pfad):
        """Prueft ob ein PDF mit dem gegebenen Prefix und WJ-Nummer existiert."""
        if not wj_nummer or not protokoll_pfad or not os.path.isdir(protokoll_pfad):
            return False

        muster = os.path.join(protokoll_pfad, f"{prefix}_*_{wj_nummer}.pdf")
        treffer = glob.glob(muster)
        return len(treffer) > 0

    def _filtere_tabelle(self, suchtext):
        """Filtert die Tabelle nach dem Suchtext (durchsucht alle Daten-Spalten)."""
        suchtext = suchtext.strip().lower()
        for zeile in range(self._tabelle.rowCount()):
            if not suchtext:
                self._tabelle.setRowHidden(zeile, False)
                continue
            gefunden = False
            # Spalten 0-4 durchsuchen (WJ-Nummer, Hersteller, Modell, S/N, Standort)
            for spalte in range(5):
                item = self._tabelle.item(zeile, spalte)
                if item and suchtext in item.text().lower():
                    gefunden = True
                    break
            self._tabelle.setRowHidden(zeile, not gefunden)

    def get_aktuelle_kundennummer(self):
        """Gibt die Kundennummer des aktuell gewaehlten Auftrags zurueck."""
        daten = self._auftrags_dropdown.currentData()
        if daten:
            return daten[1]  # auf_kunde
        return None

    def aktualisiere_status(self, wj_nummer, typ):
        """Aktualisiert den Status einer Waage in der Tabelle nach PDF-Erstellung.

        Args:
            wj_nummer: WJ-Nummer als Teil der Kalibrierscheinnummer
            typ: "temp" oder "vde"
        """
        spalte = 5 if typ == "temp" else 6
        for zeile in range(self._tabelle.rowCount()):
            item = self._tabelle.item(zeile, 0)
            if item and item.text() == wj_nummer:
                status_item = self._tabelle.item(zeile, spalte)
                if status_item:
                    status_item.setData(Qt.UserRole, "erledigt")
                    # Neuzeichnung erzwingen
                    self._delegate._icon_cache.clear()
                    model = self._tabelle.model()
                    idx = model.index(zeile, spalte)
                    self._tabelle.update(idx)
                break

    def aktualisiere_theme(self, farben: dict):
        """Aktualisiert die Farben bei Theme-Wechsel."""
        self._aktuelle_farben = farben
        self._delegate.aktualisiere_farben(
            farben["hover_bg"], farben["aktiv_bg"],
            farben["erfolg"], farben["fehler"]
        )
        self._aktualisiere_dropdown_icon(farben)

    def _aktualisiere_dropdown_icon(self, farben: dict):
        """Aktualisiert die Chevron-Farbe in den Dropdowns."""
        self._auftrags_dropdown.setze_icon_farbe(farben["text_sekundaer"])
        self._db_dropdown.setze_icon_farbe(farben["text_sekundaer"])
