# Feature-Planung WJPruefpilot

---

## Geplante Features (nach Prioritaet)

- [x] GUI-Migration: Tkinter -> PySide6 (Schritt 5 Feinschliff offen)
- [x] VDE-Wizard (3-Seiten, Schritt 3.5)
- [ ] Auto-Update-Mechanismus — Spec: `docs/specs/build-und-auto-update.md`
- [ ] Pruefgewichte-Kalibrierung (eigener Kalibrierschein) — Spec: `docs/specs/2026-03-22-pruefgewichte-kalibrierung-design.md`
- [ ] Zaehlwaagen-Kalibrierschein (Stueckstreuung)
- [ ] VDE-Erweiterungen (Drucker, angeschlossene Geraete)
- [ ] Zentrale `__version__` Variable statt hardcoded im Info-Fenster
- [ ] Ergebnisse vorheriger Pruefungen anzeigen

---

## Neue Features

### Hauptfeatures

- [ ] **Waagenliste als PDF** -- Geraeteuebersicht eines Auftrags als druckbare Liste
- [ ] **Wartungsprotokoll** -- Allgemeines Wartungs-/Serviceprotokoll fuer Waagen (Reinigung, mechanische Pruefung, Justage-Dokumentation)
- [ ] **Auftrag abschliessen** -- Auftrag als erledigt markieren wenn alle Waagen geprueft sind

---

### Ausgabe & Export

#### Mittel

- [ ] **Export-Funktionen** -- Waagenlisten als CSV/Excel exportieren

#### Klein

- [ ] **Protokoll-Ordner pro Auftrag** -- Automatisch Unterordner je Auftrag anlegen statt alle PDFs flach in einen Ordner

---

### Stabilitaet & Qualitaet

#### Mittel

- [ ] **DB-Integritaetspruefung** -- Beim Laden einer SimplyCal-DB pruefen ob erwartete Tabellen/Spalten vorhanden sind, klare Fehlermeldung statt stilles Scheitern
- [ ] **Eingabe-Validierung mit Grenzwerten** -- Eingabefelder validieren (z.B. Temperatur plausibel?), Grenzwerte konfigurierbar in den Settings mit sinnvollen Standardwerten

#### Klein

- [ ] **Doppelte WJ-Nummern erkennen** -- Warnung wenn WJ-Nummer in mehreren Auftraegen vorkommt
- [ ] **Fehlerbericht senden** -- Bei Fehler Log-Daten sammeln die der Techniker weiterleiten kann

---

### Einstellungen & Konfiguration

#### Mittel

- [ ] **Messgeraete-Kalibrierablauf** -- Kalibrierintervall pro Messgeraet in den Settings hinterlegen, Warnung wenn Nachkalibrierung faellig

#### Klein

- [ ] **Zentrale Versionsnummer** -- `__version__` Variable statt hardcoded
- [ ] **Eingaben-Persistenz ueber Programmende** -- Formulareingaben pro Waage dauerhaft speichern (JSON oder SQLite)
- [ ] **Letztes Messgeraet merken** -- Zuletzt gewaehltes Messgeraet automatisch vorauswaehlen
- [ ] **Spalten-Sortierung merken** -- Letzte Tabellen-Sortierung speichern und wiederherstellen
- [ ] **Bemerkungen-Vorlagen** -- Haeufig verwendete Bemerkungstexte als Schnellauswahl speichern
- [ ] **Changelog in der App** -- "Was ist neu"-Anzeige im Info-Bereich nach einem Update

---

### Usability

#### Mittel

- [ ] **Offline-SimplyCal-Sync** -- Aenderungen an der DB erkennen und Tabelle automatisch aktualisieren
- [ ] **Auftrags-Fortschritt** -- Status-Zusammenfassung ("5/12 Waagen geprueft"), visueller Fortschrittsbalken und Tabellen-Footer mit Gesamtanzahl

#### Klein

- [ ] **Tastaturkuerzel** -- Ctrl+P fuer PDF erstellen, Escape fuer Overlay schliessen, etc.
- [ ] **Toast-Benachrichtigungen** -- Dezente Erfolgsmeldungen ("PDF erstellt", "Settings gespeichert") statt nur Icon-Wechsel
- [ ] **Tab-Reihenfolge im Formular** -- Mit Tab logisch durch alle Felder springen
- [ ] **Eingabefelder mit Scrollrad** -- Temperaturwerte per Mausrad in 0,1-Schritten aendern
- [ ] **Tabellen-Spalten verschiebbar/ausblendbar** -- Spalten nach eigenem Bedarf anordnen
- [ ] **Schnellzugriff auf Protokoll-Ordner** -- Button um Protokoll-Ordner im Explorer zu oeffnen
- [ ] **Kontextmenue in der Tabelle** -- Rechtsklick auf Waage fuer Schnellaktionen (Temp, VDE, Protokoll-Ordner)
- [ ] **Doppelklick oeffnet Detail** -- Doppelklick auf Tabellenzeile oeffnet direkt die Temp-Detail-Seite
- [ ] **Letzte Pruefung anzeigen** -- Datum der letzten PDF-Erstellung pro Waage in der Tabelle
- [ ] **System-Tray-Icon** -- App ins System-Tray minimieren statt in die Taskleiste

