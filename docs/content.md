# PySide6 Migration -- Planungsdokument

---

## Arbeitsanweisung fuer neue Sessions

> **WICHTIG: Diese Sektion bei jeder neuen Session zuerst lesen.**

### So funktioniert die Arbeit ueber mehrere Sessions

1. **Zu Beginn jeder Session:**
   - Lies diese `content.md` vollstaendig, um den aktuellen Projektstand zu verstehen.
   - Pruefe den **Fortschritts-Tracker** unten -- dort steht, welcher Schritt aktuell bearbeitet wird und welche Teilaufgaben bereits erledigt sind (`[x]`) oder noch offen (`[ ]`).
   - Lies die `CLAUDE.md` fuer Projekt-Konventionen und technische Details.
   - Frage den Benutzer nicht nach Kontext, der hier bereits dokumentiert ist.

2. **Waehrend der Arbeit:**
   - Arbeite immer nur am aktuellen Schritt (siehe Fortschritts-Tracker).
   - Markiere erledigte Teilaufgaben mit `[x]` in dieser Datei.
   - Teste nach jeder Teilaufgabe, ob die App noch lauffaehig ist.
   - Bei Problemen oder Designfragen: Frage den Benutzer, statt eigene Entscheidungen zu treffen, die vom Plan abweichen.

3. **Am Ende jeder Session:**
   - Aktualisiere den Fortschritts-Tracker in dieser Datei (Checkboxen setzen, Status aktualisieren).
   - Dokumentiere unter **Session-Log**, was in dieser Session erledigt wurde und was als naechstes ansteht.
   - Falls offene Fragen oder Probleme bestehen, notiere diese unter **Offene Punkte**.

4. **Reihenfolge einhalten:**
   - Die 5 Schritte muessen in der dokumentierten Reihenfolge abgearbeitet werden.
   - Ein Schritt gilt erst als abgeschlossen, wenn alle Teilaufgaben erledigt UND der zugehoerige Test vom Benutzer bestaetigt wurde.
   - Erst nach Bestaetigung zum naechsten Schritt uebergehen.

### Aktueller Status

**Aktiver Schritt:** Schritt 5 (Feinschliff)
**Gesamtfortschritt:** 4.5 / 5 Schritte abgeschlossen

---

## Session-Log

