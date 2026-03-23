# Pruefgewichte-Kalibrierung: App-Integration in WJPruefpilot

> **Status:** Entwurf
> **Erstellt:** 2026-03-22
> **Autor:** Lennart (Waagen-Joehnk KG)
> **Repository:** WJPruefpilot (bestehendes Desktop-App-Repo)
> **Abhaengigkeit:** WJ-API Server (siehe `2026-03-22-wj-api-design.md`)

---

## 1. Uebersicht

Neues Modul in der WJPruefpilot Desktop-App (PySide6) fuer die Verwaltung und
Durchfuehrung von Pruefgewichte-Kalibrierungen. Komplett unabhaengig vom
bestehenden SimplyCal-Bereich -- eigener Sidebar-Eintrag, eigene Seiten,
eigene Datenkommunikation ueber die WJ-API.

### Was dieses Modul tut

1. Offene Auftraege von der WJ-API laden (die wiederum Odoo abfragt)
2. Pruefgewichtsaetze mit Einzelgewichten erfassen
3. ABBA-Messwerte und Umgebungsbedingungen eingeben
4. Kalibrierschein als PDF lokal generieren
5. Auftraege als abgeschlossen markieren

### Was dieses Modul NICHT tut

- Direkt mit Odoo kommunizieren (alles ueber die WJ-API)
- Direkt auf die MariaDB zugreifen (alles ueber die WJ-API)
- Referenzgewichte verwalten (read-only aus der API)
- SimplyCal-Daten aendern oder lesen

---

## 2. Abhaengigkeit: WJ-API

Die App kommuniziert ausschliesslich mit der WJ-API (`api.waagen-joehnk.de`).
Fuer Details zum Server, Datenmodell, Endpunkten und Authentifizierung siehe
das separate Server-Spec: `2026-03-22-wj-api-design.md`.

```
WJPruefpilot (diese Spec)
    │
    │  HTTPS + Techniker-API-Key
    │
    ▼
WJ-API (api.waagen-joehnk.de)
    ├── → MariaDB (Pruefgewichte, Messungen)
    └── → Odoo 19 (Auftraege, Kunden)
```

Die App weiss nicht und muss nicht wissen, ob die Daten aus Odoo, MariaDB
oder einer anderen Quelle kommen. Sie kennt nur die API-Endpunkte.

---

## 3. Neue Dateien im Projekt

```
WJPruefpilot/
├── api/                              # NEU: API-Kommunikation
│   ├── __init__.py
│   ├── client.py                     # PruefpilotAPI-Klasse (alle HTTP-Calls)
│   └── auth.py                       # API-Key Verwaltung (laden/speichern)
│
├── ui/
│   ├── pruefgewichte_seite.py        # NEU: Hauptseite (Karten-Grid)
│   ├── pruefgewichte_detail.py       # NEU: Detail-Overlay (Gewichte + Messungen)
│   ├── sidebar.py                    # AENDERUNG: Neuer Eintrag "Pruefgewichte"
│   ├── main_window.py               # AENDERUNG: Neue Seite einbinden
│   └── settings_overlay.py          # AENDERUNG: Neuer Reiter "Server"
│
├── pdf_pruefgewicht_generator.py     # NEU: PDF-Generierung fuer Kalibrierscheine
│
└── templates/
    └── pruefgewicht_template.html    # NEU: HTML-Template fuer Kalibrierschein
```

### Bestehende Dateien die geaendert werden

| Datei | Aenderung |
|-------|-----------|
| `ui/sidebar.py` | Neuer Button "Pruefgewichte" mit Icon `mdi6.weight` |
| `ui/main_window.py` | Neue Seite im ContentStack, Overlay-Handling fuer Detail |
| `ui/settings_overlay.py` | Neuer Reiter "Server" (API-URL + API-Key) |
| `settings.py` | Neue Settings: `api_url`, `api_key`, Getter/Setter |
| `ui/styles.py` | Styles fuer Karten-Grid und Pruefgewichte-Detail |

---

## 4. API-Client Modul

### 4.1 api/client.py

Kapselt alle HTTP-Kommunikation mit der WJ-API. Verwendet `httpx` als
HTTP-Client (modern, async-faehig, besser als `requests`).

