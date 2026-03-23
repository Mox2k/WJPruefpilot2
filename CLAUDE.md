# WJPruefpilot

## Projektbeschreibung

WJPruefpilot ist eine Python/PySide6 Desktop-Anwendung fuer Waagen-Joehnk KG.
Sie erstellt Temperaturkalibrierungs- und VDE-Pruefprotokolle als PDF und liest
Geraetedaten aus der externen SimplyCal-SQLite-Datenbank (Haefner Gewichte GmbH).

Zielgruppe: Techniker im Aussendienst, die waehrend der Kalibrierung von Waagen
gleichzeitig Pruefprotokolle erstellen.

## Tech-Stack

- **Sprache:** Python (bei Bedarf auf neueste Version upgraden)
- **GUI:** PySide6 (Migration von Tkinter abgeschlossen, Feinschliff ausstehend)
- **PDF-Generierung:** xhtml2pdf (HTML-Templates -> PDF)
- **Diagramme:** matplotlib (Temperatur-Vergleichsgrafiken)
- **Bildverarbeitung:** Pillow
- **Datenbank:** SQLite (read-only Zugriff auf externe SimplyCal-DB)
- **Konfiguration:** configparser (settings.ini)
- **Icons:** qtawesome mit Remix Icon (`ri.*`) — https://remixicon.com/
- **Build:** PyInstaller (Windows .exe, --onefile --windowed)
- **Plattform:** Ausschliesslich Windows

## Projektstruktur

```
main.py                  # Einstiegspunkt (QApplication, Inter-Schriftart laden)
ui/
  __init__.py
  main_window.py         # Hauptfenster (Frameless, Sidebar, Content, Win32 Snap/Resize)
  title_bar.py           # Custom Title Bar (Toggle, Theme-Switch, Window Controls)
  sidebar.py             # Collapsible Sidebar (WJ-Logo, Navigation)
  auftraege_seite.py     # SimplyCal-Seite (DB-Dropdown, Auftrags-Dropdown, Waagentabelle, Icon-Buttons)
  detail_temp_seite.py   # Temperaturjustage Detail-Seite (Formular, PDF im QThread, Spinner, Feedback)
  detail_vde_seite.py    # VDE-Pruefung Detail-Seite mit 3-Seiten-Wizard (geplant)
  overlay_dialog.py      # Wiederverwendbare modale Dialog-Komponente (theme-konform, 4 Typen)
  settings_overlay.py    # Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload, Messgeraete +/-)
  styles.py              # Zentrale Farben (FARBEN_DARK/FARBEN_LIGHT) + Stylesheet + Settings-Styles
pdf_base_generator.py    # Basisklasse fuer PDF-Generatoren (gemeinsame Methoden)
pdf_temp_generator.py    # PDF-Generierung fuer Temperaturprotokolle (erbt von PDFGeneratorBase)
pdf_vde_generator.py     # PDF-Generierung fuer VDE-Protokolle (erbt von PDFGeneratorBase)
templates/               # HTML-Templates fuer PDF-Generierung (string.Template mit $-Platzhaltern)
  temp_template.html     #   Temperatur-Protokoll Template
  vde_template.html      #   VDE-Protokoll Template
settings.py              # Settings-Klasse (liest/schreibt settings.ini)
external_db.py           # Read-only Zugriff auf SimplyCal-SQLite-Datenbank
internal_db.py           # Interne DB (Platzhalter fuer zukuenftige Features)
hook-combined.py         # PyInstaller Hook fuer hidden imports + Template-Dateien
settings.ini             # Konfigurationsdatei (wird zur Laufzeit erzeugt/gelesen)
docs/
  content.md             # Migrationsplan, Fortschritts-Tracker, Session-Log
  prime.md               # Session-Start-Anweisungen (via /prime Skill)
  design-guide.md        # UI Design Guide (Spacing, Typografie, Komponenten) -- bei Bedarf lesen
assets/
  fonts/                 # Inter + Plus Jakarta Sans Schriftarten
  icons/                 # WJ-Logomark SVGs (Asset 9/10)
  images/                # Vollstaendige Logo SVGs
```

## Architektur-Hinweise

### Externe Datenbank (SimplyCal)
- **Nur lesender Zugriff** -- niemals in die externe DB schreiben.
- Die DB wird vom Techniker heruntergeladen und lokal abgelegt.
- SQL-Queries verwenden spezifische SimplyCal-Spaltennamen (kdw_*, adr_*, auf_*).
- Das DB-Schema kann sich durch SimplyCal-Updates aendern -- bei Aenderungen
  an external_db.py robuste Fehlerbehandlung beruecksichtigen.

### Interne Datenbank (geplant)
- Fuer zukuenftige Features: Pruefgewichte-Kalibrierung, Ergebnisse vorheriger
  Pruefungen, letzte Pruefungsdaten pro Waage.
- Kann Kundendaten aus der externen DB ableiten, verwaltet aber eigene Daten.

### PDF-Generierung
- Verwendet xhtml2pdf mit HTML-Templates aus dem `templates/`-Ordner.
- Templates verwenden `string.Template` mit `$platzhalter`-Syntax.
- Gemeinsame Logik (Bildverarbeitung, Waagendaten, Pruefdatum) liegt in der
  Basisklasse `PDFGeneratorBase` (`pdf_base_generator.py`).
- `PDFGeneratorTemp` und `PDFGeneratorVDE` erben davon und enthalten nur
  die jeweils spezifische Logik (Diagramm-Erstellung, VDE-Prueflogik).