| Session | Datum | Erledigt | Naechster Schritt |
|---------|-------|----------|-------------------|
| 1 | 2026-03-19 | Planung abgeschlossen, content.md erstellt | Schritt 1: Grundgeruest starten |
| 1b | 2026-03-19 | Grundgeruest v1 erstellt (Title Bar, Sidebar, Content), Tkinter-Dateien geloescht | Redesign: Toggle, Theme-Toggle, Flow-Farblogik, WJ-Logo in Sidebar |
| 1c | 2026-03-19 | Schritt 1 komplett: Sidebar-Icon statt Hamburger, Win32 Snap+Resize via WM_NCHITTEST, Dark/Light Theme, WJ-Logo+Text in Sidebar, Content-Schatten, Title Bar Hoehe = Sidebar-Breite, abgerundete Ecken 10px, Farbfeintuning | Schritt 2: Auftraege-Seite |
| 2 | 2026-03-19 | Schritt 2 komplett: Auftrags-Dropdown (SimplyCal-DB), Waagentabelle mit ZeilenHoverDelegate (ganze Zeile), Status-Spalten (TK/VDE PDF-Existenz), Doppelklick-Signal, Sidebar-Reiter "SimplyCal", Inter-Schriftart eingebunden (assets/fonts/, QFontDatabase), Tabellen-Farben an Hauptfenster-Schema angepasst | Schritt 3: Detail-Seite |
| 2b | 2026-03-20 | UI-Feinschliff: Title Bar schmaler (38px), Sonnen-Icon (white-balance-sunny), alle Hover-Buttons border-radius 6px, Dropdown Chevron-Icon (dreht sich), Dropdown-Popup runde Ecken + Hover, Content-Bereich 4 Ecken rund (14px) mit Margin rechts/unten, Toggle-Button symmetrisch positioniert | Schritt 3: Detail-Seite |
| 3-plan | 2026-03-20 | Schritt 3 detailliert geplant: Tabellen-Buttons statt Doppelklick, Overlay-Mechanik mit Dimm-Effekt, Temp-Seite (zweispaltig), VDE als 3-Seiten-Wizard, Toggle-Switches, Info-Tooltips, Live-Validierung, PDF-Feedback-Icon, Persistenz, wiederverwendbare Dialog-Komponente, Responsive-Verhalten | Schritt 3: Implementierung starten |
| 3a | 2026-03-20 | Schritt 3 Phase 1: Tabelle umgebaut (Icon-Buttons statt Doppelklick, ZeilenHoverDelegate malt Status-Icons), Overlay-Mechanik (DimmOverlay, Click-Outside-to-Close, Fade+Slide 150ms), Temp-Detail-Seite (Formular mit Messgeraet/Datum/Pruefpunkte/Umgebung/Bemerkungen, PDF-Generierung im QThread mit Spinner, gruenes Doc-Icon persistent via Dateisystem-Check, Fehlermeldungen in Aktionszeile), Styles erweitert (Formular-Elemente, transparente Raender, Detail-Seite), QVariant-Bug gefixt (Waagen-Lookup via Dict statt Item-Data), None-Werte aus DB bereinigt | Schritt 3: VDE-Wizard (3.5), Validierung (3.7), Dialog (3.9), restliche Teilaufgaben |
| 3b | 2026-03-21 | Schritt 3 Phase 2: Dialog-Komponente (overlay_dialog.py, theme-konform, Fade, Bestaetigung/Fehler/Warnung/Info), Live-Validierung (roter Rand formInputFehler, Inline-Fehler unter Feldern, Datum+Dezimal-Validatoren), Ueberschreib-Dialog bei existierender Kalibrierscheinnummer, Header-Tooltip (S/N, Standort, Raum, Inventar), Infobox (X-Button zum Session-Ausblenden, info-Farbe), Info-Icons neben Labels mit Tooltip, Session-Persistenz (Eingaben pro Waage gecacht, Reset bei Auftragswechsel), Responsive Layout (Pruefpunkte zweispaltig/einspaltig bei <600px), Tooltip-Styling global auf QApplication-Ebene (theme-konform), PlusJakartaSans-Font repariert (korrupte Datei ersetzt) | Schritt 3.5: VDE-Wizard oder Schritt 4: Settings |
| 4a | 2026-03-21 | Schritt 4 komplett: Settings-Overlay (settings_overlay.py) mit 6 Reitern (Allgemein/SimplyCal/Firma/Pruefer/Messgeraete/System), Tab-Navigation mit Icons+ActiveIndicator, Auto-Save (sofort bei Aenderung), Bilder nach data/-Ordner kopiert, Bild-Upload mit Thumbnail-Vorschau, Messgeraete +/- mit Name+Seriennummer, Pruefer-Kuerzel (optional, sonst auto), Standard-Temperaturen konfigurierbar, DB-Datei-Dropdown neben Auftrags-Dropdown in SimplyCal-Seite, Click-on-TitleBar schliesst Overlay (Bug-Fix), Settings zentriert im Fenster (wie Flow), Theme-Toggle bleibt in Title Bar (Sonne/Mond), settings.py erweitert (data/, theme, kuerzel, standard_temps, messgeraete_strukturiert, fenster_geometrie, sidebar_zustand, letzter_auftrag), Multi-Instanz-sicheres set_setting (INI vor Schreiben neu lesen), pdf_base_generator + pdf_temp/vde_generator Bildpfade data/-kompatibel + Pruefer-Kuerzel, UI-Zustandspersistenz (Fensterposition/-groesse, Maximiert, Sidebar, aktive Seite, letzter Auftrag, Theme) | Schritt 5: Feinschliff |
| 5-design | 2026-03-21 | Design Guide erstellt (docs/design-guide.md), Design-Werte im Code angepasst: Spacing kompakter (Settings/Auftraege 16px, Detail 20px), Input-Hoehen einheitlich 36px, Dialog-Margins symmetrisch 32/24/32/24, Gruppen-Titel 14px, Logo-Text 16px, Font-Skala auf 6 Stufen reduziert, Infobox-Margins symmetrisch, Qt-Skills installiert (qt-styling/layouts/dialogs/architecture/debugging/model-view/packaging) | Schritt 5 oder 3.5 |
| 3.5 | 2026-03-22 | Schritt 3.5 komplett: VDE-Wizard als 3-Seiten-Detail-Overlay (detail_vde_seite.py), Stepper-Navigation (3 klickbare Schritte mit Nummernkreisen+Linien), Seite 1 (VDE 701/702 RadioButtons mit Pruefungsart-Dropdown, Schutzklasse I/II/III, elektr. Daten vorausgefuellt, VDE-Messgeraet-Dropdown, Pruefdatum), Seite 2 (13 Sichtpruefungs-Toggles mdi6.toggle-switch gruen/rot, alle Standard bestanden), Seite 3 (RPE/RISO/IPE/IB dynamisch nach Schutzklasse ein-/ausgeblendet, Bemerkung pro Messwert, Funktionspruefung-Toggle, allgemeine Bemerkungen), Zurueck/Weiter/PDF-Buttons, Eingaben-Cache pro Waage (Session), Ueberschreib-Dialog bei existierendem PDF, PDF-Generierung im QThread mit Spinner, Kundennummer via auftraege_seite.get_aktuelle_kundennummer(), Live-Validierung, Theme-Support, Tabellen-Status-Update nach PDF-Erstellung | Schritt 5: Feinschliff |
| 3.5b | 2026-03-24 | VDE-Feedback-Runde: Infobox-Bug gefixt (alle 3 wurden angezeigt statt nur aktive Seite), Infobox-Session-Flag (Schliessen bleibt erhalten wie bei Temp), VDE 702 + SK II als Standard, Tooltips fuer alle Felder auf Seite 1+3, Sichtpruefung/Funktionspruefung-Toggle visueller Cache-Restore-Bug gefixt, Messgeraet-Validierung bei PDF-Erstellung, Bounds-Pruefung in _zeige_seite, Messgeraet-Fehlermeldung verschwindet nach Hinzufuegen | Inline setStyleSheet nach styles.py migrieren (detail_vde_seite.py) |
| 3.5c | 2026-03-24 | Inline setStyleSheet nach styles.py migriert (detail_vde_seite.py): Alle 12 setStyleSheet()-Aufrufe entfernt, neue ObjectNames (stepperPunkt/Label/Linie, vdeTypButton, sichtpruefungToggle, infoBoxClose), Property-Selektoren in styles.py (zustand, vde_aktiv, hat_einheit), Infobox/PDF-Feedback/Einheit-Suffix Styles zentral | Responsive Layouts |
| 5a | 2026-03-24 | Responsive Layouts: Alle setFixedWidth() auf Input-Feldern entfernt (beide Detail-Seiten), breite-Parameter aus _erstelle_validiertes_feld entfernt, Sichtpruefung-Buttons SizePolicy.Ignored (lange Texte blockieren nicht QStackedWidget-Mindestbreite), Dropdown-MinimumWidths reduziert, Messwert/Bemerkung-Zeilen Stretch-Faktoren 1:2, elek_zeile ohne Stretch (gleichmaessige Verteilung), Pruefdatum maxWidth 130px + rechtsbuendig, Content-Container Margin 6->10px, Content-Container Gradient wie Sidebar | Schritt 5: Feinschliff |
| 5b | 2026-03-24 | Inline setStyleSheet nach styles.py migriert (detail_temp_seite.py + overlay_dialog.py): 6+7 setStyleSheet()-Aufrufe entfernt, neue ObjectNames (overlayDialog, dialogBox, dialogTitel, dialogNachricht, dialogIcon), bestehende ObjectNames genutzt (infoBoxClose, infoBox, infoBoxText, formEinheitInline, pdfFeedbackBtn), hat_einheit Property statt inline padding, Dialog-Buttons nutzen globale primaryButton/secondaryButton Styles | Schritt 5: Feinschliff |

