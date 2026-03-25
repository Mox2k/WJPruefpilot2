# WJPruefpilot

## Projektbeschreibung

WJPruefpilot ist eine Python/PySide6 Desktop-Anwendung fuer Waagen-Joehnk KG.
Sie erstellt Temperaturkalibrierungs- und VDE-Pruefprotokolle als PDF und liest
Geraetedaten aus der externen SimplyCal-SQLite-Datenbank (Haefner Gewichte GmbH).

Zielgruppe: Techniker im Aussendienst, die waehrend der Kalibrierung von Waagen
gleichzeitig Pruefprotokolle erstellen.

## Tech-Stack

- **Sprache:** Python (bei Bedarf auf neueste Version upgraden)
- **GUI:** PySide6
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
version.py               # Zentrale Versionsnummer (__version__, Semantic Versioning)
ui/
  __init__.py
  main_window.py         # Hauptfenster (Frameless, Sidebar, Content, Win32 Snap/Resize)
  title_bar.py           # Custom Title Bar (Toggle, Theme-Switch, Window Controls)
  sidebar.py             # Collapsible Sidebar (WJ-Logo, Navigation)
  auftraege_seite.py     # SimplyCal-Seite (DB-Dropdown, Auftrags-Dropdown, Waagentabelle, Icon-Buttons)
  detail_basis.py        # Gemeinsame Basisklasse fuer Detail-Seiten (Validierung, Spinner, PDF-Feedback)
  detail_temp_seite.py   # Temperaturjustage Detail-Seite (erbt von DetailBasis)
  detail_vde_seite.py    # VDE-Pruefung Detail-Seite mit 3-Seiten-Wizard (erbt von DetailBasis)
  overlay_dialog.py      # Wiederverwendbare modale Dialog-Komponente (theme-konform, 4 Typen)
  settings_overlay.py    # Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload, Messgeraete +/-)
  styles.py              # Zentrale Farben (FARBEN_DARK/FARBEN_LIGHT) + Stylesheet + Settings-Styles
  widgets.py             # Wiederverwendbare Custom-Widgets (AnimatedButton mit Scale-Feedback)
logger.py                # Logging-Helfer (setup_logger, log_info)
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
  content.md             # Migrationsplan, Fortschritts-Tracker
  prime.md               # Session-Start-Anweisungen (via /prime Skill)
  design-guide.md        # UI Design Guide (Spacing, Typografie, Komponenten) -- bei Bedarf lesen
assets/
  fonts/                 # Inter Schriftarten
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

## Verhaltensregeln (VERBINDLICH)

Alle folgenden Regeln sind verbindlich und muessen in jeder Konversation befolgt
werden. Neue Regeln koennen jederzeit aufgenommen werden und muessen dann ebenfalls
hier eingetragen werden -- dieses Dokument ist die einzige autoritative Quelle.

### Aenderungsumfang

1. **Nur das aendern, was explizit angefragt wurde.**
   Es werden ausschliesslich die Stellen im Code angefasst, die der Benutzer
   konkret benannt hat. Keine unaufgeforderten Aenderungen an unbeteiligtem Code,
   Styles, Konfigurationen oder Komponenten -- auch nicht, wenn sie "offensichtlich
   besser" waeren. Einzige Ausnahme: Stellen, die durch die Aenderung zwingend
   mit angepasst werden muessen (z.B. ein umbenannter Parameter in allen
   Aufrufstellen). Im Zweifel vorher fragen, statt eigenmaechtig "Verbesserungen"
   mitzunehmen.
   > Hintergrund: Unaufgeforderte Nebenaenderungen fuehren zu unerwarteten
   > Seiteneffekten und machen Code-Reviews unnoetig schwer.

2. **Keine Dateien loeschen ohne Rueckfrage.**
   Auch wenn eine Datei, Funktion oder Variable unused aussieht, wird sie nicht
   eigenstaendig entfernt. Erst nachfragen -- es kann sein, dass sie fuer einen
   anderen Zweck gebraucht wird oder absichtlich vorbereitet wurde.

3. **Commits nur auf ausdrueckliche Anweisung.**
   Es wird niemals eigenstaendig ein Git-Commit erstellt. Der Benutzer bestimmt
   wann und mit welcher Nachricht committed wird.

### Kommunikation

1. **Bei Fehlern erst beschreiben, nicht sofort fixen.**
   Wenn der Benutzer einen Fehler meldet, einen Screenshot zeigt oder einen Log
   schickt, wird zuerst eine Diagnose mitgeteilt: Was ist das Problem, wo liegt
   die Ursache, welche Dateien sind betroffen. Danach wird auf eine Anweisung
   gewartet. Der Benutzer entscheidet, ob und wie gefixt wird.
   > Hintergrund: Voreiliges Fixen fuehrt oft dazu, dass am eigentlichen Problem
   > vorbei gearbeitet wird oder Aenderungen entstehen, die der Benutzer so nicht
   > wollte.

2. **Keine Annahmen treffen.**
   Wenn unklar ist, was genau gemeint ist, wird nachgefragt statt geraten. Eine
   Frage zu viel ist besser als eine falsche Annahme, die zu unnoetigem Aufwand
   fuehrt. Das gilt besonders bei mehrdeutigen Begriffen, unklarem Scope oder
   wenn mehrere Loesungswege moeglich sind.

3. **Ehrlich bei Unsicherheit.**
   Wenn nicht sicher ist, ob ein Ansatz funktioniert oder eine Aussage korrekt
   ist, wird das offen gesagt. Kein "das sollte funktionieren" wenn eigentlich
   unklar ist ob es stimmt. Stattdessen: "Ich bin mir nicht sicher ob X, weil Y
   -- soll ich das pruefen?"

