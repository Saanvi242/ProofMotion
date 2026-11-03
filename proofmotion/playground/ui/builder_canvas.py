"""
playground/ui/builder_canvas.py
-------------------------------
Interactive 2D vector canvas for Proof Builder.
Enables visual point placement, vertex dragging, line drawing, polygon creation,
angle arc annotation, and selection editing.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QPolygonF, QFont, QPainterPath
)

from playground.proof_builder_model import (
    BuilderProofStep, BuilderShape, ShapeType
)
from resources.theme import COLORS, get_mono_font, get_ui_font


class BuilderCanvas(QWidget):
    statusMessage = pyqtSignal(str)
    stepModified = pyqtSignal()
    shapeSelected = pyqtSignal(str)  # shape ID or ""
    cursorCoordChanged = pyqtSignal(float, float)
    toolChanged = pyqtSignal(str)  # emitted when tool auto-switches to "select" after drawing
    zoomChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BuilderCanvas")
        self.setMinimumSize(400, 320)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self._step: Optional[BuilderProofStep] = None
        self._selected_shape_id: Optional[str] = None
        self._hovered_shape_id: Optional[str] = None

        self.tool = "select"  # select, pan, point, line, curve, triangle, polygon, rectangle, circle, slice, angle, text
        self.snap_to_grid = True
        self.grid_size = 0.5

        # Draft points while drawing multi-click shapes
        self._draft_pts: List[Tuple[float, float]] = []
        self._hover_world: Optional[Tuple[float, float]] = None

        # Camera & Viewport
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self._panning = False
        self._space_held = False
        self._drag_mode: Optional[str] = None  # "vertex" or "shape"
        self._dragged_point_idx: Optional[int] = None
        self._dragged_shape: Optional[BuilderShape] = None
        self._last_drag_world: Optional[Tuple[float, float]] = None
        self._last_mouse_pos = QPoint()

        # Letter generator for auto-naming points
        self._letter_counter = 0

    # ------------------------------------------------------------------
    # Data Binding
    # ------------------------------------------------------------------
    def set_step(self, step: Optional[BuilderProofStep]):
        self._step = step
        self._draft_pts.clear()
        self._selected_shape_id = None
        self._hovered_shape_id = None
        self._drag_mode = None
        self._dragged_shape = None
        self._last_drag_world = None
        self.update()

    def get_step(self) -> Optional[BuilderProofStep]:
        return self._step

    def selected_shape(self) -> Optional[BuilderShape]:
        if not self._step or not self._selected_shape_id:
            return None
        for s in self._step.shapes:
            if s.id == self._selected_shape_id:
                return s
        return None

    def set_selected_shape_id(self, shape_id: Optional[str]):
        self._selected_shape_id = shape_id
        self.shapeSelected.emit(shape_id or "")
        self.update()

    def set_snap_to_grid(self, enabled: bool):
        self.snap_to_grid = bool(enabled)
        self.update()

    def set_tool(self, tool_name: str):
        self.tool = tool_name
        self._draft_pts.clear()
        self._drag_mode = None
        self._dragged_shape = None
        self._last_drag_world = None
        if tool_name == "pan":
            self.setCursor(Qt.OpenHandCursor)
        elif tool_name == "select":
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.CrossCursor)

        hints = {
            "select": "Select / Drag: Click to select shapes, drag vertices to reshape, or drag background to pan.",
            "pan": "Pan View (✋): Click and drag anywhere to pan freely (or drag with right mouse, middle mouse, or hold Space).",
            "point": "Point: Click on canvas to drop a labeled point.",
            "line": "Line Segment: Click start point, then click end point.",
            "curve": "Curve (Bézier): Click start, click control/peak point, then click end point.",
            "triangle": "Triangle: Click three vertices to construct a triangle.",
            "polygon": "Polygon: Click vertices sequentially. Double-click or press Enter to close.",
            "rectangle": "Rectangle / Square: Click first corner, then click opposite corner.",
            "circle": "Circle: Click center point, then click or drag radius.",
            "slice": "Divide / Slice: Click inside any divided portion of a circle or polygon to select/isolate it.",
            "angle": "Angle Arc: Click two points (e.g. corner and inside a triangle) to place the angle symbol.",
            "right_angle": "Right Angle (90°): Click corner and second point (or double-click) to place a 90° box.",
            "text": "Math Label: Click on canvas to place a formula or text annotation.",
        }
        self.statusMessage.emit(hints.get(tool_name, ""))
        self.update()

    def reset_view(self):
        self._zoom = 1.0
        self._pan = [0.0, 0.0]
        self.zoomChanged.emit(self._zoom)
        self.update()

    def pan_by(self, dx: float, dy: float):
        self._pan[0] += dx
        self._pan[1] += dy
        self.update()

    def zoom_at(self, factor: float, center_screen: Optional[QPoint] = None):
        old_zoom = self._zoom
        new_zoom = max(0.15, min(8.0, old_zoom * factor))
        if abs(new_zoom - old_zoom) < 1e-5:
            return

        if center_screen is not None:
            sx = float(center_screen.x())
            sy = float(center_screen.y())
            wx, wy = self.screen_to_world(sx, sy)

            self._zoom = new_zoom
            s = self._scale()
            w_half = self.width() / 2.0
            h_half = self.height() / 2.0
            self._pan[0] = sx - w_half - wx * s
            self._pan[1] = sy - h_half + wy * s
        else:
            self._zoom = new_zoom

        self.zoomChanged.emit(self._zoom)
        self.update()

    def zoom_by(self, factor: float):
        self.zoom_at(factor, None)

    def fit_to_content(self):
        if not self._step or not self._step.shapes:
            self.reset_view()
            return
        all_pts: List[Tuple[float, float]] = []
        for s in self._step.shapes:
            st = s.shape_type
            if st == ShapeType.POINT.value and len(s.coords) >= 2:
                all_pts.append((s.coords[0], s.coords[1]))
            elif st in (ShapeType.LINE.value, ShapeType.CURVE.value):
                for i in range(0, len(s.coords) - 1, 2):
                    all_pts.append((s.coords[i], s.coords[i + 1]))
            elif st == ShapeType.POLYGON.value and s.polygon_points:
                all_pts.extend(s.polygon_points)
            elif st in (ShapeType.CIRCLE.value, ShapeType.ANGLE.value, ShapeType.SECTOR.value) and len(s.coords) >= 3:
                cx, cy, r = s.coords[0], s.coords[1], s.coords[2]
                all_pts.extend([(cx - r, cy - r), (cx + r, cy + r)])
            elif st == ShapeType.TEXT.value and len(s.coords) >= 2:
                all_pts.append((s.coords[0], s.coords[1]))

        if not all_pts:
            self.reset_view()
            return

        min_x = min(p[0] for p in all_pts)
        max_x = max(p[0] for p in all_pts)
        min_y = min(p[1] for p in all_pts)
        max_y = max(p[1] for p in all_pts)

        mid_x = (min_x + max_x) * 0.5
        mid_y = (min_y + max_y) * 0.5
        span_x = max(1.5, max_x - min_x)
        span_y = max(1.5, max_y - min_y)

        base_s = min(self.width(), self.height()) / 14.0
        target_zoom = min(self.width() / (span_x * base_s * 1.5), self.height() / (span_y * base_s * 1.5))
        self._zoom = max(0.25, min(4.0, target_zoom))
        s = self._scale()
        self._pan = [-mid_x * s, mid_y * s]
        self.zoomChanged.emit(self._zoom)
        self.update()

    # ------------------------------------------------------------------
    # Coordinate Transforms
    # ------------------------------------------------------------------
    def _scale(self) -> float:
        base = min(self.width(), self.height()) / 14.0
        return base * self._zoom

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        cx = self.width() / 2.0 + self._pan[0]
        cy = self.height() / 2.0 + self._pan[1]
        s = self._scale()
        return cx + wx * s, cy - wy * s

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        cx = self.width() / 2.0 + self._pan[0]
        cy = self.height() / 2.0 + self._pan[1]
        s = self._scale()
        wx = (sx - cx) / s
        wy = (cy - sy) / s
        return wx, wy

    def _snap(self, wx: float, wy: float) -> Tuple[float, float]:
        if not self.snap_to_grid or self.grid_size <= 0:
            return round(wx, 3), round(wy, 3)
        gs = self.grid_size
        return round(round(wx / gs) * gs, 3), round(round(wy / gs) * gs, 3)

    # ------------------------------------------------------------------
    # Next Available Point Label
    # ------------------------------------------------------------------
    def _next_point_name(self) -> str:
        used_names = set()
        if self._step:
            for s in self._step.shapes:
                if s.shape_type == ShapeType.POINT.value and s.name:
                    used_names.add(s.name.strip().upper())
        for code in range(ord('A'), ord('Z') + 1):
            letter = chr(code)
            if letter not in used_names:
                return letter
        # Fallback to A1, B1...
        self._letter_counter += 1
        return f"P{self._letter_counter}"

    @staticmethod
    def _is_point_in_polygon(px: float, py: float, pts: List[Tuple[float, float]]) -> bool:
        """Ray casting algorithm to test if (px, py) is strictly inside a 2D polygon."""
        inside = False
        n = len(pts)
        if n < 3:
            return False
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1):
                inside = not inside
        return inside

    def _collect_canvas_segments(self) -> List[Tuple[Tuple[float, float], Tuple[float, float], str]]:
        """Extracts all line segments from the canvas (both standalone lines and polygon edges)."""
        segments = []
        if not self._step:
            return segments
        for s in self._step.shapes:
            if s.shape_type == ShapeType.LINE.value and len(s.coords) >= 4:
                segments.append(((s.coords[0], s.coords[1]), (s.coords[2], s.coords[3]), s.id))
            elif s.shape_type == ShapeType.POLYGON.value and len(s.polygon_points) >= 3:
                pts = s.polygon_points
                n = len(pts)
                for i in range(n):
                    segments.append((pts[i], pts[(i + 1) % n], s.id))
        return segments

    @staticmethod
    def _point_to_segment_dist(px: float, py: float, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Euclidean distance from point (px, py) to line segment (a, b)."""
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        l2 = dx * dx + dy * dy
        if l2 < 1e-12:
            return math.hypot(px - a[0], py - a[1])
        t = max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / l2))
        proj_x = a[0] + t * dx
        proj_y = a[1] + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def _find_nearest_segment(
        self, wx: float, wy: float, max_dist: float = 1.2
    ) -> Optional[Tuple[Tuple[float, float], Tuple[float, float], str]]:
        """Finds the closest canvas segment (line or polygon edge) within max_dist of (wx, wy)."""
        segments = self._collect_canvas_segments()
        best_seg = None
        best_d = max_dist
        for seg in segments:
            d = self._point_to_segment_dist(wx, wy, seg[0], seg[1])
            if d < best_d:
                best_d = d
                best_seg = seg
        return best_seg

    @staticmethod
    def _line_line_intersection(
        a1: Tuple[float, float], b1: Tuple[float, float],
        a2: Tuple[float, float], b2: Tuple[float, float]
    ) -> Optional[Tuple[float, float]]:
        """Computes intersection of two infinite lines passing through (a1, b1) and (a2, b2)."""
        for p_a in (a1, b1):
            for p_b in (a2, b2):
                if math.hypot(p_a[0] - p_b[0], p_a[1] - p_b[1]) < 0.15:
                    return p_a

        dx1 = b1[0] - a1[0]
        dy1 = b1[1] - a1[1]
        dx2 = b2[0] - a2[0]
        dy2 = b2[1] - a2[1]

        denom = dx1 * dy2 - dy1 * dx2
        if abs(denom) < 1e-7:
            return None

        t1 = ((a2[0] - a1[0]) * dy2 - (a2[1] - a1[1]) * dx2) / denom
        ix = a1[0] + t1 * dx1
        iy = a1[1] + t1 * dy1
        return round(ix, 3), round(iy, 3)

    def _create_angle_from_two_points(
        self, p1: Tuple[float, float], p2: Tuple[float, float], is_right: bool = False
    ) -> BuilderShape:
        """
        Universally creates an Angle shape from two clicked points in ANY geometry case:
        1. Two distinct lines / segments (e.g. triangle edge + passing line, or two intersecting lines).
        2. Point near a vertex + sector click (works for interior AND exterior angles!).
        3. Two points inside a polygon.
        4. Arbitrary two points on free canvas.
        """
        apex = p1
        start_deg = 0.0
        span_deg = 90.0 if is_right else 60.0
        rad = 0.7
        is_rt = is_right

        if not self._step:
            return BuilderShape(
                shape_type=ShapeType.ANGLE.value,
                name="90°" if is_rt else "60°",
                color="#D8A94E" if is_rt else "#F59E0B",
                is_right_angle=is_rt,
                coords=[apex[0], apex[1], rad, start_deg, span_deg]
            )

        # --------------------------------------------------------------
        # CASE 1: Clicked two segments / edges (e.g. Triangle edge + passing line, or two intersecting lines)
        # --------------------------------------------------------------
        seg1 = self._find_nearest_segment(p1[0], p1[1], max_dist=1.2)
        seg2 = self._find_nearest_segment(p2[0], p2[1], max_dist=1.2)

        if seg1 and seg2 and (seg1 != seg2):
            inter = self._line_line_intersection(seg1[0], seg1[1], seg2[0], seg2[1])
            is_valid_inter = (inter is not None) and (
                (seg1[2] != seg2[2]) or (math.hypot(p1[0] - inter[0], p1[1] - inter[1]) < 1.5)
            )
            if is_valid_inter and inter is not None:
                ix, iy = inter
                # Direction vector along seg1 line
                d1 = (seg1[1][0] - seg1[0][0], seg1[1][1] - seg1[0][1])
                len_d1 = math.hypot(d1[0], d1[1])
                if len_d1 > 1e-6:
                    u_dir = (d1[0] / len_d1, d1[1] / len_d1)
                    # Dot product with offset from inter to p1
                    w1 = (p1[0] - ix, p1[1] - iy)
                    if math.hypot(w1[0], w1[1]) > 0.15:
                        dot1 = w1[0] * u_dir[0] + w1[1] * u_dir[1]
                        u = (u_dir[0] if dot1 >= 0 else -u_dir[0], u_dir[1] if dot1 >= 0 else -u_dir[1])
                    else:
                        d0 = math.hypot(seg1[0][0] - ix, seg1[0][1] - iy)
                        d_end = math.hypot(seg1[1][0] - ix, seg1[1][1] - iy)
                        far = seg1[0] if d0 > d_end else seg1[1]
                        u = (far[0] - ix, far[1] - iy)
                else:
                    u = (1.0, 0.0)

                # Direction vector along seg2 line
                d2 = (seg2[1][0] - seg2[0][0], seg2[1][1] - seg2[0][1])
                len_d2 = math.hypot(d2[0], d2[1])
                if len_d2 > 1e-6:
                    v_dir = (d2[0] / len_d2, d2[1] / len_d2)
                    # Dot product with offset from inter to p2
                    w2 = (p2[0] - ix, p2[1] - iy)
                    if math.hypot(w2[0], w2[1]) > 0.15:
                        dot2 = w2[0] * v_dir[0] + w2[1] * v_dir[1]
                        v = (v_dir[0] if dot2 >= 0 else -v_dir[0], v_dir[1] if dot2 >= 0 else -v_dir[1])
                    else:
                        d0 = math.hypot(seg2[0][0] - ix, seg2[0][1] - iy)
                        d_end = math.hypot(seg2[1][0] - ix, seg2[1][1] - iy)
                        far = seg2[0] if d0 > d_end else seg2[1]
                        v = (far[0] - ix, far[1] - iy)
                else:
                    v = (0.0, 1.0)

                if math.hypot(u[0], u[1]) > 1e-4 and math.hypot(v[0], v[1]) > 1e-4:
                    ang1 = math.degrees(math.atan2(u[1], u[0])) % 360.0
                    ang2 = math.degrees(math.atan2(v[1], v[0])) % 360.0

                    span_A = (ang2 - ang1) % 360.0
                    span_B = (ang1 - ang2) % 360.0

                    if span_A <= 180.0:
                        start_deg, span_deg = ang1, span_A
                    else:
                        start_deg, span_deg = ang2, span_B

                    rad = 0.75
                    if not is_rt and abs(span_deg - 90.0) < 3.5:
                        is_rt = True

                    name = "90°" if is_rt else f"{round(span_deg)}°"
                    deg_span = 90.0 if is_rt else span_deg
                    return BuilderShape(
                        shape_type=ShapeType.ANGLE.value,
                        name=name,
                        color="#D8A94E" if is_rt else "#F59E0B",
                        is_right_angle=is_rt,
                        coords=[round(ix, 2), round(iy, 2), round(rad, 2), round(start_deg, 1), round(deg_span, 1)]
                    )

        # --------------------------------------------------------------
        # CASE 2: Point 1 is at/near a vertex, Point 2 chooses orientation (Interior OR Exterior!)
        # --------------------------------------------------------------
        target_poly: Optional[BuilderShape] = None
        target_vertex_idx: Optional[int] = None

        for s in reversed(self._step.shapes):
            if s.shape_type == ShapeType.POLYGON.value and len(s.polygon_points) >= 3:
                for idx, (vx, vy) in enumerate(s.polygon_points):
                    if math.hypot(p1[0] - vx, p1[1] - vy) <= 0.8:
                        target_poly = s
                        target_vertex_idx = idx
                        break
                    elif math.hypot(p2[0] - vx, p2[1] - vy) <= 0.8:
                        target_poly = s
                        target_vertex_idx = idx
                        p1, p2 = p2, p1
                        break
                if target_poly:
                    break

        if not target_poly:
            for s in reversed(self._step.shapes):
                if s.shape_type == ShapeType.POLYGON.value and len(s.polygon_points) >= 3:
                    in1 = self._is_point_in_polygon(p1[0], p1[1], s.polygon_points)
                    in2 = self._is_point_in_polygon(p2[0], p2[1], s.polygon_points)
                    if in1 or in2:
                        target_poly = s
                        best_d = float("inf")
                        best_idx = 0
                        for idx, (vx, vy) in enumerate(s.polygon_points):
                            d = math.hypot(p1[0] - vx, p1[1] - vy)
                            if d < best_d:
                                best_d = d
                                best_idx = idx
                        target_vertex_idx = best_idx
                        break

        if target_poly and target_vertex_idx is not None:
            pts = target_poly.polygon_points
            n = len(pts)
            apex = pts[target_vertex_idx]
            prev_pt = pts[(target_vertex_idx - 1) % n]
            next_pt = pts[(target_vertex_idx + 1) % n]

            u1 = (prev_pt[0] - apex[0], prev_pt[1] - apex[1])
            u2 = (next_pt[0] - apex[0], next_pt[1] - apex[1])
            len1 = math.hypot(u1[0], u1[1])
            len2 = math.hypot(u2[0], u2[1])

            ang1 = math.degrees(math.atan2(u1[1], u1[0])) % 360.0
            ang2 = math.degrees(math.atan2(u2[1], u2[0])) % 360.0

            span_A = (ang2 - ang1) % 360.0
            start_A = ang1
            mid_A = math.radians((start_A + span_A / 2.0) % 360.0)
            test_A = (apex[0] + 0.25 * math.cos(mid_A), apex[1] + 0.25 * math.sin(mid_A))

            span_B = (ang1 - ang2) % 360.0
            start_B = ang2

            is_A_interior = self._is_point_in_polygon(test_A[0], test_A[1], pts)

            p2_is_interior = self._is_point_in_polygon(p2[0], p2[1], pts)
            p2_dist = math.hypot(p2[0] - apex[0], p2[1] - apex[1])

            if p2_dist > 0.5 and not p2_is_interior:
                # User clicked outside: exterior angle!
                start_deg, span_deg = (start_B, span_B) if is_A_interior else (start_A, span_A)
            else:
                # User clicked inside: interior angle!
                start_deg, span_deg = (start_A, span_A) if is_A_interior else (start_B, span_B)

            rad = max(0.45, min(0.9, min(len1, len2) * 0.42))
            if not is_rt and abs(span_deg - 90.0) < 3.5:
                is_rt = True

            name = "90°" if is_rt else f"{round(span_deg)}°"
            deg_span = 90.0 if is_rt else span_deg
            return BuilderShape(
                shape_type=ShapeType.ANGLE.value,
                name=name,
                color="#D8A94E" if is_rt else "#F59E0B",
                is_right_angle=is_rt,
                coords=[round(apex[0], 2), round(apex[1], 2), round(rad, 2), round(start_deg, 1), round(deg_span, 1)]
            )

        # --------------------------------------------------------------
        # CASE 3: Standalone two points on free canvas
        # --------------------------------------------------------------
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if math.hypot(dx, dy) > 1e-4:
            start_deg = math.degrees(math.atan2(dy, dx)) % 360.0
        else:
            start_deg = 0.0
        span_deg = 90.0 if is_rt else 60.0
        rad = max(0.5, min(1.0, math.hypot(dx, dy) * 0.5)) if math.hypot(dx, dy) > 0.5 else 0.7

        name = "90°" if is_rt else f"{round(span_deg)}°"
        return BuilderShape(
            shape_type=ShapeType.ANGLE.value,
            name=name,
            color="#D8A94E" if is_rt else "#F59E0B",
            is_right_angle=is_rt,
            coords=[round(p1[0], 2), round(p1[1], 2), round(rad, 2), round(start_deg, 1), round(span_deg, 1)]
        )

    def _detect_shape_portion(self, wx: float, wy: float) -> Optional[BuilderShape]:
        """
        Detects if (wx, wy) lies inside a shape divided by canvas lines
        (e.g. circle divided into sectors or segments, or polygon divided by lines),
        and returns a new BuilderShape representing that specific portion/slice.
        """
        if not self._step:
            return None

        # 1. Circle divided by lines or radial segments
        for s in reversed(self._step.shapes):
            if s.shape_type == ShapeType.CIRCLE.value and len(s.coords) >= 3:
                cx, cy, r = s.coords[0], s.coords[1], s.coords[2]
                dist = math.hypot(wx - cx, wy - cy)
                if dist <= r:
                    boundary_angles: List[float] = []

                    for line in self._step.shapes:
                        if line.shape_type == ShapeType.LINE.value and len(line.coords) >= 4:
                            x1, y1, x2, y2 = line.coords[0], line.coords[1], line.coords[2], line.coords[3]
                            dx = x2 - x1
                            dy = y2 - y1
                            l2 = dx * dx + dy * dy
                            if l2 < 1e-8:
                                continue

                            # Endpoint near center (radius line)
                            if math.hypot(x1 - cx, y1 - cy) < 0.35:
                                ang = math.degrees(math.atan2(y2 - cy, x2 - cx)) % 360.0
                                boundary_angles.append(ang)
                                continue
                            elif math.hypot(x2 - cx, y2 - cy) < 0.35:
                                ang = math.degrees(math.atan2(y1 - cy, x1 - cx)) % 360.0
                                boundary_angles.append(ang)
                                continue

                            # Line-circle intersection
                            fx = x1 - cx
                            fy = y1 - cy
                            a = l2
                            b = 2.0 * (fx * dx + fy * dy)
                            c_coeff = fx * fx + fy * fy - r * r
                            disc = b * b - 4.0 * a * c_coeff

                            if disc >= 0:
                                sq_disc = math.sqrt(disc)
                                t1 = (-b - sq_disc) / (2.0 * a)
                                t2 = (-b + sq_disc) / (2.0 * a)
                                dist_to_center = abs(dy * cx - dx * cy + x2 * y1 - y2 * x1) / math.sqrt(l2)
                                if dist_to_center < r * 0.99:
                                    ix1 = x1 + t1 * dx
                                    iy1 = y1 + t1 * dy
                                    ix2 = x2 + t2 * dx
                                    iy2 = y2 + t2 * dy
                                    ang1 = math.degrees(math.atan2(iy1 - cy, ix1 - cx)) % 360.0
                                    ang2 = math.degrees(math.atan2(iy2 - cy, ix2 - cx)) % 360.0
                                    boundary_angles.extend([ang1, ang2])

                    if boundary_angles:
                        unique_angles: List[float] = []
                        for ang in sorted(boundary_angles):
                            if not any(abs((ang - u) % 360.0) < 1.5 or abs((u - ang) % 360.0) < 1.5 for u in unique_angles):
                                unique_angles.append(ang)

                        if len(unique_angles) == 1:
                            unique_angles.append((unique_angles[0] + 180.0) % 360.0)
                            unique_angles.sort()

                        if len(unique_angles) >= 2:
                            click_ang = math.degrees(math.atan2(wy - cy, wx - cx)) % 360.0
                            n_ang = len(unique_angles)
                            best_start = unique_angles[0]
                            best_span = 360.0

                            for i in range(n_ang):
                                a_start = unique_angles[i]
                                a_next = unique_angles[(i + 1) % n_ang]
                                span = (a_next - a_start) % 360.0
                                if span < 1e-3:
                                    span = 360.0
                                if ((click_ang - a_start) % 360.0) <= span:
                                    best_start = a_start
                                    best_span = span
                                    break

                            sector_name = f"Sector ({round(best_span)}°)" if abs(best_span - 90.0) >= 2.0 else "Quadrant (90°)"
                            return BuilderShape(
                                shape_type=ShapeType.SECTOR.value,
                                name=sector_name,
                                color="#5EEAD4",
                                fill_color="rgba(94, 234, 212, 0.35)",
                                stroke_width=2.2,
                                coords=[round(cx, 3), round(cy, 3), round(r, 3), round(best_start, 1), round(best_span, 1)]
                            )

        # 2. Polygon divided by lines
        for s in reversed(self._step.shapes):
            if s.shape_type == ShapeType.POLYGON.value and len(s.polygon_points) >= 3:
                pts = list(s.polygon_points)
                if self._is_point_in_polygon(wx, wy, pts):
                    dividing_segs = []
                    for line in self._step.shapes:
                        if line.shape_type == ShapeType.LINE.value and len(line.coords) >= 4:
                            lx1, ly1, lx2, ly2 = line.coords[0], line.coords[1], line.coords[2], line.coords[3]
                            mid_lx = (lx1 + lx2) * 0.5
                            mid_ly = (ly1 + ly2) * 0.5
                            if (self._is_point_in_polygon(mid_lx, mid_ly, pts) or
                                self._is_point_in_polygon(lx1, ly1, pts) or
                                self._is_point_in_polygon(lx2, ly2, pts)):
                                dividing_segs.append(((lx1, ly1), (lx2, ly2)))

                    if dividing_segs:
                        clipped_poly = list(pts)
                        for (lx1, ly1), (lx2, ly2) in dividing_segs:
                            dx = lx2 - lx1
                            dy = ly2 - ly1
                            click_side = dx * (wy - ly1) - dy * (wx - lx1)
                            if abs(click_side) < 1e-6:
                                continue

                            new_poly = []
                            n_p = len(clipped_poly)
                            for k in range(n_p):
                                p_curr = clipped_poly[k]
                                p_prev = clipped_poly[(k - 1) % n_p]
                                side_curr = dx * (p_curr[1] - ly1) - dy * (p_curr[0] - lx1)
                                side_prev = dx * (p_prev[1] - ly1) - dy * (p_prev[0] - lx1)

                                in_curr = (side_curr * click_side) >= -1e-6
                                in_prev = (side_prev * click_side) >= -1e-6

                                if in_curr:
                                    if not in_prev:
                                        inter = self._line_line_intersection((lx1, ly1), (lx2, ly2), p_prev, p_curr)
                                        if inter:
                                            new_poly.append(inter)
                                    new_poly.append(p_curr)
                                elif in_prev:
                                    inter = self._line_line_intersection((lx1, ly1), (lx2, ly2), p_prev, p_curr)
                                    if inter:
                                        new_poly.append(inter)

                            if len(new_poly) >= 3:
                                clipped_poly = new_poly

                        # Clean up duplicate and collinear vertices
                        clean_pts = []
                        for p_pt in clipped_poly:
                            if not clean_pts or math.hypot(p_pt[0] - clean_pts[-1][0], p_pt[1] - clean_pts[-1][1]) > 0.05:
                                clean_pts.append(p_pt)
                        if len(clean_pts) >= 2 and math.hypot(clean_pts[0][0] - clean_pts[-1][0], clean_pts[0][1] - clean_pts[-1][1]) < 0.05:
                            clean_pts.pop()
                        # Remove collinear vertices
                        if len(clean_pts) >= 3:
                            simplified_pts = []
                            n_c = len(clean_pts)
                            for i in range(n_c):
                                prev_p = clean_pts[(i - 1) % n_c]
                                curr_p = clean_pts[i]
                                next_p = clean_pts[(i + 1) % n_c]
                                cross_v = (curr_p[0] - prev_p[0]) * (next_p[1] - curr_p[1]) - (curr_p[1] - prev_p[1]) * (next_p[0] - curr_p[0])
                                if abs(cross_v) > 1e-3:
                                    simplified_pts.append(curr_p)
                            if len(simplified_pts) >= 3:
                                clean_pts = simplified_pts

                        if len(clean_pts) >= 3 and self._is_point_in_polygon(wx, wy, clean_pts):
                            return BuilderShape(
                                shape_type=ShapeType.POLYGON.value,
                                name=f"{s.name or 'Shape'} Portion",
                                color="#5EEAD4",
                                fill_color="rgba(94, 234, 212, 0.35)",
                                stroke_width=2.2,
                                polygon_points=[(round(px, 3), round(py, 3)) for px, py in clean_pts]
                            )

        return None

    def _finish_shape_creation(self, shape: BuilderShape, message: str = ""):
        """Adds newly created shape, selects it, and auto-switches to select tool for immediate dragging."""
        if not self._step:
            return
        self._step.shapes.append(shape)
        self.set_selected_shape_id(shape.id)
        self.stepModified.emit()
        # Automatically switch to select tool so the user can immediately drag and move it anywhere!
        self.set_tool("select")
        self.toolChanged.emit("select")
        msg = message or f"{shape.shape_type.capitalize()} created! Click and drag anywhere to move or place it on the canvas."
        self.statusMessage.emit(msg)
        self.update()

    # ------------------------------------------------------------------
    # Mouse Events
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        pos = event.pos()
        wx, wy = self.screen_to_world(pos.x(), pos.y())
        snapped_wx, snapped_wy = self._snap(wx, wy)

        # Panning triggers:
        # 1. Right or Middle mouse button
        # 2. Left click with Pan tool (self.tool == "pan")
        # 3. Holding Spacebar (self._space_held)
        if event.button() in (Qt.RightButton, Qt.MiddleButton) or (
            event.button() == Qt.LeftButton and (self.tool == "pan" or self._space_held)
        ):
            self._panning = True
            self._last_mouse_pos = pos
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.LeftButton:
            if self.tool == "select":
                # 1. Check if clicking on an individual vertex handle to reshape
                hit = self._hit_test_point(pos.x(), pos.y())
                if hit is not None:
                    shape, pt_idx = hit
                    self._drag_mode = "vertex"
                    self._dragged_shape = shape
                    self._dragged_point_idx = pt_idx
                    self._last_drag_world = (snapped_wx, snapped_wy)
                    self.set_selected_shape_id(shape.id)
                    self.setCursor(Qt.CrossCursor)
                    return

                # 2. Check if clicking on the body of ANY shape to move the entire shape
                shape_hit = self._hit_test_any_shape(pos.x(), pos.y())
                if shape_hit is not None:
                    # Check if this shape is divided by lines and user clicked inside a divided portion/region
                    if shape_hit.shape_type in (ShapeType.CIRCLE.value, ShapeType.POLYGON.value):
                        portion = self._detect_shape_portion(snapped_wx, snapped_wy)
                        if portion and portion.name != shape_hit.name:
                            self._finish_shape_creation(portion, f"Portion '{portion.name}' selected! Drag to move anywhere.")
                            return

                    self.set_selected_shape_id(shape_hit.id)
                    self._drag_mode = "shape"
                    self._dragged_shape = shape_hit
                    self._last_drag_world = (snapped_wx, snapped_wy)
                    self.setCursor(Qt.ClosedHandCursor)
                    self.statusMessage.emit(
                        f"Moving {shape_hit.shape_type.capitalize()} '{shape_hit.name or ''}'. Drag to place anywhere on canvas."
                    )
                    self.update()
                    return
                else:
                    # Clicked on empty canvas background in Select mode: pan freely!
                    self.set_selected_shape_id(None)
                    self._drag_mode = None
                    self._dragged_shape = None
                    self._last_drag_world = None
                    self._panning = True
                    self._last_mouse_pos = pos
                    self.setCursor(Qt.ClosedHandCursor)
                    self.update()
                    return

            if not self._step:
                return

            # Tool actions:
            if self.tool == "point":
                new_pt = BuilderShape(
                    shape_type=ShapeType.POINT.value,
                    name=self._next_point_name(),
                    color="#6C5CE7",
                    coords=[snapped_wx, snapped_wy, 4.5]
                )
                self._finish_shape_creation(
                    new_pt, f"Point {new_pt.name} placed at ({snapped_wx:.1f}, {snapped_wy:.1f}). Drag to move anywhere."
                )

            elif self.tool == "line":
                if not self._draft_pts:
                    self._draft_pts.append((snapped_wx, snapped_wy))
                    self.statusMessage.emit(f"Line start set at ({snapped_wx:.1f}, {snapped_wy:.1f}). Click to place end point.")
                else:
                    start = self._draft_pts[0]
                    self._draft_pts.clear()
                    new_line = BuilderShape(
                        shape_type=ShapeType.LINE.value,
                        name="",
                        color="#5B8DEF",
                        stroke_width=2.5,
                        coords=[start[0], start[1], snapped_wx, snapped_wy]
                    )
                    self._finish_shape_creation(new_line, "Line created! Click and drag to move or place it anywhere.")

            elif self.tool == "triangle":
                self._draft_pts.append((snapped_wx, snapped_wy))
                if len(self._draft_pts) < 3:
                    self.statusMessage.emit(f"Triangle vertex {len(self._draft_pts)} placed. Place vertex {len(self._draft_pts) + 1}.")
                else:
                    pts = list(self._draft_pts)
                    self._draft_pts.clear()
                    new_tri = BuilderShape(
                        shape_type=ShapeType.POLYGON.value,
                        name="Δ",
                        color="#5B8DEF",
                        fill_color="rgba(91, 141, 239, 0.22)",
                        stroke_width=2.5,
                        polygon_points=pts
                    )
                    self._finish_shape_creation(new_tri, "Triangle created! Click inside it to drag and place anywhere.")

            elif self.tool == "polygon":
                # If clicking close to the first point, close polygon
                if len(self._draft_pts) >= 2:
                    first = self._draft_pts[0]
                    if math.hypot(snapped_wx - first[0], snapped_wy - first[1]) < 0.4:
                        pts = list(self._draft_pts)
                        self._draft_pts.clear()
                        new_poly = BuilderShape(
                            shape_type=ShapeType.POLYGON.value,
                            name="Poly",
                            color="#2F9E78",
                            fill_color="rgba(47, 158, 120, 0.22)",
                            stroke_width=2.2,
                            polygon_points=pts
                        )
                        self._finish_shape_creation(new_poly, "Polygon closed! Drag to move anywhere.")
                        return
                self._draft_pts.append((snapped_wx, snapped_wy))
                self.statusMessage.emit(f"Polygon vertex {len(self._draft_pts)} placed. Click next, or double-click to finish.")
                self.update()

            elif self.tool == "rectangle":
                if not self._draft_pts:
                    self._draft_pts.append((snapped_wx, snapped_wy))
                    self.statusMessage.emit("First corner placed. Click opposite corner.")
                else:
                    x0, y0 = self._draft_pts[0]
                    self._draft_pts.clear()
                    x1, y1 = snapped_wx, snapped_wy
                    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                    new_rect = BuilderShape(
                        shape_type=ShapeType.POLYGON.value,
                        name="Rect",
                        color="#6C5CE7",
                        fill_color="rgba(108, 92, 231, 0.25)",
                        stroke_width=2.2,
                        polygon_points=pts
                    )
                    self._finish_shape_creation(new_rect, "Rectangle created! Click inside it to drag and place anywhere.")

            elif self.tool == "circle":
                if not self._draft_pts:
                    self._draft_pts.append((snapped_wx, snapped_wy))
                    self.statusMessage.emit("Center point placed. Click to set circle radius.")
                else:
                    cx, cy = self._draft_pts[0]
                    self._draft_pts.clear()
                    rad = max(0.5, round(math.hypot(snapped_wx - cx, snapped_wy - cy), 2))
                    new_circ = BuilderShape(
                        shape_type=ShapeType.CIRCLE.value,
                        name="Circle",
                        color="#5B8DEF",
                        fill_color="rgba(91, 141, 239, 0.08)",
                        stroke_width=2.0,
                        coords=[cx, cy, rad]
                    )
                    self._finish_shape_creation(new_circ, f"Circle created (radius {rad:.1f})! Drag anywhere to move it.")

            elif self.tool == "curve":
                self._draft_pts.append((snapped_wx, snapped_wy))
                if len(self._draft_pts) == 1:
                    self.statusMessage.emit("Curve start placed. Click to place curve peak / control point.")
                elif len(self._draft_pts) == 2:
                    self.statusMessage.emit("Control point placed. Click to place curve end point.")
                else:
                    p0 = self._draft_pts[0]
                    pc = self._draft_pts[1]
                    p1 = self._draft_pts[2]
                    self._draft_pts.clear()
                    new_curve = BuilderShape(
                        shape_type=ShapeType.CURVE.value,
                        name="Curve",
                        color="#5EEAD4",
                        stroke_width=2.5,
                        coords=[p0[0], p0[1], pc[0], pc[1], p1[0], p1[1]]
                    )
                    self._finish_shape_creation(new_curve, "Curve created! Drag vertices or control point to adjust.")

            elif self.tool == "slice":
                portion = self._detect_shape_portion(snapped_wx, snapped_wy)
                if portion:
                    self._finish_shape_creation(portion, f"Divided portion '{portion.name}' selected! Drag anywhere to move it.")
                else:
                    self.statusMessage.emit("Click inside a circle or polygon divided by lines to select that portion.")

            elif self.tool in ("angle", "right_angle"):
                is_rt = self.tool == "right_angle"
                if not self._draft_pts:
                    # Point 1 (Apex / Corner / First Point)
                    self._draft_pts.append((snapped_wx, snapped_wy))
                    self.statusMessage.emit("Point 1 set! Now click inside the triangle or a second point to place the angle.")
                    self.update()
                else:
                    # Point 2 (Finished! Exactly 2 clicks!)
                    p1 = self._draft_pts[0]
                    p2 = (snapped_wx, snapped_wy)
                    self._draft_pts.clear()
                    new_ang = self._create_angle_from_two_points(p1, p2, is_right=is_rt)
                    self._finish_shape_creation(
                        new_ang, f"Angle symbol ({new_ang.name}) placed at ({new_ang.coords[0]:.1f}, {new_ang.coords[1]:.1f})! Drag to move anywhere."
                    )

            elif self.tool == "text":
                text_val, ok = QInputDialog.getText(
                    self, "New Math Label", "Enter formula or text annotation (e.g. a² + b² = c²):",
                    QLineEdit.Normal, "a² + b² = c²"
                )
                chosen_text = text_val.strip() if (ok and text_val.strip()) else "Formula"
                new_text = BuilderShape(
                    shape_type=ShapeType.TEXT.value,
                    name=chosen_text,
                    text=chosen_text,
                    color="#5EEAD4",
                    coords=[snapped_wx, snapped_wy],
                    font_size=13,
                    bold=True
                )
                self._finish_shape_creation(new_text, f"Label '{chosen_text}' placed! Drag to move anywhere.")

    def mouseDoubleClickEvent(self, event):
        pos = event.pos()
        wx, wy = self.screen_to_world(pos.x(), pos.y())
        snapped_wx, snapped_wy = self._snap(wx, wy)

        if self.tool == "select" and self._step:
            hit_shape = self._hit_test_any_shape(pos.x(), pos.y())
            if hit_shape and hit_shape.shape_type == ShapeType.TEXT.value:
                curr_txt = hit_shape.text or hit_shape.name
                new_txt, ok = QInputDialog.getText(
                    self, "Edit Math Label", "Formula / Text Annotation:",
                    QLineEdit.Normal, curr_txt
                )
                if ok and new_txt.strip():
                    hit_shape.text = new_txt.strip()
                    hit_shape.name = hit_shape.text
                    self.stepModified.emit()
                    self.update()
                    self.statusMessage.emit(f"Updated text: '{hit_shape.text}'")
                    return
            # Double-clicking inside a divided circle or polygon isolates that portion!
            portion = self._detect_shape_portion(snapped_wx, snapped_wy)
            if portion:
                self._finish_shape_creation(portion, f"Divided portion '{portion.name}' isolated! Drag anywhere to move it.")
                return

        if self.tool in ("angle", "right_angle") and self._step:
            is_rt = self.tool == "right_angle"
            self._draft_pts.clear()
            new_ang = self._create_angle_from_two_points(
                (snapped_wx, snapped_wy), (snapped_wx, snapped_wy), is_right=is_rt
            )
            self._finish_shape_creation(new_ang, f"Angle symbol ({new_ang.name}) placed at corner!")
            return

        if self.tool == "polygon" and len(self._draft_pts) >= 3 and self._step:
            pts = list(self._draft_pts)
            self._draft_pts.clear()
            new_poly = BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="Poly",
                color="#2F9E78",
                fill_color="rgba(47, 158, 120, 0.22)",
                stroke_width=2.2,
                polygon_points=pts
            )
            self._finish_shape_creation(new_poly, "Polygon closed! Drag to move anywhere.")

    def mouseMoveEvent(self, event):
        pos = event.pos()
        wx, wy = self.screen_to_world(pos.x(), pos.y())
        snapped_wx, snapped_wy = self._snap(wx, wy)
        self._hover_world = (snapped_wx, snapped_wy)
        self.cursorCoordChanged.emit(snapped_wx, snapped_wy)

        if self._panning:
            dx = pos.x() - self._last_mouse_pos.x()
            dy = pos.y() - self._last_mouse_pos.y()
            self._pan[0] += dx
            self._pan[1] += dy
            self._last_mouse_pos = pos
            self.update()
            return

        # 1. Whole-Shape Dragging Mode (translates entire shape)
        if self._drag_mode == "shape" and self._dragged_shape is not None and self._last_drag_world is not None:
            dx = snapped_wx - self._last_drag_world[0]
            dy = snapped_wy - self._last_drag_world[1]
            if abs(dx) > 1e-5 or abs(dy) > 1e-5:
                self._dragged_shape.translate(dx, dy)
                self._last_drag_world = (snapped_wx, snapped_wy)
                self.stepModified.emit()
                self.update()
            return

        # 2. Vertex Dragging Mode (reshapes individual vertex)
        if self._drag_mode == "vertex" and self._dragged_shape is not None and self._step:
            shape = self._dragged_shape
            st = shape.shape_type

            if st == ShapeType.POINT.value and len(shape.coords) >= 2:
                shape.coords[0] = snapped_wx
                shape.coords[1] = snapped_wy
            elif st == ShapeType.LINE.value and len(shape.coords) >= 4 and self._dragged_point_idx is not None:
                if self._dragged_point_idx == 0:
                    shape.coords[0] = snapped_wx
                    shape.coords[1] = snapped_wy
                else:
                    shape.coords[2] = snapped_wx
                    shape.coords[3] = snapped_wy
            elif st == ShapeType.POLYGON.value and self._dragged_point_idx is not None:
                idx = self._dragged_point_idx
                if 0 <= idx < len(shape.polygon_points):
                    shape.polygon_points[idx] = (snapped_wx, snapped_wy)
            elif st in (ShapeType.ANGLE.value, ShapeType.CIRCLE.value, ShapeType.TEXT.value):
                if len(shape.coords) >= 2:
                    shape.coords[0] = snapped_wx
                    shape.coords[1] = snapped_wy
            elif st == ShapeType.CURVE.value and len(shape.coords) >= 6 and self._dragged_point_idx is not None:
                if self._dragged_point_idx == 0:
                    shape.coords[0] = snapped_wx
                    shape.coords[1] = snapped_wy
                elif self._dragged_point_idx == 1:
                    shape.coords[2] = snapped_wx
                    shape.coords[3] = snapped_wy
                elif self._dragged_point_idx == 2:
                    shape.coords[4] = snapped_wx
                    shape.coords[5] = snapped_wy
            elif st == ShapeType.SECTOR.value and len(shape.coords) >= 5 and self._dragged_point_idx is not None:
                cx, cy = shape.coords[0], shape.coords[1]
                if self._dragged_point_idx == 0:
                    shape.coords[0] = snapped_wx
                    shape.coords[1] = snapped_wy
                elif self._dragged_point_idx == 1:
                    ang = math.degrees(math.atan2(snapped_wy - cy, snapped_wx - cx)) % 360.0
                    shape.coords[3] = round(ang, 1)
                elif self._dragged_point_idx == 2:
                    ang = math.degrees(math.atan2(snapped_wy - cy, snapped_wx - cx)) % 360.0
                    span = (ang - shape.coords[3]) % 360.0
                    shape.coords[4] = round(span if span > 0.5 else 360.0, 1)

            self.stepModified.emit()
            self.update()
            return

        # 3. Dynamic Cursor Hover Feedback
        if self.tool == "pan" or self._space_held:
            if not self._panning:
                self.setCursor(Qt.OpenHandCursor)
        elif self.tool == "select":
            hit_pt = self._hit_test_point(pos.x(), pos.y())
            if hit_pt is not None:
                self.setCursor(Qt.CrossCursor)
            else:
                hit_shape = self._hit_test_any_shape(pos.x(), pos.y())
                if hit_shape is not None:
                    self.setCursor(Qt.SizeAllCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.RightButton, Qt.MiddleButton, Qt.LeftButton):
            if self._panning:
                self._panning = False
                if self.tool == "pan" or self._space_held:
                    self.setCursor(Qt.OpenHandCursor)
                elif self.tool == "select":
                    hit_shape = self._hit_test_any_shape(event.pos().x(), event.pos().y())
                    self.setCursor(Qt.SizeAllCursor if hit_shape else Qt.ArrowCursor)
                else:
                    self.setCursor(Qt.CrossCursor)

        if event.button() == Qt.LeftButton:
            self._drag_mode = None
            self._dragged_shape = None
            self._dragged_point_idx = None
            self._last_drag_world = None
            if self.tool == "select" and not self._panning:
                hit_shape = self._hit_test_any_shape(event.pos().x(), event.pos().y())
                self.setCursor(Qt.SizeAllCursor if hit_shape else Qt.ArrowCursor)
        self.update()

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        delta_y = event.angleDelta().y()
        delta_x = event.angleDelta().x()

        if modifiers & Qt.ShiftModifier:
            # Shift + wheel: horizontal pan
            self.pan_by(delta_y * 0.8 if delta_y != 0 else delta_x * 0.8, 0.0)
        elif modifiers & Qt.AltModifier:
            # Alt + wheel: vertical pan
            self.pan_by(0.0, delta_y * 0.8)
        elif delta_x != 0 and delta_y != 0 and not (modifiers & Qt.ControlModifier):
            # Touchpad 2D pan
            self.pan_by(delta_x * 0.7, delta_y * 0.7)
        else:
            # Mouse wheel or Ctrl+wheel: Smooth zoom focused directly at mouse cursor!
            factor = 1.15 if delta_y > 0 else (1.0 / 1.15)
            self.zoom_at(factor, event.pos())

    def keyPressEvent(self, event):
        # Spacebar for quick hand-pan mode
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._space_held = True
            self.setCursor(Qt.OpenHandCursor)
            return

        # Plus / Minus for zoom
        if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_by(1.2)
            return
        elif event.key() in (Qt.Key_Minus, Qt.Key_Underscore):
            self.zoom_by(1.0 / 1.2)
            return
        elif event.key() in (Qt.Key_Home, Qt.Key_0):
            self.reset_view()
            return
        elif event.key() == Qt.Key_F:
            self.fit_to_content()
            return

        # Arrow Keys:
        # If a shape is selected and not holding Ctrl: Nudge the shape
        # Otherwise (or with Ctrl): Pan the canvas Up, Down, Left, Right!
        selected = self.selected_shape()
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            if selected is not None and not (event.modifiers() & Qt.ControlModifier):
                step = 0.1 if (event.modifiers() & Qt.ShiftModifier) else self.grid_size
                dx, dy = 0.0, 0.0
                if event.key() == Qt.Key_Left:
                    dx = -step
                elif event.key() == Qt.Key_Right:
                    dx = step
                elif event.key() == Qt.Key_Up:
                    dy = step
                elif event.key() == Qt.Key_Down:
                    dy = -step
                selected.translate(dx, dy)
                self.stepModified.emit()
                self.update()
                return
            else:
                # Pan canvas with arrow keys!
                pan_step = 60.0
                if event.key() == Qt.Key_Left:
                    self.pan_by(pan_step, 0.0)
                elif event.key() == Qt.Key_Right:
                    self.pan_by(-pan_step, 0.0)
                elif event.key() == Qt.Key_Up:
                    self.pan_by(0.0, pan_step)
                elif event.key() == Qt.Key_Down:
                    self.pan_by(0.0, -pan_step)
                return

        if event.key() == Qt.Key_Escape:
            self._draft_pts.clear()
            self.set_tool("select")
            self.toolChanged.emit("select")
            self.update()
            return

        # Delete / Backspace: Remove selected shape
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            selected = self.selected_shape()
            if selected and self._step:
                self._step.shapes = [s for s in self._step.shapes if s.id != selected.id]
                self.set_selected_shape_id(None)
                self.stepModified.emit()
                self.update()
                self.statusMessage.emit("Shape deleted.")
                return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and self.tool == "polygon" and len(self._draft_pts) >= 3:
            pts = list(self._draft_pts)
            self._draft_pts.clear()
            new_poly = BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="Poly",
                color="#2F9E78",
                fill_color="rgba(47, 158, 120, 0.22)",
                stroke_width=2.2,
                polygon_points=pts
            )
            self._finish_shape_creation(new_poly, "Polygon closed! Drag to move anywhere.")
            return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._space_held = False
            if self.tool == "pan":
                self.setCursor(Qt.OpenHandCursor)
            elif self.tool == "select":
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)
            return
        super().keyReleaseEvent(event)

    # ------------------------------------------------------------------
    # Hit Testing
    # ------------------------------------------------------------------
    def _hit_test_point(self, sx: float, sy: float) -> Optional[Tuple[BuilderShape, int]]:
        """Returns (BuilderShape, vertex_index) if clicking near any vertex or point."""
        if not self._step:
            return None
        threshold = 12.0

        for s in reversed(self._step.shapes):
            if s.shape_type == ShapeType.POINT.value and len(s.coords) >= 2:
                psx, psy = self.world_to_screen(s.coords[0], s.coords[1])
                if math.hypot(sx - psx, sy - psy) <= threshold:
                    return s, 0

            elif s.shape_type == ShapeType.LINE.value and len(s.coords) >= 4:
                p1x, p1y = self.world_to_screen(s.coords[0], s.coords[1])
                p2x, p2y = self.world_to_screen(s.coords[2], s.coords[3])
                if math.hypot(sx - p1x, sy - p1y) <= threshold:
                    return s, 0
                if math.hypot(sx - p2x, sy - p2y) <= threshold:
                    return s, 1

            elif s.shape_type == ShapeType.POLYGON.value:
                for idx, (px, py) in enumerate(s.polygon_points):
                    psx, psy = self.world_to_screen(px, py)
                    if math.hypot(sx - psx, sy - psy) <= threshold:
                        return s, idx

            elif s.shape_type in (ShapeType.ANGLE.value, ShapeType.CIRCLE.value, ShapeType.TEXT.value):
                if len(s.coords) >= 2:
                    psx, psy = self.world_to_screen(s.coords[0], s.coords[1])
                    if math.hypot(sx - psx, sy - psy) <= threshold:
                        return s, 0

            elif s.shape_type == ShapeType.CURVE.value and len(s.coords) >= 6:
                for idx, (vx, vy) in enumerate([
                    (s.coords[0], s.coords[1]),
                    (s.coords[2], s.coords[3]),
                    (s.coords[4], s.coords[5]),
                ]):
                    psx, psy = self.world_to_screen(vx, vy)
                    if math.hypot(sx - psx, sy - psy) <= threshold:
                        return s, idx

            elif s.shape_type == ShapeType.SECTOR.value and len(s.coords) >= 5:
                cx, cy, r, s_deg, sp_deg = s.coords[:5]
                psx, psy = self.world_to_screen(cx, cy)
                if math.hypot(sx - psx, sy - psy) <= threshold:
                    return s, 0
                a1 = math.radians(s_deg)
                p1x, p1y = self.world_to_screen(cx + r * math.cos(a1), cy + r * math.sin(a1))
                if math.hypot(sx - p1x, sy - p1y) <= threshold:
                    return s, 1
                a2 = math.radians(s_deg + sp_deg)
                p2x, p2y = self.world_to_screen(cx + r * math.cos(a2), cy + r * math.sin(a2))
                if math.hypot(sx - p2x, sy - p2y) <= threshold:
                    return s, 2

        return None

    def _dist_to_segment(self, px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        l2 = (x2 - x1)**2 + (y2 - y1)**2
        if l2 == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y)

    def _hit_test_any_shape(self, sx: float, sy: float) -> Optional[BuilderShape]:
        """Returns the shape if clicking inside a polygon, on an edge, on a line, in a circle, or near any shape."""
        if not self._step:
            return None

        for s in reversed(self._step.shapes):
            st = s.shape_type

            if st == ShapeType.POLYGON.value and s.polygon_points:
                screen_pts = [QPointF(*self.world_to_screen(px, py)) for px, py in s.polygon_points]
                qpoly = QPolygonF(screen_pts)
                # 1. Inside polygon fill
                if qpoly.containsPoint(QPointF(sx, sy), Qt.OddEvenFill):
                    return s
                # 2. Near any edge of the polygon
                for i in range(len(screen_pts)):
                    p1 = screen_pts[i]
                    p2 = screen_pts[(i + 1) % len(screen_pts)]
                    if self._dist_to_segment(sx, sy, p1.x(), p1.y(), p2.x(), p2.y()) <= 12.0:
                        return s

            elif st == ShapeType.LINE.value and len(s.coords) >= 4:
                p1x, p1y = self.world_to_screen(s.coords[0], s.coords[1])
                p2x, p2y = self.world_to_screen(s.coords[2], s.coords[3])
                if self._dist_to_segment(sx, sy, p1x, p1y, p2x, p2y) <= 12.0:
                    return s

            elif st == ShapeType.CIRCLE.value and len(s.coords) >= 3:
                cx, cy = self.world_to_screen(s.coords[0], s.coords[1])
                r_screen = s.coords[2] * self._scale()
                dist = math.hypot(sx - cx, sy - cy)
                if dist <= r_screen + 12.0:
                    return s

            elif st == ShapeType.ANGLE.value and len(s.coords) >= 3:
                asx, asy = self.world_to_screen(s.coords[0], s.coords[1])
                r_screen = s.coords[2] * self._scale()
                dist = math.hypot(sx - asx, sy - asy)
                if dist <= max(24.0, r_screen + 14.0):
                    return s

            elif st == ShapeType.TEXT.value and len(s.coords) >= 2:
                tx, ty = self.world_to_screen(s.coords[0], s.coords[1])
                if abs(sx - tx) <= 50.0 and abs(sy - ty) <= 24.0:
                    return s

            elif st == ShapeType.POINT.value and len(s.coords) >= 2:
                psx, psy = self.world_to_screen(s.coords[0], s.coords[1])
                if math.hypot(sx - psx, sy - psy) <= 16.0:
                    return s

            elif st == ShapeType.CURVE.value and len(s.coords) >= 6:
                x0, y0, cx, cy, x1, y1 = s.coords[:6]
                curve_pts = []
                for step_i in range(17):
                    t = step_i / 16.0
                    bx = (1 - t)**2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
                    by = (1 - t)**2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1
                    curve_pts.append(self.world_to_screen(bx, by))
                for k in range(len(curve_pts) - 1):
                    p1 = curve_pts[k]
                    p2 = curve_pts[k + 1]
                    if self._dist_to_segment(sx, sy, p1[0], p1[1], p2[0], p2[1]) <= 12.0:
                        return s

            elif st == ShapeType.SECTOR.value and len(s.coords) >= 5:
                cx, cy, r, s_deg, sp_deg = s.coords[:5]
                scx, scy = self.world_to_screen(cx, cy)
                r_screen = r * self._scale()
                dist = math.hypot(sx - scx, sy - scy)
                if dist <= r_screen + 10.0:
                    wx, wy = self.screen_to_world(sx, sy)
                    ang = math.degrees(math.atan2(wy - cy, wx - cx)) % 360.0
                    rel_ang = (ang - s_deg) % 360.0
                    if rel_ang <= sp_deg:
                        return s

        return None

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        w, h = float(self.width()), float(self.height())
        canvas_rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)

        # Dark blueprint background matching Studio aesthetic
        p.setPen(QPen(QColor("#1F2A38"), 1.0))
        p.setBrush(QBrush(QColor("#0B0E14")))
        p.drawRoundedRect(canvas_rect, 12.0, 12.0)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(canvas_rect.adjusted(1, 1, -1, -1), 11.0, 11.0)
        p.setClipPath(clip_path)

        # 1. Subtle drafting grid & axes
        self._paint_grid(p, w, h)

        # 2. Render all step shapes
        if self._step:
            self._paint_shapes(p)

        # 3. Render live draft geometry while creating
        self._paint_draft(p)

        p.end()

    def _paint_grid(self, p: QPainter, w: float, h: float):
        scale = self._scale()
        cx = w / 2.0 + self._pan[0]
        cy = h / 2.0 + self._pan[1]

        if self.snap_to_grid:
            gs = max(0.25, self.grid_size)
            grid_px = gs * scale

            step_mult = 1
            while grid_px * step_mult < 18.0:
                step_mult *= 2
            eff_grid_px = grid_px * step_mult

            # Minor grid lines / dots aligned to grid_size
            p.setPen(QPen(QColor(36, 50, 72, 75), 0.8, Qt.DotLine))
            x = cx % eff_grid_px
            while x < w:
                p.drawLine(QPointF(x, 0), QPointF(x, h))
                x += eff_grid_px
            y = cy % eff_grid_px
            while y < h:
                p.drawLine(QPointF(0, y), QPointF(w, y))
                y += eff_grid_px

            # Major grid lines at 1.0 or multiples
            major_px = max(eff_grid_px, 1.0 * scale)
            p.setPen(QPen(QColor(45, 65, 95, 110), 0.9))
            x = cx % major_px
            while x < w:
                p.drawLine(QPointF(x, 0), QPointF(x, h))
                x += major_px
            y = cy % major_px
            while y < h:
                p.drawLine(QPointF(0, y), QPointF(w, y))
                y += major_px
        else:
            # Faint guideline indication that Snap Grid is OFF
            p.setPen(QPen(QColor(25, 35, 50, 40), 0.6, Qt.DotLine))
            guide_px = 2.0 * scale
            x = cx % guide_px
            while x < w:
                p.drawLine(QPointF(x, 0), QPointF(x, h))
                x += guide_px
            y = cy % guide_px
            while y < h:
                p.drawLine(QPointF(0, y), QPointF(w, y))
                y += guide_px

        # Central coordinate axes
        axis_color = QColor(70, 95, 130, 180) if self.snap_to_grid else QColor(50, 70, 95, 120)
        p.setPen(QPen(axis_color, 1.5))
        p.drawLine(QPointF(0, cy), QPointF(w, cy))
        p.drawLine(QPointF(cx, 0), QPointF(cx, h))

        # Origin indicator
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#64748B")))
        p.drawEllipse(QPointF(cx, cy), 3.0, 3.0)

    def _paint_shapes(self, p: QPainter):
        if not self._step:
            return

        # Pass 1: Polygons
        for s in self._step.shapes:
            if s.shape_type == ShapeType.POLYGON.value and s.polygon_points:
                is_selected = s.id == self._selected_shape_id
                qpoly = QPolygonF([QPointF(*self.world_to_screen(x, y)) for x, y in s.polygon_points])

                fill = QColor(s.fill_color)
                stroke = QColor(s.color)
                if is_selected:
                    stroke = QColor("#5EEAD4")
                    fill.setAlpha(min(255, fill.alpha() + 45))

                p.setBrush(QBrush(fill))
                pen = QPen(stroke, s.stroke_width + (1.0 if is_selected else 0.0))
                p.setPen(pen)
                p.drawPolygon(qpoly)

                # Centroid label
                if s.name:
                    pts = s.polygon_points
                    ctx = sum(pt[0] for pt in pts) / len(pts)
                    cty = sum(pt[1] for pt in pts) / len(pts)
                    sx, sy = self.world_to_screen(ctx, cty)
                    self._paint_pill_label(p, sx, sy, s.name, stroke.name())

                if is_selected:
                    # Draw vertex grip handles
                    for px, py in s.polygon_points:
                        vx, vy = self.world_to_screen(px, py)
                        p.setBrush(QBrush(QColor("#FFFFFF")))
                        p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                        p.drawEllipse(QPointF(vx, vy), 4.5, 4.5)
                    # Draw centroid move grip badge
                    pts = s.polygon_points
                    ctx = sum(pt[0] for pt in pts) / len(pts)
                    cty = sum(pt[1] for pt in pts) / len(pts)
                    csx, csy = self.world_to_screen(ctx, cty)
                    p.setBrush(QBrush(QColor(16, 21, 32, 230)))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(csx, csy), 9.0, 9.0)
                    p.setPen(QPen(QColor("#5EEAD4"), 1.6, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(QPointF(csx - 5, csy), QPointF(csx + 5, csy))
                    p.drawLine(QPointF(csx, csy - 5), QPointF(csx, csy + 5))

        # Pass 2: Circles
        for s in self._step.shapes:
            if s.shape_type == ShapeType.CIRCLE.value and len(s.coords) >= 3:
                is_selected = s.id == self._selected_shape_id
                cx, cy, rad = s.coords[0], s.coords[1], s.coords[2]
                scx, scy = self.world_to_screen(cx, cy)
                srad = rad * self._scale()

                stroke = QColor("#5EEAD4" if is_selected else s.color)
                fill = QColor(s.fill_color)
                p.setBrush(QBrush(fill))
                p.setPen(QPen(stroke, s.stroke_width + (1.0 if is_selected else 0.0)))
                p.drawEllipse(QPointF(scx, scy), srad, srad)

                # Center dot
                p.setBrush(QBrush(stroke))
                p.drawEllipse(QPointF(scx, scy), 2.5, 2.5)

                if is_selected:
                    # Move grip at center
                    p.setBrush(QBrush(QColor(16, 21, 32, 230)))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(scx, scy), 8.0, 8.0)
                    p.setPen(QPen(QColor("#5EEAD4"), 1.5, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(QPointF(scx - 4, scy), QPointF(scx + 4, scy))
                    p.drawLine(QPointF(scx, scy - 4), QPointF(scx, scy + 4))

        # Pass 2b: Sectors / Divided Circle Slices
        for s in self._step.shapes:
            if s.shape_type == ShapeType.SECTOR.value and len(s.coords) >= 5:
                is_selected = s.id == self._selected_shape_id
                cx, cy, r, s_deg, sp_deg = s.coords[:5]
                scx, scy = self.world_to_screen(cx, cy)
                srad = r * self._scale()

                stroke = QColor("#5EEAD4" if is_selected else s.color)
                fill = QColor(s.fill_color)
                if is_selected:
                    fill.setAlpha(min(255, fill.alpha() + 45))

                rect = QRectF(scx - srad, scy - srad, 2 * srad, 2 * srad)
                p.setBrush(QBrush(fill))
                p.setPen(QPen(stroke, s.stroke_width + (1.0 if is_selected else 0.0)))
                p.drawPie(rect, int(s_deg * 16), int(sp_deg * 16))

                if s.name:
                    mid_rad = math.radians(s_deg + sp_deg / 2.0)
                    lx = scx + (srad * 0.62) * math.cos(mid_rad)
                    ly = scy - (srad * 0.62) * math.sin(mid_rad)
                    self._paint_pill_label(p, lx, ly, s.name, stroke.name())

                if is_selected:
                    # Center and arc endpoint grip handles
                    p.setBrush(QBrush(QColor("#FFFFFF")))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(scx, scy), 4.5, 4.5)
                    a1 = math.radians(s_deg)
                    a2 = math.radians(s_deg + sp_deg)
                    p.drawEllipse(QPointF(scx + srad * math.cos(a1), scy - srad * math.sin(a1)), 4.0, 4.0)
                    p.drawEllipse(QPointF(scx + srad * math.cos(a2), scy - srad * math.sin(a2)), 4.0, 4.0)

                    # Centroid move badge
                    mid_rad = math.radians(s_deg + sp_deg / 2.0)
                    csx = scx + (srad * 0.55) * math.cos(mid_rad)
                    csy = scy - (srad * 0.55) * math.sin(mid_rad)
                    p.setBrush(QBrush(QColor(16, 21, 32, 230)))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(csx, csy), 9.0, 9.0)
                    p.setPen(QPen(QColor("#5EEAD4"), 1.6, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(QPointF(csx - 5, csy), QPointF(csx + 5, csy))
                    p.drawLine(QPointF(csx, csy - 5), QPointF(csx, csy + 5))

        # Pass 3: Lines
        for s in self._step.shapes:
            if s.shape_type == ShapeType.LINE.value and len(s.coords) >= 4:
                is_selected = s.id == self._selected_shape_id
                x1, y1, x2, y2 = s.coords[0], s.coords[1], s.coords[2], s.coords[3]
                sx1, sy1 = self.world_to_screen(x1, y1)
                sx2, sy2 = self.world_to_screen(x2, y2)

                stroke = QColor("#5EEAD4" if is_selected else s.color)
                pen = QPen(stroke, s.stroke_width + (1.0 if is_selected else 0.0))
                if s.dashed:
                    pen.setStyle(Qt.DashLine)
                p.setPen(pen)
                p.drawLine(QPointF(sx1, sy1), QPointF(sx2, sy2))

                if s.name:
                    mx, my = (sx1 + sx2) * 0.5, (sy1 + sy2) * 0.5
                    self._paint_pill_label(p, mx, my - 12, s.name, stroke.name())

                if is_selected:
                    # Endpoint grip handles
                    for vx, vy in ((sx1, sy1), (sx2, sy2)):
                        p.setBrush(QBrush(QColor("#FFFFFF")))
                        p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                        p.drawEllipse(QPointF(vx, vy), 4.5, 4.5)
                    # Midpoint move grip
                    mx, my = (sx1 + sx2) * 0.5, (sy1 + sy2) * 0.5
                    p.setBrush(QBrush(QColor(16, 21, 32, 230)))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(mx, my), 8.0, 8.0)
                    p.setPen(QPen(QColor("#5EEAD4"), 1.5, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(QPointF(mx - 4, my), QPointF(mx + 4, my))
                    p.drawLine(QPointF(mx, my - 4), QPointF(mx, my + 4))

        # Pass 3b: Curves (Quadratic Bézier)
        for s in self._step.shapes:
            if s.shape_type == ShapeType.CURVE.value and len(s.coords) >= 6:
                is_selected = s.id == self._selected_shape_id
                x0, y0, cx, cy, x1, y1 = s.coords[:6]
                sx0, sy0 = self.world_to_screen(x0, y0)
                scx, scy = self.world_to_screen(cx, cy)
                sx1, sy1 = self.world_to_screen(x1, y1)

                stroke = QColor("#5EEAD4" if is_selected else s.color)
                pen = QPen(stroke, s.stroke_width + (1.0 if is_selected else 0.0))
                if s.dashed:
                    pen.setStyle(Qt.DashLine)

                path = QPainterPath()
                path.moveTo(sx0, sy0)
                path.quadTo(scx, scy, sx1, sy1)
                p.setBrush(Qt.NoBrush)
                p.setPen(pen)
                p.drawPath(path)

                if s.name:
                    mid_bx = 0.25 * x0 + 0.5 * cx + 0.25 * x1
                    mid_by = 0.25 * y0 + 0.5 * cy + 0.25 * y1
                    smx, smy = self.world_to_screen(mid_bx, mid_by)
                    self._paint_pill_label(p, smx, smy - 12, s.name, stroke.name())

                if is_selected:
                    # Dotted tangent control polygon
                    p.setPen(QPen(QColor(94, 234, 212, 100), 1.0, Qt.DotLine))
                    p.drawLine(QPointF(sx0, sy0), QPointF(scx, scy))
                    p.drawLine(QPointF(scx, scy), QPointF(sx1, sy1))

                    # Endpoint grips
                    for vx, vy in ((sx0, sy0), (sx1, sy1)):
                        p.setBrush(QBrush(QColor("#FFFFFF")))
                        p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                        p.drawEllipse(QPointF(vx, vy), 4.5, 4.5)

                    # Control peak handle (diamond)
                    p.setBrush(QBrush(QColor("#5EEAD4")))
                    p.setPen(QPen(QColor("#0B0E14"), 1.5))
                    poly_d = QPolygonF([
                        QPointF(scx, scy - 5.5), QPointF(scx + 5.5, scy),
                        QPointF(scx, scy + 5.5), QPointF(scx - 5.5, scy)
                    ])
                    p.drawPolygon(poly_d)

                    # Move badge at curve center
                    mcx, mcy = (x0 + cx + x1) / 3.0, (y0 + cy + y1) / 3.0
                    cmx, cmy = self.world_to_screen(mcx, mcy)
                    p.setBrush(QBrush(QColor(16, 21, 32, 230)))
                    p.setPen(QPen(QColor("#5EEAD4"), 1.8))
                    p.drawEllipse(QPointF(cmx, cmy), 8.0, 8.0)
                    p.setPen(QPen(QColor("#5EEAD4"), 1.5, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(QPointF(cmx - 4, cmy), QPointF(cmx + 4, cmy))
                    p.drawLine(QPointF(cmx, cmy - 4), QPointF(cmx, cmy + 4))

        # Pass 4: Angles / Arcs
        for s in self._step.shapes:
            if s.shape_type == ShapeType.ANGLE.value and len(s.coords) >= 3:
                is_selected = s.id == self._selected_shape_id
                cx, cy, r = s.coords[0], s.coords[1], s.coords[2]
                start_deg = s.coords[3] if len(s.coords) > 3 else 0.0
                span_deg = s.coords[4] if len(s.coords) > 4 else 90.0
                asx, asy = self.world_to_screen(cx, cy)
                r_screen = r * self._scale()

                stroke = QColor("#5EEAD4" if is_selected else s.color)

                if s.is_right_angle:
                    sq_sz = r_screen * 0.75
                    ang1 = math.radians(start_deg)
                    ang2 = math.radians(start_deg + span_deg)
                    u1 = (math.cos(ang1) * sq_sz, -math.sin(ang1) * sq_sz)
                    u2 = (math.cos(ang2) * sq_sz, -math.sin(ang2) * sq_sz)
                    corner = (asx + u1[0] + u2[0], asy + u1[1] + u2[1])

                    p.setPen(QPen(stroke, 2.0))
                    p.drawLine(QPointF(asx + u1[0], asy + u1[1]), QPointF(corner[0], corner[1]))
                    p.drawLine(QPointF(asx + u2[0], asy + u2[1]), QPointF(corner[0], corner[1]))
                    if s.name:
                        self._paint_pill_label(p, corner[0] + 8, corner[1] - 8, s.name, stroke.name())
                else:
                    rect = QRectF(asx - r_screen, asy - r_screen, 2 * r_screen, 2 * r_screen)
                    p.setPen(QPen(stroke, 2.0))
                    fill = QColor(stroke)
                    fill.setAlpha(45)
                    p.setBrush(QBrush(fill))
                    p.drawPie(rect, int(start_deg * 16), int(span_deg * 16))

                    if s.name:
                        mid_ang = math.radians(start_deg + span_deg / 2.0)
                        lx = asx + (r_screen + 14) * math.cos(mid_ang)
                        ly = asy - (r_screen + 14) * math.sin(mid_ang)
                        self._paint_pill_label(p, lx, ly, s.name, stroke.name())

        # Pass 5: Points
        for s in self._step.shapes:
            if s.shape_type == ShapeType.POINT.value and len(s.coords) >= 2:
                is_selected = s.id == self._selected_shape_id
                px, py = s.coords[0], s.coords[1]
                psx, psy = self.world_to_screen(px, py)
                rad = s.coords[2] if len(s.coords) > 2 else 4.5

                if is_selected:
                    # Pulsing glow halo around selected point
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(QColor(94, 234, 212, 60)))
                    p.drawEllipse(QPointF(psx, psy), rad + 6.0, rad + 6.0)

                color = QColor("#5EEAD4" if is_selected else s.color)
                p.setBrush(QBrush(color))
                p.setPen(QPen(QColor("#0B0E14"), 1.8))
                p.drawEllipse(QPointF(psx, psy), rad, rad)

                if s.name:
                    self._paint_pill_label(p, psx + 10, psy - 10, s.name, color.name())

        # Pass 6: Math Text Annotations
        for s in self._step.shapes:
            if s.shape_type == ShapeType.TEXT.value and len(s.coords) >= 2:
                is_selected = s.id == self._selected_shape_id
                tx, ty = s.coords[0], s.coords[1]
                stx, sty = self.world_to_screen(tx, ty)
                text_content = s.text or s.name
                self._paint_banner_label(p, stx, sty, text_content, "#5EEAD4" if is_selected else s.color, s.font_size, s.bold)

    def _paint_draft(self, p: QPainter):
        """Paints rubberband draft geometry while a shape is being drawn."""
        if not self._draft_pts and not self._hover_world:
            return

        p.save()
        cursor_world = self._hover_world
        if cursor_world is None:
            p.restore()
            return

        csx, csy = self.world_to_screen(cursor_world[0], cursor_world[1])

        # Active crosshair dot at snapped cursor
        p.setPen(QPen(QColor("#5EEAD4"), 1.0, Qt.DotLine))
        p.drawLine(QPointF(csx - 12, csy), QPointF(csx + 12, csy))
        p.drawLine(QPointF(csx, csy - 12), QPointF(csx, csy + 12))
        p.setBrush(QBrush(QColor("#5EEAD4")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(csx, csy), 3.0, 3.0)
        if self.snap_to_grid:
            p.setPen(QPen(QColor(94, 234, 212, 160), 1.0))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(csx, csy), 6.0, 6.0)

        if self.tool == "line" and len(self._draft_pts) == 1:
            p1 = self._draft_pts[0]
            sx1, sy1 = self.world_to_screen(p1[0], p1[1])
            p.setPen(QPen(QColor("#5EEAD4"), 2.0, Qt.DashLine))
            p.drawLine(QPointF(sx1, sy1), QPointF(csx, csy))

        elif self.tool == "curve":
            if len(self._draft_pts) == 1:
                p0 = self._draft_pts[0]
                sx0, sy0 = self.world_to_screen(p0[0], p0[1])
                p.setPen(QPen(QColor("#5EEAD4"), 1.8, Qt.DashLine))
                p.drawLine(QPointF(sx0, sy0), QPointF(csx, csy))
            elif len(self._draft_pts) == 2:
                p0 = self._draft_pts[0]
                pc = self._draft_pts[1]
                sx0, sy0 = self.world_to_screen(p0[0], p0[1])
                scx, scy = self.world_to_screen(pc[0], pc[1])
                p.setPen(QPen(QColor(94, 234, 212, 120), 1.0, Qt.DotLine))
                p.drawLine(QPointF(sx0, sy0), QPointF(scx, scy))
                p.drawLine(QPointF(scx, scy), QPointF(csx, csy))
                path = QPainterPath()
                path.moveTo(sx0, sy0)
                path.quadTo(scx, scy, csx, csy)
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(QColor("#5EEAD4"), 2.0, Qt.DashLine))
                p.drawPath(path)

        elif self.tool == "slice":
            portion = self._detect_shape_portion(cursor_world[0], cursor_world[1])
            if portion:
                p.setPen(QPen(QColor("#5EEAD4"), 2.0, Qt.DashLine))
                p.setBrush(QBrush(QColor(94, 234, 212, 50)))
                if portion.shape_type == ShapeType.SECTOR.value and len(portion.coords) >= 5:
                    cx, cy, r, s_deg, sp_deg = portion.coords[:5]
                    scx, scy = self.world_to_screen(cx, cy)
                    srad = r * self._scale()
                    rect = QRectF(scx - srad, scy - srad, 2 * srad, 2 * srad)
                    p.drawPie(rect, int(s_deg * 16), int(sp_deg * 16))
                elif portion.shape_type == ShapeType.POLYGON.value and portion.polygon_points:
                    s_pts = [QPointF(*self.world_to_screen(x, y)) for x, y in portion.polygon_points]
                    p.drawPolygon(QPolygonF(s_pts))
                self._paint_pill_label(p, csx + 14, csy - 14, f"Slice: {portion.name}", "#5EEAD4")

        elif self.tool in ("triangle", "polygon") and self._draft_pts:
            screen_pts = [QPointF(*self.world_to_screen(x, y)) for x, y in self._draft_pts]
            screen_pts.append(QPointF(csx, csy))
            p.setPen(QPen(QColor("#5EEAD4"), 1.8, Qt.DashLine))
            p.setBrush(QBrush(QColor(94, 234, 212, 35)))
            p.drawPolygon(QPolygonF(screen_pts))

        elif self.tool == "rectangle" and len(self._draft_pts) == 1:
            x0, y0 = self._draft_pts[0]
            sx0, sy0 = self.world_to_screen(x0, y0)
            rect = QRectF(QPointF(sx0, sy0), QPointF(csx, csy)).normalized()
            p.setPen(QPen(QColor("#5EEAD4"), 1.8, Qt.DashLine))
            p.setBrush(QBrush(QColor(94, 234, 212, 35)))
            p.drawRect(rect)

        elif self.tool == "circle" and len(self._draft_pts) == 1:
            cx, cy = self._draft_pts[0]
            scx, scy = self.world_to_screen(cx, cy)
            r_screen = math.hypot(csx - scx, csy - scy)
            p.setPen(QPen(QColor("#5EEAD4"), 1.8, Qt.DashLine))
            p.setBrush(QBrush(QColor(94, 234, 212, 25)))
            p.drawEllipse(QPointF(scx, scy), r_screen, r_screen)
            p.drawLine(QPointF(scx, scy), QPointF(csx, csy))

        elif self.tool in ("angle", "right_angle") and len(self._draft_pts) == 1:
            p1 = self._draft_pts[0]
            p2 = cursor_world
            preview_ang = self._create_angle_from_two_points(p1, p2, is_right=self.tool == "right_angle")
            if preview_ang and len(preview_ang.coords) >= 5:
                cx, cy, r = preview_ang.coords[0], preview_ang.coords[1], preview_ang.coords[2]
                start_deg = preview_ang.coords[3]
                span_deg = preview_ang.coords[4]
                asx, asy = self.world_to_screen(cx, cy)
                r_screen = r * self._scale()

                stroke = QColor("#D8A94E" if preview_ang.is_right_angle else "#5EEAD4")
                if preview_ang.is_right_angle:
                    sq_sz = r_screen * 0.75
                    ang1 = math.radians(start_deg)
                    ang2 = math.radians(start_deg + span_deg)
                    u1 = (math.cos(ang1) * sq_sz, -math.sin(ang1) * sq_sz)
                    u2 = (math.cos(ang2) * sq_sz, -math.sin(ang2) * sq_sz)
                    corner = (asx + u1[0] + u2[0], asy + u1[1] + u2[1])
                    p.setPen(QPen(stroke, 2.0, Qt.DashLine))
                    p.drawLine(QPointF(asx + u1[0], asy + u1[1]), QPointF(corner[0], corner[1]))
                    p.drawLine(QPointF(asx + u2[0], asy + u2[1]), QPointF(corner[0], corner[1]))
                else:
                    rect = QRectF(asx - r_screen, asy - r_screen, 2 * r_screen, 2 * r_screen)
                    p.setPen(QPen(stroke, 2.0, Qt.DashLine))
                    fill = QColor(stroke)
                    fill.setAlpha(45)
                    p.setBrush(QBrush(fill))
                    p.drawPie(rect, int(start_deg * 16), int(span_deg * 16))

                # Guide line to cursor
                csx, csy = self.world_to_screen(cursor_world[0], cursor_world[1])
                p.setPen(QPen(QColor(94, 234, 212, 130), 1.0, Qt.DotLine))
                p.drawLine(QPointF(asx, asy), QPointF(csx, csy))
                self._paint_pill_label(p, csx + 10, csy - 10, f"Angle: {preview_ang.name}", stroke.name())

        p.restore()

    def _paint_pill_label(self, p: QPainter, sx: float, sy: float, text: str, border_color: str):
        if not text:
            return
        p.save()
        font = get_mono_font(11, weight=600)
        p.setFont(font)
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text)
        th = fm.height()

        pad_x, pad_y = 6.0, 3.0
        rect = QRectF(sx - tw / 2.0 - pad_x, sy - th / 2.0 - pad_y, tw + 2 * pad_x, th + 2 * pad_y)

        p.setBrush(QBrush(QColor(16, 21, 32, 220)))
        p.setPen(QPen(QColor(border_color), 1.0))
        p.drawRoundedRect(rect, 6.0, 6.0)

        p.setPen(QPen(QColor("#F8FAFC")))
        p.drawText(rect, Qt.AlignCenter, text)
        p.restore()

    def _paint_banner_label(self, p: QPainter, sx: float, sy: float, text: str, color_hex: str, font_size: int = 12, bold: bool = False):
        if not text:
            return
        p.save()
        font = get_mono_font(font_size, weight=700 if bold else 500)
        p.setFont(font)
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text)
        th = fm.height()

        pad_x, pad_y = 8.0, 4.0
        rect = QRectF(sx - pad_x, sy - th + pad_y, tw + 2 * pad_x, th + 2 * pad_y)

        p.setBrush(QBrush(QColor(12, 16, 26, 220)))
        p.setPen(QPen(QColor(color_hex), 1.2))
        p.drawRoundedRect(rect, 8.0, 8.0)

        p.setPen(QPen(QColor("#F8FAFC")))
        p.drawText(rect, Qt.AlignCenter, text)
        p.restore()