---

## Offene Punkte

- **Schritt 5** Feinschliff: Ersteinrichtungs-Flow, Info-Seite, Animationen, Edge Cases

---

## Uebersicht

Migration der WJPruefpilot-App von Tkinter zu PySide6 mit komplett neuem UI.
PDF-Generierung, DB-Zugriff und Settings-Logik bleiben unveraendert -- nur die GUI-Schicht wird ersetzt.

---

## Design-Entscheidungen

### Visueller Stil
- **Theme:** Zwei Themes (Dark/Light), umschaltbar per Toggle in der Title Bar
  - **Dark:** Blauliches modernes Anthrazit (kein reines Grau)
  - **Light:** Sehr helles Grau
- **Farblogik:** Title Bar und Sidebar haben den **gleichen Farbton** (wie bei Flow).
  Der Content-Bereich ist nur **ganz dezent heller** -- kein harter Kontrast.
- **Akzentfarbe:** `#ed1b24` (WJ-Rot) -- ausschliesslich fuer Buttons
- **Stil:** Minimalistisch, schlicht, Flat Design
- **Farben zentral:** Alle Hex-Codes in `ui/styles.py` im `FARBEN`-Dictionary,
  leicht aenderbar. Separate Dictionaries fuer Dark und Light Theme.
- **Referenzen:** Wispr Flow (Sidebar, Settings-Overlay, Farbtrennung),
  Claude App fuer Windows (collapsible Icon-Sidebar)

### Title Bar (wie Flow -- kein separater Balken)
- Frameless Window, Title Bar verschmilzt visuell mit Sidebar (gleicher Farbton)
- **Hoehe:** 38px (kompakt)
- **Links:** Sidebar-Toggle-Icon (`mdi6.dock-left`) zum Auf/Zuklappen, symmetrischer Abstand
- **Rechts:** Theme-Toggle (`mdi6.white-balance-sunny`/`mdi6.weather-night`), Minimieren, Maximieren, Schliessen
- Alle Buttons: `border-radius: 6px` (einheitliche Rundung), Icons 16x16
- Schliessen-Button einheitlich schlicht (hover zeigt Akzentfarbe)
- Drag zum Verschieben, Doppelklick zum Maximieren/Wiederherstellen
- Windows Snap Support via Win32 API (WS_THICKFRAME + WM_NCHITTEST + WM_NCCALCSIZE)
- Resize an allen Raendern und Ecken

### Sidebar (collapsible)
- Zustand wird gespeichert und beim Start wiederhergestellt
- Toggle in Title Bar klappt auf/zu
- **Oben in der Sidebar:**
  - WJ-Logomark (Asset 10.svg / Asset 9.svg je nach Theme)
  - Beim Aufklappen erscheint Text "Pruefpilot" neben dem Icon
    (Icon bleibt gleich, kein Logo-Wechsel)
- Navigations-Eintraege (darunter):
  - SimplyCal (Startseite/Hauptnavigation, ehemals "Auftraege")
  - *(Platz fuer zukuenftige Eintraege)*
- Unten:
  - Einstellungen
  - Info

