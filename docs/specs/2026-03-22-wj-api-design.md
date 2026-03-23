# WJ-API: Server-Design fuer Waagen-Joehnk Kalibrierplattform

> **Status:** Entwurf
> **Erstellt:** 2026-03-22
> **Autor:** Lennart (Waagen-Joehnk KG)
> **Ziel-Repository:** `wj-api` (eigenstaendiges Repo, nicht Teil von WJPruefpilot)

---

## 1. Uebersicht

Die WJ-API ist ein zentraler REST-API-Server fuer Waagen-Joehnk KG. Sie dient als
einzige Schnittstelle zwischen den Client-Anwendungen (WJPruefpilot Desktop-App,
zukuenftiges Kunden-Dashboard) und den Backend-Systemen (MariaDB, Odoo 19 ERP).

### Primaerer Anwendungsfall: Pruefgewichte-Kalibrierung

Kunden senden ihre Pruefgewichte an Waagen-Joehnk zur Werkskalibrierung (nicht
akkreditiert, angelehnt an akkreditierten Prozess). Die API verwaltet:

- Auftraege und Kundendaten (aus Odoo)
- Pruefgewichtsaetze mit Einzelgewichten
- ABBA-Messergebnisse und Umgebungsbedingungen
- Referenzgewichte (aus SimplyCal synchronisiert)

### Zukuenftige Erweiterungen (Architektur vorbereitet)

- Zaehlwaagen-Kalibrierung
- Kunden-Dashboard (Web-Frontend)
- Offline/Online-Synchronisation fuer die Desktop-App

---

## 2. Systemarchitektur

```
┌──────────────────────────────────────────────────────┐
│  Hetzner VPS (CX22, Ubuntu 24.04 LTS)               │
│                                                       │
│  ┌───────────────┐      ┌───────────────┐            │
│  │   Caddy        │      │   MariaDB     │            │
│  │   (Reverse     │      │   10.11+      │            │
│  │    Proxy +     │      │               │            │
│  │    HTTPS)      │      │  - benutzer   │            │
│  │                │      │  - kunde      │            │
│  │   Port 443 ────┼─────▶│  - auftrag    │            │
│  │                │      │  - pruefgew.  │            │
│  └───────┬────────┘      │  - messung    │            │
│          │               │  - referenz   │            │
│          ▼               └───────────────┘            │
│  ┌───────────────┐                                    │
│  │   FastAPI      │                                   │
│  │   + Uvicorn    │                                   │
│  │                │      ┌───────────────┐            │
│  │   Port 8000    │─────▶│   Odoo 19     │  (extern)  │
│  │   (localhost)  │      │   SaaS Custom │            │
│  │                │      │   JSON-RPC    │            │
│  └───────────────┘      └───────────────┘            │
│                                                       │
└──────────────────────────────────────────────────────┘
         ▲                          ▲
         │ HTTPS                    │
         │ + API-Key                │
         │                          │
┌────────┴─────────┐     ┌─────────┴──────────┐
│  WJPruefpilot    │     │  SimplyCal-Server  │
│  (Desktop-App)   │     │  (Windows Server)
│                  │     │                     │
│  httpx Client    │     │  Sync-Skript        │
│                  │     │  pusht Referenz-     │
│                  │     │  gewichte nach       │
│                  │     │  MariaDB             │
└──────────────────┘     └─────────────────────┘
         ▲
         │ (spaeter)
         │
┌────────┴─────────┐
│  Kunden-Dashboard│
│  (Web-Frontend)  │
│                  │
│  SSO via Odoo    │
└──────────────────┘
```

### Datenfluss

1. **WJPruefpilot → FastAPI:** Techniker fragt Auftraege ab, erfasst Gewichte und
   Messwerte, schliesst Auftraege ab. Authentifizierung per API-Key.
2. **FastAPI → Odoo:** On-demand Abfrage offener Auftraege und Kundendaten.
   Ein globaler Service-Account mit Leserechten. Keine staendige Synchronisation.
3. **FastAPI → MariaDB:** Persistierung aller Pruefgewicht-Daten, Messungen,
   Auftragsstatus. Die Datenbank ist die zentrale Wahrheit.
4. **SimplyCal-Server → MariaDB:** Separates Sync-Skript pusht Referenzgewichte
   in die MariaDB. Laeuft auf dem lokalen Server im Firmen-LAN.
5. **Kunden-Dashboard → FastAPI (spaeter):** Kunden sehen ihre Kalibrierscheine.
   Authentifizierung ueber signierten Token aus dem Odoo-Portal (SSO).

