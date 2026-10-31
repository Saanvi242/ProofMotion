"""
ui/home_screens.py
------------------
Launch gateway (Learn vs Studio) and the Learn topic catalog.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QScrollArea, QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QPolygonF,
)


LEARNING_TOPICS = [
    ("algorithms", "Algorithms", "Compare, swap, and search — one step at a time.", "Sorting & searching"),
    ("transformations", "Transformations", "Move, rotate, and scale shapes on the plane.", "2D matrices"),
    ("rasterization", "Rasterization", "Watch lines and circles become pixels.", "Bresenham & midpoint"),
    ("clipping", "Clipping", "See what stays inside the window, and why.", "Lines & polygons"),
    ("curves", "Curves", "Bend a path with control points you can drag.", "Bézier, B-spline, Hermite"),
    ("theorems", "Theorems", "Geometric proofs that rearrange as you watch.", "Pythagoras to cosines"),
]


def _shadow(widget, blur=22, alpha=28, y=6):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setColor(QColor(32, 48, 79, alpha))
    effect.setOffset(0, y)
    widget.setGraphicsEffect(effect)


def paint_topic_preview(p: QPainter, rect: QRectF, key: str):
    """Draw a compact illustration for a learning topic."""
    p.save()
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setClipRect(rect)

    bg = QLinearGradient(rect.topLeft(), rect.bottomRight())
    bg.setColorAt(0.0, QColor("#F4F1FF"))
    bg.setColorAt(1.0, QColor("#E8EEFB"))
    p.fillRect(rect, QBrush(bg))

    cx, cy = rect.center().x(), rect.center().y()
    w, h = rect.width(), rect.height()

    if key == "algorithms":
        values = [24, 13, 9, 45, 18, 32]
        n = len(values)
        max_v = max(values)
        gap = w * 0.07
        ball_r = min(w * 0.055, h * 0.16)
        span = (n - 1) * (ball_r * 2 + gap)
        x0 = cx - span / 2.0
        base = cy + h * 0.18
        for i, val in enumerate(values):
            x = x0 + i * (ball_r * 2 + gap)
            y = base - (val / max_v) * h * 0.28
            grad = QLinearGradient(x - ball_r, y - ball_r, x + ball_r, y + ball_r)
            grad.setColorAt(0.0, QColor("#8B78F2"))
            grad.setColorAt(1.0, QColor("#5B4AD4"))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(grad))
            p.drawEllipse(QPointF(x, y), ball_r, ball_r)
            p.setPen(QPen(QColor(255, 255, 255, 70), 1.2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(x - ball_r * 0.25, y - ball_r * 0.28), ball_r * 0.42, ball_r * 0.28)
        p.setPen(QPen(QColor("#D5DDED"), 1.4))
        p.drawLine(QPointF(rect.left() + 18, base + ball_r + 8), QPointF(rect.right() - 18, base + ball_r + 8))

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

    elif key == "curves":
        pts = [
            QPointF(rect.left() + 28, cy + 28),
            QPointF(cx - 30, cy - 38),
            QPointF(cx + 36, cy + 44),
            QPointF(rect.right() - 28, cy - 22),
        ]
        p.setPen(QPen(QColor("#C5CDDC"), 1.3, Qt.DashLine, Qt.RoundCap))
        p.drawPolyline(QPolygonF(pts))
        path = QPainterPath(pts[0])
        path.cubicTo(pts[1], pts[2], pts[3])
        p.setPen(QPen(QColor("#6C5CE7"), 2.4, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.setBrush(QBrush(QColor("#6C5CE7")))
        p.setPen(Qt.NoPen)
        for pt in pts:
            p.drawEllipse(pt, 4.4, 4.4)

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

    elif key == "learn":
        p.restore()
        paint_topic_preview(p, rect, "algorithms")
        return

    elif key == "studio":
        bg2 = QLinearGradient(rect.topLeft(), rect.bottomRight())
        bg2.setColorAt(0.0, QColor("#12141C"))
        bg2.setColorAt(1.0, QColor("#07080D"))
        p.fillRect(rect, QBrush(bg2))
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
        clip.addRoundedRect(r.adjusted(0, 0, 0, 20), 16, 16)
        p.setClipPath(clip)
        paint_topic_preview(p, r, self._kind)
        p.end()


class TopicCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, key: str, title: str, caption: str, meta: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("TopicCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(220, 228)
        _shadow(self, blur=20, alpha=22, y=5)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        preview_wrap = QFrame()
        preview_wrap.setObjectName("TopicCardPreview")
        preview_wrap.setMinimumHeight(140)
        pv_layout = QVBoxLayout(preview_wrap)
        pv_layout.setContentsMargins(0, 0, 0, 0)
        pv_layout.addWidget(PreviewCanvas(key))
        layout.addWidget(preview_wrap, stretch=1)

        body = QWidget()
        body.setObjectName("TopicCardBody")
        body_col = QVBoxLayout(body)
        body_col.setContentsMargins(16, 12, 16, 14)
        body_col.setSpacing(4)

        title_lab = QLabel(title)
        title_lab.setObjectName("TopicCardTitle")
        cap = QLabel(caption)
        cap.setObjectName("TopicCardCaption")
        cap.setWordWrap(True)
        meta_lab = QLabel(meta)
        meta_lab.setObjectName("TopicCardMeta")
        body_col.addWidget(title_lab)
        body_col.addWidget(cap)
        body_col.addWidget(meta_lab)
        layout.addWidget(body)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.key)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.setProperty("hover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setProperty("hover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class GatewayTile(QFrame):
    clicked = pyqtSignal()

    def __init__(self, kind: str, title: str, caption: str, parent=None):
        super().__init__(parent)
        self.setObjectName("GatewayTile")
        self.setProperty("kind", kind)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(280, 320)
        _shadow(self, blur=28, alpha=36, y=8)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        preview_wrap = QFrame()
        preview_wrap.setObjectName("GatewayPreview")
        preview_wrap.setMinimumHeight(200)
        pv = QVBoxLayout(preview_wrap)
        pv.setContentsMargins(0, 0, 0, 0)
        pv.addWidget(PreviewCanvas(kind))
        layout.addWidget(preview_wrap, stretch=1)

        body = QWidget()
        body.setObjectName("GatewayBody")
        col = QVBoxLayout(body)
        col.setContentsMargins(22, 16, 22, 20)
        col.setSpacing(6)
        eyebrow = QLabel("START HERE" if kind == "learn" else "OPEN CANVAS")
        eyebrow.setObjectName("GatewayEyebrow")
        heading = QLabel(title)
        heading.setObjectName("GatewayTitle")
        blurb = QLabel(caption)
        blurb.setObjectName("GatewayCaption")
        blurb.setWordWrap(True)
        col.addWidget(eyebrow)
        col.addWidget(heading)
        col.addWidget(blurb)
        layout.addWidget(body)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


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
        grid.setContentsMargins(4, 16, 4, 8)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

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
