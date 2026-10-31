"""Floating Studio chrome: icon rail, matrix HUD, and a short action bar."""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup, QSizePolicy,
    QWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF, QPointF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF


def _icon(kind: str, color: str = "#D6DEEA", size: int = 18) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    c = QColor(color)
    pen = QPen(c, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    s = float(size)
    if kind == "select":
        p.setBrush(QBrush(c))
        p.drawPolygon(QPolygonF([QPointF(4, 3), QPointF(4, 15), QPointF(8, 12), QPointF(11, 16.5), QPointF(13, 15), QPointF(10, 10.5), QPointF(14, 9)]))
    elif kind == "point":
        p.setBrush(QBrush(c))
        p.drawEllipse(QPointF(s / 2, s / 2), 3.2, 3.2)
    elif kind == "line":
        p.drawLine(QPointF(4, 13), QPointF(14, 5))
        p.setBrush(QBrush(c))
        p.drawEllipse(QPointF(4, 13), 1.8, 1.8)
        p.drawEllipse(QPointF(14, 5), 1.8, 1.8)
    elif kind == "triangle":
        p.drawPolygon(QPolygonF([QPointF(9, 3.5), QPointF(15.5, 15), QPointF(2.5, 15)]))
    elif kind == "rectangle":
        p.drawRoundedRect(QRectF(3.5, 5, 11, 8), 1.5, 1.5)
    elif kind == "polygon":
        p.drawPolygon(QPolygonF([
            QPointF(9, 2.8), QPointF(15.2, 7.2), QPointF(13.2, 14.8),
            QPointF(4.8, 14.8), QPointF(2.8, 7.2),
        ]))
    elif kind == "clip":
        p.setPen(QPen(c, 1.4, Qt.DashLine, Qt.RoundCap))
        p.drawRect(QRectF(3.5, 4.5, 11, 9))
    elif kind == "delete":
        p.drawLine(QPointF(5, 5), QPointF(13, 13))
        p.drawLine(QPointF(13, 5), QPointF(5, 13))
    elif kind == "cube":
        p.drawPolygon(QPolygonF([QPointF(5, 7), QPointF(9, 4.5), QPointF(14, 7), QPointF(10, 9.5)]))
        p.drawPolygon(QPolygonF([QPointF(5, 7), QPointF(5, 13), QPointF(10, 15.5), QPointF(10, 9.5)]))
        p.drawPolygon(QPolygonF([QPointF(14, 7), QPointF(14, 13), QPointF(10, 15.5), QPointF(10, 9.5)]))
    elif kind == "sphere":
        p.drawEllipse(QRectF(3.5, 3.5, 11, 11))
        p.drawArc(QRectF(3.5, 6.5, 11, 5), 0, 180 * 16)
        p.drawArc(QRectF(6.5, 3.5, 5, 11), 90 * 16, 180 * 16)
    elif kind == "pyramid":
        p.drawPolygon(QPolygonF([QPointF(9, 3), QPointF(15, 15), QPointF(3, 15)]))
        p.drawLine(QPointF(9, 3), QPointF(9, 15))
    elif kind == "cylinder":
        p.drawEllipse(QRectF(4.5, 3.2, 9, 4.2))
        p.drawLine(QPointF(4.5, 5.4), QPointF(4.5, 13))
        p.drawLine(QPointF(13.5, 5.4), QPointF(13.5, 13))
        p.drawArc(QRectF(4.5, 10.8, 9, 4.2), 0, -180 * 16)
    elif kind == "compare":
        p.drawRoundedRect(QRectF(2.5, 4.5, 6, 9), 1.2, 1.2)
        p.drawRoundedRect(QRectF(9.5, 4.5, 6, 9), 1.2, 1.2)
    elif kind == "focus":
        p.drawRect(QRectF(4, 4, 10, 10))
        p.drawLine(QPointF(4, 7), QPointF(2.2, 7))
        p.drawLine(QPointF(14, 7), QPointF(15.8, 7))
    p.end()
    return QIcon(pix)


def _icon_btn(kind: str, tip: str, checkable: bool = False) -> QPushButton:
    btn = QPushButton()
    btn.setObjectName("StudioIconBtn")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(checkable)
    btn.setToolTip(tip)
    btn.setIcon(_icon(kind))
    btn.setIconSize(QSize(18, 18))
    btn.setFixedSize(42, 42)
    btn.setFocusPolicy(Qt.NoFocus)
    if checkable:
        def _sync(_on=False, b=btn, k=kind):
            b.setIcon(_icon(k, "#07080D" if b.isChecked() else "#D6DEEA"))
        btn.toggled.connect(_sync)
        if btn.isChecked():
            _sync()
    return btn


def _text_btn(label: str, checkable: bool = False) -> QPushButton:
    btn = QPushButton(label)
    btn.setObjectName("StudioActionBtn")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(checkable)
    btn.setFocusPolicy(Qt.NoFocus)
    btn.setMinimumHeight(34)
    return btn


class StudioToolRail(QFrame):
    toolChosen = pyqtSignal(str)
    create3dRequested = pyqtSignal(str)
    deleteRequested = pyqtSignal()
    clipToggled = pyqtSignal(bool)
    compareToggled = pyqtSignal(bool)

    def __init__(self, mode: str = "2d", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setObjectName("StudioToolRail")
        self.setAttribute(Qt.WA_StyledBackground, True)
        col = QVBoxLayout(self)
        col.setContentsMargins(6, 8, 6, 8)
        col.setSpacing(4)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self.clip_btn = None
        self.compare_btn = None

        if mode == "2d":
            tools = [
                ("select", "Select  ·  drag to move"),
                ("point", "Point"),
                ("line", "Line"),
                ("triangle", "Triangle"),
                ("rectangle", "Rectangle"),
                ("polygon", "Polygon"),
            ]
            for key, tip in tools:
                btn = _icon_btn(key, tip, checkable=True)
                btn.clicked.connect(lambda _=False, k=key: self.toolChosen.emit(k))
                self._group.addButton(btn)
                col.addWidget(btn)
                if key == "select":
                    btn.setChecked(True)
            self.clip_btn = _icon_btn("clip", "Clip window", checkable=True)
            self.clip_btn.toggled.connect(self.clipToggled.emit)
            col.addWidget(self.clip_btn)
        else:
            for key, tip in (
                ("cube", "Add cube"),
                ("sphere", "Add sphere"),
                ("pyramid", "Add pyramid"),
                ("cylinder", "Add cylinder"),
            ):
                btn = _icon_btn(key, tip)
                btn.clicked.connect(lambda _=False, k=key: self.create3dRequested.emit(k))
                col.addWidget(btn)

        trash = _icon_btn("delete", "Delete selected")
        trash.clicked.connect(self.deleteRequested.emit)
        col.addWidget(trash)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class StudioMatrixHud(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioMatrixHud")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(248)
        col = QVBoxLayout(self)
        col.setContentsMargins(14, 12, 14, 12)
        col.setSpacing(6)

        self._kicker = QLabel("MATRIX")
        self._kicker.setObjectName("StudioHudKicker")
        col.addWidget(self._kicker)

        self._name = QLabel("No selection")
        self._name.setObjectName("StudioHudName")
        col.addWidget(self._name)

        self._matrix = QLabel("—")
        self._matrix.setObjectName("StudioHudMatrix")
        self._matrix.setWordWrap(True)
        self._matrix.setTextInteractionFlags(Qt.TextSelectableByMouse)
        col.addWidget(self._matrix)

        self._meta = QLabel("Drag the shape. The matrix follows.")
        self._meta.setObjectName("StudioHudMeta")
        self._meta.setWordWrap(True)
        col.addWidget(self._meta)

    def bind(self, payload: dict):
        if payload.get("empty"):
            self._name.setText("No selection")
            self._matrix.setText("—")
            self._meta.setText("Draw or pick an object.")
            return
        self._name.setText(payload.get("name") or "Object")
        self._matrix.setText(payload.get("matrix_str") or "—")
        hist = payload.get("history") or []
        stack = " → ".join(hist) if hist else "pose  T · R · S"
        world = payload.get("world") or []
        if world:
            x, y = world[0][0], world[0][1]
            extra = f"A → ({x:.1f}, {y:.1f})"
            if len(world[0]) > 2:
                extra = f"V0 → ({x:.1f}, {y:.1f}, {world[0][2]:.1f})"
        else:
            extra = ""
        self._meta.setText(f"{stack}\n{extra}".strip())


class StudioActionBar(QFrame):
    rotateClicked = pyqtSignal()
    scaleClicked = pyqtSignal()
    animateRequested = pyqtSignal()
    resetObject = pyqtSignal()
    compareToggled = pyqtSignal(bool)
    orthoToggled = pyqtSignal(bool)
    fullscreenToggled = pyqtSignal(bool)
    ghostToggled = pyqtSignal(bool)
    wireToggled = pyqtSignal(bool)
    runwayClicked = pyqtSignal()

    def __init__(self, mode: str = "2d", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setObjectName("StudioActionBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(6)

        rotate = _text_btn("Rotate")
        rotate.setToolTip("Apply a rotation to the selected object")
        rotate.clicked.connect(self.rotateClicked.emit)
        row.addWidget(rotate)

        scale = _text_btn("Scale")
        scale.setToolTip("Scale the selected object uniformly")
        scale.clicked.connect(self.scaleClicked.emit)
        row.addWidget(scale)

        play = _text_btn("Play")
        play.setToolTip("Animate the last transform")
        play.clicked.connect(self.animateRequested.emit)
        row.addWidget(play)

        reset = _text_btn("Reset")
        reset.setToolTip("Reset the selected object")
        reset.clicked.connect(self.resetObject.emit)
        row.addWidget(reset)

        self.compare_btn = None
        self.ortho_btn = None
        self.ghost_btn = _text_btn("Ghost", checkable=True)
        self.ghost_btn.setToolTip("Show previous poses as ghosts")
        self.ghost_btn.setChecked(True)
        self.ghost_btn.toggled.connect(self.ghostToggled.emit)
        row.addWidget(self.ghost_btn)

        self.wire_btn = _text_btn("Wire", checkable=True)
        self.wire_btn.setToolTip("Wireframe overlay")
        self.wire_btn.toggled.connect(self.wireToggled.emit)
        row.addWidget(self.wire_btn)

        self.runway_btn = None
        if mode == "2d":
            self.runway_btn = _text_btn("Runway")
            self.runway_btn.setToolTip("Send this shape through Transform → Clip → Raster")
            self.runway_btn.clicked.connect(self.runwayClicked.emit)
            row.addWidget(self.runway_btn)

        if mode == "3d":
            self.ortho_btn = _text_btn("Ortho", checkable=True)
            self.ortho_btn.setToolTip("Orthographic projection")
            self.ortho_btn.toggled.connect(self.orthoToggled.emit)
            row.addWidget(self.ortho_btn)
            self.compare_btn = _text_btn("Split", checkable=True)
            self.compare_btn.setToolTip("Perspective and orthographic side by side")
            self.compare_btn.toggled.connect(self.compareToggled.emit)
            row.addWidget(self.compare_btn)

        self.fullscreen_btn = _icon_btn("focus", "Focus canvas", checkable=True)
        self.fullscreen_btn.setFixedSize(34, 34)
        self.fullscreen_btn.toggled.connect(self.fullscreenToggled.emit)
        row.addWidget(self.fullscreen_btn)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


def build_studio_layout(host: QWidget, stage: QWidget, rail: QWidget, hud: QWidget, bar: QWidget, filmstrip: QWidget = None):
    """Canvas-first studio: slim rail, stage, matrix HUD, filmstrip, one action bar."""
    root = QVBoxLayout(host)
    root.setContentsMargins(16, 16, 16, 16)
    root.setSpacing(12)
    mid = QHBoxLayout()
    mid.setSpacing(12)
    if rail is not None:
        mid.addWidget(rail, 0, Qt.AlignVCenter)
    mid.addWidget(stage, 1)
    if hud is not None:
        mid.addWidget(hud, 0, Qt.AlignTop)
    root.addLayout(mid, 1)
    if filmstrip is not None:
        root.addWidget(filmstrip)
    if bar is not None:
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        bottom.addWidget(bar, 0, Qt.AlignCenter)
        bottom.addStretch(1)
        root.addLayout(bottom)
