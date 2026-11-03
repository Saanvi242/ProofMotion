"""Scrubbable transform-history filmstrip for Studio 2D / 3D."""

from typing import List, Optional, Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from resources.theme import get_mono_font, get_ui_font


class StudioFilmstrip(QWidget):
    frameChanged = pyqtSignal(int, float)  # op_index, t in [0, 1]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioFilmstrip")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(72)
        self.setCursor(Qt.PointingHandCursor)
        self._frames: List[Tuple[str, int]] = [("Pose", -1)]
        self._index = -1
        self._t = 1.0
        self._cells: List[QRectF] = []
        self._drag_i: Optional[int] = None

    def bind(self, obj) -> None:
        frames: List[Tuple[str, int]] = [("Pose", -1)]
        hist = getattr(obj, "history", None) or []
        for i, op in enumerate(hist):
            label = getattr(op, "label", None) or getattr(op, "kind", f"op {i + 1}")
            frames.append((str(label), i))
        self._frames = frames
        if self._index >= len(hist):
            self._index = len(hist) - 1 if hist else -1
            self._t = 1.0
        self.update()

    def set_playhead(self, op_index: int, t: float = 1.0) -> None:
        self._index = int(op_index)
        self._t = max(0.0, min(1.0, float(t)))
        self.update()

    def playhead(self) -> Tuple[int, float]:
        return self._index, self._t

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())
        painter.fillRect(self.rect(), QColor("#07080D"))
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0C1018")))
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 14.0, 14.0)

        painter.setFont(get_ui_font(10, weight=700))
        painter.setPen(QPen(QColor("#5EEAD4")))
        painter.drawText(QRectF(14, 8, 70, 14), Qt.AlignLeft | Qt.AlignVCenter, "FILM")

        n = max(1, len(self._frames))
        margin_l, margin_r, top = 14.0, 14.0, 26.0
        gap = 6.0
        avail = max(40.0, w - margin_l - margin_r)
        cell_w = min(132.0, max(56.0, (avail - gap * (n - 1)) / n))
        cell_h = 36.0
        x = margin_l
        self._cells = []
        for i, (label, op_index) in enumerate(self._frames):
            rect = QRectF(x, top, cell_w, cell_h)
            self._cells.append(rect)
            active = op_index == self._index
            if active:
                painter.setBrush(QBrush(QColor("#5EEAD4")))
                painter.setPen(QPen(QColor("#5EEAD4"), 1.0))
                fg = QColor("#07080D")
            else:
                painter.setBrush(QBrush(QColor("#121822")))
                painter.setPen(QPen(QColor("#2A3544"), 1.0))
                fg = QColor("#CBD5E1")
            painter.drawRoundedRect(rect, 8.0, 8.0)
            painter.setPen(QPen(fg))
            painter.setFont(get_mono_font(10, weight=600))
            text = label if len(label) <= 16 else label[:15] + "…"
            painter.drawText(rect.adjusted(6, 0, -6, 0), Qt.AlignCenter, text)
            if active and op_index >= 0:
                bar = QRectF(rect.left() + 8, rect.bottom() - 6, (rect.width() - 16) * self._t, 2.4)
                painter.setBrush(QBrush(QColor("#07080D" if active else "#5EEAD4")))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(bar, 1.2, 1.2)
            x += cell_w + gap
        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        idx = self._hit(event.pos())
        if idx is None:
            return
        self._drag_i = idx
        self._emit_from_pos(idx, event.pos().x())

    def mouseMoveEvent(self, event):
        if self._drag_i is None:
            return
        self._emit_from_pos(self._drag_i, event.pos().x())

    def mouseReleaseEvent(self, event):
        self._drag_i = None

    def _hit(self, pos) -> Optional[int]:
        for i, rect in enumerate(self._cells):
            if rect.contains(pos):
                return i
        return None

    def _emit_from_pos(self, frame_i: int, x: float) -> None:
        if frame_i < 0 or frame_i >= len(self._frames):
            return
        _label, op_index = self._frames[frame_i]
        rect = self._cells[frame_i]
        if op_index < 0:
            t = 1.0
        else:
            t = 0.0 if rect.width() <= 1 else (x - rect.left()) / rect.width()
            t = max(0.0, min(1.0, t))
        self._index = op_index
        self._t = t
        self.update()
        self.frameChanged.emit(op_index, t)
