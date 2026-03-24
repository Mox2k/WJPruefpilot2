# Prime: WJPruefpilot PySide6 Migration

Lies zuerst diese Dateien vollstaendig, um den Projektstand zu verstehen:

1. `docs/content.md` -- Migrationsplan, Design-Entscheidungen, Fortschritts-Tracker, Session-Log
2. `CLAUDE.md` (Projekt-Root) -- Projekt-Konventionen, Tech-Stack, Architektur

Dann lies den aktuellen Code:

3. `ui/styles.py` -- Zentrale Farbdefinitionen (Dark/Light Theme) + Formular-Styles + Settings-Styles + Tooltip-Styling
4. `ui/main_window.py` -- Hauptfenster (Frameless, Win32 Snap/Resize, Sidebar, Content, DimmOverlay, Dialog, Settings-Overlay, Zustandspersistenz)
5. `ui/title_bar.py` -- Custom Title Bar (Toggle, Theme-Switch Sonne/Mond, Window Controls)
6. `ui/sidebar.py` -- Collapsible Sidebar mit WJ-Logo
7. `ui/auftraege_seite.py` -- SimplyCal-Seite (DB-Dropdown, Auftrags-Dropdown, Waagentabelle, Icon-Buttons, auftrag_gewechselt Signal)
8. `ui/detail_temp_seite.py` -- Temperaturjustage Detail-Seite (Formular, Live-Validierung, PDF mit Ueberschreib-Dialog, Infobox, Persistenz, Responsive, Standard-Temps aus Settings)
9. `ui/detail_vde_seite.py` -- VDE-Pruefung Detail-Seite (3-Seiten-Wizard, Stepper, Sichtpruefung-Toggles, dynamische Messwerte nach Schutzklasse, PDF-Generierung, Eingaben-Cache)
10. `ui/overlay_dialog.py` -- Wiederverwendbare modale Dialog-Komponente (Bestaetigung/Fehler/Warnung/Info)
11. `ui/settings_overlay.py` -- Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload nach data/, Messgeraete +/-, Pruefer-Kuerzel)
12. `main.py` -- Einstiegspunkt (Inter + Plus Jakarta Sans Schriftart laden)

Business-Logik-Dateien (wichtig fuer Kontext):

13. `external_db.py` -- SimplyCal-Datenbankzugriff (SQL-Queries, Spaltennamen)
14. `settings.py` -- Settings-Klasse (Pfade, Firmendaten, Messgeraete, Theme, Fensterzustand, Standard-Temps, data/-Ordner, Multi-Instanz-sicher)
15. `pdf_base_generator.py` -- Basisklasse (add_waagen_data, Bildverarbeitung mit data/-Fallback, Template-Laden)
16. `pdf_temp_generator.py` -- Temperatur-PDF (Diagramm, Kalibrierscheinnummer TK_*, Pruefer-Kuerzel)
17. `pdf_vde_generator.py` -- VDE-PDF (Prueflogik, Kalibrierscheinnummer VDE_*, Pruefer-Kuerzel)

## Aktueller Status

Schritte 1-4 + 3.5 abgeschlossen.
Schritt 3.5 Feedback-Runde + Style-Migration + Responsive Layouts erledigt.
Schritt 5 (Feinschliff) offen.

