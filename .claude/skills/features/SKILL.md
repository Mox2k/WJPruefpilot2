---
name: features
description: Feature-Planung und Brainstorming im Frage-Antwort-Stil. Liest Projektkontext automatisch, dann interaktives Gespraech ueber neue Features. Funktioniert mit jedem Projekt.
---

## Schritt 0: Projektkontext aufbauen

Bevor du mit dem Benutzer interagierst, baue dir ein vollstaendiges Bild des Projekts auf:

1. **Projektdokumentation lesen** -- Suche und lies folgende Dateien falls sie existieren:
   - `CLAUDE.md` (Projektbeschreibung, Architektur, Konventionen)
   - `docs/prime.md` (Projektstand, Fortschritt)
   - `docs/features.md` (bestehende Feature-Liste und abgelehnte Features)
   - `README.md`, `CONTRIBUTING.md` oder aehnliche Dokumentation

2. **Feature-Liste suchen** -- Falls `docs/features.md` nicht existiert, suche nach anderen Feature-/Roadmap-Dateien (z.B. `ROADMAP.md`, `TODO.md`, `docs/roadmap.md`). Falls keine existiert, erstelle spaeter `docs/features.md` beim Aktualisieren.

3. **Quellcode ueberfliegen** -- Finde die wichtigsten Dateien des Projekts automatisch:
   - Suche nach dem Einstiegspunkt (z.B. `main.py`, `app.py`, `index.ts`, `main.cpp`)
   - Lies die Projektstruktur (Ordner, Module)
   - Ueberfliege die zentralen Dateien (UI, Logik, Konfiguration, Datenbank)
   - Erkenne den Tech-Stack und die Zielgruppe

Nutze diesen Kontext um fundierte, projektspezifische Feature-Vorschlaege zu machen die zum tatsaechlichen Code und den Beduerfnissen der Benutzer passen.

---

## Schritt 1: Kategorie-Auswahl

Nach dem Einlesen des Kontexts, zeige eine kurze Uebersicht der aktuellen Feature-Anzahl (falls eine Feature-Liste existiert) und frage den Benutzer, in welcher Kategorie er Features brainstormen moechte.

Passe die Kategorien an den Projekttyp an. Beispiel-Kategorien:

- **Hauptfeatures** -- Grosse neue Funktionen
- **Usability** -- Bedienbarkeit und Workflow-Verbesserungen
- **Design & UI** -- Visuelles Erscheinungsbild und Darstellung
- **Stabilitaet & Qualitaet** -- Fehlerbehandlung, Validierung, Robustheit
- **Ausgabe & Export** -- Berichte, PDFs, Exporte, Ausgabeformate
- **Einstellungen & Konfiguration** -- Settings und Konfigurierbarkeit
- **Alles** -- Alle Kategorien gemischt

Passe die Kategorien-Beschreibungen an das konkrete Projekt an (z.B. bei einer Web-App andere Kategorien als bei einer Desktop-App). Biete die Kategorien als Optionen an.

---

## Schritt 2: Feature-Uebersicht

Zeige eine kurze Uebersicht der bereits geplanten Features in der gewaehlten Kategorie (falls eine Feature-Liste existiert).

---

## Schritt 3: Neue Ideen vorschlagen

Schlage dem Benutzer 5-10 neue Feature-Ideen vor, passend zur gewaehlten Kategorie. Basiere die Vorschlaege auf:
- Dem tatsaechlichen Code und seinen Luecken
- Der Zielgruppe und ihrem Arbeitsalltag
- Best Practices fuer den jeweiligen App-Typ

**Wichtig:** Vermeide Vorschlaege die bereits in der Feature-Liste stehen oder bereits abgelehnt wurden.

---

## Schritt 4: Features einzeln durchgehen

Stelle immer nur eine Frage zur Zeit. Fuer jedes Feature frage: "Relevant?" mit den Optionen Ja / Nein / Vielleicht spaeter.

---

## Schritt 5: Allgemeine Regeln

- **Halte es oberflaechlich** -- Gehe nicht in Details oder Implementierung. Es geht nur darum zu sammeln und zu sortieren was rein soll und was nicht.
- **Keine automatische Priorisierung** -- Priorisiere nur wenn der Benutzer explizit danach fragt.
- **Weitere Ideen** -- Wenn der Benutzer "weitere Ideen" will, generiere 10 neue Vorschlaege in der gewaehlten Kategorie. Wiederhole nie bereits vorgeschlagene oder abgelehnte Features.
- **Eigene Ideen** -- Der Benutzer kann jederzeit eigene Ideen einbringen.

---

## Schritt 6: Liste aktualisieren

Wenn der Benutzer fertig ist, aktualisiere `docs/features.md` (oder erstelle die Datei falls sie nicht existiert):
- Neue relevante Features in die passende Groessen-Kategorie einsortieren (Gross / Mittel / Klein)
- Abgelehnte Features in die "Abgelehnte Features"-Sektion
- Keine Duplikate erstellen
