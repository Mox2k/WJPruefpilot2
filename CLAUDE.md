# CLAUDE.md

## Projekt

*WJPruefpilot* – Windows-Desktop-App (Python, PySide6) für Waagen-Jöhnk KG: erstellt Temperaturkalibrierungs- und VDE-Prüfprotokolle als PDF und liest Gerätedaten read-only aus der SimplyCal-SQLite-Datenbank; Zielgruppe sind Techniker im Außendienst. Wo was liegt:

- `docs/projekt-roadmap.md` – Projektstruktur, Befehle (Start, Build), Architektur, Ziele, Status aller Vorhaben. Einzige Doku-Datei; ihr Abschnitt 0 regelt, wer was hineinschreibt.
- `.claude/workflow-profil.md` – was in diesem Projekt für den Workflow gilt: Prüfbefehle, Projektregeln für Code, Abnahme-Referenzen, Security, Rückfragen.
- `docs/design-guide.md` – UI-Design (Raster, Spacing, Typografie, Komponenten, Style- und Icon-Regeln); dort autoritativ.
- `docs/features.md` – Feature-Sammlung aus dem Brainstorming. `docs/specs/` – interne Specs (nicht im öffentlichen Repo, per `.gitignore` ausgeschlossen).
- `templates/` – HTML-Vorlagen der PDF-Protokolle. `.github/workflows/build.yml` – Release-Build bei Tag `v*`.

## Arbeitsweise

- **Erst lesen, dann ändern.** Annahmen über Dateien führen zu Fehlern, die erst Schritte später auffallen.
- **Nur das Gefragte.** Kein Umbau nebenbei; direkte Abhängigkeiten der Änderung dürfen mit. Fällt etwas anderes auf: sagen. Bewusste Vereinfachungen als `ponytail:`-Kommentar mit Grenze und Ausbaupfad markieren.
- **Fragen, wenn zwei Lesarten zu wirklich verschiedener Arbeit führen.** Routine und Technik, die der User nicht sieht, selbst entscheiden.
- **Freigaben.** Lokale, umkehrbare Arbeit im Auftrag einfach tun. Was nach außen wirkt oder nicht umkehrbar ist – Push, Force, Release-Tags, Löschen fremder Arbeit, Nachrichten, Schreiben in die SimplyCal-DB – nur mit Freigabe. Freigeben kann der User oder der Orchestrator, der eine Session gestartet hat (`Auftraggeber:` im Startauftrag): seine Anweisung gilt wie die des Users.
- **Bestehender Stil** von Code und Dateien gibt die Form vor. Code, Kommentare, Docstrings und Variablennamen auf Deutsch, wie im ganzen Projekt.
- **Prüfen vor Fertigmelden.** Tests, Build oder Ansicht tatsächlich laufen lassen; ohne Nachweis gilt nichts als fertig.
- Zu Beginn jeder Session die Skills `caveman` und `ponytail` in Stufe `full` laden: knapp im Chat (Dateien, Code, Commits bleiben normale Prosa), einfachste funktionierende Lösung im Code. Vorgeschriebene Tests bleiben trotzdem Pflicht.

## Workflow

Die Workflow-Skills (`/prime`, `/brainstorm`, `/orchestrate`, `/implement`, `/browser-test`, `/debugging`, `/security-check`, `/shutdown`, `/workflow-aktualisieren`) sind Konto-Skills der Claude-App – so hat sie jede Session und jeder Thread, lokal und in der Cloud. Gepflegt werden sie im Repo `Mox2k/claude-workflow`; geändert wird dort, dann neu in die App hochgeladen.

- Was nur für dieses Projekt gilt, gehört ins Profil, nicht in den Workflow.
- Projekt-eigene Skills (`features`, `qt-*`) liegen versioniert in `.claude/skills/` dieses Repos. Lokale Sessions laden sie selbst; **in einem Cloud-Thread fehlen sie** – dort bei Bedarf `.claude/skills/<name>/SKILL.md` lesen und befolgen.
- In einem Cloud-Thread laufen Programme vom Rechner des Users nicht (Windows-Python mit PySide6, SimplyCal-Beispiel-DB); Prüfungen, die sie brauchen (siehe Profil), als offen melden, nicht als bestanden.

Das Profil gilt in jeder Session, nicht nur im Workflow: @.claude/workflow-profil.md
