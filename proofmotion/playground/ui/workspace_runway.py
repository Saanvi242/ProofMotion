"""Pipeline Runway: one shape through Transform → Clip → Raster."""

from PyQt5.QtWidgets import (
    QWidget, QComboBox, QLabel, QHBoxLayout, QFrame, QPushButton,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF

from playground.experiences import pipeline_state
from playground.math_sync import format_matrix
from playground.models import default_shape_2d
from playground.ui.studio_chrome import StudioMatrixHud, StudioActionBar, build_studio_layout
from resources.theme import get_mono_font, get_ui_font, CHEVRON_TEAL_PATH
from PyQt5.QtGui import QPalette
import math


class _RunwayStage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 280)
        self.state = pipeline_state(default_shape_2d("triangle"), t=0.0)
        self.color = QColor("#5EEAD4")

    def set_state(self, state: dict, color: str = "#5EEAD4"):
        self.state = state
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())
        painter.fillRect(self.rect(), QColor("#07080D"))
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0A0C12")))
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 16.0, 16.0)

        labels = ("TRANSFORM", "CLIP", "RASTER")
        station = int(self.state.get("station", 0))
        header_h = 36.0
        col_w = (w - 28.0) / 3.0
        for i, name in enumerate(labels):
            rect = QRectF(14 + i * col_w, 10, col_w - 8, header_h)
            on = i == station
            painter.setBrush(QBrush(QColor("#5EEAD4") if on else QColor("#121822")))
            painter.setPen(QPen(QColor("#5EEAD4") if on else QColor("#2A3544"), 1.0))
            painter.drawRoundedRect(rect, 8.0, 8.0)
            painter.setPen(QPen(QColor("#07080D") if on else QColor("#94A3B8")))
            painter.setFont(get_ui_font(11, weight=700))
            painter.drawText(rect, Qt.AlignCenter, name)
            if i < 2:
                painter.setPen(QPen(QColor("#334155"), 1.4))
                x = 14 + (i + 1) * col_w - 6
                painter.drawLine(QPointF(x, 28), QPointF(x + 10, 28))

        body_top = 56.0
        body_h = h - body_top - 14.0
        cols = [
            QRectF(14, body_top, col_w - 8, body_h),
            QRectF(14 + col_w, body_top, col_w - 8, body_h),
            QRectF(14 + 2 * col_w, body_top, col_w - 8, body_h),
        ]
        self._draw_world(painter, cols[0], self.state.get("transformed") or self.state["original"], clip=False)
        clip_verts = self.state["clipped"] if self.state.get("clip_t", 0.0) > 0.0 else self.state["transformed"]
        self._draw_world(painter, cols[1], clip_verts, clip=True)
        self._draw_grid(painter, cols[2])
        painter.end()

    def _draw_world(self, painter: QPainter, rect: QRectF, verts, clip: bool):
        painter.save()
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0C1018")))
        painter.drawRoundedRect(rect, 10.0, 10.0)
        painter.setClipRect(rect.adjusted(4, 4, -4, -4))
        cx, cy = rect.center().x(), rect.center().y()
        s = min(rect.width(), rect.height()) / 14.0

        def to_s(x, y):
            return QPointF(cx + x * s, cy - y * s)

        painter.setPen(QPen(QColor("#334155"), 1.0))
        painter.drawLine(to_s(-5, 0), to_s(5, 0))
        painter.drawLine(to_s(0, -4), to_s(0, 4))

        if clip:
            xmin, ymin, xmax, ymax = self.state["clip_rect"]
            wr = QRectF(to_s(xmin, ymax), to_s(xmax, ymin)).normalized()
            fill = QColor("#F472B6")
            fill.setAlpha(28)
            painter.setBrush(QBrush(fill))
            painter.setPen(QPen(QColor("#F472B6"), 1.4, Qt.DashLine))
            painter.drawRect(wr)

        if verts and len(verts) >= 2:
            poly = QPolygonF([to_s(x, y) for x, y in verts])
            col = QColor(self.color)
            col.setAlpha(70 if not clip else 110)
            painter.setBrush(QBrush(col))
            painter.setPen(QPen(self.color, 2.2))
            if len(verts) == 2:
                painter.drawLine(poly[0], poly[1])
            else:
                painter.drawPolygon(poly)
        painter.restore()

    def _draw_grid(self, painter: QPainter, rect: QRectF):
        painter.save()
        painter.setPen(QPen(QColor("#1F2A32"), 1.0))
        painter.setBrush(QBrush(QColor("#0C1018")))
        painter.drawRoundedRect(rect, 10.0, 10.0)
        n = int(self.state.get("grid_size", 19))
        # One grid cell represents span/n world units. The grid's full world
        # extent matches the ±7 range used by the Transform and Clip panels.
        cell = min(rect.width(), rect.height()) / n
        ox = rect.left() + (rect.width() - n * cell) / 2.0
        oy = rect.top() + (rect.height() + n * cell) / 2.0
        painter.setPen(QPen(QColor("#1E293B"), 1.0))
        for i in range(n):
            for j in range(n):
                painter.setBrush(QBrush(QColor("#111827")))
                painter.drawRect(QRectF(ox + i * cell, oy - (j + 1) * cell, cell, cell))
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor("#042F2E"), 1.0))
        for gx, gy in self.state.get("pixels") or []:
            if 0 <= gx < n and 0 <= gy < n:
                painter.drawRect(QRectF(ox + gx * cell, oy - (gy + 1) * cell, cell, cell))
        painter.restore()