```python
import httpx
from typing import Optional


class PruefpilotAPI:
    """Client fuer die WJ-API. Einziger Kontaktpunkt der App zum Server."""

    def __init__(self, base_url: str, api_key: str):
        self._client = httpx.Client(
            base_url=f"{base_url}/api/v1",
            headers={"X-API-Key": api_key},
            timeout=15.0
        )
        self._techniker_info = None

    # --- Auth ---

    def verify(self) -> dict:
        """Prueft den API-Key und gibt Techniker-Info zurueck.
        Wird beim App-Start aufgerufen."""
        response = self._client.post("/auth/verify")
        response.raise_for_status()
        self._techniker_info = response.json()
        return self._techniker_info

    @property
    def techniker_name(self) -> str:
        return self._techniker_info.get("name", "") if self._techniker_info else ""

    @property
    def techniker_kuerzel(self) -> str:
        return self._techniker_info.get("kuerzel", "") if self._techniker_info else ""

    # --- Auftraege ---

    def hole_auftraege(self, status: str = "offen") -> list:
        """Holt Auftraege von der API (die wiederum Odoo abfragt)."""
        response = self._client.get("/auftraege/", params={"status": status})
        response.raise_for_status()
        return response.json()["auftraege"]

    def hole_auftrag(self, auftrag_id: int) -> dict:
        """Holt einen einzelnen Auftrag mit Kundendaten."""
        response = self._client.get(f"/auftraege/{auftrag_id}")
        response.raise_for_status()
        return response.json()

    # --- Pruefgewichtsaetze ---

    def erstelle_satz(self, auftrag_id: int) -> dict:
        """Legt einen neuen Pruefgewichtsatz an."""
        response = self._client.post("/gewichtsaetze/",
                                      json={"auftrag_id": auftrag_id})
        response.raise_for_status()
        return response.json()

    def hole_satz(self, satz_id: int) -> dict:
        """Holt einen Satz mit allen Einzelgewichten und Messungen."""
        response = self._client.get(f"/gewichtsaetze/{satz_id}")
        response.raise_for_status()
        return response.json()

    def satz_abschliessen(self, satz_id: int) -> dict:
        """Schliesst einen Pruefgewichtsatz ab."""
        response = self._client.put(f"/gewichtsaetze/{satz_id}/abschliessen")
        response.raise_for_status()
        return response.json()

    # --- Einzelgewichte ---

    def gewicht_hinzufuegen(self, satz_id: int, daten: dict) -> dict:
        """Fuegt ein Einzelgewicht zum Satz hinzu."""
        response = self._client.post(
            f"/gewichtsaetze/{satz_id}/gewichte/", json=daten)
        response.raise_for_status()
        return response.json()

    def gewicht_bearbeiten(self, satz_id: int, gewicht_id: int,
                           daten: dict) -> dict:
        """Bearbeitet ein Einzelgewicht."""
        response = self._client.put(
            f"/gewichtsaetze/{satz_id}/gewichte/{gewicht_id}", json=daten)
        response.raise_for_status()
        return response.json()

    def gewicht_entfernen(self, satz_id: int, gewicht_id: int):
        """Entfernt ein Einzelgewicht aus dem Satz."""
        response = self._client.delete(
            f"/gewichtsaetze/{satz_id}/gewichte/{gewicht_id}")
        response.raise_for_status()

    # --- Messungen ---

    def messung_speichern(self, satz_id: int, gewicht_id: int,
                          daten: dict) -> dict:
        """Speichert eine ABBA-Messung fuer ein Gewicht."""
        response = self._client.post(
            f"/gewichtsaetze/{satz_id}/gewichte/{gewicht_id}/messung",
            json=daten)
        response.raise_for_status()
        return response.json()

    # --- Referenzgewichte ---

    def hole_referenzgewichte(self, nennwert: Optional[float] = None,
                               einheit: Optional[str] = None) -> list:
        """Holt verfuegbare Referenzgewichte (read-only)."""
        params = {}
        if nennwert is not None:
            params["nennwert"] = nennwert
        if einheit:
            params["einheit"] = einheit
        response = self._client.get("/referenzgewichte/", params=params)
        response.raise_for_status()
        return response.json()["referenzgewichte"]
```

### 4.2 api/auth.py

Verwaltet den API-Key und die Server-URL. Gespeichert in `settings.ini`
unter der neuen Sektion `[SERVER]`.