### Content-Bereich
- Dezent hellerer Farbton als Sidebar/Title Bar
- **Alle 4 Ecken abgerundet** (14px Radius)
- Umgeben von Content-Container mit Margin (0 oben/links, 6px rechts/unten)
  -- Content schliesst nahtlos an Title Bar und Sidebar an, steht aber rechts/unten frei
- Dezenter Schatten (QGraphicsDropShadowEffect, offset 0/2, blur 20) zur Abhebung

### Detail-Seiten (Overlay-Mechanik)
- Detail-Seiten (Temp/VDE) erscheinen als Overlay im Content-Bereich
- **Hintergrund-Dimm:** Sidebar und Title Bar werden abgedunkelt (halbtransparentes Overlay)
- **Click-Outside-to-Close:** Klick auf abgedunkelten Bereich schliesst Detail-Seite,
  loest aber NICHT die Aktion des geklickten Elements aus (erster Klick = nur schliessen)
- **Animation:** Schneller Fade+Slide (~150ms), zuegigesDimmen -- reaktiv, nicht traege
- **Kein Zurueck-Button** -- nur Click-Outside zum Schliessen
- Sidebar bleibt unveraendert waehrend Detail-Seite offen ist

### Wiederverwendbare Dialog-Komponente
- Eigenes modales Overlay im App-Stil (nicht QMessageBox)
- Theme-konform (Dark/Light), abgerundete Ecken, App-eigene Buttons
- Global aufrufbar fuer: Bestaetigungen, Fehlermeldungen, Warnungen
- Verwendet z.B. fuer PDF-Ueberschreib-Bestätigung

### Eingabevalidierung (global)
- **Live-Validierung** beim Tippen (roter Rand bei ungueltigem Wert)
- **Inline-Fehlermeldungen** direkt unter dem jeweiligen Feld
- **Dezimaltrenner:** Komma als Anzeige (deutsches Format), Punkt wird auch akzeptiert
- **Pflichtfelder:** Alle ausser Bemerkungen
- Felder mit Standardwerten vorausgefuellt (deutsche Standardwerte, Komma-Trenner)

### Info-System (Tooltips + Infoboxen)
- **Feld-Tooltips:** Sichtbares `mdi6.information-outline`-Icon neben Labels mit Zusatzinfo
- **Seiten-Infoboxen:** Dezenter Banner pro Wizard-Seite mit allgemeiner Erklaerung
  - Einklappbar per Chevron (erfahrene Benutzer koennen dauerhaft zuklappen)
  - Stil: `info`-Farbe aus Farbschema, Icon links

### PDF-Feedback
- Nach Erstellung: gruenes `mdi6.file-document-check`-Icon neben PDF-Button
- Icon klickbar: oeffnet erstelltes PDF im Standard-PDF-Viewer
- Status-Button in Tabelle aktualisiert sich sofort (rot -> gruen, Icon wechselt)
- Bei existierender Kalibrierscheinnummer: Ueberschreib-Dialog (eigene Dialog-Komponente)

### Persistenz
- Eingaben pro Waage bleiben in der Session erhalten (Schliessen + Wiederöffnen der Detail-Seite)
- Reset aller Eingaben bei Auftragswechsel im Dropdown
- **UI-Zustand** wird beim Schliessen in settings.ini gespeichert:
  Fensterposition/-groesse, Maximiert, Sidebar, aktive Seite, letzter Auftrag, Theme

### Fenstergroesse
- Startgroesse: 1000x700px, zentriert auf Bildschirm (nur beim allerersten Start)
- Position, Groesse und Maximiert-Zustand werden beim Schliessen gespeichert
- Mindestgroesse: 800x500px
- Abgerundete Ecken: 10px Radius (via QPainterPath Mask)
- Teilweise responsive: Inhalte passen sich an Fenstergroesse an

---

## Navigationskonzept

### Single Window mit Seitennavigation
- Alles in einem Fenster, keine separaten Toplevel-Fenster mehr
- Sidebar navigiert zwischen Hauptseiten (Auftraege, Info)
- Content-Bereich wechselt je nach Auswahl

### Navigationsflow Auftraege
```
Auftraege-Seite (Tabelle)
  --> Klick auf Temp-Icon-Button in Tabelle
    --> Detail-Seite Temperaturjustage (Overlay im Content-Bereich)
  --> Klick auf VDE-Icon-Button in Tabelle
    --> Detail-Seite VDE-Pruefung (Overlay, 3-Seiten-Wizard)
  --> Klick ausserhalb Content-Bereich schliesst Detail-Seite
```

### Waagentabelle
- Modernisierte Tabelle (Flat Design, Zeilen-Hover via ZeilenHoverDelegate, Sortierung per Spaltenklick)
- Spalten: WJ-Nummer, Hersteller, Modell, S/N, Standort, Temp-Button, VDE-Button
- **Kein Doppelklick** -- stattdessen klickbare Icon-Buttons in den letzten zwei Spalten
- **Temp-Button Icons:**
  - `mdi6.thermometer-alert` (rot) -- noch kein Protokoll erstellt
  - `mdi6.thermometer-check` (gruen) -- Protokoll existiert
