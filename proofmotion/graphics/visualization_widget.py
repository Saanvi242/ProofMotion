"""
graphics/visualization_widget.py
---------------------------------
Comprehensive 2D interactive graphics engine for ProofMotion.

Renders:
  - Geometric constructions for theorems (points, lines, polygons, arcs, labels)
  - Sorting and searching bar visualizations with state highlights
  - Transformation studio (world coordinates, axes, original & transformed shapes)
  - Rasterization pixel grids (DDA, Bresenham, Midpoint Circle with candidate & selected pixels)
  - Line clipping (Cohen-Sutherland clipping window, 9-region outcodes, intersections)
  - Image processing before/after canvas

Supports interactive mouse dragging to pan, wheel to zoom, view controls,
and smooth auto-framing with responsive antialiased rendering.
"""

import math
from typing import Optional, List, Dict, Any, Tuple
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygonF, QImage, QPainterPath
)

import resources.theme as theme
from resources.theme import COLORS, FONT_FAMILY_MONO, get_ui_font, get_mono_font
from core.step_model import RenderData
from graphics.sorting_renderer import SortingPlaygroundRenderer
from graphics.label_layout import (
    LabelPlacer, LabelSpec, PlacedLabel, outward_from_centroid, polygon_bbox_anchor, leader_needed
)


