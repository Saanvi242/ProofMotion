"""Living Basis: drag î and ĵ; the grid is the matrix."""

from typing import Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF

from playground.experiences import (
    deform_points, living_basis_det, living_basis_matrix, sample_letter_f, unit_grid_lines,
)
from playground.math_sync import format_matrix
from playground.ui.studio_chrome import StudioMatrixHud, StudioActionBar, build_studio_layout
from resources.theme import get_mono_font
import cgip.transformations as t2d


class _BasisCanvas(QWidget):
    statusMessage = pyqtSignal(str)
    basisChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 280)
        self.setMouseTracking(True)
        self.ix, self.iy = 1.0, 0.0
        self.jx, self.jy = 0.0, 1.0
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self._drag = None
        self._last = QPoint()

    def reset(self):
        self.ix, self.iy = 1.0, 0.0
        self.jx, self.jy = 0.0, 1.0
        self.basisChanged.emit()
        self.update()

    def rotate(self, angle: float):
        R = t2d.rotation_matrix(angle)
        i = t2d.apply_transform(R, [(self.ix, self.iy)])[0]
        j = t2d.apply_transform(R, [(self.jx, self.jy)])[0]
        self.ix, self.iy = i
        self.jx, self.jy = j
        self.basisChanged.emit()
        self.update()

    def scale_i(self, factor: float):
        self.ix *= factor
        self.iy *= factor
        self.basisChanged.emit()
        self.update()

    def _scale(self) -> float:
        return min(self.width(), self.height()) / 12.0 * self._zoom

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        s = self._scale()
        return self.width() / 2.0 + x * s + self._pan[0], self.height() / 2.0 - y * s + self._pan[1]

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        s = self._scale()
        return (sx - self.width() / 2.0 - self._pan[0]) / s, (self.height() / 2.0 + self._pan[1] - sy) / s

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())
        painter.fillRect(self.rect(), QColor("#07080D"))
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0A0C12")))
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 16.0, 16.0)
        painter.setClipRect(QRectF(8, 8, w - 16, h - 16))

        origin = QPointF(*self.world_to_screen(0, 0))
        painter.setPen(QPen(QColor("#252A3A"), 1.0))
        painter.drawLine(QPointF(8, origin.y()), QPointF(w - 8, origin.y()))
        painter.drawLine(QPointF(origin.x(), 8), QPointF(origin.x(), h - 8))

        for line in unit_grid_lines(4, 3.0):
            a, b = deform_points(self.ix, self.iy, self.jx, self.jy, line)
            painter.setPen(QPen(QColor("#1E3A3A"), 1.0))
            painter.drawLine(QPointF(*self.world_to_screen(*a)), QPointF(*self.world_to_screen(*b)))

        shape = deform_points(self.ix, self.iy, self.jx, self.jy, sample_letter_f())
        poly = QPolygonF([QPointF(*self.world_to_screen(x, y)) for x, y in shape])
        fill = QColor("#5EEAD4")
        fill.setAlpha(40)
        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(QColor("#5EEAD4"), 2.0))
        painter.drawPolygon(poly)

        self._draw_vector(painter, self.ix, self.iy, QColor("#38BDF8"), "î")
        self._draw_vector(painter, self.jx, self.jy, QColor("#F472B6"), "ĵ")
        painter.end()

    def _draw_vector(self, painter: QPainter, x: float, y: float, color: QColor, label: str):
        o = QPointF(*self.world_to_screen(0, 0))
        p = QPointF(*self.world_to_screen(x, y))
        painter.setPen(QPen(color, 2.6, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(o, p)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(p, 7.0, 7.0)
        painter.setPen(QPen(color))
        painter.setFont(get_mono_font(13, weight=700))
        painter.drawText(QPointF(p.x() + 10, p.y() - 8), f"{label}  ({x:.2f}, {y:.2f})")

    def mousePressEvent(self, event):
        self._last = event.pos()
        wx, wy = self.screen_to_world(event.x(), event.y())
        if (wx - self.ix) ** 2 + (wy - self.iy) ** 2 < 0.22:
            self._drag = "i"
        elif (wx - self.jx) ** 2 + (wy - self.jy) ** 2 < 0.22:
            self._drag = "j"
        elif event.button() == Qt.RightButton:
            self._drag = "pan"
        else:
            self._drag = None

    def mouseMoveEvent(self, event):
        wx, wy = self.screen_to_world(event.x(), event.y())
        if self._drag == "i":
            self.ix, self.iy = wx, wy
            self.basisChanged.emit()
            self.update()
        elif self._drag == "j":
            self.jx, self.jy = wx, wy
            self.basisChanged.emit()
            self.update()
        elif self._drag == "pan":
            d = event.pos() - self._last
            self._pan[0] += d.x()
            self._pan[1] += d.y()
            self._last = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self._drag = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.08 if delta > 0 else 0.92
        self._zoom = max(0.4, min(4.0, self._zoom * factor))
        self.update()


class LivingBasisWorkspace(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.canvas = _BasisCanvas()
        self.hud = StudioMatrixHud()
        self.bar = StudioActionBar("2d")
        if self.bar.runway_btn:
            self.bar.runway_btn.hide()
        if self.bar.ghost_btn:
            self.bar.ghost_btn.hide()
        if self.bar.wire_btn:
            self.bar.wire_btn.hide()
        build_studio_layout(self, self.canvas, None, self.hud, self.bar)

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._tick)
        self._from = (1.0, 0.0, 0.0, 1.0)
        self._to = (1.0, 0.0, 0.6, 1.0)
        self._t = 0.0

        self.bar.rotateClicked.connect(lambda: self.canvas.rotate(15.0))
        self.bar.scaleClicked.connect(lambda: self.canvas.scale_i(1.25))
        self.bar.animateRequested.connect(self._play)
        self.bar.resetObject.connect(self.canvas.reset)
        self.bar.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self.canvas.basisChanged.connect(self._refresh)
        self._refresh()

    def _play(self):
        self._from = (self.canvas.ix, self.canvas.iy, self.canvas.jx, self.canvas.jy)
        self._to = (1.0, 0.15, 0.85, 1.0)
        self._t = 0.0
        self._anim.start()
        self.statusMessage.emit("Shearing the basis — watch î, ĵ, and the F.")

    def _tick(self):
        self._t += 0.03
        u = min(1.0, self._t)
        a, b = self._from, self._to
        self.canvas.ix = a[0] + (b[0] - a[0]) * u
        self.canvas.iy = a[1] + (b[1] - a[1]) * u
        self.canvas.jx = a[2] + (b[2] - a[2]) * u
        self.canvas.jy = a[3] + (b[3] - a[3]) * u
        self.canvas.update()
        self._refresh()
        if u >= 1.0:
            self._anim.stop()
            self.canvas.basisChanged.emit()

    def _refresh(self):
        c = self.canvas
        M = living_basis_matrix(c.ix, c.iy, c.jx, c.jy)
        det = living_basis_det(c.ix, c.iy, c.jx, c.jy)
        self.hud.bind({
            "empty": False,
            "name": "Living basis",
            "matrix_str": format_matrix(M),
            "history": ["î column 0", "ĵ column 1"],
            "world": [(c.ix, c.iy), (c.jx, c.jy)],
        })
        self.hud._meta.setText(
            f"î = ({c.ix:.2f}, {c.iy:.2f})   ĵ = ({c.jx:.2f}, {c.jy:.2f})\n"
            f"det = {det:.2f}" + ("  — degenerate" if abs(det) < 1e-4 else "")
        )

    def set_focus_mode(self, on: bool):
        self.hud.setVisible(not on)
        self.bar.setVisible(not on)

    def set_fullscreen_button(self, on: bool):
        self.bar.fullscreen_btn.blockSignals(True)
        self.bar.fullscreen_btn.setChecked(on)
        self.bar.fullscreen_btn.blockSignals(False)