---

### Design & UI

#### Mittel

- [ ] **UI-Konsistenz** -- Einheitliche Buttongroessen, abgerundete Eingabefelder, Hover-/Press-Animationen, Scrollbar-Styling, Schatten/Elevation, sichtbare Fokus-Ringe

#### Klein

- [ ] **Responsive Tabellen-Schriftgroesse** -- Schriftgroesse der Tabelle passt sich an die Fensterbreite an
- [ ] **Sticky-Header in der Tabelle** -- Tabellenkopf bleibt sichtbar beim Scrollen durch lange Waagenlisten
- [ ] **Feldgruppen visuell abgrenzen** -- Formularfelder durch dezente Karten/Rahmen in logische Gruppen unterteilen
- [ ] **Modale Dialoge mit Backdrop-Blur** -- Hintergrund leicht verschwommen statt nur abgedunkelt bei Dialogen
- [ ] **Eingabefelder mit Einheiten-Label** -- Temperaturfelder zeigen "°C" direkt im Feld an, Gewichtsfelder "kg"
- [ ] **Eingabefeld-Placeholder-Texte** -- Hilfreiche Platzhaltertexte in leeren Feldern (z.B. "21,5" bei Temperatur)
- [ ] **Tooltips in der Tabelle** -- Hover ueber Zelle zeigt den vollen Text bei abgeschnittenen Werten

---

## Abgelehnte Features

- Dashboard/Startseite
- Kundenhistorie
- Batch-PDF-Erstellung
- PDF-Vorschau
- Faelligkeits-Anzeige
- Drucken direkt aus der App
- Drag & Drop fuer Bilder
- Favoriten-Auftraege
- Letzte Aktivitaet pro Waage
- Automatische Sicherungskopie
- Protokoll-Archiv
- Auftragsnotizen
- Mehrere Pruefer-Profile
- Pruefintervall-Warnung
- Waagen-Schnellsuche (global)
- Kalibrierschein-Nummern-Uebersicht
- Bericht per E-Mail
- PDF nach Erstellung automatisch oeffnen
- Kopieren-Button fuer Kalibrierscheinnummer
- Fenster immer im Vordergrund
- Zuletzt verwendete DB hervorheben
- Bestaetigungs-Sound
- Undo bei PDF-Erstellung
- Kompakt-Modus
- Vollbild-Modus
- Automatische Ist-Temperatur-Erkennung
- Protokoll-Zaehler
- Automatischer Dateiname-Vorschlag
- Naechste Waage automatisch oeffnen
- Schnelleingabe-Modus
- Auftrags-Zusammenfassung drucken
- Waage ueberspringen
- Protokoll-Duplikat-Erkennung
- Mehrsprachige Protokolle
- Offline-Modus-Indikator
- Waagen-Foto auf Protokoll
- Signatur-Pad
- PDF-Zusammenfassung
- Waagen manuell hinzufuegen
- Auftrags-Filter
- Multi-Monitor-Wiederherstellung
- Kalibrierschein-Kopie
- Techniker-Zeiterfassung
- Settings-Backup
- Barcode/QR-Scanner
- Temperatur-Trendanzeige
- PDF-Dateiname mit Kundenname
- Pruefbericht-Vorlagen
- Netzlaufwerk-Kompatibilitaet
- App-Log-Datei
- Waagen-Detailansicht
- Kunden-Unterschrift auf Protokoll
- Checkliste vor PDF-Erstellung
- Theme nach Zeitplan
- Pruefsiegel-Druck
- Tablet-Modus
- Waagen-Sortierung nach Raum-Reihenfolge
- Automatischer SimplyCal-DB-Download
- Eingaben aus letzter Pruefung vorbelegen
- Datum-Picker
- Automatische Komma/Punkt-Konvertierung
- Splash Screen
- Waagen-Anzahl als Badge
- Session-Wiederherstellung
- PDF-Dateigroesse optimieren
- Mehrere Detail-Seiten gleichzeitig
- Fortschritts-Detail bei PDF
- Farbige Zeilen-Markierung in der Tabelle
- Animierte Seitenwechsel
- Sidebar-Badges
- Akzentfarbe konfigurierbar
- Breadcrumb-Navigation
- Tabellenzeilen-Hover-Aktionen
- Leere-Zustaende gestalten
- Kompakte Sidebar-Icons
- Formular-Sektionen einklappbar
- Fenster-Ecken abrunden
- Ladeanimation beim DB-Wechsel
- Farbige Status-Dots
- Sidebar-Trennlinien
- Icon-Set modernisieren
- Detail-Seite als Slide-In Panel
- Dark/Light Theme Vorschau
- Animierter Theme-Wechsel
- Mini-Map in langen Formularen
- Responsive Sidebar-Breakpoint
- Tabellen-Zebra-Streifen
- Schriftgroesse global einstellbar
- Statistik-Export
- QR-Code auf Protokoll
- Ersteinrichtungs-Assistent
- Waagen nach Standort gruppieren
- Hochkontrast-Modus