class PipelineRunwayWorkspace(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.vertices = default_shape_2d("triangle")
        self.shape_name = "Triangle"
        self.color = "#5EEAD4"
        self.angle = 40.0
        self.sx = 1.4
        self.sy = 1.15
        self.clip_rect = (-3.0, -2.0, 3.0, 2.0)
        self.t = 0.0

        self.stage = _RunwayStage()
        self.stage.setObjectName("StudioViewport")
        self.stage.setAttribute(Qt.WA_StyledBackground, True)
        self.hud = StudioMatrixHud()
        self.bar = StudioActionBar("2d")
        if self.bar.runway_btn:
            self.bar.runway_btn.hide()
        if self.bar.ghost_btn:
            self.bar.ghost_btn.hide()
        if self.bar.wire_btn:
            self.bar.wire_btn.hide()
        build_studio_layout(self, self.stage, None, self.hud, self.bar)

        # Elegant floating header bar for shape selection and pipeline progress
        self.shape_bar = QFrame()
        self.shape_bar.setObjectName("StudioShapeBar")
        self.shape_bar.setAttribute(Qt.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.shape_bar)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.shape_bar.setGraphicsEffect(shadow)

        shape_row = QHBoxLayout(self.shape_bar)
        shape_row.setContentsMargins(18, 8, 18, 8)
        shape_row.setSpacing(12)

        shape_label = QLabel("SHAPE")
        shape_label.setObjectName("StudioHudKicker")

        self.shape_picker = QComboBox()
        self.shape_picker.setObjectName("StudioShapePicker")
        self.shape_picker.addItems(["Triangle", "Square", "Rectangle", "Diamond", "Pentagon", "Hexagon", "Star"])
        self.shape_picker.setCurrentText(self.shape_name)
        self.shape_picker.setMinimumWidth(160)
        self.shape_picker.setFixedHeight(34)
        self.shape_picker.setCursor(Qt.PointingHandCursor)
        picker_pal = self.shape_picker.palette()
        picker_pal.setColor(QPalette.Text, QColor("#F8FAFC"))
        picker_pal.setColor(QPalette.WindowText, QColor("#F8FAFC"))
        picker_pal.setColor(QPalette.ButtonText, QColor("#F8FAFC"))
        self.shape_picker.setPalette(picker_pal)
        self.shape_picker.setStyleSheet(f"""
            QComboBox#StudioShapePicker {{
                background-color: #121624;
                border: 1.5px solid rgba(94, 234, 212, 0.35);
                border-radius: 10px;
                color: #F8FAFC;
                font-size: 13.5px;
                font-weight: 600;
                padding: 4px 32px 4px 14px;
                min-height: 30px;
            }}
            QComboBox#StudioShapePicker:hover {{
                border-color: #5EEAD4;
                background-color: #182032;
                color: #5EEAD4;
            }}
            QComboBox#StudioShapePicker::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border-left: none;
            }}
            QComboBox#StudioShapePicker::down-arrow {{
                image: url("{CHEVRON_TEAL_PATH}");
                width: 11px;
                height: 11px;
                margin-right: 10px;
            }}
            QComboBox#StudioShapePicker QAbstractItemView {{
                background-color: #0E121E;
                border: 1.5px solid rgba(94, 234, 212, 0.4);
                border-radius: 8px;
                color: #F1F5F9;
                selection-background-color: rgba(94, 234, 212, 0.22);
                selection-color: #5EEAD4;
                padding: 4px;
            }}
            QComboBox#StudioShapePicker QAbstractItemView::item {{
                min-height: 28px;
                padding: 4px 8px;
                color: #F1F5F9;
            }}
            QComboBox#StudioShapePicker QAbstractItemView::item:selected,
            QComboBox#StudioShapePicker QAbstractItemView::item:hover {{
                background-color: rgba(94, 234, 212, 0.22);
                color: #5EEAD4;
            }}
        """)
        self.shape_picker.currentTextChanged.connect(self._select_shape)

        shape_row.addWidget(shape_label)
        shape_row.addWidget(self.shape_picker)
        shape_row.addStretch(1)

        pipeline_badge = QLabel("PIPELINE:  Transform  →  Clip  →  Raster")
        pipeline_badge.setObjectName("StudioPipelineBadge")
        shape_row.addWidget(pipeline_badge)

        self.layout().insertWidget(0, self.shape_bar)

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._tick)

        self.bar.rotateClicked.connect(self._bump_angle)
        self.bar.scaleClicked.connect(self._bump_scale)
        self.bar.animateRequested.connect(self._play)
        self.bar.resetObject.connect(self._reset)
        self.bar.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self._refresh()

    def ingest(self, vertices, color: str = "#5EEAD4"):
        if vertices and len(vertices) >= 2:
            self.vertices = [(float(x), float(y)) for x, y in vertices]
        self.color = color or "#5EEAD4"
        self.t = 0.0
        self._refresh()
        self._play()

    def _select_shape(self, name: str):
        self.shape_name = name
        if self.shape_picker.currentText() != name:
            self.shape_picker.blockSignals(True)
            self.shape_picker.setCurrentText(name)
            self.shape_picker.blockSignals(False)
        if name == "Triangle":
            self.vertices = default_shape_2d("triangle")
        elif name == "Square":
            self.vertices = [(-1.5, -1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, 1.5)]
        elif name == "Rectangle":
            self.vertices = default_shape_2d("rectangle")
        elif name == "Diamond":
            self.vertices = [(0.0, 1.9), (1.5, 0.0), (0.0, -1.9), (-1.5, 0.0)]
        elif name in ("Pentagon", "Hexagon"):
            count = 5 if name == "Pentagon" else 6
            self.vertices = [
                (1.8 * math.cos(math.pi / 2 + 2 * math.pi * i / count),
                 1.8 * math.sin(math.pi / 2 + 2 * math.pi * i / count))
                for i in range(count)
            ]
        else:  # Star: alternating outer and inner radii, connected as one outline.
            self.vertices = [
                ((1.9 if i % 2 == 0 else 0.85) * math.cos(math.pi / 2 + math.pi * i / 5),
                 (1.9 if i % 2 == 0 else 0.85) * math.sin(math.pi / 2 + math.pi * i / 5))
                for i in range(10)
            ]
        self.t = 0.0
        self._refresh()
        self.statusMessage.emit(f"{name} selected. Press Play to run it through the pipeline.")

    def _bump_angle(self):
        self.angle = (self.angle + 20.0) % 360.0
        self._refresh()

    def _bump_scale(self):
        self.sx = 0.7 if self.sx > 1.6 else self.sx + 0.2
        self.sy = 0.7 if self.sy > 1.6 else self.sy + 0.15
        self._refresh()

    def _play(self):
        self.t = 0.0
        self._anim.start()
        self.statusMessage.emit("Running the pipeline: transform, clip, rasterize.")

    def _reset(self):
        self.t = 0.0
        self.angle = 40.0
        self.sx, self.sy = 1.4, 1.15
        self._anim.stop()
        self._refresh()

    def _tick(self):
        self.t = min(1.0, self.t + 0.012)
        self._refresh()
        if self.t >= 1.0:
            self._anim.stop()

    def _refresh(self):
        state = pipeline_state(
            self.vertices, angle=self.angle, sx=self.sx, sy=self.sy,
            clip_rect=self.clip_rect, t=self.t,
        )
        self.stage.set_state(state, self.color)
        names = ("Transform", "Clip", "Raster")
        self.hud.bind({
            "empty": False,
            "name": f"{self.shape_name} · {names[state['station']]}",
            "matrix_str": format_matrix(state["matrix"]),
            "history": ["S", "R", "clip", "Bresenham"],
            "world": state["transformed"][:1] if state["transformed"] else [],
        })
        self.hud._meta.setText(
            f"{len(state['clipped'])} clipped verts · {len(state['pixels'])} pixels\n"
            f"M = R({self.angle:.0f}°) · S({self.sx:.2f}, {self.sy:.2f})"
        )

    def set_focus_mode(self, on: bool):
        self.hud.setVisible(not on)
        self.bar.setVisible(not on)

    def set_fullscreen_button(self, on: bool):
        self.bar.fullscreen_btn.blockSignals(True)
        self.bar.fullscreen_btn.setChecked(on)
        self.bar.fullscreen_btn.blockSignals(False)
