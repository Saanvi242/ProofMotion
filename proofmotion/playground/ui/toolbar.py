"""Compact playground toolbar for transforms, view, and projection."""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSlider,
)
from PyQt5.QtCore import Qt, pyqtSignal

from playground.ui.widgets import make_spin, tool_button


class PlaygroundToolbar(QWidget):
    transformApply = pyqtSignal(str, dict)  # kind, params
    animateRequested = pyqtSignal()
    ghostToggled = pyqtSignal(bool)
    wireframeToggled = pyqtSignal(bool)
    resetObject = pyqtSignal()
    resetCamera = pyqtSignal()
    zoomIn = pyqtSignal()
    zoomOut = pyqtSignal()
    resetView = pyqtSignal()
    projectionChanged = pyqtSignal(str)
    fovChanged = pyqtSignal(float)
    compareToggled = pyqtSignal(bool)
    fullscreenToggled = pyqtSignal(bool)

    def __init__(self, mode: str = "2d", parent=None):
        super().__init__(parent)
        self.mode = mode
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        lab = QLabel("TRANSFORM")
        lab.setObjectName("SpeedLabel")
        row1.addWidget(lab)

        if mode == "2d":
            self.dx = make_spin(-20, 20, 2.0, 0.5)
            self.dy = make_spin(-20, 20, 1.0, 0.5)
            self.dx.setFixedWidth(78)
            self.dy.setFixedWidth(78)
            row1.addWidget(QLabel("dx"))
            row1.addWidget(self.dx)
            row1.addWidget(QLabel("dy"))
            row1.addWidget(self.dy)
            t_btn = tool_button("Translate")
            t_btn.clicked.connect(lambda: self.transformApply.emit(
                "translate", {"dx": self.dx.value(), "dy": self.dy.value()}
            ))
            row1.addWidget(t_btn)

            self.angle = make_spin(-360, 360, 45.0, 5.0, decimals=1, suffix="°")
            self.angle.setFixedWidth(88)
            row1.addWidget(QLabel("θ"))
            row1.addWidget(self.angle)
            r_btn = tool_button("Rotate")
            r_btn.clicked.connect(lambda: self.transformApply.emit(
                "rotate", {"angle": self.angle.value()}
            ))
            row1.addWidget(r_btn)

            self.sx = make_spin(0.1, 5.0, 1.5, 0.1)
            self.sy = make_spin(0.1, 5.0, 1.5, 0.1)
            self.sx.setFixedWidth(70)
            self.sy.setFixedWidth(70)
            row1.addWidget(QLabel("sx"))
            row1.addWidget(self.sx)
            row1.addWidget(QLabel("sy"))
            row1.addWidget(self.sy)
            s_btn = tool_button("Scale")
            s_btn.clicked.connect(lambda: self.transformApply.emit(
                "scale", {"sx": self.sx.value(), "sy": self.sy.value()}
            ))
            row1.addWidget(s_btn)

            self.axis = QComboBox()
            self.axis.setObjectName("StyleCombo")
            self.axis.addItems(["X-axis", "Y-axis", "Origin", "y = x"])
            row1.addWidget(self.axis)
            f_btn = tool_button("Reflect")
            f_btn.clicked.connect(lambda: self.transformApply.emit(
                "reflect", {"axis": self.axis.currentText()}
            ))
            row1.addWidget(f_btn)
        else:
            self.dx = make_spin(-10, 10, 1.0, 0.2)
            self.dy = make_spin(-10, 10, 0.0, 0.2)
            self.dz = make_spin(-10, 10, 0.0, 0.2)
            for spin in (self.dx, self.dy, self.dz):
                spin.setFixedWidth(72)
            row1.addWidget(QLabel("dx"))
            row1.addWidget(self.dx)
            row1.addWidget(QLabel("dy"))
            row1.addWidget(self.dy)
            row1.addWidget(QLabel("dz"))
            row1.addWidget(self.dz)
            t_btn = tool_button("Translate")
            t_btn.clicked.connect(lambda: self.transformApply.emit(
                "translate", {"dx": self.dx.value(), "dy": self.dy.value(), "dz": self.dz.value()}
            ))
            row1.addWidget(t_btn)

            self.rot_axis = QComboBox()
            self.rot_axis.setObjectName("StyleCombo")
            self.rot_axis.addItems(["X", "Y", "Z"])
            self.rot_axis.setCurrentText("Y")
            self.angle = make_spin(-360, 360, 30.0, 5.0, decimals=1, suffix="°")
            self.angle.setFixedWidth(88)
            row1.addWidget(self.rot_axis)
            row1.addWidget(self.angle)
            r_btn = tool_button("Rotate")
            r_btn.clicked.connect(lambda: self.transformApply.emit(
                "rotate", {"axis": self.rot_axis.currentText(), "angle": self.angle.value()}
            ))
            row1.addWidget(r_btn)

            self.sx = make_spin(0.1, 5.0, 1.4, 0.1)
            self.sy = make_spin(0.1, 5.0, 1.4, 0.1)
            self.sz = make_spin(0.1, 5.0, 1.4, 0.1)
            for spin in (self.sx, self.sy, self.sz):
                spin.setFixedWidth(70)
            row1.addWidget(QLabel("s"))
            row1.addWidget(self.sx)
            row1.addWidget(self.sy)
            row1.addWidget(self.sz)
            s_btn = tool_button("Scale")
            s_btn.clicked.connect(lambda: self.transformApply.emit(
                "scale", {"sx": self.sx.value(), "sy": self.sy.value(), "sz": self.sz.value()}
            ))
            row1.addWidget(s_btn)

        row1.addStretch(1)
        root.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        view = QLabel("VIEW")
        view.setObjectName("SpeedLabel")
        row2.addWidget(view)

        anim = tool_button("Animate last")
        anim.clicked.connect(self.animateRequested.emit)
        row2.addWidget(anim)

        ghost = tool_button("Ghost", checkable=True)
        ghost.setChecked(True)
        ghost.setToolTip("Show the object before the last sequential transform")
        ghost.toggled.connect(self.ghostToggled.emit)
        row2.addWidget(ghost)

        wire = tool_button("Wireframe", checkable=True)
        wire.toggled.connect(self.wireframeToggled.emit)
        row2.addWidget(wire)
        self.wire_btn = wire

        zm = tool_button("−")
        zm.setToolTip("Zoom out")
        zm.clicked.connect(self.zoomOut.emit)
        zp = tool_button("+")
        zp.setToolTip("Zoom in")
        zp.clicked.connect(self.zoomIn.emit)
        rv = tool_button("Reset view")
        rv.clicked.connect(self.resetView.emit)
        row2.addWidget(zm)
        row2.addWidget(zp)
        row2.addWidget(rv)

        ro = tool_button("Reset object")
        ro.clicked.connect(self.resetObject.emit)
        row2.addWidget(ro)

        if mode == "3d":
            rc = tool_button("Reset camera")
            rc.clicked.connect(self.resetCamera.emit)
            row2.addWidget(rc)

            self.proj = QComboBox()
            self.proj.setObjectName("StyleCombo")
            self.proj.addItems(["Perspective", "Orthographic"])
            self.proj.currentTextChanged.connect(lambda t: self.projectionChanged.emit(t.lower()))
            row2.addWidget(self.proj)

            fov_lab = QLabel("FOV")
            fov_lab.setObjectName("SpeedLabel")
            row2.addWidget(fov_lab)
            self.fov = QSlider(Qt.Horizontal)
            self.fov.setRange(20, 90)
            self.fov.setValue(45)
            self.fov.setFixedWidth(90)
            self.fov.valueChanged.connect(lambda v: self.fovChanged.emit(float(v)))
            row2.addWidget(self.fov)
            self.fov_value = QLabel("45°")
            self.fov_value.setObjectName("SpeedBadge")
            row2.addWidget(self.fov_value)
            self.fov.valueChanged.connect(lambda v: self.fov_value.setText(f"{v}°"))

            cmp = tool_button("Compare projections", checkable=True)
            cmp.setToolTip("Side-by-side perspective and orthographic viewports")
            cmp.toggled.connect(self.compareToggled.emit)
            row2.addWidget(cmp)
            self.compare_btn = cmp

        row2.addStretch(1)
        fs = tool_button("Fullscreen", checkable=True)
        fs.toggled.connect(self.fullscreenToggled.emit)
        self.fullscreen_btn = fs
        row2.addWidget(fs)
        root.addLayout(row2)

    def set_projection_ui(self, mode: str, fov: float):
        if self.mode != "3d":
            return
        self.proj.blockSignals(True)
        self.proj.setCurrentText("Orthographic" if mode.startswith("ortho") else "Perspective")
        self.proj.blockSignals(False)
        self.fov.blockSignals(True)
        self.fov.setValue(int(round(fov)))
        self.fov.blockSignals(False)
        self.fov.setEnabled(not str(mode).startswith("ortho"))
        self.fov_value.setText(f"{int(round(fov))}°")
