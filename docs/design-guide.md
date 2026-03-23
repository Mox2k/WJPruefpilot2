# WJPruefpilot Design Guide

Referenzdokument fuer einheitliches UI-Design. Alle Werte basieren auf einem
**8px-Grundraster** und einer konsistenten Typografie-Skala.

---

## 1. Raster & Spacing-System

Basierend auf einem **8px-Grid**. Alle Abstaende sind Vielfache von 4px oder 8px.

| Token   | Wert  | Verwendung                                      |
|---------|-------|--------------------------------------------------|
| `xs`    | 4px   | Minimaler Abstand (Icon-Spacing, Button-Gaps)    |
| `sm`    | 8px   | Enger Abstand (Label-zu-Input, Inline-Elemente)  |
| `md`    | 12px  | Standard-Abstand (Zwischen Formular-Elementen)   |
| `lg`    | 16px  | Gruppen-Abstand (Settings-Sektionen, Auftraege)  |
| `xl`    | 24px  | Sektions-Abstand (Zwischen Hauptbereichen)       |
| `2xl`   | 32px  | Seiten-Rand (horizontales Padding)               |
| `3xl`   | 40px  | Grosser Sektions-Abstand (Detail-Seiten-Rand)    |

### Seiten-Margins (ContentsMargins)

| Bereich             | Links | Oben | Rechts | Unten |
|---------------------|-------|------|--------|-------|
| Auftraege-Seite     | 32    | 24   | 32     | 24    |
| Detail-Seite Inhalt | 40    | 32   | 40     | 24    |
| Detail Aktionszeile | 40    | 12   | 40     | 24    |
| Dialog-Box          | 32    | 24   | 32     | 24    |
| Settings Tab-Panel  | 8     | 16   | 8      | 16    |
| Settings Inhalt     | 32    | 24   | 32     | 24    |
| Infobox             | 12    | 12   | 12     | 12    |

Detail-Seite hat bewusst groessere Margins (40px) als die Auftraege-Seite (32px),
da sie weniger Inhalt hat und luftiger wirken soll.

### Spacing (Abstand zwischen Elementen)

| Kontext                         | Wert  | Token |
|---------------------------------|-------|-------|
| Label -> Input                  | 6px   | —     |
| Formular-Zeilen (Detail)        | 20px  | —     |
| Pruefpunkte nebeneinander       | 40px  | 3xl   |
| Dropdown-Zeile Spacing          | 12px  | md    |
| Seitenabschnitte (Auftraege)    | 16px  | lg    |
| Settings Sektionen              | 16px  | lg    |
| Dialog Header-Spacing           | 12px  | md    |
| Dialog Button-Spacing           | 12px  | md    |

Formular-Spacing ist bewusst kompakt (16-20px), damit bei wachsender Anzahl
von Optionen (besonders in den Settings) genug Platz bleibt.

---

## 2. Typografie

Primaerschrift: **Inter** (Regular, Medium, SemiBold, Bold)
Akzentschrift: **Plus Jakarta Sans** (SemiBold) — nur fuer Titel

### Typografie-Skala (6 Stufen)

| Stufe        | Groesse | Gewicht | Schriftart        | Verwendung                     |
|--------------|---------|---------|-------------------|---------------------------------|
| Seitentitel  | 22px    | 600     | Plus Jakarta Sans | Hauptseiten-Titel               |
| Detail-Titel | 20px    | 600     | Plus Jakarta Sans | Detail-Seiten-Ueberschrift      |
| Sektion      | 16px    | 600     | Plus Jakarta Sans | Settings-Titel, Dialog-Titel, Logo-Text |
| Gruppe       | 14px    | 600     | Inter             | Formular-Gruppen, Gruppen-Titel |
| Body/Input   | 13px    | 500     | Inter             | Eingabefelder, Buttons          |
| Label        | 12px    | 500     | Inter             | Feldbezeichnungen, Sidebar, Header |
| Caption      | 11px    | 400     | Inter             | Fehlermeldungen, Hinweise       |

### Regeln

- **Seitentitel** bekommen eine 2px rote Unterlinie (`indicator`-Farbe)
- **Gruppen-Titel** haben keine Unterlinie, nur Gewicht 600 bei 14px
- **Labels** sind `text_sekundaer`, **Inputs** sind `text_primaer`
- **Fehlermeldungen** sind immer `fehler`-Farbe, 11px
- **Logo-Text** "Pruefpilot" ist 16px Bold Inter (Sidebar)