- **VDE-Button Icons:**
  - `mdi6.meter-electric-outline` (rot) -- noch kein Protokoll erstellt
  - `mdi6.meter-electric` (gruen) -- Protokoll existiert
- **Statusermittlung:** Pruefen ob PDF mit passender Kalibrierscheinnummer im Speicherpfad existiert (datei-basiert, keine DB noetig)
- Alle Buttons immer klickbar (auch gruene, um Protokoll erneut zu erstellen/ueberschreiben)
- Klick auf Button oeffnet entsprechende Detail-Seite als Overlay

### Einstellungen
- Oeffnen sich als **modales Overlay** ueber dem Content (wie Wispr Flow Settings)
- Zentriert im Fenster (kleiner als Content), Schliessen per Click-Outside
- Eigene Reiter-Navigation links im Overlay:
  - **Allgemein:** Protokoll-Speicherpfad
  - **SimplyCal:** Datenbank-Ordnerpfad
  - **Firma:** Firmenname, Strasse, PLZ, Ort, Land, Telefon, Webseite, Logo, Stempel (Bilder nach data/ kopiert)
  - **Pruefer:** Name, Kuerzel (optional), Unterschrift-Bild
  - **Messgeraete:** Temperatur-Messgeraete (dynamisch +/-), VDE-Messgeraete (dynamisch +/-)
  - **System:** Standard-Soll-Temperaturen, Standard-Umgebungstemperatur
- Auto-Save bei jeder Aenderung (kein Speichern-Button)

### Ersteinrichtung
- Beim ersten Start (keine settings.ini vorhanden): Gefuehrter Setup-Flow
  1. Datenbank-Pfad auswaehlen
  2. Protokoll-Speicherpfad festlegen
  3. Firmendaten eingeben

---

## Assets

```
assets/
├── icons/
│   ├── Asset 9.svg    -- WJ-Logomark (dunkel, fuer helle Hintergruende)
│   └── Asset 10.svg   -- WJ-Logomark (weiss, fuer dunkle Hintergruende / Title Bar)
└── images/
    ├── Logo-1.svg     -- Vollstaendiges Logo (dunkel)
    └── Logo-7.svg     -- Vollstaendiges Logo (weiss auf dunkel)
```

SVGs werden mit PySide6 direkt verwendet (QSvgWidget / QIcon).

---

## Migrationsplan (5 Schritte)

### Schritt 1: Grundgeruest
- [x] PySide6-Hauptfenster mit Custom Title Bar
- [x] Frameless Window mit Windows Snap Support
- [x] Collapsible Sidebar (Icons: Auftraege, Einstellungen, Info)
- [x] Leerer Content-Bereich als Platzhalter
- [x] Dunkles Farbschema
- [x] Title Bar Redesign: Toggle links, Theme-Toggle (Sonne/Mond) rechts neben Minimieren
- [x] Sidebar: WJ-Logomark oben, wird beim Aufklappen zum vollen Logo
- [x] Title Bar und Sidebar gleicher Farbton, Content dezent heller (wie Flow)
- [x] Dark Theme: Blauliches Anthrazit statt reines Grau
- [x] Light Theme: Sehr helles Grau, umschaltbar per Sonne/Mond-Toggle
- [x] Farben zentral in styles.py als separate Dark/Light Dictionaries
- **Test:** Fenster oeffnet sich, Sidebar klappt auf/zu, Title Bar funktioniert (Drag, Snap, Buttons), Groesse anpassen geht, Theme wechselt korrekt

### Schritt 2: Auftraege-Seite
- [x] Auftrags-Dropdown (aus SimplyCal-DB)
- [x] Modernisierte Waagentabelle mit Hover-Effekten und Sortierung
- [x] Status-Spalte (Temp/VDE erledigt basierend auf PDF-Existenz)
- [x] Doppelklick navigiert zur Detailansicht
- **Test:** Datenbank anbinden, Auftraege laden, Waagen anzeigen, Status pruefen

### Schritt 3: Detail-Seiten (Temp + VDE) als Overlay

#### 3.1 Tabelle umbauen
- [x] Doppelklick-Funktion entfernen
- [x] Status-Spalten durch klickbare Icon-Buttons ersetzen (Temp: `mdi6.thermometer-alert`/`mdi6.thermometer-check`, VDE: `mdi6.meter-electric-outline`/`mdi6.meter-electric`)
- [x] Buttons rot (offen) / gruen (erledigt), alle immer klickbar
- [x] Klick auf Button oeffnet entsprechende Detail-Seite
- [x] Waagen-Lookup via `_waagen_map` Dict statt QTableWidgetItem.setData (QVariant-Roundtrip-Bug vermieden)

#### 3.2 Overlay-Mechanik
- [x] Detail-Seite erscheint im Content-Bereich (DimmOverlay + Detail als Kind-Widget)
- [x] Hintergrund (Sidebar, Title Bar) wird abgedunkelt (DimmOverlay, rgba(0,0,0,100))
- [x] Klick auf abgedunkelten Bereich schliesst Detail-Seite (mousePressEvent auf Overlay, Detail akzeptiert Events um Propagation zu verhindern)
- [x] Schnelle Animation: Fade+Slide (~150ms) via QParallelAnimationGroup