### Was bereits funktioniert (Schritt 1-4 + 3.5)
- **Grundgeruest:** Frameless Window, Custom Title Bar, Collapsible Sidebar, Dark/Light Theme, Win32 Snap/Resize
- **SimplyCal-Seite:** DB-Dropdown + Auftrags-Dropdown, Waagentabelle mit Icon-Buttons
- **Tabelle:** Icon-Buttons (Thermometer/Meter) statt Doppelklick, rot/gruen je nach PDF-Status
- **Overlay:** DimmOverlay mit Click-Outside-to-Close, Fade+Slide Animation (150ms)
- **Temp-Detail-Seite:** Formular mit allen Feldern vorausgefuellt (Standard-Temps aus Settings), PDF-Generierung im QThread mit Spinner, gruenes Doc-Icon, Fehlermeldungen
- **VDE-Detail-Seite:** 3-Seiten-Wizard (Grundeinstellungen/Sichtpruefung/Messwerte), Stepper-Navigation, VDE 701/702, Schutzklasse I/II/III, 13 Toggle-Sichtpruefungspunkte, dynamische Messwerte nach Schutzklasse, PDF-Generierung, Eingaben-Cache
- **Dialog-Komponente:** theme-konform, Fade-Animation, 4 Typen, Escape/Enter-Shortcuts
- **Live-Validierung:** Roter Rand + Inline-Fehlermeldungen, Dezimal+Datum-Validatoren
- **Settings-Overlay:** 6 Reiter (Allgemein/SimplyCal/Firma/Pruefer/Messgeraete/System), Auto-Save, Bild-Upload nach data/, Messgeraete +/- mit Name+Seriennummer, Pruefer-Kuerzel
- **UI-Zustandspersistenz:** Fensterposition/-groesse, Maximiert, Sidebar, aktive Seite, letzter Auftrag, Theme

### Was als naechstes ansteht
- **Schritt 5** Feinschliff (Ersteinrichtung, Info-Seite, Animationen, Edge Cases)

Frage den Benutzer welcher Schritt als naechstes bearbeitet werden soll.

### Style-Regeln (VERBINDLICH -- siehe auch CLAUDE.md)
- **Kein `setStyleSheet()` in UI-Dateien.** Alle Styles gehoeren in `ui/styles.py`.
- **Dynamische Zustaende** ueber Qt Properties loesen: `widget.setProperty("zustand", "aktiv")` + `unpolish()/polish()`. Die passenden Selektoren (`[zustand="aktiv"]` etc.) muessen in `styles.py` definiert sein.
- **Farb-Dicts** (`FARBEN_DARK`/`FARBEN_LIGHT`) duerfen in UI-Dateien nur fuer Icons, QPainter, QColor importiert werden -- **nie fuer `setStyleSheet()`**.
- **Neue Widgets** brauchen einen ObjectName und passende Styles in `styles.py`.
- **Alle UI-Dateien sind vollstaendig migriert** (0 inline setStyleSheet in detail_vde_seite.py, detail_temp_seite.py und overlay_dialog.py).

### Wichtige technische Hinweise
- **Python-Pfad:** `C:/Users/Locha/AppData/Local/Programs/Python/Python313/python.exe` (hat PySide6)
- **QVariant-Bug:** Niemals komplexe Python-Objekte (Tuples) in QTableWidgetItem.setData() speichern -- stattdessen Lookup-Dict verwenden
- **None aus DB:** Die DB-Subqueries fuer Aufheizzyklus/TempHerstellertoleranz koennen NULL liefern -- vor Uebergabe an PDF-Generatoren mit `str(v) if v is not None else ''` bereinigen
- **Stylesheet-Kaskade:** Keine inline-setStyleSheet() auf Widgets mit Tooltip -- bricht die globale QToolTip-Vererbung. Stattdessen ObjectName verwenden und im globalen Stylesheet definieren
- **Tooltip-Styling:** Muss auf QApplication-Ebene gesetzt werden (in _wende_theme_an), da reparented Widgets (Detail-Seiten im Overlay) sonst das Fenster-Stylesheet nicht erben
- **Multi-Instanz-Settings:** set_setting() liest die INI-Datei vor jedem Schreiben neu ein, damit Aenderungen anderer Settings-Instanzen nicht ueberschrieben werden
- **Bilder-Pfade:** Zuerst in data/ suchen, dann Fallback auf Arbeitsverzeichnis (Rueckwaertskompatibilitaet)
- **PDF-Fusszeile:** Land, Telefon, Webseite sind Template-Variablen ($land, $telefon, $webseite) aus settings.ini Sektion FIRMA