```python
from settings import Settings


class APIAuth:
    """Verwaltet API-Key und Server-Verbindung."""

    def __init__(self):
        self._settings = Settings("settings.ini")

    @property
    def api_url(self) -> str:
        return self._settings.get_setting('SERVER', 'api_url',
                                           'https://api.waagen-joehnk.de')

    @api_url.setter
    def api_url(self, url: str):
        self._settings.set_setting('SERVER', 'api_url', url)

    @property
    def api_key(self) -> str:
        return self._settings.get_setting('SERVER', 'api_key', '')

    @api_key.setter
    def api_key(self, key: str):
        self._settings.set_setting('SERVER', 'api_key', key)

    @property
    def ist_konfiguriert(self) -> bool:
        return bool(self.api_url and self.api_key)
```

### 4.3 Threading

Alle API-Calls laufen in einem **QThread**, damit die UI nicht blockiert.
Gleiches Muster wie bei der PDF-Generierung (PdfWorker in detail_temp_seite.py).

```python
from PySide6.QtCore import QThread, Signal


class ApiWorker(QThread):
    """Fuehrt API-Calls im Hintergrund aus."""

    fertig = Signal(bool, object)  # (erfolg, daten_oder_fehler)

    def __init__(self, api_call, *args, **kwargs):
        super().__init__()
        self._api_call = api_call
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            ergebnis = self._api_call(*self._args, **self._kwargs)
            self.fertig.emit(True, ergebnis)
        except Exception as e:
            self.fertig.emit(False, str(e))
```

**Verwendung in der UI:**
```python
def _lade_auftraege(self):
    self._starte_spinner()
    self._worker = ApiWorker(self._api.hole_auftraege)
    self._worker.fertig.connect(self._auftraege_geladen)
    self._worker.start()

def _auftraege_geladen(self, erfolg, daten):
    self._stoppe_spinner()
    if erfolg:
        self._zeige_auftrags_karten(daten)
    else:
        self._zeige_fehler(f"Auftraege konnten nicht geladen werden: {daten}")
```

---

## 5. UI-Design

### 5.1 Sidebar-Erweiterung

Neuer Button in der Sidebar zwischen "SimplyCal" und dem Spacer:

```
Sidebar
  ├── [WJ-Logo]
  ├── SimplyCal          (bestehend, Index 0)
  ├── Prüfgewichte       ◄── NEU (Index 1)
  ├── ──── Spacer ────
  ├── Einstellungen      (bestehend)
  └── Info               (bestehend)
```

**Icon:** `mdi6.weight` (oder `mdi6.scale-balance`)
**Verbindungsstatus:** Kleiner Punkt neben dem Icon:
- Gruen: API erreichbar, Key gueltig
- Rot: Keine Verbindung oder ungueltiger Key
- Grau: Nicht konfiguriert (kein API-Key in Settings)

### 5.2 Hauptseite: Pruefgewichte (pruefgewichte_seite.py)

Zeigt offene Auftraege als Karten-Grid mit Such- und Filterfunktion.