4. **Im Brainstorming erst Ueberblick, dann Details.**
   Beim gemeinsamen Brainstorming werden zuerst alle Ideen gesammelt und
   priorisiert. Erst wenn das grosse Bild steht, werden einzelne Features
   vertieft. Nicht bei jedem Punkt sofort in Folgefragen und Implementierungs-
   details abtauchen.
   > Hintergrund: Zu fruehes Detail-Bohren bremst den kreativen Fluss und
   > fuehrt dazu, dass das Gesamtbild verloren geht.

### Sprache und Code-Stil

1. **Deutsch im Code beibehalten.**
   Kommentare, Docstrings und Variablennamen werden auf Deutsch geschrieben, so
   wie es im gesamten Projekt bereits gehandhabt wird. Das gilt auch fuer neue
   Dateien und Funktionen.

2. **Verstaendliche Fehlermeldungen, nie stilles Scheitern.**
   Bei Fehlern wird immer eine verstaendliche Meldung an den Benutzer ausgegeben.
   Dafuer wird `OverlayDialog` (`ui/overlay_dialog.py`) verwendet. Formularfelder
   bekommen Live-Validierung mit rotem Rand und Inline-Fehlermeldungen. Ein Fehler
   darf niemals still verschluckt werden -- der Techniker im Aussendienst muss
   sofort sehen, was schiefgelaufen ist.
   > Hintergrund: Frueher wurde z.B. kein Protokoll gedruckt ohne jede
   > Fehlermeldung, wenn das Logo fehlte oder ein Komma statt Punkt eingegeben
   > wurde.

3. **Bestehenden Code verstehen vor Aenderung.**
   Bevor eine Datei geaendert wird, wird sie zuerst gelesen und verstanden. Nie
   blind Code vorschlagen, der auf Vermutungen ueber die bestehende Implementierung
   basiert. Das verhindert, dass Aenderungen bestehende Logik brechen oder
   Duplikate von bereits vorhandener Funktionalitaet entstehen.

4. **Keine Placeholder oder TODOs hinterlassen.**
   Was implementiert wird, wird vollstaendig implementiert. Kein
   `# TODO: hier noch implementieren` oder `pass`-Bloecke als Platzhalter. Wenn
   ein Feature zu gross ist, wird das vorher besprochen und in Teilschritte
   aufgeteilt -- aber jeder Teilschritt ist in sich abgeschlossen.

5. **PyInstaller-Kompatibilitaet beachten.**
   Die App wird als Windows .exe via PyInstaller (`--onefile --windowed`)
   ausgeliefert. Bei allen Dateipfaden muss `sys._MEIPASS` beruecksichtigt werden,
   damit Templates, Fonts und Assets auch im gepackten Zustand gefunden werden.
   Neue Dateien, die zur Laufzeit geladen werden, muessen im PyInstaller-Hook
   (`hook-combined.py`) eingetragen werden.

### Style-Regeln

1. **Alle Styles gehoeren in `ui/styles.py`.**
   In UI-Dateien wird kein `setStyleSheet()` aufgerufen. Jegliches Styling wird
   zentral in `styles.py` definiert. Das sorgt fuer Konsistenz und macht
   Theme-Wechsel (Dark/Light) zuverlaessig moeglich.

2. **Dynamische Zustaende ueber Qt Properties loesen.**
   Zustandsabhaengiges Styling (aktiv, inaktiv, Fehler, etc.) wird ueber Qt
   Properties und `[eigenschaft="wert"]`-Selektoren in `styles.py` gesteuert.
   Der UI-Code setzt nur die Property und triggert ein Re-Polish:
   ```python
   # In styles.py -- Selektor definieren:
   QWidget#stepperPunkt[zustand="aktiv"] { background: #3B82F6; }

   # In der UI-Datei -- Property setzen:
   widget.setProperty("zustand", "aktiv")
   widget.style().unpolish(widget)
   widget.style().polish(widget)
   ```

3. **Farb-Dicts nur fuer Nicht-Stylesheet-Zwecke.**
   `FARBEN_DARK` und `FARBEN_LIGHT` duerfen in UI-Dateien importiert werden, aber
   ausschliesslich fuer Dinge wie Icon-Einfaerbung (`qta.icon(..., color=farbe)`),
   QPainter-Operationen oder QColor-Konstruktoren. **Niemals** fuer
   `setStyleSheet()`-Aufrufe -- dafuer gibt es die zentralen Stylesheets.

4. **Neue Widgets brauchen einen ObjectName und passende Styles.**
   Jedes neue Widget bekommt einen `setObjectName("meinWidget")`-Aufruf und
   einen entsprechenden Style-Block in `styles.py`. Ohne ObjectName greift kein
   Selektor zuverlaessig.

### Icon-Regeln

1. **Nur Remix Icon (`ri.*`) verwenden.**
   Keine anderen Icon-Prefixes wie `mdi6.*`, `fa5.*` oder aehnliche. Das Projekt
   verwendet ausschliesslich Remix Icons ueber qtawesome. Icon-Referenz:
   https://remixicon.com/

2. **Outline als Standard, Filled nur fuer aktive/erledigte Zustaende.**
   Standard-Icons verwenden die `-line`-Variante (Outline). Die `-fill`-Variante
   wird nur eingesetzt, um einen aktiven oder erledigten Zustand visuell
   hervorzuheben (z.B. aktiver Navigationspunkt, abgeschlossener Schritt).
   ```python
   # Standard (inaktiv):
   qta.icon("ri.settings-line", color=farbe)
   # Aktiver Zustand:
   qta.icon("ri.settings-fill", color=farbe_aktiv)
   ```