---

## 3. Komponenten-Groessen

### Touch-Targets & Interaktive Elemente

Minimum-Hoehe fuer klickbare Elemente: **36px** (Desktop-Standard)
Einheitliche Input-Hoehe: **36px** (alle Inputs, Dropdowns, Settings-Felder)

| Komponente                  | Hoehe | Breite          |
|-----------------------------|-------|-----------------|
| Title-Bar-Button            | 32px  | 36px            |
| Sidebar-Button              | 44px  | variabel        |
| Dropdown (Auftraege)        | 36px  | min 200/350px   |
| Dropdown (Formular)         | 36px  | min 300px       |
| Formular-Input              | 36px  | 140px (fest)    |
| Primary Button              | 42px  | min 160px       |
| Secondary Button            | 36px  | min 100px       |
| Dialog Button               | 36px  | min 100px       |
| Settings Tab-Button         | 40px  | volle Breite    |
| Settings Input              | 36px  | variabel        |
| PDF-Feedback-Button         | 40px  | 40px            |
| Infobox Close-Button        | 22px  | 22px (nur X)    |

### Tabelle

| Element             | Wert   |
|---------------------|--------|
| Zeilenhoehe         | 40px   |
| Header-Padding      | 8/10px |
| Status-Icon-Groesse | 20x20px|
| Status-Spalten      | 60px   |
| Text-Spalten        | 120-150px, Modell: stretch |

### Overlay & Dialoge

| Element             | Wert                         |
|---------------------|------------------------------|
| Dialog Breite       | 420px (fest)                 |
| Dialog Max-Hoehe    | 300px                        |
| Settings Breite     | 75% Fenster, max 750px       |
| Settings Hoehe      | 80% Fenster, max 550px       |
| Settings Tab-Panel  | 180px (fest)                 |

---

## 4. Border-Radius

Drei Stufen fuer konsistente Rundungen:

| Stufe       | Radius | Verwendung                                      |
|-------------|--------|--------------------------------------------------|
| Klein       | 4px    | Infobox-Close, kleine Akzente                    |
| Standard    | 6px    | Buttons, Inputs, Dropdowns, Tooltips, Sidebar    |
| Gross       | 8px    | Dropdown-Popup, Infobox, Theme-Option            |
| Container   | 14px   | Content-Bereich, Detail-Seite, Settings, Dialog  |
| Fenster     | 10px   | Aeusseres Fenster, Title Bar                     |

### Regeln

- **Interaktive Elemente** (Buttons, Inputs): immer 6px
- **Container** (Panels, Overlays): immer 14px
- **Fenster-Ecken**: 10px (via QPainterPath Mask)
- Scrollbar-Handle: 3px (schmal, dezent)

---

## 5. Padding

### Input-Felder & Buttons

| Komponente        | Vertikal | Horizontal |
|-------------------|----------|------------|
| Formular-Input    | 8px      | 12px       |
| Formular-Dropdown | 8px      | 12px       |
| TextArea          | 8px      | 12px       |
| Primary Button    | 8px      | 20px       |
| Secondary Button  | 8px      | 20px       |
| Browse Button     | 6px      | 14px       |
| Tooltip           | 8px      | 12px       |

### Konsistenz-Regel

- **Alle Eingabefelder**: 8px vertikal, 12px horizontal
- **Alle Buttons**: 8px vertikal, 20px horizontal (primaer/sekundaer)
- **Kleine Buttons** (Browse, Add): 6px vertikal, 14px horizontal

---

## 6. Schatten & Visuelle Tiefe

| Element          | Blur | Offset  | Farbe         | Verwendung           |
|------------------|------|---------|---------------|----------------------|
| Content-Bereich  | 20px | 0, 2px  | rgba(0,0,0,80)| Abhebung vom Rahmen  |
| Dimm-Overlay     | —    | —       | rgba(0,0,0,100)| Detail-Hintergrund  |
| Dialog-Overlay   | —    | —       | rgba(0,0,0,120)| Dialog-Hintergrund  |

---

## 7. Animationen

