# Workflow-Profil WJPruefpilot

## Art
Windows-Desktop-App (Python 3.13, PySide6, PyInstaller-EXE) für Waagen-Jöhnk KG; verarbeitet Kunden- und Gerätedaten aus SimplyCal, Firmendaten, Unterschrift und Stempel; Auto-Updater lädt Releases über die GitHub-API. Repo `Mox2k/WJPruefpilot2` ist öffentlich.

## Befehle
`docs/projekt-roadmap.md` Abschnitt 2, Tabelle „Befehle“ (Start, Build). Python immer über `C:/Users/Locha/AppData/Local/Programs/Python/Python313/python.exe` (hat PySide6), nicht über das `venv/` im Projekt.

Tests: Es gibt keine automatische Testsuite; der User testet von Hand mit einer Beispiel-SimplyCal-DB in einem Testordner. Bis eine Suite aufgebaut ist, gilt als Prüfung: App startet ohne Fehler, betroffene Logik per kurzem Python-Aufruf geprüft und – wo eine Beispiel-DB erreichbar ist – ein Protokoll-PDF erzeugt. Was sich so nicht prüfen lässt, im Bericht als „ohne automatische Verifikation“ melden.

## Rechenlast
direkt

## Projektregeln für Code-Agents
- SimplyCal-Datenbank nur lesend öffnen, nie hineinschreiben – sie gehört der Firmensoftware (Häfner Gewichte GmbH).
- SimplyCal-Schema kann sich mit Updates ändern: Queries in `external_db.py` mit robuster Fehlerbehandlung; Unterabfragen (Aufheizzyklus, TempHerstellertoleranz) liefern auch NULL – vor Übergabe an PDF-Generatoren mit `str(v) if v is not None else ''` bereinigen.
- PyInstaller `--onefile`: jeder zur Laufzeit geladene Pfad über `sys._MEIPASS`; neue Laufzeitdateien in `hook-combined.py` und in die `--add-data`-Angaben von `.github/workflows/build.yml` eintragen, sonst fehlen sie in der EXE.
- Einstellungen nur über `Settings.set_setting()` schreiben (liest die INI vor jedem Schreiben neu), nie `config.set()` + `write()` direkt – mehrere Settings-Instanzen laufen parallel und überschreiben sich sonst.
- Styles nur in `ui/styles.py`, Zustände über Qt-Properties, Icons nur Remix Icon (`ri.*`) – Details und Werte in `docs/design-guide.md`.
- Fehler nie still verschlucken: Meldung über `OverlayDialog` (`ui/overlay_dialog.py`), Formularfelder mit Live-Validierung (roter Rand, Inline-Text) – der Techniker im Außendienst muss sofort sehen, was schiefging.
- Keine `TODO`- oder `pass`-Platzhalter; was gebaut wird, ist in sich fertig. Bewusste Vereinfachungen nur als `ponytail:`-Kommentar.
- Keine komplexen Python-Objekte (Tupel) in `QTableWidgetItem.setData()` – Qt-QVariant-Fehler; stattdessen Lookup-Dict.
- Tooltip-Styling auf QApplication-Ebene setzen (`_wende_theme_an`), sonst erben umgehängte Detail-Seiten im Overlay das Fenster-Stylesheet nicht.
- Persönliche Dateien (Unterschrift, Stempel, Logo, `settings.ini`, `data/`) und `docs/specs/` nie committen – das Repo ist öffentlich.
- Version in `version.py` nach SemVer: PATCH Bugfix, MINOR Feature, MAJOR neue Oberfläche; neue Abhängigkeiten mit fester Version in `requirements.txt`.

## Abnahme-Referenzen
- UI → `docs/design-guide.md` (Raster, Margins, Typografie, Komponenten, Icon-Regeln) und die Spec; nennt die Spec einen eigenen Entwurf, geht der vor.
- PDF-Protokolle → bestehende Vorlagen in `templates/` und das aus ihnen erzeugte PDF; Aufbau, Felder und Fußzeile bleiben gleich, außer die Spec ändert sie ausdrücklich.

## Security
an – Kunden- und Firmendaten, Unterschrift/Stempel in PDFs, Netzzugriff durch den Auto-Updater und geplante Anbindungen (WJ-Plattform, SimplyCal-Sync), öffentliches Repo.

## Rückfragen
Aufräumen: ohne Rückfrage
Merge bei unsauberem main-Worktree: ja
Spec-Widersprüche und Lösungswege: selbst entscheiden (im Bericht nennen); nur Fragen zu Produkt und Gestaltung an den Auftraggeber

## Leistungsmessung
aus

## Orchestrierung
Höchstzahl paralleler Sessions: nach Kontingent, nicht fest
Freigabe selbst erteilen: ja, wenn die Repo-Prüfung passt; bei Unsicherheit den User fragen
Nach Abschluss: „✓ “ vor den Titel, `master` nach GitHub pushen (vorher `origin` holen), Session archivieren, Worktree aufräumen. Ein Push auf `master` löst keine Auslieferung aus; das tut nur ein Tag `v*` (Release-Build) – Release-Tags nur auf Zuruf des Users.
Kontingent: nach dem 5-Stunden-Limit steuern, falls das Konto eins hat (`get_usage`); gibt es keins, nicht darauf achten.
