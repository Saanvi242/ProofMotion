"""Homogeneous Lift: 2D points rise onto the plane w = 1 in OpenGL."""

import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from graphics.opengl_widget import OpenGL3DWidget
from playground.experiences import ground_vertices, lift_vertices
from playground.math_sync import format_matrix
from playground.models import default_shape_2d
from playground.ui.studio_chrome import StudioMatrixHud, StudioActionBar, build_studio_layout
import cgip.projection_3d as t3d
import cgip.transformations as t2d


class HomogeneousLiftWorkspace(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.points = default_shape_2d("triangle")
        self.extra = np.eye(3, dtype=float)
        self.w = 0.0

        self.gl = OpenGL3DWidget()
        self.gl.set_scene_objects([])
        self.gl.set_camera_state({
            "azimuth": 42.0,
            "elevation": 28.0,
            "distance": 9.0,
            "pan_x": 0.0,
            "pan_y": 0.5,
            "target_z": 0.0,
        })
        self.hud = StudioMatrixHud()
        self.bar = StudioActionBar("2d")
        if self.bar.runway_btn:
            self.bar.runway_btn.hide()
        if self.bar.ghost_btn:
            self.bar.ghost_btn.hide()
        if self.bar.wire_btn:
            self.bar.wire_btn.hide()
        build_studio_layout(self, self.gl, None, self.hud, self.bar)

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._tick)
        self._lifting = True

        self.bar.rotateClicked.connect(self._rotate)
        self.bar.scaleClicked.connect(self._scale)
        self.bar.animateRequested.connect(self._play)
        self.bar.resetObject.connect(self._reset)
        self.bar.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self._push()

    def _rotate(self):
        self.extra = t2d.rotation_matrix(25.0) @ self.extra
        self._push()
        self.statusMessage.emit("Rotated in the plane, then lifted with w.")

    def _scale(self):
        self.extra = t2d.scaling_matrix(1.25, 1.25) @ self.extra
        self._push()
        self.statusMessage.emit("Scaled in the plane w = 1.")

    def _play(self):
        self._lifting = self.w < 0.5
        self._anim.start()
        self.statusMessage.emit("Lifting onto w = 1." if self._lifting else "Lowering off the homogeneous plane.")

    def _reset(self):
        self.extra = np.eye(3, dtype=float)
        self.w = 0.0
        self._anim.stop()
        self._push()
        self.statusMessage.emit("Back on the table — w = 0.")

    def _tick(self):
        step = 0.04 if self._lifting else -0.04
        self.w = max(0.0, min(1.0, self.w + step))
        self._push()
        if self.w in (0.0, 1.0):
            self._anim.stop()

    def _push(self):
        lifted = lift_vertices(self.points, self.w, extra=self.extra)
        ground = ground_vertices(self.points, extra=self.extra)
        objects = []
        lines = []
        cyan = (0.37, 0.92, 0.83)
        mute = (0.45, 0.52, 0.62)
        pink = (0.96, 0.45, 0.71)
        for i, (x, y, z) in enumerate(lifted):
            model = t3d.translation_matrix_3d(x, y, z) @ t3d.scaling_matrix_3d(0.16, 0.16, 0.16)
            objects.append({
                "id": f"v{i}",
                "kind": "sphere",
                "model": model,
                "selected": i == 0,
                "color": cyan,
            })
            gx, gy, gz = ground[i]
            lines.append(((gx, gy, gz), (x, y, z), mute))
        n = len(lifted)
        for i in range(n):
            lines.append((lifted[i], lifted[(i + 1) % n], cyan))
            lines.append((ground[i], ground[(i + 1) % n], mute))
        # w = 1 plane corners as a hint frame
        s = 3.2
        plane = [(-s, 1.0, -s), (s, 1.0, -s), (s, 1.0, s), (-s, 1.0, s)]
        for i in range(4):
            lines.append((plane[i], plane[(i + 1) % 4], pink))
        self.gl.set_scene_objects(objects)
        self.gl.set_overlay_lines(lines)
        self.gl.set_overlay_plane_y(1.0)
        self.hud.bind({
            "empty": False,
            "name": f"w = {self.w:.2f}",
            "matrix_str": format_matrix(self.extra),
            "history": ["lift to w", "2D extra"],
            "world": [(p[0], p[2]) for p in lifted],
        })
        self.hud._meta.setText(
            f"Homogeneous (x, y, w) drawn as world (x, w, y).\n"
            f"Plane y = 1 is w = 1. Drag to orbit."
        )

    def set_focus_mode(self, on: bool):
        self.hud.setVisible(not on)
        self.bar.setVisible(not on)

    def set_fullscreen_button(self, on: bool):
        self.bar.fullscreen_btn.blockSignals(True)
        self.bar.fullscreen_btn.setChecked(on)
        self.bar.fullscreen_btn.blockSignals(False)
