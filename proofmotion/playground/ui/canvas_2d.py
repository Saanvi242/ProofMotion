"""
playground/ui/canvas_2d.py
--------------------------
Interactive 2D Cartesian canvas: draw, select, drag, grid, clip window.
"""

from typing import List, Optional, Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF

from playground.scene_2d import Scene2D
from playground.models import composed_matrix_through
import cgip.transformations as t2d
from resources.theme import COLORS, get_ui_font, get_mono_font


class PlaygroundCanvas2D(QWidget):
    statusMessage = pyqtSignal(str)

    def __init__(self, scene: Scene2D, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.setMinimumSize(360, 280)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.tool = "select"  # select, point, line, triangle, rectangle, polygon
        self._draft: List[Tuple[float, float]] = []
        self._hover_world: Optional[Tuple[float, float]] = None
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self._dragging = False
        self._panning = False
        self._last_pos = QPoint()
        self._drag_moved = False
        self.anim_t: Optional[float] = None
        self.film_index: Optional[int] = None
        self.film_t: float = 1.0
        self.show_grid = True

        self.scene.subscribe(self.update)

    def set_tool(self, tool: str):
        self.tool = tool
        self._draft = []
        cursor = Qt.CrossCursor if tool != "select" else Qt.ArrowCursor
        self.setCursor(cursor)
        hints = {
            "select": "Select and drag objects. Right-drag pans the view.",
            "point": "Click to place a point.",
            "line": "Click two endpoints to draw a line.",
            "triangle": "Click three vertices to draw a triangle.",
            "rectangle": "Click two opposite corners to draw a rectangle.",
            "polygon": "Click vertices, then Enter or right-click to close.",
        }
        self.statusMessage.emit(hints.get(tool, ""))
        self.update()

    def set_zoom(self, factor: float):
        self._zoom = max(0.25, min(8.0, float(factor)))
        self.update()

    def reset_view(self):
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self.update()

    def pan_by(self, dx: float, dy: float):
        self._pan[0] += dx
        self._pan[1] += dy
        self.update()

    def _base_scale(self) -> float:
        return min(self.width(), self.height()) / 16.0

    def _scale(self) -> float:
        return self._base_scale() * self._zoom

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        cx = self.width() / 2.0 + self._pan[0]
        cy = self.height() / 2.0 + self._pan[1]
        s = self._scale()
        return cx + x * s, cy - y * s

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        cx = self.width() / 2.0 + self._pan[0]
        cy = self.height() / 2.0 + self._pan[1]
        s = self._scale()
        return (sx - cx) / s, (cy - sy) / s

    def _needed_clicks(self) -> int:
        return {
            "point": 1,
            "line": 2,
            "triangle": 3,
            "rectangle": 2,
            "polygon": 0,
        }.get(self.tool, 0)

    def _finish_draft(self):
        tool = self.tool
        pts = list(self._draft)
        self._draft = []
        if tool == "point" and len(pts) >= 1:
            self.scene.add_object("point", vertices=[pts[0]])
        elif tool == "line" and len(pts) >= 2:
            self.scene.add_object("line", vertices=pts[:2])
        elif tool == "triangle" and len(pts) >= 3:
            self.scene.add_object("triangle", vertices=pts[:3])
        elif tool == "rectangle" and len(pts) >= 2:
            (x0, y0), (x1, y1) = pts[0], pts[1]
            verts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            self.scene.add_object("rectangle", vertices=verts)
        elif tool == "polygon" and len(pts) >= 3:
            self.scene.add_object("polygon", vertices=pts)
        self.update()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and self.tool == "polygon":
            if len(self._draft) >= 3:
                self._finish_draft()
            return
        if event.key() == Qt.Key_Escape:
            self._draft = []
            self.update()
            return
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.scene.delete_selected()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self._last_pos = event.pos()
        self._drag_moved = False
        wx, wy = self.screen_to_world(event.pos().x(), event.pos().y())

        if event.button() == Qt.RightButton:
            if self.tool == "polygon" and len(self._draft) >= 3:
                self._finish_draft()
                return
            self._panning = True
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() != Qt.LeftButton:
            return

        if self.tool != "select":
            self._draft.append((wx, wy))
            need = self._needed_clicks()
            if need and len(self._draft) >= need:
                self._finish_draft()
            self.update()
            return

        hit = self.scene.hit_test(wx, wy)
        self.scene.select(hit)
        if hit:
            self._dragging = True
            self.scene.begin_world_drag()
            self.setCursor(Qt.ClosedHandCursor)
        self.update()

    def mouseMoveEvent(self, event):
        wx, wy = self.screen_to_world(event.pos().x(), event.pos().y())
        self._hover_world = (wx, wy)

        if self._panning:
            delta = event.pos() - self._last_pos
            self._last_pos = event.pos()
            self._pan[0] += delta.x()
            self._pan[1] += delta.y()
            self.update()
            return

        if self._dragging and self.scene.selected():
            prev = self.screen_to_world(self._last_pos.x(), self._last_pos.y())
            self._last_pos = event.pos()
            dx, dy = wx - prev[0], wy - prev[1]
            if abs(dx) > 1e-9 or abs(dy) > 1e-9:
                self._drag_moved = True
                self.scene.translate_world(dx, dy, dragging=True)
            return

        self._last_pos = event.pos()
        if self.tool == "select":
            hit = self.scene.hit_test(wx, wy)
            self.setCursor(Qt.PointingHandCursor if hit else Qt.ArrowCursor)
        if self._draft:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._panning = False
            self.setCursor(Qt.CrossCursor if self.tool != "select" else Qt.ArrowCursor)
        if event.button() == Qt.LeftButton:
            self._dragging = False
            if self.tool == "select":
                self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        if self.tool == "polygon" and len(self._draft) >= 3:
            self._finish_draft()

    def wheelEvent(self, event):
        factor = 1.12 if event.angleDelta().y() > 0 else 0.89
        self.set_zoom(self._zoom * factor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w, h = float(self.width()), float(self.height())
        painter.fillRect(self.rect(), QColor("#07080D"))
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0A0C12")))
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 16.0, 16.0)
        painter.setClipRect(QRectF(8, 8, w - 16, h - 16))
        self._draw_grid(painter)

        if self.scene.clip_enabled:
            self._draw_clip_window(painter)

        selected = self.scene.selected()
        for obj in self.scene.objects:
            is_sel = selected is not None and obj.id == selected.id
            if is_sel and self.scene.show_ghost and obj.history:
                self._draw_trails(painter, obj)
            verts = self._live_vertices(obj, is_sel)
            color = obj.color
            live = verts
            clipped = self.scene.clipped_geometry(obj) if self.scene.clip_enabled else None
            if self.scene.clip_enabled:
                self._draw_shape(painter, obj.kind, live, color, ghost=True, selected=False)
                if clipped:
                    self._draw_shape(painter, obj.kind, clipped, color, ghost=False, selected=is_sel, wire=self.scene.wireframe)
            else:
                self._draw_shape(painter, obj.kind, live, color, ghost=False, selected=is_sel, wire=self.scene.wireframe)
            if is_sel and self.scene.show_coords:
                self._draw_vertex_labels(painter, live)

        if self._draft:
            preview = list(self._draft)
            if self._hover_world:
                preview.append(self._hover_world)
            self._draw_draft(painter, preview)

        self._draw_hint(painter)
        painter.end()

    def _film_matrix(self, obj):
        if self.anim_t is not None and obj.history:
            idx = self.film_index if self.film_index is not None else len(obj.history) - 1
            return composed_matrix_through(obj, idx, self.anim_t, dim=2)
        if self.film_index is not None:
            return composed_matrix_through(obj, self.film_index, self.film_t, dim=2)
        return obj.composed_matrix()

    def _live_vertices(self, obj, is_sel: bool):
        if is_sel and (self.anim_t is not None or self.film_index is not None):
            return t2d.apply_transform(self._film_matrix(obj), obj.local_vertices)
        return obj.world_vertices()

    def _draw_trails(self, painter: QPainter, obj):
        n = len(obj.history)
        if n <= 0:
            return
        live_index = self.film_index
        for i in range(-1, n):
            if live_index is None and self.anim_t is None and i == n - 1:
                continue
            if live_index is not None and i == live_index and (self.anim_t is None or self.film_t >= 0.999):
                continue
            verts = t2d.apply_transform(composed_matrix_through(obj, i, 1.0, dim=2), obj.local_vertices)
            self._draw_shape(painter, obj.kind, verts, "#64748B", ghost=True)

    def _draw_grid(self, painter: QPainter):
        w, h = self.width(), self.height()
        s = self._scale()
        ox, oy = self.world_to_screen(0.0, 0.0)
        step = 1.0
        while step * s < 36:
            step *= 2.0
        while step * s > 96:
            step /= 2.0

        if self.show_grid:
            pen = QPen(QColor("#252A3A"))
            pen.setWidth(1)
            painter.setPen(pen)
            x = ox
            while x >= 0:
                painter.drawLine(QPointF(x, 0), QPointF(x, h))
                x -= step * s
            x = ox + step * s
            while x <= w:
                painter.drawLine(QPointF(x, 0), QPointF(x, h))
                x += step * s
            y = oy
            while y >= 0:
                painter.drawLine(QPointF(0, y), QPointF(w, y))
                y -= step * s
            y = oy + step * s
            while y <= h:
                painter.drawLine(QPointF(0, y), QPointF(w, y))
                y += step * s

        axis = QPen(QColor("#4B5573"))
        axis.setWidth(1)
        painter.setPen(axis)
        painter.drawLine(QPointF(0, oy), QPointF(w, oy))
        painter.drawLine(QPointF(ox, 0), QPointF(ox, h))

        painter.setFont(get_mono_font(11, weight=600))
        painter.setPen(QPen(QColor("#F43F5E")))
        painter.drawText(QPointF(min(w - 18, ox + 8), 16), "Y")
        painter.setPen(QPen(QColor("#7DD3FC")))
        painter.drawText(QPointF(w - 18, oy - 6), "X")

        painter.setFont(get_mono_font(10))
        painter.setPen(QPen(QColor("#64748B")))
        k = step
        while True:
            sx, sy = self.world_to_screen(k, 0)
            if sx > w - 8:
                break
            painter.drawText(QPointF(sx - 8, oy + 14), f"{k:g}")
            k += step
        k = -step
        while True:
            sx, sy = self.world_to_screen(k, 0)
            if sx < 8:
                break
            painter.drawText(QPointF(sx - 12, oy + 14), f"{k:g}")
            k -= step

    def _draw_clip_window(self, painter: QPainter):
        xmin, ymin, xmax, ymax = self.scene.clip_rect
        x0, y0 = self.world_to_screen(xmin, ymax)
        x1, y1 = self.world_to_screen(xmax, ymin)
        rect = QRectF(QPointF(x0, y0), QPointF(x1, y1)).normalized()
        fill = QColor(COLORS["accent_gold"])
        fill.setAlpha(22)
        painter.setBrush(QBrush(fill))
        pen = QPen(QColor(COLORS["accent_gold_pressed"]), 1.6, Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(rect)
        painter.setFont(get_mono_font(10, weight=600))
        painter.setPen(QPen(QColor(COLORS["accent_gold_pressed"])))
        painter.drawText(rect.adjusted(6, 4, 0, 0), "clip window")

    def _draw_shape(self, painter, kind, verts, color, ghost=False, selected=False, wire=False):
        if not verts:
            return
        qcolor = QColor(color)
        pts = [QPointF(*self.world_to_screen(x, y)) for x, y in verts]
        if ghost:
            qcolor.setAlpha(110)
            pen = QPen(qcolor, 1.4, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
        else:
            pen = QPen(qcolor, 2.6 if selected else 2.0)
            painter.setPen(pen)
            fill = QColor(qcolor)
            fill.setAlpha(0 if wire else 72)
            painter.setBrush(Qt.NoBrush if (kind in ("point", "line") or wire) else QBrush(fill))

        if kind == "point" or len(pts) == 1:
            r = 5.5 if selected else 4.5
            painter.setBrush(QBrush(qcolor))
            painter.drawEllipse(pts[0], r, r)
            return
        if kind == "line" or len(pts) == 2:
            painter.drawLine(pts[0], pts[1])
            painter.setBrush(QBrush(qcolor))
            for p in pts:
                painter.drawEllipse(p, 3.5, 3.5)
            return
        poly = QPolygonF(pts)
        painter.drawPolygon(poly)
        if selected:
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            for p in pts:
                painter.drawEllipse(p, 4.0, 4.0)

    def _draw_vertex_labels(self, painter, verts):
        painter.setFont(get_mono_font(11, weight=600))
        painter.setPen(QPen(QColor("#E2E8F0")))
        for i, (x, y) in enumerate(verts[:12]):
            sx, sy = self.world_to_screen(x, y)
            label = chr(ord("A") + i) if i < 26 else f"P{i}"
            painter.drawText(QPointF(sx + 7, sy - 7), f"{label}({x:.1f},{y:.1f})")

    def _draw_draft(self, painter, pts):
        color = QColor(COLORS["accent_gold_pressed"])
        painter.setPen(QPen(color, 1.6, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        sp = [QPointF(*self.world_to_screen(x, y)) for x, y in pts]
        if len(sp) == 1:
            painter.drawEllipse(sp[0], 4, 4)
        elif len(sp) == 2:
            painter.drawLine(sp[0], sp[1])
        else:
            painter.drawPolyline(QPolygonF(sp))
        painter.setBrush(QBrush(color))
        for p in sp:
            painter.drawEllipse(p, 3.2, 3.2)

    def _draw_hint(self, painter):
        if self.scene.objects:
            return
        painter.setPen(QPen(QColor("#94A3B8")))
        painter.setFont(get_ui_font(14, weight=500))
        painter.drawText(
            QRectF(0, 0, self.width(), self.height()),
            Qt.AlignCenter,
            "Pick a tool and click the canvas — this is yours to make",
        )
