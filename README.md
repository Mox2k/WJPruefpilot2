
## WJPruefpilot

**Optimierung von Kalibrierungs- und Pruefprozessen fuer Waegeeinrichtungen**

WJPruefpilot ist eine Desktop-Anwendung fuer Waagen-Joehnk KG, die Temperaturkalibrierungs- und VDE-Pruefprotokolle als PDF erstellt. Die App liest Geraetedaten aus der externen SimplyCal-SQLite-Datenbank (Haefner Gewichte GmbH).

Zielgruppe: Techniker im Aussendienst, die waehrend der Kalibrierung von Waagen gleichzeitig Pruefprotokolle erstellen.

### Tech-Stack

- **GUI:** PySide6 (Frameless Window, Custom Title Bar, Dark/Light Theme)
- **PDF:** xhtml2pdf (HTML-Templates)
- **Diagramme:** matplotlib
- **Datenbank:** SQLite (read-only, SimplyCal)
- **Build:** GitHub Actions + PyInstaller (Windows .exe)
- **Plattform:** Ausschliesslich Windows

### Hauptfunktionen

- **Temperaturkalibrierungsprotokolle:** Formular mit Live-Validierung, PDF-Generierung im Hintergrund
- **VDE-Pruefprotokolle:** Optimierte Erstellung von VDE-konformer Pruefdokumentation
- **SimplyCal-Integration:** Nahtlose Verbindung mit SQLite-Datenbank, Auftrags- und Waagenverwaltung
- **Einstellungen:** Firmendaten, Pruefer, Messgeraete, Protokollpfade -- alles ueber Settings-Overlay konfigurierbar
- **Dark/Light Theme:** Umschaltbar per Toggle in der Title Bar

### Coming soon

- Auto-Update-Mechanismus (Ein-Klick-Update fuer Techniker)
- Pruefgewichte-Kalibrierung (interne DB)
- Zaehlwaagenpruefung & Stueckstreuung
- VDE-Erweiterungen (Drucker, weitere angeschlossene Geraete)
- Ergebnisse vorheriger Pruefungen

### Support

Bei Fragen oder Unterstuetzungswuenschen wenden Sie sich bitte direkt an den Entwickler.

lennart.joehnk@gmail.com
