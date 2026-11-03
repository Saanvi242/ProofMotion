"""
ui/home_screens.py
------------------
Launch gateway (Learn vs Studio) and the Learn topic catalog.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QScrollArea, QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QPolygonF, QFont,
)
from resources.theme import get_mono_font, get_ui_font, COLORS


LEARNING_TOPICS = [
    ("sorting", "Sorting Algorithms", "Arrange elements in order using comparisons and swaps.", "Bubble, Selection, Insertion, Merge, Quick"),
    ("searching", "Searching Algorithms", "Locate target values through sequential scans and interval halving.", "Linear & Binary Search"),
    ("graphs", "Graph Algorithms", "Build minimum spanning trees and compare greedy strategies.", "Prim's & Kruskal's Algorithms"),
    ("trees", "Trees & Traversals", "Explore binary search tree invariants and recursive visit orders.", "BST CRUD & 4 Traversal Orders"),
    ("transformations", "2D Transformations", "Translate, rotate, scale, and shear shapes on the Cartesian plane.", "Homogeneous 2D matrices"),
    ("rasterization", "Rasterization", "Convert continuous geometric lines and circles into discrete pixels.", "Bresenham & Midpoint algorithms"),
    ("clipping", "Clipping", "Determine geometric visibility inside rectangular windows and viewports.", "Cohen-Sutherland outcodes"),
    ("theorems", "Theorems", "Interactive geometric proofs that unfold visually step-by-step.", "Pythagoras, Cosines & Similar Triangles"),
]

# Per-topic gradient colors for distinct card previews
TOPIC_GRADIENTS = {
    "sorting":             ("#F0EDFF", "#E1DAFB"),
    "searching":           ("#EFF6FF", "#DBEAFE"),
    "graphs":              ("#ECFDF5", "#D1FAE5"),
    "trees":               ("#FDF4FF", "#F5D0FE"),
    "transformations":     ("#EDF4FF", "#DAE8FB"),
    "rasterization":       ("#F0FFF4", "#D9F2E3"),
    "clipping":            ("#FFF7ED", "#FBEBD6"),
    "theorems":            ("#F0F7FF", "#D6E6FB"),
    "algorithms":          ("#F0EDFF", "#E1DAFB"),
    "learn":               ("#F0EDFF", "#E1DAFB"),
    "studio":              ("#12141C", "#07080D"),
}


def _shadow(widget, blur=28, alpha=40, y=8):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setColor(QColor(90, 70, 180, alpha))
    effect.setOffset(0, y)
    widget.setGraphicsEffect(effect)


def paint_topic_preview(p: QPainter, rect: QRectF, key: str):
    """Draw a compact illustration for a learning topic."""
    p.save()
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setClipRect(rect, Qt.IntersectClip)

    # Per-topic gradient for visual distinction
    grad_colors = TOPIC_GRADIENTS.get(key, ("#F4F1FF", "#E8EEFB"))
    bg = QLinearGradient(rect.topLeft(), rect.bottomRight())
    bg.setColorAt(0.0, QColor(grad_colors[0]))
    bg.setColorAt(1.0, QColor(grad_colors[1]))
    p.fillRect(rect, QBrush(bg))

    cx, cy = rect.center().x(), rect.center().y()
    w, h = rect.width(), rect.height()

    if key == "learn":
        # Interactive Mathematical Proof & Algorithm Learning Lab
        # 1. Background drafting grid
        p.setPen(QPen(QColor(180, 170, 230, 60), 1.0, Qt.DotLine))
        gx = rect.left() + 24
        while gx < rect.right() - 20:
            p.drawLine(QPointF(gx, rect.top() + 10), QPointF(gx, rect.bottom() - 10))
            gx += 28
        gy = rect.top() + 20
        while gy < rect.bottom() - 15:
            p.drawLine(QPointF(rect.left() + 15, gy), QPointF(rect.right() - 15, gy))
            gy += 28

        # 2. Main lesson workbench slate
        slate_w = min(w * 0.84, 340.0)
        slate_h = min(h * 0.74, 160.0)
        slate_x = cx - slate_w / 2.0
        slate_y = cy - slate_h / 2.0 - 4.0
        slate_rect = QRectF(slate_x, slate_y, slate_w, slate_h)

        # Soft card shadow
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(100, 80, 190, 20)))
        p.drawRoundedRect(slate_rect.adjusted(0, 5, 0, 7), 16, 16)

        # Slate body
        p.setPen(QPen(QColor("#D6D3F8"), 1.5))
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.drawRoundedRect(slate_rect, 16, 16)

        # Workbench header bar
        hdr_h = 26.0
        header_path = QPainterPath()
        header_path.addRoundedRect(QRectF(slate_x, slate_y, slate_w, hdr_h + 10), 16, 16)
        hdr_rect = QRectF(slate_x, slate_y, slate_w, hdr_h)
        p.save()
        p.setClipRect(hdr_rect)
        p.fillPath(header_path, QBrush(QColor("#F8FAFC")))
        p.setPen(QPen(QColor("#E2E8F0"), 1.0))
        p.drawLine(QPointF(slate_x, slate_y + hdr_h), QPointF(slate_x + slate_w, slate_y + hdr_h))
        p.restore()

        # Traffic light dots on header
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#F87171")))
        p.drawEllipse(QPointF(slate_x + 14, slate_y + hdr_h / 2.0), 3.2, 3.2)
        p.setBrush(QBrush(QColor("#FBBF24")))
        p.drawEllipse(QPointF(slate_x + 24, slate_y + hdr_h / 2.0), 3.2, 3.2)
        p.setBrush(QBrush(QColor("#34D399")))
        p.drawEllipse(QPointF(slate_x + 34, slate_y + hdr_h / 2.0), 3.2, 3.2)

        # Header title
        p.setFont(get_mono_font(9, weight=600))
        p.setPen(QPen(QColor("#64748B")))
        p.drawText(QRectF(slate_x + 46, slate_y, 220, hdr_h), Qt.AlignLeft | Qt.AlignVCenter, "INTERACTIVE PROOF & ALGO LAB")

        # Left: Geometric Theorem (Right-angle triangle + proof square)
        t_base = slate_y + slate_h - 26.0
        t_left = slate_x + 36.0
        t_w = min(slate_w * 0.22, 66.0)
        t_h = min(slate_h * 0.44, 52.0)
        t_orig = QPointF(t_left, t_base)
        tri_pts = [t_orig, t_orig + QPointF(t_w, 0), t_orig + QPointF(0, -t_h)]
        p.setPen(QPen(QColor("#6366F1"), 2.0))
        p.setBrush(QBrush(QColor(99, 102, 241, 30)))
        p.drawPolygon(QPolygonF(tri_pts))

        # Right-angle indicator
        p.setPen(QPen(QColor("#4F46E5"), 1.2))
        p.setBrush(QBrush(QColor(99, 102, 241, 50)))
        p.drawRect(QRectF(t_orig.x(), t_orig.y() - 9, 9, 9))

        # Adjacent proof area (Pythagorean)
        p.setPen(QPen(QColor("#F59E0B"), 1.2, Qt.DashLine))
        p.setBrush(QBrush(QColor(245, 158, 11, 25)))
        p.drawRect(QRectF(t_orig.x() - 13, t_orig.y() - t_h, 13, t_h))

        # Center: Smooth Bézier motion curve connecting geometry to algorithms
        curve_path = QPainterPath()
        p0 = t_orig + QPointF(t_w, -8)
        p1 = QPointF(cx - slate_w * 0.08, slate_y + hdr_h + 10)
        p2 = QPointF(cx + slate_w * 0.06, slate_y + slate_h - 18)
        p3 = QPointF(slate_x + slate_w - 75, slate_y + hdr_h + 24)
        curve_path.moveTo(p0)
        curve_path.cubicTo(p1, p2, p3)
        p.setPen(QPen(QColor("#8B5CF6"), 2.4, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawPath(curve_path)

        # Right: Algorithm Graph / Tree Nodes (A -> B, A -> C)
        node_a = QPointF(slate_x + slate_w - 75, slate_y + hdr_h + 24)
        node_b = QPointF(slate_x + slate_w - 110, slate_y + slate_h - 28)
        node_c = QPointF(slate_x + slate_w - 38, slate_y + slate_h - 28)

        # Edges
        p.setPen(QPen(QColor("#10B981"), 2.2))
        p.drawLine(node_a, node_b)
        p.drawLine(node_a, node_c)
        p.setPen(QPen(QColor("#CBD5E1"), 1.4, Qt.DashLine))
        p.drawLine(node_b, node_c)

        # Nodes
        for pt, name, col in [(node_a, "A", "#7C3AED"), (node_b, "B", "#10B981"), (node_c, "C", "#06B6D4")]:
            p.setPen(QPen(QColor("#FFFFFF"), 2.0))
            p.setBrush(QBrush(QColor(col)))
            p.drawEllipse(pt, 9.0, 9.0)
            p.setFont(get_mono_font(8.5, weight=700))
            p.setPen(QPen(QColor("#FFFFFF")))
            p.drawText(QRectF(pt.x() - 9.0, pt.y() - 9.0, 18, 18), Qt.AlignCenter, name)

        # Bottom step pill badge
        pill_w = min(slate_w * 0.65, 210.0)
        pill_h = 22.0
        pill_rect = QRectF(cx - pill_w / 2.0, slate_y + slate_h - pill_h / 2.0 + 2.0, pill_w, pill_h)
        p.setPen(QPen(QColor("#C7D2FE"), 1.2))
        p.setBrush(QBrush(QColor("#EEF2FF")))
        p.drawRoundedRect(pill_rect, 11, 11)
        p.setFont(get_mono_font(9, weight=700))
        p.setPen(QPen(QColor("#4338CA")))
        p.drawText(pill_rect, Qt.AlignCenter, "STEP 01  →  INTERACTIVE PROOF")

    elif key in ("sorting", "algorithms"):
        # Arrangement of bars in mid-sort state (not monotonic signal bars)
        bar_vals = [55, 115, 38, 135, 78, 96]
        max_v = max(bar_vals)
        n = len(bar_vals)
        bar_w = min(w * 0.08, 22.0)
        gap = w * 0.045
        total_w = n * bar_w + (n - 1) * gap
        x0 = cx - total_w / 2.0
        base_y = cy + h * 0.28
        for i, val in enumerate(bar_vals):
            bx = x0 + i * (bar_w + gap)
            bh = (val / max_v) * (h * 0.55)
            by = base_y - bh
            r = QRectF(bx, by, bar_w, bh)
            is_active = (i in (1, 3))
            grad = QLinearGradient(bx, by, bx, base_y)
            if is_active:
                grad.setColorAt(0.0, QColor("#8B78F2"))
                grad.setColorAt(1.0, QColor("#5B4AD4"))
            else:
                grad.setColorAt(0.0, QColor("#CBD5E1"))
                grad.setColorAt(1.0, QColor("#94A3B8"))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(r, 4.0, 4.0)

        # Comparison arc between swapped bars 1 and 3
        p.setPen(QPen(QColor("#6C5CE7"), 1.8, Qt.DashLine))
        p.setBrush(Qt.NoBrush)
        arc_x = x0 + 1 * (bar_w + gap) + bar_w * 0.5
        arc_w = 2 * (bar_w + gap)
        p.drawArc(QRectF(arc_x, cy - h * 0.28, arc_w, 24.0), 0, 180 * 16)
        # Ground line
        p.setPen(QPen(QColor("#D5DDED"), 1.4))
        p.drawLine(QPointF(rect.left() + 18, base_y + 4), QPointF(rect.right() - 18, base_y + 4))

    elif key == "searching":
        # Horizontal array of elements with a highlighted target element
        tiles = ["12", "25", "38", "45", "64", "80"]
        n = len(tiles)
        tile_w = min(w * 0.12, 34.0)
        tile_h = 32.0
        gap = 8.0
        total_w = n * tile_w + (n - 1) * gap
        x0 = cx - total_w / 2.0
        y0 = cy - tile_h / 2.0
        for i, val in enumerate(tiles):
            tx = x0 + i * (tile_w + gap)
            r = QRectF(tx, y0, tile_w, tile_h)
            is_target = (i == 3)
            p.setBrush(QBrush(QColor("#6C5CE7" if is_target else "#FFFFFF")))
            p.setPen(QPen(QColor("#4D3BB8" if is_target else "#CBD5E1"), 1.6 if is_target else 1.2))
            p.drawRoundedRect(r, 6.0, 6.0)

            # Text
            p.setFont(get_mono_font(10, weight=700 if is_target else 600))
            p.setPen(QPen(QColor("#FFFFFF" if is_target else "#334155")))
            p.drawText(r, Qt.AlignCenter, val)

            # Target pointer above target tile
            if is_target:
                p.setPen(QPen(QColor("#F59E0B"), 2.0))
                p.drawLine(QPointF(tx + tile_w / 2.0, y0 - 14), QPointF(tx + tile_w / 2.0, y0 - 4))
                p.drawLine(QPointF(tx + tile_w / 2.0 - 4, y0 - 8), QPointF(tx + tile_w / 2.0, y0 - 4))
                p.drawLine(QPointF(tx + tile_w / 2.0 + 4, y0 - 8), QPointF(tx + tile_w / 2.0, y0 - 4))

    elif key == "graphs":
        # Weighted graph with selected green edges
        g_nodes = [
            ("A", cx - w * 0.28, cy - h * 0.12),
            ("B", cx - w * 0.08, cy - h * 0.26),
            ("C", cx + w * 0.18, cy - h * 0.22),
            ("D", cx + w * 0.28, cy + h * 0.16),
            ("E", cx - w * 0.12, cy + h * 0.24),
        ]
        g_edges = [
            (0, 1, True, "4"),   # A-B (MST)
            (1, 2, True, "2"),   # B-C (MST)
            (2, 3, True, "3"),   # C-D (MST)
            (0, 4, True, "3"),   # A-E (MST)
            (1, 4, False, "6"),  # B-E
            (2, 4, False, "5"),  # C-E
        ]
        for u_i, v_i, is_mst, wt in g_edges:
            ux, uy = g_nodes[u_i][1], g_nodes[u_i][2]
            vx, vy = g_nodes[v_i][1], g_nodes[v_i][2]
            p.setPen(QPen(QColor("#10B981" if is_mst else "#CBD5E1"), 2.4 if is_mst else 1.2, Qt.SolidLine if is_mst else Qt.DashLine))
            p.drawLine(QPointF(ux, uy), QPointF(vx, vy))

        for lbl, nx, ny in g_nodes:
            p.setBrush(QBrush(QColor("#FFFFFF")))
            p.setPen(QPen(QColor("#6C5CE7"), 2.0))
            p.drawEllipse(QPointF(nx, ny), 12.0, 12.0)
            p.setFont(get_mono_font(9, weight=700))
            p.setPen(QPen(QColor("#6C5CE7")))
            p.drawText(QRectF(nx - 12, ny - 12, 24, 24), Qt.AlignCenter, lbl)

    elif key == "trees":
        # Binary search tree with highlighted nodes
        t_nodes = [
            ("50", cx, cy - h * 0.28, True),
            ("30", cx - w * 0.20, cy, True),
            ("70", cx + w * 0.20, cy, False),
            ("20", cx - w * 0.30, cy + h * 0.26, False),
            ("40", cx - w * 0.10, cy + h * 0.26, True),
        ]
        t_edges = [(0, 1, True), (0, 2, False), (1, 3, False), (1, 4, True)]
        for u_i, v_i, is_path in t_edges:
            ux, uy = t_nodes[u_i][1], t_nodes[u_i][2]
            vx, vy = t_nodes[v_i][1], t_nodes[v_i][2]
            p.setPen(QPen(QColor("#6C5CE7" if is_path else "#CBD5E1"), 2.2 if is_path else 1.2))
            p.drawLine(QPointF(ux, uy), QPointF(vx, vy))

        for lbl, nx, ny, is_hl in t_nodes:
            p.setBrush(QBrush(QColor("#6C5CE7" if is_hl else "#FFFFFF")))
            p.setPen(QPen(QColor("#4D3BB8" if is_hl else "#94A3B8"), 1.8 if is_hl else 1.2))
            p.drawEllipse(QPointF(nx, ny), 12.5, 12.5)
            p.setFont(get_mono_font(8, weight=700))
            p.setPen(QPen(QColor("#FFFFFF" if is_hl else "#1E293B")))
            p.drawText(QRectF(nx - 12, ny - 12, 24, 24), Qt.AlignCenter, lbl)

    elif key == "transformations":
        p.setPen(QPen(QColor("#C5CDDC"), 1.3))
        p.drawLine(QPointF(rect.left() + 20, cy + 18), QPointF(rect.right() - 20, cy + 18))
        p.drawLine(QPointF(cx - 10, rect.top() + 18), QPointF(cx - 10, rect.bottom() - 18))
        tri = QPolygonF([
            QPointF(cx - 8, cy + 16),
            QPointF(cx + 52, cy + 16),
            QPointF(cx - 8, cy - 42),
        ])
        p.setBrush(QBrush(QColor(108, 92, 231, 40)))
        p.setPen(QPen(QColor("#6C5CE7"), 1.8))
        p.drawPolygon(tri)
        p.setPen(QPen(QColor("#6C5CE7"), 1.5, Qt.DashLine))
        p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(cx - 36, cy - 36, 72, 72), 20 * 16, 110 * 16)

    elif key == "rasterization":
        cols, rows = 9, 6
        cell = min((w - 40) / cols, (h - 36) / rows)
        ox = cx - cols * cell / 2
        oy = cy - rows * cell / 2 + 4
        filled = {(1, 4), (2, 3), (3, 3), (4, 2), (5, 2), (6, 1), (7, 1)}
        for gy in range(rows):
            for gx in range(cols):
                r = QRectF(ox + gx * cell, oy + gy * cell, cell - 2.2, cell - 2.2)
                if (gx, gy) in filled:
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(QColor("#6C5CE7")))
                    p.drawRoundedRect(r, 2.2, 2.2)
                else:
                    p.setPen(QPen(QColor("#D5DDED"), 1.0))
                    p.setBrush(QBrush(QColor("#FFFFFF")))
                    p.drawRoundedRect(r, 2.2, 2.2)
        p.setPen(QPen(QColor("#F59E0B"), 1.8))
        p.drawLine(QPointF(ox + cell, oy + 5 * cell), QPointF(ox + 8 * cell, oy + cell))

    elif key == "clipping":
        win = QRectF(cx - w * 0.22, cy - h * 0.22, w * 0.44, h * 0.42)
        p.setPen(QPen(QColor("#6C5CE7"), 2.0))
        p.setBrush(QBrush(QColor(108, 92, 231, 28)))
        p.drawRoundedRect(win, 6, 6)
        p.setPen(QPen(QColor("#94A3B8"), 1.8, Qt.DashLine, Qt.RoundCap))
        p.drawLine(QPointF(rect.left() + 22, cy + h * 0.22), QPointF(win.left(), cy + 8))
        p.setPen(QPen(QColor("#0F172A"), 2.2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(win.left(), cy + 8), QPointF(win.right(), cy - 10))
        p.setPen(QPen(QColor("#94A3B8"), 1.8, Qt.DashLine, Qt.RoundCap))
        p.drawLine(QPointF(win.right(), cy - 10), QPointF(rect.right() - 22, cy - h * 0.22))
        p.setBrush(QBrush(QColor("#F59E0B")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(win.left(), cy + 8), 4.2, 4.2)
        p.drawEllipse(QPointF(win.right(), cy - 10), 4.2, 4.2)

    elif key == "theorems":
        a, b = w * 0.22, h * 0.28
        origin = QPointF(cx - a * 0.35, cy + b * 0.35)
        p.setPen(QPen(QColor("#0F172A"), 1.7))
        p.setBrush(QBrush(QColor(108, 92, 231, 35)))
        tri = QPolygonF([origin, origin + QPointF(a, 0), origin + QPointF(0, -b)])
        p.drawPolygon(tri)
        p.setBrush(QBrush(QColor(245, 158, 11, 40)))
        p.setPen(QPen(QColor("#D97706"), 1.2))
        p.drawRect(QRectF(origin.x(), origin.y(), a, a * 0.42))
        p.setBrush(QBrush(QColor(47, 158, 120, 40)))
        p.setPen(QPen(QColor("#2F9E78"), 1.2))
        p.drawRect(QRectF(origin.x() - b * 0.42, origin.y() - b, b * 0.42, b))

    elif key == "studio":
        p.setPen(QPen(QColor("#2A9A8C"), 1.6))
        p.setBrush(Qt.NoBrush)
        cube = [
            QPointF(cx - 28, cy - 4),
            QPointF(cx + 4, cy - 22),
            QPointF(cx + 36, cy - 4),
            QPointF(cx + 4, cy + 14),
        ]
        p.drawPolygon(QPolygonF(cube))
        p.drawLine(QPointF(cx - 28, cy - 4), QPointF(cx - 28, cy + 28))
        p.drawLine(QPointF(cx + 36, cy - 4), QPointF(cx + 36, cy + 28))
        p.drawLine(QPointF(cx + 4, cy + 14), QPointF(cx + 4, cy + 46))
        p.drawLine(QPointF(cx - 28, cy + 28), QPointF(cx + 4, cy + 46))
        p.drawLine(QPointF(cx + 36, cy + 28), QPointF(cx + 4, cy + 46))
        p.setPen(QPen(QColor("#5EEAD4"), 1.4, Qt.DashLine))
        p.drawRect(QRectF(cx - 56, cy - 40, 70, 48))

    p.restore()


class PreviewCanvas(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self._kind = kind
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(132)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(self.rect())
        clip = QPainterPath()
        clip.addRoundedRect(r.adjusted(0, 0, 0, 20), 20, 20)
        p.setClipPath(clip)
        paint_topic_preview(p, r, self._kind)
        p.end()


class SmoothElevator:
    """Animates drop shadow blur, vertical offset, and glow color for 3D card elevation."""
    def __init__(self, shadow: QGraphicsDropShadowEffect, rest_b=22, hover_b=38,
                 rest_y=5, hover_y=14, rest_c=None, hover_c=None):
        self.shadow = shadow
        self.rest_b = rest_b
        self.hover_b = hover_b
        self.rest_y = rest_y
        self.hover_y = hover_y
        self.rest_c = rest_c or QColor(25, 35, 65, 32)
        self.hover_c = hover_c or QColor(108, 92, 231, 70)

        self.anim_b = QPropertyAnimation(shadow, b"blurRadius")
        self.anim_b.setDuration(160)
        self.anim_b.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_o = QPropertyAnimation(shadow, b"offset")
        self.anim_o.setDuration(160)
        self.anim_o.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_c = QPropertyAnimation(shadow, b"color")
        self.anim_c.setDuration(160)
        self.anim_c.setEasingCurve(QEasingCurve.OutCubic)

    def lift(self):
        self.anim_b.stop()
        self.anim_o.stop()
        self.anim_c.stop()
        self.anim_b.setStartValue(self.shadow.blurRadius())
        self.anim_b.setEndValue(self.hover_b)
        self.anim_o.setStartValue(self.shadow.offset())
        self.anim_o.setEndValue(QPointF(0, self.hover_y))
        self.anim_c.setStartValue(self.shadow.color())
        self.anim_c.setEndValue(self.hover_c)
        self.anim_b.start()
        self.anim_o.start()
        self.anim_c.start()

    def settle(self):
        self.anim_b.stop()
        self.anim_o.stop()
        self.anim_c.stop()
        self.anim_b.setStartValue(self.shadow.blurRadius())
        self.anim_b.setEndValue(self.rest_b)
        self.anim_o.setStartValue(self.shadow.offset())
        self.anim_o.setEndValue(QPointF(0, self.rest_y))
        self.anim_c.setStartValue(self.shadow.color())
        self.anim_c.setEndValue(self.rest_c)
        self.anim_b.start()
        self.anim_o.start()
        self.anim_c.start()


class TopicCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, key: str, title: str, caption: str, meta: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("TopicCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(220, 236)
        self._is_hovered = False

        # Enhanced shadow for 3D pop effect
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(22)
        self._shadow_effect.setColor(QColor(25, 35, 65, 32))
        self._shadow_effect.setOffset(0, 5)
        self.setGraphicsEffect(self._shadow_effect)

        self._elevator = SmoothElevator(
            self._shadow_effect,
            rest_b=22, hover_b=38,
            rest_y=5, hover_y=14,
            rest_c=QColor(25, 35, 65, 32),
            hover_c=QColor(108, 92, 231, 70),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Spacer placeholder for the preview painting area
        self.preview_placeholder = QWidget(self)
        self.preview_placeholder.setObjectName("TopicCardPreview")
        self.preview_placeholder.setMinimumHeight(140)
        self.preview_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_placeholder.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.preview_placeholder, stretch=1)

        body = QWidget(self)
        body.setObjectName("TopicCardBody")
        body.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        body_col = QVBoxLayout(body)
        body_col.setContentsMargins(16, 12, 16, 14)
        body_col.setSpacing(4)

        title_lab = QLabel(title, body)
        title_lab.setObjectName("TopicCardTitle")
        cap = QLabel(caption, body)
        cap.setObjectName("TopicCardCaption")
        cap.setWordWrap(True)

        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 4, 0, 0)
        meta_row.setSpacing(6)
        meta_lab = QLabel(meta, body)
        meta_lab.setObjectName("TopicCardMeta")
        self.arrow_lab = QLabel("→", body)
        self.arrow_lab.setObjectName("TopicCardArrow")
        self.arrow_lab.setAlignment(Qt.AlignCenter)
        meta_row.addWidget(meta_lab, stretch=1)
        meta_row.addWidget(self.arrow_lab)

        body_col.addWidget(title_lab)
        body_col.addWidget(cap)
        body_col.addLayout(meta_row)
        layout.addWidget(body)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        radius = 20.0
        inset = 0.8
        card_rect = QRectF(inset, inset, w - inset * 2, h - inset * 2)

        card_path = QPainterPath()
        card_path.addRoundedRect(card_rect, radius, radius)

        # 1. Fill card background (clean white)
        p.fillPath(card_path, QBrush(QColor("#FFFFFF")))

        # 2. Clip strictly to the rounded card shape
        p.save()
        p.setClipPath(card_path)

        # 3. Paint preview illustration in the upper area
        pv_h = float(self.preview_placeholder.height()) if self.preview_placeholder.height() > 10 else 140.0
        preview_rect = QRectF(0.0, 0.0, w, pv_h)
        paint_topic_preview(p, preview_rect, self.key)

        # 4. Subtle separator line between preview and content
        p.setPen(QPen(QColor("#EAEFF8"), 1.0))
        p.drawLine(QPointF(0.0, pv_h), QPointF(w, pv_h))

        p.restore()

        # 5. Draw the rounded border ON TOP with antialiasing
        if self._is_hovered:
            border_color = QColor("#8B78F2")
            border_width = 1.8
        elif self.property("selected") in (True, "true"):
            border_color = QColor("#6C5CE7")
            border_width = 1.8
        else:
            border_color = QColor("#DCE1ED")
            border_width = 1.2

        border_pen = QPen(border_color, border_width)
        p.strokePath(card_path, border_pen)
        p.end()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.key)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self._is_hovered = True
        self.setProperty("hover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        if hasattr(self, "arrow_lab"):
            self.arrow_lab.style().unpolish(self.arrow_lab)
            self.arrow_lab.style().polish(self.arrow_lab)
        self.update()
        self._elevator.lift()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.setProperty("hover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if hasattr(self, "arrow_lab"):
            self.arrow_lab.style().unpolish(self.arrow_lab)
            self.arrow_lab.style().polish(self.arrow_lab)
        self.update()
        self._elevator.settle()
        super().leaveEvent(event)


class GatewayTile(QFrame):
    clicked = pyqtSignal()

    def __init__(self, kind: str, title: str, caption: str, parent=None):
        super().__init__(parent)
        self.setObjectName("GatewayTile")
        self.setProperty("kind", kind)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(280, 330)
        self._kind = kind
        self._is_hovered = False

        # Enhanced 3D shadow for gateway tiles
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        if kind == "studio":
            self._shadow_effect.setBlurRadius(28)
            self._shadow_effect.setColor(QColor(0, 0, 0, 85))
            self._shadow_effect.setOffset(0, 6)
            self._elevator = SmoothElevator(
                self._shadow_effect,
                rest_b=28, hover_b=46,
                rest_y=6, hover_y=16,
                rest_c=QColor(0, 0, 0, 85),
                hover_c=QColor(94, 234, 212, 90),
            )
        else:
            self._shadow_effect.setBlurRadius(28)
            self._shadow_effect.setColor(QColor(25, 35, 65, 38))
            self._shadow_effect.setOffset(0, 6)
            self._elevator = SmoothElevator(
                self._shadow_effect,
                rest_b=28, hover_b=46,
                rest_y=6, hover_y=16,
                rest_c=QColor(25, 35, 65, 38),
                hover_c=QColor(108, 92, 231, 75),
            )
        self.setGraphicsEffect(self._shadow_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Spacer placeholder for preview painting area
        self.preview_placeholder = QWidget(self)
        self.preview_placeholder.setObjectName("GatewayPreview")
        self.preview_placeholder.setMinimumHeight(200)
        self.preview_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_placeholder.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.preview_placeholder, stretch=1)

        body = QWidget(self)
        body.setObjectName("GatewayBody")
        body.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        col = QVBoxLayout(body)
        col.setContentsMargins(22, 16, 22, 20)
        col.setSpacing(6)
        eyebrow = QLabel("START HERE" if kind == "learn" else "OPEN CANVAS", body)
        eyebrow.setObjectName("GatewayEyebrow")
        heading = QLabel(title, body)
        heading.setObjectName("GatewayTitle")
        blurb = QLabel(caption, body)
        blurb.setObjectName("GatewayCaption")
        blurb.setWordWrap(True)
        col.addWidget(eyebrow)
        col.addWidget(heading)
        col.addWidget(blurb)
        col.addSpacing(6)

        self.cta_badge = QLabel("Explore Lessons  →" if kind == "learn" else "Open Studio Canvas  ✦", body)
        self.cta_badge.setObjectName("GatewayCtaBadge")
        col.addWidget(self.cta_badge, alignment=Qt.AlignLeft)
        layout.addWidget(body)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        radius = 24.0
        inset = 0.9
        card_rect = QRectF(inset, inset, w - inset * 2, h - inset * 2)

        card_path = QPainterPath()
        card_path.addRoundedRect(card_rect, radius, radius)

        # 1. Fill card background
        is_studio = (self._kind == "studio")
        bg_color = QColor("#0B0D14" if is_studio else "#FFFFFF")
        p.fillPath(card_path, QBrush(bg_color))

        # 2. Clip strictly to the rounded card shape
        p.save()
        p.setClipPath(card_path)

        # 3. Paint preview illustration
        pv_h = float(self.preview_placeholder.height()) if self.preview_placeholder.height() > 10 else 200.0
        preview_rect = QRectF(0.0, 0.0, w, pv_h)
        paint_topic_preview(p, preview_rect, self._kind)

        # 4. Divider line
        div_color = QColor("#1F2A32" if is_studio else "#EAEFF8")
        p.setPen(QPen(div_color, 1.0))
        p.drawLine(QPointF(0.0, pv_h), QPointF(w, pv_h))

        p.restore()

        # 5. Draw rounded border ON TOP
        if is_studio:
            border_color = QColor("#5EEAD4" if self._is_hovered else "#1E2535")
            border_width = 2.0 if self._is_hovered else 1.5
        else:
            border_color = QColor("#8B78F2" if self._is_hovered else "#DCE1ED")
            border_width = 2.0 if self._is_hovered else 1.5

        border_pen = QPen(border_color, border_width)
        p.strokePath(card_path, border_pen)
        p.end()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self._is_hovered = True
        self.setProperty("hover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        if hasattr(self, "cta_badge"):
            self.cta_badge.style().unpolish(self.cta_badge)
            self.cta_badge.style().polish(self.cta_badge)
        self.update()
        self._elevator.lift()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.setProperty("hover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if hasattr(self, "cta_badge"):
            self.cta_badge.style().unpolish(self.cta_badge)
            self.cta_badge.style().polish(self.cta_badge)
        self.update()
        self._elevator.settle()
        super().leaveEvent(event)


class GatewayPage(QWidget):
    learnChosen = pyqtSignal()
    studioChosen = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        col = QVBoxLayout(self)
        col.setContentsMargins(48, 28, 48, 32)
        col.setSpacing(18)

        heading = QLabel("How do you want to begin?")
        heading.setObjectName("HomeHeading")
        sub = QLabel("Learn a topic step by step, or open Studio and build something yourself.")
        sub.setObjectName("HomeSubheading")
        col.addWidget(heading)
        col.addWidget(sub)
        col.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(22)
        learn = GatewayTile(
            "learn",
            "Learn",
            "Guided lessons with a canvas, parameters, and a step-by-step proof.",
        )
        studio = GatewayTile(
            "studio",
            "Studio",
            "A blank scene. Draw, transform, and watch the matrix follow.",
        )
        studio.setProperty("kind", "studio")
        learn.clicked.connect(self.learnChosen.emit)
        studio.clicked.connect(self.studioChosen.emit)
        row.addWidget(learn, stretch=1)
        row.addWidget(studio, stretch=1)
        col.addLayout(row, stretch=1)


class CatalogPage(QWidget):
    topicChosen = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 20, 36, 24)
        outer.setSpacing(6)

        heading = QLabel("What do you want to learn?")
        heading.setObjectName("HomeHeading")
        sub = QLabel("Pick a topic. The full workspace opens after you choose — sidebar, canvas, and steps.")
        sub.setObjectName("HomeSubheading")
        outer.addWidget(heading)
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setObjectName("HomeScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        grid_host = QWidget()
        grid_host.setObjectName("CatalogGridHost")
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(12, 16, 12, 16)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)

        self.cards = {}
        for i, (key, title, caption, meta) in enumerate(LEARNING_TOPICS):
            card = TopicCard(key, title, caption, meta)
            card.clicked.connect(self.topicChosen.emit)
            self.cards[key] = card
            grid.addWidget(card, i // 3, i % 3)

        scroll.setWidget(grid_host)
        outer.addWidget(scroll, stretch=1)

    def set_selected(self, module_key: str):
        for key, card in self.cards.items():
            on = key == module_key
            card.setProperty("selected", "true" if on else "false")
            card.style().unpolish(card)
            card.style().polish(card)
            card.update()


class HomeHost(QWidget):
    learnChosen = pyqtSignal()
    studioChosen = pyqtSignal()
    topicChosen = pyqtSignal(str)

    PAGE_GATEWAY = 0
    PAGE_CATALOG = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomeHost")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.gateway = GatewayPage()
        self.catalog = CatalogPage()
        self.stack.addWidget(self.gateway)
        self.stack.addWidget(self.catalog)
        layout.addWidget(self.stack)

        self.gateway.learnChosen.connect(self.learnChosen.emit)
        self.gateway.studioChosen.connect(self.studioChosen.emit)
        self.catalog.topicChosen.connect(self.topicChosen.emit)

        self._module_buttons = self.catalog.cards

    def show_gateway(self):
        self.stack.setCurrentIndex(self.PAGE_GATEWAY)

    def show_catalog(self):
        self.stack.setCurrentIndex(self.PAGE_CATALOG)

    def on_catalog(self) -> bool:
        return self.stack.currentIndex() == self.PAGE_CATALOG

    def set_selected_topic(self, module_key: str):
        self.catalog.set_selected(module_key)
