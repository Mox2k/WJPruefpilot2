# Projekt-Roadmap

Langfristige Sicht auf WJPruefpilot. Hier steht nur das grosse Bild — was
erledigt ist, was gerade laeuft, was als naechstes kommt, und was grob
geplant ist. Detail-Spezifikationen und Brainstormings liegen separat
unter `docs/specs/` bzw. `docs/features.md`.

## 0 Pflegeregeln

_Diese Regeln gelten für jede Session, die in diese Datei schreibt. Sie bleiben dauerhaft hier stehen._

1. **Status steht nur in Abschnitt 4.** Kein anderer Abschnitt trifft eine Statusaussage.
2. **Genau vier Statuswerte, wörtlich:** `Idee`, `Spec läuft`, `Spec fertig`, `Gebaut`.
3. **Jedes Vorhaben hat genau eine Zeile in Abschnitt 4.** Die nächste freie Nummer ergibt sich aus dieser Tabelle.
4. **Bereiche (Abschnitt 3) legt nur der Mensch an.** Passt kein Bereich, wird `—` eingetragen und gemeldet.
5. **Überholtes wird ersetzt, nicht überlagert** – keine Durchstreichungen, keine „überholt“-Vermerke.
6. **Keine Lauf-Historie und keine Bestandszahlen.** Wer wann was gebaut hat, steht in `docs/superpowers/implement-log.md`.
7. **Nur die Zellen ändern, die die eigene Operation vorsieht.** Ist die Zuordnung unklar, eine neue Zeile anlegen und melden.

**Wer schreibt was:**

| Wer | Wann | Was |
| --- | ---- | --- |
| `/prime` | einmal beim Projektstart | Abschnitte 1, 2, 3, 5 befüllen |
| `/brainstorm` | Start / Abschluss | Zeile in Abschnitt 4 auf `Spec läuft` (oder neu anlegen) / auf `Spec fertig` mit Spec-Pfad |
| `/implement` | Abschluss, nur grün | Status `Gebaut`; Abschnitt 2 bei belegbaren Struktur- oder Befehlsänderungen |
| `/orchestrate` | – | schreibt nichts, meldet Abweichungen |
| Mensch | jederzeit | alles |

## 1 Projekt

**Kurzbeschreibung:** Windows-Desktop-App für Temperatur- und VDE-Prüfprotokolle aus SimplyCal-Daten, für die Außendienst-Techniker von Waagen-Jöhnk KG.

## 2 Projektstruktur

**Stack:** Python 3.13 · PySide6 (Frameless, Dark/Light) · xhtml2pdf + reportlab (Barcode) · matplotlib · Pillow · qtawesome (Remix Icon) · SQLite read-only (SimplyCal) · configparser (`settings.ini`) · PyInstaller `--onefile --windowed` · GitHub Actions · nur Windows

