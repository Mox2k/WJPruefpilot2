# WJPruefpilot Fortschritt

---

> Erledigte Teilaufgaben mit `[x]` markieren, offene mit `[ ]`.

---

## Fortschritt

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

### Schritt 2: Auftraege-Seite
- [x] Auftrags-Dropdown (aus SimplyCal-DB)
- [x] Modernisierte Waagentabelle mit Hover-Effekten und Sortierung
- [x] Status-Spalte (Temp/VDE erledigt basierend auf PDF-Existenz)
- [x] Doppelklick navigiert zur Detailansicht

### Schritt 3: Detail-Seiten (Temp + VDE) als Overlay

#### 3.1 Tabelle umbauen
- [x] Doppelklick-Funktion entfernen
- [x] Status-Spalten durch klickbare Icon-Buttons ersetzen (Temp: `ri.thermometer-line`/`ri.thermometer-fill`, VDE: `ri.flashlight-line`/`ri.flashlight-fill`)
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
- [x] Unten: PDF-erstellen-Button (primaryButton, rot) mit `ri.printer-line`-Icon
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
- [x] 13 Pruefpunkte als Toggle-Switches (`ri.checkbox-circle-line` gruen/rot)
- [x] Alle standardmaessig auf bestanden (gruen)

**Seite 3 -- Messwerte & Ergebnis:**
- [x] RPE, RISO, IPE, IB -- dynamisch je nach Schutzklasse (irrelevante ausgeblendet)
- [x] Bemerkungsfeld pro Messwert
- [x] Funktionspruefung (i.O. Toggle)
- [x] Allgemeine Bemerkungen (optional)
- [x] PDF-erstellen-Button mit `ri.printer-line`, nur auf Seite 3 sichtbar

#### 3.6 Info-Tooltips und Infoboxen
- [x] Sichtbare Info-Icons (`ri.information-line`) neben Feldern mit Tooltip
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
- [x] Spinner-Animation auf dem Button waehrend der Generierung (ri.loader-5-line, Rotation)
- [x] Ueberschreib-Dialog bei existierender Kalibrierscheinnummer (eigene Dialog-Komponente)
- [x] Erfolgs-Feedback: gruenes `ri.file-text-line`-Icon erscheint neben PDF-Button
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
- [x] Reset aller gespeicherten Eingaben bei Auftragswechsel im Dropdown

#### 3.11 Responsive Verhalten
- [x] Zweispaltig -> einspaltig bei kleinem Fenster (Schwelle 600px)
- [x] Sinnvolle Mindestgroesse fuer Laptop-Displays (800x500 bereits gesetzt)

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

### Schritt 5: Feinschliff
- [ ] Ersteinrichtungs-Flow (bei fehlendem settings.ini)
- [ ] Info-Seite
- [ ] Animationen (Sidebar auf/zu, Seitenwechsel)
- [ ] Edge Cases und Fehlermeldungen

### Build & Auto-Update
- Spec: [`docs/specs/build-und-auto-update.md`](specs/build-und-auto-update.md)