---

## 3. Tech-Stack

| Komponente         | Technologie                    | Begruendung                                            |
|--------------------|--------------------------------|--------------------------------------------------------|
| Betriebssystem     | Ubuntu 24.04 LTS               | Stabil, langfristig supported, Standard bei Hetzner    |
| Reverse Proxy      | Caddy 2                        | Automatisches HTTPS (Let's Encrypt), minimale Config   |
| API-Framework      | FastAPI (Python)               | Async, automatische Swagger-Docs, Pydantic-Validierung |
| ASGI-Server        | Uvicorn                        | Standard fuer FastAPI, performant                      |
| Datenbank          | MariaDB 10.11+                 | Mehrbenutzerfaehig, auf Hetzner gut supported          |
| ORM                | SQLAlchemy 2.0 (async)         | Ausgereift, Alembic fuer Migrationen                   |
| DB-Migrationen     | Alembic                        | Versionierte Schema-Aenderungen, rollback-faehig       |
| Odoo-Client        | httpx (JSON-RPC direkt)        | Leichtgewichtig, kein Extra-Dependency noetig          |
| Authentifizierung  | API-Key (Techniker), JWT (spaeter Kunden) | Einfach, erweiterbar             |
| Prozessmanager     | systemd                        | Standard unter Ubuntu, auto-restart bei Crash          |
| Domain             | api.waagen-joehnk.de           | Firmen-Domain, allgemein nutzbar                       |

### Python-Dependencies (requirements.txt)

```
fastapi>=0.115
uvicorn[standard]>=0.30
sqlalchemy[asyncio]>=2.0
aiomysql>=0.2
alembic>=1.13
pydantic>=2.0
pydantic-settings>=2.0
httpx>=0.27
passlib[bcrypt]>=1.7
python-dotenv>=1.0
```

---

## 4. Datenmodell

### 4.1 Uebersicht Beziehungen

```
benutzer ──┐
           │ techniker_id
           ▼
kunde ◄── auftrag ──▶ pruefgewichtsatz ──▶ einzelgewicht ──▶ messung
  ▲                                                             │
  │ odoo_partner_id                              referenzgewicht_id
  │ (Abgleich)                                                  │
  │                                         referenzgewicht ◄───┘
Odoo
```

### 4.2 Tabelle: benutzer

Verwaltet alle Benutzer des Systems. Durch das `rolle`-Feld erweiterbar fuer
zukuenftige Benutzertypen (Kunden-Dashboard).

| Spalte          | Typ              | Beschreibung                                  |
|-----------------|------------------|-----------------------------------------------|
| id              | INT, PK, AUTO    | Primaerschluessel                             |
| name            | VARCHAR(100)     | Voller Name                                   |
| email           | VARCHAR(150)     | E-Mail-Adresse (eindeutig)                    |
| rolle           | ENUM             | `techniker`, `kunde`, `admin`                 |
| kuerzel         | VARCHAR(5), NULL | Nur fuer Techniker (z.B. "LS" fuer Kalibrierschein-Nr) |
| kunde_id        | INT, FK, NULL    | Nur fuer Rolle `kunde` → Verknuepfung zu kunde-Tabelle |
| api_key_hash    | VARCHAR(255)     | Gehashter API-Key (bcrypt)                    |
| passwort_hash   | VARCHAR(255), NULL | Fuer spaeteres Portal-Login (Kunden)        |
| aktiv           | BOOLEAN          | Deaktivierte Benutzer koennen sich nicht anmelden |
| erstellt_am     | DATETIME         | Erstellungszeitpunkt                          |

**Indizes:** `email` (UNIQUE), `api_key_hash` (INDEX fuer schnelle Suche)

### 4.3 Tabelle: kunde

Kundendaten aus Odoo. Werden bei jedem Auftrags-Abruf automatisch aktualisiert,
falls sich in Odoo etwas geaendert hat.

| Spalte          | Typ              | Beschreibung                                  |
|-----------------|------------------|-----------------------------------------------|
| id              | INT, PK, AUTO    | Primaerschluessel                             |
| odoo_partner_id | INT, UNIQUE      | Odoo-Referenz (res.partner ID) fuer Abgleich  |
| name            | VARCHAR(200)     | Firmenname / Kundenname (adr_name1)           |
| name2           | VARCHAR(200), NULL | Zusatzzeile (adr_name2)                     |
| name3           | VARCHAR(200), NULL | Zusatzzeile (adr_name3)                     |
| strasse         | VARCHAR(200)     | Strasse + Hausnummer                          |
| plz             | VARCHAR(20)      | Postleitzahl                                  |
| ort             | VARCHAR(100)     | Stadt                                         |
| land            | VARCHAR(100)     | Land (Default: Deutschland)                   |
| aktualisiert_am | DATETIME         | Letzter Abgleich mit Odoo                     |

**Indizes:** `odoo_partner_id` (UNIQUE)

### 4.4 Tabelle: auftrag

Zentrale Klammer fuer alle Prueftypen. Das `typ`-Feld bestimmt, welche
Detail-Tabelle(n) zugehoerig sind. Spaeter kommen Typen wie `zaehlwaage`,
`vde_extern` etc. hinzu.

| Spalte           | Typ              | Beschreibung                                 |
|------------------|------------------|----------------------------------------------|
| id               | INT, PK, AUTO    | Primaerschluessel                            |
| kunde_id         | INT, FK          | → kunde.id                                   |
| techniker_id     | INT, FK          | → benutzer.id (der zustaendige Techniker)    |
| odoo_auftrag_nr  | VARCHAR(50)      | Auftragsnummer aus Odoo (z.B. "A-2026-0342") |
| typ              | ENUM             | `pruefgewichte`, spaeter: `zaehlwaage`, etc. |
| status           | ENUM             | `offen`, `abgeschlossen`                     |
| erstellt_am      | DATETIME         | Wann der Auftrag in der API angelegt wurde   |
| abgeschlossen_am | DATETIME, NULL   | Wann der Techniker abgeschlossen hat         |

**Indizes:** `odoo_auftrag_nr` (UNIQUE), `status` (INDEX), `kunde_id` (FK INDEX)

**Wichtig:** `status` wird nur in der MariaDB verwaltet. Kein Rueckschrieb nach
Odoo. Abgeschlossene Auftraege bleiben dauerhaft in der DB erhalten (Archiv),
werden aber nicht mehr gegen Odoo abgeglichen.

### 4.5 Tabelle: pruefgewichtsatz

Detail-Tabelle fuer Auftraege vom Typ `pruefgewichte`. Jeder Auftrag hat
genau einen Pruefgewichtsatz (1:1). Auch Einzelgewichte werden als Satz
mit einem Eintrag behandelt.

| Spalte            | Typ              | Beschreibung                                |
|-------------------|------------------|---------------------------------------------|
| id                | INT, PK, AUTO    | Primaerschluessel                           |
| auftrag_id        | INT, FK, UNIQUE  | → auftrag.id (1:1 Beziehung)               |
| kalibrierschein_nr| VARCHAR(50), NULL| Generierte Nummer (z.B. "PG_LS_0326_001")  |
| bemerkungen       | TEXT, NULL       | Allgemeine Bemerkungen zum Satz             |
| erstellt_am       | DATETIME         | Erstellungszeitpunkt                        |
| abgeschlossen_am  | DATETIME, NULL   | Wann alle Gewichte kalibriert waren         |

### 4.6 Tabelle: einzelgewicht

Die einzelnen Gewichte innerhalb eines Pruefgewichtsatzes. Jedes Gewicht
wird separat kalibriert und erscheint als eigene Zeile auf dem Kalibrierschein.

| Spalte         | Typ              | Beschreibung                                  |
|----------------|------------------|-----------------------------------------------|
| id             | INT, PK, AUTO    | Primaerschluessel                             |
| satz_id        | INT, FK          | → pruefgewichtsatz.id                         |
| nennwert       | DECIMAL(12,6)    | Nennmasse (z.B. 100.000000 fuer 100 g)       |
| einheit        | ENUM             | `mg`, `g`, `kg`                               |
| gewichtsklasse | VARCHAR(10)      | OIML-Klasse: E1, E2, F1, F2, M1, M1-2, M2, M2-3, M3 |
| form           | VARCHAR(50)      | z.B. "zylindrisch", "Knopf", "Blockgewicht"  |
| material       | VARCHAR(50)      | z.B. "Edelstahl", "Messing", "Gusseisen"     |
| hersteller     | VARCHAR(100), NULL | Hersteller des Gewichts                     |
| seriennummer   | VARCHAR(50), NULL | Seriennummer falls vorhanden                 |

**Indizes:** `satz_id` (FK INDEX)

### 4.7 Tabelle: messung

ABBA-Messergebnisse pro Einzelgewicht. Aktuell 1:1 (ein ABBA-Zyklus pro
Gewicht bei Werkskalibrierung). Die Struktur erlaubt spaeter 1:n fuer
mehrere Zyklen bei akkreditierter Kalibrierung.

| Spalte             | Typ              | Beschreibung                               |
|--------------------|------------------|--------------------------------------------|
| id                 | INT, PK, AUTO    | Primaerschluessel                          |
| gewicht_id         | INT, FK          | → einzelgewicht.id                         |
| referenzgewicht_id | INT, FK          | → referenzgewicht.id (verwendetes Normal)  |
| abba_a1            | DECIMAL(12,6)    | 1. Messung Pruefling (A)                   |
| abba_b1            | DECIMAL(12,6)    | 1. Messung Referenz (B)                    |
| abba_b2            | DECIMAL(12,6)    | 2. Messung Referenz (B)                    |
| abba_a2            | DECIMAL(12,6)    | 2. Messung Pruefling (A)                   |
| ergebnis_masse     | DECIMAL(12,6)    | Berechnete konventionelle Masse            |
| abweichung         | DECIMAL(12,6)    | Abweichung vom Nennwert                    |
| messunsicherheit   | DECIMAL(12,6)    | Erweiterte Messunsicherheit (k=2)          |
| temperatur         | DECIMAL(5,1)     | Umgebungstemperatur in °C                  |
| luftfeuchtigkeit   | DECIMAL(5,1)     | Relative Luftfeuchtigkeit in %             |
| luftdruck          | DECIMAL(7,1)     | Luftdruck in hPa                           |
| gemessen_am        | DATETIME         | Zeitpunkt der Messung                      |

**Indizes:** `gewicht_id` (FK INDEX), `referenzgewicht_id` (FK INDEX)

**Hinweis zu ABBA:** Die konventionelle Masse ergibt sich aus:
`Mittelwert(A1, A2) - Mittelwert(B1, B2) + Referenzmasse`. Die Berechnung
erfolgt in der App oder in der API -- der berechnete Wert wird zusaetzlich
gespeichert um Nachvollziehbarkeit zu gewaehrleisten.

### 4.8 Tabelle: referenzgewicht

Eigene Referenznormale (kalibrierte Gewichte) von Waagen-Joehnk. Werden
durch ein separates Sync-Skript vom SimplyCal-Server befuellt. Die API
stellt sie nur zum Lesen bereit.

| Spalte              | Typ              | Beschreibung                              |
|---------------------|------------------|-------------------------------------------|
| id                  | INT, PK, AUTO    | Primaerschluessel                         |
| nennwert            | DECIMAL(12,6)    | Nennmasse                                 |
| einheit             | ENUM             | `mg`, `g`, `kg`                           |
| gewichtsklasse      | VARCHAR(10)      | OIML-Klasse                               |
| ist_masse           | DECIMAL(12,6)    | Tatsaechliche kalibrierte Masse           |
| messunsicherheit    | DECIMAL(12,6)    | Messunsicherheit aus dem Kalibrierschein   |
| kalibrierschein_nr  | VARCHAR(50)      | Nr. des Kalibrierscheins des Referenznormals |
| kalibriert_bis      | DATE             | Gueltigkeitsdatum der Kalibrierung        |
| quelle              | VARCHAR(50)      | Herkunft (z.B. "simplycal_sync")          |
| aktualisiert_am     | DATETIME         | Letztes Update durch Sync-Skript          |

**Indizes:** `nennwert` + `einheit` (INDEX fuer Suche nach passendem Referenzgewicht)

---

## 5. API-Endpunkte

Basis-URL: `https://api.waagen-joehnk.de/api/v1`

Alle Endpunkte erfordern den Header `X-API-Key: <techniker-api-key>`,
sofern nicht anders angegeben.

### 5.1 Authentifizierung

| Methode | Endpunkt        | Beschreibung                                    |
|---------|----------------|-------------------------------------------------|
| POST    | /auth/verify   | API-Key pruefen, Techniker-Info zurueckgeben    |

**Request:** Header `X-API-Key`
**Response:** `{ "techniker_id": 1, "name": "Lennart S.", "kuerzel": "LS" }`
**Fehler:** 401 bei ungueltigem oder deaktiviertem Key

Wird beim App-Start einmalig aufgerufen um den Key zu validieren und den
Techniker-Namen fuer die Session zu laden.

### 5.2 Auftraege

Auftraege werden on-demand aus Odoo geladen. Beim Abruf passiert:
1. FastAPI fragt Odoo nach offenen Aussendienst-Auftraegen (Typ Pruefgewichte)
2. Neue Auftraege werden in MariaDB angelegt (inkl. Kundendaten)
3. Bereits bekannte Kunden werden aktualisiert falls sich Odoo-Daten geaendert haben
4. Bereits in MariaDB abgeschlossene Auftraege werden NICHT erneut aus Odoo geholt

| Methode | Endpunkt         | Beschreibung                                   |
|---------|------------------|-------------------------------------------------|
| GET     | /auftraege/      | Offene Auftraege aus Odoo holen + MariaDB-Auftraege kombinieren |
| GET     | /auftraege/{id}  | Einzelner Auftrag mit Kundendaten               |

**GET /auftraege/ Query-Parameter:**
- `status` (optional): `offen` (default), `abgeschlossen`, `alle`

**Response-Beispiel:**
```json
{
  "auftraege": [
    {
      "id": 1,
      "odoo_auftrag_nr": "A-2026-0342",
      "typ": "pruefgewichte",
      "status": "offen",
      "kunde": {
        "name": "Musterfirma GmbH",
        "ort": "Hamburg"
      },
      "gewichtsatz_id": null,
      "erstellt_am": "2026-03-22T10:30:00"
    }
  ]
}
```

### 5.3 Pruefgewichtsaetze

| Methode | Endpunkt                           | Beschreibung                          |
|---------|------------------------------------|---------------------------------------|
| POST    | /gewichtsaetze/                    | Neuen Satz anlegen (an Auftrag)       |
| GET     | /gewichtsaetze/                    | Alle Saetze (Filter: status, kunde)   |
| GET     | /gewichtsaetze/{id}                | Satz mit Einzelgewichten + Messungen  |
| PUT     | /gewichtsaetze/{id}                | Satz aktualisieren (Bemerkungen)      |
| PUT     | /gewichtsaetze/{id}/abschliessen   | Status auf abgeschlossen setzen       |

**POST /gewichtsaetze/ Request:**
```json
{
  "auftrag_id": 1
}
```

**PUT /gewichtsaetze/{id}/abschliessen:**
- Setzt `pruefgewichtsatz.abgeschlossen_am` und `auftrag.status = "abgeschlossen"`
- Generiert die Kalibrierscheinnummer (Format: `PG_[Kuerzel]_[MMJJ]_[laufende Nr]`)
- Abgeschlossene Auftraege verschwinden aus der Standard-Ansicht

### 5.4 Einzelgewichte

| Methode | Endpunkt                                      | Beschreibung           |
|---------|-----------------------------------------------|------------------------|
| POST    | /gewichtsaetze/{satz_id}/gewichte/             | Gewicht hinzufuegen    |
| PUT     | /gewichtsaetze/{satz_id}/gewichte/{id}         | Gewicht bearbeiten     |
| DELETE  | /gewichtsaetze/{satz_id}/gewichte/{id}         | Gewicht entfernen      |

**POST Request-Beispiel:**
```json
{
  "nennwert": 100.0,
  "einheit": "g",
  "gewichtsklasse": "F1",
  "form": "zylindrisch",
  "material": "Edelstahl",
  "hersteller": "Kern & Sohn",
  "seriennummer": "KS-2024-001"
}
```

### 5.5 Messungen

| Methode | Endpunkt                                                    | Beschreibung        |
|---------|-------------------------------------------------------------|---------------------|
| POST    | /gewichtsaetze/{satz_id}/gewichte/{gew_id}/messung          | Messung speichern   |
| PUT     | /gewichtsaetze/{satz_id}/gewichte/{gew_id}/messung          | Messung korrigieren |

**POST Request-Beispiel:**
```json
{
  "referenzgewicht_id": 5,
  "abba_a1": 100.000312,
  "abba_b1": 100.000105,
  "abba_b2": 100.000108,
  "abba_a2": 100.000309,
  "temperatur": 21.5,
  "luftfeuchtigkeit": 45.2,
  "luftdruck": 1013.25
}
```

**Response:** Enthaelt zusaetzlich die berechneten Werte:
```json
{
  "id": 1,
  "ergebnis_masse": 100.000310,
  "abweichung": 0.000310,
  "messunsicherheit": 0.000050,
  "..."
}
```

### 5.6 Referenzgewichte

Read-only. Befuellt durch das SimplyCal-Sync-Skript.

| Methode | Endpunkt                          | Beschreibung                        |
|---------|-----------------------------------|-------------------------------------|
| GET     | /referenzgewichte/                 | Alle verfuegbaren Referenzgewichte  |

**Query-Parameter:**
- `nennwert` (optional): Filtern nach Nennwert (z.B. `100`)
- `einheit` (optional): `mg`, `g`, `kg`
- `gueltig` (optional, default: `true`): Nur Gewichte deren Kalibrierung noch gueltig ist

---

## 6. Authentifizierung & Autorisierung

### 6.1 Techniker-Authentifizierung (jetzt)

Jeder Techniker erhaelt einen individuellen API-Key. Dieser wird:
- Vom Admin generiert und an den Techniker uebergeben
- In der `benutzer`-Tabelle als bcrypt-Hash gespeichert
- Vom Techniker einmalig in der WJPruefpilot-App eingegeben (Settings)
- Bei jedem API-Call im Header `X-API-Key` mitgesendet

```
WJPruefpilot                    FastAPI
    │                               │
    │  X-API-Key: abc123...         │
    │──────────────────────────────▶│
    │                               │ bcrypt.verify(key, hash)
    │                               │ → benutzer.rolle == "techniker"?
    │                               │ → benutzer.aktiv == true?
    │      200 OK + Daten           │
    │◀──────────────────────────────│
```

**FastAPI Dependency (auth/dependencies.py):**
```python
async def aktueller_techniker(x_api_key: str = Header(...)) -> Benutzer:
    benutzer = await finde_benutzer_per_api_key(x_api_key)
    if not benutzer or not benutzer.aktiv:
        raise HTTPException(401, "Ungueltiger API-Key")
    if benutzer.rolle != "techniker":
        raise HTTPException(403, "Kein Techniker-Zugang")
    return benutzer
```

### 6.2 Odoo Service-Account

Ein einzelner technischer Benutzer in Odoo (z.B. `api@waagen-joehnk.de`) mit:
- **Nur Leserechten** auf Aussendienst-Auftraege und Kontakte
- Authentifizierung per **Odoo API-Key** (nicht Passwort)
- Credentials liegen in der `.env`-Datei auf dem VPS

```env
# .env auf dem VPS
ODOO_URL=https://waagen-joehnk.odoo.com
ODOO_DB=waagen-joehnk
ODOO_USER=api@waagen-joehnk.de
ODOO_API_KEY=odoo_api_key_hier
```

### 6.3 Kunden-Authentifizierung (spaeter, geplant)

Kunden authentifizieren sich ueber ihr Odoo-Portal. Der Ablauf:

1. Kunde ist im Odoo-Portal eingeloggt
2. Klickt auf "Meine Kalibrierscheine" (Custom-Modul in Odoo)
3. Odoo generiert einen signierten JWT-Token (gemeinsames Secret mit FastAPI)
4. Redirect zu `https://dashboard.waagen-joehnk.de/?token=eyJhb...`
5. FastAPI verifiziert den Token und authentifiziert den Kunden
6. Dashboard zeigt nur Daten dieses Kunden (gefiltert ueber `kunde_id`)

**Endpunkte fuer das Kunden-Dashboard:**
```
/portal/v1/kalibrierscheine/     → eigene Kalibrierscheine
/portal/v1/auftraege/            → eigene Auftraege + Status
```

Authentifizierung per `Authorization: Bearer <JWT>` Header.

---

## 7. Odoo-Integration

### 7.1 Verbindung

Odoo 19 bietet eine JSON-RPC API (auch XML-RPC, aber JSON-RPC ist moderner).
Die FastAPI kommuniziert direkt via `httpx` mit der Odoo JSON-RPC Schnittstelle.

```python
# kunden/odoo_service.py -- vereinfachtes Beispiel
class OdooService:
    def __init__(self, url, db, user, api_key):
        self._url = url
        self._db = db
        self._uid = None  # wird bei authenticate() gesetzt
        self._api_key = api_key
        self._client = httpx.AsyncClient()

    async def authenticate(self):
        """Authentifiziert sich bei Odoo und speichert die UID."""
        response = await self._client.post(f"{self._url}/jsonrpc", json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self._db, self._user, self._api_key, {}]
            }
        })
        self._uid = response.json()["result"]

    async def hole_offene_auftraege(self):
        """Holt offene Aussendienst-Auftraege vom Typ Pruefgewichte."""
        response = await self._client.post(f"{self._url}/jsonrpc", json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self._db, self._uid, self._api_key,
                    "project.task",  # oder das passende Odoo-Modell
                    "search_read",
                    [[
                        ("stage_id.name", "!=", "Erledigt"),
                        ("tag_ids.name", "=", "Pruefgewichte"),
                    ]],
                    {"fields": ["name", "partner_id", "date_deadline"]}
                ]
            }
        })
        return response.json()["result"]
```

### 7.2 Welche Odoo-Felder werden abgefragt

Nur die fuer die Pruefgewichte-Kalibrierung relevanten Felder:

**Aus Auftraegen (project.task / field.service):**
- Auftragsnummer
- Kundennummer (partner_id)
- Status
- Faelligkeitsdatum

**Aus Kontakten (res.partner) -- ueber partner_id:**
- Firmenname (name)
- Strasse, PLZ, Ort, Land

### 7.3 Sync-Verhalten

- **Kein staendiger Sync** -- nur on-demand wenn ein Techniker Auftraege abruft
- **Nur offene Auftraege** aus Odoo abfragen
- **Kundendaten aktualisieren** wenn der Kunde bereits in MariaDB existiert
  und sich Odoo-Daten geaendert haben (Vergleich ueber `odoo_partner_id`)
- **Abgeschlossene Auftraege** in MariaDB werden nie wieder gegen Odoo abgeglichen
- **Kein Rueckschrieb** nach Odoo -- Odoo ist read-only Quelle

---

## 8. Server-Setup & Deployment

### 8.1 Initiales Server-Setup

```bash
# 1. Hetzner VPS bestellen (CX22, Ubuntu 24.04)
# 2. DNS: api.waagen-joehnk.de → VPS-IP

# 3. Server absichern
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable

# 4. MariaDB installieren
apt install mariadb-server
mysql_secure_installation
# Datenbank + Benutzer anlegen:
# CREATE DATABASE wj_api CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'wj_api'@'localhost' IDENTIFIED BY '...';
# GRANT ALL ON wj_api.* TO 'wj_api'@'localhost';

# 5. Python + venv
apt install python3.12 python3.12-venv
mkdir /opt/wj-api
cd /opt/wj-api
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Caddy installieren
apt install caddy
# Caddyfile: /etc/caddy/Caddyfile
```

### 8.2 Caddy-Konfiguration

```
api.waagen-joehnk.de {
    reverse_proxy localhost:8000
}
```

HTTPS-Zertifikat wird automatisch von Let's Encrypt geholt und erneuert.

### 8.3 systemd Service

```ini
# /etc/systemd/system/wj-api.service
[Unit]
Description=WJ API Server
After=network.target mariadb.service

[Service]
Type=exec
User=www-data
WorkingDirectory=/opt/wj-api
EnvironmentFile=/opt/wj-api/.env
ExecStart=/opt/wj-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable wj-api
systemctl start wj-api
```

### 8.4 Deployment-Workflow

```
Entwickler-PC                    GitHub                  Hetzner VPS
    │                               │                       │
    │  git push                     │                       │
    │──────────────────────────────▶│                       │
    │                               │                       │
    │  ssh + deploy.sh              │                       │
    │──────────────────────────────────────────────────────▶│
    │                               │                       │
    │                               │  cd /opt/wj-api       │
    │                               │  git pull              │
    │                               │  pip install -r req..  │
    │                               │  alembic upgrade head  │
    │                               │  systemctl restart     │
```

**deploy.sh (auf dem VPS):**
```bash
#!/bin/bash
cd /opt/wj-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
systemctl restart wj-api
```

### 8.5 Backup

```bash
# Cronjob: taeglich um 03:00
0 3 * * * mysqldump -u wj_api wj_api | gzip > /opt/backups/wj_api_$(date +\%Y\%m\%d).sql.gz
# Aufbewahrung: 30 Tage, aeltere automatisch loeschen
find /opt/backups -name "wj_api_*.sql.gz" -mtime +30 -delete
```

---

## 9. Projektstruktur

```
wj-api/
├── main.py                     # FastAPI App-Instanz, Router einbinden, CORS, Startup
├── requirements.txt            # Python-Dependencies
├── .env                        # Secrets: DB, Odoo, JWT (NICHT im Git)
├── .env.example                # Vorlage mit Platzhaltern (im Git)
├── .gitignore
├── deploy.sh                   # Deployment-Skript
│
├── auth/
│   ├── __init__.py
│   ├── dependencies.py         # FastAPI Dependency: API-Key pruefen → Benutzer
│   └── models.py               # SQLAlchemy Model: Benutzer
│
├── kunden/
│   ├── __init__.py
│   ├── router.py               # Endpunkte: GET /kunden/
│   ├── models.py               # SQLAlchemy Model: Kunde
│   ├── schemas.py              # Pydantic Schemas fuer Request/Response
│   └── odoo_service.py         # Odoo JSON-RPC Calls (Kunden + Auftraege)
│
├── auftraege/
│   ├── __init__.py
│   ├── router.py               # Endpunkte: GET /auftraege/
│   ├── models.py               # SQLAlchemy Model: Auftrag
│   └── schemas.py              # Pydantic Schemas
│
├── pruefgewichte/
│   ├── __init__.py
│   ├── router.py               # CRUD: Saetze, Gewichte, Messungen
│   ├── models.py               # SQLAlchemy Models: Satz, Einzelgewicht, Messung
│   ├── schemas.py              # Pydantic Schemas
│   └── berechnungen.py         # ABBA-Berechnung, Messunsicherheit
│
├── referenzgewichte/
│   ├── __init__.py
│   ├── router.py               # GET /referenzgewichte/
│   ├── models.py               # SQLAlchemy Model: Referenzgewicht
│   └── schemas.py              # Pydantic Schemas
│
├── db/
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy async Engine + SessionLocal
│   ├── alembic.ini             # Alembic-Konfiguration
│   └── migrations/
│       ├── env.py              # Alembic Migration-Environment
│       └── versions/           # Einzelne Migrationen (autogenerate)
│
├── docs/
│   └── api.md                  # Zusaetzliche API-Dokumentation (optional)
│
└── tests/
    ├── conftest.py             # Test-DB Setup, Fixtures, Test-Client
    ├── test_auth.py            # Auth-Tests
    ├── test_auftraege.py       # Auftrags-Tests
    ├── test_pruefgewichte.py   # Pruefgewicht-CRUD-Tests
    └── test_messungen.py       # Mess-Tests inkl. ABBA-Berechnung
```

### Prinzipien

- **Ein Ordner pro Domaene:** Neuer Prueftyp (z.B. Zaehlwaagen) = neuer Ordner
  mit eigenen Models, Schemas, Router. Bestehender Code wird nicht angefasst.
- **Schemas getrennt von Models:** Pydantic Schemas (API-Schicht) sind unabhaengig
  von SQLAlchemy Models (DB-Schicht). Aenderungen an der DB brechen nicht die API.
- **Secrets nur in .env:** Nie im Code, nie im Git. `.env.example` als Vorlage.
- **Tests von Anfang an:** Mindestens die wichtigsten Endpunkte und die
  ABBA-Berechnung testen.

---

## 10. Offene Punkte & Zukuenftige Erweiterungen

### Spaeter implementieren (Architektur ist vorbereitet)

- **Kunden-Dashboard:** Web-Frontend (React, Vue, oder Python-basiert),
  gleiche FastAPI als Backend, SSO ueber Odoo-Portal
- **Offline/Online-Sync:** App cached Daten lokal, synchronisiert bei Verbindung
  mit der API. Erfordert Conflict-Resolution-Strategie.
- **Zaehlwaagen-Kalibrierung:** Neuer `auftrag.typ` + eigene Detail-Tabelle(n)
  + eigener Ordner im API-Repo
- **SimplyCal-Sync-Skript:** Laeuft auf dem lokalen SimplyCal-Server, pusht
  Referenzgewichte in die MariaDB. Separates Skript, nicht Teil der FastAPI.
- **E-Mail-Versand:** Kalibrierscheine automatisch per Mail an Kunden senden
  (optional, koennte ueber Odoo oder direkt ueber die API laufen)
- **Odoo-Rueckschrieb:** Auftragsstatus in Odoo aktualisieren wenn in der
  App abgeschlossen (Option C aus dem Brainstorming, mit Retry-Warteschlange)

### Noch zu klaeren

- Genaues Odoo-Modell fuer Aussendienst-Auftraege (`project.task`, `field.service`,
  oder Custom-Modell?) -- muss in der Odoo-Instanz geprueft werden
- Detaillierte ABBA-Berechnungsformel und Messunsicherheitsbudget
- Kalibrierschein-Layout und Template (HTML → PDF wie bei Temp-Protokollen)
- SimplyCal-Sync: Welche Felder exportiert SimplyCal fuer Referenzgewichte?
