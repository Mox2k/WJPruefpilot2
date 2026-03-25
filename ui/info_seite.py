"""Info-Seite mit App-Version, Copyright, Kontakt und Lizenzen."""

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt

from version import __version__


class InfoSeite(QWidget):
    """Info-Seite mit App-Informationen, Copyright und verwendeten Bibliotheken."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contentSeite")
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut die Info-Seite auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Titel
        titel = QLabel("Info")
        titel.setObjectName("seitenTitel")
        layout.addWidget(titel)

        # Scrollbereich
        scroll = QScrollArea()
        scroll.setObjectName("detailScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        inhalt = QWidget()
        inhalt.setObjectName("contentSeite")
        inhalt_layout = QVBoxLayout(inhalt)
        inhalt_layout.setContentsMargins(0, 0, 0, 0)
        inhalt_layout.setSpacing(12)

        # App-Name + Version
        app_label = QLabel(f"WJPruefpilot  v{__version__}")
        app_label.setObjectName("detailSeitenTitel")
        inhalt_layout.addWidget(app_label)

        # Copyright
        jahr = date.today().year
        copyright_label = QLabel(f"\u00a9 {jahr} Waagen-J\u00f6hnk KG. Alle Rechte vorbehalten.")
        copyright_label.setObjectName("formLabel")
        inhalt_layout.addWidget(copyright_label)

        inhalt_layout.addSpacing(8)
        inhalt_layout.addWidget(self._trennlinie())

        # Kontakt & Support
        kontakt_titel = QLabel("Kontakt & Support")
        kontakt_titel.setObjectName("formGruppenTitel")
        inhalt_layout.addWidget(kontakt_titel)

        kontakt_text = QLabel(
            "Waagen-J\u00f6hnk KG\n"
            "info@waagen-joehnk.de"
        )
        kontakt_text.setObjectName("formLabel")
        kontakt_text.setWordWrap(True)
        inhalt_layout.addWidget(kontakt_text)

        inhalt_layout.addSpacing(8)
        inhalt_layout.addWidget(self._trennlinie())

        # Verwendete Bibliotheken
        lib_titel = QLabel("Verwendete Bibliotheken")
        lib_titel.setObjectName("formGruppenTitel")
        inhalt_layout.addWidget(lib_titel)

        bibliotheken = [
            ("PySide6", "Qt for Python", "LGPL v3"),
            ("xhtml2pdf", "HTML-zu-PDF-Konvertierung", "Apache License 2.0"),
            ("matplotlib", "Diagrammerstellung", "PSF License"),
            ("Pillow", "Bildverarbeitung", "HPND License"),
            ("qtawesome", "Icon-Integration", "MIT License"),
            ("Remix Icon", "Icon-Bibliothek", "Apache License 2.0"),
        ]

        for name, beschreibung, lizenz in bibliotheken:
            zeile = QLabel(f"{name}  \u2014  {beschreibung}  ({lizenz})")
            zeile.setObjectName("formLabel")
            zeile.setWordWrap(True)
            inhalt_layout.addWidget(zeile)

        inhalt_layout.addStretch()
        scroll.setWidget(inhalt)
        layout.addWidget(scroll)

    def _trennlinie(self):
        """Erstellt eine gestrichelte Trennlinie."""
        linie = QFrame()
        linie.setObjectName("gruppenTrennlinie")
        linie.setFrameShape(QFrame.HLine)
        return linie

    def aktualisiere_theme(self, farben):
        """Aktualisiert Farben bei Theme-Wechsel."""
        # Styling wird komplett ueber styles.py gesteuert (ObjectNames)
        pass