#### 3.3 Detail-Seite Header
- [x] Einheitlicher Titel im `seitenTitel`-Stil (Plus Jakarta Sans, rote Unterlinie): "WJ-Nummer · Hersteller · Modell"
- [x] Tooltip bei Hover ueber Header: S/N, Hersteller, Standort, Raum, etc.

#### 3.4 Temperaturjustage-Seite
- [x] Zweispaltiges Layout (Pruefpunkte nebeneinander)
- [x] Oben: Messgeraet-Dropdown + Pruefdatum (Standard: heute)
- [x] Soll/Ist-Temperaturpaare nebeneinander (Pruefpunkt 1: 100°C, Pruefpunkt 2: 160°C)
- [x] Umgebungstemperatur (Standard: 22,0°C)
- [x] Bemerkungen (optional)
- [x] Unten: PDF-erstellen-Button (primaryButton, rot) mit `mdi6.printer-outline`-Icon
- [x] Alle Felder vorausgefuellt: Soll 100/160, Ist 100/160, Umgebung 22,0, heutiges Datum, erstes Messgeraet
- [x] Komma als Dezimaltrenner (deutsches Format), Punkt wird auch akzeptiert
- [x] None-Werte aus DB werden vor PDF-Generierung bereinigt (tuple comprehension)

#### 3.5 VDE-Pruefung als 3-Seiten-Wizard
- [x] Stepper/Fortschrittsanzeige oben (3 Punkte/Schritte)
- [x] Freie Navigation ueber Stepper-Punkte (nicht nur sequentiell)
- [x] "Weiter"/"Zurueck"-Buttons unten, PDF-Button nur auf Seite 3

**Seite 1 -- Grundeinstellungen:**
- [x] VDE 701/702 Auswahl (mit Pruefungsart bei 701: Neugeraet/Erweiterung/Instandsetzung)
- [x] Schutzklasse (I, II, III)
- [x] Elektrische Daten: Nennspannung (230V), Nennstrom, Nennleistung, Frequenz (50Hz), cos phi (1)
- [x] VDE-Messgeraet-Dropdown + Pruefdatum
- [x] Vorausgefuellt mit deutschen Standardwerten

**Seite 2 -- Sichtpruefung:**
- [x] 13 Pruefpunkte als Toggle-Switches (`mdi6.toggle-switch` gruen / `mdi6.toggle-switch-off-outline` rot)
- [x] Alle standardmaessig auf bestanden (gruen)

**Seite 3 -- Messwerte & Ergebnis:**
- [x] RPE, RISO, IPE, IB -- dynamisch je nach Schutzklasse (irrelevante ausgeblendet)
- [x] Bemerkungsfeld pro Messwert
- [x] Funktionspruefung (i.O. Toggle)
- [x] Allgemeine Bemerkungen (optional)
- [x] PDF-erstellen-Button mit `mdi6.printer-outline`, nur auf Seite 3 sichtbar

#### 3.6 Info-Tooltips und Infoboxen
- [x] Sichtbare Info-Icons (`mdi6.information-outline`) neben Feldern mit Tooltip
- [x] Einklappbare Infobox pro Wizard-Seite (allgemeine Erklaerung zum Schritt)
- [x] Infobox-Stil: dezent, `info`-Farbe, mit Icon links, Chevron zum Einklappen

#### 3.7 Eingabevalidierung
- [x] Live-Validierung beim Tippen (roter Rand bei ungueltigem Wert)
- [x] Inline-Fehlermeldungen direkt unter dem jeweiligen Feld
- [x] Komma UND Punkt als Dezimaltrenner akzeptieren, Anzeige mit Komma
- [x] Pflichtfelder: alle ausser Bemerkungen
- [x] Messgeraet leer: Inline-Fehlermeldung "Kein Messgeraet gefunden"

#### 3.8 PDF-Generierung und Feedback
- [x] Bei Klick auf PDF-Button: PDF generieren via PDFGeneratorTemp (im QThread, UI bleibt responsiv)
- [x] Spinner-Animation auf dem Button waehrend der Generierung (mdi6.circle-slice-1..8, 50ms Rotation)
- [x] Ueberschreib-Dialog bei existierender Kalibrierscheinnummer (eigene Dialog-Komponente)
- [x] Erfolgs-Feedback: gruenes `mdi6.file-document-check`-Icon erscheint neben PDF-Button
- [x] Icon klickbar: oeffnet PDF im Standard-PDF-Viewer (os.startfile)
- [x] Icon persistent: Dateisystem-Check via glob beim Oeffnen der Detail-Seite (nicht nur Session-Cache)
- [x] Status-Button in Tabelle sofort aktualisieren (rot -> gruen, Kalibrierscheinnummer wird geparst)
- [x] Fehlermeldungen in der Aktionszeile bei Validierungsfehlern oder PDF-Fehlern

