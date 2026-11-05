# WJPruefpilot

> Projekt, Struktur und Befehle. Geplantes – Vorhaben, Status, Bereiche, Meilensteine, offene Themen, Abnahme – steht in der Projektzentrale (Link im Profil, Abschnitt „Zentrale“), nicht hier.
> Pflege: `/projekt-setup` legt die Datei an; `/implement` (grüner Lauf) und `/shutdown` ziehen „Projektstruktur“ nach, wenn sich Struktur, Befehle oder Stack belegbar geändert haben; der Mensch jederzeit alles. Keine Lauf-Historie (die steht in `docs/implement-log.md`).

## Projekt

**Kurzbeschreibung:** Windows-Desktop-App für Temperatur- und VDE-Prüfprotokolle aus SimplyCal-Daten, für die Außendienst-Techniker von Waagen-Jöhnk KG.

**Vision:**

**Ziele:**

## Projektstruktur

_Wo der Code liegt und wie er läuft – kurz, eine Zeile je Sache._

**Stack:** Python 3.13 · PySide6 (Frameless, Dark/Light) · xhtml2pdf + reportlab (Barcode) · matplotlib · Pillow · qtawesome (Remix Icon) · SQLite read-only (SimplyCal) · configparser (`settings.ini`) · PyInstaller `--onefile --windowed` · GitHub Actions · nur Windows

**Befehle:**

_Spalte „Läuft in der Cloud“ nach Stack und Profil eingetragen, nicht ausprobiert (ungeprüft)._

| Zweck | Befehl | Läuft in der Cloud |
| --- | --- | --- |
| Installieren | `…/Python313/python.exe -m pip install -r requirements.txt` | ja (ungeprüft) |
| Start (dev) | `C:/Users/Locha/AppData/Local/Programs/Python/Python313/python.exe main.py` | nein: Windows-Desktop-GUI (PySide6, Win32) (ungeprüft) |
| Build (lokal) | `…/Python313/python.exe -m PyInstaller --name=WJPruefpilot --windowed --onefile --icon=assets/icons/wjpruefpilot.ico --additional-hooks-dir=. --collect-all reportlab.graphics.barcode --add-data "templates;templates" --add-data "assets;assets" main.py` | nein: Windows-EXE, nur unter Windows (ungeprüft) |
| Release | Tag `v*` pushen → `.github/workflows/build.yml` baut EXE und legt GitHub-Release an | nein: Release-Tags nur auf Zuruf des Users (ungeprüft) |
| Tests | keine automatischen (manuell mit Beispiel-DB) | nein: Beispiel-SimplyCal-DB liegt lokal (ungeprüft) |
| Linter | keiner | – |

**Verzeichnisse:**
- `main.py` Einstieg (QApplication, Inter-Schrift) · `version.py` zentrale Version
- `ui/` – `main_window.py` (Frameless, Win32 Snap/Resize, Zustandspersistenz), `title_bar.py`, `sidebar.py`, `auftraege_seite.py` (SimplyCal-DB, Aufträge, Waagentabelle), `detail_basis.py` (Basis der Detailseiten), `detail_temp_seite.py`, `detail_vde_seite.py` (3-Seiten-Wizard), `info_seite.py`, `overlay_dialog.py`, `settings_overlay.py` (6 Reiter, Auto-Save), `styles.py` (FARBEN_DARK/LIGHT + Stylesheets), `widgets.py`
- `pdf_base_generator.py` → `pdf_temp_generator.py`, `pdf_vde_generator.py`; `templates/` (`string.Template` mit `$platzhalter`)
- `settings.py`, `external_db.py` (SimplyCal), `internal_db.py` (Platzhalter), `updater.py` (GitHub-API, Batch-Self-Replace), `hook-combined.py` (PyInstaller-Hook), `logger.py`
- `assets/` (fonts, icons, images) · `data/` (kopierte Bilder, lokal) · Benutzerdaten gepackt in `%APPDATA%\WJPruefpilot\`
- `docs/design-guide.md` (UI-Design), `docs/features.md` (Feature-Sammlung, abgelehnte Features), `docs/specs/` (intern, nicht im Repo)

**Einstiegspunkte:** `main.py`; zum Einlesen `ui/main_window.py`, `ui/auftraege_seite.py`, `ui/detail_temp_seite.py`, `ui/detail_vde_seite.py`, `ui/settings_overlay.py`, `settings.py`, `ui/styles.py`.

**Architektur:**
- SimplyCal-DB: vom Techniker lokal abgelegt, nur lesend, Spalten `kdw_*`, `adr_*`, `auf_*`; Schema kann sich mit SimplyCal-Updates ändern.
- PDF: gemeinsame Logik (Bilder als Base64, Waagendaten, Prüfdatum) in `PDFGeneratorBase`; Kalibrierscheinnummer `TK_[Kürzel]_[MMJJ]_[WJ-Nr]` bzw. `VDE_[Kürzel]_[MMJJ]_[WJ-Nr]`; Fußzeile aus `settings.ini` Sektion FIRMA.
- Einstellungen: alles in `settings.ini`; Bilder nach `data/` kopiert, Auflösung erst `data/`, dann Arbeitsverzeichnis; mehrere Settings-Instanzen parallel, daher INI vor jedem Schreiben neu lesen; Fensterzustand wird beim Schließen gespeichert.

**Geplante Architektur (WJ-Plattform, Entscheidung 2026-03-31):** PocketBase (self-hosted) + Next.js/shadcn-Dashboard; nächtlicher One-way-Sync-Skript vom Windows-Firmenserver; Odoo-Abfrage direkt aus WJPruefpilot; Berechnungen lokal, nur fertige Datensätze nach PocketBase. Ersetzt FastAPI + MariaDB. Details: `docs/specs/2026-03-31-wj-plattform-spec.md`.
Rahmen (verifiziert 2026-03-25): 2–3 Techniker gleichzeitig; Prüfgewichte nur Büro/Labor, immer online; Temperaturkalibrierung bleibt direkt auf SimplyCal/SQLite; Referenzgewichte ändern sich selten (nächtlicher Sync reicht); SimplyCal läuft auf MS SQL Server im LAN; Odoo 19 im Einsatz.