```
┌──────────────────────────────────────────────────────────┐
│  Prüfgewichte                                    [Titel] │
│──────────────────────────────────────────────────────────│
│                                                           │
│  ┌──────────────────────────────────┐  ┌────────────┐    │
│  │ 🔍 Suche nach Kunde, Auftrag... │  │ Offen    ▼ │    │
│  └──────────────────────────────────┘  └────────────┘    │
│                                                           │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐│
│  │ A-2026-0342    │ │ A-2026-0339    │ │ A-2026-0335    ││
│  │                │ │                │ │                ││
│  │ Musterfirma    │ │ ABC Chemie     │ │ Labor Meyer    ││
│  │ GmbH           │ │ AG             │ │                ││
│  │                │ │                │ │                ││
│  │ 5 Gewichte     │ │ 12 Gewichte    │ │ 1 Gewicht      ││
│  │ ● offen        │ │ ✓ fertig       │ │ ● offen        ││
│  └────────────────┘ └────────────────┘ └────────────────┘│
│                                                           │
│  ┌────────────────┐ ┌────────────────┐                   │
│  │ A-2026-0330    │ │ A-2026-0328    │                   │
│  │ ...            │ │ ...            │                   │
│  └────────────────┘ └────────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

**Karten-Inhalt:**
- **Oben:** Odoo-Auftragsnummer (fett, `formGruppenTitel`-Stil)
- **Mitte:** Kundenname (1-2 Zeilen, `text_sekundaer`)
- **Unten:** Anzahl Gewichte im Satz + Status
  - `● offen` (in `fehler`-Farbe, rot)
  - `✓ fertig` (in `erfolg`-Farbe, gruen)
- Klick auf Karte → oeffnet Detail-Overlay

**Karten-Styling:**
- Hintergrund: `basis` (wie Sidebar)
- Border-Radius: 10px
- Hover: `hover_bg` mit sanftem Fade (wie Tabellenzeilen)
- Cursor: PointingHandCursor
- Schatten: dezent (QGraphicsDropShadowEffect, blur 8, offset 0/2)

**Grid-Verhalten:**
- Responsive: 3 Spalten bei breitem Fenster, 2 bei mittel, 1 bei schmal
- Implementierung: QFlowLayout oder manuelle Neuberechnung bei resizeEvent
- Karten haben eine feste Mindestbreite (~200px) und maximale Breite (~280px)

**Suche:**
- Freitext ueber Kundenname und Auftragsnummer
- Live-Filter beim Tippen (wie die bestehende Tabellensuche)

**Filter-Dropdown:**
- "Offen" (Standard) -- nur offene Auftraege
- "Alle" -- offene + abgeschlossene
- "Abgeschlossen" -- nur abgeschlossene

**Leerer Zustand:**
- Wenn keine Auftraege: Zentrierte Nachricht mit Info-Icon
- Wenn API nicht konfiguriert: Hinweis auf Settings mit Link zum Server-Reiter

**Fehlerbehandlung:**
- Netzwerkfehler: Fehlermeldung in der Seite (nicht als Dialog)
- Timeout: "Server nicht erreichbar" mit Retry-Button

### 5.3 Detail-Overlay: Pruefgewichtsatz (pruefgewichte_detail.py)

Oeffnet sich als Overlay im Content-Bereich (wie Temp-Detail-Seite).
Gleiche Overlay-Mechanik: DimmOverlay, Click-Outside-to-Close, Fade+Slide.

```
┌──────────────────────────────────────────────────────────┐
│  A-2026-0342 · Musterfirma GmbH                 [Titel]  │
│──────────────────────────────────────────────────────────│
│                                                           │
│  Umgebungsbedingungen                                     │
│  Temperatur [21,5] °C   Feuchte [45,2] %   Druck [1013] │
│                                                           │
│  ─────────────────────────────────────────────────────── │
│                                                           │
│  Einzelgewichte                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ Nennwert  │ Klasse │ Form       │ Referenz │ ⚙   │   │
│  │───────────────────────────────────────────────────│   │
│  │ 100 g     │ F1     │ zylindr.   │ Ref-042  │ ✓   │   │
│  │ 200 g     │ F1     │ zylindr.   │ Ref-043  │ —   │   │
│  │ 500 g     │ F1     │ zylindr.   │ —        │ —   │   │
│  │ 1 kg      │ F1     │ Blockgew.  │ —        │ —   │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  [+ Gewicht hinzufügen]                                  │
│                                                           │
│──────────────────────────────────────────────────────────│
│  [Fehler/Status]              [PDF erstellen] [Abschl.]  │
└──────────────────────────────────────────────────────────┘
```

**Bereiche:**

#### Titel
- Format: "Auftragsnummer · Kundenname" (wie bei Temp-Detail)
- Tooltip: Vollstaendige Kundenadresse

#### Umgebungsbedingungen
- Drei Felder nebeneinander: Temperatur (°C), Luftfeuchtigkeit (%), Luftdruck (hPa)
- Werden bei der ersten Messung gesetzt und gelten fuer alle Gewichte im Satz
- Validierung: Dezimalzahlen (Komma + Punkt akzeptiert)

#### Einzelgewichte-Tabelle
- Zeigt alle Gewichte im Satz
- Letzte Spalte: Status-Icon
  - `—` (grau): Noch nicht gemessen
  - `✓` (gruen): Messung vorhanden
- Klick auf eine Zeile → oeffnet **Mess-Dialog** (OverlayDialog oder eigenes Overlay)
- Hover-Effekte wie bei der Waagentabelle (ZeilenHoverDelegate)

#### Gewicht hinzufuegen
- Button oeffnet ein kleines Formular (inline oder als Dialog):
  - Nennwert + Einheit (mg/g/kg)
  - Gewichtsklasse (Dropdown: E1, E2, F1, F2, M1, M1-2, M2, M2-3, M3)
  - Form (Dropdown oder Freitext)
  - Material (Dropdown oder Freitext)
  - Hersteller (optional)
  - Seriennummer (optional)
- "Speichern" → API-Call → Gewicht erscheint in der Tabelle

#### Mess-Dialog (fuer ein einzelnes Gewicht)
Oeffnet sich als Dialog-Overlay wenn der Techniker auf ein Gewicht klickt:

```
┌──────────────────────────────────────────────┐
│  Messung: 100 g F1                    [Titel] │
│──────────────────────────────────────────────│
│                                               │
│  Referenzgewicht                              │
│  [Dropdown: passende Referenzgewichte] ▼      │
│  (gefiltert nach Nennwert, nur gueltige)      │
│                                               │
│  ABBA-Messwerte                               │
│  A1 (Pruefling)    [__________] g             │
│  B1 (Referenz)     [__________] g             │
│  B2 (Referenz)     [__________] g             │
│  A2 (Pruefling)    [__________] g             │
│                                               │
│  Berechnete Werte (live):                     │
│  Ergebnis: 100,000310 g                       │
│  Abweichung: +0,000310 g                      │
│  Messunsicherheit: ±0,000050 g                │
│                                               │
│          [Abbrechen]  [Speichern]              │
└──────────────────────────────────────────────┘
```

**Referenzgewicht-Dropdown:**
- Beim Oeffnen des Dialogs: API-Call `/referenzgewichte/?nennwert=100&einheit=g`
- Zeigt nur Referenzgewichte mit passendem Nennwert und gueltiger Kalibrierung
- Anzeige: "Name (S/N: xxx, gueltig bis: MM/JJJJ)"

**Live-Berechnung:**
- Waehrend der Eingabe der ABBA-Werte werden Ergebnis, Abweichung und
  Messunsicherheit live berechnet und angezeigt
- Berechnung: `Mittelwert(A1, A2) - Mittelwert(B1, B2) + Referenzmasse`
- Messunsicherheit: Aus Referenz-Messunsicherheit + Streuung der Messungen

**Validierung:**
- Alle ABBA-Felder: Pflicht, Dezimalzahl
- Referenzgewicht: Pflicht
- Live-Validierung wie bei Temp-Detail (roter Rand, Inline-Fehler)

#### Aktionszeile
- **PDF erstellen:** Generiert Kalibrierschein (nur wenn alle Gewichte gemessen)
- **Abschliessen:** Markiert den Satz als abgeschlossen (API-Call),
  Karte verschwindet aus der Standard-Ansicht
- PDF-Feedback: Gruenes Icon nach Erstellung (wie bei Temp-Detail)

### 5.4 Settings-Erweiterung: Reiter "Server"

Neuer Reiter im Settings-Overlay zwischen "System" und dem Ende:

```
Einstellungen
  ├── Allgemein       (bestehend)
  ├── SimplyCal       (bestehend)
  ├── Firma           (bestehend)
  ├── Prüfer          (bestehend)
  ├── Messgeräte      (bestehend)
  ├── System          (bestehend)
  └── Server          ◄── NEU