#### 3.9 Wiederverwendbare Dialog-Komponente
- [x] Eigenes modales Overlay im App-Stil (theme-konform, abgerundete Ecken)
- [x] Verwendbar fuer: Bestaetigungen, Fehlermeldungen, Warnungen
- [x] Global aufrufbar (nicht nur fuer PDF-Ueberschreibung)

#### 3.10 Persistenz der Eingaben
- [x] Eingaben pro Waage in der Session speichern (Schliessen + Wiederöffnen = Daten bleiben)
- [ ] Optional: Persistenz ueber Programmende hinaus (JSON-Datei oder SQLite)
- [x] Reset aller gespeicherten Eingaben bei Auftragswechsel im Dropdown

#### 3.11 Responsive Verhalten
- [x] Zweispaltig -> einspaltig bei kleinem Fenster (Schwelle 600px)
- [x] Sinnvolle Mindestgroesse fuer Laptop-Displays (800x500 bereits gesetzt)

- **Test:** Tabellen-Buttons klicken, Overlay oeffnet/schliesst korrekt, Formulare ausfuellen, Validierung pruefen, PDFs generieren, Status aktualisiert sich, Eingaben bleiben bei Schliessen/Oeffnen erhalten, Responsive-Verhalten testen

### Schritt 4: Settings-Overlay

#### 4.1 Overlay-Grundgeruest
- [x] Modales Overlay zentriert im Fenster (kleiner als Content, wie Wispr Flow)
- [x] Dimm-Hintergrund (wie Detail-Seite)
- [x] Schliessen per Click-Outside (kein X-Button)
- [x] Klick auf Title Bar bei offenem Overlay schliesst es (Bug-Fix)
- [x] Fade-Animation (150ms)
- [x] Sidebar Settings-Button: kein aktiver Indikator (bleibt Overlay, keine Seite)

#### 4.2 Reiter-Navigation links
- [x] Vertikal mit Icons + Text (wie Flow)
- [x] Aktiver Reiter: roter Balken links + Hintergrund-Highlight (wie Sidebar)
- [x] 6 Reiter: Allgemein, SimplyCal, Firma, Pruefer, Messgeraete, System

#### 4.3 Reiter "Allgemein"
- [x] Protokoll-Speicherpfad (Textfeld + Ordner-Auswahl-Dialog)

#### 4.4 Reiter "SimplyCal"
- [x] Datenbank-Ordnerpfad (Textfeld + Ordner-Auswahl-Dialog)
- [x] DB-Dateiauswahl im SimplyCal-Content-Reiter als Dropdown neben Auftrags-Dropdown

#### 4.5 Reiter "Firma"
- [x] Firmenname, Strasse, PLZ, Ort, Land, Telefon, Webseite (Textfelder)
- [x] Land/Telefon/Webseite erscheinen in der PDF-Fusszeile (Templates: $land, $telefon, $webseite)
- [x] Logo-Upload (Thumbnail-Vorschau + "Datei waehlen"-Button, Kopie nach data/)
- [x] Stempel-Upload (gleiche Logik)

#### 4.6 Reiter "Pruefer"
- [x] Name (Textfeld)
- [x] Kuerzel (Textfeld, optional -- wenn leer, automatisch aus Name generiert)
- [x] Unterschrift-Upload (Thumbnail + "Datei waehlen", Kopie nach data/)

#### 4.7 Reiter "Messgeraete"
- [x] Abschnitt Temperatur-Messgeraete: +/- Buttons, je Eintrag Name + Seriennummer
  - Getrennte Felder in UI, intern als ein String gespeichert (z.B. "Testo 735 (S/N: 12345)")
- [x] Abschnitt VDE-Messgeraete: gleiche Logik

#### 4.8 Reiter "System"
- [x] Standard-Soll-Temperaturen (Pruefpunkt 1 + 2, Default: 100/160)
- [x] Standard-Umgebungstemperatur (Default: 22,0)

#### 4.9 Speicher-Logik
- [x] Automatisches Speichern bei jeder Aenderung (kein Speichern-Button)
- [x] Bilder werden nach data/-Ordner kopiert (portabel, sauber getrennt)
- [x] Multi-Instanz-sicher: set_setting() liest INI vor jedem Schreiben neu

#### 4.10 UI-Zustandspersistenz
- [x] Fensterposition und -groesse (wiederhergestellt beim Start)
- [x] Maximiert-Zustand
- [x] Sidebar auf-/zugeklappt
- [x] Aktive Seite (SimplyCal/Info)
- [x] Gewaehlter Auftrag (Dropdown-Auswahl bleibt nach Neustart)
- [x] Gewaehlte Datenbank (war schon vorhanden)
- [x] Theme Dark/Light (persistent via Title Bar Toggle)

- **Test:** Einstellungen aendern, automatisch gespeichert, nach Neustart noch da, Bilder korrekt geladen, Messgeraete dynamisch hinzufuegen/entfernen, Fensterzustand wiederhergestellt

### Schritt 5: Feinschliff
- [ ] Ersteinrichtungs-Flow (bei fehlendem settings.ini)
- [ ] Info-Seite
- [ ] Animationen (Sidebar auf/zu, Seitenwechsel)
- [ ] Edge Cases und Fehlermeldungen