**Verzeichnisse:**
- `main.py` Einstieg (QApplication, Inter-Schrift) · `version.py` zentrale Version
- `ui/` – `main_window.py` (Frameless, Win32 Snap/Resize, Zustandspersistenz), `title_bar.py`, `sidebar.py`, `auftraege_seite.py` (SimplyCal-DB, Aufträge, Waagentabelle), `detail_basis.py` (Basis der Detailseiten), `detail_temp_seite.py`, `detail_vde_seite.py` (3-Seiten-Wizard), `info_seite.py`, `overlay_dialog.py`, `settings_overlay.py` (6 Reiter, Auto-Save), `styles.py` (FARBEN_DARK/LIGHT + Stylesheets), `widgets.py`
- `pdf_base_generator.py` → `pdf_temp_generator.py`, `pdf_vde_generator.py`; `templates/` (`string.Template` mit `$platzhalter`)
- `settings.py`, `external_db.py` (SimplyCal), `internal_db.py` (Platzhalter), `updater.py` (GitHub-API, Batch-Self-Replace), `hook-combined.py` (PyInstaller-Hook), `logger.py`
- `assets/` (fonts, icons, images) · `data/` (kopierte Bilder, lokal) · Benutzerdaten gepackt in `%APPDATA%\WJPruefpilot\`

**Befehle:**

| Zweck | Befehl |
| ----- | ------ |
| Start (dev) | `C:/Users/Locha/AppData/Local/Programs/Python/Python313/python.exe main.py` |
| Build (lokal) | `…/Python313/python.exe -m PyInstaller --name=WJPruefpilot --windowed --onefile --icon=assets/icons/wjpruefpilot.ico --additional-hooks-dir=. --collect-all reportlab.graphics.barcode --add-data "templates;templates" --add-data "assets;assets" main.py` |
| Release | Tag `v*` pushen → `.github/workflows/build.yml` baut EXE und legt GitHub-Release an |
| Tests | keine automatischen (manuell mit Beispiel-DB) |
| Linter | keiner |

**Einstiegspunkte:** `main.py`; zum Einlesen `ui/main_window.py`, `ui/auftraege_seite.py`, `ui/detail_temp_seite.py`, `ui/detail_vde_seite.py`, `ui/settings_overlay.py`, `settings.py`, `ui/styles.py`.

**Architektur:**
- SimplyCal-DB: vom Techniker lokal abgelegt, nur lesend, Spalten `kdw_*`, `adr_*`, `auf_*`; Schema kann sich mit SimplyCal-Updates ändern.
- PDF: gemeinsame Logik (Bilder als Base64, Waagendaten, Prüfdatum) in `PDFGeneratorBase`; Kalibrierscheinnummer `TK_[Kürzel]_[MMJJ]_[WJ-Nr]` bzw. `VDE_[Kürzel]_[MMJJ]_[WJ-Nr]`; Fußzeile aus `settings.ini` Sektion FIRMA.
- Einstellungen: alles in `settings.ini`; Bilder nach `data/` kopiert, Auflösung erst `data/`, dann Arbeitsverzeichnis; mehrere Settings-Instanzen parallel, daher INI vor jedem Schreiben neu lesen; Fensterzustand wird beim Schließen gespeichert.

**Geplante Architektur (WJ-Plattform, Entscheidung 2026-03-31):** PocketBase (self-hosted) + Next.js/shadcn-Dashboard; nächtlicher One-way-Sync-Skript vom Windows-Firmenserver; Odoo-Abfrage direkt aus WJPruefpilot; Berechnungen lokal, nur fertige Datensätze nach PocketBase. Ersetzt FastAPI + MariaDB. Details: `docs/specs/2026-03-31-wj-plattform-spec.md`.
Rahmen (verifiziert 2026-03-25): 2–3 Techniker gleichzeitig; Prüfgewichte nur Büro/Labor, immer online; Temperaturkalibrierung bleibt direkt auf SimplyCal/SQLite; Referenzgewichte ändern sich selten (nächtlicher Sync reicht); SimplyCal läuft auf MS SQL Server im LAN; Odoo 19 im Einsatz.
Offen: SimplyCal-Schema exportieren, Odoo-API-Zugang, ABBA-Formel und Messunsicherheitsbudget, Hetzner-VPS einrichten.

---

## Erledigt

### v2.0 — Erster stabiler Release
- Grundgeruest: PySide6-Hauptfenster (Frameless, Win32 Snap/Resize), Sidebar, Dark/Light-Theme
- Auftraege-Seite mit SimplyCal-Anbindung (Read-only SQLite), Waagentabelle, Icon-Status
- Detail-Seiten: Temperaturjustage-Formular + VDE-Wizard (3 Seiten, Stepper, Validierung)
- PDF-Generierung via xhtml2pdf (Temp + VDE), persistente Eingaben pro Waage
- Settings-Overlay (6 Reiter, Auto-Save, Bild-Upload, Messgeraete-Verwaltung)
- Build-Pipeline (GitHub Actions, Tag-Trigger) + Auto-Updater (Self-Replace via Batch)
- Benutzerdaten in `%APPDATA%\WJPruefpilot\` (nur im gepackten Zustand)

---

## In Arbeit

_derzeit keine aktive Arbeit_

---

## Als naechstes

- **Feinschliff (Schritt 5):** Info-Seite, Seitenwechsel-Animationen, Edge-Case-Behandlung
- **VDE-Wizard Benutzer-Feedback** einsammeln und einarbeiten

---

## Langfristig geplant

- **Templates auslagern:** HTML-Templates aus `templates/` in eigene Struktur oder externes Verzeichnis
- **Validierung ausbauen:** feldbezogene Live-Validierung vereinheitlichen, bessere Inline-Fehlermeldungen
- **WJ-Plattform:** Pruefgewichte-Verwaltung (PocketBase + Next.js + shadcn/ui) — loest die
  urspruenglich geplante FastAPI-+-MariaDB-Variante ab. Siehe
  `docs/specs/2026-03-31-wj-plattform-spec.md`.
- **SimplyCal-Sync:** HTTPS/API-basierte Synchronisation mit MS SQL Server im LAN (Upsert-Logik)
- **Interne DB:** Pruefgewichte-Kalibrierung, Ergebnisse vorheriger Pruefungen, letzte Pruefungsdaten
  pro Waage (ergaenzt SimplyCal-Read-only)

---

## Format-Konventionen

- **Erledigt** — stabiler Meilenstein, abgeschlossen und veroeffentlicht
- **In Arbeit** — aktuell in Bearbeitung, eine Zeile pro Thema
- **Als naechstes** — konkret priorisiert, als naechstes dran
- **Langfristig geplant** — grobes Thema, Detailplanung folgt im Brainstorming (`docs/features.md`)
  oder als Spec (`docs/specs/`)

Abgehakte Punkte wandern nach oben in "Erledigt", neue Themen kommen unten in "Langfristig"
rein und ruecken hoch, sobald sie konkret werden.
