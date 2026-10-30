"""Simple background image widget used behind the main app UI."""

import os

from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class GeoBackground(QWidget):
    def __init__(self, parent=None, image_path=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.image_path = image_path
        self._bg_label = QLabel(self)
        self._bg_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._bg_label.setStyleSheet("background: transparent;")
        self._bg_label.setAlignment(Qt.AlignCenter)

        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.35)
        self._bg_label.setGraphicsEffect(effect)

        self._bg_label.hide()

        if self.image_path:
            self._apply_background_image()

    def _apply_background_image(self):
        if not self.image_path or not os.path.exists(self.image_path):
            self._bg_label.hide()
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self._bg_label.hide()
            return

        scaled = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self._bg_label.setPixmap(scaled)
        self._bg_label.setGeometry(0, 0, self.width(), self.height())
        self._bg_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_path and os.path.exists(self.image_path):
            self._apply_background_image()

    def paintEvent(self, event):
        # no drawing, only the image shows
        pass