### Build & Auto-Update
- Spec: [`docs/specs/build-und-auto-update.md`](specs/build-und-auto-update.md)

---

## Technische Hinweise

### Was sich NICHT aendert (Business-Logik)
- `settings.ini` -- Konfigurationsformat bleibt (neue Sektionen: ALLGEMEIN, FENSTER, SYSTEM)
- `external_db.py` -- DB-Zugriff bleibt
- `pdf_base_generator.py`, `pdf_temp_generator.py`, `pdf_vde_generator.py` -- PDF-Logik bleibt
- `templates/` -- HTML-Templates bleiben

### Was geloescht wurde (Tkinter-Dateien)
- `main_window.py`, `detail_window.py`, `detail_temp_window.py`,
  `detail_vde_window.py`, `settings_window.py` -- alle geloescht
- `main.py` -- ersetzt durch neuen PySide6-Einstiegspunkt

### Neue Dateistruktur (PySide6)
```
main.py                  # Einstiegspunkt (QApplication, Inter-Schriftart laden)
ui/
├── __init__.py
├── main_window.py       # Hauptfenster (Frameless, Sidebar, Content, Win32 Snap/Resize, Zustandspersistenz)
├── title_bar.py         # Custom Title Bar (Toggle, Theme-Switch, Window Controls)
├── sidebar.py           # Collapsible Sidebar (WJ-Logo, Navigation)
├── auftraege_seite.py   # SimplyCal-Seite (DB-Dropdown, Auftrags-Dropdown, Waagentabelle, Icon-Buttons)
├── detail_temp_seite.py # Temperaturjustage Detail-Seite (Schritt 3)
├── detail_vde_seite.py  # VDE-Pruefung Detail-Seite mit 3-Seiten-Wizard (geplant)
├── overlay_dialog.py    # Wiederverwendbare modale Dialog-Komponente (Schritt 3)
├── settings_overlay.py  # Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload, Messgeraete +/-)
└── styles.py            # Zentrale Farben (FARBEN_DARK/FARBEN_LIGHT) + Stylesheet + Settings-Styles
data/                    # Bilder (Logo, Stempel, Unterschrift) -- automatisch erstellt
assets/
├── fonts/
│   ├── Inter-Regular.ttf
│   ├── Inter-Medium.ttf
│   ├── Inter-SemiBold.ttf
│   └── Inter-Bold.ttf
├── icons/
│   ├── Asset 9.svg
│   └── Asset 10.svg
└── images/
    ├── Logo-1.svg
    └── Logo-7.svg
```

### Bekannte Architektur-Probleme (werden bei Migration behoben)
- GUI und Business-Logik sind eng gekoppelt (PDF-Aufruf direkt in Window-Klassen)
- Keine Eingabevalidierung
- Stille Fehler bei fehlenden Bildern/falschen Eingaben
- Jedes Fenster instanziiert Settings separat (kein Singleton)

### Icons
- **Bibliothek:** `qtawesome` mit **Remix Icon** (`ri.*`) -- https://remixicon.com/
- Skalierbare Vektor-Icons, Farbe und Groesse per Parameter steuerbar
- **Konvention:** Outline (`-line`) als Standard, Filled (`-fill`) fuer aktive/erledigte Zustaende
- Verwendete Icons:
  - `ri.survey-line` -- SimplyCal (Sidebar)
  - `ri.settings-line` -- Einstellungen (Sidebar)
  - `ri.information-line` -- Info (Sidebar) + Tooltip-Hinweise bei Feldern
  - `ri.side-bar-line` / `ri.side-bar-fill` -- Sidebar Toggle (wechselt mit Zustand)
  - `ri.search-line` -- Suchfeld-Icon
  - `ri.sun-line` -- Theme-Toggle: Light Mode
  - `ri.moon-line` -- Theme-Toggle: Dark Mode
  - `ri.thermometer-line` -- Temp-Status: offen (rot)
  - `ri.thermometer-fill` -- Temp-Status: erledigt (gruen)
  - `ri.flashlight-line` -- VDE-Status: offen (rot)
  - `ri.flashlight-fill` -- VDE-Status: erledigt (gruen)
  - `ri.printer-line` -- PDF-erstellen-Button
  - `ri.file-check-line` -- PDF-Erfolgsanzeige (gruen, klickbar)
  - `ri.checkbox-circle-line` -- Toggle bestanden (gruen)
  - `ri.close-circle-line` -- Toggle nicht bestanden (rot)
  - `ri.loader-4-line` -- Spinner (rotated)

### Schriftart
- **Inter** (Open Source, SIL OFL) -- global gesetzt via `QFontDatabase.addApplicationFont()`
- 4 Gewichte eingebunden: Regular, Medium, SemiBold, Bold
- Dateien in `assets/fonts/`, werden in `main.py` beim Start geladen
- PyInstaller-kompatibel (`sys._MEIPASS`)

### Dependencies (neu)
- `PySide6` (ersetzt `tkinter`)
- `qtawesome` (Icon-Bibliothek fuer Qt)
- `PySide6-Addons` (SVG-Support via QSvgWidget)
- PyInstaller hidden imports muessen angepasst werden
