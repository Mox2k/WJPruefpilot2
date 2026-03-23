import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFontDatabase, QFont
from ui.main_window import MainWindow


def _lade_schriftart():
    """Laedt die Inter-Schriftart aus dem assets/fonts-Ordner."""
    if getattr(sys, 'frozen', False):
        basis = sys._MEIPASS
    else:
        basis = os.path.dirname(os.path.abspath(__file__))

    fonts_pfad = os.path.join(basis, "assets", "fonts")
    for datei in ["Inter-Regular.ttf", "Inter-Medium.ttf",
                   "Inter-SemiBold.ttf", "Inter-Bold.ttf",
                   "PlusJakartaSans-SemiBold.ttf"]:
        pfad = os.path.join(fonts_pfad, datei)
        if os.path.exists(pfad):
            QFontDatabase.addApplicationFont(pfad)


def main():
    """Hauptfunktion zum Starten der Anwendung."""
    app = QApplication(sys.argv)
    app.setApplicationName("WJPruefpilot")

    _lade_schriftart()
    app.setFont(QFont("Inter", 10))

    fenster = MainWindow()
    fenster.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