- Template-Pfad ist PyInstaller-kompatibel (`sys._MEIPASS` fuer --onefile).
- Bilder (Logo, Unterschrift, Stempel) werden als Base64 in die PDFs eingebettet.
- Kalibrierscheinnummern: Format `TK_[Kuerzel]_[MMJJ]_[WJ-Nummer]` (Temp)
  bzw. `VDE_[Kuerzel]_[MMJJ]_[WJ-Nummer]` (VDE).
- Fusszeile: Land, Telefon, Webseite aus settings.ini (Sektion FIRMA).

### Einstellungen
- Alles in settings.ini (configparser): Firmendaten, Pruefer, Messgeraete, Pfade,
  Fensterzustand, Theme, Standard-Temperaturen.
- Bilder werden nach `data/`-Ordner kopiert und per Dateiname referenziert.
- Bildpfad-Aufloesung: zuerst `data/`, dann Arbeitsverzeichnis (Rueckwaertskompatibel).
- Mehrere Settings-Instanzen: `set_setting()` liest INI vor jedem Schreiben neu ein,
  um Konflikte zwischen Instanzen zu vermeiden.
- Fensterzustand (Position, Groesse, Maximiert, Sidebar, aktive Seite, letzter Auftrag)
  wird beim Schliessen gespeichert und beim Start wiederhergestellt.

## Konventionen

- **Sprache im Code:** Deutsch fuer Kommentare, Docstrings und Variablennamen
  (so wie es bereits ist).
- **Versionierung:** Semantic Versioning (MAJOR.MINOR.PATCH)
  - PATCH: Bugfixes
  - MINOR: Neue Features
  - MAJOR: Neue Benutzeroberflaeche / grundlegende Aenderungen
- **Dependencies:** Via pip installieren, requirements.txt pflegen.
- **Kein Git-Repo aktuell** -- bei Aenderungen vorsichtig sein, kein Rollback moeglich.

### Style-Regeln (VERBINDLICH)
1. **Alle Styles gehoeren in `ui/styles.py`** -- kein `setStyleSheet()` in UI-Dateien.
2. **Dynamische Zustaende** ueber Qt Properties + `[eigenschaft="wert"]`-Selektoren
   in `styles.py` loesen. Beispiel:
   ```python
   # styles.py
   QWidget#stepperPunkt[zustand="aktiv"] { ... }
   # UI-Code
   widget.setProperty("zustand", "aktiv")
   widget.style().unpolish(widget)
   widget.style().polish(widget)
   ```
3. **Farb-Dicts** (`FARBEN_DARK`/`FARBEN_LIGHT`) duerfen in UI-Dateien nur fuer
   Nicht-Stylesheet-Zwecke importiert werden (Icons einfaerben, QPainter, QColor).
   **Niemals** fuer `setStyleSheet()`.
4. **Neue Widgets** brauchen einen ObjectName und passende Styles in `styles.py`.

### Icon-Regeln (VERBINDLICH)
1. **Nur Remix Icon** (`ri.*`) verwenden -- kein `mdi6.*` oder andere Prefixes.
2. **Outline als Standard** (`-line`), Filled (`-fill`) nur fuer aktive/erledigte Zustaende.
3. **Icon-Referenz:** https://remixicon.com/
4. **Beispiel:** `qta.icon("ri.settings-line", color=farbe)`

## Wichtige Hinweise fuer Aenderungen

### Validierung & Fehlerbehandlung
- Die App hat aktuell wenig Validierung. Fehlende Bilder (Logo, Unterschrift, Stempel)
  oder falsche Eingabeformate (Komma statt Punkt bei Dezimalzahlen) fuehren zu
  stillem Scheitern ohne Fehlermeldung.
- **Bei allen Aenderungen:** Sicherstellen, dass dem Benutzer verstaendliche
  Fehlermeldungen angezeigt werden, statt still zu scheitern.
- Eingabevalidierung: Dezimalzahlen sollten sowohl Punkt als auch Komma akzeptieren.

### Build
- `pyinstaller --name=WJPruefpilot --windowed --onefile --additional-hooks-dir=. main.py`
- App wird per USB-Stick oder OneDrive-Download an Techniker verteilt.

## Geplante Features / Aenderungen (nach Prioritaet)

### 1. GUI-Migration: Tkinter -> PySide6 (IN ARBEIT)
- **Status:** Schritte 1-3 abgeschlossen, Schritt 4 (Settings-Overlay) fast fertig, Schritt 5 (Feinschliff) offen
- **Details:** Siehe `docs/content.md` fuer vollstaendigen Migrationsplan und Fortschritt
- **Framework:** PySide6 (LGPL-Lizenz, offiziell von Qt Company)
- **Design:** Frameless Window, Custom Title Bar, Collapsible Sidebar, Dark/Light Theme
- PDF-Generierung, DB-Zugriff, Settings bleiben unveraendert -- nur die GUI-Schicht aendert sich

### 2. Auto-Update-Mechanismus
- Techniker sollen mit einem Klick updaten koennen statt USB/OneDrive

### 3. Pruefgewichte-Kalibrierung
- Ueber interne DB, eigener Kalibrierschein

### 4. Zaehlwaagen-Kalibrierschein
- Zaehlwaagenpruefung & Stueckstreuung

### 5. VDE-Erweiterungen
- Drucker und weitere angeschlossene Geraete bei VDE-Pruefung pruefen

### Sonstige Features (ohne feste Prioritaet)
- Zentrale `__version__` Variable statt hardcoded im Info-Fenster
- Ergebnisse vorheriger Pruefungen anzeigen
