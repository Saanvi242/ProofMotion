"""Right inspector: pose sliders, live matrix, coordinates, challenge."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal

from playground.ui.widgets import section_label, AxisSliderRow, quiet_button, make_spin
from playground.math_sync import format_matrix
from resources.theme import COLORS


class InspectorPanel(QWidget):
    poseChanged = pyqtSignal(dict)
    challengeRequested = pyqtSignal()
    challengeSubmitted = pyqtSignal(float, float)

    def __init__(self, mode: str = "2d", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setObjectName("StudioPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(280)
        self.setMaximumWidth(360)
        self._block = False
        self._has_object = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        self._title = QLabel("Inspector")
        self._title.setObjectName("PanelTitle")
        outer.addWidget(self._title)

        divider = QWidget()
        divider.setObjectName("PanelDivider")
        outer.addWidget(divider)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        self.body = QVBoxLayout(body)
        self.body.setContentsMargins(0, 0, 8, 0)
        self.body.setSpacing(8)
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)

        self._empty = QLabel("Select an object to inspect its pose, matrix, and coordinates.")
        self._empty.setObjectName("ParamHint")
        self._empty.setWordWrap(True)
        self.body.addWidget(self._empty)

        self.body.addWidget(section_label("Position"))
        self.tx = AxisSliderRow("X", -12, 12, 0.0)
        self.ty = AxisSliderRow("Y", -12, 12, 0.0)
        self.body.addWidget(self.tx)
        self.body.addWidget(self.ty)
        self.tz = AxisSliderRow("Z", -12, 12, 0.0)
        self.body.addWidget(self.tz)
        self.tz.setVisible(mode == "3d")

        if mode == "2d":
            self.body.addWidget(section_label("Rotation"))
            self.rot = AxisSliderRow("θ", -180, 180, 0.0, step=1.0, decimals=1, suffix="°")
            self.body.addWidget(self.rot)
            self.rx = self.ry = self.rz = None
        else:
            self.body.addWidget(section_label("Rotation"))
            self.rx = AxisSliderRow("X", -180, 180, 0.0, step=1.0, decimals=1, suffix="°")
            self.ry = AxisSliderRow("Y", -180, 180, 0.0, step=1.0, decimals=1, suffix="°")
            self.rz = AxisSliderRow("Z", -180, 180, 0.0, step=1.0, decimals=1, suffix="°")
            self.body.addWidget(self.rx)
            self.body.addWidget(self.ry)
            self.body.addWidget(self.rz)
            self.rot = None

        self.body.addWidget(section_label("Scale"))
        self.sx = AxisSliderRow("X", 0.1, 4.0, 1.0, step=0.05)
        self.sy = AxisSliderRow("Y", 0.1, 4.0, 1.0, step=0.05)
        self.sz = AxisSliderRow("Z", 0.1, 4.0, 1.0, step=0.05)
        self.body.addWidget(self.sx)
        self.body.addWidget(self.sy)
        self.body.addWidget(self.sz)
        self.sz.setVisible(mode == "3d")

        for row in (self.tx, self.ty, self.tz, self.sx, self.sy, self.sz):
            row.valueChanged.connect(self._emit_pose)
        if self.rot:
            self.rot.valueChanged.connect(self._emit_pose)
        if self.rx:
            self.rx.valueChanged.connect(self._emit_pose)
            self.ry.valueChanged.connect(self._emit_pose)
            self.rz.valueChanged.connect(self._emit_pose)

        self.body.addWidget(section_label("Transformation matrix"))
        self._matrix = QLabel("—")
        self._matrix.setObjectName("EquationLabel")
        self._matrix.setWordWrap(True)
        self._matrix.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body.addWidget(self._matrix)

        self._multiply = QLabel("")
        self._multiply.setObjectName("ExplanationLabel")
        self._multiply.setWordWrap(True)
        self._multiply.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body.addWidget(self._multiply)

        self.body.addWidget(section_label("Coordinates  before → after"))
        self._coords = QLabel("—")
        self._coords.setObjectName("EquationLabel")
        self._coords.setWordWrap(True)
        self._coords.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body.addWidget(self._coords)

        self._history = QLabel("")
        self._history.setObjectName("ParamHint")
        self._history.setWordWrap(True)
        self.body.addWidget(self._history)

        self._proj = QLabel("")
        self._proj.setObjectName("ParamHint")
        self._proj.setWordWrap(True)
        self.body.addWidget(self._proj)
        self._proj.setVisible(mode == "3d")

        if mode == "2d":
            self.body.addWidget(section_label("Challenge"))
            self._challenge_prompt = QLabel("Predict a rotation without looking at the canvas.")
            self._challenge_prompt.setObjectName("ExplanationLabel")
            self._challenge_prompt.setWordWrap(True)
            self.body.addWidget(self._challenge_prompt)
            guess_row = QHBoxLayout()
            self._guess_x = make_spin(-40, 40, 0.0, 0.1)
            self._guess_y = make_spin(-40, 40, 0.0, 0.1)
            guess_row.addWidget(QLabel("x"))
            guess_row.addWidget(self._guess_x)
            guess_row.addWidget(QLabel("y"))
            guess_row.addWidget(self._guess_y)
            self.body.addLayout(guess_row)
            chal_btns = QHBoxLayout()
            new_btn = quiet_button("New challenge")
            new_btn.setMaximumHeight(34)
            new_btn.clicked.connect(self.challengeRequested.emit)
            check_btn = QPushButton("Check")
            check_btn.setObjectName("ApplyButton")
            check_btn.setMaximumHeight(34)
            check_btn.clicked.connect(self._submit_challenge)
            chal_btns.addWidget(new_btn)
            chal_btns.addWidget(check_btn)
            self.body.addLayout(chal_btns)
            self._challenge_result = QLabel("")
            self._challenge_result.setObjectName("ResultLabel")
            self._challenge_result.setWordWrap(True)
            self.body.addWidget(self._challenge_result)

        self.body.addStretch(1)
        self._set_enabled(False)

    def _emit_pose(self, *_):
        if self._block or not self._has_object:
            return
        payload = {
            "tx": self.tx.value(),
            "ty": self.ty.value(),
            "sx": self.sx.value(),
            "sy": self.sy.value(),
        }
        if self.mode == "2d":
            payload["rotation"] = self.rot.value()
        else:
            payload["tz"] = self.tz.value()
            payload["rx"] = self.rx.value()
            payload["ry"] = self.ry.value()
            payload["rz"] = self.rz.value()
            payload["sz"] = self.sz.value()
        self.poseChanged.emit(payload)

    def _set_enabled(self, on: bool):
        self._has_object = on
        for w in self.findChildren(AxisSliderRow):
            w.setEnabled(on)

    def bind(self, payload: dict):
        self._block = True
        if payload.get("empty"):
            self._title.setText("Inspector")
            self._empty.show()
            self._matrix.setText("—")
            self._coords.setText("—")
            self._multiply.setText("")
            self._history.setText("")
            self._set_enabled(False)
            self._block = False
            return

        self._empty.hide()
        self._set_enabled(True)
        self._title.setText(payload.get("name", "Inspector"))
        self.tx.set_value(payload["tx"])
        self.ty.set_value(payload["ty"])
        self.sx.set_value(payload["sx"])
        self.sy.set_value(payload["sy"])
        if self.mode == "2d":
            self.rot.set_value(payload["rotation"])
        else:
            self.tz.set_value(payload["tz"])
            self.rx.set_value(payload["rx"])
            self.ry.set_value(payload["ry"])
            self.rz.set_value(payload["rz"])
            self.sz.set_value(payload["sz"])
            proj = payload.get("projection") or {}
            mode = str(proj.get("mode", "perspective")).title()
            fov = proj.get("fov", 45.0)
            extra = f"  FOV {fov:.0f}°" if proj.get("mode") == "perspective" else ""
            self._proj.setText(f"Projection: {mode}{extra}")

        self._matrix.setText(payload.get("matrix_str", "—"))
        self._coords.setText(payload.get("coords_str", "—"))
        hist = payload.get("history") or []
        self._history.setText("Stack: " + " → ".join(hist) if hist else "Stack: pose only (T · R · S)")

        mul = payload.get("multiply")
        if mul:
            self._multiply.setText(
                f"{mul['equation']}\n"
                f"M_op =\n{format_matrix(mul['op_matrix'])}\n"
                f"M_prev =\n{format_matrix(mul['prev_matrix'])}\n"
                f"M =\n{format_matrix(mul['result_matrix'])}"
            )
        else:
            pose = payload.get("pose_str", "")
            self._multiply.setText(f"M = T · R · S\n{pose}")

        self._block = False

    def set_challenge(self, data: dict):
        start = data.get("start", (0.0, 0.0))
        self._challenge_prompt.setText(
            f"{data['prompt']}\nCurrently {data['label']} = ({start[0]:.2f}, {start[1]:.2f})."
        )
        self._challenge_result.setText("")
        self._challenge_target = data.get("target")

    def show_challenge_result(self, ok: bool, expected):
        if ok:
            self._challenge_result.setText(
                f"Correct. {expected[0]:.2f}, {expected[1]:.2f}"
            )
        else:
            self._challenge_result.setText(
                f"Not quite. Expected ({expected[0]:.2f}, {expected[1]:.2f})."
            )

    def _submit_challenge(self):
        self.challengeSubmitted.emit(self._guess_x.value(), self._guess_y.value())
