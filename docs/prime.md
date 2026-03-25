# Prime: WJPruefpilot

Lies diese Dateien, um den Projektstand zu verstehen:

1. `docs/content.md` -- Fortschritts-Tracker (offene Checkboxen = naechste Aufgaben)
2. `docs/design-guide.md` -- UI Design Guide (Spacing, Typografie, Komponenten, Icons)
3. `ui/styles.py` -- Zentrale Farbdefinitionen (Dark/Light Theme) + Stylesheet
3. `ui/main_window.py` -- Hauptfenster (Frameless, Win32 Snap/Resize, Sidebar, Content, Overlays, Zustandspersistenz)
5. `ui/auftraege_seite.py` -- SimplyCal-Seite (DB-Anbindung, Tabelle, Signals)
6. `ui/detail_temp_seite.py` -- Temperaturjustage Detail-Seite (Formular, Validierung, PDF, Persistenz)
7. `ui/detail_vde_seite.py` -- VDE-Wizard (3-Seiten, Stepper, Messwerte, PDF)
8. `ui/settings_overlay.py` -- Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload, Messgeraete)
9. `main.py` -- Einstiegspunkt (Schriftarten, QApplication)
10. `settings.py` -- Settings-Klasse (Pfade, Firmendaten, Theme, Multi-Instanz-sicher)

`CLAUDE.md` wird automatisch geladen und muss nicht gelesen werden.

Bei Bedarf zusaetzlich lesen:
- `ui/title_bar.py`, `ui/sidebar.py`, `ui/overlay_dialog.py` -- kleine, stabile UI-Komponenten
- `external_db.py` -- SimplyCal-Datenbankzugriff (SQL-Queries)
- `pdf_base_generator.py`, `pdf_temp_generator.py`, `pdf_vde_generator.py` -- PDF-Generierung

Frage den Benutzer welcher Schritt als naechstes bearbeitet werden soll.

### Wichtige technische Hinweise
- **Python-Pfad:** `C:/Users/Locha/AppData/Local/Programs/Python/Python313/python.exe` (hat PySide6)
- **QVariant-Bug:** Niemals komplexe Python-Objekte (Tuples) in QTableWidgetItem.setData() speichern -- stattdessen Lookup-Dict verwenden
- **None aus DB:** Die DB-Subqueries fuer Aufheizzyklus/TempHerstellertoleranz koennen NULL liefern -- vor Uebergabe an PDF-Generatoren mit `str(v) if v is not None else ''` bereinigen
- **Tooltip-Styling:** Muss auf QApplication-Ebene gesetzt werden (in _wende_theme_an), da reparented Widgets (Detail-Seiten im Overlay) sonst das Fenster-Stylesheet nicht erben
