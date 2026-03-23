"""Custom Title Bar mit Toggle, Theme-Switch und Window-Controls."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
import qtawesome as qta


class TitleBar(QWidget):
    """Eigene Titelleiste: Toggle links, Theme-Switch + Window-Controls rechts."""

    minimieren_geklickt = Signal()
    maximieren_geklickt = Signal()
    schliessen_geklickt = Signal()
    toggle_geklickt = Signal()
    theme_geklickt = Signal()

    HOEHE = 38

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(self.HOEHE)
        self._ist_dark = True
        self._icon_farbe = "#8a8fa0"
        self._erstelle_ui()

    def _erstelle_ui(self):
        """Baut die Title Bar auf."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(2)

        btn_groesse = QSize(36, self.HOEHE - 6)
        icon_groesse = QSize(16, 16)

        # Toggle-Button (Hamburger) -- ganz links
        self._btn_toggle = QPushButton()
        self._btn_toggle.setObjectName("titleButton")
        self._btn_toggle.setIcon(qta.icon("ri.side-bar-line", color=self._icon_farbe))
        self._btn_toggle.setIconSize(icon_groesse)
        self._btn_toggle.setFixedSize(btn_groesse)
        self._btn_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_toggle.clicked.connect(self.toggle_geklickt.emit)
        layout.addWidget(self._btn_toggle)

        # Stretch -- drueckt alles Folgende nach rechts
        layout.addStretch()

        # Theme-Toggle (Sonne/Mond)
        self._btn_theme = QPushButton()
        self._btn_theme.setObjectName("titleButton")
        self._btn_theme.setIcon(
            qta.icon("ri.sun-line", color=self._icon_farbe)
        )
        self._btn_theme.setIconSize(icon_groesse)
        self._btn_theme.setFixedSize(btn_groesse)
        self._btn_theme.setCursor(Qt.PointingHandCursor)
        self._btn_theme.clicked.connect(self.theme_geklickt.emit)
        layout.addWidget(self._btn_theme)

        # Minimieren
        self._btn_minimieren = QPushButton()
        self._btn_minimieren.setObjectName("titleButton")
        self._btn_minimieren.setIcon(
            qta.icon("ri.subtract-line", color=self._icon_farbe)
        )
        self._btn_minimieren.setIconSize(icon_groesse)
        self._btn_minimieren.setFixedSize(btn_groesse)
        self._btn_minimieren.clicked.connect(self.minimieren_geklickt.emit)
        layout.addWidget(self._btn_minimieren)

        # Maximieren
        self._btn_maximieren = QPushButton()
        self._btn_maximieren.setObjectName("titleButton")
        self._btn_maximieren.setIcon(
            qta.icon("ri.checkbox-blank-line", color=self._icon_farbe, scale_factor=0.65)
        )
        self._btn_maximieren.setIconSize(icon_groesse)
        self._btn_maximieren.setFixedSize(btn_groesse)
        self._btn_maximieren.clicked.connect(self.maximieren_geklickt.emit)
        layout.addWidget(self._btn_maximieren)

        # Schliessen
        self._btn_schliessen = QPushButton()
        self._btn_schliessen.setObjectName("titleButtonClose")
        self._btn_schliessen.setIcon(
            qta.icon("ri.close-line", color=self._icon_farbe)
        )
        self._btn_schliessen.setIconSize(icon_groesse)
        self._btn_schliessen.setFixedSize(btn_groesse)
        self._btn_schliessen.clicked.connect(self.schliessen_geklickt.emit)
        layout.addWidget(self._btn_schliessen)

    def aktualisiere_maximieren_icon(self, ist_maximiert: bool):
        """Wechselt das Maximieren-Icon zwischen Normal und Restore."""
        if ist_maximiert:
            self._btn_maximieren.setIcon(
                qta.icon("ri.window-2-line", color=self._icon_farbe, scale_factor=0.7)
            )
        else:
            self._btn_maximieren.setIcon(
                qta.icon("ri.checkbox-blank-line", color=self._icon_farbe, scale_factor=0.7)
            )

    def aktualisiere_theme_icons(self, ist_dark: bool, icon_farbe: str):
        """Aktualisiert alle Icons mit der neuen Theme-Farbe."""
        self._ist_dark = ist_dark
        self._icon_farbe = icon_farbe

        # Theme-Button: Sonne im Dark Mode (-> wechsle zu Light), Mond im Light Mode
        if ist_dark:
            self._btn_theme.setIcon(
                qta.icon("ri.sun-line", color=icon_farbe)
            )
        else:
            self._btn_theme.setIcon(
                qta.icon("ri.moon-line", color=icon_farbe)
            )

        self.aktualisiere_sidebar_icon(getattr(self, '_sidebar_offen', False))
        self._btn_minimieren.setIcon(qta.icon("ri.subtract-line", color=icon_farbe))
        self._btn_schliessen.setIcon(qta.icon("ri.close-line", color=icon_farbe))
        self.aktualisiere_maximieren_icon(False)

    def aktualisiere_sidebar_icon(self, ist_offen: bool):
        """Wechselt das Sidebar-Icon zwischen line (zu) und fill (offen)."""
        self._sidebar_offen = ist_offen
        icon_name = "ri.side-bar-fill" if ist_offen else "ri.side-bar-line"
        self._btn_toggle.setIcon(qta.icon(icon_name, color=self._icon_farbe))

    def mouseDoubleClickEvent(self, event):
        """Doppelklick auf Title Bar maximiert/wiederherstellt das Fenster."""
        if event.button() == Qt.LeftButton:
            self.maximieren_geklickt.emit()
