"""
graphics/sorting_renderer.py
----------------------------
Modular rendering engine for the ProofMotion Animated Sorting Playground.

Each visual style has its own kinematics in graphics.sorting_motion:
  1. Bouncing Balls — hop on parabolic arcs and squash on landing.
  2. Floating Cubes — lift, turn, slide, then settle.
  3. Marble Track — roll along the rail with visible rotation; never fly.
  4. Toy Cars — accelerate, change lanes to pass, and brake into place.
  5. Bars — grounded horizontal slides and height pulses.
"""

import math
from typing import List, Dict, Any, Optional, Tuple

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QRadialGradient, QLinearGradient, QPainterPath, QPolygonF
)

from resources.theme import COLORS, get_ui_font, get_mono_font
from algorithms.sorting.sorting_events import SortEvent, SortEventType
from graphics.sorting_motion import motion_for, MotionPose


class SortingPlaygroundRenderer:
    """Renders sorting steps across multiple visual themes with smooth arc interpolation."""

    STYLES = [
        ("balls", "Bouncing Balls"),
        ("cubes", "Floating Cubes"),
        ("marbles", "Marble Track"),
        ("cars", "Toy Cars"),
        ("bars", "Bars"),
    ]

    def __init__(self):
        self.style: str = "balls"          # "balls", "cubes", "marbles", "bars"
        self.reduced_motion: bool = False
        self.progress: float = 1.0         # 0.0 to 1.0 animation progress

    def render(self, painter: QPainter, width: int, height: int,
               bars: Optional[List[Dict[str, Any]]],
               sort_event: Optional[SortEvent] = None):
        """Main entry point called by VisualizationWidget."""
        if not bars and not (sort_event and sort_event.array):
            self._draw_empty_state(painter, width, height)
            return

        # Extract values
        if sort_event and sort_event.array:
            values = list(sort_event.array)
        else:
            values = [b.get("val", 0) for b in bars]

        n = len(values)
        if n == 0:
            self._draw_empty_state(painter, width, height)
            return

        # Delegate to active style
        t = 1.0 if self.reduced_motion else max(0.0, min(1.0, self.progress))

        if self.style == "cubes":
            self._render_floating_cubes(painter, width, height, values, bars, sort_event, t)
        elif self.style == "marbles":
            self._render_marble_machine(painter, width, height, values, bars, sort_event, t)
        elif self.style == "cars":
            self._render_toy_cars(painter, width, height, values, bars, sort_event, t)
        elif self.style == "bars":
            self._render_conventional_bars(painter, width, height, values, bars, sort_event, t)
        else:
            self._render_bouncing_balls(painter, width, height, values, bars, sort_event, t)

        if sort_event and sort_event.description:
            self._draw_event_caption(painter, width, height, sort_event)

    def _draw_empty_state(self, painter: QPainter, width: int, height: int):
        painter.save()
        painter.setPen(QPen(QColor(COLORS["text_muted"])))
        painter.setFont(get_ui_font(14, weight=400))
        painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, "No sorting data available.")
        painter.restore()

    # ------------------------------------------------------------------
    # Helper: Layout and Slot Geometry
    # ------------------------------------------------------------------
    def _compute_slots(self, width: int, height: int, n: int) -> Tuple[float, float, List[float], float]:
        """Calculates slot centers, item diameter/width, and baseline Y."""
        margin_x = 44.0
        avail_w = max(100.0, width - 2 * margin_x)
        slot_w = avail_w / max(1, n)
        item_size = min(max(26.0, slot_w * 0.72), 64.0)
        base_y = height * 0.54

        centers = [margin_x + (i + 0.5) * slot_w for i in range(n)]
        return slot_w, item_size, centers, base_y

    def _get_element_state(self, i: int, sort_event: Optional[SortEvent], bars: Optional[List[Dict[str, Any]]]):
        """Determines highlight status of element at index i."""
        is_swapping = False
        is_comparing = False
        is_min = False
        is_pivot = False
        is_sorted = False
        is_shifting = False
        is_key = False
        tag = ""

        if sort_event:
            ev_type = sort_event.event_type
            if sort_event.swapping_indices and i in sort_event.swapping_indices:
                is_swapping = True
            elif ev_type == SortEventType.SWAP and i in sort_event.indices:
                is_swapping = True

            if sort_event.comparing_indices and i in sort_event.comparing_indices:
                is_comparing = True
            elif ev_type in (SortEventType.COMPARE, SortEventType.MERGE_COMPARE) and i in sort_event.indices:
                is_comparing = True

            if sort_event.min_index == i:
                is_min = True
            if sort_event.pivot_index == i:
                is_pivot = True
            if sort_event.key_index == i:
                is_key = True
            if sort_event.moving_index == i or (ev_type == SortEventType.SHIFT and i in sort_event.indices):
                is_shifting = True
            if i in sort_event.sorted_indices:
                is_sorted = True
            if ev_type == SortEventType.COMPLETE:
                is_sorted = True
        elif bars and i < len(bars):
            tag = bars[i].get("tag", "").upper()
            if "SWAP" in tag:
                is_swapping = True
            elif "CMP" in tag or "SCAN" in tag:
                is_comparing = True
            elif "MIN" in tag:
                is_min = True
            elif "PIVOT" in tag:
                is_pivot = True
            elif "SORTED" in tag:
                is_sorted = True
            elif "SHIFT" in tag or "WRITE" in tag:
                is_shifting = True

        return {
            "swapping": is_swapping,
            "comparing": is_comparing,
            "min": is_min,
            "pivot": is_pivot,
            "sorted": is_sorted,
            "shifting": is_shifting,
            "key": is_key,
            "tag": tag
        }

    def _swap_pair(self, sort_event: Optional[SortEvent]) -> Optional[Tuple[int, int]]:
        if not sort_event:
            return None
        if sort_event.swapping_indices:
            return sort_event.swapping_indices
        if sort_event.event_type == SortEventType.SWAP and len(sort_event.indices) >= 2:
            return (sort_event.indices[0], sort_event.indices[1])
        return None

    def _pose(self, i: int, centers: List[float], base_y: float,
              sort_event: Optional[SortEvent], t: float, radius: float = 20.0) -> MotionPose:
        return motion_for(self.style).pose(
            i, centers, base_y, sort_event, t, self.reduced_motion, radius
        )

    def _draw_event_caption(self, painter: QPainter, width: int, height: int, sort_event: SortEvent):
        text = sort_event.description
        if not text:
            return
        painter.save()
        painter.setFont(get_ui_font(13, weight=500))
        fm = painter.fontMetrics()
        tw = min(width - 36.0, fm.horizontalAdvance(text) + 28)
        rect = QRectF((width - tw) / 2.0, height - 40.0, tw, 28)
        painter.setBrush(QBrush(QColor(255, 255, 255, 236)))
        painter.setPen(QPen(QColor("#DDD6FE"), 1.1))
        painter.drawRoundedRect(rect, 10, 10)
        painter.setPen(QPen(QColor("#4338CA")))
        painter.drawText(rect, Qt.AlignCenter, text)
        painter.restore()

    # ==================================================================
    # 1. Bouncing Balls Style
    # ==================================================================
    def _render_bouncing_balls(self, painter: QPainter, width: int, height: int,
                              values: List[int], bars: Optional[List[Dict[str, Any]]],
                              sort_event: Optional[SortEvent], t: float):
        n = len(values)
        slot_w, diam, centers, base_y = self._compute_slots(width, height, n)
        radius = diam / 2.0

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 1. Draw subtle base track / resting platform
        track_pen = QPen(QColor(COLORS["border"]), 2.0, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawLine(QPointF(centers[0] - slot_w * 0.4, base_y + radius + 12),
                         QPointF(centers[-1] + slot_w * 0.4, base_y + radius + 12))

        # Slot resting indents
        for cx in centers:
            painter.setPen(QPen(QColor(COLORS["border_focus"]), 1.2, Qt.DashLine))
            painter.drawLine(QPointF(cx - radius * 0.5, base_y + radius + 12),
                             QPointF(cx + radius * 0.5, base_y + radius + 12))

        # Detect active pair for animation
        swap_pair = None
        if sort_event and sort_event.swapping_indices:
            swap_pair = sort_event.swapping_indices
        elif sort_event and sort_event.event_type == SortEventType.SWAP and len(sort_event.indices) >= 2:
            swap_pair = (sort_event.indices[0], sort_event.indices[1])

        compare_pair = None
        if sort_event and sort_event.comparing_indices:
            compare_pair = sort_event.comparing_indices
        elif sort_event and sort_event.is_comparison() and len(sort_event.indices) >= 2:
            compare_pair = (sort_event.indices[0], sort_event.indices[1])

        # 2. Draw Comparison Indicator Arc / Halo
        if compare_pair and not self.reduced_motion:
            idx1, idx2 = compare_pair
            if 0 <= idx1 < n and 0 <= idx2 < n:
                x1, x2 = centers[idx1], centers[idx2]
                cmp_mid_x = (x1 + x2) / 2.0
                cmp_h = max(30.0, abs(x2 - x1) * 0.35)
                arc_path = QPainterPath()
                arc_path.moveTo(x1, base_y - radius - 8)
                arc_path.quadTo(cmp_mid_x, base_y - radius - 8 - cmp_h, x2, base_y - radius - 8)

                glow_pen = QPen(QColor(245, 158, 11, 160), 3.0, Qt.DashLine, Qt.RoundCap)
                painter.setPen(glow_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(arc_path)

                # Comparison Badge at crest of arc
                badge_w, badge_h = 56, 22
                badge_rect = QRectF(cmp_mid_x - badge_w / 2.0, base_y - radius - 8 - cmp_h - 14, badge_w, badge_h)
                painter.setPen(QPen(QColor(245, 158, 11), 1.0))
                painter.setBrush(QBrush(QColor("#FEF3C7")))
                painter.drawRoundedRect(badge_rect, 6, 6)
                painter.setFont(get_mono_font(11, weight=700))
                painter.setPen(QPen(QColor("#92400E")))
                painter.drawText(badge_rect, Qt.AlignCenter, "CMP ?")

        # 3. Calculate position and render each ball
        for i in range(n):
            val = values[i]
            state = self._get_element_state(i, sort_event, bars)

            pose = self._pose(i, centers, base_y, sort_event, t, radius)
            cur_x, cur_y = pose.x, pose.y
            scale_x, scale_y = pose.scale_x, pose.scale_y

            # Draw Ground Drop Shadow (scales with elevation)
            elevation = max(0.0, base_y - cur_y)
            shadow_w = radius * 1.8 * max(0.4, 1.0 - elevation * 0.008)
            shadow_h = 7.0 * max(0.3, 1.0 - elevation * 0.008)
            shadow_alpha = int(max(15, 60 * (1.0 - elevation * 0.01)))
            shadow_rect = QRectF(cur_x - shadow_w / 2.0, base_y + radius + 8 - shadow_h / 2.0, shadow_w, shadow_h)

            painter.setPen(Qt.NoPen)
            shadow_grad = QRadialGradient(cur_x, base_y + radius + 8, shadow_w / 2.0)
            shadow_grad.setColorAt(0.0, QColor(20, 30, 55, shadow_alpha))
            shadow_grad.setColorAt(1.0, QColor(20, 30, 55, 0))
            painter.setBrush(QBrush(shadow_grad))
            painter.drawEllipse(shadow_rect)

            # Draw Selection / Comparison Glowing Halo
            if state["comparing"] or state["swapping"] or state["min"] or state["pivot"]:
                halo_color = QColor(COLORS["accent_gold"])
                if state["swapping"]:
                    halo_color = QColor(COLORS["danger"])
                elif state["pivot"]:
                    halo_color = QColor("#8B5CF6")

                halo_radius = radius * 1.35
                halo_color.setAlpha(55)
                painter.setBrush(QBrush(halo_color))
                painter.drawEllipse(QPointF(cur_x, cur_y), halo_radius, halo_radius)

            # 3D Shaded Sphere
            ball_rect = QRectF(cur_x - radius * scale_x, cur_y - radius * scale_y,
                               radius * 2.0 * scale_x, radius * 2.0 * scale_y)

            # Determine sphere base color
            if state["sorted"]:
                c_light = QColor("#34D399")
                c_dark = QColor("#059669")
            elif state["swapping"]:
                c_light = QColor("#F87171")
                c_dark = QColor("#DC2626")
            elif state["pivot"]:
                c_light = QColor("#C084FC")
                c_dark = QColor("#7C3AED")
            elif state["min"] or state["key"]:
                c_light = QColor("#FBBF24")
                c_dark = QColor("#D97706")
            elif state["comparing"]:
                c_light = QColor("#60A5FA")
                c_dark = QColor("#2563EB")
            else:
                # Default ProofMotion soft indigo/slate
                c_light = QColor("#818CF8")
                c_dark = QColor("#4F46E5")

            sphere_grad = QRadialGradient(cur_x - radius * 0.32, cur_y - radius * 0.35, radius * 1.4)
            sphere_grad.setColorAt(0.0, QColor(255, 255, 255, 230))
            sphere_grad.setColorAt(0.35, c_light)
            sphere_grad.setColorAt(0.85, c_dark)
            sphere_grad.setColorAt(1.0, c_dark.darker(130))

            painter.setBrush(QBrush(sphere_grad))
            painter.setPen(QPen(c_dark.darker(140), 1.0))
            painter.drawEllipse(ball_rect)

            # Inner specular highlight crest
            highlight_rect = QRectF(cur_x - radius * 0.45, cur_y - radius * 0.55, radius * 0.55, radius * 0.32)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 110)))
            painter.drawEllipse(highlight_rect)

            # Numeric Value centered on ball
            font_size = max(11, int(diam * 0.32))
            painter.setFont(get_mono_font(font_size, weight=700))
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(ball_rect, Qt.AlignCenter, str(val))

            # Index label below slot
            painter.setFont(get_mono_font(12, weight=500))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(centers[i] - slot_w * 0.4, base_y + radius + 16, slot_w * 0.8, 18),
                             Qt.AlignCenter, f"[{i}]")

            # Status Tag badge above or below
            tag_label = ""
            tag_color = COLORS["text_secondary"]
            if state["sorted"]:
                tag_label = "SORTED"
                tag_color = COLORS["success"]
            elif state["pivot"]:
                tag_label = "PIVOT"
                tag_color = "#7C3AED"
            elif state["min"]:
                tag_label = "MIN"
                tag_color = COLORS["accent_gold"]
            elif state["key"]:
                tag_label = "KEY"
                tag_color = COLORS["accent_gold"]
            elif state["swapping"]:
                tag_label = "SWAP"
                tag_color = COLORS["danger"]
            elif state["comparing"]:
                tag_label = "CMP"
                tag_color = COLORS["accent_blue"]

            if tag_label:
                painter.setFont(get_ui_font(10, weight=700))
                painter.setPen(QPen(QColor(tag_color)))
                painter.drawText(QRectF(centers[i] - slot_w * 0.45, base_y + radius + 34, slot_w * 0.9, 16),
                                 Qt.AlignCenter, tag_label)

        painter.restore()

    # ==================================================================
    # 2. Floating Cubes Style
    # ==================================================================
    def _render_floating_cubes(self, painter: QPainter, width: int, height: int,
                              values: List[int], bars: Optional[List[Dict[str, Any]]],
                              sort_event: Optional[SortEvent], t: float):
        n = len(values)
        slot_w, cube_size, centers, base_y = self._compute_slots(width, height, n)
        cube_s = min(cube_size * 0.95, 54.0)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Baseline platform track
        painter.setPen(QPen(QColor(COLORS["border"]), 2.0))
        painter.drawLine(QPointF(centers[0] - slot_w * 0.4, base_y + cube_s * 0.8),
                         QPointF(centers[-1] + slot_w * 0.4, base_y + cube_s * 0.8))

        # Render each cube with 3 isometric faces
        for i in range(n):
            val = values[i]
            state = self._get_element_state(i, sort_event, bars)

            pose = self._pose(i, centers, base_y, sort_event, t, cube_s * 0.5)
            cx, cy = pose.x, pose.y
            lift = pose.lift if pose.lift else max(0.0, base_y - cy)

            # Ground shadow
            shadow_w = cube_s * 1.2
            shadow_h = 10.0
            shadow_alpha = int(max(15, 60 * (1.0 - abs(lift) * 0.012)))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(20, 30, 55, shadow_alpha)))
            painter.drawEllipse(QRectF(cx - shadow_w / 2.0, base_y + cube_s * 0.7 - shadow_h / 2.0, shadow_w, shadow_h))

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(pose.tilt_deg + pose.rotation_deg * 0.18)
            painter.translate(-cx, -cy)

            # Isometric cube geometry
            s = cube_s * 0.5
            dx = s * 0.866
            dy = s * 0.5

            # Base colors
            if state["sorted"]:
                c_top = QColor("#6EE7B7")
                c_front = QColor("#10B981")
                c_right = QColor("#047857")
            elif state["swapping"]:
                c_top = QColor("#FCA5A5")
                c_front = QColor("#EF4444")
                c_right = QColor("#B91C1C")
            elif state["pivot"]:
                c_top = QColor("#D8B4FE")
                c_front = QColor("#9333EA")
                c_right = QColor("#6B21A8")
            elif state["min"] or state["key"]:
                c_top = QColor("#FDE68A")
                c_front = QColor("#F59E0B")
                c_right = QColor("#B45309")
            elif state["comparing"]:
                c_top = QColor("#93C5FD")
                c_front = QColor("#3B82F6")
                c_right = QColor("#1D4ED8")
            else:
                c_top = QColor("#C7D2FE")
                c_front = QColor("#6366F1")
                c_right = QColor("#4338CA")

            # 1. Top Face
            p_center = QPointF(cx, cy - s)
            p_top = QPointF(cx, cy - s - dy)
            p_left = QPointF(cx - dx, cy - s)
            p_right = QPointF(cx + dx, cy - s)
            p_mid = QPointF(cx, cy - s + dy)

            top_poly = QPolygonF([p_top, p_right, p_mid, p_left])
            painter.setBrush(QBrush(c_top))
            painter.setPen(QPen(c_right.darker(120), 1.0))
            painter.drawPolygon(top_poly)

            # 2. Front-Left Face
            p_bot_left = QPointF(cx - dx, cy + s - dy)
            p_bot_mid = QPointF(cx, cy + s)
            front_poly = QPolygonF([p_left, p_mid, p_bot_mid, p_bot_left])
            painter.setBrush(QBrush(c_front))
            painter.drawPolygon(front_poly)

            # 3. Right Face
            p_bot_right = QPointF(cx + dx, cy + s - dy)
            right_poly = QPolygonF([p_mid, p_right, p_bot_right, p_bot_mid])
            painter.setBrush(QBrush(c_right))
            painter.drawPolygon(right_poly)

            # Value label on front face
            painter.setFont(get_mono_font(max(11, int(s * 0.7)), weight=700))
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(QRectF(cx - dx, cy - dy, dx * 2, s * 1.5), Qt.AlignCenter, str(val))
            painter.restore()

            # Minimum / Pivot crown indicator
            if state["min"]:
                painter.setFont(get_ui_font(12, weight=700))
                painter.setPen(QPen(QColor(COLORS["accent_gold"])))
                painter.drawText(QRectF(cx - 20, cy - s - dy - 22, 40, 18), Qt.AlignCenter, "👑 MIN")
            elif state["pivot"]:
                painter.setFont(get_ui_font(12, weight=700))
                painter.setPen(QPen(QColor("#9333EA")))
                painter.drawText(QRectF(cx - 20, cy - s - dy - 22, 40, 18), Qt.AlignCenter, "◆ PIVOT")

            # Slot index label
            painter.setFont(get_mono_font(12, weight=500))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(centers[i] - slot_w * 0.4, base_y + cube_s * 0.9, slot_w * 0.8, 18),
                             Qt.AlignCenter, f"[{i}]")

        painter.restore()

    # ==================================================================
    # 3. Marble Sorting Machine Style
    # ==================================================================
    def _render_marble_machine(self, painter: QPainter, width: int, height: int,
                               values: List[int], bars: Optional[List[Dict[str, Any]]],
                               sort_event: Optional[SortEvent], t: float):
        n = len(values)
        slot_w, diam, centers, base_y = self._compute_slots(width, height, n)
        radius = diam / 2.0

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 1. Dual polished steel rail tracks
        rail1_y = base_y + radius - 4
        rail2_y = base_y + radius + 12

        rail_grad = QLinearGradient(0, rail1_y, 0, rail2_y)
        rail_grad.setColorAt(0.0, QColor("#E2E8F0"))
        rail_grad.setColorAt(0.5, QColor("#94A3B8"))
        rail_grad.setColorAt(1.0, QColor("#64748B"))

        painter.setPen(QPen(QBrush(rail_grad), 3.5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(centers[0] - slot_w * 0.5, rail1_y), QPointF(centers[-1] + slot_w * 0.5, rail1_y))
        painter.drawLine(QPointF(centers[0] - slot_w * 0.5, rail2_y), QPointF(centers[-1] + slot_w * 0.5, rail2_y))

        # Rail ties / brackets
        painter.setPen(QPen(QColor("#CBD5E1"), 2.0))
        for cx in centers:
            painter.drawLine(QPointF(cx, rail1_y - 2), QPointF(cx, rail2_y + 4))

        # Active event indicators
        swap_pair = None
        if sort_event and sort_event.swapping_indices:
            swap_pair = sort_event.swapping_indices

        # Partition gate for Quick Sort
        if sort_event and sort_event.pivot_index is not None and 0 <= sort_event.pivot_index < n:
            p_cx = centers[sort_event.pivot_index]
            gate_rect = QRectF(p_cx - 4, base_y - radius - 35, 8, radius * 2 + 50)
            painter.setBrush(QBrush(QColor("#8B5CF6")))
            painter.setPen(QPen(QColor("#6D28D9"), 1.0))
            painter.drawRoundedRect(gate_rect, 3, 3)

            painter.setFont(get_mono_font(10, weight=700))
            painter.setPen(QPen(QColor("#6D28D9")))
            painter.drawText(QRectF(p_cx - 30, base_y - radius - 52, 60, 16), Qt.AlignCenter, "GATE")

        # 2. Render each marble
        for i in range(n):
            val = values[i]
            state = self._get_element_state(i, sort_event, bars)

            pose = self._pose(i, centers, base_y, sort_event, t, radius)
            cur_x, cur_y = pose.x, pose.y

            painter.save()
            painter.translate(cur_x, cur_y)
            painter.rotate(pose.rotation_deg)

            # Glass marble with colorful core swirl
            marble_rect = QRectF(-radius, -radius, radius * 2, radius * 2)

            # Marble outer glass gradient
            glass_grad = QRadialGradient(-radius * 0.35, -radius * 0.35, radius * 1.3)
            glass_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
            glass_grad.setColorAt(0.4, QColor(241, 245, 249, 180))
            glass_grad.setColorAt(0.85, QColor(148, 163, 184, 210))
            glass_grad.setColorAt(1.0, QColor(71, 85, 105, 240))

            painter.setBrush(QBrush(glass_grad))
            painter.setPen(QPen(QColor(100, 116, 139), 1.2))
            painter.drawEllipse(marble_rect)

            # Inner colored swirl core
            core_r = radius * 0.62
            if state["sorted"]:
                core_c = QColor("#10B981")
            elif state["swapping"]:
                core_c = QColor("#EF4444")
            elif state["pivot"]:
                core_c = QColor("#8B5CF6")
            elif state["min"] or state["key"]:
                core_c = QColor("#F59E0B")
            elif state["comparing"]:
                core_c = QColor("#3B82F6")
            else:
                core_c = QColor("#0EA5E9")

            core_grad = QRadialGradient(-core_r * 0.2, -core_r * 0.2, core_r)
            core_grad.setColorAt(0.0, core_c.lighter(130))
            core_grad.setColorAt(1.0, core_c.darker(120))

            painter.setBrush(QBrush(core_grad))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(-core_r, -core_r, core_r * 2, core_r * 2))

            # Rolling stripe so rotation is visible
            painter.setBrush(QBrush(QColor(255, 255, 255, 70)))
            painter.drawEllipse(QRectF(-radius * 0.18, -radius * 0.72, radius * 0.36, radius * 0.28))
            stripe = QPainterPath()
            stripe.moveTo(-radius * 0.55, -radius * 0.15)
            stripe.quadTo(0, radius * 0.08, radius * 0.55, -radius * 0.1)
            painter.setPen(QPen(QColor(255, 255, 255, 90), max(2.0, radius * 0.12), Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(stripe)

            # Numeric Value stays upright
            painter.rotate(-pose.rotation_deg)
            font_size = max(10, int(diam * 0.3))
            painter.setFont(get_mono_font(font_size, weight=700))
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(QRectF(-radius, -radius, radius * 2, radius * 2), Qt.AlignCenter, str(val))
            painter.restore()

            # Index label below
            painter.setFont(get_mono_font(12, weight=500))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(centers[i] - slot_w * 0.4, rail2_y + 8, slot_w * 0.8, 18),
                             Qt.AlignCenter, f"[{i}]")

        painter.restore()

    # ==================================================================
    # 4. Toy Cars Style
    # ==================================================================
    def _render_toy_cars(self, painter: QPainter, width: int, height: int,
                         values: List[int], bars: Optional[List[Dict[str, Any]]],
                         sort_event: Optional[SortEvent], t: float):
        n = len(values)
        slot_w, size, centers, base_y = self._compute_slots(width, height, n)
        car_w = min(size * 1.35, slot_w * 0.82)
        car_h = car_w * 0.48

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        road_y = base_y + car_h * 0.35
        road_x = centers[0] - slot_w * 0.55
        road_w = centers[-1] - centers[0] + slot_w * 1.1
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#94A3B8")))
        painter.drawRoundedRect(QRectF(road_x, road_y - 22, road_w, 18), 8, 8)
        painter.setBrush(QBrush(QColor("#CBD5E1")))
        painter.drawRoundedRect(QRectF(road_x, road_y, road_w, 16), 8, 8)
        painter.setPen(QPen(QColor("#F8FAFC"), 2, Qt.DashLine))
        painter.drawLine(QPointF(centers[0] - slot_w * 0.3, road_y + 8),
                         QPointF(centers[-1] + slot_w * 0.3, road_y + 8))
        painter.setPen(QPen(QColor("#E2E8F0"), 1.5, Qt.DashLine))
        painter.drawLine(QPointF(centers[0] - slot_w * 0.3, road_y - 13),
                         QPointF(centers[-1] + slot_w * 0.3, road_y - 13))

        for i in range(n):
            val = values[i]
            state = self._get_element_state(i, sort_event, bars)
            pose = self._pose(i, centers, base_y, sort_event, t, size * 0.5)
            cx, cy = pose.x, pose.y

            if state["sorted"]:
                body = QColor("#10B981")
            elif state["swapping"] or state["shifting"]:
                body = QColor("#EF4444")
            elif state["pivot"]:
                body = QColor("#8B5CF6")
            elif state["min"] or state["key"]:
                body = QColor("#F59E0B")
            elif state["comparing"]:
                body = QColor("#3B82F6")
            else:
                body = QColor("#4F46E5")

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(pose.tilt_deg)

            body_rect = QRectF(-car_w / 2.0, -car_h / 2.0, car_w, car_h)
            cabin = QRectF(-car_w * 0.22, -car_h * 0.95, car_w * 0.44, car_h * 0.58)
            painter.setBrush(QBrush(body))
            painter.setPen(QPen(body.darker(130), 1.0))
            painter.drawRoundedRect(body_rect, 7, 7)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawRoundedRect(cabin, 5, 5)

            wheel_r = max(4.0, car_h * 0.28)
            for wx in (-car_w * 0.28, car_w * 0.28):
                wy = car_h * 0.42
                painter.setBrush(QBrush(QColor("#0F172A")))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(wx, wy), wheel_r, wheel_r)
                painter.save()
                painter.translate(wx, wy)
                painter.rotate(pose.rotation_deg)
                painter.setPen(QPen(QColor("#E2E8F0"), max(1.4, wheel_r * 0.28)))
                painter.drawLine(QPointF(-wheel_r * 0.7, 0), QPointF(wheel_r * 0.7, 0))
                painter.drawLine(QPointF(0, -wheel_r * 0.7), QPointF(0, wheel_r * 0.7))
                painter.restore()

            painter.setFont(get_mono_font(max(10, int(car_h * 0.55)), weight=700))
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(body_rect, Qt.AlignCenter, str(val))
            painter.restore()

            painter.setFont(get_mono_font(11, weight=500))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(centers[i] - slot_w * 0.4, road_y + 20, slot_w * 0.8, 16),
                             Qt.AlignCenter, f"[{i}]")

        painter.restore()

    # ==================================================================
    # 5. Conventional Bars Style (Fallback)
    # ==================================================================
    def _render_conventional_bars(self, painter: QPainter, width: int, height: int,
                                 values: List[int], bars: Optional[List[Dict[str, Any]]],
                                 sort_event: Optional[SortEvent], t: float):
        n = len(values)
        margin_x = 44.0
        margin_y = 50.0
        avail_w = max(100.0, width - 2 * margin_x)
        avail_h = max(80.0, height - 2 * margin_y)

        bar_spacing = max(3, min(14, int(avail_w / (n * 4))))
        bar_w = (avail_w - (n - 1) * bar_spacing) / max(1, n)
        max_val = max(max(values), 1)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        for i in range(n):
            val = values[i]
            state = self._get_element_state(i, sort_event, bars)

            bar_h = (val / max_val) * (avail_h - 40)
            rest_x = margin_x + i * (bar_w + bar_spacing)
            rest_y = height - margin_y - bar_h
            slot_centers = [margin_x + k * (bar_w + bar_spacing) for k in range(n)]
            pose = self._pose(i, slot_centers, rest_y, sort_event, t)
            bx = pose.x
            by = rest_y
            bar_h = bar_h * pose.scale_y
            by = height - margin_y - bar_h

            # Color logic
            if state["sorted"]:
                c_base = QColor(COLORS["success"])
            elif state["swapping"]:
                c_base = QColor(COLORS["danger"])
            elif state["pivot"]:
                c_base = QColor("#8B5CF6")
            elif state["min"] or state["key"]:
                c_base = QColor(COLORS["accent_gold"])
            elif state["comparing"]:
                c_base = QColor(COLORS["accent_blue"])
            else:
                c_base = QColor(COLORS["accent_teal"])

            bar_grad = QLinearGradient(bx, by, bx, by + bar_h)
            bar_grad.setColorAt(0.0, c_base.lighter(115))
            bar_grad.setColorAt(1.0, c_base)

            painter.setBrush(QBrush(bar_grad))
            painter.setPen(QPen(QColor(COLORS["border"]), 1.0))
            painter.drawRoundedRect(QRectF(bx, by, bar_w, bar_h), 5, 5)

            # Value label on top
            painter.setFont(get_mono_font(13, weight=600))
            painter.setPen(QPen(QColor(COLORS["text_primary"])))
            painter.drawText(QRectF(bx - 10, by - 22, bar_w + 20, 18), Qt.AlignCenter, str(val))

            # Index label below
            painter.setFont(get_mono_font(12, weight=400))
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            painter.drawText(QRectF(bx - 10, height - margin_y + 6, bar_w + 20, 16), Qt.AlignCenter, f"[{i}]")

            # Tag label if active
            tag_label = ""
            if state["sorted"]:
                tag_label = "SORTED"
            elif state["pivot"]:
                tag_label = "PIVOT"
            elif state["min"]:
                tag_label = "MIN"
            elif state["swapping"]:
                tag_label = "SWAP"
            elif state["comparing"]:
                tag_label = "CMP"

            if tag_label:
                painter.setFont(get_ui_font(10, weight=700))
                painter.setPen(QPen(c_base))
                painter.drawText(QRectF(bx - 20, height - margin_y + 24, bar_w + 40, 16), Qt.AlignCenter, tag_label)

        painter.restore()

