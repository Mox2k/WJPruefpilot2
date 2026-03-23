"""Zentrale Stylesheet-Definitionen fuer die Anwendung.

Alle Farben sind hier zentral definiert und leicht aenderbar.
Dark und Light Theme als separate Dictionaries.
"""

# --- Farbpaletten ---

FARBEN_DARK = {
    # Basis-Toene (blauliches Anthrazit, aufgehellt)
    "basis": "#2c3245",            # Title Bar + Sidebar
    "basis_hell": "#363d52",       # Content-Bereich (abgehoben)
    "hover_bg": "#3a4158",         # Hover-Zustand
    "aktiv_bg": "#343b50",         # Aktiver Sidebar-Button
    "border": "#3a4158",           # Trennlinien

    # Text
    "text_primaer": "#e0e0e0",
    "text_sekundaer": "#8a8fa0",
    "text_aktiv": "#ffffff",

    # Akzent (nur Buttons)
    "akzent": "#ed1b24",
    "akzent_hover": "#d41920",
    "akzent_pressed": "#b8151c",

    # Window Controls
    "icon_farbe": "#8a8fa0",
    "close_hover_bg": "#ed1b24",

    # Status-Farben
    "erfolg": "#4caf50",
    "warnung": "#ff9800",
    "fehler": "#f44336",
    "info": "#42a5f5",

    # Sidebar Active-Indicator
    "indicator": "#ed1b24",
}

FARBEN_LIGHT = {
    # Basis-Toene (sehr helles Grau)
    "basis": "#f0f0f0",            # Title Bar + Sidebar
    "basis_hell": "#f7f7f7",       # Content-Bereich (dezent heller)
    "hover_bg": "#e4e4e4",         # Hover-Zustand
    "aktiv_bg": "#e0e0e0",         # Aktiver Sidebar-Button
    "border": "#e0e0e0",           # Trennlinien

    # Text
    "text_primaer": "#1a1a1a",
    "text_sekundaer": "#6b6b6b",
    "text_aktiv": "#1a1a1a",

    # Akzent (nur Buttons)
    "akzent": "#ed1b24",
    "akzent_hover": "#d41920",
    "akzent_pressed": "#b8151c",

    # Window Controls
    "icon_farbe": "#6b6b6b",
    "close_hover_bg": "#ed1b24",

    # Status-Farben
    "erfolg": "#388e3c",
    "warnung": "#f57c00",
    "fehler": "#d32f2f",
    "info": "#1976d2",

    # Sidebar Active-Indicator
    "indicator": "#ed1b24",
}