| Animation              | Dauer | Easing       | Verwendung                |
|------------------------|-------|--------------|---------------------------|
| Seitenwechsel          | 200ms | OutCubic     | Content-Fade + 16px Slide |
| Sidebar Ein/Aus        | 200ms | InOutCubic   | Sidebar-Breite aendern    |
| Overlay Ein             | 150ms | OutCubic     | Detail/Settings oeffnen   |
| Dialog Ein              | 150ms | OutCubic     | Dialog-Fade               |
| Zeilen-Hover (Tabelle) | ~96ms | Linear (6 Schritte a 16ms) | Sanftes Hover-Fade |
| Zeilen-Stagger         | 30ms  | —            | Verzoegerung pro Zeile    |

### Regeln

- **Seitenwechsel**: immer 200ms (nicht zu schnell, nicht traege)
- **Overlays**: immer 150ms (schneller, reaktiv)
- **Slide-Distanz**: immer 16px
- Kein `Linear` fuer UI-Elemente — immer `OutCubic` oder `InOutCubic`

---

## 8. Responsive-Verhalten

| Schwelle   | Verhalten                                        |
|------------|--------------------------------------------------|
| < 600px    | Pruefpunkte wechseln von zweispaltig zu einspaltig|
| 800x500px  | Fenster-Mindestgroesse                           |
| > 1000px   | Volle zweispaltige Darstellung                   |

---

## 9. Icon-System

**Bibliothek:** qtawesome mit **Remix Icon** (`ri.*`) — https://remixicon.com/
**Konvention:** Outline-Varianten (`-line`) als Standard, Filled (`-fill`) nur fuer aktive/erledigte Zustaende.
**Kein `mdi6.*`** — alle Icons verwenden ausschliesslich den `ri.*`-Prefix.

### Icon-Groessen

| Kontext         | Groesse | Verwendung                    |
|-----------------|---------|-------------------------------|
| Title-Bar       | 16x16px | Window Controls, Toggle       |
| Sidebar         | 22x22px | Navigations-Icons             |
| Settings Tab    | 18x18px | Reiter-Icons                  |
| Tabelle Status  | 20x20px | Temp/VDE Status-Icons         |
| PDF-Button      | 18x18px | Printer-Icon im Button        |
| PDF-Feedback    | 24x24px | Gruenes Check-Icon            |
| Dialog          | 24x24px | Typ-Icon (Warnung/Fehler/etc) |
| Info-Tooltip    | 14x14px | Info-Icon neben Labels        |
| Infobox         | 18x18px | Info-Icon links               |

### Farb-Regeln fuer Icons

- **Inaktiv/Neutral**: `icon_farbe` (text_sekundaer)
- **Aktiv/Ausgewaehlt**: `text_aktiv`
- **Status erledigt**: `erfolg` (gruen)
- **Status offen**: `fehler` (rot)
- **Info-Icons**: `info` (blau)
- **Buttons (weiss)**: immer `#ffffff` auf Akzent-Hintergrund

---

## 10. Fenster-Struktur

```
┌─────────────────────────────────────────────────┐ ← 10px Radius
│  Title Bar (38px)  [Toggle]    [☀][─][□][✕]     │
├──────┬──────────────────────────────────────────┤
│      │                                    ┌────┐│
│  S   │   Content-Bereich (14px Radius)    │    ││
│  i   │                                    │6px ││ ← Margin rechts
│  d   │   Margins: 32/24/32/24 (Seiten)    │    ││
│  e   │             40/32/40/24 (Detail)    │    ││
│  b   │                                    └────┘│
│  a   │                                          │
│  r   │                                    ┌────┐│
│(52px)│                                    │6px ││ ← Margin unten
│      │                                    └────┘│
└──────┴──────────────────────────────────────────┘
```

---

## Zusammenfassung: Goldene Regeln

1. **8px-Grid**: Alle Abstaende in Vielfachen von 4px/8px
2. **3 Radien**: 6px (Elemente), 14px (Container), 10px (Fenster)
3. **Einheitliches Padding**: 8/12px fuer Inputs, 8/20px fuer Buttons
4. **Einheitliche Input-Hoehe**: 36px fuer alle Inputs und Dropdowns
5. **Touch-Target**: Mindestens 36px Hoehe fuer klickbare Elemente
6. **Animationen**: 150ms (Overlays), 200ms (Seitenwechsel), OutCubic
7. **Typografie**: 6 Stufen (22/20/16/14/13/12/11px)
8. **Icons**: 4 Groessen (14/16/18-20/22-24px je nach Kontext)
9. **Kompaktes Spacing**: 16px in Settings/Auftraege, 20px in Detail-Formularen
