"""Wiederverwendbare Custom-Widgets mit Animationen."""

from PySide6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QPointF, QRectF
)
from PySide6.QtGui import QPainter, QTransform


class AnimatedButton(QPushButton):
    """Primary Button mit Scale-Down-Feedback beim Klick.

    Verwendung:
        btn = AnimatedButton("PDF erstellen")
        btn.setObjectName("primaryButton")
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._scale = 1.0
        self._ziel_scale = 1.0
        self._anim = None

    def mousePressEvent(self, event):
        """Scale-Down beim Druecken."""
        if event.button() == Qt.LeftButton:
            self._animiere_scale(0.96)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Scale zurueck beim Loslassen."""
        if event.button() == Qt.LeftButton:
            self._animiere_scale(1.0)
        super().mouseReleaseEvent(event)

    def _animiere_scale(self, ziel: float):
        """Animiert den Scale-Faktor."""
        self._ziel_scale = ziel
        # Direkte Animation ueber Timer-Steps (schnell, 80ms)
        schritte = 4
        schritt_wert = (ziel - self._scale) / schritte
        self._scale_schritte = schritte
        self._scale_delta = schritt_wert
        self._scale_tick()

    def _scale_tick(self):
        """Ein Animations-Schritt fuer Scale."""
        self._scale += self._scale_delta
        self._scale_schritte -= 1
        if self._scale_schritte <= 0:
            self._scale = self._ziel_scale
        self.update()
        if self._scale_schritte > 0:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(16, self._scale_tick)

    def paintEvent(self, event):
        """Zeichnet den Button mit aktuellem Scale-Faktor."""
        if abs(self._scale - 1.0) < 0.001:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Transformation: Skalierung um Mittelpunkt
        mitte = QPointF(self.width() / 2, self.height() / 2)
        transform = QTransform()
        transform.translate(mitte.x(), mitte.y())
        transform.scale(self._scale, self._scale)
        transform.translate(-mitte.x(), -mitte.y())
        painter.setTransform(transform)

        # Widget normal rendern mit Transformation
        painter.end()

        # QPushButton mit Transformation zeichnen
        super().paintEvent(event)