class VisualizationWidget(QWidget):
    """Interactive visualizer for geometry, algorithms, transformations, and CGIP."""

    viewChanged = pyqtSignal(float, float, float)  # zoom, pan_x, pan_y
    clippingEndpointDragged = pyqtSignal(str, float, float)  # target ("P1" or "P2"), x, y
    clippingRegionClicked = pyqtSignal(int, str)  # code, region_name
    curveHandleDragged = pyqtSignal(str, float, float)  # handle id ("P0"/"T0"), x, y

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlaceholderCanvas")
        self.setMinimumSize(360, 220)
        self.setMouseTracking(True)

        self._theorem_key = None
        self._display_name = ""
        self._step_index = 0
        self._values = {}
        self._render_data: RenderData = RenderData()

        # Camera / Viewport state
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self._dragging = False
        self._last_mouse_pos = None
        self._show_grid = True

        # Cohen-Sutherland endpoint dragging & hover
        self._drag_endpoint_target: Optional[str] = None
        self._hovered_endpoint: Optional[str] = None

        # Bézier / Curve handle dragging & hover
        self._drag_curve_target: Optional[str] = None
        self._hovered_curve_target: Optional[str] = None

        # Smart label placement engine
        self._label_placer: Optional[LabelPlacer] = None
        self._last_placed_labels: List[PlacedLabel] = []

        # Animated Sorting Playground Engine
        self._sorting_renderer = SortingPlaygroundRenderer()
        self._anim_progress = 1.0
        self._anim_duration = 450  # ms
        self._speed_mult = 1.0
        self._prev_render_data: Optional[RenderData] = None
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        self._anim_timer.timeout.connect(self._on_anim_tick)

    def _on_anim_tick(self):
        self._anim_progress += 16.0 / max(50.0, self._anim_duration)
        if self._anim_progress >= 1.0:
            self._anim_progress = 1.0
            self._anim_timer.stop()
        self._sorting_renderer.progress = self._anim_progress
        self.update()

    def set_sorting_style(self, style: str):
        self._sorting_renderer.style = style
        self.update()

    def set_sorting_reduced_motion(self, reduced: bool):
        self._sorting_renderer.reduced_motion = reduced
        if reduced:
            self._anim_progress = 1.0
            self._sorting_renderer.progress = 1.0
            self._anim_timer.stop()
        self.update()

    def set_sorting_duration(self, duration_ms: int):
        self._anim_duration = max(50, duration_ms)
        self._speed_mult = 450.0 / max(50.0, float(duration_ms))

    # ------------------------------------------------------------------
    # Public interface (called by controller)
    # ------------------------------------------------------------------
    def set_show_grid(self, show: bool):
        self._show_grid = bool(show)
        self.update()

    def set_theorem(self, theorem_key: str, display_name: str = ""):
        self._theorem_key = theorem_key
        self._display_name = display_name
        self._step_index = 0
        self._values = {}
        self._render_data = RenderData()
        self.reset_view()
        self.update()

    def update_step(self, step_index: int, values: dict, render_data: RenderData = None):
        self._step_index = step_index
        self._values = values or {}
        self._prev_render_data = self._render_data
        if render_data is not None:
            self._render_data = render_data
        elif "render_data" in self._values and isinstance(self._values["render_data"], RenderData):
            self._render_data = self._values["render_data"]

        rd = self._render_data
        is_sorting = bool(rd and (rd.mode == "bars" or getattr(rd, "sort_event", None) is not None))
        is_clipping = bool(rd and rd.mode == "clipping" and rd.clipping_data)
        is_geometry = bool(rd and rd.mode in ("geometry", "") and not is_clipping and not is_sorting)
        is_raster = bool(rd and rd.mode == "pixel_grid")
        is_search = bool(rd and getattr(rd, "search_data", None) is not None)
        reduced = bool(self._sorting_renderer.reduced_motion)
        speed = max(0.25, getattr(self, "_speed_mult", 1.0))

        has_anim = False
        if reduced:
            has_anim = False
        elif is_sorting:
            has_anim = True
            ev = getattr(rd, "sort_event", None)
            long = bool(ev and str(getattr(ev, "event_type", "")).lower() in (
                "sorteventtype.swap", "sorteventtype.shift", "sorteventtype.merge_write", "swap", "shift", "merge_write"
            ) or (ev and getattr(ev, "is_swap", lambda: False)()))
            base = 1000 if long else 700
            self._anim_duration = int(base / speed)
        elif is_clipping and rd.clipping_data.get("anim"):
            has_anim = True
            anim_type = str(rd.clipping_data.get("anim", {}).get("type", ""))
            base = 1100 if anim_type in ("edge_travel", "pass_morph", "endpoint_move") else 800
            self._anim_duration = int(base / speed)
        elif is_search:
            has_anim = True
            self._anim_duration = int(750 / speed)
        elif is_raster:
            has_anim = True
            self._anim_duration = int(650 / speed)
        elif is_geometry and rd and (rd.polygons or rd.lines or rd.points or rd.arcs):
            has_anim = True
            self._anim_duration = int(900 / speed)

        if has_anim:
            self._anim_progress = 0.0
            self._sorting_renderer.progress = 0.0
            self._anim_timer.start(16)
        else:
            self._anim_progress = 1.0
            self._sorting_renderer.progress = 1.0
            self._anim_timer.stop()

        self.update()

    def is_animating(self) -> bool:
        return self._anim_timer.isActive() and self._anim_progress < 1.0

    def playback_interval_ms(self, speed_multiplier: float = 1.0) -> int:
        """Hold each step long enough for its motion to finish, then a comfortable beat."""
        speed = max(0.25, float(speed_multiplier))
        return int((self._anim_duration + 550) / speed)

    def set_render_data(self, render_data: RenderData):
        self._render_data = render_data or RenderData()
        self.update()

    def set_zoom(self, factor: float):
        self._zoom = max(0.1, min(10.0, factor))
        self.viewChanged.emit(self._zoom, self._pan[0], self._pan[1])
        self.update()

    def set_pan(self, dx: float, dy: float):
        self._pan[0] += dx
        self._pan[1] += dy
        self.viewChanged.emit(self._zoom, self._pan[0], self._pan[1])
        self.update()

    def reset_view(self):
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self.viewChanged.emit(self._zoom, self._pan[0], self._pan[1])
        self.update()

    def clear(self):
        self._theorem_key = None
        self._display_name = ""
        self._step_index = 0
        self._values = {}
        self._render_data = RenderData()
        self.update()

    # ------------------------------------------------------------------
    # Clipping Coordinate Helpers
    # ------------------------------------------------------------------
    def _clip_ease(self, t: Optional[float] = None) -> float:
        if t is None:
            t = self._anim_progress
        t = min(1.0, max(0.0, float(t)))
        return t * t * (3.0 - 2.0 * t)

    def _clip_stagger(self, index: int, count: int = 4) -> float:
        t = self._clip_ease()
        start = index / float(count + 0.85)
        span = 0.38
        return min(1.0, max(0.0, (t - start) / span))

    def _get_clipping_transform(self) -> Tuple[float, float, float]:
        w, h = float(self.width()), float(self.height())
        cd = {}
        if self._render_data and getattr(self._render_data, "clipping_data", None):
            cd = self._render_data.clipping_data or {}
        xmin = float(cd.get("xmin", -4.0))
        ymin = float(cd.get("ymin", -3.0))
        xmax = float(cd.get("xmax", 4.0))
        ymax = float(cd.get("ymax", 3.0))
        span_x = max(2.0, xmax - xmin)
        span_y = max(2.0, ymax - ymin)
        margin = 1.25
        world_w = span_x * (1.0 + 2.0 * margin)
        world_h = span_y * (1.0 + 2.0 * margin)
        usable_w = max(80.0, w - 36.0)
        top_pad, bottom_pad = 96.0, 62.0
        usable_h = max(80.0, h - top_pad - bottom_pad)
        scale = min(usable_w / world_w, usable_h / world_h) * self._zoom
        mid_x = (xmin + xmax) / 2.0
        mid_y = (ymin + ymax) / 2.0
        cx = w / 2.0 + self._pan[0] - mid_x * scale
        cy = top_pad + usable_h / 2.0 + self._pan[1] + mid_y * scale
        return cx, cy, scale

    def _clipping_world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        cx, cy, scale = self._get_clipping_transform()
        return cx + x * scale, cy - y * scale

    def _clipping_screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        cx, cy, scale = self._get_clipping_transform()
        if scale == 0:
            return 0.0, 0.0
        return (sx - cx) / scale, (cy - sy) / scale

    # ------------------------------------------------------------------
    # Curve Coordinate Transform
    # ------------------------------------------------------------------
    def _get_curve_transform(self) -> Tuple[float, float, float]:
        w, h = float(self.width()), float(self.height())
        cd = (getattr(self._render_data, "curve_data", None) or {}) if self._render_data else {}
        bounds = getattr(self._render_data, "view_bounds", None) if self._render_data else None
        if bounds and len(bounds) == 4:
            xmin, ymin, xmax, ymax = bounds
        else:
            pts = cd.get("control_points", [])
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                pad = 2.0
                xmin, xmax = min(xs) - pad, max(xs) + pad
                ymin, ymax = min(ys) - pad, max(ys) + pad
            else:
                xmin, ymin, xmax, ymax = -8.0, -6.0, 8.0, 6.0

        span_x = max(3.0, float(xmax - xmin))
        span_y = max(3.0, float(ymax - ymin))
        margin = 1.15
        world_w = span_x * margin
        world_h = span_y * margin
        usable_w = max(80.0, w - 60.0)
        usable_h = max(80.0, h - 80.0)
        scale = min(usable_w / world_w, usable_h / world_h) * self._zoom
        mid_x = (xmin + xmax) / 2.0
        mid_y = (ymin + ymax) / 2.0
        cx = w / 2.0 + self._pan[0] - mid_x * scale
        cy = h / 2.0 + self._pan[1] + mid_y * scale
        return cx, cy, scale

    def _curve_world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        cx, cy, scale = self._get_curve_transform()
        return cx + x * scale, cy - y * scale

    def _curve_screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        cx, cy, scale = self._get_curve_transform()
        if scale <= 1e-6:
            return 0.0, 0.0
        return (sx - cx) / scale, (cy - sy) / scale

    # ------------------------------------------------------------------
    # Mouse interaction (Pan, Zoom & Endpoint Dragging)
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._render_data and (self._render_data.mode == "curves" or getattr(self._render_data, "curve_data", None)):
                cd = self._render_data.curve_data or {}
                if cd.get("draggable", True):
                    pts = cd.get("control_points", [])
                    labels = cd.get("labels", [f"P{i}" for i in range(len(pts))])
                    mx, my = float(event.pos().x()), float(event.pos().y())
                    for pt, lbl in zip(pts, labels):
                        sx, sy = self._curve_world_to_screen(pt[0], pt[1])
                        if (mx - sx) ** 2 + (my - sy) ** 2 <= 22.0 ** 2:
                            self._drag_curve_target = lbl
                            self.setCursor(Qt.ClosedHandCursor)
                            return

            if self._render_data and self._render_data.mode == "clipping" and self._render_data.clipping_data:
                cd = self._render_data.clipping_data
                view_tab = cd.get("view_tab", "clip_line")
                if view_tab == "region_codes":
                    mx, my = float(event.pos().x()), float(event.pos().y())
                    wx, wy = self._clipping_screen_to_world(mx, my)
                    xmin = float(cd.get("xmin", -4.0))
                    ymin = float(cd.get("ymin", -3.0))
                    xmax = float(cd.get("xmax", 4.0))
                    ymax = float(cd.get("ymax", 3.0))
                    from cgip.clipping import compute_outcode, REGION_NAMES
                    code = compute_outcode(wx, wy, xmin, ymin, xmax, ymax)
                    rname = REGION_NAMES.get(code, "Unknown")
                    self.clippingRegionClicked.emit(code, rname)
                    cd["selected_code"] = code
                    self.update()
                    return

                cur_p1 = cd.get("current_p1") or cd.get("orig_p1")
                cur_p2 = cd.get("current_p2") or cd.get("orig_p2")
                mx, my = float(event.pos().x()), float(event.pos().y())
                if cur_p1:
                    s1x, s1y = self._clipping_world_to_screen(cur_p1[0], cur_p1[1])
                    if (mx - s1x) ** 2 + (my - s1y) ** 2 <= 20.0 ** 2:
                        self._drag_endpoint_target = "P1"
                        self.setCursor(Qt.ClosedHandCursor)
                        return
                if cur_p2:
                    s2x, s2y = self._clipping_world_to_screen(cur_p2[0], cur_p2[1])
                    if (mx - s2x) ** 2 + (my - s2y) ** 2 <= 20.0 ** 2:
                        self._drag_endpoint_target = "P2"
                        self.setCursor(Qt.ClosedHandCursor)
                        return

            self._dragging = True
            self._last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._drag_curve_target:
            wx, wy = self._curve_screen_to_world(float(event.pos().x()), float(event.pos().y()))
            self.curveHandleDragged.emit(self._drag_curve_target, round(wx, 2), round(wy, 2))
            return

        if self._drag_endpoint_target:
            wx, wy = self._clipping_screen_to_world(float(event.pos().x()), float(event.pos().y()))
            self.clippingEndpointDragged.emit(self._drag_endpoint_target, round(wx, 1), round(wy, 1))
            return

        # Check hover over control points in curves mode
        if self._render_data and (self._render_data.mode == "curves" or getattr(self._render_data, "curve_data", None)) and not self._dragging:
            cd = self._render_data.curve_data or {}
            if cd.get("draggable", True):
                pts = cd.get("control_points", [])
                labels = cd.get("labels", [f"P{i}" for i in range(len(pts))])
                mx, my = float(event.pos().x()), float(event.pos().y())
                matched = None
                for pt, lbl in zip(pts, labels):
                    sx, sy = self._curve_world_to_screen(pt[0], pt[1])
                    if (mx - sx) ** 2 + (my - sy) ** 2 <= 22.0 ** 2:
                        matched = lbl
                        break
                if matched != self._hovered_curve_target:
                    self._hovered_curve_target = matched
                    self.setCursor(Qt.PointingHandCursor if matched else Qt.ArrowCursor)
                    self.update()

        # Check hover over endpoints in clipping mode
        if self._render_data and self._render_data.mode == "clipping" and self._render_data.clipping_data and not self._dragging:
            cd = self._render_data.clipping_data
            cur_p1 = cd.get("current_p1") or cd.get("orig_p1")
            cur_p2 = cd.get("current_p2") or cd.get("orig_p2")
            mx, my = float(event.pos().x()), float(event.pos().y())
            is_hover = False
            if cur_p1:
                s1x, s1y = self._clipping_world_to_screen(cur_p1[0], cur_p1[1])
                if (mx - s1x) ** 2 + (my - s1y) ** 2 <= 20.0 ** 2:
                    self._hovered_endpoint = "P1"
                    self.setCursor(Qt.PointingHandCursor)
                    is_hover = True
                    self.update()
            if not is_hover and cur_p2:
                s2x, s2y = self._clipping_world_to_screen(cur_p2[0], cur_p2[1])
                if (mx - s2x) ** 2 + (my - s2y) ** 2 <= 20.0 ** 2:
                    self._hovered_endpoint = "P2"
                    self.setCursor(Qt.PointingHandCursor)
                    is_hover = True
                    self.update()
            if not is_hover and self._hovered_endpoint is not None:
                self._hovered_endpoint = None
                self.setCursor(Qt.ArrowCursor)
                self.update()

        if self._dragging and self._last_mouse_pos is not None:
            delta = event.pos() - self._last_mouse_pos
            self._last_mouse_pos = event.pos()
            self.set_pan(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._drag_curve_target:
                self._drag_curve_target = None
                self.setCursor(Qt.PointingHandCursor if self._hovered_curve_target else Qt.ArrowCursor)
                return
            if self._drag_endpoint_target:
                self._drag_endpoint_target = None
                self.setCursor(Qt.PointingHandCursor if self._hovered_endpoint else Qt.ArrowCursor)
                return
            self._dragging = False
            self.setCursor(Qt.ArrowCursor)
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        rd = self._render_data
        if rd and (rd.mode == "bars" or getattr(rd, "search_data", None) is not None or getattr(rd, "sort_event", None) is not None):
            return
        if getattr(self, "_theorem_key", "") in (
            "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort", "linear_search", "binary_search"
        ):
            return
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 0.85
        self.set_zoom(self._zoom * factor)

    # ------------------------------------------------------------------
    # Rendering Orchestration
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # Plotting canvas: subtle pale grey-blue background (#F8F9FD) with fine 1px border (#E0E6F2)
        w, h = float(self.width()), float(self.height())
        canvas_rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        painter.setPen(QPen(QColor(COLORS["border_canvas"]), 1.0))
        painter.setBrush(QBrush(QColor(COLORS["bg_viewport"])))
        painter.drawRoundedRect(canvas_rect, 10.0, 10.0)

        # Clip inner drawings cleanly inside the fine border
        painter.save()
        clip_path = QPainterPath()
        clip_path.addRoundedRect(canvas_rect.adjusted(0.5, 0.5, -0.5, -0.5), 9.5, 9.5)
        painter.setClipPath(clip_path)

        rd = self._render_data
        mode = rd.mode if rd else "geometry"

        if rd and getattr(rd, "tree_data", None) is not None:
            self._draw_tree(painter, rd.tree_data)
        elif rd and getattr(rd, "graph_data", None) is not None:
            self._draw_graph(painter, rd.graph_data)
        elif rd and getattr(rd, "search_data", None) is not None:
            self._draw_search_tiles(painter, rd.search_data)
        elif mode == "bars" and rd.bars is not None:
            self._draw_bars(painter, rd.bars)
        elif mode == "pixel_grid" and rd.pixel_grid is not None:
            self._draw_pixel_grid(painter, rd.pixel_grid)
        elif mode == "clipping" and rd.clipping_data is not None:
            self._draw_clipping(painter, rd.clipping_data)
        elif (mode == "curves" or getattr(rd, "curve_data", None) is not None) and rd.curve_data is not None:
            self._draw_curves(painter, rd.curve_data)
        elif mode == "image" and rd.image_data is not None:
            self._draw_image(painter, rd.image_data)
        else:
            self._draw_geometry(painter, rd)

        painter.restore()

        # Overlay faint top-right status tag
        self._draw_overlay_hud(painter)

    # ------------------------------------------------------------------
    # HUD / Overlay
    # ------------------------------------------------------------------
    def _draw_overlay_hud(self, painter: QPainter):
        painter.save()
        painter.setFont(get_mono_font(12, weight=400))
        painter.setPen(QPen(QColor(COLORS["text_muted"])))

        info_text = f"Zoom: {self._zoom:.2f}×"
        if self._pan[0] != 0 or self._pan[1] != 0:
            info_text += f" | Pan: ({int(self._pan[0])}, {int(self._pan[1])})"

        # Keep the zoom badge off clipping captions and algorithms (sorting / searching / graphs / trees)
        is_clipping = bool(self._render_data and self._render_data.mode == "clipping")
        is_algorithms = bool(
            getattr(self, "_theorem_key", "") in (
                "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort", "linear_search", "binary_search"
            )
            or (self._render_data and (
                self._render_data.mode == "bars"
                or getattr(self._render_data, "search_data", None) is not None
                or getattr(self._render_data, "sort_event", None) is not None
                or getattr(self._render_data, "tree_data", None) is not None
                or getattr(self._render_data, "graph_data", None) is not None
            ))
        )
        if not is_clipping and not is_algorithms:
            painter.drawText(
                QRectF(16, self.height() - 26, self.width() - 32, 18),
                Qt.AlignRight | Qt.AlignVCenter,
                info_text
            )
        painter.restore()

    # ------------------------------------------------------------------
    # Geometry Mode (Theorems, Transformations)
    # ------------------------------------------------------------------
    def _draw_geometry(self, painter: QPainter, rd: RenderData):
        w, h = self.width(), self.height()
        cx = w / 2.0 + self._pan[0]
        cy = h / 2.0 + self._pan[1]

        # Determine actual geometric extent from shapes to use available space efficiently
        coords_x = []
        coords_y = []
        if rd:
            for poly in rd.polygons:
                for pt in poly.points:
                    coords_x.append(pt[0])
                    coords_y.append(pt[1])
            for line in rd.lines:
                coords_x.extend([line.x1, line.x2])
                coords_y.extend([line.y1, line.y2])
            for pt in rd.points:
                coords_x.append(pt.x)
                coords_y.append(pt.y)
            for arc in rd.arcs:
                coords_x.extend([arc.cx - arc.radius, arc.cx + arc.radius])
                coords_y.extend([arc.cy - arc.radius, arc.cy + arc.radius])
            for t in rd.texts:
                coords_x.extend([t.x - 2.5, t.x + 2.5])
                coords_y.extend([t.y - 1.2, t.y + 1.2])

        if rd and rd.view_bounds:
            bx0, by0, bx1, by1 = rd.view_bounds
            coords_x.extend([bx0, bx1])
            coords_y.extend([by0, by1])

        if coords_x and coords_y:
            shape_xmin = min(coords_x)
            shape_xmax = max(coords_x)
            shape_ymin = min(coords_y)
            shape_ymax = max(coords_y)

            # Center nicely on the shapes with a comfortable margin
            content_w = max(1.0, shape_xmax - shape_xmin)
            content_h = max(1.0, shape_ymax - shape_ymin)
            margin_factor = 1.18

            mid_x = (shape_xmin + shape_xmax) / 2.0
            mid_y = (shape_ymin + shape_ymax) / 2.0
            span_x = content_w * margin_factor
            span_y = content_h * margin_factor
        else:
            bounds = rd.view_bounds if (rd and rd.view_bounds) else (-10, -10, 10, 10)
            xmin, ymin, xmax, ymax = bounds
            mid_x = (xmin + xmax) / 2.0
            mid_y = (ymin + ymax) / 2.0
            span_x = max(1.0, xmax - xmin)
            span_y = max(1.0, ymax - ymin)

        fit_scale = min((w * 0.92) / span_x, (h * 0.90) / span_y)
        scale = fit_scale * self._zoom

        def world_to_screen(wx, wy):
            sx = cx + (wx - mid_x) * scale
            sy = cy - (wy - mid_y) * scale
            return sx, sy

        # Draw subtle coordinate grid & axes
        self._draw_grid_and_axes(painter, cx, cy, scale, mid_x, mid_y)

        if not rd or (not rd.polygons and not rd.lines and not rd.points and not rd.arcs and not rd.texts):
            # Welcome watermark if empty
            painter.save()
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.setFont(get_ui_font(14, weight=500))
            painter.drawText(
                QRectF(0, 0, w, h),
                Qt.AlignCenter,
                "Ready to Visualize — Select a step or configure parameters"
            )
            painter.restore()
            return

        t = self._clip_ease()
        prev_rd = self._prev_render_data if self._prev_render_data and self._prev_render_data.mode == rd.mode else None

        def lerp_pt(a, b, u):
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)

        def fade_color(color, u):
            qc = self._parse_color(color)
            qc.setAlpha(int(qc.alpha() * min(1.0, max(0.0, u))))
            return qc

        pending_labels = []
        screen_polys = []
        screen_lines = []
        screen_points = []

        # 1. Draw Polygons
        for i, poly in enumerate(rd.polygons):
            painter.save()
            pts = list(poly.points)
            appear = t
            if prev_rd and i < len(prev_rd.polygons) and len(prev_rd.polygons[i].points) == len(pts) and pts:
                pts = [lerp_pt(prev_rd.polygons[i].points[k], pts[k], t) for k in range(len(pts))]
                appear = 1.0
            elif prev_rd and prev_rd.polygons and i == len(rd.polygons) - 1 \
                    and len(prev_rd.polygons[-1].points) == len(pts) and pts:
                pts = [lerp_pt(prev_rd.polygons[-1].points[k], pts[k], t) for k in range(len(pts))]
                appear = 1.0
            qpoly = QPolygonF()
            for pt in pts:
                sx, sy = world_to_screen(pt[0], pt[1])
                qpoly.append(QPointF(sx, sy))

            painter.setBrush(QBrush(fade_color(poly.fill_color, appear)))
            pen = QPen(fade_color(poly.stroke_color, appear), poly.stroke_width)
            painter.setPen(pen)
            painter.drawPolygon(qpoly)

            screen_pts = [(p.x(), p.y()) for p in qpoly]
            screen_polys.append(screen_pts)

            if poly.label:
                centroid_x = sum(pt[0] for pt in poly.points) / len(poly.points)
                centroid_y = sum(pt[1] for pt in poly.points) / len(poly.points)

                # Skip polygon label if a custom Text2D is co-located at this centroid
                has_colocated_text = any(
                    math.hypot(txt.x - centroid_x, txt.y - centroid_y) < 0.6
                    for txt in rd.texts
                )
                if not has_colocated_text:
                    pending_labels.append({
                        "kind": "polygon",
                        "text": poly.label,
                        "color": COLORS.get("text_primary", "#FFFFFF"),
                        "font": get_mono_font(12, weight=600),
                        "screen_pts": screen_pts,
                        "priority": 20,
                    })

            painter.restore()

        # 2. Draw Arcs (Angle markers)
        for i, arc in enumerate(rd.arcs):
            painter.save()
            span = arc.span_angle_deg * t
            asx, asy = world_to_screen(arc.cx, arc.cy)
            r_screen = arc.radius * scale
            rect = QRectF(asx - r_screen, asy - r_screen, 2 * r_screen, 2 * r_screen)

            pen = QPen(fade_color(arc.color, 0.35 + 0.65 * t), 2)
            painter.setPen(pen)
            fill = QColor(COLORS["accent_gold"])
            fill.setAlpha(int(32 * t))
            painter.setBrush(QBrush(fill))
            painter.drawPie(rect, int(arc.start_angle_deg * 16), int(span * 16))

            if arc.label:
                mid_angle = math.radians(arc.start_angle_deg + arc.span_angle_deg / 2.0)
                lx = asx + (r_screen + 16) * math.cos(mid_angle)
                ly = asy - (r_screen + 16) * math.sin(mid_angle)
                pending_labels.append({
                    "kind": "free",
                    "text": arc.label,
                    "color": arc.color,
                    "font": get_mono_font(11, weight=500),
                    "anchor": (lx, ly),
                    "outward": (math.cos(mid_angle), -math.sin(mid_angle)),
                    "priority": 15,
                })

            painter.restore()

        # 3. Draw Lines
        for i, line in enumerate(rd.lines):
            painter.save()
            x1, y1, x2, y2 = line.x1, line.y1, line.x2, line.y2
            if prev_rd and i < len(prev_rd.lines):
                pl = prev_rd.lines[i]
                x1 = pl.x1 + (line.x1 - pl.x1) * t
                y1 = pl.y1 + (line.y1 - pl.y1) * t
                x2 = pl.x2 + (line.x2 - pl.x2) * t
                y2 = pl.y2 + (line.y2 - pl.y2) * t
            else:
                x2 = x1 + (x2 - x1) * t
                y2 = y1 + (y2 - y1) * t
            sx1, sy1 = world_to_screen(x1, y1)
            sx2, sy2 = world_to_screen(x2, y2)

            pen = QPen(self._parse_color(line.color), line.width)
            if line.dashed:
                pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(sx1, sy1), QPointF(sx2, sy2))

            screen_lines.append(((sx1, sy1), (sx2, sy2), line.width))
            if line.label:
                mx = (sx1 + sx2) * 0.5
                my = (sy1 + sy2) * 0.5
                dx = sx2 - sx1
                dy = sy2 - sy1
                pending_labels.append({
                    "kind": "line",
                    "text": line.label,
                    "color": line.color,
                    "font": get_mono_font(11, weight=500),
                    "anchor": (mx, my),
                    "outward": (-dy, dx),
                    "priority": 18,
                })

            painter.restore()

        # 4. Draw Points
        for i, pt in enumerate(rd.points):
            painter.save()
            px, py = pt.x, pt.y
            if prev_rd and i < len(prev_rd.points):
                px = prev_rd.points[i].x + (pt.x - prev_rd.points[i].x) * t
                py = prev_rd.points[i].y + (pt.y - prev_rd.points[i].y) * t
            sx, sy = world_to_screen(px, py)
            color = self._parse_color(pt.color)
            rad = pt.radius * (0.45 + 0.55 * t) if not (prev_rd and i < len(prev_rd.points)) else pt.radius
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(COLORS["bg_app"]), 1.5))
            painter.drawEllipse(QPointF(sx, sy), rad, rad)

            screen_points.append((sx, sy, rad))
            if pt.label:
                pending_labels.append({
                    "kind": "point",
                    "text": pt.label,
                    "color": pt.color,
                    "font": get_ui_font(11, weight=600),
                    "anchor": (sx, sy),
                    "outward": outward_from_centroid((sx, sy), (cx, cy)),
                    "priority": 5,
                    "pill": True,
                })

            painter.restore()

        # 5. Draw Custom Texts
        for txt in rd.texts:
            sx, sy = world_to_screen(txt.x, txt.y)
            is_banner = txt.font_size >= 12
            pending_labels.append({
                "kind": "banner" if is_banner else "free",
                "text": txt.text,
                "color": txt.color,
                "font": get_mono_font(max(12, txt.font_size), weight=600 if txt.bold else 500),
                "anchor": (sx, sy),
                "preferred": (sx - 70, sy - 12),
                "priority": 25 if is_banner else 12,
                "pill": is_banner,
            })

        self._last_placed_labels = []
        self._place_and_draw_labels(painter, pending_labels, screen_polys, screen_lines, screen_points)

    def _make_label_placer(self, extra_reserved=None) -> LabelPlacer:
        w, h = float(self.width()), float(self.height())
        reserved = [(8.0, h - 30.0, w - 16.0, 26.0)]
        if extra_reserved:
            reserved.extend(extra_reserved)
        placer = LabelPlacer(
            viewport=(0.0, 0.0, w, h),
            margin=10.0,
            reserved=reserved,
            gap=14.0,
        )
        self._label_placer = placer
        return placer

    def _place_and_draw_labels(self, painter: QPainter, pending: list, polys: list, lines: list, points: list):
        if not pending:
            self._last_placed_labels = []
            return
        placer = self._make_label_placer()
        for poly in polys:
            placer.add_polygon(poly)
        for p1, p2, width in lines:
            placer.add_segment(p1, p2, thickness=max(2.0, float(width)))
        for sx, sy, rad in points:
            placer.add_point((sx, sy), radius=max(6.0, float(rad) + 3.0))

        specs = []
        meta = []
        for item in pending:
            painter.setFont(item["font"])
            fm = painter.fontMetrics()
            text = item["text"]
            max_w = max(80.0, self.width() - 28.0)
            tw = min(max(36.0, fm.horizontalAdvance(text) + 16.0), max_w)
            th = max(20.0, fm.height() + 8.0)
            if item["kind"] == "polygon":
                anchor = polygon_bbox_anchor(item["screen_pts"])
                outward = (0.0, -1.0)
            else:
                anchor = item["anchor"]
                outward = item.get("outward")
            specs.append(
                LabelSpec(
                    text=text,
                    anchor=anchor,
                    width=tw,
                    height=th,
                    kind=item["kind"],
                    outward=outward,
                    preferred=item.get("preferred"),
                    priority=item.get("priority", 10),
                )
            )
            meta.append(item)

        placed = placer.place_all(specs)
        self._last_placed_labels = list(placed)
        by_key = {
            (p.text, round(p.anchor[0], 1), round(p.anchor[1], 1)): p
            for p in placed
        }
        for item, spec in zip(meta, specs):
            key = (spec.text, round(spec.anchor[0], 1), round(spec.anchor[1], 1))
            result = by_key.get(key) or next((p for p in placed if p.text == spec.text), None)
            if result:
                self._draw_placed_annotation(
                    painter,
                    result,
                    item["color"],
                    item["font"],
                    pill=bool(item.get("pill")),
                )

    def _draw_placed_annotation(
        self, painter: QPainter, placed: PlacedLabel, color: Any, font: QFont, pill: bool = False
    ):
        painter.save()
        x, y, w, h = placed.rect
        rect = QRectF(x, y, w, h)
        qc = self._parse_color(color)
        tip = QPointF(placed.anchor[0], placed.anchor[1])
        cx, cy = x + w * 0.5, y + h * 0.5

        if placed.leader:
            leader = QPen(Qt.DashLine)
            leader.setWidthF(1.0)
            leader.setColor(QColor(qc.red(), qc.green(), qc.blue(), 120))
            painter.setPen(leader)
            painter.drawLine(tip, QPointF(cx, cy))

        if pill or placed.kind in ("polygon", "banner", "point"):
            fill = QColor(255, 255, 255, 228)
            painter.setBrush(QBrush(fill))
            painter.setPen(QPen(QColor(qc.red(), qc.green(), qc.blue(), 70), 1.0))
            painter.drawRoundedRect(rect, 7, 7)

        painter.setFont(font)
        painter.setPen(QPen(qc))
        painter.drawText(rect, Qt.AlignCenter, placed.text)
        painter.restore()

    def _smart_label(self, painter: QPainter, text: str, anchor: Tuple[float, float], color: Any,
                     font: QFont, kind: str = "point", outward: Optional[Tuple[float, float]] = None,
                     pill: bool = False, priority: int = 2):
        if not text:
            return
        placer = getattr(self, "_label_placer", None)
        if placer is None:
            placer = self._make_label_placer()
            self._label_placer = placer
        painter.setFont(font)
        fm = painter.fontMetrics()
        tw = min(max(32.0, fm.horizontalAdvance(text) + 14.0), max(80.0, self.width() - 28.0))
        th = max(18.0, fm.height() + 6.0)
        spec = LabelSpec(
            text=text,
            anchor=(float(anchor[0]), float(anchor[1])),
            width=tw,
            height=th,
            kind=kind,
            outward=outward,
            priority=priority,
        )
        placed = placer.place(spec)
        self._last_placed_labels = list(placer.placed)
        self._draw_placed_annotation(painter, placed, color, font, pill=pill)

    def _fit_label_rect(self, rect: QRectF) -> QRectF:
        margin = 8.0
        max_width = max(1.0, self.width() - margin * 2)
        max_height = max(1.0, self.height() - margin * 2)
        rect.setWidth(min(rect.width(), max_width))
        rect.setHeight(min(rect.height(), max_height))
        rect.moveLeft(max(margin, min(rect.left(), self.width() - margin - rect.width())))
        rect.moveTop(max(margin, min(rect.top(), self.height() - margin - rect.height())))
        return rect

    def _draw_grid_and_axes(self, painter: QPainter, cx, cy, scale, mid_x, mid_y):
        w, h = self.width(), self.height()
        painter.save()

        # Origin in screen coordinates
        ox = cx - mid_x * scale
        oy = cy + mid_y * scale

        step_world = 1.0
        while step_world * scale < 45:
            step_world *= 2.0
        while step_world * scale > 110:
            step_world /= 2.0

        # 1. Subtle Grid Lines (if toggled on)
        if getattr(self, "_show_grid", True):
            grid_pen = QPen(QColor(COLORS["grid_line"]))
            grid_pen.setWidth(1)
            grid_pen.setStyle(Qt.DotLine)
            painter.setPen(grid_pen)

            # Vertical grid lines
            x = ox
            while x >= 0:
                painter.drawLine(QPointF(x, 0), QPointF(x, h))
                x -= step_world * scale
            x = ox + step_world * scale
            while x <= w:
                painter.drawLine(QPointF(x, 0), QPointF(x, h))
                x += step_world * scale

            # Horizontal grid lines
            y = oy
            while y >= 0:
                painter.drawLine(QPointF(0, y), QPointF(w, y))
                y -= step_world * scale
            y = oy + step_world * scale
            while y <= h:
                painter.drawLine(QPointF(0, y), QPointF(w, y))
                y += step_world * scale

        if getattr(self, "_show_grid", True):
            axis_pen = QPen(QColor(COLORS["axis_line"]))
            axis_pen.setWidth(1)
            painter.setPen(axis_pen)

            if 0 <= ox <= w:
                painter.drawLine(QPointF(ox, 0), QPointF(ox, h))
            if 0 <= oy <= h:
                painter.drawLine(QPointF(0, oy), QPointF(w, oy))

            tick_pen = QPen(QColor(COLORS["axis_line"]), 1)
            painter.setPen(tick_pen)

            if 0 <= oy <= h:
                x = ox + step_world * scale
                while x <= w:
                    painter.drawLine(QPointF(x, oy - 2), QPointF(x, oy + 2))
                    x += step_world * scale
                x = ox - step_world * scale
                while x >= 0:
                    painter.drawLine(QPointF(x, oy - 2), QPointF(x, oy + 2))
                    x -= step_world * scale

            if 0 <= ox <= w:
                y = oy - step_world * scale
                while y >= 0:
                    painter.drawLine(QPointF(ox - 2, y), QPointF(ox + 2, y))
                    y -= step_world * scale
                y = oy + step_world * scale
                while y <= h:
                    painter.drawLine(QPointF(ox - 2, y), QPointF(ox + 2, y))
                    y += step_world * scale

        painter.restore()

    # ------------------------------------------------------------------
    # Graph Algorithms Mode (Prim, Kruskal, Dijkstra)
    # ------------------------------------------------------------------
    def _draw_graph(self, painter: QPainter, gd: dict):
        w, h = float(self.width()), float(self.height())
        nodes = list(gd.get("nodes", []))
        edges = list(gd.get("edges", []))
        if not nodes:
            painter.save()
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.setFont(get_ui_font(14, weight=400))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "Graph is empty.")
            painter.restore()
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 1. Understated Context Header (No bulky card, no decorative banner)
        algo_title = "Prim's Algorithm" if gd.get("type") == "prim" else ("Kruskal's Algorithm" if gd.get("type") == "kruskal" else "MST Comparison")
        op_label = str(gd.get("status_text", "")).strip()
        for pfx in ("Prim's Algorithm:", "Kruskal's Algorithm:", "Prim's Algorithm -", "Kruskal's Algorithm -", "Prim's:", "Kruskal's:"):
            if op_label.lower().startswith(pfx.lower()):
                op_label = op_label[len(pfx):].strip()
        if "Total weight" in op_label:
            op_label = op_label.split("Total weight", 1)[0].rstrip(" .;")
        if len(op_label) > 65:
            op_label = op_label[:62] + "..."

        top_y = 16.0
        painter.setFont(get_ui_font(12, weight=600))
        painter.setPen(QPen(QColor("#64748B")))
        context_str = f"{algo_title}  ·  {op_label}" if op_label else algo_title
        painter.drawText(QRectF(22.0, top_y, w - 190.0, 22.0), Qt.AlignLeft | Qt.AlignVCenter, context_str)

        # Compact metric chip at top right
        tot_wt = gd.get("total_weight")
        if tot_wt is not None:
            wt_text = f"MST Weight: {tot_wt}"
            painter.setFont(get_mono_font(11, weight=600))
            fm = painter.fontMetrics()
            chip_w = fm.horizontalAdvance(wt_text) + 20.0
            chip_rect = QRectF(w - chip_w - 22.0, top_y, chip_w, 24.0)
            painter.setBrush(QBrush(QColor("#F8FAFC")))
            painter.setPen(QPen(QColor("#E2E8F0"), 1.0))
            painter.drawRoundedRect(chip_rect, 6.0, 6.0)
            painter.setPen(QPen(QColor("#0F172A")))
            painter.drawText(chip_rect, Qt.AlignCenter, wt_text)

        # 2. Generous Coordinate Transformation (Maximizes graph space)
        xs = [float(n.get("x", 0.0)) for n in nodes]
        ys = [float(n.get("y", 0.0)) for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)

        usable_w = max(100.0, w - 100.0)
        usable_h = max(100.0, h - 80.0)
        scale = min(usable_w / span_x, usable_h / span_y) * 0.78 * self._zoom
        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0
        cx = w / 2.0 + self._pan[0] - mid_x * scale
        cy = h / 2.0 + 16.0 + self._pan[1] + mid_y * scale

        pos = {}
        for n in nodes:
            nid = str(n.get("id", ""))
            nx = cx + float(n.get("x", 0.0)) * scale
            ny = cy - float(n.get("y", 0.0)) * scale
            pos[nid] = (nx, ny)

        radius = max(22.0, min(28.0, 24.0 * self._zoom))

        # 3. Draw Edges with Clear States and Readable Weights
        edge_colors = {
            "selected": QColor("#10B981"),
            "mst": QColor("#10B981"),
            "tree": QColor("#10B981"),
            "active": QColor("#6C5CE7"),
            "candidate": QColor("#F59E0B"),
            "path": QColor("#F59E0B"),
            "rejected": QColor("#EF4444"),
            "backtrack": QColor("#EF4444"),
            "cycle": QColor("#EF4444"),
            "relaxed": QColor("#8B5CF6"),
            "idle": QColor("#E2E8F0"),
            "unvisited": QColor("#CBD5E1"),
        }
        for edge in edges:
            u, v = str(edge.get("u", "")), str(edge.get("v", ""))
            if u not in pos or v not in pos:
                continue
            ux, uy = pos[u]
            vx, vy = pos[v]
            st = str(edge.get("state", "unvisited")).lower()
            ec = edge_colors.get(st, edge_colors["unvisited"])
            ew = 3.6 if st in ("selected", "mst", "tree", "active") else (2.4 if st in ("candidate", "path", "rejected", "backtrack", "cycle") else 1.6)

            dist = math.hypot(vx - ux, vy - uy)
            if dist > 2 * radius:
                dx, dy = (vx - ux) / dist, (vy - uy) / dist
                sx1, sy1 = ux + dx * radius, uy + dy * radius
                sx2, sy2 = vx - dx * radius, vy - dy * radius
            else:
                sx1, sy1, sx2, sy2 = ux, uy, vx, vy

            painter.save()
            pen = QPen(ec, ew)
            if st in ("candidate", "path", "rejected", "backtrack", "cycle"):
                pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(sx1, sy1), QPointF(sx2, sy2))

            # Red 'X' rejection indicator for cycle-creating edges
            if st in ("rejected", "backtrack", "cycle"):
                mx, my = (sx1 + sx2) * 0.5, (sy1 + sy2) * 0.5
                painter.setBrush(QBrush(QColor("#FEE2E2")))
                painter.setPen(QPen(QColor("#EF4444"), 1.2))
                painter.drawEllipse(QPointF(mx, my), 8.0, 8.0)
                painter.setPen(QPen(QColor("#B91C1C"), 1.8))
                painter.drawLine(QPointF(mx - 3.5, my - 3.5), QPointF(mx + 3.5, my + 3.5))
                painter.drawLine(QPointF(mx - 3.5, my + 3.5), QPointF(mx + 3.5, my - 3.5))

            w_val = edge.get("weight")
            if w_val is not None:
                mx = (ux + vx) * 0.5
                my = (uy + vy) * 0.5
                if dist > 0.001:
                    nx_perp = -(vy - uy) / dist * 15.0
                    ny_perp = (vx - ux) / dist * 15.0
                else:
                    nx_perp, ny_perp = 0.0, -15.0
                pill_x = mx + nx_perp - 14.0
                pill_y = my + ny_perp - 11.0
                pill_rect = QRectF(pill_x, pill_y, 28.0, 22.0)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                border_c = ec if st in ("selected", "mst", "active") else QColor("#CBD5E1")
                painter.setPen(QPen(border_c, 1.2))
                painter.drawRoundedRect(pill_rect, 6.0, 6.0)
                painter.setFont(get_mono_font(11, weight=700))
                text_c = ec if st in ("selected", "mst", "active") else QColor("#334155")
                painter.setPen(QPen(text_c))
                painter.drawText(pill_rect, Qt.AlignCenter, str(w_val))
            painter.restore()

        # 4. Draw Graph Vertices (Crisp, High-Contrast, No Obtrusive Badges)
        fills = {
            "current": QColor("#EEF2FF"),
            "active": QColor("#EEF2FF"),
            "visited": QColor("#ECFDF5"),
            "mst": QColor("#ECFDF5"),
            "frontier": QColor("#FEF3C7"),
            "in_queue": QColor("#FEF3C7"),
            "unvisited": QColor("#FFFFFF"),
        }
        strokes = {
            "current": QColor("#6C5CE7"),
            "active": QColor("#6C5CE7"),
            "visited": QColor("#10B981"),
            "mst": QColor("#10B981"),
            "frontier": QColor("#F59E0B"),
            "in_queue": QColor("#F59E0B"),
            "unvisited": QColor("#94A3B8"),
        }
        texts = {
            "current": QColor("#4338CA"),
            "active": QColor("#4338CA"),
            "visited": QColor("#065F46"),
            "mst": QColor("#065F46"),
            "frontier": QColor("#92400E"),
            "in_queue": QColor("#92400E"),
            "unvisited": QColor("#1E293B"),
        }
        for n in nodes:
            nid = str(n.get("id", ""))
            if nid not in pos:
                continue
            nx, ny = pos[nid]
            st = str(n.get("state", "unvisited")).lower()
            fc = fills.get(st, fills["unvisited"])
            sc = strokes.get(st, strokes["unvisited"])
            tc = texts.get(st, texts["unvisited"])

            painter.save()
            painter.setBrush(QBrush(fc))
            painter.setPen(QPen(sc, 2.5 if st in ("current", "active", "visited", "mst") else 1.8))
            painter.drawEllipse(QPointF(nx, ny), radius, radius)

            lbl = str(n.get("label") or nid)
            short_lbl = nid if len(lbl) > 5 else lbl
            painter.setFont(get_ui_font(13, weight=700))
            painter.setPen(QPen(tc))
            painter.drawText(QRectF(nx - radius, ny - radius, radius * 2, radius * 2), Qt.AlignCenter, short_lbl)
            painter.restore()

        painter.restore()

    # ------------------------------------------------------------------
    # Tree Traversals & BST Mode
    # ------------------------------------------------------------------
    def _draw_tree(self, painter: QPainter, td: dict):
        w, h = float(self.width()), float(self.height())
        nodes = list(td.get("nodes", []))
        edges = list(td.get("edges", []))
        if not nodes:
            painter.save()
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.setFont(get_ui_font(14, weight=400))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "Tree is empty.")
            painter.restore()
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        hud_h, dock_h = 76.0, 86.0
        hud_w = min(w - 48.0, 760.0)
        hud_x = (w - hud_w) / 2.0
        hud_y = 14.0

        # 1. Top HUD Card
        painter.setBrush(QBrush(QColor(COLORS["bg_panel_alt"])))
        painter.setPen(QPen(QColor(COLORS["border"]), 1.0))
        painter.drawRoundedRect(QRectF(hud_x, hud_y, hud_w, hud_h), 10.0, 10.0)

        kind = str(td.get("type", "Tree / BST")).upper()
        painter.setBrush(QBrush(QColor(COLORS.get("selected_bg", "#F3F0FF"))))
        painter.setPen(QPen(QColor(COLORS.get("border_focus", "#6C5CE7")), 1.0))
        badge_w = max(90.0, min(140.0, 14.0 * len(kind)))
        painter.drawRoundedRect(QRectF(hud_x + 10.0, hud_y + 10.0, badge_w, hud_h - 20.0), 8.0, 8.0)
        painter.setFont(get_mono_font(12, weight=700))
        painter.setPen(QPen(QColor(COLORS.get("accent_purple", "#6C5CE7"))))
        painter.drawText(QRectF(hud_x + 10.0, hud_y + 10.0, badge_w, hud_h - 20.0), Qt.AlignCenter, kind)

        status_text = td.get("status_text", "")
        comparison_text = td.get("comparison_text", "")
        text_x = hud_x + badge_w + 20.0
        text_w = hud_w - badge_w - 30.0

        painter.setFont(get_ui_font(13, weight=600))
        painter.setPen(QPen(QColor(COLORS["text_primary"])))
        painter.drawText(QRectF(text_x, hud_y + 12.0, text_w, 24.0), Qt.AlignLeft | Qt.AlignVCenter, status_text)

        if comparison_text:
            painter.setFont(get_mono_font(12, weight=500))
            painter.setPen(QPen(QColor(COLORS.get("accent_blue", "#3B82F6"))))
            painter.drawText(QRectF(text_x, hud_y + 40.0, text_w, 22.0), Qt.AlignLeft | Qt.AlignVCenter, comparison_text)

        # 2. Coordinates
        xs = [float(n.get("x", 0.0)) for n in nodes]
        ys = [float(n.get("y", 0.0)) for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)

        usable_w = max(80.0, w - 80.0)
        usable_h = max(80.0, h - hud_h - dock_h - 50.0)
        scale_x = usable_w / max(1.0, span_x * 1.25)
        scale_y = usable_h / max(1.0, span_y * 1.25)
        scale = min(scale_x, scale_y) * self._zoom

        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0
        cx = w / 2.0 + self._pan[0] - mid_x * scale
        cy = hud_y + hud_h + 20.0 + usable_h / 2.0 + self._pan[1] + mid_y * scale

        pos = {}
        for n in nodes:
            k = n.get("key")
            nx = cx + float(n.get("x", 0.0)) * scale
            ny = cy - float(n.get("y", 0.0)) * scale
            pos[k] = (nx, ny)

        radius = max(18.0, min(24.0, 20.0 * self._zoom))

        # 3. Draw Branches
        cand_side = td.get("candidate_side")
        for e in edges:
            u, v = e.get("u"), e.get("v")
            side = e.get("side", "")
            if u not in pos or v not in pos:
                continue
            ux, uy = pos[u]
            vx, vy = pos[v]
            dist = math.hypot(vx - ux, vy - uy)
            if dist > 2 * radius:
                dx, dy = (vx - ux) / dist, (vy - uy) / dist
                sx1, sy1 = ux + dx * radius, uy + dy * radius
                sx2, sy2 = vx - dx * radius, vy - dy * radius
            else:
                sx1, sy1, sx2, sy2 = ux, uy, vx, vy

            is_candidate = (e.get("candidate") or (e.get("state") == "candidate") or (side == cand_side and e.get("parent_active")))
            painter.save()
            pen = QPen(QColor("#F59E0B" if is_candidate else "#CBD5E1"), 2.5 if is_candidate else 1.8)
            if is_candidate:
                pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(sx1, sy1), QPointF(sx2, sy2))

            # Direction Pill ("L" or "R") at 40% of branch
            if side:
                bx = sx1 + (sx2 - sx1) * 0.4
                by = sy1 + (sy2 - sy1) * 0.4
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#F59E0B" if is_candidate else "#94A3B8"), 1.0))
                painter.drawEllipse(QPointF(bx, by), 8.0, 8.0)
                painter.setFont(get_mono_font(9, weight=700))
                painter.setPen(QPen(QColor("#B45309" if is_candidate else "#64748B")))
                painter.drawText(QRectF(bx - 8.0, by - 8.0, 16.0, 16.0), Qt.AlignCenter, side)
            painter.restore()

        # 4. Draw Nodes
        fills = {
            "current": QColor("#6C5CE7"),
            "comparing": QColor("#F59E0B"),
            "visited": QColor("#E0E7FF"),
            "path": QColor("#DDD6FE"),
            "successor": QColor("#EC4899"),
            "found": QColor("#10B981"),
            "unvisited": QColor("#FFFFFF"),
        }
        strokes = {
            "current": QColor("#4338CA"),
            "comparing": QColor("#D97706"),
            "visited": QColor("#6366F1"),
            "path": QColor("#8B5CF6"),
            "successor": QColor("#BE185D"),
            "found": QColor("#059669"),
            "unvisited": QColor("#94A3B8"),
        }
        texts = {
            "current": QColor("#FFFFFF"),
            "comparing": QColor("#FFFFFF"),
            "visited": QColor("#3730A3"),
            "path": QColor("#4C1D95"),
            "successor": QColor("#FFFFFF"),
            "found": QColor("#FFFFFF"),
            "unvisited": QColor("#1E293B"),
        }
        for n in nodes:
            k = n.get("key")
            if k not in pos:
                continue
            nx, ny = pos[k]
            st = str(n.get("state", "unvisited")).lower()
            fc = fills.get(st, fills["unvisited"])
            sc = strokes.get(st, strokes["unvisited"])
            tc = texts.get(st, texts["unvisited"])

            painter.save()
            if st in ("current", "found"):
                halo = QColor(fc)
                halo.setAlpha(45)
                painter.setBrush(QBrush(halo))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(nx, ny), radius + 6.0, radius + 6.0)

            painter.setBrush(QBrush(fc))
            painter.setPen(QPen(sc, 2.2 if st in ("current", "comparing", "found") else 1.6))
            painter.drawEllipse(QPointF(nx, ny), radius, radius)

            painter.setFont(get_mono_font(13, weight=700))
            painter.setPen(QPen(tc))
            painter.drawText(QRectF(nx - radius, ny - radius, radius * 2, radius * 2), Qt.AlignCenter, str(k))
            painter.restore()

        # 5. Bottom Sequence Dock
        dock_w = min(w - 48.0, 760.0)
        dock_x = (w - dock_w) / 2.0
        dock_y = h - dock_h - 12.0

        painter.setBrush(QBrush(QColor(COLORS["bg_panel_alt"])))
        painter.setPen(QPen(QColor(COLORS["border"]), 1.0))
        painter.drawRoundedRect(QRectF(dock_x, dock_y, dock_w, dock_h), 10.0, 10.0)

        struct_lbl = str(td.get("sequence_label", "Traversal / Visited Sequence"))
        painter.setFont(get_ui_font(12, weight=600))
        painter.setPen(QPen(QColor(COLORS["text_secondary"])))
        painter.drawText(QRectF(dock_x + 14.0, dock_y + 8.0, dock_w - 28.0, 18.0), Qt.AlignLeft | Qt.AlignVCenter, struct_lbl)

        seq = list(td.get("sequence", []))
        if not seq:
            painter.setFont(get_mono_font(12, weight=400))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(dock_x + 14.0, dock_y + 36.0, dock_w - 28.0, 36.0), Qt.AlignLeft | Qt.AlignVCenter, "(Empty)")
        else:
            chip_count = len(seq)
            chip_w = min(72.0, max(36.0, (dock_w - 28.0 - (chip_count - 1) * 8.0) / max(1, chip_count)))
            for i, val in enumerate(seq):
                cx_c = dock_x + 14.0 + i * (chip_w + 8.0)
                cy_c = dock_y + 34.0
                is_latest = (i == chip_count - 1)
                painter.setBrush(QBrush(QColor("#6C5CE7" if is_latest else "#EAE6FF")))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(QRectF(cx_c, cy_c, chip_w, 34.0), 8.0, 8.0)
                painter.setFont(get_mono_font(12, weight=700))
                painter.setPen(QPen(QColor("#FFFFFF" if is_latest else "#4D3BB8")))
                painter.drawText(QRectF(cx_c, cy_c, chip_w, 34.0), Qt.AlignCenter, str(val))

        painter.restore()

    # ------------------------------------------------------------------
    # Search Tiles Mode (Linear Search & Binary Search)
    # ------------------------------------------------------------------
    def _draw_search_tiles(self, painter: QPainter, sd: dict):
        w, h = self.width(), self.height()
        stype = sd.get("type", "linear")
        arr = sd.get("array", [])
        target = sd.get("target", 0)
        n = len(arr)
        if n == 0:
            painter.save()
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.setFont(get_ui_font(14, weight=400))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "Array is empty.")
            painter.restore()
            return

        painter.save()

        # -------------------------------------------------------------
        # 1. Top HUD / Target & Status Card
        # -------------------------------------------------------------
        hud_h = 68
        hud_w = min(w - 60, 720)
        hud_x = (w - hud_w) / 2.0
        hud_y = 18

        # HUD background card
        painter.setBrush(QBrush(QColor(COLORS["bg_panel_alt"])))
        painter.setPen(QPen(QColor(COLORS["border"]), 1))
        painter.drawRoundedRect(QRectF(hud_x, hud_y, hud_w, hud_h), 8, 8)

        # Target badge (left side of HUD)
        target_badge_w = 150
        painter.setBrush(QBrush(QColor(COLORS["selected_bg"])))
        painter.setPen(QPen(QColor(COLORS["border_focus"]), 1))
        painter.drawRoundedRect(QRectF(hud_x + 10, hud_y + 10, target_badge_w, hud_h - 20), 6, 6)

        painter.setFont(get_mono_font(12, weight=600))
        painter.setPen(QPen(QColor(COLORS["text_secondary"])))
        painter.drawText(QRectF(hud_x + 10, hud_y + 13, target_badge_w, 14), Qt.AlignCenter, "SEARCH TARGET")

        painter.setFont(get_mono_font(20, weight=700))
        painter.setPen(QPen(QColor(COLORS["accent_gold"])))
        painter.drawText(QRectF(hud_x + 10, hud_y + 28, target_badge_w, 24), Qt.AlignCenter, str(target))

        # Status text & comparison (right side of HUD)
        status_text = sd.get("status", "")
        comparison_text = sd.get("comparison", "")

        found_idx = sd.get("found_index")
        painter.setFont(get_ui_font(14, weight=600))
        if found_idx is not None and found_idx >= 0:
            painter.setPen(QPen(QColor(COLORS["success"])))
        elif found_idx == -1:
            painter.setPen(QPen(QColor(COLORS["danger"])))
        else:
            painter.setPen(QPen(QColor(COLORS["text_primary"])))

        painter.drawText(
            QRectF(hud_x + target_badge_w + 20, hud_y + 11, hud_w - target_badge_w - 30, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            status_text
        )

        if comparison_text:
            painter.setFont(get_mono_font(13, weight=400))
            painter.setPen(QPen(QColor(COLORS["accent_teal"])))
            painter.drawText(
                QRectF(hud_x + target_badge_w + 20, hud_y + 36, hud_w - target_badge_w - 30, 20),
                Qt.AlignLeft | Qt.AlignVCenter,
                comparison_text
            )

        # -------------------------------------------------------------
        # 2. Horizontal Row of Number Tiles
        # -------------------------------------------------------------
        avail_w = w - 80
        tile_spacing = max(6, min(16, int(avail_w / (n * 3))))
        total_spacing = (n - 1) * tile_spacing
        target_tile_w = (avail_w - total_spacing) / n
        tile_w = max(42.0, min(80.0, target_tile_w))
        tile_h = tile_w * 1.18
        row_w = n * tile_w + (n - 1) * tile_spacing
        start_x = (w - row_w) / 2.0 + self._pan[0]
        start_y = (h / 2.0) - (tile_h / 2.0) + 15 + self._pan[1]

        # -------------------------------------------------------------
        # 3. Metaphor Visuals: Scanner Rail / Search Zone Bracket
        # -------------------------------------------------------------
        if stype == "linear":
            cur_i = sd.get("current_index")
            rail_y = start_y - 28
            painter.setPen(QPen(QColor(COLORS["axis_line"]), 2))
            painter.drawLine(QPointF(start_x - 12, rail_y), QPointF(start_x + row_w + 12, rail_y))

            if cur_i is not None and 0 <= cur_i < n:
                cur_tile_cx = start_x + cur_i * (tile_w + tile_spacing) + tile_w / 2.0

                # Glowing scanner cursor on rail
                painter.setBrush(QBrush(QColor(COLORS["accent_gold"])))
                painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
                painter.drawEllipse(QPointF(cur_tile_cx, rail_y), 5, 5)

                # Laser scanner beam pointing down to tile
                beam_color = QColor(COLORS["accent_gold"])
                beam_color.setAlpha(145)
                grad_pen = QPen(beam_color, 2, Qt.DashLine)
                painter.setPen(grad_pen)
                painter.drawLine(QPointF(cur_tile_cx, rail_y + 5), QPointF(cur_tile_cx, start_y))

        elif stype == "binary":
            low = sd.get("low")
            high = sd.get("high")
            if low is not None and high is not None and low <= high and low < n and high >= 0:
                clamped_low = max(0, min(n - 1, low))
                clamped_high = max(0, min(n - 1, high))
                zone_x1 = start_x + clamped_low * (tile_w + tile_spacing)
                zone_x2 = start_x + clamped_high * (tile_w + tile_spacing) + tile_w
                zone_y = start_y - 24

                zone_pen = QPen(QColor(COLORS["accent_teal"]), 2)
                painter.setPen(zone_pen)
                painter.drawLine(QPointF(zone_x1, zone_y), QPointF(zone_x2, zone_y))
                painter.drawLine(QPointF(zone_x1, zone_y), QPointF(zone_x1, zone_y + 8))
                painter.drawLine(QPointF(zone_x2, zone_y), QPointF(zone_x2, zone_y + 8))

                painter.setFont(QFont("Cascadia Mono", 8, QFont.Bold))
                painter.setPen(QPen(QColor(COLORS["accent_teal"])))
                painter.drawText(QRectF(zone_x1, zone_y - 18, zone_x2 - zone_x1, 16),
                                 Qt.AlignCenter, f"ACTIVE SEARCH ZONE [{clamped_low}..{clamped_high}]")

        # -------------------------------------------------------------
        # 4. Render Individual Tiles
        # -------------------------------------------------------------
        for i in range(n):
            val = arr[i]
            tx = start_x + i * (tile_w + tile_spacing)
            ty = start_y
            tile_rect = QRectF(tx, ty, tile_w, tile_h)

            is_match = (i == sd.get("found_index"))
            is_linear_current = (stype == "linear" and i == sd.get("current_index"))
            is_linear_examined = (stype == "linear" and i in sd.get("examined_indices", []))

            is_binary_mid = (stype == "binary" and i == sd.get("mid"))
            is_binary_eliminated = (stype == "binary" and i in sd.get("eliminated_indices", []))
            is_binary_low = (stype == "binary" and i == sd.get("low"))
            is_binary_high = (stype == "binary" and i == sd.get("high"))

            if is_match:
                # MATCH LIGHTS UP: Emerald glow & rich fill
                glow_rect = QRectF(tx - 6, ty - 6, tile_w + 12, tile_h + 12)
                glow_color = QColor(COLORS["success"])
                glow_color.setAlpha(45)
                painter.setBrush(QBrush(glow_color))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(glow_rect, 14, 14)

                painter.setBrush(QBrush(QColor("#E8F6F0")))
                painter.setPen(QPen(QColor(COLORS["success"]), 2.5))
                painter.drawRoundedRect(tile_rect, 10, 10)

                font_px = max(13, int(tile_w * 0.36))
                painter.setFont(get_mono_font(font_px, weight=700))
                painter.setPen(QPen(QColor(COLORS["text_primary"])))
                painter.drawText(tile_rect, Qt.AlignCenter, str(val))

                painter.setFont(get_ui_font(12, weight=600))
                painter.setPen(QPen(QColor(COLORS["success"])))
                painter.drawText(QRectF(tx - 20, ty - 22, tile_w + 40, 18), Qt.AlignCenter, "✓ MATCH")

            elif is_linear_current or (is_binary_mid and not is_match):
                # ACTIVE GLOWING SCANNER CURSOR / MIDPOINT HIGHLIGHT
                pulse = 0.55 + 0.45 * math.sin(self._clip_ease() * math.pi)
                glow_rect = QRectF(tx - 5, ty - 5, tile_w + 10, tile_h + 10)
                glow_color = QColor(COLORS["accent_gold"])
                glow_color.setAlpha(int(28 + 36 * pulse))
                painter.setBrush(QBrush(glow_color))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(glow_rect, 14, 14)

                painter.setBrush(QBrush(QColor(COLORS["selected_bg"])))
                painter.setPen(QPen(QColor(COLORS["accent_gold"]), 2.5))
                painter.drawRoundedRect(tile_rect, 10, 10)

                font_px = max(13, int(tile_w * 0.36))
                painter.setFont(get_mono_font(font_px, weight=700))
                painter.setPen(QPen(QColor(COLORS["text_primary"])))
                painter.drawText(tile_rect, Qt.AlignCenter, str(val))

                marker_label = "▼ SCANNING" if stype == "linear" else "▼ MID"
                painter.setFont(get_mono_font(12, weight=600))
                painter.setPen(QPen(QColor(COLORS["accent_gold"])))
                painter.drawText(QRectF(tx - 20, ty - 20, tile_w + 40, 16), Qt.AlignCenter, marker_label)

            elif is_linear_examined or is_binary_eliminated:
                # FADED AWAY (Eliminated / Checked)
                painter.setBrush(QBrush(QColor("#F0F2F7")))
                painter.setPen(QPen(QColor(COLORS["border"]), 1))
                painter.drawRoundedRect(tile_rect, 10, 10)

                font_px = max(12, int(tile_w * 0.32))
                painter.setFont(get_mono_font(font_px, weight=400))
                painter.setPen(QPen(QColor(COLORS["text_muted"])))
                painter.drawText(tile_rect, Qt.AlignCenter, str(val))

                if is_linear_examined:
                    painter.setFont(get_mono_font(11, weight=400))
                    painter.setPen(QPen(QColor(160, 60, 60, 110)))
                    painter.drawText(QRectF(tx, ty + 4, tile_w, 12), Qt.AlignCenter, "✗")

            else:
                # NORMAL UNEXAMINED TILE (or inside active binary search zone)
                in_active_zone = (stype == "binary" and not is_binary_eliminated)
                border_color = COLORS["accent_teal"] if in_active_zone else COLORS["border"]
                bg_color = COLORS["selected_bg"] if in_active_zone else COLORS["bg_panel"]

                painter.setBrush(QBrush(QColor(bg_color)))
                painter.setPen(QPen(QColor(border_color), 1.5 if in_active_zone else 1))
                painter.drawRoundedRect(tile_rect, 10, 10)

                font_px = max(13, int(tile_w * 0.36))
                painter.setFont(get_mono_font(font_px, weight=700))
                painter.setPen(QPen(QColor(COLORS["text_primary"])))
                painter.drawText(tile_rect, Qt.AlignCenter, str(val))

            # Index label below tile: [0], [1], ...
            painter.setFont(get_mono_font(12, weight=400))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(tx, ty + tile_h + 6, tile_w, 16), Qt.AlignCenter, f"[{i}]")

            # Binary Search LOW and HIGH Markers below index label
            if stype == "binary":
                if is_binary_low and is_binary_high:
                    painter.setFont(get_mono_font(12, weight=600))
                    painter.setPen(QPen(QColor(COLORS["accent_blue"])))
                    painter.drawText(QRectF(tx - 20, ty + tile_h + 24, tile_w + 40, 16), Qt.AlignCenter, "▲ L, H")
                elif is_binary_low:
                    painter.setFont(get_mono_font(12, weight=600))
                    painter.setPen(QPen(QColor(COLORS["accent_blue"])))
                    painter.drawText(QRectF(tx - 20, ty + tile_h + 24, tile_w + 40, 16), Qt.AlignCenter, "▲ LOW")
                elif is_binary_high:
                    painter.setFont(get_mono_font(12, weight=600))
                    painter.setPen(QPen(QColor(COLORS["accent_blue"])))
                    painter.drawText(QRectF(tx - 20, ty + tile_h + 24, tile_w + 40, 16), Qt.AlignCenter, "▲ HIGH")

        painter.restore()

    # ------------------------------------------------------------------
    # Sorting Playground Renderer Mode (Balls, Cubes, Marbles, Bars)
    # ------------------------------------------------------------------
    def _draw_bars(self, painter: QPainter, bars: list):
        sort_event = getattr(self._render_data, "sort_event", None)
        self._sorting_renderer.render(painter, self.width(), self.height(), bars, sort_event)

    # ------------------------------------------------------------------
    # Rasterization Pixel Grid Mode
    # ------------------------------------------------------------------
    def _draw_pixel_grid(self, painter: QPainter, pg: dict):
        w, h = self.width(), self.height()
        grid_w = pg.get("grid_w", 20)
        grid_h = pg.get("grid_h", 20)
        pixels = pg.get("pixels", [])          # list of (x, y, color)
        candidates = pg.get("candidates", [])  # list of (x, y)
        current_px = pg.get("current", None)   # (x, y)
        ideal_line = pg.get("ideal_line", None) # (x0, y0, x1, y1)
        ideal_circle = pg.get("ideal_circle", None) # (cx, cy, r)

        painter.save()
        margin = 40
        cell_size = min((w - 2 * margin) / grid_w, (h - 2 * margin) / grid_h) * self._zoom
        start_x = (w - grid_w * cell_size) / 2.0 + self._pan[0]
        start_y = (h + grid_h * cell_size) / 2.0 + self._pan[1]

        def grid_to_screen(gx, gy):
            return start_x + gx * cell_size, start_y - (gy + 1) * cell_size

        def grid_center_to_screen(gx, gy):
            return start_x + (gx + 0.5) * cell_size, start_y - (gy + 0.5) * cell_size

        # 1. Draw Grid Background & lines
        grid_pen = QPen(QColor(COLORS["border"]))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        for gx in range(grid_w):
            for gy in range(grid_h):
                sx, sy = grid_to_screen(gx, gy)
                painter.setBrush(QBrush(QColor(COLORS["bg_input"])))
                painter.drawRect(QRectF(sx, sy, cell_size, cell_size))

        # 2. Draw Selected / Filled Pixels (newest pixel grows in)
        t = self._clip_ease()
        for idx, p in enumerate(pixels):
            gx, gy = p[0], p[1]
            color = self._parse_color(p[2] if len(p) > 2 else COLORS["accent_teal"])
            if 0 <= gx < grid_w and 0 <= gy < grid_h:
                sx, sy = grid_to_screen(gx, gy)
                grow = 1.0 if idx < len(pixels) - 1 else (0.25 + 0.75 * t)
                inset = (cell_size - 2) * (1.0 - grow) / 2.0
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor(COLORS["border_focus"]), 1))
                painter.drawRoundedRect(
                    QRectF(sx + 1 + inset, sy + 1 + inset, cell_size - 2 - 2 * inset, cell_size - 2 - 2 * inset),
                    3, 3,
                )

        # 3. Draw Candidate Pixels (dashed highlight)
        cand_pen = QPen(QColor(COLORS["accent_gold"]), 2, Qt.DashLine)
        for c in candidates:
            gx, gy = c[0], c[1]
            if 0 <= gx < grid_w and 0 <= gy < grid_h:
                sx, sy = grid_to_screen(gx, gy)
                painter.setBrush(QBrush(QColor(216, 169, 78, 50)))
                painter.setPen(cand_pen)
                painter.drawRect(QRectF(sx + 2, sy + 2, cell_size - 4, cell_size - 4))

        # 4. Current Step Pixel (pulse/focus border)
        if current_px:
            cgx, cgy = current_px[0], current_px[1]
            if 0 <= cgx < grid_w and 0 <= cgy < grid_h:
                sx, sy = grid_to_screen(cgx, cgy)
                pulse = 0.55 + 0.45 * math.sin(t * math.pi)
                painter.setBrush(QBrush(QColor(91, 141, 239, int(50 + 50 * pulse))))
                painter.setPen(QPen(QColor(COLORS["accent_gold"]), 2.5))
                painter.drawRect(QRectF(sx + 1, sy + 1, cell_size - 2, cell_size - 2))

        # 5. Continuous Geometry Overlay (drawn when rasterization completes)
        if ideal_line:
            x0, y0, x1, y1 = ideal_line
            sx0, sy0 = grid_center_to_screen(x0, y0)
            sx1, sy1 = grid_center_to_screen(x1, y1)
            line_pen = QPen(QColor(228, 104, 93, 220), 2.8, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(line_pen)
            painter.drawLine(QPointF(sx0, sy0), QPointF(sx1, sy1))

        if ideal_circle:
            cx, cy, r = ideal_circle
            scx, scy = grid_center_to_screen(cx, cy)
            sr = r * cell_size
            circle_pen = QPen(QColor(228, 104, 93, 220), 2.5, Qt.SolidLine)
            painter.setPen(circle_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(scx, scy), sr, sr)

        # 6. Start, End, and Center Badges
        start_pt = pg.get("start_point")
        end_pt = pg.get("end_point")
        center_pt = pg.get("center")

        def draw_badge(pt, bg_color, text):
            if pt and 0 <= pt[0] < grid_w and 0 <= pt[1] < grid_h:
                sx, sy = grid_to_screen(pt[0], pt[1])
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                br = min(10.0, cell_size * 0.35)
                cx = sx + cell_size / 2.0
                cy = sy + cell_size / 2.0
                painter.drawEllipse(QPointF(cx, cy), br, br)
                painter.setFont(get_mono_font(int(max(8, br * 0.95)), weight=700))
                painter.setPen(QPen(QColor("#FFFFFF")))
                painter.drawText(QRectF(cx - br, cy - br, br * 2, br * 2), Qt.AlignCenter, text)

        draw_badge(start_pt, "#38E54D", "S")
        draw_badge(end_pt, "#E4685D", "E")
        draw_badge(center_pt, "#A277FF", "C")

        # 7. Coordinate axes labels along edges
        painter.setFont(get_mono_font(12, weight=400))
        painter.setPen(QPen(QColor(COLORS["text_muted"])))
        for gx in range(0, grid_w, max(1, grid_w // 10)):
            sx, _ = grid_to_screen(gx, 0)
            painter.drawText(QRectF(sx, start_y + 4, cell_size, 16), Qt.AlignCenter, str(gx))
        for gy in range(0, grid_h, max(1, grid_h // 10)):
            _, sy = grid_to_screen(0, gy)
            painter.drawText(QRectF(start_x - 26, sy, 22, cell_size), Qt.AlignRight | Qt.AlignVCenter, str(gy))

        # 8. Color Legend Box (Top-Right)
        leg_w, leg_h = 188, 140
        leg_x, leg_y = w - leg_w - 14, 12
        painter.setPen(QPen(QColor("#DDD6FE"), 1.2))
        painter.setBrush(QBrush(QColor(255, 255, 255, 236)))
        painter.drawRoundedRect(QRectF(leg_x, leg_y, leg_w, leg_h), 10, 10)

        painter.setFont(get_ui_font(11, weight=700))
        painter.setPen(QPen(QColor("#5B21B6")))
        painter.drawText(leg_x + 14, leg_y + 20, "PIXEL LEGEND")

        legend_items = [
            ("#4EC7B0", "Plotted Pixel", "rect"),
            (COLORS["accent_gold"], "Current Step", "rect"),
            ("rgba(216, 169, 78, 120)", "Candidate Next", "dash"),
            ("#38E54D", "Start Point (S)", "circle"),
            ("#E4685D", "End Point (E)", "circle"),
        ]
        painter.setFont(get_ui_font(12, weight=400))
        for idx, (col, text, shape) in enumerate(legend_items):
            iy = leg_y + 42 + idx * 20
            painter.setPen(Qt.NoPen)
            if shape == "circle":
                painter.setBrush(QBrush(QColor(col)))
                painter.drawEllipse(QPointF(leg_x + 16, iy), 4.5, 4.5)
            elif shape == "dash":
                painter.setPen(QPen(QColor(col), 1.2, Qt.DashLine))
                painter.setBrush(QBrush(QColor(216, 169, 78, 50)))
                painter.drawRect(QRectF(leg_x + 11.5, iy - 4.5, 9, 9))
            else:
                painter.setBrush(QBrush(QColor(col)))
                painter.drawRect(QRectF(leg_x + 11.5, iy - 4.5, 9, 9))

            painter.setPen(QPen(QColor("#475569")))
            painter.drawText(leg_x + 28, iy + 4, text)

        painter.restore()

    # ------------------------------------------------------------------
    # Bézier & Curves Visualization Mode
    # ------------------------------------------------------------------
    def _draw_curves(self, painter: QPainter, cd: dict):
        w, h = float(self.width()), float(self.height())
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        cx, cy, scale = self._get_curve_transform()

        # 1. Background Grid & Cartesian Axes
        if self._show_grid:
            self._draw_curve_grid(painter, w, h, cx, cy, scale)

        # 2. Discrete Plotted Pixels (from Bresenham/DDA line rasterization of chords)
        pixels = cd.get("raster_pixels", [])
        curr_px = cd.get("current_pixel")
        if pixels:
            p_pen = QPen(QColor(99, 102, 241, 180), 1.0)
            p_brush = QBrush(QColor(129, 140, 248, 85))
            for px, py in pixels:
                # In discrete world coordinates, pixel (px, py) occupies [px-0.5, px+0.5] x [py-0.5, py+0.5]
                sx0, sy0 = self._curve_world_to_screen(px - 0.5, py + 0.5)
                sx1, sy1 = self._curve_world_to_screen(px + 0.5, py - 0.5)
                rw = max(2.0, sx1 - sx0)
                rh = max(2.0, sy1 - sy0)
                painter.setPen(p_pen)
                painter.setBrush(p_brush)
                painter.drawRoundedRect(QRectF(sx0, sy0, rw, rh), 2.5, 2.5)

        # Highlight current pixel being plotted
        if curr_px:
            c_px, c_py = curr_px[0], curr_px[1]
            sx0, sy0 = self._curve_world_to_screen(c_px - 0.5, c_py + 0.5)
            sx1, sy1 = self._curve_world_to_screen(c_px + 0.5, c_py - 0.5)
            rw = max(3.0, sx1 - sx0)
            rh = max(3.0, sy1 - sy0)
            painter.setPen(QPen(QColor(217, 119, 6), 2.0))
            painter.setBrush(QBrush(QColor(245, 158, 11, 160)))
            painter.drawRoundedRect(QRectF(sx0, sy0, rw, rh), 3.0, 3.0)

        # 3. Subdivided Control Polygons & Chords (Steps 5+)
        sub_polys = cd.get("subdivision_polygons", [])
        sub_chords = cd.get("subdivision_chords", [])
        active_seg = cd.get("active_segment")

        # Palette for multiple subdivision pieces
        poly_colors = [
            QColor(6, 182, 212),   # Cyan
            QColor(139, 92, 246),  # Purple
            QColor(236, 72, 153),  # Pink
            QColor(16, 185, 129),  # Emerald
            QColor(245, 158, 11),  # Amber
            QColor(59, 130, 246),  # Blue
            QColor(168, 85, 247),  # Violet
            QColor(20, 184, 166),  # Teal
        ]

        # Draw subdivided polygons
        if sub_polys and len(sub_polys) > 1:
            for s_idx, sp in enumerate(sub_polys):
                col = poly_colors[s_idx % len(poly_colors)]
                pen = QPen(col, 1.6, Qt.DashLine)
                painter.setPen(pen)
                for k in range(len(sp) - 1):
                    p_a, p_b = sp[k], sp[k + 1]
                    sxa, sya = self._curve_world_to_screen(p_a[0], p_a[1])
                    sxb, syb = self._curve_world_to_screen(p_b[0], p_b[1])
                    painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))

        # Draw approximating chords
        if sub_chords:
            chord_pen = QPen(QColor(79, 70, 229, 210), 2.0, Qt.SolidLine)
            painter.setPen(chord_pen)
            for ch in sub_chords:
                if len(ch) >= 2:
                    p_a, p_b = ch[0], ch[-1]
                    sxa, sya = self._curve_world_to_screen(p_a[0], p_a[1])
                    sxb, syb = self._curve_world_to_screen(p_b[0], p_b[1])
                    painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))
                    # Tiny endpoint dots
                    painter.setBrush(QBrush(QColor(79, 70, 229)))
                    painter.drawEllipse(QPointF(sxa, sya), 2.5, 2.5)
                    painter.drawEllipse(QPointF(sxb, syb), 2.5, 2.5)

        # Draw active segment highlight (chord currently being rasterized)
        if active_seg and len(active_seg) >= 2:
            p_a, p_b = active_seg[0], active_seg[1]
            sxa, sya = self._curve_world_to_screen(p_a[0], p_a[1])
            sxb, syb = self._curve_world_to_screen(p_b[0], p_b[1])
            # Glow line
            painter.setPen(QPen(QColor(244, 63, 94, 90), 6.0, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))
            # Core line
            painter.setPen(QPen(QColor(225, 29, 72), 3.0, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))

        # 4. Original Control Polygon (P0 -> P1 -> P2 -> P3)
        ctrl_pts = cd.get("control_points", [])
        labels = cd.get("labels", [f"P{i}" for i in range(len(ctrl_pts))])
        show_poly = cd.get("show_polygon", True)

        if show_poly and len(ctrl_pts) >= 2:
            poly_pen = QPen(QColor(148, 163, 184, 180), 1.8, Qt.DashLine)
            painter.setPen(poly_pen)
            for i in range(len(ctrl_pts) - 1):
                p_a, p_b = ctrl_pts[i], ctrl_pts[i + 1]
                sxa, sya = self._curve_world_to_screen(p_a[0], p_a[1])
                sxb, syb = self._curve_world_to_screen(p_b[0], p_b[1])
                painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))

        # 5. De Casteljau Pyramid & Midpoints Construction
        pyramid = cd.get("pyramid", [])
        reveal_level = cd.get("reveal_level", 0)

        if pyramid and reveal_level >= 1:
            # Level 1 (Q0, Q1, Q2)
            if len(pyramid) > 1 and reveal_level >= 1:
                q_pts = pyramid[1]
                painter.setPen(QPen(QColor(16, 185, 129), 2.0, Qt.DashLine))
                for i in range(len(q_pts) - 1):
                    sxa, sya = self._curve_world_to_screen(q_pts[i][0], q_pts[i][1])
                    sxb, syb = self._curve_world_to_screen(q_pts[i + 1][0], q_pts[i + 1][1])
                    painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))
                for i, q in enumerate(q_pts):
                    sx, sy = self._curve_world_to_screen(q[0], q[1])
                    painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
                    painter.setBrush(QBrush(QColor(16, 185, 129)))
                    painter.drawEllipse(QPointF(sx, sy), 5.0, 5.0)
                    self._draw_curve_pill(painter, sx, sy - 14, f"Q{i}", QColor("#065F46"), QColor("#D1FAE5"))

            # Level 2 (R0, R1)
            if len(pyramid) > 2 and reveal_level >= 2:
                r_pts = pyramid[2]
                painter.setPen(QPen(QColor(245, 158, 11), 2.2, Qt.DashLine))
                for i in range(len(r_pts) - 1):
                    sxa, sya = self._curve_world_to_screen(r_pts[i][0], r_pts[i][1])
                    sxb, syb = self._curve_world_to_screen(r_pts[i + 1][0], r_pts[i + 1][1])
                    painter.drawLine(QPointF(sxa, sya), QPointF(sxb, syb))
                for i, r in enumerate(r_pts):
                    sx, sy = self._curve_world_to_screen(r[0], r[1])
                    painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
                    painter.setBrush(QBrush(QColor(245, 158, 11)))
                    painter.drawEllipse(QPointF(sx, sy), 5.5, 5.5)
                    self._draw_curve_pill(painter, sx, sy - 14, f"R{i}", QColor("#92400E"), QColor("#FEF3C7"))

            # Level 3 (S0 Split Point on Curve)
            if len(pyramid) > 3 and reveal_level >= 3:
                s0 = pyramid[3][0]
                sx, sy = self._curve_world_to_screen(s0[0], s0[1])
                # Outer glow ring
                painter.setPen(QPen(QColor(124, 58, 237, 120), 2.5))
                painter.setBrush(QBrush(QColor(124, 58, 237, 40)))
                painter.drawEllipse(QPointF(sx, sy), 12.0, 12.0)
                # Split point core
                painter.setPen(QPen(QColor("#FFFFFF"), 2.5))
                painter.setBrush(QBrush(QColor(124, 58, 237)))
                painter.drawEllipse(QPointF(sx, sy), 6.5, 6.5)
                self._draw_curve_pill(painter, sx, sy + 18, "S0 (t=0.5)", QColor("#5B21B6"), QColor("#EDE9FE"))

        # 6. Continuous Smooth Bézier Curve
        show_curve = cd.get("show_curve", True)
        curve_samples = cd.get("curve_samples", [])
        if show_curve and len(curve_samples) >= 2:
            path = QPainterPath()
            s0x, s0y = self._curve_world_to_screen(curve_samples[0][0], curve_samples[0][1])
            path.moveTo(s0x, s0y)
            for pt in curve_samples[1:]:
                sx, sy = self._curve_world_to_screen(pt[0], pt[1])
                path.lineTo(sx, sy)
            # Rich smooth curve stroke
            curve_pen = QPen(QColor(124, 58, 237), 3.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(curve_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

        # 7. Control Points & Handles (Interactive draggable vertices)
        for i, pt in enumerate(ctrl_pts):
            lbl = labels[i] if i < len(labels) else f"P{i}"
            sx, sy = self._curve_world_to_screen(pt[0], pt[1])
            is_hover = (lbl == self._hovered_curve_target)
            is_drag = (lbl == self._drag_curve_target)

            # Outer glow halo if hovered or dragged
            if is_hover or is_drag:
                halo_color = QColor(99, 102, 241, 70 if is_drag else 40)
                painter.setPen(QPen(QColor(99, 102, 241, 200), 1.5))
                painter.setBrush(QBrush(halo_color))
                painter.drawEllipse(QPointF(sx, sy), 16.0, 16.0)

            # Handle body
            painter.setPen(QPen(QColor(79, 70, 229), 2.5))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawEllipse(QPointF(sx, sy), 7.5, 7.5)

            # Center pip
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(79, 70, 229)))
            painter.drawEllipse(QPointF(sx, sy), 3.0, 3.0)

            # Coordinate badge pill
            pill_text = f"{lbl} ({pt[0]:.1f}, {pt[1]:.1f})"
            self._draw_curve_pill(painter, sx, sy - 17, pill_text, QColor("#1E293B"), QColor("#F8FAFC"), border_color=QColor("#CBD5E1"))

        # 8. Top-Left Context Badge & Bottom Hint
        painter.setFont(get_ui_font(11, weight=600))
        algo_name = cd.get("raster_algorithm", "Bresenham")
        badge_text = f"BÉZIER SUBDIVISION  •  De Casteljau  •  Rasterizer: {algo_name}"
        self._draw_curve_pill(painter, 16, 14, badge_text, QColor("#4338CA"), QColor("#EEF2FF"), border_color=QColor("#C7D2FE"), anchor="left")

        if cd.get("draggable", True):
            painter.setFont(get_ui_font(11, weight=500))
            painter.setPen(QPen(QColor("#64748B")))
            painter.drawText(QRectF(20, h - 34, 480, 20), Qt.AlignLeft | Qt.AlignVCenter, "Tip: Drag control points P0–P3 on canvas to reshape the curve in real time.")

        painter.restore()

    def _draw_curve_pill(self, painter: QPainter, x: float, y: float, text: str,
                         text_color: QColor, bg_color: QColor, border_color: Optional[QColor] = None, anchor: str = "center"):
        painter.save()
        font = get_mono_font(10, weight=600)
        painter.setFont(font)
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text)
        th = fm.height()
        pad_x, pad_y = 8, 3
        rw = tw + pad_x * 2
        rh = th + pad_y * 2
        if anchor == "left":
            rx = x
            ry = y
        else:
            rx = x - rw / 2.0
            ry = y - rh / 2.0
        rect = QRectF(rx, ry, rw, rh)

        painter.setPen(QPen(border_color or text_color, 1.0))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, 4.0, 4.0)

        painter.setPen(QPen(text_color))
        painter.drawText(rect, Qt.AlignCenter, text)
        painter.restore()

    def _draw_curve_grid(self, painter: QPainter, w: float, h: float, cx: float, cy: float, scale: float):
        if scale <= 1e-6:
            return
        grid_step = 1.0 if scale >= 22.0 else 2.0
        painter.save()

        # Dot-line coordinate grid
        painter.setPen(QPen(QColor(COLORS["grid_line"]), 0.8, Qt.DotLine))
        x0 = int((-cx) / (scale * grid_step)) * grid_step - grid_step
        x1 = int((w - cx) / (scale * grid_step)) * grid_step + grid_step
        y0 = int((cy - h) / (scale * grid_step)) * grid_step - grid_step
        y1 = int(cy / (scale * grid_step)) * grid_step + grid_step

        x = x0
        while x <= x1:
            gx, _ = self._curve_world_to_screen(x, 0)
            painter.drawLine(QPointF(gx, 0), QPointF(gx, h))
            x += grid_step

        y = y0
        while y <= y1:
            _, gy = self._curve_world_to_screen(0, y)
            painter.drawLine(QPointF(0, gy), QPointF(w, gy))
            y += grid_step

        # Main Axes
        painter.setPen(QPen(QColor(COLORS["axis_line"]), 1.2))
        ax, ay = self._curve_world_to_screen(0, 0)
        painter.drawLine(QPointF(0, ay), QPointF(w, ay))
        painter.drawLine(QPointF(ax, 0), QPointF(ax, h))

        # Axis ticks and numbers
        painter.setFont(get_mono_font(9.5, weight=400))
        painter.setPen(QPen(QColor(COLORS["text_muted"])))
        tick_step = 2.0 if scale < 35.0 else 1.0
        tx = x0
        while tx <= x1:
            if abs(tx) > 0.01:
                gx, _ = self._curve_world_to_screen(tx, 0)
                painter.drawLine(QPointF(gx, ay - 3), QPointF(gx, ay + 3))
                val_str = f"{int(tx) if float(tx).is_integer() else tx}"
                painter.drawText(QRectF(gx - 18, ay + 5, 36, 14), Qt.AlignCenter, val_str)
            tx += tick_step

        ty = y0
        while ty <= y1:
            if abs(ty) > 0.01:
                _, gy = self._curve_world_to_screen(0, ty)
                painter.drawLine(QPointF(ax - 3, gy), QPointF(ax + 3, gy))
                val_str = f"{int(ty) if float(ty).is_integer() else ty}"
                painter.drawText(QRectF(ax - 28, gy - 7, 24, 14), Qt.AlignRight | Qt.AlignVCenter, val_str)
            ty += tick_step

        painter.restore()

    # ------------------------------------------------------------------
    # Cohen-Sutherland Clipping Mode
    # ------------------------------------------------------------------
    _CLIP_BIT_COLORS = {
        "TOP": QColor("#E11D48"),
        "BOTTOM": QColor("#D97706"),
        "RIGHT": QColor("#2563EB"),
        "LEFT": QColor("#7C3AED"),
    }
    _CLIP_REGION_FILL = {
        0: QColor(13, 148, 136, 42),
        8: QColor(225, 29, 72, 28),
        4: QColor(217, 119, 6, 28),
        2: QColor(37, 99, 235, 26),
        1: QColor(124, 58, 237, 26),
        9: QColor(190, 24, 93, 30),
        10: QColor(219, 39, 119, 28),
        5: QColor(180, 83, 9, 28),
        6: QColor(194, 65, 12, 26),
    }
    _CLIP_REGION_NAMES = {
        0: "Inside", 1: "Left", 2: "Right", 4: "Bottom", 8: "Top",
        5: "Bottom-Left", 6: "Bottom-Right", 9: "Top-Left", 10: "Top-Right",
    }
    _CLIP_REGION_CODES = {
        0: "0000", 1: "0001", 2: "0010", 4: "0100", 8: "1000",
        5: "0101", 6: "0110", 9: "1001", 10: "1010",
    }

    def _draw_clipping(self, painter: QPainter, cd: dict):
        self._label_placer = self._make_label_placer()
        view_tab = cd.get("view_tab", "clip_line")
        if view_tab == "region_codes":
            self._draw_clip_region_lesson(painter, cd)
            return
        if view_tab in ("four_cases", "clip_polygon") or cd.get("polygon"):
            self._draw_clip_polygon_lesson(painter, cd)
            return
        self._draw_clip_line_lesson(painter, cd)

    def _clip_to_s(self, x: float, y: float) -> Tuple[float, float]:
        return self._clipping_world_to_screen(x, y)

    def _clip_window_screen(self, cd: dict):
        xmin = float(cd.get("xmin", -4.0))
        ymin = float(cd.get("ymin", -3.0))
        xmax = float(cd.get("xmax", 4.0))
        ymax = float(cd.get("ymax", 3.0))
        sx_l, sy_t = self._clip_to_s(xmin, ymax)
        sx_r, sy_b = self._clip_to_s(xmax, ymin)
        return xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b

    def _draw_clip_grid(self, painter: QPainter, w: float, h: float):
        if not self._show_grid:
            return
        cx, cy, scale = self._get_clipping_transform()
        if scale <= 1e-6:
            return
        grid_step = 1.0 if scale >= 22.0 else 2.0
        painter.setPen(QPen(QColor(COLORS["grid_line"]), 0.8, Qt.DotLine))
        x0 = int((-cx) / (scale * grid_step)) * grid_step - grid_step
        x1 = int((w - cx) / (scale * grid_step)) * grid_step + grid_step
        y0 = int((cy - h) / (scale * grid_step)) * grid_step - grid_step
        y1 = int(cy / (scale * grid_step)) * grid_step + grid_step
        x = x0
        while x <= x1:
            gx, _ = self._clip_to_s(x, 0)
            painter.drawLine(QPointF(gx, 0), QPointF(gx, h))
            x += grid_step
        y = y0
        while y <= y1:
            _, gy = self._clip_to_s(0, y)
            painter.drawLine(QPointF(0, gy), QPointF(w, gy))
            y += grid_step
        painter.setPen(QPen(QColor(COLORS["axis_line"]), 1.15))
        ax, ay = self._clip_to_s(0, 0)
        painter.drawLine(QPointF(0, ay), QPointF(w, ay))
        painter.drawLine(QPointF(ax, 0), QPointF(ax, h))

    def _clip_region_rects(self, sx_l: float, sy_t: float, sx_r: float, sy_b: float,
                           w: float, h: float) -> Dict[int, QRectF]:
        return {
            9: QRectF(0, 0, max(0.0, sx_l), max(0.0, sy_t)),
            8: QRectF(sx_l, 0, max(0.0, sx_r - sx_l), max(0.0, sy_t)),
            10: QRectF(sx_r, 0, max(0.0, w - sx_r), max(0.0, sy_t)),
            1: QRectF(0, sy_t, max(0.0, sx_l), max(0.0, sy_b - sy_t)),
            0: QRectF(sx_l, sy_t, max(0.0, sx_r - sx_l), max(0.0, sy_b - sy_t)),
            2: QRectF(sx_r, sy_t, max(0.0, w - sx_r), max(0.0, sy_b - sy_t)),
            5: QRectF(0, sy_b, max(0.0, sx_l), max(0.0, h - sy_b)),
            4: QRectF(sx_l, sy_b, max(0.0, sx_r - sx_l), max(0.0, h - sy_b)),
            6: QRectF(sx_r, sy_b, max(0.0, w - sx_r), max(0.0, h - sy_b)),
        }

    def _draw_clip_spatial_regions(self, painter: QPainter, cd: dict, w: float, h: float,
                                   selected: Optional[int] = None, faint: bool = False,
                                   labels: bool = False, pulse_selected: bool = False):
        xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
        rects = self._clip_region_rects(sx_l, sy_t, sx_r, sy_b, w, h)
        pulse = 0.55 + 0.45 * math.sin(self._clip_ease() * math.pi)
        painter.setPen(Qt.NoPen)
        for code, rect in rects.items():
            if code == 0:
                continue
            fill = QColor(self._CLIP_REGION_FILL.get(code, QColor(226, 232, 240, 30)))
            if faint:
                fill.setAlpha(14)
            elif selected is not None and selected >= 0:
                if code == selected:
                    fill.setAlpha(int(70 + 40 * pulse) if pulse_selected else 92)
                else:
                    fill.setAlpha(16)
            painter.setBrush(QBrush(fill))
            painter.drawRect(rect)

        if labels:
            self._draw_clip_region_labels(painter, rects, selected)

    def _draw_clip_region_labels(self, painter: QPainter, rects: Dict[int, QRectF],
                                 selected: Optional[int] = None):
        for code, rect in rects.items():
            if rect.width() < 48 or rect.height() < 28:
                continue
            is_sel = selected is not None and code == selected
            painter.setFont(get_ui_font(11, weight=700 if is_sel or code == 0 else 500))
            painter.setPen(QPen(QColor("#0F766E" if code == 0 else ("#4C1D95" if is_sel else "#475569"))))
            name = self._CLIP_REGION_NAMES[code]
            label = name if rect.height() < 56 else f"{name}\n{self._CLIP_REGION_CODES[code]}"
            painter.drawText(rect.adjusted(6, 6, -6, -6), Qt.AlignCenter, label)

    def _draw_clip_window(self, painter: QPainter, cd: dict, emphasized: bool = False):
        xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
        win = QRectF(sx_l, sy_t, max(1.0, sx_r - sx_l), max(1.0, sy_b - sy_t))
        glow = QColor(13, 148, 136, 34 if emphasized else 22)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawRoundedRect(win.adjusted(-3, -3, 3, 3), 6, 6)
        painter.setBrush(QBrush(QColor(13, 148, 136, 38 if emphasized else 26)))
        painter.setPen(QPen(QColor("#0F766E"), 2.4 if emphasized else 2.0))
        painter.drawRect(win)
        painter.setBrush(QBrush(QColor("#0F766E")))
        painter.setPen(QPen(QColor("#FFFFFF"), 1.1))
        for px, py in ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)):
            sx, sy = self._clip_to_s(px, py)
            painter.drawEllipse(QPointF(sx, sy), 3.2, 3.2)

    def _draw_clip_boundaries(self, painter: QPainter, cd: dict, w: float, h: float,
                              active: Optional[str] = None, show_labels: bool = False):
        xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
        edges = [
            ("LEFT", QPointF(sx_l, 0), QPointF(sx_l, h), f"Left  x = {xmin:.1f}", QPointF(sx_l, (sy_t + sy_b) / 2.0)),
            ("RIGHT", QPointF(sx_r, 0), QPointF(sx_r, h), f"Right  x = {xmax:.1f}", QPointF(sx_r, (sy_t + sy_b) / 2.0)),
            ("TOP", QPointF(0, sy_t), QPointF(w, sy_t), f"Top  y = {ymax:.1f}", QPointF(w / 2.0, sy_t)),
            ("BOTTOM", QPointF(0, sy_b), QPointF(w, sy_b), f"Bottom  y = {ymin:.1f}", QPointF(w / 2.0, sy_b)),
        ]
        for name, p1, p2, label, tag in edges:
            is_on = active == name
            if is_on:
                glow = QColor(self._CLIP_BIT_COLORS[name])
                glow.setAlpha(70)
                painter.setPen(QPen(glow, 10, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(p1, p2)
                painter.setPen(QPen(self._CLIP_BIT_COLORS[name], 2.6, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(p1, p2)
            elif show_labels or active:
                painter.setPen(QPen(QColor("#C7CDD9"), 1.15, Qt.DashLine))
                painter.drawLine(p1, p2)
            if show_labels or is_on:
                painter.setFont(get_ui_font(11, weight=600))
                painter.setPen(QPen(self._CLIP_BIT_COLORS[name] if is_on else QColor("#64748B")))
                if name in ("TOP", "BOTTOM"):
                    painter.drawText(QRectF(tag.x() - 70, tag.y() - (22 if name == "TOP" else -6), 140, 18),
                                     Qt.AlignCenter, label)
                else:
                    painter.drawText(QRectF(tag.x() + (8 if name == "RIGHT" else -148), tag.y() - 10, 140, 20),
                                     Qt.AlignLeft if name == "RIGHT" else Qt.AlignRight, label)

    def _draw_clip_bit_plane(self, painter: QPainter, cd: dict, bit: str, w: float, h: float):
        xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
        color = QColor(self._CLIP_BIT_COLORS.get(bit, QColor("#6C5CE7")))
        color.setAlpha(int(36 + 50 * self._clip_ease()))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        if bit == "TOP":
            painter.drawRect(QRectF(0, 0, w, max(0.0, sy_t)))
        elif bit == "BOTTOM":
            painter.drawRect(QRectF(0, sy_b, w, max(0.0, h - sy_b)))
        elif bit == "LEFT":
            painter.drawRect(QRectF(0, 0, max(0.0, sx_l), h))
        elif bit == "RIGHT":
            painter.drawRect(QRectF(sx_r, 0, max(0.0, w - sx_r), h))
        self._draw_clip_boundaries(painter, cd, w, h, active=bit, show_labels=True)

    def _draw_clip_insight(self, painter: QPainter, text: str, w: float, h: float, tone: str = "neutral"):
        if not text:
            return
        tones = {
            "neutral": (QColor(255, 255, 255, 236), QColor("#D8D1FF"), QColor("#312E81")),
            "accept": (QColor(236, 253, 245, 240), QColor("#6EE7B7"), QColor("#047857")),
            "reject": (QColor(254, 242, 242, 240), QColor("#FECACA"), QColor("#B91C1C")),
            "clip": (QColor(245, 243, 255, 240), QColor("#C4B5FD"), QColor("#5B21B6")),
        }
        bg, border, fg = tones.get(tone, tones["neutral"])
        painter.setFont(get_ui_font(13, weight=500))
        fm = painter.fontMetrics()
        max_w = min(w - 36.0, 640.0)
        wrapped = []
        words = text.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if fm.horizontalAdvance(trial) > max_w - 28:
                if line:
                    wrapped.append(line)
                line = word
            else:
                line = trial
        if line:
            wrapped.append(line)
        shown = wrapped[:3]
        body = "\n".join(shown)
        tw = min(max_w, max(fm.horizontalAdvance(s) for s in shown) + 28)
        th = 16 + 18 * len(shown)
        rect = QRectF((w - tw) / 2.0, h - th - 14.0, tw, th)
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(border, 1.2))
        painter.drawRoundedRect(rect, 12, 12)
        painter.setPen(QPen(fg))
        painter.drawText(rect.adjusted(12, 4, -12, -4), Qt.AlignCenter, body)

    def _draw_clip_code_pills(self, painter: QPainter, sx: float, sy: float, w: float,
                              code_str: str, reveal: float = 1.0, active_bit: Optional[str] = None):
        bits = ["T", "B", "R", "L"]
        names = ["TOP", "BOTTOM", "RIGHT", "LEFT"]
        pill_w, gap = 22.0, 4.0
        total = 4 * pill_w + 3 * gap
        x0 = sx - total / 2.0
        y0 = sy + 14.0
        if y0 + 22 > self.height() - 64:
            y0 = sy - 36.0
        for i, (letter, bit_name, ch) in enumerate(zip(bits, names, code_str[:4].ljust(4, "0"))):
            vis = 1.0 if reveal >= 1.0 else self._clip_stagger(i)
            if vis <= 0.02:
                continue
            bx = x0 + i * (pill_w + gap)
            on = ch == "1"
            is_act = active_bit == bit_name
            col = QColor(self._CLIP_BIT_COLORS[bit_name]) if (on or is_act) else QColor("#E2E8F0")
            col.setAlpha(int(255 * min(1.0, vis)))
            painter.setBrush(QBrush(col))
            painter.setPen(QPen(QColor("#FFFFFF") if on or is_act else QColor("#94A3B8"), 0.8))
            painter.drawRoundedRect(QRectF(bx, y0, pill_w, 20), 5, 5)
            painter.setFont(get_mono_font(10, weight=700))
            painter.setPen(QPen(QColor("#FFFFFF") if on or is_act else QColor("#64748B")))
            painter.drawText(QRectF(bx, y0, pill_w, 20), Qt.AlignCenter, f"{letter}{ch}")

    def _draw_clip_decision_strip(self, painter: QPainter, cd: dict, w: float, op: str):
        c1 = cd.get("code1_str", "0000")
        c2 = cd.get("code2_str", "0000")
        result = cd.get("or_str" if op == "or" else "and_str", "0000")
        t = self._clip_ease()
        names = ["TOP", "BOTTOM", "RIGHT", "LEFT"]
        zero = result == "0000"
        if op == "or":
            title = "OR  —  is any outside bit on?"
            verdict = "all zero  →  the whole line is inside" if zero else "a 1 remains  →  not entirely inside"
            verdict_col = QColor("#047857") if zero else QColor("#5B21B6")
        else:
            title = "AND  —  do they share an outside side?"
            verdict = "a shared 1  →  entirely outside" if not zero else "no shared 1  →  clip the line"
            verdict_col = QColor("#B91C1C") if not zero else QColor("#5B21B6")

        card = QRectF(0, 14, min(w - 36.0, 560.0), 84)
        card.moveLeft((w - card.width()) / 2.0)
        painter.setBrush(QBrush(QColor(255, 255, 255, 236)))
        painter.setPen(QPen(QColor("#DDD6FE"), 1.2))
        painter.drawRoundedRect(card, 12, 12)
        painter.setFont(get_ui_font(12, weight=600))
        painter.setPen(QPen(QColor("#5B21B6")))
        painter.drawText(QRectF(card.left() + 16, card.top() + 8, card.width() - 32, 18), Qt.AlignLeft, title)

        def draw_bits(x: float, y: float, bits: str, delay: float, result_row: bool = False):
            for i, (ch, name) in enumerate(zip(bits[:4].ljust(4, "0"), names)):
                local = min(1.0, max(0.0, (t - delay - i * 0.08) / 0.2))
                if local <= 0:
                    continue
                bx = x + i * 28
                on = ch == "1"
                if result_row and not on and zero:
                    fill, edge, fg = QColor("#ECFDF5"), QColor("#A7F3D0"), QColor("#059669")
                elif on:
                    fill, edge, fg = QColor(self._CLIP_BIT_COLORS[name]), QColor("#FFFFFF"), QColor("#FFFFFF")
                else:
                    fill, edge, fg = QColor("#F8FAFC"), QColor("#E2E8F0"), QColor("#94A3B8")
                painter.setBrush(QBrush(fill))
                painter.setPen(QPen(edge, 0.8))
                painter.drawRoundedRect(QRectF(bx, y, 24, 20), 5, 5)
                painter.setFont(get_mono_font(11, weight=700))
                painter.setPen(QPen(fg))
                painter.drawText(QRectF(bx, y, 24, 20), Qt.AlignCenter, ch)

        painter.setFont(get_ui_font(11, weight=500))
        painter.setPen(QPen(QColor("#64748B")))
        painter.drawText(QRectF(card.left() + 16, card.top() + 30, 28, 20), Qt.AlignLeft | Qt.AlignVCenter, "P1")
        draw_bits(card.left() + 46, card.top() + 30, c1, 0.0)
        painter.drawText(QRectF(card.left() + 168, card.top() + 30, 28, 20), Qt.AlignLeft | Qt.AlignVCenter, "P2")
        draw_bits(card.left() + 198, card.top() + 30, c2, 0.05)

        painter.setFont(get_ui_font(11, weight=600))
        painter.setPen(QPen(QColor("#4C1D95")))
        painter.drawText(QRectF(card.left() + 16, card.top() + 56, 40, 20), Qt.AlignLeft | Qt.AlignVCenter,
                         "OR" if op == "or" else "AND")
        draw_bits(card.left() + 46, card.top() + 56, result, 0.38, result_row=True)
        painter.setFont(get_ui_font(12, weight=600))
        painter.setPen(QPen(verdict_col))
        painter.drawText(QRectF(card.left() + 168, card.top() + 56, card.width() - 184, 20),
                         Qt.AlignLeft | Qt.AlignVCenter, verdict)

    def _draw_clip_endpoint(self, painter: QPainter, pt_id: str, wx: float, wy: float,
                            sx: float, sy: float, code_str: str, show_code: bool,
                            selected: bool, color: QColor, w: float, active_bit: Optional[str] = None,
                            reveal_bits: bool = False):
        hover = self._hovered_endpoint == pt_id or self._drag_endpoint_target == pt_id
        rad = 9.0 if hover else (8.0 if selected else 6.5)
        if selected:
            halo = QColor(color)
            halo.setAlpha(55)
            painter.setBrush(QBrush(halo))
            painter.setPen(QPen(color, 1.2, Qt.DashLine))
            painter.drawEllipse(QPointF(sx, sy), 14.0, 14.0)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#FFFFFF"), 2.0 if hover else 1.6))
        painter.drawEllipse(QPointF(sx, sy), rad, rad)

        label = f"{pt_id}  ({wx:.1f}, {wy:.1f})"
        outward = (1.0, -1.0) if sx < w - 150 else (-1.0, -1.0)
        self._smart_label(
            painter, label, (sx, sy), color,
            get_ui_font(12, weight=700),
            kind="point", outward=outward, pill=True, priority=4
        )
        if show_code:
            self._draw_clip_code_pills(
                painter, sx, sy, w, code_str,
                reveal=1.0 if not reveal_bits else self._clip_ease(),
                active_bit=active_bit,
            )

    def _draw_clip_line_lesson(self, painter: QPainter, cd: dict):
        w, h = float(self.width()), float(self.height())
        focus = cd.get("focus", "meet")
        caption = cd.get("caption", "")
        status = cd.get("status", "evaluating")
        selected_pt = cd.get("selected_pt")
        active_boundary = cd.get("active_boundary")
        shared_region = cd.get("shared_region")
        anim = cd.get("anim") or {}
        code1_str = cd.get("code1_str", "0000")
        code2_str = cd.get("code2_str", "0000")

        painter.save()
        self._draw_clip_grid(painter, w, h)

        highlight_code = None
        if focus == "code_p1":
            highlight_code = int(cd.get("code1", 0))
        elif focus == "code_p2":
            highlight_code = int(cd.get("code2", 0))
        elif selected_pt == "P1":
            highlight_code = int(cd.get("code1", 0))
        elif selected_pt == "P2":
            highlight_code = int(cd.get("code2", 0))

        if focus in ("code_p1", "code_p2", "select"):
            self._draw_clip_spatial_regions(painter, cd, w, h, selected=highlight_code, pulse_selected=True)
        elif shared_region:
            self._draw_clip_spatial_regions(painter, cd, w, h, faint=True)
            xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
            painter.setPen(Qt.NoPen)
            wash = QColor(239, 68, 68, int(28 + 22 * self._clip_ease()))
            painter.setBrush(QBrush(wash))
            if shared_region == "LEFT":
                painter.drawRect(QRectF(0, 0, max(0.0, sx_l), h))
            elif shared_region == "RIGHT":
                painter.drawRect(QRectF(sx_r, 0, max(0.0, w - sx_r), h))
            elif shared_region == "TOP":
                painter.drawRect(QRectF(0, 0, w, max(0.0, sy_t)))
            elif shared_region == "BOTTOM":
                painter.drawRect(QRectF(0, sy_b, w, max(0.0, h - sy_b)))
        else:
            self._draw_clip_spatial_regions(painter, cd, w, h, faint=True)

        self._draw_clip_window(painter, cd, emphasized=focus in ("meet", "result") and status == "accepted")
        show_bounds = focus in ("meet", "select", "intersect") or bool(active_boundary)
        self._draw_clip_boundaries(painter, cd, w, h, active=active_boundary, show_labels=show_bounds)

        orig_p1 = cd.get("orig_p1")
        orig_p2 = cd.get("orig_p2")
        current_p1 = list(cd.get("current_p1") or orig_p1 or (0.0, 0.0))
        current_p2 = list(cd.get("current_p2") or orig_p2 or (0.0, 0.0))
        discarded_segs = cd.get("discarded_segs") or []
        intersections = cd.get("intersections") or []

        if orig_p1 and orig_p2:
            os1 = QPointF(*self._clip_to_s(orig_p1[0], orig_p1[1]))
            os2 = QPointF(*self._clip_to_s(orig_p2[0], orig_p2[1]))
            painter.setPen(QPen(QColor("#94A3B8"), 1.4, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(os1, os2)

        for dseg in discarded_segs:
            painter.setPen(QPen(QColor("#EF4444"), 2.0, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(QPointF(*self._clip_to_s(dseg[0], dseg[1])),
                             QPointF(*self._clip_to_s(dseg[2], dseg[3])))

        render_p1, render_p2 = list(current_p1), list(current_p2)
        if anim.get("type") == "endpoint_move":
            t = self._clip_ease()
            p_from, p_to = anim.get("from", (0, 0)), anim.get("to", (0, 0))
            ix = p_from[0] + (p_to[0] - p_from[0]) * t
            iy = p_from[1] + (p_to[1] - p_from[1]) * t
            if anim.get("target") == "P1":
                render_p1 = [ix, iy]
            else:
                render_p2 = [ix, iy]
            painter.setPen(QPen(QColor("#7C3AED"), 1.5, Qt.DotLine))
            painter.drawLine(QPointF(*self._clip_to_s(p_from[0], p_from[1])),
                             QPointF(*self._clip_to_s(ix, iy)))

        as1 = QPointF(*self._clip_to_s(render_p1[0], render_p1[1]))
        as2 = QPointF(*self._clip_to_s(render_p2[0], render_p2[1]))
        is_final = bool(cd.get("is_final"))
        if status == "accepted" and is_final:
            painter.setPen(QPen(QColor(16, 185, 129, 70), 10, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(as1, as2)
            painter.setPen(QPen(QColor("#059669"), 3.8, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(as1, as2)
        elif status == "rejected":
            painter.setPen(QPen(QColor("#EF4444"), 2.4, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(as1, as2)
        else:
            painter.setPen(QPen(QColor("#4F46E5"), 2.8, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(as1, as2)

        appear = self._clip_ease() if anim.get("type") == "intersection_marker" else 1.0
        for pt in intersections:
            isx, isy = self._clip_to_s(pt["x"], pt["y"])
            rad = 5.5 + 2.2 * appear
            col = QColor("#D97706" if pt.get("is_corner") else "#E11D48")
            painter.setBrush(QBrush(col))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.8))
            painter.drawEllipse(QPointF(isx, isy), rad, rad)
            if focus == "intersect" or is_final:
                painter.setFont(get_mono_font(11, weight=600))
                painter.setPen(QPen(col))
                painter.drawText(QRectF(isx + 10, isy - 12, 130, 20), Qt.AlignLeft,
                                 f"I({pt['x']:.2f}, {pt['y']:.2f})")

        reveal_p1 = focus == "code_p1"
        reveal_p2 = focus == "code_p2"
        self._draw_clip_endpoint(
            painter, "P1", render_p1[0], render_p1[1], as1.x(), as1.y(),
            code1_str, bool(cd.get("show_p1_code")), selected_pt == "P1",
            QColor("#4F46E5"), w, active_boundary, reveal_p1,
        )
        self._draw_clip_endpoint(
            painter, "P2", render_p2[0], render_p2[1], as2.x(), as2.y(),
            code2_str, bool(cd.get("show_p2_code")), selected_pt == "P2",
            QColor("#7C3AED"), w, active_boundary, reveal_p2,
        )

        if focus == "or_test":
            self._draw_clip_decision_strip(painter, cd, w, "or")
        elif focus == "and_test":
            self._draw_clip_decision_strip(painter, cd, w, "and")

        tone = "neutral"
        if status == "accepted" and is_final:
            tone = "accept"
        elif status == "rejected":
            tone = "reject"
        elif focus in ("select", "intersect", "update"):
            tone = "clip"
        self._draw_clip_insight(painter, caption, w, h, tone)
        painter.restore()

    def _draw_clip_region_lesson(self, painter: QPainter, cd: dict):
        w, h = float(self.width()), float(self.height())
        lesson = cd.get("lesson", "map")
        selected = cd.get("selected_code", -1)
        bit_focus = cd.get("bit_focus")
        caption = cd.get("caption", "")
        painter.save()
        self._draw_clip_grid(painter, w, h)

        if lesson == "window":
            self._draw_clip_spatial_regions(painter, cd, w, h, faint=True)
            self._draw_clip_window(painter, cd, emphasized=True)
            self._draw_clip_boundaries(painter, cd, w, h, show_labels=True)
        elif lesson == "bits" and bit_focus:
            self._draw_clip_spatial_regions(painter, cd, w, h, faint=True)
            self._draw_clip_bit_plane(painter, cd, bit_focus, w, h)
            self._draw_clip_window(painter, cd)
            self._draw_clip_bit_legend(painter, w, bit_focus)
        else:
            labels = bool(cd.get("show_all_labels") or lesson == "map" or lesson == "region")
            sel = selected if isinstance(selected, int) and selected >= 0 else None
            self._draw_clip_spatial_regions(
                painter, cd, w, h, selected=sel, labels=False, pulse_selected=(lesson == "region"),
            )
            self._draw_clip_window(painter, cd, emphasized=(sel == 0 or lesson == "map"))
            self._draw_clip_boundaries(painter, cd, w, h, show_labels=(lesson == "map"))
            if labels:
                xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
                rects = self._clip_region_rects(sx_l, sy_t, sx_r, sy_b, w, h)
                self._draw_clip_region_labels(painter, rects, sel)
            if lesson == "region" and sel is not None:
                self._draw_clip_bit_legend(painter, w, None, code=sel)

        self._draw_clip_insight(painter, caption, w, h, "clip" if lesson == "region" else "neutral")
        painter.restore()

    def _draw_clip_bit_legend(self, painter: QPainter, w: float, focus: Optional[str] = None, code: Optional[int] = None):
        items = [("T", "TOP", "Above"), ("B", "BOTTOM", "Below"), ("R", "RIGHT", "Right"), ("L", "LEFT", "Left")]
        box_w = 72.0
        total = 4 * box_w + 3 * 8
        x0 = (w - total) / 2.0
        y = 14.0
        for i, (letter, name, word) in enumerate(items):
            bx = x0 + i * (box_w + 8)
            on = (focus == name) or (code is not None and bool(code & {"TOP": 8, "BOTTOM": 4, "RIGHT": 2, "LEFT": 1}[name]))
            bg = QColor(self._CLIP_BIT_COLORS[name]) if on else QColor(255, 255, 255, 230)
            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(self._CLIP_BIT_COLORS[name] if on else QColor("#E2E8F0"), 1.2))
            painter.drawRoundedRect(QRectF(bx, y, box_w, 36), 8, 8)
            painter.setFont(get_mono_font(13, weight=700))
            painter.setPen(QPen(QColor("#FFFFFF") if on else self._CLIP_BIT_COLORS[name]))
            painter.drawText(QRectF(bx, y + 2, box_w, 18), Qt.AlignCenter, letter)
            painter.setFont(get_ui_font(10, weight=500))
            painter.setPen(QPen(QColor("#FFFFFF") if on else QColor("#64748B")))
            painter.drawText(QRectF(bx, y + 18, box_w, 16), Qt.AlignCenter, word)

    def _clip_pts_equal(self, a, b) -> bool:
        if not a or not b or len(a) != len(b):
            return False
        return all(abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6 for p, q in zip(a, b))

    def _clip_pt_key(self, pt) -> Tuple[float, float]:
        return (round(float(pt[0]), 4), round(float(pt[1]), 4))

    def _lerp_clip_polygon(self, src, dst, t: float):
        t = min(1.0, max(0.0, t))
        if t >= 0.999:
            return list(dst or [])
        if not dst:
            return list(src or []) if t < 0.55 else []
        if not src:
            return list(dst)
        n = max(len(src), len(dst))
        a = list(src) + [src[-1]] * (n - len(src))
        b = list(dst) + [dst[-1]] * (n - len(dst))
        return [
            (a[i][0] + (b[i][0] - a[i][0]) * t, a[i][1] + (b[i][1] - a[i][1]) * t)
            for i in range(n)
        ]

    def _draw_clip_poly_shape(self, painter: QPainter, pts, fill: QColor, stroke: QColor,
                              width: float = 2.0, dashed: bool = False, closed: bool = True):
        if not pts or len(pts) < 2:
            return
        qpoly = QPolygonF([QPointF(*self._clip_to_s(px, py)) for px, py in pts])
        style = Qt.DashLine if dashed else Qt.SolidLine
        painter.setBrush(QBrush(fill) if closed and len(pts) >= 3 else Qt.NoBrush)
        painter.setPen(QPen(stroke, width, style, Qt.RoundCap, Qt.RoundJoin))
        if closed and len(pts) >= 3:
            painter.drawPolygon(qpoly)
        else:
            painter.drawPolyline(qpoly)

    def _draw_clip_poly_vertex(self, painter: QPainter, pt, color: QColor, label: str = "",
                               radius: float = 6.0, halo: bool = False, discarded: bool = False):
        sx, sy = self._clip_to_s(pt[0], pt[1])
        if halo:
            halo_c = QColor(color)
            halo_c.setAlpha(70)
            painter.setBrush(QBrush(halo_c))
            painter.setPen(QPen(color, 1.2, Qt.DashLine))
            painter.drawEllipse(QPointF(sx, sy), radius + 6.0, radius + 6.0)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1.6))
        painter.drawEllipse(QPointF(sx, sy), radius, radius)
        if discarded:
            painter.setPen(QPen(QColor("#FFFFFF"), 2.0, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(sx - 3.5, sy - 3.5), QPointF(sx + 3.5, sy + 3.5))
            painter.drawLine(QPointF(sx - 3.5, sy + 3.5), QPointF(sx + 3.5, sy - 3.5))
        if label:
            painter.setFont(get_ui_font(12, weight=700))
            painter.setPen(QPen(color))
            painter.drawText(QRectF(sx + 8, sy - 16, 110, 18), Qt.AlignLeft, label)

    def _draw_clip_halfplane_captions(self, painter: QPainter, cd: dict, boundary: str):
        xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
        painter.setFont(get_ui_font(12, weight=700))
        if boundary == "LEFT":
            painter.setPen(QPen(QColor("#7C3AED")))
            painter.drawText(QRectF(10, (sy_t + sy_b) / 2.0 - 10, max(40.0, sx_l - 16), 20),
                             Qt.AlignCenter, "outside")
            painter.setPen(QPen(QColor("#0F766E")))
            painter.drawText(QRectF(sx_l + 12, (sy_t + sy_b) / 2.0 - 10, 70, 20),
                             Qt.AlignLeft, "inside")
        elif boundary == "RIGHT":
            painter.setPen(QPen(QColor("#0F766E")))
            painter.drawText(QRectF(sx_l + 12, (sy_t + sy_b) / 2.0 - 10, 70, 20),
                             Qt.AlignLeft, "inside")
            painter.setPen(QPen(QColor("#2563EB")))
            painter.drawText(QRectF(sx_r + 10, (sy_t + sy_b) / 2.0 - 10, 80, 20),
                             Qt.AlignLeft, "outside")
        elif boundary == "TOP":
            painter.setPen(QPen(QColor("#E11D48")))
            painter.drawText(QRectF((sx_l + sx_r) / 2.0 - 40, sy_t - 22, 80, 18),
                             Qt.AlignCenter, "outside")
            painter.setPen(QPen(QColor("#0F766E")))
            painter.drawText(QRectF((sx_l + sx_r) / 2.0 - 40, sy_t + 8, 80, 18),
                             Qt.AlignCenter, "inside")
        elif boundary == "BOTTOM":
            painter.setPen(QPen(QColor("#0F766E")))
            painter.drawText(QRectF((sx_l + sx_r) / 2.0 - 40, sy_b - 22, 80, 18),
                             Qt.AlignCenter, "inside")
            painter.setPen(QPen(QColor("#D97706")))
            painter.drawText(QRectF((sx_l + sx_r) / 2.0 - 40, sy_b + 8, 80, 18),
                             Qt.AlignCenter, "outside")

    def _draw_clip_four_rules(self, painter: QPainter, w: float):
        rules = [
            ("IN → IN", "keep P", QColor("#4F46E5")),
            ("IN → OUT", "keep I", QColor("#D97706")),
            ("OUT → IN", "I, then P", QColor("#059669")),
            ("OUT → OUT", "nothing", QColor("#E11D48")),
        ]
        box_w = 118.0
        gap = 8.0
        total = 4 * box_w + 3 * gap
        x0 = (w - total) / 2.0
        y = 12.0
        for i, (title, action, color) in enumerate(rules):
            bx = x0 + i * (box_w + gap)
            painter.setBrush(QBrush(QColor(255, 255, 255, 236)))
            painter.setPen(QPen(color, 1.3))
            painter.drawRoundedRect(QRectF(bx, y, box_w, 42), 10, 10)
            painter.setFont(get_ui_font(11, weight=700))
            painter.setPen(QPen(color))
            painter.drawText(QRectF(bx, y + 4, box_w, 16), Qt.AlignCenter, title)
            painter.setFont(get_ui_font(11, weight=500))
            painter.setPen(QPen(QColor("#475569")))
            painter.drawText(QRectF(bx, y + 20, box_w, 16), Qt.AlignCenter, action)

    def _draw_clip_output_strip(self, painter: QPainter, cd: dict, w: float):
        output = (cd.get("polygon") or {}).get("output") or []
        before = (cd.get("polygon") or {}).get("output_before") or []
        emitted = cd.get("emitted") or []
        case = cd.get("case")
        t = self._clip_ease()
        titles = {
            "in_in": "Inside → Inside  ·  keep P",
            "in_out": "Inside → Outside  ·  keep I, drop P",
            "out_in": "Outside → Inside  ·  keep I, then P",
            "out_out": "Outside → Outside  ·  emit nothing",
        }
        title = titles.get(case, "Output vertex list")
        card = QRectF(0, 12, min(w - 28.0, 640.0), 78 if case else 58)
        card.moveLeft((w - card.width()) / 2.0)
        painter.setBrush(QBrush(QColor(255, 255, 255, 236)))
        painter.setPen(QPen(QColor("#DDD6FE"), 1.2))
        painter.drawRoundedRect(card, 12, 12)
        painter.setFont(get_ui_font(12, weight=600))
        painter.setPen(QPen(QColor("#5B21B6")))
        painter.drawText(QRectF(card.left() + 16, card.top() + 8, card.width() - 32, 18), Qt.AlignLeft, title)

        chips = output if output else before
        max_chips = 10
        shown = chips[-max_chips:]
        skipped = max(0, len(chips) - len(shown))
        x = card.left() + 16
        y = card.top() + (36 if case else 28)
        if skipped:
            painter.setFont(get_ui_font(11, weight=500))
            painter.setPen(QPen(QColor("#94A3B8")))
            painter.drawText(QRectF(x, y, 36, 24), Qt.AlignLeft | Qt.AlignVCenter, "…")
            x += 28
        new_keys = {self._clip_pt_key(item.get("pt", (0, 0))) for item in emitted}
        new_kinds = {
            self._clip_pt_key(item.get("pt", (0, 0))): item.get("kind")
            for item in emitted
        }
        if not shown:
            painter.setFont(get_ui_font(12, weight=500))
            painter.setPen(QPen(QColor("#94A3B8")))
            painter.drawText(QRectF(x, y, 220, 24), Qt.AlignLeft | Qt.AlignVCenter,
                             "empty — nothing added")
            return
        for i, pt in enumerate(shown):
            key = self._clip_pt_key(pt)
            is_new = key in new_keys
            appear = t if is_new else 1.0
            if appear <= 0.02:
                continue
            kind_new = is_new and new_kinds.get(key) == "new"
            fill = QColor("#F59E0B") if kind_new else (QColor("#4F46E5") if is_new else QColor("#EEF2FF"))
            fg = QColor("#FFFFFF") if (kind_new or is_new) else QColor("#4338CA")
            painter.setBrush(QBrush(fill))
            painter.setPen(QPen(QColor("#FFFFFF") if (kind_new or is_new) else QColor("#C7D2FE"), 0.8))
            painter.drawRoundedRect(QRectF(x, y, 34, 24), 6, 6)
            painter.setFont(get_mono_font(10, weight=700))
            painter.setPen(QPen(fg))
            label = "I" if kind_new else ("P" if is_new else f"V{skipped + i + 1}")
            painter.drawText(QRectF(x, y, 34, 24), Qt.AlignCenter, label)
            x += 40

    def _draw_clip_polygon_lesson(self, painter: QPainter, cd: dict):
        w, h = float(self.width()), float(self.height())
        focus = cd.get("focus", "meet")
        caption = cd.get("caption", "")
        poly = cd.get("polygon") or {}
        orig = poly.get("original") or []
        incoming = poly.get("input") or orig
        outgoing = poly.get("output") or []
        is_final = bool(poly.get("is_final") or focus == "result")
        boundary = cd.get("active_boundary")
        case = cd.get("case")
        t = self._clip_ease()

        painter.save()
        self._draw_clip_grid(painter, w, h)
        self._draw_clip_spatial_regions(painter, cd, w, h, faint=True)

        if boundary:
            self._draw_clip_bit_plane(painter, cd, boundary, w, h)
            if focus in ("halfplane", "pass"):
                self._draw_clip_halfplane_captions(painter, cd, boundary)
        elif focus == "pipeline":
            self._draw_clip_boundaries(painter, cd, w, h, show_labels=True)
            labels = [("LEFT", "1"), ("RIGHT", "2"), ("BOTTOM", "3"), ("TOP", "4")]
            xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
            spots = {
                "LEFT": QPointF(sx_l - 18, (sy_t + sy_b) / 2.0),
                "RIGHT": QPointF(sx_r + 18, (sy_t + sy_b) / 2.0),
                "TOP": QPointF((sx_l + sx_r) / 2.0, sy_t - 16),
                "BOTTOM": QPointF((sx_l + sx_r) / 2.0, sy_b + 16),
            }
            for name, num in labels:
                pt = spots[name]
                painter.setBrush(QBrush(self._CLIP_BIT_COLORS[name]))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(pt, 11, 11)
                painter.setFont(get_ui_font(11, weight=700))
                painter.setPen(QPen(QColor("#FFFFFF")))
                painter.drawText(QRectF(pt.x() - 10, pt.y() - 9, 20, 18), Qt.AlignCenter, num)
        else:
            self._draw_clip_boundaries(painter, cd, w, h, show_labels=(focus in ("meet", "halfplane", "wrap")))

        self._draw_clip_window(painter, cd, emphasized=is_final or focus in ("meet", "result"))

        if orig and focus in ("meet", "wrap"):
            self._draw_clip_poly_shape(
                painter, orig, QColor(79, 70, 229, 36), QColor("#4F46E5"), width=2.2,
            )
            if focus == "meet" and orig:
                xmin, ymin, xmax, ymax, sx_l, sy_t, sx_r, sy_b = self._clip_window_screen(cd)
                painter.save()
                painter.setClipRect(QRectF(sx_l, sy_t, max(1.0, sx_r - sx_l), max(1.0, sy_b - sy_t)))
                self._draw_clip_poly_shape(
                    painter, orig, QColor(16, 185, 129, int(50 + 70 * t)), QColor("#059669"), width=2.8,
                )
                painter.restore()
        elif orig:
            self._draw_clip_poly_shape(
                painter, orig, QColor(148, 163, 184, 16), QColor("#94A3B8"),
                width=1.3, dashed=True,
            )

        same_as_orig = self._clip_pts_equal(incoming, orig)
        if focus in ("pass", "edge", "halfplane", "case") and incoming and not (focus in ("meet", "wrap") and same_as_orig):
            if not same_as_orig or focus != "pass":
                self._draw_clip_poly_shape(
                    painter, incoming, QColor(79, 70, 229, 40), QColor("#6366F1"),
                    width=1.8, dashed=True,
                )

        if focus == "pass_complete":
            morph = self._lerp_clip_polygon(incoming, outgoing, t)
            out_alpha = int(40 + 80 * t)
            self._draw_clip_poly_shape(
                painter, morph or outgoing, QColor(16, 185, 129, out_alpha), QColor("#059669"),
                width=2.6, dashed=len(outgoing) < 3,
            )
        elif is_final and len(outgoing) >= 3:
            painter.setPen(QPen(QColor(16, 185, 129, 70), 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            qpoly = QPolygonF([QPointF(*self._clip_to_s(px, py)) for px, py in outgoing])
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(qpoly)
            self._draw_clip_poly_shape(
                painter, outgoing, QColor(16, 185, 129, 90), QColor("#059669"), width=3.2,
            )
        elif focus == "edge":
            before = poly.get("output_before") or []
            if len(before) >= 2:
                self._draw_clip_poly_shape(
                    painter, before, QColor(16, 185, 129, 28), QColor("#10B981"),
                    width=2.0, dashed=True, closed=False,
                )
        elif focus == "case" and len(outgoing) >= 2:
            self._draw_clip_poly_shape(
                painter, outgoing, QColor(16, 185, 129, 40), QColor("#10B981"),
                width=2.4, dashed=False, closed=False,
            )

        edge_s, edge_p = cd.get("edge_s"), cd.get("edge_p")
        if edge_s and edge_p and focus in ("edge", "case"):
            s1 = QPointF(*self._clip_to_s(edge_s[0], edge_s[1]))
            s2 = QPointF(*self._clip_to_s(edge_p[0], edge_p[1]))
            inter = cd.get("intersection")
            i_pt = QPointF(*self._clip_to_s(inter[0], inter[1])) if inter else None
            keep = QPen(QColor("#059669"), 3.4, Qt.SolidLine, Qt.RoundCap)
            drop = QPen(QColor("#EF4444"), 2.6, Qt.DashLine, Qt.RoundCap)

            if case == "in_in":
                painter.setPen(keep)
                painter.drawLine(s1, s2)
            elif case == "out_out":
                painter.setPen(drop)
                painter.drawLine(s1, s2)
            elif i_pt is not None and case == "in_out":
                painter.setPen(keep)
                painter.drawLine(s1, i_pt)
                painter.setPen(drop)
                painter.drawLine(i_pt, s2)
            elif i_pt is not None and case == "out_in":
                painter.setPen(drop)
                painter.drawLine(s1, i_pt)
                painter.setPen(keep)
                painter.drawLine(i_pt, s2)
            else:
                painter.setPen(QPen(QColor("#4F46E5"), 3.2, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(s1, s2)

            mx = edge_s[0] + (edge_p[0] - edge_s[0]) * t
            my = edge_s[1] + (edge_p[1] - edge_s[1]) * t
            bead = QPointF(*self._clip_to_s(mx, my))
            painter.setBrush(QBrush(QColor("#7C3AED")))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.4))
            painter.drawEllipse(bead, 5.5, 5.5)

            s_in = bool(cd.get("s_inside"))
            p_in = bool(cd.get("p_inside"))
            s_col = QColor("#0F766E") if s_in else QColor("#E11D48")
            p_col = QColor("#0F766E") if p_in else QColor("#E11D48")
            self._draw_clip_poly_vertex(
                painter, edge_s, s_col, "S  " + ("inside" if s_in else "outside"),
                7.5, True, discarded=(case == "out_out" and not s_in),
            )
            self._draw_clip_poly_vertex(
                painter, edge_p, p_col, "P  " + ("inside" if p_in else "outside"),
                7.5, True, discarded=(not p_in and case in ("in_out", "out_out")),
            )

            if inter and t > 0.38:
                pulse = 5.5 + 2.0 * min(1.0, (t - 0.38) / 0.28)
                self._draw_clip_poly_vertex(painter, inter, QColor("#D97706"), "I  new", pulse, True)

        if focus in ("pass", "pass_complete", "result") and 3 <= len(outgoing if focus != "pass" else incoming) <= 8:
            pts = incoming if focus == "pass" else outgoing
            for i, pt in enumerate(pts):
                self._draw_clip_poly_vertex(painter, pt, QColor("#059669") if focus != "pass" else QColor("#4F46E5"),
                                            f"V{i+1}", 5.0)

        if focus in ("wrap",):
            self._draw_clip_four_rules(painter, w)
        if focus in ("edge", "case"):
            self._draw_clip_output_strip(painter, cd, w)

        tone = "neutral"
        if is_final and len(outgoing) >= 3:
            tone = "accept"
        elif is_final:
            tone = "reject"
        elif case == "out_out":
            tone = "reject"
        elif case == "in_in":
            tone = "accept"
        elif focus in ("edge", "pass", "case"):
            tone = "clip"
        self._draw_clip_insight(painter, caption, w, h, tone)
        painter.restore()

    # ------------------------------------------------------------------
    # Image Processing Mode (OpenCV Before / After)
    # ------------------------------------------------------------------
    def _draw_image(self, painter: QPainter, idata: dict):
        w, h = self.width(), self.height()
        orig_img = idata.get("original")  # QImage or numpy
        proc_img = idata.get("processed") # QImage or numpy
        title_orig = idata.get("title_orig", "Original Image (Input)")
        title_proc = idata.get("title_proc", "Processed Result")
        orig_dims = idata.get("orig_dims", "")
        proc_dims = idata.get("proc_dims", "")

        painter.save()
        margin = 16
        box_w = (w - 3 * margin) / 2.0
        box_h = h - 2 * margin - 10

        def render_qimage(img, target_rect, title, dims_str, is_processed=False):
            # Card Container
            painter.setPen(QPen(QColor(COLORS["border"]), 1.2))
            painter.setBrush(QBrush(QColor(20, 26, 34)))
            painter.drawRoundedRect(target_rect, 8, 8)

            # Card Header Bar
            header_rect = QRectF(target_rect.left(), target_rect.top(), target_rect.width(), 36)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(26, 34, 46)))
            painter.drawRoundedRect(header_rect, 8, 8)
            # Flatten bottom corners of header
            painter.drawRect(QRectF(target_rect.left(), target_rect.top() + 20, target_rect.width(), 16))

            # Header border line
            painter.setPen(QPen(QColor(COLORS["border"]), 1))
            painter.drawLine(QPointF(target_rect.left(), target_rect.top() + 36), QPointF(target_rect.right(), target_rect.top() + 36))

            # Title
            painter.setFont(QFont("Cascadia Mono", 10, QFont.Bold))
            painter.setPen(QPen(QColor(COLORS["accent_teal"] if is_processed else COLORS["accent_gold"])))
            painter.drawText(
                QRectF(target_rect.left() + 14, target_rect.top() + 4, target_rect.width() - 28, 28),
                Qt.AlignLeft | Qt.AlignVCenter,
                title
            )

            # Dimensions badge in header right
            if dims_str:
                painter.setFont(QFont("Cascadia Mono", 8))
                painter.setPen(QPen(QColor(COLORS["text_muted"])))
                painter.drawText(
                    QRectF(target_rect.left() + 14, target_rect.top() + 4, target_rect.width() - 28, 28),
                    Qt.AlignRight | Qt.AlignVCenter,
                    dims_str
                )

            # Image display area
            img_area = QRectF(
                target_rect.left() + 12,
                target_rect.top() + 46,
                target_rect.width() - 24,
                target_rect.height() - 56
            )

            if img and not img.isNull():
                scaled = img.scaled(
                    int(img_area.width()),
                    int(img_area.height()),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                dest_x = img_area.left() + (img_area.width() - scaled.width()) / 2
                dest_y = img_area.top() + (img_area.height() - scaled.height()) / 2
                painter.drawImage(QPointF(dest_x, dest_y), scaled)
            else:
                painter.setFont(QFont("Cascadia Mono", 9))
                painter.setPen(QPen(QColor(COLORS["text_muted"])))
                painter.drawText(
                    img_area,
                    Qt.AlignCenter,
                    "No image loaded\nClick 'Load Image...' in toolbar to select a file\nor select a procedural test pattern in parameters."
                )

        rect_left = QRectF(margin, margin, box_w, box_h)
        rect_right = QRectF(margin * 2 + box_w, margin, box_w, box_h)

        render_qimage(orig_img, rect_left, title_orig, orig_dims, is_processed=False)
        render_qimage(proc_img, rect_right, title_proc, proc_dims, is_processed=True)

        painter.restore()

    # ------------------------------------------------------------------
    # Color parsing helper
    # ------------------------------------------------------------------
    def _parse_color(self, c) -> QColor:
        if isinstance(c, QColor):
            color = QColor(c)
        elif isinstance(c, str):
            if c.startswith("rgba"):
                try:
                    parts = c.replace("rgba(", "").replace(")", "").split(",")
                    r = int(parts[0].strip())
                    g = int(parts[1].strip())
                    b = int(parts[2].strip())
                    a = float(parts[3].strip())
                    color = QColor(r, g, b, int(a * 255 if a <= 1.0 else a))
                except Exception:
                    color = QColor(COLORS["accent_teal"])
            else:
                color = QColor(c)
        else:
            color = QColor(COLORS["accent_teal"])

        legacy_palette = {
            (91, 141, 239): COLORS["accent_blue"],
            (78, 199, 176): COLORS["success"],
            (216, 169, 78): COLORS["accent_gold"],
            (234, 240, 246): COLORS["text_primary"],
        }
        replacement = legacy_palette.get((color.red(), color.green(), color.blue()))
        if replacement:
            replacement_color = QColor(replacement)
            replacement_color.setAlpha(color.alpha())
            return replacement_color
        return color