```

**Reiter-Inhalt:**

```
┌──────────────────────────────────────────────┐
│  Server-Verbindung                            │
│                                               │
│  API-URL                                      │
│  [https://api.waagen-joehnk.de          ]     │
│                                               │
│  API-Key                                      │
│  [••••••••••••••••••••]  [Anzeigen/Verbergen] │
│                                               │
│  Status: ● Verbunden (Lennart S.)             │
│          oder                                 │
│  Status: ● Nicht verbunden (Fehler: ...)      │
│                                               │
│  [Verbindung testen]                          │
└──────────────────────────────────────────────┘
```

- **API-URL:** Standardwert `https://api.waagen-joehnk.de`, aenderbar
- **API-Key:** Passwort-Feld mit Toggle-Button zum Anzeigen/Verbergen
- **Status:** Live-Anzeige ob die Verbindung funktioniert
- **Verbindung testen:** Button der `/auth/verify` aufruft und das Ergebnis anzeigt
- Auto-Save wie alle anderen Settings

---

## 6. PDF-Generierung: Kalibrierschein

### 6.1 Generator (pdf_pruefgewicht_generator.py)

Erbt von `PDFGeneratorBase` (wie `PDFGeneratorTemp` und `PDFGeneratorVDE`).
Nutzt die gleiche Infrastruktur: HTML-Template, string.Template, xhtml2pdf,
Base64-Bilder.

```python
from pdf_base_generator import PDFGeneratorBase
from datetime import datetime


class PDFGeneratorPruefgewicht(PDFGeneratorBase):

    def add_pruefgewicht_data(self, satz_daten: dict):
        """Fuegt Pruefgewichtsatz-Daten hinzu (aus API-Response)."""
        self.data_to_append['pruefgewicht_data'] = satz_daten

    def generate_calibration_number(self):
        """Kalibrierschein-Nummer: PG_[Kuerzel]_[MMJJ]_[laufende Nr]"""
        kuerzel = self.data_to_append.get('pruefgewicht_data', {}).get(
            'techniker_kuerzel', 'XX')
        current_date = datetime.now().strftime("%m%y")
        satz_id = self.data_to_append.get('pruefgewicht_data', {}).get(
            'satz_id', '000')
        return f"PG_{kuerzel}_{current_date}_{satz_id:03d}"

    def generate_pdf(self, filename="pruefgewicht_report.pdf"):
        calibration_number = self.generate_calibration_number()
        # ... Template laden, Kontext erstellen, PDF rendern
        # Gleiche Mechanik wie in pdf_temp_generator.py
```

### 6.2 Kalibrierschein-Inhalt (grobe Struktur)

Der Kalibrierschein enthaelt:

- **Kopf:** Firmenlogo, Kalibrierscheinnummer, Pruefdatum
- **Kundendaten:** Name, Adresse
- **Auftragsdaten:** Auftragsnummer
- **Referenznormal:** Name, Seriennummer, Kalibrierscheinnummer, gueltig bis
- **Umgebungsbedingungen:** Temperatur, Feuchte, Druck
- **Tabelle der Einzelgewichte:**
  - Nennwert, Klasse, Form, Material
  - Ergebnis-Masse, Abweichung, Messunsicherheit
  - Bewertung (innerhalb/ausserhalb der Toleranz)
- **Fusszeile:** Pruefer, Unterschrift, Stempel, Firma, naechste Kalibrierung

**Hinweis:** Das genaue Template-Layout wird spaeter separat definiert.
Die Architektur (HTML-Template + string.Template + xhtml2pdf) steht bereits
und ist bewaehrt.

### 6.3 PDF-Workflow

Gleicher Ablauf wie bei Temperatur-PDFs:

1. Techniker klickt "PDF erstellen" im Detail-Overlay
2. Validierung: Alle Gewichte gemessen? Umgebungsbedingungen eingetragen?
3. Falls Kalibrierschein bereits existiert: Ueberschreib-Dialog (OverlayDialog)
4. PDF-Generierung im QThread (PdfWorker)
5. Spinner auf dem Button waehrend der Generierung
6. Erfolg: Gruenes Feedback-Icon, klickbar zum Oeffnen
7. PDF wird im Protokolle-Ordner gespeichert (`PG_LS_0326_001.pdf`)

---

## 7. Verbindungs-Management

### 7.1 App-Start

Beim Start der App, wenn ein API-Key konfiguriert ist:

```
App startet
  │
  │ API-Key in settings.ini vorhanden?
  │
  ├── Nein → Sidebar: grauer Punkt, Seite zeigt "Bitte konfigurieren"
  │
  └── Ja → POST /auth/verify im QThread
           │
           ├── Erfolg → Sidebar: gruener Punkt, Techniker-Name gespeichert
           │
           └── Fehler → Sidebar: roter Punkt, Fehler in der Seite angezeigt
```

### 7.2 Fehlerbehandlung bei API-Calls

Alle API-Calls gehen durch den `ApiWorker` (QThread). Fehler werden
in der UI angezeigt, nicht als Exceptions weitergereicht:

- **Netzwerkfehler (Timeout, Connection refused):**
  "Server nicht erreichbar. Pruefe die Internetverbindung."
- **401 Unauthorized:**
  "API-Key ungueltig. Bitte in den Einstellungen pruefen."
- **404 Not Found:**
  "Datensatz nicht gefunden."
- **500 Server Error:**
  "Serverfehler. Bitte spaeter erneut versuchen."
- **Allgemeiner Fehler:**
  Fehlermeldung direkt anzeigen.

### 7.3 Verbindungsstatus in der Sidebar

Ein kleiner farbiger Punkt neben dem "Pruefgewichte"-Icon:

- **Gruen (erfolg-Farbe):** Verbunden, Key gueltig
- **Rot (fehler-Farbe):** Verbindung fehlgeschlagen
- **Grau (text_sekundaer):** Nicht konfiguriert

Implementierung: Eigener Paint-Event im SidebarButton oder ein kleines
QLabel als Overlay.

---

## 8. Aenderungen an bestehenden Dateien

### 8.1 settings.py

Neue Getter/Setter fuer Server-Einstellungen:

```python
# --- Server/API ---

def get_api_url(self):
    return self.get_setting('SERVER', 'api_url',
                             'https://api.waagen-joehnk.de')

def set_api_url(self, url):
    self.set_setting('SERVER', 'api_url', url)

def get_api_key(self):
    return self.get_setting('SERVER', 'api_key', '')

def set_api_key(self, key):
    self.set_setting('SERVER', 'api_key', key)
```

### 8.2 ui/sidebar.py

Neuer Button nach `_btn_auftraege`:

```python
self._btn_pruefgewichte = SidebarButton(
    "mdi6.weight", "Prüfgewichte", "pruefgewichte"
)
self._btn_pruefgewichte.clicked.connect(
    lambda: self._navigation_klick(self._btn_pruefgewichte)
)
layout.addWidget(self._btn_pruefgewichte)
self._buttons.append(self._btn_pruefgewichte)
```

### 8.3 ui/main_window.py

Neue Seite im ContentStack einbinden:

```python
from ui.pruefgewichte_seite import PruefgewichteSeite

# In _erstelle_seiten():
self._pruefgewichte_seite = PruefgewichteSeite()
self._content_stack.addWidget(self._pruefgewichte_seite)  # Index 1

# seiten_map erweitern:
seiten_map = {"auftraege": 0, "pruefgewichte": 1, "info": 2}
```

Detail-Overlay Handling analog zu `_oeffne_temp_detail`.

### 8.4 ui/settings_overlay.py

Neuer Tab "Server" hinzufuegen:

```python
# In tabs-Liste:
("mdi6.cloud-outline", "Server"),

# Neues Panel:
def _erstelle_server_panel(self):
    layout = self._erstelle_scroll_panel()
    layout.addWidget(self._section_titel("Server-Verbindung"))
    # API-URL, API-Key (Passwort-Feld), Verbindung-testen-Button
    ...
```

### 8.5 ui/styles.py

Neue Styles fuer Karten:

```python
# Im generiere_stylesheet():

# Auftrags-Karten
QWidget#auftragKarte {
    background-color: {farben["basis"]};
    border-radius: 10px;
    border: 1px solid transparent;
}
QWidget#auftragKarte:hover {
    border-color: {farben["border"]};
}

# Verbindungs-Indikator
QLabel#verbindungsStatus {
    border-radius: 4px;
}
```

---

## 9. Zusammenfassung der Abhaengigkeiten

### Neue Python-Dependencies

| Package | Zweck | Installation |
|---------|-------|-------------|
| httpx   | HTTP-Client fuer API-Calls | `pip install httpx` |

Alle anderen Dependencies (PySide6, qtawesome, xhtml2pdf, etc.) sind bereits
vorhanden.

### requirements.txt Ergaenzung

```
httpx>=0.27
```

### Build (PyInstaller)

`httpx` hat keine speziellen hidden imports. Der bestehende PyInstaller-Build
sollte ohne Anpassungen funktionieren. Falls noetig, wird der
`hook-combined.py` erweitert.

---

## 10. Offene Punkte

### Vor der Implementierung zu klaeren

- Genaues Kalibrierschein-Layout (Template-Design)
- ABBA-Berechnungsformel und Messunsicherheitsbudget im Detail
- Welche Gewichtsklassen sind fuer eure Werkskalibrierung relevant?
- Flow-Layout fuer Karten: QFlowLayout als Custom-Widget oder Grid mit
  resizeEvent-Neuberechnung?

### Spaetere Erweiterungen (Architektur vorbereitet)

- Offline-Cache: API-Daten lokal zwischenspeichern (SQLite oder JSON)
- Eigene Pruefgewichtsaetze von Waagen-Joehnk verwalten (aus SimplyCal-Sync)
- Kalibrierschein per Mail versenden (aus der App heraus oder ueber API)
- Zaehlwaagen-Kalibrierung als weiterer Prueftyp (neue Seite, gleiches Muster)