def generiere_stylesheet(farben: dict) -> str:
    """Erzeugt das komplette Stylesheet basierend auf einer Farbpalette."""
    return f"""
    /* Aeusseres Widget (abgerundete Ecken) */
    QWidget#aussenWidget {{
        background-color: {farben["basis"]};
        border-radius: 8px;
    }}

    /* Title Bar */
    QWidget#titleBar {{
        background-color: {farben["basis"]};
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}

    QLabel#titleLabel {{
        color: {farben["text_sekundaer"]};
        font-size: 12px;
        font-weight: normal;
    }}

    QPushButton#titleButton {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
    }}
    QPushButton#titleButton:hover {{
        background-color: {farben["hover_bg"]};
    }}

    QPushButton#titleButtonClose {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
    }}
    QPushButton#titleButtonClose:hover {{
        background-color: {farben["close_hover_bg"]};
    }}

    /* Sidebar */
    QWidget#sidebar {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {farben["basis"]}, stop:1 {farben["aktiv_bg"]}
        );
        border-bottom-left-radius: 8px;
    }}

    QPushButton#sidebarToggle {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: {farben["text_sekundaer"]};
        text-align: left;
        padding-left: 10px;
        font-size: 13px;
    }}
    QPushButton#sidebarToggle:hover {{
        background-color: {farben["hover_bg"]};
    }}

    QPushButton#sidebarButton {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: {farben["text_sekundaer"]};
        text-align: left;
        padding-left: 10px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton#sidebarButton:hover {{
        background-color: {farben["hover_bg"]};
    }}
    QPushButton#sidebarButton[aktiv="true"] {{
        background-color: {farben["aktiv_bg"]};
        color: {farben["text_aktiv"]};
    }}

    /* Hauptbereich */
    QWidget#hauptbereich {{
        background-color: {farben["basis"]};
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
    }}

    /* Content-Container (Margin um Content) */
    QWidget#contentContainer {{
        background-color: {farben["basis"]};
        border-bottom-right-radius: 8px;
    }}

    /* Content-Bereich */
    QStackedWidget#contentStack {{
        background-color: {farben["basis_hell"]};
        border-radius: 14px;
    }}

    QWidget#contentSeite {{
        background-color: transparent;
    }}

    QLabel#seitenTitel {{
        color: {farben["text_primaer"]};
        font-family: "Plus Jakarta Sans";
        font-size: 22px;
        font-weight: 600;
        padding: 0px;
        padding-bottom: 12px;
        border-bottom: 2px solid {farben["indicator"]};
    }}

    /* Detail-Seite Header */
    QLabel#detailSeitenTitel {{
        color: {farben["text_primaer"]};
        font-family: "Plus Jakarta Sans";
        font-size: 20px;
        font-weight: 600;
        padding: 0px;
    }}

    QLabel#detailWaagenInfo {{
        color: {farben["text_sekundaer"]};
        font-size: 13px;
        font-weight: 500;
        padding-bottom: 8px;
    }}

    /* Gestrichelte Gruppen-Trennlinie */
    QFrame#gruppenTrennlinie {{
        border: none;
        border-top: 1px dashed {farben["border"]};
        max-height: 1px;
        margin-top: 4px;
        margin-bottom: 4px;
    }}

    /* Auftrag-Label */
    QLabel#auftragLabel {{
        color: {farben["text_sekundaer"]};
        font-size: 13px;
    }}

    /* Auftrags-Dropdown */
    QComboBox#auftragDropdown {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid {farben["border"]};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: bold;
        outline: none;
    }}
    QComboBox#auftragDropdown:hover {{
        border-color: {farben["text_sekundaer"]};
    }}
    QComboBox#auftragDropdown:focus {{
        border: 1px solid {farben["border"]};
        outline: none;
    }}
    QComboBox#auftragDropdown:on {{
        border: 1px solid {farben["border"]};
    }}
    QComboBox#auftragDropdown::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox#auftragDropdown::down-arrow {{
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: none;
        border-radius: 8px;
        outline: none;
        selection-background-color: {farben["hover_bg"]};
        selection-color: {farben["text_aktiv"]};
        padding: 4px;
        font-size: 12px;
        font-weight: bold;
    }}
    QComboBox QAbstractItemView::item {{
        border: none;
        border-radius: 6px;
        outline: none;
        padding: 6px 10px;
        margin: 2px 4px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {farben["hover_bg"]};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {farben["hover_bg"]};
    }}

    /* Waagentabelle */
    QTableWidget#waageTabelle {{
        background-color: {farben["basis_hell"]};
        color: {farben["text_primaer"]};
        border: none;
        font-size: 12px;
        font-weight: 500;
        outline: none;
    }}
    QTableWidget#waageTabelle::item {{
        border: none;
        outline: none;
    }}
    QTableWidget#waageTabelle::item:focus {{
        border: none;
        outline: none;
    }}
    QHeaderView::section {{
        background-color: {farben["basis_hell"]};
        color: {farben["text_sekundaer"]};
        border: none;
        border-bottom: 1px solid {farben["border"]};
        padding: 8px 10px;
        font-size: 12px;
        font-weight: bold;
    }}
    QHeaderView::section:hover {{
        color: {farben["text_primaer"]};
    }}

    /* Primaere Buttons (Akzentfarbe) */
    QPushButton#primaryButton {{
        background-color: {farben["akzent"]};
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {farben["akzent_hover"]};
    }}
    QPushButton#primaryButton:pressed {{
        background-color: {farben["akzent_pressed"]};
    }}

    /* Sekundaere Buttons */
    QPushButton#secondaryButton {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid {farben["border"]};
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton#secondaryButton:hover {{
        background-color: {farben["hover_bg"]};
    }}

    /* Detail-Seite */
    QWidget#detailSeite {{
        background-color: {farben["basis_hell"]};
        border-radius: 14px;
    }}

    QLabel#detailTitel {{
        color: {farben["text_primaer"]};
        font-family: "Plus Jakarta Sans";
        font-size: 20px;
        font-weight: 600;
    }}

    QLabel#detailSubtitel {{
        color: {farben["text_sekundaer"]};
        font-size: 14px;
        padding-top: 4px;
    }}

    QWidget#detailScrollInhalt {{
        background: transparent;
    }}

    QWidget#detailAktionszeile {{
        background: transparent;
    }}

    QFrame#detailTrennlinie {{
        color: {farben["border"]};
        max-height: 1px;
    }}

    /* Radio-Buttons */
    QRadioButton {{
        color: {farben["text_primaer"]};
        font-size: 13px;
        spacing: 8px;
    }}
    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 2px solid {farben["text_sekundaer"]};
        border-radius: 8px;
        background: transparent;
    }}
    QRadioButton::indicator:checked {{
        border-color: {farben["akzent"]};
        background-color: {farben["akzent"]};
    }}
    QRadioButton::indicator:hover {{
        border-color: {farben["akzent"]};
    }}

    /* Checkboxen (Settings) */
    QCheckBox {{
        color: {farben["text_primaer"]};
        font-size: 13px;
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {farben["text_sekundaer"]};
        border-radius: 4px;
        background: transparent;
    }}
    QCheckBox::indicator:checked {{
        border-color: {farben["erfolg"]};
        background-color: {farben["erfolg"]};
    }}
    QCheckBox::indicator:hover {{
        border-color: {farben["erfolg"]};
    }}

    /* Formular-Elemente */
    QLabel#formLabel {{
        color: {farben["text_sekundaer"]};
        font-size: 12px;
        font-weight: 500;
    }}

    QLabel#formGruppenTitel {{
        color: {farben["text_primaer"]};
        font-size: 14px;
        font-weight: 600;
    }}

    QLabel#formEinheit {{
        color: {farben["text_sekundaer"]};
        font-size: 12px;
        padding-top: 4px;
    }}

    QLabel#formFehler {{
        color: {farben["fehler"]};
        font-size: 11px;
    }}

    QLineEdit#formInput {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QLineEdit#formInput:focus {{
        border-color: {farben["text_sekundaer"]};
    }}
    QLineEdit#formInputFehler {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid {farben["fehler"]};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QLineEdit#formInputFehler:focus {{
        border-color: {farben["fehler"]};
    }}

    QTextEdit#formTextArea {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QTextEdit#formTextArea:focus {{
        border-color: {farben["text_sekundaer"]};
    }}

    QComboBox#formDropdown {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 500;
    }}
    QComboBox#formDropdown:hover {{
        border-color: {farben["text_sekundaer"]};
    }}
    QComboBox#formDropdown::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox#formDropdown QAbstractItemView {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: none;
        border-radius: 6px;
        outline: none;
        selection-background-color: {farben["hover_bg"]};
        padding: 4px;
        font-size: 13px;
    }}

    /* Scrollbereiche transparent */
    QScrollArea#detailScroll {{
        background: transparent;
        border: none;
    }}
    QScrollArea#detailScroll > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        width: 6px;
        background: transparent;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(128, 128, 128, 60);
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid {farben["border"]};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }}

    /* Settings-Overlay */
    QWidget#settingsOverlay {{
        background-color: {farben["basis_hell"]};
        border-radius: 14px;
    }}

    QWidget#settingsTabPanel {{
        background-color: {farben["basis"]};
        border-top-left-radius: 14px;
        border-bottom-left-radius: 14px;
    }}

    QPushButton#settingsTabButton {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: {farben["text_sekundaer"]};
        text-align: left;
        padding-left: 10px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton#settingsTabButton:hover {{
        background-color: {farben["hover_bg"]};
    }}
    QPushButton#settingsTabButton[aktiv="true"] {{
        background-color: {farben["aktiv_bg"]};
        color: {farben["text_aktiv"]};
    }}

    QWidget#settingsContent {{
        background-color: {farben["basis_hell"]};
        border-top-right-radius: 14px;
        border-bottom-right-radius: 14px;
    }}

    QLabel#settingsSectionTitel {{
        color: {farben["text_primaer"]};
        font-family: "Plus Jakarta Sans";
        font-size: 16px;
        font-weight: 600;
    }}

    QLabel#settingsLabel {{
        color: {farben["text_sekundaer"]};
        font-size: 12px;
        font-weight: 500;
    }}

    QLineEdit#settingsInput {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QLineEdit#settingsInput:focus {{
        border-color: {farben["text_sekundaer"]};
    }}

    QPushButton#settingsBrowseButton {{
        background-color: {farben["basis"]};
        color: {farben["text_primaer"]};
        border: 1px solid {farben["border"]};
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
    }}
    QPushButton#settingsBrowseButton:hover {{
        background-color: {farben["hover_bg"]};
    }}

    QPushButton#settingsAddButton {{
        background-color: transparent;
        color: {farben["text_sekundaer"]};
        border: 1px dashed {farben["border"]};
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
    }}
    QPushButton#settingsAddButton:hover {{
        background-color: {farben["hover_bg"]};
        color: {farben["text_primaer"]};
    }}

    QPushButton#settingsRemoveButton {{
        background-color: transparent;
        color: {farben["text_sekundaer"]};
        border: none;
        border-radius: 6px;
        padding: 4px;
    }}
    QPushButton#settingsRemoveButton:hover {{
        background-color: {farben["hover_bg"]};
        color: {farben["fehler"]};
    }}

    QLabel#settingsImagePreview {{
        background-color: {farben["basis"]};
        border: 1px solid {farben["border"]};
        border-radius: 6px;
        padding: 4px;
    }}

    QWidget#settingsThemeOption {{
        background-color: {farben["basis"]};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 12px;
    }}
    QWidget#settingsThemeOption[aktiv="true"] {{
        border-color: {farben["akzent"]};
    }}

    QFrame#settingsTrennlinie {{
        color: {farben["border"]};
        max-height: 1px;
    }}
"""
